#!/usr/bin/env python3
"""vcia — Citation Integrity Audit, mechanical checks (read-only, standard library only).
Reads a manuscript (.docx, .md or .txt) and reports:
  A  in-text citations <-> reference list: MISSING, ORPHAN, possible duplicate entries
  B  note markers <-> note definitions (Word footnotes/endnotes, and manual [n] / superscript schemes)
  H  over-citation: works cited more than --occ-cap times in the main body

It reads paragraphs AND table cells, and every reference list it finds. Matching is a heuristic on
(first-author surname, year): pair MISSING with ORPHAN before believing either (see SKILL.md).

Usage:
  python3 vcia.py manuscript.docx [--bib References] [--cut "not for submission"]
                                  [--body-start Introduction] [--occ-cap 3] [--json report.json]
"""
import argparse, json, re, sys, unicodedata, zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
BIB_DEFAULT = ["references", "bibliography", "works cited", "reference list", "literature",
               "appendix references", "references for the appendix"]
NOTES_DEFAULT = ["notes", "endnotes", "footnotes"]
CUT_DEFAULT = ["not for submission", "working draft material", "unused notes"]
BACK_MATTER = ["acknowledg", "funding", "declaration", "data availability", "ethics", "conflict of interest",
               "author contributions", "biograph", "appendix", "supplementary"]

PART = r"(?:van|von|de|der|den|du|la|le|da|di|del|dos|ten|ter)"
NAME = rf"(?:{PART}\s+)*[A-ZÀ-ÖØ-Þ][\wÀ-ÖØ-öø-ÿ'’\-]+"
YEAR = r"(?:1[6-9]\d\d|20\d\d)[a-z]?"
NARR = re.compile(rf"({NAME})(\s+et al\.|\s+(?:and|&)\s+{NAME})?(?:['’]s)?\s+\(({YEAR})((?:\s*,\s*(?:{YEAR}|p+\.\s*[\d\-–]+))*)[^)]*\)")
PAREN = re.compile(r"\(([^()]*?\b(?:1[6-9]\d\d|20\d\d)[a-z]?\b[^()]*)\)")
PREFIX = re.compile(r"^\s*(?:e\.g\.,?|i\.e\.,?|see also|see|cf\.|compare|but see|for example,?|following|as in)\s+", re.I)
SKIPWORDS = {"In", "The", "This", "These", "Table", "Figure", "Fig", "Section", "Appendix", "Chapter", "See",
             "January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
             "November", "December", "Spring", "Summer", "Autumn", "Fall", "Winter", "Since", "From", "Between",
             "During", "After", "Before", "Until", "By", "Of", "On", "At", "For", "And", "Or", "A", "An"}

def nfc(s): return unicodedata.normalize("NFC", s)

def key(name):
    name = nfc(name).replace("’", "'")
    name = re.sub(r"'s$", "", name)
    name = re.sub(rf"^(?:{PART}\s+)+", "", name, flags=re.I)
    return name.casefold()

# ---------------------------------------------------------------- reading
def read_docx(path):
    z = zipfile.ZipFile(path)
    root = ET.fromstring(z.read("word/document.xml"))
    body = root.find(W + "body")
    blocks = []
    def para(p, in_table):
        style = p.find(f"{W}pPr/{W}pStyle")
        sv = style.get(W + "val", "") if style is not None else ""
        lvl = None
        m = re.match(r"(?i)heading\s*(\d)", sv) or re.match(r"(?i)^(title)$", sv)
        if m: lvl = 0 if m.group(1).lower() == "title" else int(m.group(1))
        text, sup, fref = [], [], []
        for r in p.iter(W + "r"):
            va = r.find(f"{W}rPr/{W}vertAlign")
            is_sup = va is not None and va.get(W + "val") == "superscript"
            for t in r.iter():
                if t.tag == W + "t":
                    text.append(t.text or "")
                if is_sup and re.fullmatch(r"\s*\d{1,3}\s*", t.text or ""): sup.append(int(t.text))
                elif t.tag in (W + "footnoteReference", W + "endnoteReference"):
                    fref.append((t.tag.split("}")[1], t.get(W + "id")))
                elif t.tag == W + "tab": text.append("\t")
        blocks.append(dict(text=nfc("".join(text)), level=lvl, table=in_table, sup=sup, fref=fref))
    for el in body:
        if el.tag == W + "p": para(el, False)
        elif el.tag == W + "tbl":
            for p in el.iter(W + "p"): para(p, True)
    notes = {}
    for part, tag in (("word/footnotes.xml", "footnote"), ("word/endnotes.xml", "endnote")):
        if part in z.namelist():
            r = ET.fromstring(z.read(part))
            notes[tag] = {n.get(W + "id"): nfc("".join(t.text or "" for t in n.iter(W + "t")))
                          for n in r.iter(W + tag) if n.get(W + "type") not in ("separator", "continuationSeparator")}
    return blocks, notes

