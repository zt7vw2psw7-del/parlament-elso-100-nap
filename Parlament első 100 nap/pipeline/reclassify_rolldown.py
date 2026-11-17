#!/usr/bin/env python3
"""
ROLL-DOWN CAP 20 ÚJRABESOROLÁS (v1.0)
Azokat a CAP 20-as beszédeket sorolja át, amelyek kizárólag az automatikus
visszaesés (roll-down) miatt kerültek oda -- nem tartalmaznak valódi
kormányzati/alkotmányos kulcsszavakat.

A script:
1. ALTER TABLE speech_classification ADD COLUMN cap_classification_method TEXT
2. Minden CAP 20-as rekordnál megvizsgálja, valódi-e (van-e alkotmány/önkormányzat/stb. szó)
3. Ha NEM valódi -> teljes szövegen újra futtatja a CAP-szabályokat
4. Ha talál jobb kódot -> átírja primary_topic_code-ot, beállítja method='rolldown_reclassified'
5. Ha nem talál semmit -> beállítja method='rolldown_unclassified' (marad 20-as, de jelölve)
6. Valódi CAP 20-aknál method='keyword_match'
7. Kiírja az új eloszlást
"""

import sqlite3
import re
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "parlament_100nap.db")

# ---- Valódi CAP 20 kulcsszavak ----
CAP20_PATTERNS = [
    r'\balkotmány\w*', r'\balaptörvény\w*', r'\balkotmánymódosítás\w*',
    r'\bházszabály\w*', r'\bmentelmi jog\w*', r'\balkotmánybíróság\w*',
    r'\bszuverenitásvédelmi\w*',
    r'\bválasztás\w*', r'\bnépszavazás\w*', r'\bnépszámlálás\w*',
    r'\bönkormányzat\w*', r'\bpolgármester\w*', r'\bképviselő-testület\w*',
    r'\bminisztérium\w*', r'\bközigazgatás\w*', r'\bközszolgálat\w*',
    r'\bkormánytisztviselő\w*', r'\bközbeszerzés\w*',
    r'\bállami vagyon\w*', r'\bvizsgálóbizottság\w*', r'\bkampányfinanszírozás\w*',
    r'\bpártfinanszírozás\w*',
]

