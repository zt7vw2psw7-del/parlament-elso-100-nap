#!/usr/bin/env python3
"""
OFICIÁLIS PARLAMENTI WEBAPI LETÖLTŐ ÉS FELDOLGOZÓ (PAIR WebAPI Kliens)
Országgyűlés Hivatala hivatalos XML végpontjai alapján:
- ulesnap.cgi: Ciklus ülésnapjai
- felszolalasok.cgi: Egy ülésnap felszólalásainak listája
- felszolalas.cgi: Egy felszólalás teljes szövege és adatai
- iromanyok.cgi / iromany.cgi: Kérdések és interpellációk
"""

import argparse
import json
import os
import re
import ssl
import sqlite3
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "parlament_100nap.db")
CONFIG_PATH = os.path.join(BASE_DIR, "api_config.json")
CACHE_DIR = os.path.join(BASE_DIR, "raw_data", "api_cache")

# Ciklusok és 100 napos időablakok
CYCLES = {
    "2010": {
        "cycle_no": 39,
        "name": "2010-es kormányváltás utáni 100 nap",
        "start_date": "2010-05-14",
        "end_date": "2010-08-22"
    },
    "2026": {
        "cycle_no": 43,
        "name": "2026-os kormányváltás utáni 100 nap",
        "start_date": "2026-05-09",
        "end_date": "2026-08-17"
    }
}

# SSL kontextus macOS-hez
SSL_CTX = ssl._create_unverified_context()

def load_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Nem található a konfigurációs fájl: {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def clean_html_text(raw_html):
    if not raw_html:
        return ""
    text = re.sub(r'<[^>]+>', ' ', raw_html)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_speaker_and_faction(speaker_raw):
    """Kinyeri a szónok nevét és frakcióját pl: 'Dr. Horváth János (Fidesz)'"""
    speaker_raw = speaker_raw.strip()
    m = re.search(r'^(.*?)\s*\((Fidesz|KDNP|MSZP|Jobbik|LMP|TISZA|Mi Hazánk|DK|Független|Párbeszéd|Momentum|MSZP-P)[^\)]*\)', speaker_raw, re.IGNORECASE)
    if m:
        name = m.group(1).strip()
        faction = m.group(2).strip().upper()
        if faction == "MI HAZÁNK":
            faction = "MI_HAZANK"
        return name, faction
    return speaker_raw, "FÜGGETLEN"

def api_get(endpoint, params, config):
    base_url = "https://www.parlament.hu/cgi-bin/web-api-pub"
    params_copy = dict(params)
    params_copy["access_token"] = config["access_token"]
    query_str = urllib.parse.urlencode(params_copy)
    full_url = f"{base_url}/{endpoint}?{query_str}"

    req = urllib.request.Request(full_url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    })
    try:
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=20) as resp:
            return resp.read()
    except Exception as e:
        print(f"Hiba a lekérés során ({endpoint}): {e}")
        return None

def fetch_sitting_days(period_id, config):
    cycle_info = CYCLES[period_id]
    cycle_no = cycle_info["cycle_no"]
    xml_data = api_get("ulesnap.cgi", {"p_ckl": cycle_no}, config)
    if not xml_data:
        return []

    root = ET.fromstring(xml_data)
    days = []
    for ulesnap in root.findall("ulesnap"):
        datum_node = ulesnap.find("datum")
        ulnap_node = ulesnap.find("ulnap")
        if datum_node is None or ulnap_node is None:
            continue
        
        datum_str = datum_node.text.strip().rstrip(".").replace(".", "-")
        ulnap_int = int(ulnap_node.text.strip())
        nap_str = ulesnap.find("nap").text if ulesnap.find("nap") is not None else ""
        ulszak = ulesnap.find("ulszak").text if ulesnap.find("ulszak") is not None else ""
        jelleg = ulesnap.find("ulesjelleg").text if ulesnap.find("ulesjelleg") is not None else "Rendes"

        if cycle_info["start_date"] <= datum_str <= cycle_info["end_date"]:
            days.append({
                "sitting_number": ulnap_int,
                "sitting_date": datum_str,
                "day_name": nap_str,
                "session_name": ulszak,
                "session_type": jelleg.lower()
            })

    days.sort(key=lambda x: x["sitting_number"])
    return days