def read_text(path):
    blocks, notes = [], {}
    for line in open(path, encoding="utf-8"):
        line = nfc(line.rstrip("\n"))
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m: blocks.append(dict(text=m.group(2).strip(), level=len(m.group(1)), table=False, sup=[], fref=[]))
        elif re.match(r"^\[\^[^\]]+\]:", line):
            notes.setdefault("footnote", {})[re.match(r"^\[\^([^\]]+)\]", line).group(1)] = line.split(":", 1)[1].strip()
        elif line.strip():
            fr = [("footnote", i) for i in re.findall(r"\[\^([^\]]+)\]", line)]
            blocks.append(dict(text=re.sub(r"\[\^[^\]]+\]", "", line.strip()), level=None, table=line.lstrip().startswith("|"), sup=[], fref=fr))
    return blocks, notes

# ---------------------------------------------------------------- citations
def parse_cites(text):
    out = []
    for m in NARR.finditer(text):
        first, extra, y1, rest = m.groups()
        if first in SKIPWORDS: continue
        years = [y1] + re.findall(YEAR, rest or "")
        second = re.sub(r"^\s+(?:and|&)\s+", "", extra or "") if extra and "et al" not in extra else ""
        for y in years: out.append(dict(surname=first, second=second, etal=bool(extra and "et al" in extra),
                                       year=y, raw=m.group(0), pos=m.start()))
    for m in PAREN.finditer(text):
        inner = m.group(1)
        if re.fullmatch(rf"\s*{YEAR}(?:\s*[,;]\s*(?:{YEAR}|p+\.\s*[\d\-–]+))*\s*", inner): continue # narrative tail
        off = m.start(1)
        for seg0 in inner.split(";"):
            pos = off; off += len(seg0) + 1
            seg = PREFIX.sub("", seg0.strip())
            nm = re.match(rf"({NAME})(\s+et al\.|\s*(?:,\s*{NAME})*,?\s+(?:and|&)\s+{NAME})?", seg)
            ys = re.findall(rf"\b{YEAR}\b", seg)
            if not nm or not ys or nm.group(1) in SKIPWORDS: continue
            extra = nm.group(2) or ""
            second = ""
            if extra and "et al" not in extra:
                names = re.findall(NAME, extra)
                second = names[0] if names else ""
            for y in ys: out.append(dict(surname=nm.group(1), second=second, etal="et al" in extra, year=y,
                                         raw=seg, pos=pos))
    seen, uniq = set(), []
    for c in out: # a narrative cite can also match the paren pattern; keep one
        k = (c["pos"], key(c["surname"]), c["year"])
        if k in seen: continue
        seen.add(k); uniq.append(c)
    return uniq

def entry_key(entry):
    m = re.match(rf"\s*(?:\[?\d+[\].]\s*)?({NAME})", entry)
    ys = re.findall(rf"\b{YEAR}\b", entry)
    return (key(m.group(1)) if m else None, ys[0] if ys else None)

