---
name: vcia
description: Citation Integrity Audit (VCIA). Audits a manuscript's citations and references (.docx, .md, .txt) before submission or review. Performs mechanical checks (missing citations, orphan references, duplicates, footnote/endnote numbering, over-citation) and qualitative judgement checks (claim-source alignment, construct validity, target-journal coverage, literature gaps).
---

# Citation Integrity Audit (vcia)

A reusable audit of a manuscript’s citations. It changes nothing by default: it reports, and the author decides. Run it after each round of citation edits; it is cheap to repeat.

## The Goal

A reviewer who follows one citation and finds it wrong stops trusting all of them. This audit finds, before the reviewer does, every citation that is missing from the reference list, every entry nobody cites, every note that points nowhere, and every claim the cited source does not make.

## Workflow

### Step 1: Run the mechanical checks (A, B, H) with the script

```bash
python3 scripts/vcia.py manuscript.docx # also .md or .txt
python3 scripts/vcia.py manuscript.docx --bib "References" --occ-cap 3 --json report.json
```

The script needs only Python 3.9+ (standard library). It reads the body and every table cell, the footnotes and endnotes, and each reference list it can find.

Useful options:
- `--bib "References"`: Heading text of the reference list (default: References / Bibliography / Works Cited)
- `--cut "not for submission"`: Ignore everything from this heading on (draft material after the paper)
- `--body-start "Introduction"`: Where the main body starts, for the over-citation count
- `--occ-cap 3`: Flag any work cited more often than this in the main body
- `--json FILE`: Write the findings as JSON too

### Step 2: Read the script’s report with its limits in mind

The script matches a citation to an entry on (first-author surname, year). That is a heuristic, not a proof. Before believing any finding:
1. **Pair MISSING with ORPHAN.** A false “missing” usually has a mirror false “orphan”: a possessive (`Smith's (2018)`), a particle (`van Dijk` vs `Dijk, T. van`), a three-author narrative cite keyed on the last name, a label prefix (`(Wordfish: Slapin & Proksch, 2008)`). Clear the pairs first; only the unpaired residue is real.
2. **Check for a second reference list.** An appendix with its own references makes every cite resolved there look “missing” if only the first list was read. Search the second list before reporting.
3. **An orphan is real only if the entry is absent from the whole paper:** body, notes, appendices and tables. A reference cited only in an appendix is not an orphan.

### Step 3: Do the judgement checks (C, D, E, F, G, I) by reading

These need the sources, not the script. Work through them for the citations that carry the argument.

### Step 4: Report (see Output format), then fix only what the author approves

## The Nine Checks

- **A — In-text ↔ reference list.** Every in-text citation has an entry; every entry is cited. Both directions: MISSING (cited, no entry) and ORPHAN (entry, never cited). Handle et al., &, multiple authors, year suffixes (2024a), narrative (`Author (Year)`) and parenthetical (`(Author Year; Author Year, Year)`) forms. Hygiene sub-checks: duplicate entries (the same work listed twice under different author orders), title typos, and two works by the same authors in the same year confused with each other.
- **B — Notes.** Every footnote or endnote marker ([n] or superscript) has a definition, and every definition is used. Flag duplicate numbers, gaps, dangling markers and orphan notes, and a format mismatch (body [1] against notes 1.). Renumbering stays in lockstep across markers and definitions.
- **C — Non-academic sources ↔ supplementary list.** If the paper keeps a separate list or archive of news and web sources, every such source cited in the text is on it, every item on it is cited, and the URL in the text matches the URL on the list.
- **D — Claim ↔ source.** For each load-bearing citation, the cited work actually makes the claim: find a verbatim quote with a page number. Quick triage, the title test: compare the entry’s title with the claim it backs; a topic mismatch is the tell. Every quantified or specific claim (a count, a percentage, a threshold, a dated fact) carries a page in the citation: `(Author Year, p. N)`.
- **E — Construct validity.** A citation that anchors a named concept, measure, method, dataset or theory must point to the work that owns it, and the paper must use it faithfully. Four questions:
  1. *Origin:* does the construct come from this work, or is it merely mentioned there?
  2. *Definition:* does the paper use the source’s definition, or stretch it?
  3. *Measure:* is the instrument the same version, category count and threshold?
  4. *Scope:* was it validated on this kind of data, or is the paper transferring it silently? A wrong origin or a nonexistent attribution is a blocker; stretching and silent transfer are polish, unless the construct carries the design.
