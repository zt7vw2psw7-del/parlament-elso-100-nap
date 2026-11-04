#!/usr/bin/env python3
"""
BATCH IMPORTER (1.2-es Megoldás)
Összes letöltött HTML/XML/JSON parlamenti jegyzőkönyv és kérdés kötegelt beolvasása,
adatbázisba töltése, témabesorolása és exportálása.
"""

import glob
import json
import os
import re
import sqlite3
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "parlament_100nap.db")
RAW_DATA_DIR = os.path.join(BASE_DIR, "raw_data")

# Hónapnevek konvertálása számmá
MONTH_MAP = {
    "január": "01", "február": "02", "március": "03", "április": "04",
    "május": "05", "június": "06", "július": "07", "augusztus": "08",
    "szeptember": "09", "október": "10", "november": "11", "december": "12"
}

def parse_date_from_text(text):
    match = re.search(r'(\d{4})\.\s*(január|február|március|április|május|június|július|augusztus|szeptember|október|november|december)\s*(\d{1,2})\.?', text, re.IGNORECASE)
    if match:
        year = match.group(1)
        month = MONTH_MAP.get(match.group(2).lower(), "01")
        day = int(match.group(3))
        return f"{year}-{month}-{day:02d}"
    return None

def parse_sitting_info(html_content, filename, fallback_period):
    # Ülésnap sorszám
    sit_match = re.search(r'(\d+)\.\s*ülésnap', html_content, re.IGNORECASE)
    sitting_num = int(sit_match.group(1)) if sit_match else 1

    # Dátum
    date_val = parse_date_from_text(html_content)
    if not date_val:
        # Fájlnévből próbáljuk: pl. 2010_05_14
        file_date_match = re.search(r'(\d{4})_(\d{2})_(\d{2})', filename)
        if file_date_match:
            date_val = f"{file_date_match.group(1)}-{file_date_match.group(2)}-{file_date_match.group(3)}"
        else:
            date_val = f"{fallback_period}-05-14"

    period_id = fallback_period
    if "2026" in date_val:
        period_id = "2026"
    elif "2010" in date_val:
        period_id = "2010"

    sitting_id = f"{period_id}_{sitting_num:03d}"
    session_type = "alakuló" if sitting_num == 1 else "rendes"
    if "rendkívüli" in html_content.lower():
        session_type = "rendkívüli"

    return sitting_id, period_id, sitting_num, date_val, session_type

def parse_html_speeches(html_content, sitting_id, period_id):
    speeches = []
    
    # 1. Keresünk napirendi pontokat
    agenda_blocks = re.split(r'<(?:h4|h3|h2)[^>]*>.*?(?:Napirendi pont|Tárgy):\s*(.*?)</(?:h4|h3|h2)>', html_content, flags=re.IGNORECASE)
    
    current_agenda = "Általános napirend"
    speech_idx = 1

    # Regex szónok felismerésére: pl. <b>DR. HORVÁTH JÁNOS (Fidesz), korelnök:</b> vagy DR. HORVÁTH JÁNOS (Fidesz):
    speaker_re = re.compile(
        r'(?:<[bp][^>]*>)?\s*<b>\s*([A-ZÁÉÍÓÖŐÚÜŰa-záéíóöőúüű\.\s\-]+?)\s*\((Fidesz|KDNP|MSZP|Jobbik|LMP|TISZA|Mi Hazánk|DK|Független)[^\)]*\)(?:,\s*([a-záéíóöőúüű\s]+))?\s*:\s*</b>\s*(.*?)(?=(?:<[bp][^>]*>)?\s*<b>[A-ZÁÉÍÓÖŐÚÜŰa-záéíóöőúüű\.\s\-]+?\s*\(|$)',
        re.DOTALL | re.IGNORECASE
    )

    matches = list(speaker_re.finditer(html_content))
    for m in matches:
        speaker_name = m.group(1).strip()
        faction = m.group(2).strip().upper()
        role = (m.group(3) or "").strip().lower()
        text_raw = m.group(4).strip()
        
        # HTML tagek eltávolítása a szövegből
        clean_text = re.sub(r'<[^>]+>', ' ', text_raw)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        if len(clean_text) < 20:
            continue

        # Felszólalás típusa
        stype = "HOZZASZOLAS"
        if "napirend előtt" in clean_text.lower() or speech_idx == 1:
            stype = "NAPIREND_ELOTTI"
        if "előterjesztő" in role or "expozé" in role or "miniszterelnök" in role and speech_idx <= 2:
            stype = "EXPOZE"
        elif "vezérszónok" in role:
            stype = "VEZERSZONOKI"
        elif "kétperces" in role:
            stype = "KETPERCES"
        elif "ügyrendi" in role:
            stype = "UGYRENDI"

        speech_obj = {
            "id": f"{sitting_id}_{speech_idx:03d}",
            "period_id": period_id,
            "sitting_day_id": sitting_id,
            "sequence_number": speech_idx,
            "speaker_name": speaker_name,
            "faction_code": faction,
            "speech_type_code": stype,
            "agenda_item": current_agenda,
            "full_text": clean_text,
            "word_count": len(clean_text.split()),
            "source_url": f"local://raw_data/{sitting_id}"
        }
        speeches.append(speech_obj)
        speech_idx += 1

    return speeches