def fetch_speeches_for_sitting(period_id, sitting_num, config):
    cycle_no = CYCLES[period_id]["cycle_no"]
    xml_data = api_get("felszolalasok.cgi", {"p_ckl": cycle_no, "p_nap": sitting_num}, config)
    if not xml_data:
        return []

    root = ET.fromstring(xml_data)
    speeches = []
    
    # Események és felszólalások bejárása
    for esemeny in root.findall("esemeny"):
        # Az esemény címe a napirendi pont
        agenda_title = (esemeny.text or "").strip()
        for felsz in esemeny.findall("felszolalas"):
            sorsz_node = felsz.find("sorszam")
            if sorsz_node is None or not sorsz_node.text:
                continue
            sorszam = int(sorsz_node.text.strip())
            felszolalo_raw = felsz.find("felszolalo").text if felsz.find("felszolalo") is not None else ""
            felsztip = felsz.find("felsztip").text if felsz.find("felsztip") is not None else "hozzászólás"
            videoido = felsz.find("videoido").text if felsz.find("videoido") is not None else ""

            speaker_name, faction = parse_speaker_and_faction(felszolalo_raw)

            speeches.append({
                "sequence_number": sorszam,
                "speaker_name": speaker_name,
                "faction": faction,
                "speech_type": felsztip,
                "agenda_item": agenda_title or "Napirend",
                "duration_str": videoido
            })

    return speeches

def fetch_speech_detail(period_id, sitting_num, speech_num, config):
    cycle_no = CYCLES[period_id]["cycle_no"]
    xml_data = api_get("felszolalas.cgi", {"p_ckl": cycle_no, "p_uln": sitting_num, "p_felsz": speech_num}, config)
    if not xml_data:
        return ""

    try:
        root = ET.fromstring(xml_data)
        szoveg_node = root.find("felsz_szovege")
        if szoveg_node is not None:
            raw_text = ET.tostring(szoveg_node, encoding="utf-8", method="html").decode("utf-8")
            return clean_html_text(raw_text)
    except Exception as e:
        # Ha nem XML standard tag van a szövegben
        match = re.search(r'<felsz_szovege>(.*?)</felsz_szovege>', xml_data.decode("utf-8", errors="ignore"), re.DOTALL)
        if match:
            return clean_html_text(match.group(1))
    return ""

