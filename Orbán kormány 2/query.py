#!/usr/bin/env python3
"""
Kereső és lekérdező eszköz a Második Orbán-kormány kormányüléseinek adatbázisához.
Használat:
    python3 query.py list                # Összes kormányülés listázása
    python3 query.py search <kulcsszó>   # Keresés témákban, döntésekben (pl. nyugdíj, adó, vörösiszap)
    python3 query.py get <ID vagy Dátum> # Egy adott kormányülés részletes adatlapja
    python3 query.py stats               # Statisztikai összesítő
    python3 query.py ministers           # Kormánytagok listája (2010-2011)
"""

import sqlite3
import sys
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "kormanyulesek_2010.db")

def get_connection():
    if not os.path.exists(DB_FILE):
        print(f"Hiba: Az adatbázis nem található ({DB_FILE}). Futtasd előbb az 'python3 init_database.py' parancsot!")
        sys.exit(1)
    return sqlite3.connect(DB_FILE)

def list_meetings():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, datum, iktatoszam, idopont_tipus, cim FROM kormanyulesek ORDER BY datum ASC")
    rows = c.fetchall()
    conn.close()

    print("\n" + "=" * 95)
    print(f"{'ID':<4} | {'Dátum':<12} | {'Iktatószám':<16} | {'Típus':<15} | {'Cím'}")
    print("-" * 95)
    for r in rows:
        print(f"{r[0]:<4} | {r[1]:<12} | {r[2]:<16} | {r[3]:<15} | {r[4]}")
    print("=" * 95)
    print(f"Összesen: {len(rows)} közzétett kormányülés (kormany.hu)\n")

def search_meetings(keyword):
    conn = get_connection()
    c = conn.cursor()
    query = """
    SELECT id, datum, iktatoszam, kiemelt_temak, dontesek_es_osszefoglalo, pdf_url
    FROM kormanyulesek
    WHERE kiemelt_temak LIKE ? OR dontesek_es_osszefoglalo LIKE ? OR cim LIKE ? OR iktatoszam LIKE ?
    ORDER BY datum ASC
    """
    pattern = f"%{keyword}%"
    c.execute(query, (pattern, pattern, pattern, pattern))
    rows = c.fetchall()
    conn.close()

    print(f"\nTalálatok a(z) '{keyword}' kulcsszóra ({len(rows)} találat):")
    print("=" * 95)
    if not rows:
        print("Nincs találat a megadott kifejezésre.")
    for r in rows:
        print(f"\n[#{r[0]}] Dátum: {r[1]} | Iktatószám: {r[2]}")
        print(f"  Kiemelt témák: {r[3]}")
        print(f"  Összefoglaló:   {r[4]}")
        print(f"  Hivatalos PDF:  {r[5]}")
        print("-" * 95)
    print()

def get_meeting_details(identifier):
    conn = get_connection()
    c = conn.cursor()
    if identifier.isdigit():
        c.execute("SELECT * FROM kormanyulesek WHERE id = ?", (int(identifier),))
    else:
        c.execute("SELECT * FROM kormanyulesek WHERE datum LIKE ? OR datum_szoveges LIKE ?", (f"%{identifier}%", f"%{identifier}%"))
    row = c.fetchone()
    conn.close()

    if not row:
        print(f"Nincs találat erre az azonosítóra: {identifier}")
        return

    print("\n" + "=" * 80)
    print(f"KORMÁNYÜLÉS ADATLAP: #{row[0]} - {row[2]} ({row[4]})")
    print("=" * 80)
    print(f"Dátum (ISO):         {row[1]}")
    print(f"Cím:                 {row[5]}")
    print(f"Ülés száma:          {row[3]}. kormányülés")
    print(f"Iktatószám:          {row[4]}")
    print(f"Ülés jellege:        {row[7]}")
    print(f"Dokumentum terjedelme: {row[8]} oldal")
    print(f"Státusz:             {row[11]}")
    print(f"Hivatalos PDF link:  {row[6]}")
    print("-" * 80)
    print("KIEMELT TÉMÁK:")
    print(f"  {row[9]}")
    print("-" * 80)
    print("DÖNTÉSEK ÉS ÖSSZEFOGLALÓ:")
    print(f"  {row[10]}")
    print("=" * 80 + "\n")

def show_stats():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM kormanyulesek")
    total = c.fetchone()[0]

    c.execute("SELECT strftime('%Y-%m', datum) as honap, COUNT(*) FROM kormanyulesek GROUP BY honap ORDER BY honap")
    by_month = c.fetchall()

    c.execute("SELECT idopont_tipus, COUNT(*) FROM kormanyulesek GROUP BY idopont_tipus")
    by_type = c.fetchall()
    conn.close()

    print("\n" + "=" * 60)
    print("MÁSODIK ORBÁN-KORMÁNY (2010) - KORMÁNYÜLÉSI STATISZTIKÁK")
    print("=" * 60)
    print(f"Összes közzétett kormányülés: {total} db (2010. május 31. - dec. 22.)")
    print("\nHavi bontás:")
    for m in by_month:
        bar = "█" * (m[1] * 3)
        print(f"  {m[0]}: {m[1]:>2} ülés  {bar}")
    print("\nÜlések jellege szerint:")
    for t in by_type:
        print(f"  - {t[0]}: {t[1]} db")
    print("=" * 60 + "\n")

def list_ministers():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT nev, pozicio, tarca, hivatal_kezdete, hivatal_vege FROM kormanytagok")
    rows = c.fetchall()
    conn.close()

    print("\n" + "=" * 90)
    print("A MÁSODIK ORBÁN-KORMÁNY TAGJAI (2010-2011)")
    print("=" * 90)
    for r in rows:
        print(f"{r[0]:<20} | {r[1]:<35} | {r[2]}")
    print("=" * 90 + "\n")

def print_help():
    print(__doc__)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)

    cmd = sys.argv[1].lower()
    if cmd == "list":
        list_meetings()
    elif cmd == "search":
        if len(sys.argv) < 3:
            print("Hiba: Add meg a keresendő kulcsszót! Például: python3 query.py search nyugdíj")
        else:
            search_meetings(" ".join(sys.argv[2:]))
    elif cmd == "get":
        if len(sys.argv) < 3:
            print("Hiba: Add meg az ülés azonosítóját vagy dátumát! Például: python3 query.py get 1")
        else:
            get_meeting_details(sys.argv[2])
    elif cmd == "stats":
        show_stats()
    elif cmd == "ministers":
        list_ministers()
    else:
        print_help()