# ---- Összes többi CAP (NEM 20) újrabesoroláshoz ----
CAP_RULES_NO20 = [
    (9,  [r'\bállampolgárság\w*', r'\bhonosítás\w*', r'\bbevándorl\w*',
          r'\bmenekült\w*', r'\bmigráci\w*', r'\bidegenrendészet\w*']),
    (17, [r'\bmédia\b', r'\bmédiatörvény\w*', r'\bsajtó\b', r'\bsajtószabadság\w*',
          r'\brádió\w*', r'\btelevízió\w*', r'\bhírközlés\w*', r'\btávközlés\w*',
          r'\binternet\w*', r'\bkiberbiztonság\w*', r'\binformatik\w*',
          r'\bmesterséges intelligenci\w*']),
    (13, [r'\bcsalád\w*\s+támogatás\w*', r'\bcsaládtámogatás\w*',
          r'\bcsaládi pótlék\w*', r'\bgyes\b', r'\bgyed\b', r'\bcsok\b',
          r'\bgyermekvédelem\w*', r'\bgyámügy\w*', r'\bnyugdíj\w*',
          r'\bsegély\w*', r'\bszociális\w*', r'\bszegénység\w*', r'\bfogyatékosság\w*']),
    (12, [r'\bkorrupció\w*', r'\belszámoltatás\w*', r'\bpénzmosás\w*',
          r'\btitkosszolgálat\w*', r'\bbtk\b', r'\bbűncselekmény\w*',
          r'\brendőrség\w*', r'\bközbiztonság\w*', r'\bbíróság\w*',
          r'\bügyészség\w*', r'\bkúria\b', r'\bptk\b', r'\bcsődeljárás\w*',
          r'\bfelszámolás\w*']),
    (1,  [r'\bköltségvetés\w*', r'\bállamadósság\w*', r'\bállamháztartás\w*',
          r'\báfa\b', r'\bszja\b', r'\badó\b', r'\badótörvény\w*',
          r'\bjövedelemadó\w*', r'\btársasági adó\w*', r'\bkülönadó\w*',
          r'\binfláció\w*', r'\bárstop\w*', r'\bárak megállapítás\w*',
          r'\bmnb\b', r'\bnemzeti bank\w*', r'\balapkamat\w*']),
    (15, [r'\bbank\b', r'\bbankadó\w*', r'\bbankrendszer\w*', r'\bhitel\w*',
          r'\bdevizahitel\w*', r'\bértékpapír\w*', r'\btőzsde\w*', r'\bkripto\w*',
          r'\bfogyasztóvédelem\w*', r'\bgvh\b', r'\bmonopólium\w*', r'\bkkv\b',
          r'\bsport\w*', r'\bturizmus\w*', r'\bvendéglátás\w*']),
    (3,  [r'\begészségügy\w*', r'\bkórház\w*', r'\borvos\w*', r'\bápoló\w*',
          r'\bbetegellátás\w*', r'\bmentő\w*', r'\bgyógyszer\w*',
          r'\bjárvány\w*', r'\begészségbiztosítás\w*', r'\boep\b', r'\bneak\b']),
    (4,  [r'\bmezőgazdaság\w*', r'\bagrár\w*', r'\bgazda\b', r'\bgazdák\w*',
          r'\bgabona\w*', r'\bbúza\b', r'\bállattenyésztés\w*', r'\bnövénytermesztés\w*']),
    (5,  [r'\bmunkaügy\w*', r'\bmunkabér\w*', r'\bminimálbér\w*', r'\bszakszervezet\w*',
          r'\bfoglalkoztatás\w*', r'\bmunkanélküliség\w*', r'\begyszerűsített foglalkoztatás\w*',
          r'\bmunkaszüneti nap\w*', r'\bmunkaidő\w*']),
    (6,  [r'\boktatás\w*', r'\bközoktatás\w*', r'\bköznevelés\w*', r'\biskola\w*',
          r'\bpedagógus\w*', r'\btanár\w*', r'\btankönyv\w*', r'\bszakképzés\w*',
          r'\begyetem\w*', r'\bfelsőoktatás\w*', r'\bdiákhitel\w*', r'\bmta\b']),
    (8,  [r'\benergia\w*', r'\bvillamos energia\w*', r'\bföldgáz\w*',
          r'\bgázellátás\w*', r'\bpaks\b', r'\batomenergia\w*', r'\bkőolaj\w*']),
    (10, [r'\bközlekedés\w*', r'\bvasút\w*', r'\bmáv\b', r'\bautópálya\w*',
          r'\bközút\w*', r'\btömegközlekedés\w*', r'\bparkolás\w*']),
    (19, [r'\beurópai unió\w*', r'\beu\b', r'\bbrüsszel\b', r'\buniós forrás\w*',
          r'\brrf\b', r'\bhelyreállítási terv\w*', r'\bkülpolitika\w*',
          r'\bdiplomácia\w*', r'\bnagykövet\w*', r'\bukrajna\w*',
          r'\boroszország\w*', r'\bszlovák\w*', r'\begyesült államok\w*']),
    (16, [r'\bhonvédelem\w*', r'\bhonvédség\w*', r'\bkatona\w*', r'\bnato\b', r'\bhaderő\w*']),
    (7,  [r'\bkörnyezetvédelem\w*', r'\bhulladék\w*', r'\bújrahasznosítás\w*',
          r'\bakku\w*', r'\bakkumulátorgyár\w*', r'\bklíma\w*']),
    (14, [r'\blakásügy\w*', r'\blakhatás\w*', r'\bbérlakás\w*',
          r'\botthonteremtés\w*', r'\bvidékfejlesztés\w*', r'\blakásfoglal\w*']),
    (21, [r'\bállami föld\w*', r'\btermőföld\w*', r'\bnemzeti földalap\w*',
          r'\bvízgazdálkodás\w*', r'\bárvíz\w*', r'\bbalaton\b']),
    (23, [r'\bkultúra\w*', r'\bszínház\w*', r'\bmúzeum\w*', r'\bkönyvtár\w*',
          r'\bmûvészet\w*', r'\bnka\b', r'\bkulturális örökség\w*']),
    (2,  [r'\bemberi jog\w*', r'\broma\b', r'\bromák\w*', r'\bkisebbség\w*',
          r'\bnemzetiség\w*', r'\bdiszkrimináció\w*', r'\begyenlő bánásmód\w*',
          r'\besélyegyenlőség\w*']),
    (18, [r'\bkülkereskedelem\w*', r'\bexport\w*', r'\bimport\w*', r'\bvám\b', r'\bvámunió\w*']),
]

CAP_NAMES = {
    1: "Makrogazdaság", 2: "Polgári jogok", 3: "Egészségügy", 4: "Mezőgazdaság",
    5: "Munkaügy", 6: "Oktatás", 7: "Környezetvédelem", 8: "Energiaügy",
    9: "Bevándorlás", 10: "Közlekedés", 12: "Jog/közbiztonság",
    13: "Szociálpolitika", 14: "Lakásügy", 15: "Belkereskedelem/pénzügy",
    16: "Honvédelem", 17: "Technológia/média", 18: "Külkereskedelem",
    19: "Külügyek", 20: "Kormányzati működés",
    21: "Földek/vízgazdálkodás", 23: "Kultúra"
}