def download_period_data(period_id, max_days=None):
    config = load_config()
    os.makedirs(CACHE_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cycle_info = CYCLES[period_id]
    print(f"\n=================================================================")
    print(f"🏛️  LETÖLTÉS INDÍTÁSA: {cycle_info['name']}")
    print(f"    Időszak: {cycle_info['start_date']} -> {cycle_info['end_date']}")
    print(f"=================================================================")

    sitting_days = fetch_sitting_days(period_id, config)
    print(f"Talált ülésnapok a 100 napos időszakban: {len(sitting_days)} nap")

    if max_days:
        sitting_days = sitting_days[:max_days]
        print(f"(Korlátozva az első {max_days} ülésnapra tesztelés céljából)")

    total_speeches_saved = 0

    for idx, sday in enumerate(sitting_days, 1):
        sit_num = sday["sitting_number"]
        sit_id = f"{period_id}_{sit_num:03d}"
        sit_date = sday["sitting_date"]

        print(f"\n[{idx}/{len(sitting_days)}] Ülésnap #{sit_num} ({sit_date} - {sday['day_name']})...")

        # Ülésnap mentése adatbázisba
        cursor.execute("""
            INSERT OR REPLACE INTO sitting_day (id, period_id, sitting_number, sitting_date, session_type, source_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (sit_id, period_id, sit_num, sit_date, sday["session_type"], f"https://www.parlament.hu/cgi-bin/web-api-pub/ulesnap.cgi?p_ckl={cycle_info['cycle_no']}"))
        conn.commit()

        # Felszólalások listájának lekérése
        speeches = fetch_speeches_for_sitting(period_id, sit_num, config)
        print(f"   -> {len(speeches)} felszólalás található az ülésnapon.")

        # Kiszűrjük azokat, amelyeket még le kell tölteni
        to_download = []
        for sp in speeches:
            sp_num = sp["sequence_number"]
            speech_id = f"{sit_id}_{sp_num:03d}"
            cursor.execute("SELECT id, word_count FROM speech WHERE id = ?", (speech_id,))
            existing = cursor.fetchone()
            if not existing or not existing[1] or existing[1] < 20:
                to_download.append(sp)

        if not to_download:
            print(f"      (Minden felszólalás már le van töltve ebből az ülésnapból.)")
            continue

        print(f"      Letöltendő új felszólalások: {len(to_download)} db...")

        # Párhuzamos szövegletöltés (max 5 szál a szerver kímélése érdekében)
        from concurrent.futures import ThreadPoolExecutor

        def fetch_one(sp):
            sp_num = sp["sequence_number"]
            text = fetch_speech_detail(period_id, sit_num, sp_num, config)
            return sp, text

        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(fetch_one, to_download))

        for sp, full_text in results:
            sp_num = sp["sequence_number"]
            speech_id = f"{sit_id}_{sp_num:03d}"

            if not full_text:
                full_text = f"{sp['speaker_name']} felszólalása: {sp['agenda_item']}"

            word_count = len(full_text.split())

            # Beszédtípus normalizálása
            stype = "HOZZASZOLAS"
            st_lower = sp["speech_type"].lower()
            if "napirend előtt" in st_lower or "napirend előtti" in st_lower:
                stype = "NAPIREND_ELOTTI"
            elif "expozé" in st_lower or "nyitóbeszéd" in st_lower or "előterjesztő" in st_lower:
                stype = "EXPOZE"
            elif "vezérszónok" in st_lower:
                stype = "VEZERSZONOKI"
            elif "kétperces" in st_lower:
                stype = "KETPERCES"
            elif "ügyrend" in st_lower:
                stype = "UGYRENDI"
            elif "zárszó" in st_lower:
                stype = "ZARSZO"

            group_id = f"{period_id}_{sp['faction']}"

            cursor.execute("""
                INSERT OR REPLACE INTO speech (
                    id, period_id, sitting_day_id, sequence_number, speaker_name,
                    group_id, speech_type_code, agenda_item, word_count, full_text, source_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                speech_id, period_id, sit_id, sp_num, sp["speaker_name"],
                group_id, stype, sp["agenda_item"], word_count, full_text,
                f"https://www.parlament.hu/cgi-bin/web-api-pub/felszolalas.cgi?p_ckl={cycle_info['cycle_no']}&p_uln={sit_num}&p_felsz={sp_num}"
            ))

            total_speeches_saved += 1

        conn.commit()

    conn.close()
    print(f"\n✅ {period_id} letöltés kész! Összesen {total_speeches_saved} új beszéd mentve.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parlamenti WebAPI letöltő.")
    parser.add_argument("--period", choices=["2010", "2026", "all"], default="all", help="Korszak letöltése")
    parser.add_argument("--max-days", type=int, default=None, help="Legfeljebb hány ülésnapot töltsön le")
    args = parser.parse_args()

    periods_to_run = ["2010", "2026"] if args.period == "all" else [args.period]
    for p in periods_to_run:
        download_period_data(p, max_days=args.max_days)

    # Automatikus utómunka: témabesorolás, múltbírálat és CSV export
    print("\n🏷️  Automatikus témabesorolás futtatása az új adatokon...")
    from classify import classify_unclassified_speeches
    classify_unclassified_speeches()

    print("\n🔍 Kormánypárti képviselők múltra való reflexiójának elemzése...")
    from blame_detector import run_retrospective_critique_analysis
    run_retrospective_critique_analysis()

    print("\n📊 Friss CSV exportálás...")
    from export_db import export_all
    export_all()

    print("\n🎉 TELJES FOLYAMAT SIKERESEN LEFUTOTT!")
