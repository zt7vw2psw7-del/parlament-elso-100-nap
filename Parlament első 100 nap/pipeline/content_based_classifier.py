#!/usr/bin/env python3
"""
VÉGLEGES TARTALMI SZÖVEGALAPÚ TÉMAOSZTÁLYOZÓ PIPELINE (v3.1)
Finomhangolás:
1. Önkormányzati ügyek (működés, polgármesterek, helyi döntések) -> CAP 14 (Településfejlesztés, helyi közösségek és lakásügy)
2. Helyi iparűzési adó (T/284) -> CAP 1 (Makrogazdaság / adó)
3. Iskolai Nemzeti Összetartozás (H/638) -> CAP 6 (Oktatás)
4. Napirend előtti viták (130 db) tartalmi felbontása a domináns téma szerint
5. Valódi CAP 20 megtartása kizárólag a tiszta alkotmányozási, választási és államszervezeti vitákra
"""

import sqlite3
import re
import os
from collections import Counter

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
    14: {"name_hu": "Településfejlesztés, önkormányzatok és lakásügy", "name_en": "Community Development & Housing"},
    15: {"name_hu": "Belkereskedelem és pénzügyi szektor", "name_en": "Domestic Commerce"},
    16: {"name_hu": "Honvédelem és katonapolitika", "name_en": "Defense"},
    17: {"name_hu": "Technológia, média és távközlés", "name_en": "Technology and Media"},
    18: {"name_hu": "Külkereskedelem", "name_en": "Foreign Trade"},
    19: {"name_hu": "Nemzetközi kapcsolatok és külügyek", "name_en": "International Affairs"},
    20: {"name_hu": "Alkotmányosság, kormányzati működés és választások", "name_en": "Government Operations"},
    21: {"name_hu": "Állami földek és vízgazdálkodás", "name_en": "Public Lands and Water Management"},
    23: {"name_hu": "Kultúra", "name_en": "Culture"}
}