- **F — Target-journal coverage.** Count reference-list entries published in the target journal (match former names and abbreviations). Advisory only: zero is worth a look, never a reason to pad.
- **G — Literature gap.** The ten or so high-quality works in the paper’s scope that it does not cite, ranked by importance. Advisory only. Every suggestion must be verified to exist (authors, venue, year, a DOI that resolves) before it is shown; fewer verified beats more guessed.
- **H — Over-citation.** No single work cited more than N times (default 3) in the main body. Count by the full author signature, not by surname and year, so two different works by the same first author in the same year stay separate. Exclude the abstract, reference list, tables, notes and back matter. Advisory: the author keeps the load-bearing instances and never orphans the entry.
- **I — Central-term literature.** Search for top-journal work that uses the paper’s own central concept in the same empirical domain and is not cited. Doubles as evidence that the concept is an established one.

## Gotchas (each cost a real paper time)

1. **Tables hide citations.** A reader that walks paragraphs only never sees table cells, so markers and citations inside tables look missing. The script reads tables; any other tool must too.
2. **Draft material after the paper pollutes the audit.** A file that carries notes, a second introduction or planning text after the real paper produces phantom orphans. Use `--cut`.
3. **`et al.` breaks naive patterns.** Never span the period in `et al.` with a `[^.]` character class; it silently drops every such citation.
4. **Diacritics.** Éltető, Wójcik, Adăscăliței fail byte-exact matching when one side is decomposed. Normalise both sides (Unicode NFC) and anchor on surname plus year.
5. **Verify the reference style’s exact variant before any mass reformat.** “Harvard” alone names several incompatible styles; some journals use Chicago notes and bibliography instead. Read the journal’s own guide and two of its recent articles first.
6. **A pasted reference list may be degraded.** Check against the manuscript itself before “fixing” something that was only broken in the paste.
7. **The same authors, the same year, two works.** A book and its companion article often share both. Keep them apart and cite the one that makes the claim.

## Reference-List Format Check

For each entry: author–date form, italics on the journal or book title (not on the article title), volume (issue), page range with an en dash, place and publisher for books, editors for chapters, consistent title case, DOIs present or absent throughout. For double-blind review, every self-citation in the text and in the list becomes `[Author]`, and the acknowledgements, funding and file metadata are checked for names.

## Honesty Rule

Never invent a quote or a page. If the open web cannot verify a quote from a book, say so and ask for the print or PDF copy. A citation flagged “unverified” is a finding, not a failure. Books often resist online checks: expect to confirm a page for perhaps one monograph in three.

## Output Format

```text
CITATION INTEGRITY AUDIT — <manuscript> — <date>
Scope: body + tables + notes + appendices; reference lists read: <names>

[BLOCKER] Blockers
1. MISSING Smith 2019 — cited in §3, no entry
2. D (claim ↔ source) Jones 2020 cited for X; the paper is about Y

[POLISH] Polish
3. ORPHAN Brown 2017 — entry never cited
4. H (over-citation) Lee et al. 2021 — 5 body cites (cap 3)

[CLEAN] Clean
- Notes: 24 markers, 24 definitions, no gaps
```

Numbered, one finding per line, severity first, full names beside every abbreviation, confirmed findings kept apart from ones still to verify.

## What NOT to Do

- Don’t fix author-facing citations beyond unambiguous mechanical errors without asking.
- Don’t delete an “orphan” before checking appendices, tables and notes.
- Don’t report a script finding as confirmed before pairing MISSING with ORPHAN.
- Don’t suggest a reference you have not verified exists.
- Don’t reformat a whole reference list on a guessed style.
