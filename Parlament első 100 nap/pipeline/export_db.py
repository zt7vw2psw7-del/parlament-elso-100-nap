#!/usr/bin/env python3
"""
Adatbázis exportáló modul: CSV és JSONL formátumba exportálja a kategorizált felszólalásokat és kérdéseket.
"""

import csv
import json
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "parlament_100nap.db")
EXPORT_DIR = os.path.join(BASE_DIR, "exports")

def export_all():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Felszólalások exportálása CSV-be
    cursor.execute("SELECT * FROM v_speeches_categorized ORDER BY period_id, sitting_date")
    rows = cursor.fetchall()
    if rows:
        speeches_csv = os.path.join(EXPORT_DIR, "felszolalasok_kategorizalva.csv")
        with open(speeches_csv, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(rows[0].keys())
            for r in rows:
                writer.writerow(list(r))
        print(f"Exportálva: {speeches_csv} ({len(rows)} sor)")

    # 2. Kérdések exportálása CSV-be
    cursor.execute("SELECT * FROM v_questions_categorized ORDER BY period_id, submission_date")
    rows = cursor.fetchall()
    if rows:
        questions_csv = os.path.join(EXPORT_DIR, "kerdesek_kategorizalva.csv")
        with open(questions_csv, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(rows[0].keys())
            for r in rows:
                writer.writerow(list(r))
        print(f"Exportálva: {questions_csv} ({len(rows)} sor)")

    # 3. Törvényjavaslatok exportálása CSV-be
    cursor.execute("SELECT * FROM v_bills_categorized ORDER BY period_id, CAST(SUBSTR(bill_number, 3) AS INTEGER)")
    rows = cursor.fetchall()
    if rows:
        bills_csv = os.path.join(EXPORT_DIR, "torvenyjavaslatok_kategorizalva.csv")
        with open(bills_csv, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(rows[0].keys())
            for r in rows:
                writer.writerow(list(r))
        print(f"Exportálva: {bills_csv} ({len(rows)} sor)")

    conn.close()

if __name__ == "__main__":
    export_all()
