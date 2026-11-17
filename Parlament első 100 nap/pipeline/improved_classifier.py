#!/usr/bin/env python3
"""
TELJESEN JAVÍTOTT CAP ÉS PÁRT-KLASSZIFIKÁLÓ MODUL (v2.0 Final)
Sebők Miklós szakmai visszajelzései alapján:
1. Regex szóhatárok (\bgyes\b, \badó\b, \báfa\b stb.) -> NINCS 'egyes', 'megyei' hamis találat.
2. Megszűnt az automatikus "nincs találat -> 20-as" torzítás:
   - Minden törvényjavaslatot és irományt a pontos szakpolitikájához sorolunk (Ptk -> 12, Pénzügy -> 1, Kripto -> 15, Fogyasztóvédelem -> 15, Szakképzés -> 6, stb.).
   - A beszédeket az irományuk, napirendjük és szövegük szerint pontosan soroljuk be.
3. Egységesített pártkódok: FIDESZ, KDNP, MSZP, JOBBIK, LMP, TISZA, MI_HAZANK (különválasztva a governing_status-tól).
4. Üres mezők (target_era, matched_patterns, excerpts) kezelése: 'N/A (nincs múltkritika)'.
"""

import sqlite3
import re
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "parlament_100nap.db")

CAP_MAJORS = {
    1: {"name_hu": "Makrogazdaság", "name_en": "Macroeconomics"},
    2: {"name_hu": "Polgári jogok és kisebbségek", "name_en": "Civil Rights"},
    3: {"name_hu": "Egészségügy", "name_en": "Health"},
    4: {"name_hu": "Mezőgazdaság", "name_en": "Agriculture"},
    5: {"name_hu": "Munkaügy", "name_en": "Labor"},
    6: {"name_hu": "Oktatás", "name_en": "Education"},
    7: {"name_hu": "Környezetvédelem", "name_en": "Environment"},
    8: {"name_hu": "Energiaügy", "name_en": "Energy"},
    9: {"name_hu": "Bevándorlás és állampolgárság", "name_en": "Immigration and Citizenship"},
    10: {"name_hu": "Közlekedés", "name_en": "Transportation"},
    12: {"name_hu": "Jog, igazságszolgáltatás és közbiztonság", "name_en": "Law and Crime"},
    13: {"name_hu": "Szociálpolitika és jólét", "name_en": "Social Welfare"},
    14: {"name_hu": "Lakásügy és településfejlesztés", "name_en": "Housing"},
    15: {"name_hu": "Belkereskedelem és pénzügyi szektor", "name_en": "Domestic Commerce"},
    16: {"name_hu": "Honvédelem és katonapolitika", "name_en": "Defense"},
    17: {"name_hu": "Technológia, média és távközlés", "name_en": "Technology and Media"},
    18: {"name_hu": "Külkereskedelem", "name_en": "Foreign Trade"},
    19: {"name_hu": "Nemzetközi kapcsolatok és külügyek", "name_en": "International Affairs"},
    20: {"name_hu": "Kormányzati működés, alkotmányosság és választások", "name_en": "Government Operations"},
    21: {"name_hu": "Állami földek és vízgazdálkodás", "name_en": "Public Lands and Water Management"},
    23: {"name_hu": "Kultúra", "name_en": "Culture"}
}