def is_real_cap20(text):
    return any(re.search(p, text, re.IGNORECASE) for p in CAP20_PATTERNS)


def find_best_cap(text):
    for cap_code, patterns in CAP_RULES_NO20:
        if any(re.search(p, text, re.IGNORECASE) for p in patterns):
            return cap_code
    return None


def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. Új oszlop hozzáadása (ha még nincs)
    try:
        c.execute("ALTER TABLE speech_classification ADD COLUMN cap_classification_method TEXT")
        conn.commit()
        print("✅ cap_classification_method oszlop létrehozva.")
    except sqlite3.OperationalError:
        print("ℹ️  cap_classification_method oszlop már létezik.")

    # 2. Lekérjük az összes CAP 20-as, >=200 szavas beszédet
    c.execute("""
        SELECT s.id, s.agenda_item, s.full_text, s.period_id
        FROM speech s
        JOIN speech_classification sc ON s.id = sc.speech_id
        WHERE sc.primary_topic_code = '20'
    """)
    rows = c.fetchall()
    print(f"\n📊 Összes CAP 20-as felszólalás: {len(rows)}")

    stats = {
        "real_cap20": 0,
        "rolldown_reclassified": 0,
        "rolldown_unclassified": 0,
    }
    new_cap_counts = {}
    updates = []

    for sid, agenda, text, period in rows:
        full_text = f"{agenda or ''} {text or ''}"
        short_text = f"{agenda or ''} {(text or '')[:600]}"

        if is_real_cap20(short_text):
            # Valódi CAP 20
            updates.append(("keyword_match", "20", sid))
            stats["real_cap20"] += 1
        else:
            # Roll-down -> próbáljuk átsorolni teljes szöveggel
            new_cap = find_best_cap(full_text)
            if new_cap:
                updates.append(("rolldown_reclassified", str(new_cap), sid))
                new_cap_counts[new_cap] = new_cap_counts.get(new_cap, 0) + 1
                stats["rolldown_reclassified"] += 1
            else:
                # Marad 20, de jelölve mint nem valódi
                updates.append(("rolldown_unclassified", "20", sid))
                stats["rolldown_unclassified"] += 1

    # 3. Batch update
    c.executemany("""
        UPDATE speech_classification
        SET cap_classification_method = ?, primary_topic_code = ?
        WHERE speech_id = ?
    """, updates)
    conn.commit()

    print(f"\n✅ Frissítve {len(updates)} rekord.")
    print(f"\n📋 Eredmény:")
    print(f"   Valódi CAP 20 (keyword_match):        {stats['real_cap20']:4d} db")
    print(f"   Roll-down -> átsorolva:                {stats['rolldown_reclassified']:4d} db")
    print(f"   Roll-down -> marad 20 (jelölve):       {stats['rolldown_unclassified']:4d} db")

    print(f"\n🔄 Roll-down átsorolások megoszlása:")
    for cap, cnt in sorted(new_cap_counts.items(), key=lambda x: -x[1]):
        print(f"   CAP {cap:2d} ({CAP_NAMES.get(cap,'?'):30s}): {cnt:3d} db")

    # 4. Frissített teljes CAP eloszlás (>=200 szó)
    print(f"\n📊 ÚJ teljes CAP eloszlás (>=200 szavas felszólalások):")
    c.execute("""
        SELECT sc.primary_topic_code, COUNT(DISTINCT s.id) as db,
               SUM(CASE WHEN s.period_id='2010' THEN 1 ELSE 0 END),
               SUM(CASE WHEN s.period_id='2026' THEN 1 ELSE 0 END)
        FROM speech_classification sc
        JOIN speech s ON sc.speech_id = s.id
        WHERE s.word_count >= 200
        GROUP BY sc.primary_topic_code
        ORDER BY db DESC
    """)
    rows2 = c.fetchall()
    total = sum(r[1] for r in rows2)
    print(f"   Összesen: {total}")
    print(f"   {'CAP':5} {'Témakör':30} {'db':>5} {'%':>6} {'2010':>5} {'2026':>5}")
    print(f"   {'-'*60}")
    for r in rows2:
        cap = int(r[0]) if r[0] else 0
        name = CAP_NAMES.get(cap, "?")
        pct = r[1]/total*100
        print(f"   CAP {cap:2d} {name:30} {r[1]:5d} {pct:6.1f}% {r[2]:5d} {r[3]:5d}")

    conn.close()
    print("\n✅ Kész! Adatbázis mentve.")


if __name__ == "__main__":
    main()
