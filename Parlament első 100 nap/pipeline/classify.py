#!/usr/bin/env python3
"""
Témabesoroló motor (Heurisztikus és LLM-alapú klasszifikáció)
Felszólalások és kérdések automatikus kategorizálása téma, konfidencia és kulcsszavak szerint.
"""

import json
import os
import re
import sqlite3
import sys

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "parlament_100nap.db")
TAXONOMY_PATH = os.path.join(os.path.dirname(__file__), "..", "topics_taxonomy.json")

def load_taxonomy():
    with open(TAXONOMY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def heuristic_classify_text(text, agenda_item, taxonomy):
    """
    Kulcsszó- és szabályalapú osztályozó a témakategóriák súlyozott előfordulása alapján.
    """
    combined_text = f"{agenda_item or ''} {text or ''}".lower()
    scores = {}

    for cat in taxonomy:
        cat_code = cat["code"]
        keywords = cat.get("keywords", [])
        score = 0
        matched_kw = []

        # Napirendi pontban való előfordulás 3x-os súlyozást kap
        agenda_lower = (agenda_item or "").lower()
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower in agenda_lower:
                score += 3
                matched_kw.append(kw)
            elif kw_lower in combined_text:
                # Szövegbeli előfordulások száma
                count = len(re.findall(r'\b' + re.escape(kw_lower) + r'\w*', combined_text))
                if count > 0:
                    score += min(count, 5) # capping per keyword
                    matched_kw.append(kw)

        if score > 0:
            scores[cat_code] = {"score": score, "matched": matched_kw}

    if not scores:
        return "EGYEB_UGYRENDI", None, 0.5, ["általános"], "Általános felszólalás vagy ügyrendi kérdés."

    sorted_cats = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
    primary = sorted_cats[0][0]
    secondary = sorted_cats[1][0] if len(sorted_cats) > 1 else None
    
    # Bizonyosság becslése (arányosítás)
    top_score = sorted_cats[0][1]["score"]
    confidence = min(0.95, 0.60 + (top_score * 0.05))
    matched_keywords = sorted_cats[0][1]["matched"][:5]
    summary = f"Fő téma: {primary} a szövegben azonosított kulcsfogalmak alapján."

    return primary, secondary, confidence, matched_keywords, summary

def classify_unclassified_speeches():
    taxonomy = load_taxonomy()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Keresünk olyan felszólalásokat, amelyek még nincsenek besorolva
    cursor.execute("""
        SELECT s.id, s.agenda_item, s.full_text
        FROM speech s
        LEFT JOIN speech_classification sc ON s.id = sc.speech_id
        WHERE sc.id IS NULL
    """)
    unclassified = cursor.fetchall()
    print(f"Besorolásra váró felszólalások száma: {len(unclassified)}")

    for speech_id, agenda_item, full_text in unclassified:
        primary, secondary, confidence, keywords, summary = heuristic_classify_text(full_text, agenda_item, taxonomy)
        kw_str = ", ".join(keywords)

        cursor.execute("""
            INSERT INTO speech_classification 
            (speech_id, primary_topic_code, secondary_topic_code, confidence, summary, extracted_keywords, classification_method)
            VALUES (?, ?, ?, ?, ?, ?, 'keyword_rules')
        """, (speech_id, primary, secondary, confidence, summary, kw_str))

    conn.commit()
    conn.close()
    print("Besorolás sikeresen frissítve!")

if __name__ == "__main__":
    classify_unclassified_speeches()