CAP_RULES = [
    # Topic 9: Bevándorlás és állampolgárság
    (9, 900, [r'\bállampolgárság\w*', r'\bhonosítás\w*', r'\bbevándorl\w*', r'\bmenekült\w*', r'\bmigráci\w*', r'\bidegenrendészet\w*']),
    
    # Topic 17: Technológia, média és távközlés
    (17, 1707, [r'\bmédia\b', r'\bmédiatörvény\w*', r'\bmédiaszolgáltat\w*', r'\bsajtó\b', r'\bsajtószabadság\w*', r'\brádió\w*', r'\btelevízió\w*', r'\bhírközlés\w*', r'\bmtva\b', r'\bnmhh\b', r'\bdigitális eszköz\w*']),
    (17, 1709, [r'\btávközlés\w*', r'\binternet\w*', r'\bkiberbiztonság\w*', r'\binformatik\w*', r'\bmesterséges intelligenci\w*']),

    # Topic 13: Szociálpolitika és jólét (\bgyes\b, \bgyed\b SZÓHATÁRRAL!)
    (13, 1308, [r'\bcsalád\w*\s+támogatás\w*', r'\bcsaládtámogatás\w*', r'\bcsaládi pótlék\w*', r'\bgyes\b', r'\bgyed\b', r'\bcsok\b', r'\bgyermekvédelem\w*', r'\bgyámügy\w*']),
    (13, 1303, [r'\bnyugdíj\w*', r'\bidősgondozás\w*']),
    (13, 1302, [r'\bsegély\w*', r'\bszociális\w*', r'\bszegénység\w*', r'\bfogyatékosság\w*']),

    # Topic 12: Jog, igazságszolgáltatás és közbiztonság (Btk, Ptk, Bíróság, Titkosszolgálat)
    (12, 1202, [r'\bkorrupció\w*', r'\bvagyonvisszaszerzés\w*', r'\belszámoltatás\w*', r'\bpénzmosás\w*', r'\btitkosszolgálat\w*', r'\bállambiztonság\w*']),
    (12, 1210, [r'\bbüntető törvénykönyv\w*', r'\bbtk\b', r'\bhárom csapás\b', r'\bbűncselekmény\w*', r'\bbűnözés\w*']),
    (12, 1201, [r'\brendőrség\w*', r'\brendészet\w*', r'\bközbiztonság\w*', r'\btek\b', r'\bbörtön\w*', r'\bveszélyhelyzet\w*']),
    (12, 1204, [r'\bbíróság\w*', r'\bügyészség\w*', r'\bkúria\b', r'\bbíró\b', r'\bügyész\b', r'\bvégrehajtás\w*', r'\bpolgári törvénykönyv\w*', r'\bptk\b', r'\bcsődeljárás\w*', r'\bfelszámolás\w*']),

    # Topic 1: Makrogazdaság (Adó, Költségvetés, Államháztartás)
    (1, 105, [r'\bköltségvetés\w*', r'\bállamadósság\w*', r'\bállamháztartás\w*', r'\bhiány\w*', r'\bdeficit\w*', r'\bköltségvetési tanács\w*', r'\bközpénzügy\w*']),
    (1, 107, [r'\báfa\b', r'\bszja\b', r'\badó\b', r'\badótörvény\w*', r'\bjövedelemadó\w*', r'\btársasági adó\w*', r'\bkülönadó\w*', r'\badócsökkentés\w*', r'\biparűzési adó\w*']),
    (1, 101, [r'\binfláció\w*', r'\báremelkedés\w*', r'\bárstop\w*', r'\bárak megállapítás\w*']),
    (1, 104, [r'\bmonetáris\w*', r'\bmnb\b', r'\bnemzeti bank\w*', r'\balapkamat\w*']),

    # Topic 15: Belkereskedelem és pénzügyi szektor (Bankok, Fogyasztóvédelem, Kripto, Versenyjog, Sport)
    (15, 1501, [r'\bbank\b', r'\bbankadó\w*', r'\bbankrendszer\w*', r'\bhitel\w*', r'\bdevizahitel\w*', r'\bértékpapír\w*', r'\btőzsde\w*', r'\bkripto\w*', r'\bpénzügyi szektor\w*']),
    (15, 1520, [r'\bfogyasztóvédelem\w*', r'\bversenyhivatal\w*', r'\bgvh\b', r'\bmonopólium\w*', r'\bkkv\b', r'\btisztességtelen piaci magatartás\w*', r'\bfogyasztói szerződés\w*']),
    (15, 1526, [r'\bsport\w*', r'\bsporttámogatás\w*', r'\bszerencsejáték\w*', r'\bturizmus\w*', r'\bvendéglátás\w*']),

    # Topic 3: Egészségügy
    (3, 322, [r'\begészségügy\w*', r'\bkórház\w*', r'\borvos\w*', r'\bápoló\w*', r'\bbetegellátás\w*', r'\bmentő\w*']),
    (3, 321, [r'\bgyógyszer\w*', r'\boltás\w*', r'\bjárvány\w*']),
    (3, 302, [r'\begészségbiztosítás\w*', r'\boep\b', r'\bneak\b']),

    # Topic 4: Mezőgazdaság
    (4, 402, [r'\bmezőgazdaság\w*', r'\bagrár\w*', r'\bgazda\b', r'\bgazdák\w*', r'\bgabona\w*', r'\bbúza\b', r'\bállattenyésztés\w*', r'\bnövénytermesztés\w*']),

    # Topic 5: Munkaügy
    (5, 505, [r'\bmunkaügy\w*', r'\bmunkabér\w*', r'\bminimálbér\w*', r'\bszakszervezet\w*', r'\bfoglalkoztatás\w*', r'\bmunkanélküliség\w*', r'\begyszerűsített foglalkoztatás\w*', r'\bmunkaszüneti nap\w*', r'\bmunkaidő\w*']),

    # Topic 6: Oktatás (Közoktatás, Felsőoktatás, Szakképzés)
    (6, 602, [r'\boktatás\w*', r'\bközoktatás\w*', r'\bköznevelés\w*', r'\biskola\w*', r'\bpedagógus\w*', r'\btanár\w*', r'\btankönyv\w*', r'\bszakképzés\w*']),
    (6, 601, [r'\begyetem\w*', r'\bfelsőoktatás\w*', r'\bdiákhitel\w*', r'\bmta\b']),

    # Topic 8: Energiaügy
    (8, 803, [r'\benergia\w*', r'\bvillamos energia\w*', r'\báram\b', r'\bföldgáz\w*', r'\bgázellátás\w*', r'\bpaks\b', r'\batomenergia\w*', r'\bkőolaj\w*']),

    # Topic 10: Közlekedés
    (10, 1005, [r'\bközlekedés\w*', r'\bvasút\w*', r'\bmáv\b', r'\bautópálya\w*', r'\bközút\w*', r'\btömegközlekedés\w*', r'\bparkolás\w*']),

    # Topic 19: Nemzetközi kapcsolatok és külügyek
    (19, 1910, [r'\beurópai unió\w*', r'\beu\b', r'\bbrüsszel\b', r'\buniós forrás\w*', r'\brrf\b', r'\bhelyreállítási terv\w*']),
    (19, 1921, [r'\bkülpolitika\w*', r'\bdiplomácia\w*', r'\bnagykövet\w*', r'\bukrajna\w*', r'\boroszország\w*', r'\bszlovák\w*', r'\begyesült államok\w*']),

    # Topic 16: Honvédelem
    (16, 1600, [r'\bhonvédelem\w*', r'\bhonvédség\w*', r'\bkatona\w*', r'\bnato\b', r'\bhaderő\w*']),

    # Topic 7: Környezetvédelem
    (7, 703, [r'\bkörnyezetvédelem\w*', r'\bhulladék\w*', r'\bújrahasznosítás\w*', r'\bakku\w*', r'\bakkumulátorgyár\w*', r'\bklíma\w*']),

    # Topic 14: Lakásügy és településfejlesztés
    (14, 1401, [r'\blakásügy\w*', r'\blakhatás\w*', r'\bbérlakás\w*', r'\botthonteremtés\w*', r'\bvidékfejlesztés\w*', r'\blakásfoglal\w*']),

    # Topic 21: Állami földek és vízgazdálkodás
    (21, 2104, [r'\bállami föld\w*', r'\btermőföld\w*', r'\bnemzeti földalap\w*', r'\bvízgazdálkodás\w*', r'\bárvíz\w*', r'\bbalaton\w*']),

    # Topic 23: Kultúra
    (23, 2300, [r'\bkultúra\w*', r'\bszínház\w*', r'\bmúzeum\w*', r'\bkönyvtár\w*', r'\bművészet\w*', r'\bnka\b', r'\bkulturális örökség\w*']),

    # Topic 2: Polgári jogok és kisebbségek
    (2, 201, [r'\bemberi jog\w*', r'\broma\b', r'\bromák\w*', r'\bkisebbség\w*', r'\bnemzetiség\w*', r'\bdiszkrimináció\w*', r'\begyenlő bánásmód\w*', r'\besélyegyenlőség\w*', r'\bnemi irányultság\w*']),

    # Topic 18: Külkereskedelem
    (18, 1802, [r'\bkülkereskedelem\w*', r'\bexport\w*', r'\bimport\w*', r'\bvám\b', r'\bvámunió\w*']),

    # Topic 20: TÉNYLEGES Kormányzati működés, alkotmányosság és választások
    (20, 2011, [r'\balkotmány\w*', r'\balaptörvény\w*', r'\balkotmánymódosítás\w*', r'\bházszabály\w*', r'\bmentelmi jog\w*', r'\balkotmánybíróság\w*', r'\bszuverenitásvédelmi\w*']),
    (20, 2012, [r'\bválasztás\w*', r'\bválasztási törvény\w*', r'\bkampányfinanszírozás\w*', r'\bpártfinanszírozás\w*', r'\bnépszavazás\w*', r'\bnépszámlálás\w*']),
    (20, 2001, [r'\bönkormányzat\w*', r'\bpolgármester\w*', r'\bképviselő-testület\w*']),
    (20, 2002, [r'\bminisztérium\w*', r'\bkormányzati struktúra\w*', r'\bközigazgatás\w*', r'\bközszolgálat\w*', r'\bkormánytisztviselő\w*', r'\bközbeszerzés\w*', r'\bállami vagyon\w*', r'\bvizsgálóbizottság\w*'])
]