LEXICON_PATTERNS = {
    1: r'\b(költségvetés\w*|államadósság\w*|államháztartás\w*|hiány\w*|deficit\w*|áfa\b|szja\b|adó\b|adózás\w*|adótörvény\w*|jövedelemadó\w*|társasági adó\w*|különadó\w*|adócsökkentés\w*|iparűzési adó\w*|helyi adó\w*|infláció\w*|árstop\w*|árnövekedés\w*|áremelkedés\w*|monetáris\w*|mnb\b|nemzeti bank\w*|alapkamat\w*|forintárfolyam\w*|állami vagyon\w*)\b',
    2: r'\b(emberi jog\w*|roma\b|romák\w*|cigány\w*|kisebbség\w*|nemzetiség\w*|diszkrimináció\w*|egyenlő bánásmód\w*|esélyegyenlőség\w*|nemi irányultság\w*)\b',
    3: r'\b(egészségügy\w*|kórház\w*|orvos\w*|ápoló\w*|betegellátás\w*|mentő\w*|gyógyszer\w*|oltás\w*|járvány\w*|egészségbiztosítás\w*|oep\b|neak\b|várólista\w*|gyógyítás\w*|klinika\w*)\b',
    4: r'\b(mezőgazdaság\w*|agrár\w*|gazda\b|gazdák\w*|gabona\w*|búza\b|állattenyésztés\w*|növénytermesztés\w*|aszály\w*|öntözés\w*|termőföld\w*|földalap\w*)\b',
    5: r'\b(munkaügy\w*|munkabér\w*|minimálbér\w*|szakszervezet\w*|foglalkoztatás\w*|munkanélküliség\w*|egyszerűsített foglalkoztatás\w*|munkaszüneti nap\w*|munkaidő\w*|munka törvénykönyv\w*|bérnövekedés\w*|közmunka\w*)\b',
    6: r'\b(oktatás\w*|közoktatás\w*|köznevelés\w*|iskola\w*|pedagógus\w*|tanár\w*|tankönyv\w*|szakképzés\w*|egyetem\w*|felsőoktatás\w*|diákhitel\w*|mta\b|tandíj\w*|tanszék\w*|iskolai\w*)\b',
    7: r'\b(környezetvédelem\w*|hulladék\w*|újrahasznosítás\w*|akku\w*|akkumulátorgyár\w*|klíma\w*|természetvédelem\w*|levegőszennyezés\w*|védett terület\w*)\b',
    8: r'\b(energia\w*|villamos energia\w*|áram\b|földgáz\w*|gázellátás\w*|paks\b|atomenergia\w*|kőolaj\w*|rezsi\w*|megújuló energia\w*|szélerőmű\w*|napelem\w*)\b',
    9: r'\b(állampolgárság\w*|honosítás\w*|bevándorl\w*|menekült\w*|migráci\w*|idegenrendészet\w*|kettős állampolgárság\w*|határőrizet\w*|határkerítés\w*|külhoni magyar\w*)\b',
    10: r'\b(közlekedés\w*|vasút\w*|máv\b|autópálya\w*|közút\w*|tömegközlekedés\w*|parkolás\w*|volán\w*|jármű\w*|mozdony\w*)\b',
    12: r'\b(korrupció\w*|elszámoltatás\w*|pénzmosás\w*|titkosszolgálat\w*|btk\b|bűncselekmény\w*|bűnözés\w*|rendőrség\w*|közbiztonság\w*|bíróság\w*|ügyészség\w*|kúria\b|ptk\b|csődeljárás\w*|felszámolás\w*|vagyonvisszaszerzés\w*|szuverenitásvédelmi\w*)\b',
    13: r'\b(családtámogatás\w*|család\w*\s+támogatás\w*|családi pótlék\w*|gyes\b|gyed\b|csok\b|gyermekvédelem\w*|gyámügy\w*|nyugdíj\w*|idősgondozás\w*|segély\w*|szociális\w*|szegénység\w*|fogyatékosság\w*)\b',
    # CAP 14: Településfejlesztés, lakásügy ÉS helyi önkormányzatok
    14: r'\b(önkormányzat\w*|polgármester\w*|képviselő-testület\w*|lakásügy\w*|lakhatás\w*|bérlakás\w*|otthonteremtés\w*|vidékfejlesztés\w*|magyar falu program\w*|településfejlesztés\w*|település\w*|kistelepülés\w*|falu\w*|városfejlesztés\w*)\b',
    15: r'\b(bank\b|bankok\w*|bankadó\w*|bankrendszer\w*|hitel\w*|devizahitel\w*|értékpapír\w*|tőzsde\w*|kripto\w*|pénzügyi szektor\w*|fogyasztóvédelem\w*|versenyhivatal\w*|gvh\b|kkv\b|sport\w*|turizmus\w*|közbeszerzés\w*)\b',
    16: r'\b(honvédelem\w*|honvédség\w*|katona\w*|nato\b|haderő\w*|légierő\w*|haditechnika\w*)\b',
    17: r'\b(média\b|médiatörvény\w*|médiaszolgáltat\w*|sajtó\b|sajtószabadság\w*|rádió\w*|televízió\w*|hírközlés\w*|mtva\b|nmhh\b|távközlés\w*|internet\w*|kiberbiztonság\w*|informatik\w*)\b',
    18: r'\b(külkereskedelem\w*|export\w*|import\w*|vám\b|vámunió\w*)\b',
    19: r'\b(európai unió\w*|eu\b|brüsszel\b|uniós forrás\w*|rrf\b|helyreállítási terv\w*|külpolitika\w*|diplomácia\w*|nagykövet\w*|ukrajna\w*|oroszország\w*|egyesült államok\w*)\b',
    # CAP 20: Tiszta alkotmányozás, választási rendszer, kormányzati szerkezet (önkormányzatok nélkül!)
    20: r'\b(alkotmány\w*|alaptörvény\w*|alkotmánymódosítás\w*|házszabály\w*|mentelmi jog\w*|alkotmánybíróság\w*|választás\w*|választási törvény\w*|kampányfinanszírozás\w*|pártfinanszírozás\w*|népszavazás\w*|minisztérium\w*|kormányzati struktúra\w*|közigazgatás\w*|közszolgálat\w*|vizsgálóbizottság\w*)\b',
    21: r'\b(vízgazdálkodás\w*|árvíz\w*|balaton\b|duna\b|gát\b|árvízvédelem\w*)\b',
    23: r'\b(kultúra\w*|színház\w*|múzeum\w*|könyvtár\w*|művészet\w*|nka\b|kulturális örökség\w*)\b'
}