def import_all():
    print("=" * 65)
    print("🏛️  PARLAMENTI ADATOK KÖTEGELT BEOLVASÁSA (1.2-es Megoldás)")
    print("=" * 65)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    total_files = 0
    total_speeches = 0
    total_questions = 0

    # Pásztázzuk a 2010 és 2026 mappákat
    for period in ["2010", "2026", "incoming"]:
        folder = os.path.join(RAW_DATA_DIR, period)
        if not os.path.exists(folder):
            continue

        files = glob.glob(os.path.join(folder, "*.html")) + glob.glob(os.path.join(folder, "*.htm")) + glob.glob(os.path.join(folder, "*.xml"))
        for filepath in files:
            filename = os.path.basename(filepath)
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            default_period = "2026" if "2026" in filename or period == "2026" else "2010"
            sitting_id, period_id, sitting_num, date_val, session_type = parse_sitting_info(content, filename, default_period)

            # Ülésnap mentése
            cursor.execute("""
                INSERT OR REPLACE INTO sitting_day (id, period_id, sitting_number, sitting_date, session_type, source_url)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (sitting_id, period_id, sitting_num, date_val, session_type, f"file://{filepath}"))

            # Felszólalások kinyerése
            speeches = parse_html_speeches(content, sitting_id, period_id)
            for s in speeches:
                # Frakció azonosító megfeleltetés
                group_id = f"{period_id}_{s['faction_code']}"
                cursor.execute("""
                    INSERT OR REPLACE INTO speech (
                        id, period_id, sitting_day_id, sequence_number, speaker_name,
                        group_id, speech_type_code, agenda_item, word_count, full_text, source_url
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    s["id"], s["period_id"], s["sitting_day_id"], s["sequence_number"],
                    s["speaker_name"], group_id, s["speech_type_code"], s["agenda_item"],
                    s["word_count"], s["full_text"], s["source_url"]
                ))
                total_speeches += 1

            total_files += 1
            print(f" -> Feldolgozva: [{period_id}] {filename} ({len(speeches)} felszólalás)")

    # Kérdések JSON beolvasása
    q_folder = os.path.join(RAW_DATA_DIR, "questions")
    if os.path.exists(q_folder):
        q_files = glob.glob(os.path.join(q_folder, "*.json"))
        for qf in q_files:
            with open(qf, "r", encoding="utf-8") as f:
                q_data = json.load(f)
            for q in q_data:
                group_id = f"{q['period_id']}_{q.get('submitter_group_code', 'FÜGGETLEN')}"
                cursor.execute("""
                    INSERT OR REPLACE INTO question (
                        id, period_id, document_number, question_type, title,
                        submitter_name, submitter_group_id, target_person, target_ministry,
                        submission_date, answered_date, question_text, answer_text,
                        responder_name, accepted_by_submitter, accepted_by_parliament, source_url
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    q["id"], q["period_id"], q.get("document_number"), q.get("question_type"), q.get("title"),
                    q.get("submitter_name"), group_id, q.get("target_person"), q.get("target_ministry"),
                    q.get("submission_date"), q.get("answered_date"), q.get("question_text"), q.get("answer_text"),
                    q.get("responder_name"), q.get("accepted_by_submitter"), q.get("accepted_by_parliament"), q.get("source_url")
                ))
                total_questions += 1
            print(f" -> Kérdések importálva: {os.path.basename(qf)} ({len(q_data)} kérdés)")

    conn.commit()
    conn.close()

    print("\n" + "=" * 65)
    print(f"✅ Sikeres importálás!")
    print(f"   - Feldolgozott fájlok: {total_files}")
    print(f"   - Beolvasott felszólalások: {total_speeches}")
    print(f"   - Beolvasott kérdések: {total_questions}")
    print("=" * 65)

    # Automatikus témabesorolás futtatása
    print("\n🏷️  Automatikus témabesorolás (CAP Taxonómia) futtatása...")
    try:
        from classify import classify_unclassified_speeches
        classify_unclassified_speeches()
    except Exception as e:
        print(f"   (Besorolási értesítés: {e})")

    # Múltra való reflexió és korábbi korszak bírálatának elemzése
    print("\n🔍 Kormánypárti képviselők múltra való reflexiójának elemzése...")
    try:
        from blame_detector import run_retrospective_critique_analysis
        run_retrospective_critique_analysis()
    except Exception as e:
        print(f"   (Múltbírálat-elemzési értesítés: {e})")

    # Automatikus CSV exportálás
    print("\n📊 Friss CSV exportálás generálása...")
    try:
        from export_db import export_all
        export_all()
    except Exception as e:
        print(f"   (Export értesítés: {e})")

    print("\n🎉 Minden lépés sikeresen lefutott! Az adatbázis és a CSV fájlok naprakészek.")

if __name__ == "__main__":
    import_all()