# ---------------------------------------------------------------- audit
def audit(blocks, notes, a):
    bib_names = [a.bib.lower()] if a.bib else BIB_DEFAULT
    cut = [a.cut.lower()] if a.cut else CUT_DEFAULT
    # cut draft material
    for i, b in enumerate(blocks):
        if b["level"] is not None and any(c in b["text"].lower() for c in cut):
            blocks = blocks[:i]; break
    # classify blocks into sections
    sec, bib_level, cur_head = "front", None, ""
    refs, surface, notes_defs, body = [], [], [], []
    body_started = False
    for b in blocks:
        t = b["text"]
        if b["level"] is not None:
            h = t.lower().strip().rstrip(":")
            cur_head = h
            if any(h == n or h.startswith(n) for n in bib_names) and not any(h.startswith(n) for n in NOTES_DEFAULT):
                sec, bib_level = "refs", b["level"]; continue
            if any(h == n for n in NOTES_DEFAULT):
                sec = "notes"; continue
            if sec in ("refs", "notes") and (bib_level is None or b["level"] <= (bib_level or 9)):
                sec = "body"
            elif sec == "front": sec = "body"
            if not body_started and (not a.body_start or a.body_start.lower() in h): body_started = True
            if any(k in h for k in BACK_MATTER): body_started = body_started and False
            continue
        if sec == "refs":
            if t.strip(): refs.append(t.strip())
            continue
        if sec == "notes":
            notes_defs.append(t); surface.append(t); continue
        surface.append(t)
        if body_started and sec == "body" and not b["table"] and "abstract" not in cur_head \
           and not any(k in cur_head for k in BACK_MATTER):
            body.append(t)
    for kind in notes.values(): surface.extend(kind.values())
    surf = "\n".join(surface)
    # A — citations vs references
    cites = parse_cites(surf)
    ekeys = [entry_key(e) for e in refs]
    missing = []
    for c in cites:
        s, y = key(c["surname"]), c["year"]
        hit = any(k == (s, y) for k in ekeys) or any(s in key(e) and y in e for e in refs)
        if not hit: missing.append(f'{c["surname"]} {y}')
    orphans = []
    surf_n = surf.casefold()
    for e, (s, y) in zip(refs, ekeys):
        if not s or not y: continue
        if not re.search(re.escape(s) + r"[\s\S]{0,160}?" + re.escape(y), surf_n): orphans.append(e[:110])
    dup = [f"{s} {y} ×{n}" for (s, y), n in Counter(k for k in ekeys if k[0] and k[1]).items() if n > 1]
    # B — notes
    B = {}
    for kind, defs in notes.items():
        used = [i for b in blocks for (k, i) in b["fref"] if k.startswith(kind)]
        B[f"{kind}s"] = dict(markers=len(used), definitions=len(defs),
                             dangling=sorted(set(used) - set(defs), key=str),
                             unused=sorted(set(defs) - set(used), key=str))
    bracket = [int(n) for t in surface if t not in notes_defs for n in re.findall(r"\[(\d{1,3})\]", t)]
    supers = [n for b in blocks[1:] for n in b["sup"]]
    defs_b = [int(m.group(1)) for t in notes_defs for m in [re.match(r"\s*\[?(\d{1,3})[\].]\s", t)] if m]
    markers = bracket or supers
    if markers or defs_b:
        ms, ds = set(markers), set(defs_b)
        B["manual notes"] = dict(markers=len(markers), definitions=len(defs_b),
                                 dangling=sorted(ms - ds), unused=sorted(ds - ms),
                                 duplicate_definitions=sorted(n for n, c in Counter(defs_b).items() if c > 1),
                                 gaps=sorted(set(range(1, max(ms | ds) + 1)) - ms - ds) if (ms | ds) else [],
                                 format="body [n]" if bracket else "body superscript")
    # H — over-citation in the main body, by author signature
    occ = Counter()
    for c in parse_cites("\n".join(body)):
        sig = key(c["surname"]) + (f" & {key(c['second'])}" if c["second"] else "") + (" et al." if c["etal"] else "")
        occ[(sig, c["year"])] += 1
    over = [f"{s} {y}: {n} body cites" for (s, y), n in occ.most_common() if n > a.occ_cap]
    return dict(reference_entries=len(refs), citations_found=len(cites),
                missing=sorted(set(missing)), orphans=orphans, possible_duplicates=dup,
                notes=B, over_citation=over, occ_cap=a.occ_cap, body_paragraphs=len(body))

def report(r, path):
    L = [f"CITATION INTEGRITY AUDIT — {path}",
         f"Reference entries read: {r['reference_entries']} · citations parsed: {r['citations_found']} · "
         f"main-body paragraphs: {r['body_paragraphs']}", ""]
    n = 0
    def item(sev, label, text):
        nonlocal n; n += 1; L.append(f"{n}. {sev} {label}: {text}")
    for m in r["missing"]: item("[BLOCKER]", "MISSING (cited, no entry)", m)
    for d in r["possible_duplicates"]: item("[POLISH]", "POSSIBLE DUPLICATE ENTRY", d)
    for o in r["orphans"]: item("[POLISH]", "ORPHAN (entry, never cited)", o)
    for k, v in r["notes"].items():
        if v["dangling"]: item("[BLOCKER]", f"NOTES ({k}) dangling markers", v["dangling"])
        if v["unused"]: item("[POLISH]", f"NOTES ({k}) unused definitions", v["unused"])
        if v.get("duplicate_definitions"): item("[BLOCKER]", f"NOTES ({k}) duplicate numbers", v["duplicate_definitions"])
        if v.get("gaps"): item("[POLISH]", f"NOTES ({k}) numbering gaps", v["gaps"])
    for o in r["over_citation"]: item("[POLISH]", f"OVER-CITATION (cap {r['occ_cap']})", o)
    if n == 0: L.append("[CLEAN] No mechanical findings.")
    L += ["", "Notes summary: " + ("; ".join(f"{k}: {v['markers']} markers / {v['definitions']} definitions"
          for k, v in r["notes"].items()) or "no notes found"),
          "Heuristic matching on (first-author surname, year): pair MISSING with ORPHAN before believing either."]
    return "\n".join(L)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manuscript"); ap.add_argument("--bib"); ap.add_argument("--cut")
    ap.add_argument("--body-start"); ap.add_argument("--occ-cap", type=int, default=3)
    ap.add_argument("--json")
    a = ap.parse_args()
    blocks, notes = read_docx(a.manuscript) if a.manuscript.lower().endswith(".docx") else read_text(a.manuscript)
    r = audit(blocks, notes, a)
    print(report(r, a.manuscript))
    if a.json:
        json.dump(r, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
