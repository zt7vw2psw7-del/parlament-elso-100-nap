#!/usr/bin/env python3
"""
Draghi-jelentés EP Adatbázis Lekérdező Eszköz (Query Tool)
Használat:
  python3 query_database.py --stats
  python3 query_database.py --speeches
  python3 query_database.py --acts
  python3 query_database.py --questions
  python3 query_database.py --hungarian
  python3 query_database.py --pillar PILLAR_4
  python3 query_database.py --search "adósság"
"""

import sqlite3
import argparse
import sys

DB_PATH = "ep_draghi_database.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def print_stats():
    conn = get_connection()
    cur = conn.cursor()
    
    print("\n" + "="*80)
    print(" 📊 DRAGHI-JELENTÉS EURÓPAI PARLAMENTI ADATBÁZIS - STATISZTIKAI ÁTTEKINTÉS")
    print("="*80)
    
    cur.execute("SELECT COUNT(*) FROM plenary_debates")
    debates_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM speeches")
    speeches_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM official_acts")
    acts_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM parliamentary_questions")
    questions_count = cur.fetchone()[0]
    
    print(f" ▸ Kiemelt plenáris viták száma:      {debates_count} ülésnap")
    print(f" ▸ Részletesen rögzített felszólalás:  {speeches_count} felszólalás")
    print(f" ▸ Hivatalos aktus / eljárás:         {acts_count} jogalkotási/nem jogalkotási aktus")
    print(f" ▸ Parlamenti írásbeli/szóbeli kérdés: {questions_count} kérdés")
    print("-" * 80)
    
    print("\n🏛️  FELSZÓLALÁSOK FRAKCIÓK SZERINTI MEGOSZLÁSA:")
    cur.execute("""
        SELECT political_group, COUNT(*), GROUP_CONCAT(speaker_name, ', ')
        FROM speeches 
        GROUP BY political_group 
        ORDER BY COUNT(*) DESC
    """)
    for grp, count, speakers in cur.fetchall():
        print(f"  • {grp:<12} : {count:>2} felszólalás  (Felszólalók: {speakers})")
        
    print("\n📑 HIVATALOS AKTUSOK PILLÉREK SZERINT:")
    cur.execute("""
        SELECT tp.pillar_code, tp.pillar_name_hu, COUNT(oa.id)
        FROM thematic_pillars tp
        LEFT JOIN official_acts oa ON oa.draghi_pillar = tp.pillar_code
        GROUP BY tp.pillar_code
        ORDER BY tp.pillar_code
    """)
    for code, name, count in cur.fetchall():
        print(f"  • [{code}] {name:<45} : {count} aktus")

    print("\n🇭🇺 MAGYAR KÉPVISELŐI MEGSZÓLALÁSOK ÉS KÉRDÉSEK:")
    cur.execute("SELECT COUNT(*) FROM speeches WHERE country = 'Magyarország'")
    hu_speeches = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM parliamentary_questions WHERE country = 'Magyarország'")
    hu_questions = cur.fetchone()[0]
    print(f"  • Magyar képviselői plenáris felszólalások a mintában: {hu_speeches}")
    print(f"  • Magyar képviselői parlamenti kérdések a mintában:    {hu_questions}")
    print("="*80 + "\n")
    conn.close()

def list_speeches(pillar=None, group=None):
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT id, date, speaker_name, political_group, national_party, key_stance, speech_summary_hu FROM speeches WHERE 1=1"
    params = []
    if pillar:
        query += " AND draghi_pillar = ?"
        params.append(pillar)
    if group:
        query += " AND political_group = ?"
        params.append(group)
    query += " ORDER BY date ASC"
    
    cur.execute(query, params)
    rows = cur.fetchall()
    print(f"\n📢 FELSZÓLALÁSOK ({len(rows)} találat):")
    print("-" * 100)
    for r in rows:
        print(f"[{r[1]}] {r[2]} ({r[3]} - {r[4]}) | Álláspont: {r[5]}")
        print(f"   Összegzés: {r[6]}\n")
    conn.close()