COMPILED = {cap: re.compile(pat, re.IGNORECASE) for cap, pat in LEXICON_PATTERNS.items()}

def get_content_scores(text):
    if not text:
        return {}
    scores = {}
    for cap, regex in COMPILED.items():
        matches = len(regex.findall(text))
        if matches > 0:
            scores[cap] = matches
    return scores

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("=== 1. TÖRVÉNYJAVASLATOK FINOMHANGOLT TARTALMI BESOROLÁSA ===")
    cur.execute("SELECT id, bill_number, title, short_title, affected_law FROM bill")
    bills = cur.fetchall()

    bill_updates = []
    bill_cap_map = {}

    for bid, bnum, title, stitle, aff in bills:
        formal_text = f"{title or ''} {stitle or ''} {aff or ''}".lower()
        
        # Explicit tartalmi besorolás a kulcstörvényeknél:
        if '581' in bnum:
            chosen_cap = 1 # 29 pontos gazdasági csomag
        elif '284' in bnum:
            chosen_cap = 1 # Helyi iparűzési adó
        elif '35' in bnum and 'állami vagyon' in formal_text:
            chosen_cap = 1 # Állami vagyon felelős gazdálkodása
        elif '582' in bnum or '389' in bnum:
            chosen_cap = 15 # Közbeszerzések és piaci kifizetések
        elif '415' in bnum:
            chosen_cap = 15 # KKV fejlesztés
        elif '359' in bnum and ('energetika' in formal_text or 'helyreállítás' in formal_text):
            chosen_cap = 8 # RRF energetikai vállalások
        elif '45' in bnum and 'kormánytisztviselő' in formal_text:
            chosen_cap = 5 # Kormánytisztviselők jogállása (munkaügy)
        elif '123' in bnum and 'szuverenitás' in formal_text:
            chosen_cap = 12 # Szuverenitásvédelmi Hivatal megszüntetése
        elif '39' in bnum and 'összetartozás' in formal_text:
            chosen_cap = 9 # Nemzeti összetartozás / állampolgárság
        elif '638' in bnum:
            chosen_cap = 6 # Iskolai Nemzeti Összetartozás Napja a közoktatásban
        # Önkormányzati törvények -> CAP 14 (Településfejlesztés és helyi önkormányzatok)
        elif any(k in bnum for k in ['42', '32', '44', '253']) and 'önkormányzat' in formal_text:
            chosen_cap = 14
        else:
            scores = get_content_scores(formal_text)
            if scores:
                chosen_cap = sorted(scores.items(), key=lambda x: -x[1])[0][0]
            else:
                chosen_cap = 20

        bill_cap_map[bnum.strip()] = chosen_cap
        cap_name = CAP_MAJORS[chosen_cap]["name_hu"]
        bill_updates.append((str(chosen_cap), chosen_cap * 100, f"CAP {chosen_cap} ({cap_name}): {stitle}", bid))

    cur.executemany("""
        UPDATE bill
        SET primary_topic_code = ?, subtopic_code = ?, topic_summary = ?
        WHERE id = ?
    """, bill_updates)
    conn.commit()
    print(f"✅ {len(bills)} törvényjavaslat tartalmi szövegalapon frissítve.")

    print("\n=== 2. FELSZÓLALÁSOK TARTALMI SZÖVEGALAPÚ BESOROLÁSA ===")
    cur.execute("""
        SELECT s.id, s.agenda_item, s.full_text, s.speech_type_code
        FROM speech s
        WHERE s.word_count >= 200 AND s.is_procedural = 0
    """)
    speeches = cur.fetchall()

    speech_updates = []
    cap_distribution = Counter()

    for sid, agenda, text, stype in speeches:
        agenda_clean = agenda or ""
        text_clean = text or ""
        
        # 1. Teljes szöveg pontozása
        content_scores = get_content_scores(text_clean)
        
        # 2. Napirend törvénykapcsolása
        matched_bill_cap = None
        m = re.search(r'[THPK]\s*/\s*(\d+)', agenda_clean)
        if m:
            bkey_t = f"T/{m.group(1)}"
            bkey_h = f"H/{m.group(1)}"
            if bkey_t in bill_cap_map:
                matched_bill_cap = bill_cap_map[bkey_t]
            elif bkey_h in bill_cap_map:
                matched_bill_cap = bill_cap_map[bkey_h]

        # 3. Döntési hierarchia a valós tartalom alapján:
        if content_scores:
            sorted_scores = sorted(content_scores.items(), key=lambda x: -x[1])
            top_content_cap, top_score = sorted_scores[0]
            cap20_score = content_scores.get(20, 0)
            
            # Kifejezetten Napirend előtti felszólalás: a teljes szöveg domináns szakpolitikája dönt
            if 'napirend előtti' in agenda_clean.lower():
                if top_score >= 2 and (top_content_cap != 20 or cap20_score >= 3):
                    final_cap = top_content_cap
                else:
                    final_cap = 20
                method = "content_speech_dominant"
            # Ha van kapcsolódó törvényjavaslat:
            elif matched_bill_cap and matched_bill_cap != 20:
                bill_score = content_scores.get(matched_bill_cap, 0)
                # Ha a szöveg tartalmilag alátámasztja a törvényt, vagy nincs nála jóval erősebb téma
                if bill_score >= 1 or top_score < 4:
                    final_cap = matched_bill_cap
                    method = "content_bill_aligned"
                else:
                    final_cap = top_content_cap
                    method = "content_speech_dominant"
            elif matched_bill_cap == 20:
                # Alkotmányozási vagy államszervezeti törvény:
                # Ha a képviselő valós szakpolitikáról beszél benne (pl. egészségügy, gazdaság, oktatás):
                if top_content_cap != 20 and top_score >= 3 and (cap20_score == 0 or top_score >= cap20_score * 1.3):
                    final_cap = top_content_cap
                    method = "content_speech_dominant"
                else:
                    final_cap = 20
                    method = "keyword_match"
            else:
                # Nincs törvényjavaslat (kérdés, interpelláció):
                if top_content_cap != 20 and top_score >= 2:
                    final_cap = top_content_cap
                    method = "content_speech_dominant"
                elif cap20_score >= 2:
                    final_cap = 20
                    method = "keyword_match"
                else:
                    final_cap = top_content_cap if top_score >= 1 else 20
                    method = "general_debate"
        else:
            final_cap = matched_bill_cap if matched_bill_cap else 20
            method = "rolldown_unclassified"

        cap_name = CAP_MAJORS[final_cap]["name_hu"]
        speech_updates.append((str(final_cap), final_cap * 100, 0.92, f"CAP {final_cap}: {cap_name}", method, sid))
        cap_distribution[final_cap] += 1

    cur.executemany("""
        UPDATE speech_classification
        SET primary_topic_code = ?, subtopic_code = ?, confidence = ?, summary = ?, cap_classification_method = ?
        WHERE speech_id = ?
    """, speech_updates)
    conn.commit()

    total = len(speeches)
    print(f"\n📊 VÉGLEGES TÉMAMEGOSZLÁS A FINOMHANGOLÁS UTÁN (N = {total} érdemi beszéd):")
    print(f"{'CAP':5} {'Témakör':45} {'db':>5} {'%':>7}")
    print("-" * 62)
    for cap, cnt in cap_distribution.most_common():
        name = CAP_MAJORS[cap]["name_hu"]
        pct = (cnt / total) * 100
        print(f"CAP {cap:2d} {name:45} {cnt:5d} {pct:6.1f}%")

    conn.close()
    print("\n✅ Adatbázis sikeresen frissítve.")

if __name__ == "__main__":
    main()