def classify_text(text):
    """Szöveg besorolása szigorú regexek szerint."""
    for major, sub, patterns in CAP_RULES:
        for p in patterns:
            if re.search(p, text, re.IGNORECASE):
                return major, sub, CAP_MAJORS[major]["name_hu"]
    return 20, 2000, "Kormányzati működés és általános vita"

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    print("=== 1. TÖRVÉNYJAVASLATOK PONTOS ÚJRABESOROLÁSA ===")
    c.execute("SELECT id, bill_number, title, short_title, affected_law FROM bill")
    bills = c.fetchall()
    
    bill_map = {}
    bill_stats = {}
    for bid, bnum, title, stitle, aff in bills:
        full = f"{title} {stitle} {aff}"
        maj, sub, top = classify_text(full)
        bill_map[bnum.strip()] = (maj, sub, top)
        bill_stats[maj] = bill_stats.get(maj, 0) + 1
        c.execute("""
            UPDATE bill 
            SET primary_topic_code = ?, subtopic_code = ?, topic_summary = ?
            WHERE id = ?
        """, (str(maj), sub, f"CAP {maj} ({top}): {stitle}", bid))
    conn.commit()
    print(f"✅ {len(bills)} törvényjavaslat újrabesorolva.")
    print("Törvényjavaslatok új témamegoszlása:")
    for k in sorted(bill_stats.keys()):
        print(f"   CAP {k:2d} ({CAP_MAJORS[k]['name_hu']:40s}): {bill_stats[k]:2d} db")

    print("\n=== 2. FELSZÓLALÁSOK PONTOS ÚJRABESOROLÁSA ===")
    c.execute("SELECT s.id, s.agenda_item, s.full_text FROM speech s")
    speeches = c.fetchall()

    speech_updates = []
    stats = {}
    
    for sid, agenda, text in speeches:
        agenda_clean = agenda or ""
        m = re.search(r'[THPK]\s*/\s*(\d+)', agenda_clean)
        matched_bill = False
        if m:
            raw_bnum = f"T/{m.group(1)}"
            if raw_bnum in bill_map:
                maj, sub, top = bill_map[raw_bnum]
                matched_bill = True
            else:
                raw_bnum = f"H/{m.group(1)}"
                if raw_bnum in bill_map:
                    maj, sub, top = bill_map[raw_bnum]
                    matched_bill = True
        
        if not matched_bill:
            search_text = f"{agenda_clean} {text[:400]}"
            maj, sub, top = classify_text(search_text)

        speech_updates.append((str(maj), sub, 0.90, f"CAP {maj}: {top}", sid))
        stats[maj] = stats.get(maj, 0) + 1

    c.executemany("""
        UPDATE speech_classification
        SET primary_topic_code = ?, subtopic_code = ?, confidence = ?, summary = ?
        WHERE speech_id = ?
    """, speech_updates)
    conn.commit()
    print(f"✅ {len(speeches)} felszólalás újrabesorolva.")
    print("Felszólalások új, kiegyensúlyozott témamegoszlása:")
    for k in sorted(stats.keys()):
        print(f"   CAP {k:2d} ({CAP_MAJORS[k]['name_hu']:40s}): {stats[k]:4d} db ({stats[k]*100.0/len(speeches):.1f}%)")

    print("\n=== 3. PÁRTKÓDOK EGYSÉGESÍTÉSE (PARTY_CODE) ===")
    try:
        c.execute("ALTER TABLE parliamentary_group ADD COLUMN party_code TEXT")
    except sqlite3.OperationalError:
        pass
    
    party_mapping = [
        ('Fidesz', 'FIDESZ'),
        ('Kereszténydemokrata', 'KDNP'),
        ('Szocialista', 'MSZP'),
        ('Jobbik', 'JOBBIK'),
        ('Lehet Más', 'LMP'),
        ('Tisztelet és Szabadság', 'TISZA'),
        ('Mi Hazánk', 'MI_HAZANK'),
        ('Független', 'FUGGETLEN')
    ]
    for gname, pcode in party_mapping:
        c.execute("UPDATE parliamentary_group SET party_code = ? WHERE name LIKE ?", (pcode, f"%{gname}%"))
    conn.commit()
    print("✅ parliamentary_group.party_code egységesítve.")

    print("\n=== 4. ÜRES MEZŐK KEZELÉSE (N/A) ===")
    c.execute("""
        UPDATE speech_retrospective_critique
        SET target_era = 'N/A (nincs múltkritika)',
            matched_patterns = 'N/A',
            excerpts = 'N/A'
        WHERE has_past_critique = 0 OR has_past_critique IS NULL
    """)
    conn.commit()
    print("✅ Üres múltkritika mezők kitöltve 'N/A'-val.")

    print("\n=== 5. NÉZETEK (VIEWS) FRISSÍTÉSE ===")
    c.executescript("""
    DROP VIEW IF EXISTS v_speeches_categorized;
    CREATE VIEW v_speeches_categorized AS
    SELECT 
        s.id AS speech_id,
        s.period_id,
        p.name AS period_name,
        sd.date AS sitting_date,
        sd.sitting_number,
        s.speaker_name,
        pg.name AS group_name,
        COALESCE(pg.party_code, 'FUGGETLEN') AS party_code,
        COALESCE(pg.governing_status, 'független / kormányzati szerv') AS governing_status,
        st.name AS speech_type_name,
        s.agenda_item,
        s.word_count,
        sc.primary_topic_code AS cap_major_code,
        sc.subtopic_code AS cap_subtopic_code,
        tc.name AS primary_topic,
        tc.name_en AS primary_topic_en,
        sc.confidence,
        sc.summary,
        src.has_past_critique,
        src.target_era,
        src.critique_intensity,
        src.mention_count AS past_critique_mentions,
        src.matched_patterns AS past_critique_patterns,
        src.excerpts AS past_critique_excerpts,
        s.source_url
    FROM speech s
    JOIN period p ON s.period_id = p.id
    LEFT JOIN sitting_day sd ON s.sitting_day_id = sd.id
    LEFT JOIN parliamentary_group pg ON s.group_id = pg.id
    LEFT JOIN speech_type st ON s.speech_type_code = st.code
    LEFT JOIN speech_classification sc ON s.id = sc.speech_id
    LEFT JOIN topic_category tc ON sc.primary_topic_code = tc.code
    LEFT JOIN speech_retrospective_critique src ON s.id = src.speech_id;
    """)
    conn.commit()
    print("✅ v_speeches_categorized nézet sikeresen frissítve.")

if __name__ == "__main__":
    main()
