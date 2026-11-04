#!/usr/bin/env python3
"""
Múltra való reflexió és korábbi korszakot bíráló diskurzuselemző modul
(Retrospective Regime Critique / Blame Detector)

Kiszűri, hogy a felszólaló (különösen a kormánypárti képviselők) hányszor és milyen intenzitással
utalt vissza a korábbi kormányzati korszakra úgy, mintha az rossz, káros vagy romboló lett volna.
"""

import json
import os
import re
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "parlament_100nap.db")

# Kifejezéstárak korszakonként
PATTERNS_2010 = [
    r'\belmúlt\s+(?:nyolc|8)\s+év\w*',
    r'\bmegörököl\w+',
    r'\bür(?:es|ített)\s+államkassz\w*',
    r'\bcsőd\s+szél\w*',
    r'\bromhalmaz\w*',
    r'\beladósít\w+',
    r'\bfelelőtlen\s+(?:kormányzás|gazdálkodás|politika)\w*',
    r'\bszocialist\w+\s+(?:bűn|kormány|rombolás)\w*',
    r'\bGyurcsány\w*',
    r'\bBajnai\w*',
    r'\b2004\.\s*december\s*5\w*',
    r'\bgyászos\s+népszavazás\w*',
    r'\beltapsol\w+',
    r'\bkifoszt\w+',
    r'\bdevizahitel\w*\s+válság\w*'
]

PATTERNS_2026 = [
    r'\belmúlt\s+(?:tizenhat|16)\s+év\w*',
    r'\bNER\b',
    r'\bOrbán-kormány\w*',
    r'\bintézményesített\s+korrupció\w*',
    r'\bromokban\s+hever\w*',
    r'\bszétvert\w+',
    r'\bszétzilál\w+',
    r'\bellopott\s+(?:forint|milliárd|közpénz|vagyon)\w*',
    r'\bhátrahagyott\s+(?:káosz|adósság|romok)\w*',
    r'\bmegörökölt\s+állapot\w*',
    r'\bkorábbi\s+rezsim\w*',
    r'\belnyomó\s+rendszer\w*',
    r'\belszámoltat\w+',
    r'\bszámonkérés\w*'
]

def analyze_speech_for_blame(text, period_id):
    """
    Elemez egy felszólalás szöveget és megállapítja, volt-e benne visszautalás az előző korszak bűneire/hibáira.
    """
    patterns = PATTERNS_2010 if period_id == "2010" else PATTERNS_2026
    target_era = "2002-2010 (MSZP-SZDSZ kormányok)" if period_id == "2010" else "2010-2026 (Fidesz-NER korszak)"

    # Mondatokra bontás
    sentences = re.split(r'(?<=[.!?])\s+', text)
    matched_phrases = []
    excerpts = []

    for sentence in sentences:
        sentence_clean = sentence.strip()
        if not sentence_clean:
            continue
        
        hit_in_sentence = False
        for pat in patterns:
            found = re.findall(pat, sentence_clean, re.IGNORECASE)
            if found:
                for f in found:
                    if f.lower() not in [p.lower() for p in matched_phrases]:
                        matched_phrases.append(f)
                hit_in_sentence = True
        
        if hit_in_sentence:
            excerpts.append(sentence_clean)

    mention_count = len(excerpts)
    has_critique = 1 if mention_count > 0 else 0
    intensity = min(1.0, mention_count * 0.35)

    return {
        "has_past_critique": has_critique,
        "target_era": target_era if has_critique else None,
        "critique_intensity": round(intensity, 2),
        "mention_count": mention_count,
        "matched_patterns": json.dumps(matched_phrases, ensure_ascii=False) if matched_phrases else None,
        "excerpts": " | ".join(excerpts[:3]) if excerpts else None
    }

def run_retrospective_critique_analysis():
    print("=" * 65)
    print("🔍 MÚLTRA VALÓ REFLEXIÓ ÉS KORÁBBI KORSZAK BÍRÁLATÁNAK ELEMZÉSE")
    print("=" * 65)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.id, s.period_id, s.speaker_name, pg.governing_status, s.full_text
        FROM speech s
        LEFT JOIN parliamentary_group pg ON s.group_id = pg.id
    """)
    speeches = cursor.fetchall()
    print(f"Elemzendő felszólalások száma: {len(speeches)}")

    detected_count = 0
    gov_detected_count = 0

    for speech_id, period_id, speaker_name, gov_status, text in speeches:
        res = analyze_speech_for_blame(text, period_id)
        
        cursor.execute("""
            INSERT OR REPLACE INTO speech_retrospective_critique 
            (speech_id, has_past_critique, target_era, critique_intensity, mention_count, matched_patterns, excerpts)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            speech_id, res["has_past_critique"], res["target_era"],
            res["critique_intensity"], res["mention_count"],
            res["matched_patterns"], res["excerpts"]
        ))

        if res["has_past_critique"] == 1:
            detected_count += 1
            if gov_status == "kormany":
                gov_detected_count += 1
                print(f" [Múltbírálat észlelve] [{period_id} Kormánypárt] {speaker_name}: {res['mention_count']} említés")
                if res['excerpts']:
                    print(f"    -> Idézet: \"{res['excerpts'][:120]}...\"")

    conn.commit()
    conn.close()

    print("\n" + "=" * 65)
    print(f"✅ Elemzés befejezve!")
    print(f"   - Összes múltra reflektáló beszéd: {detected_count}")
    print(f"   - Ebből kormánypárti képviselő beszéde: {gov_detected_count}")
    print("=" * 65)

if __name__ == "__main__":
    run_retrospective_critique_analysis()