def list_acts():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT procedure_ref, title_hu, act_type, lead_committee, status, adoption_date FROM official_acts ORDER BY adoption_date ASC")
    rows = cur.fetchall()
    print(f"\n📜 HIVATALOS AKTUSOK ÉS ELJÁRÁSOK ({len(rows)} találat):")
    print("-" * 100)
    for r in rows:
        print(f"• Referencia: {r[0]} | Típus: {r[2]} | Bizottság: {r[3]} | Státusz: {r[4]} ({r[5]})")
        print(f"  Cím: {r[1]}\n")
    conn.close()

def list_hungarian():
    conn = get_connection()
    cur = conn.cursor()
    print("\n🇭🇺 MAGYAR KÉPVISELŐK MEGSZÓLALÁSAI ÉS AKTUSAI:")
    print("=" * 80)
    cur.execute("SELECT date, speaker_name, political_group, national_party, speech_summary_hu FROM speeches WHERE country = 'Magyarország'")
    for r in cur.fetchall():
        print(f"Felszólalás [{r[0]}]: {r[1]} ({r[2]} - {r[3]})")
        print(f"  {r[4]}\n")
    
    cur.execute("SELECT question_ref, submission_date, mep_name, subject_hu FROM parliamentary_questions WHERE country = 'Magyarország'")
    for r in cur.fetchall():
        print(f"Kérdés [{r[0]} - {r[1]}]: {r[2]}")
        print(f"  Tárgy: {r[3]}\n")
    conn.close()

def search_database(keyword):
    conn = get_connection()
    cur = conn.cursor()
    kw = f"%{keyword}%"
    print(f"\n🔍 KERESÉS: '{keyword}'")
    print("=" * 80)
    
    print("--- Felszólalásokban ---")
    cur.execute("SELECT date, speaker_name, political_group, speech_summary_hu FROM speeches WHERE speech_summary_hu LIKE ? OR speech_excerpt LIKE ?", (kw, kw))
    rows = cur.fetchall()
    for r in rows:
        print(f"[{r[0]}] {r[1]} ({r[2]}): {r[3]}")
    if not rows:
        print("Nincs találat.")

    print("\n--- Hivatalos aktusokban ---")
    cur.execute("SELECT procedure_ref, title_hu, summary_hu FROM official_acts WHERE title_hu LIKE ? OR summary_hu LIKE ?", (kw, kw))
    rows = cur.fetchall()
    for r in rows:
        print(f"[{r[0]}] {r[1]}")
    if not rows:
        print("Nincs találat.")

    print("\n--- Parlamenti kérdésekben ---")
    cur.execute("SELECT question_ref, mep_name, subject_hu FROM parliamentary_questions WHERE subject_hu LIKE ? OR answer_summary_hu LIKE ?", (kw, kw))
    rows = cur.fetchall()
    for r in rows:
        print(f"[{r[0]}] {r[1]}: {r[2]}")
    if not rows:
        print("Nincs találat.")
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="Draghi-jelentés EP Adatbázis Lekérdező")
    parser.add_argument("--stats", action="store_true", help="Statisztikai összefoglaló mutatása")
    parser.add_argument("--speeches", action="store_true", help="Felszólalások listázása")
    parser.add_argument("--acts", action="store_true", help="Hivatalos aktusok listázása")
    parser.add_argument("--questions", action="store_true", help="Parlamenti kérdések listázása")
    parser.add_argument("--hungarian", action="store_true", help="Magyar képviselők megszólalásai")
    parser.add_argument("--pillar", type=str, help="Szűrés Draghi-pillérre (pl. PILLAR_4)")
    parser.add_argument("--group", type=str, help="Szűrés frakcióra (pl. EPP, S&D, PfE, Renew)")
    parser.add_argument("--search", type=str, help="Szabadszavas keresés")

    if len(sys.argv) == 1:
        print_stats()
        return

    args = parser.parse_args()
    if args.stats:
        print_stats()
    if args.speeches or args.pillar or args.group:
        list_speeches(pillar=args.pillar, group=args.group)
    if args.acts:
        list_acts()
    if args.hungarian:
        list_hungarian()
    if args.search:
        search_database(args.search)

if __name__ == "__main__":
    main()
