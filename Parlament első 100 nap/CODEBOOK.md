# KÓDKÖNYV (CODEBOOK)
## Parlamenti Első 100 Nap Összehasonlító Adatbázis (2010 vs. 2026)
**Verzió:** 2.2 (Procedurális és Mandátumigazolási szűréssel)  
**Standard:** Nemzetközi ParlLawSpeech adatmodell & Comparative Agendas Project (CAP)  
**Készítő:** Bérczi Zoltán | ELTE Bibó István Szakkollégium  
**Kurzusvezető:** Sebők Miklós | 2026. november

---

## 1. Az adatbázis áttekintése (`parlament_100nap.db`)

Az SQLite adatbázis az Országgyűlés plenáris naplóiból kinyert, normalizált relációs szerkezet, amely két kormányváltás utáni első 100 naptári napot dolgozza fel:
- **2010-es időszak:** 2010. május 14. – 2010. augusztus 22. (Fidesz–KDNP kormányváltás)
- **2026-os időszak:** 2026. május 9. – 2026. augusztus 17. (TISZA kormányváltás)

### Korpusz-statisztikák:
- **Összes nyers felszólalás:** 4 826 db
- **Szűrt, ≥200 szavas felszólalások:** 3 873 db
- **Procedurális elnöki határozathirdetések:** 60 db (`is_procedural = 1`)
- **Érdemi szakpolitikai felszólalások:** **3 813 db** (`is_procedural = 0`)
- **Törvényjavaslatok:** 127 db
- **Politikus entitások:** 492 fő

---

## 2. Táblák és változók leírása

### 2.1. `speech` (Felszólalások táblája)
- `id` (TEXT, PK): Egyedi azonosító (`{period}_{sitting_number:03d}_{seq:03d}`, pl. `2010_001_005`).
- `period_id` (TEXT, FK): Korszak azonosítója (`2010` vagy `2026`).
- `sitting_day_id` (TEXT, FK): Az ülésnap azonosítója.
- `speaker_name` (TEXT): A felszólaló hivatalos neve a napló szerint.
- `politician_id` (TEXT, FK): Összekapcsolt politikus entitás azonosítója.
- `group_id` (TEXT, FK): Frakció azonosítója.
- `speech_type_code` (TEXT): Felszólalás típusa (`NAPIREND_ELOTTI`, `EXPOZE`, `VEZERSZONOKI`, `HOZZASZOLAS`, `KETPERCES`, `UGYRENDI`, `ZARSZO`, `AZONNALI_KERDES`, `KORMANYZATI_VALASZ`).
- `agenda_item` (TEXT): A tárgyalt napirendi pont, irományszámokkal.
- `bill_id` (TEXT, FK): Kapcsolódó törvényjavaslat azonosítója (ha van).
- `word_count` (INTEGER): A felszólalás szószáma.
- `full_text` (TEXT): A felszólalás teljes, tisztított szövege.
- `is_procedural` (INTEGER): **[ÚJ]** 1, ha elnöki szavaztatás, határozathirdetés vagy mandátumkezelés; 0, ha érdemi vita.

### 2.2. `speech_classification` (CAP témabesorolás)
- `speech_id` (TEXT, PK, FK): Felszólalás azonosítója.
- `primary_topic_code` (TEXT): Elsődleges CAP főkód (1–23, lásd a 3. fejezetet).
- `subtopic_code` (INTEGER): CAP alkód (pl. 105: Államháztartás, 1202: Korrupció, 1308: Családtámogatás).
- `cap_classification_method` (TEXT): **[ÚJ]** Besorolás módszere:
  - `keyword_match`: Szóhatáros regex egyezés vagy irományszám-alapú linking alapján azonosított téma (pl. valódi CAP 20 alkotmányos vita).
  - `rolldown_reclassified`: A korábbi torzított CAP 20 kategóriából a teljes szövegen valós szakpolitikai kategóriába átsorolt rekord (620 db).
  - `rolldown_unclassified`: Valódi általános vita, amelyben nem volt szakpolitikai kulcsszó (119 db, CAP 20 alatt maradva).
- `confidence` (REAL): Osztályozási megbízhatósági pontszám (0.00 – 1.00).
- `summary` (TEXT): A kategória rövid szöveges összefoglalója.

### 2.3. `parliamentary_group` (Frakciók)
- `id` (TEXT, PK): Frakció azonosítója.
- `name` (TEXT): Frakció teljes neve.
- `short_name` (TEXT): Frakció rövidítése.
- `party_code` (TEXT): **[ÚJ]** Normalizált pártkód függetlenül a kormányzati pozíciótól: `FIDESZ`, `KDNP`, `MSZP`, `JOBBIK`, `LMP`, `TISZA`, `MI_HAZANK`, `FUGGETLEN`.
- `governing_status` (TEXT): `kormánypárt` vagy `ellenzék`.

### 2.4. `speech_retrospective_critique` (Múltkritika)
- `speech_id` (TEXT, PK, FK): Felszólalás azonosítója.
- `has_past_critique` (INTEGER): 1, ha tartalmaz múltbéli kormányzatot bíráló fordulatot; 0 egyébként.
- `target_era` (TEXT): A bírálat célpontja (`2002-2010`, `NER_2010-2026`, vagy `'N/A (nincs múltkritika)'`).
- `critique_intensity` (TEXT): `alacsony`, `közepes`, `magas`, vagy `'N/A'`.
- `matched_patterns` (TEXT): Egyező kulcskifejezések vagy `'N/A'`.
- `excerpts` (TEXT): Releváns idézet vagy `'N/A'`.

---

## 3. A Comparative Agendas Project (CAP) főkategóriái

| CAP Kód | Magyar megnevezés | Angol megnevezés | Főbb tartalom |
|:---:|:---|:---|:---|
| **1** | Makrogazdaság | Macroeconomics | Költségvetés, adósság, adótörvények, MNB, infláció |
| **2** | Polgári jogok és kisebbségek | Civil Rights | Emberi jogok, diszkrimináció, nemzetiségek, romák |
| **3** | Egészségügy | Health | Kórházak, orvosok, gyógyszer, egészségbiztosítás |
| **4** | Mezőgazdaság | Agriculture | Agrárpolitika, gazdák, termőföld-használat, állattenyésztés |
| **5** | Munkaügy | Labor | Foglalkoztatás, minimálbér, szakszervezetek, sztrájkjog |
| **6** | Oktatás | Education | Közoktatás, felsőoktatás, egyetemek, pedagógusbérek |
| **7** | Környezetvédelem | Environment | Klímapolitika, hulladékgazdálkodás, akkugyárak |
| **8** | Energiaügy | Energy | Villamos energia, földgáz, Paks, megújulók |
| **9** | Bevándorlás és állampolgárság | Immigration & Citizenship | Kettős állampolgárság, honosítás, menekültügy |
| **10** | Közlekedés | Transportation | Vasút (MÁV), autópályák, közúti hálózat, tömegközlekedés |
| **12** | Jog és igazságszolgáltatás | Law & Crime | Btk., Ptk., bíróságok, rendőrség, korrupció, elszámoltatás |
| **13** | Szociálpolitika és jólét | Social Welfare | Családtámogatás, GYES/GYED, nyugdíjak, szociális segélyek |
| **14** | Településfejlesztés, önkormányzatok és lakásügy | Community Development & Housing | Helyi önkormányzatok működése, településfejlesztés, bérlakás, Magyar Falu Program |
| **15** | Belkereskedelem, pénzügy | Domestic Commerce | Bankok, devizahitelek, fogyasztóvédelem, sport, turizmus |
| **16** | Honvédelem | Defense | Magyar Honvédség, NATO kötelezettségek, haderőfejlesztés |
| **17** | Technológia és média | Technology & Media | Médiatörvény, sajtószabadság, digitális átállás, távközlés |
| **18** | Külkereskedelem | Foreign Trade | Export, import, vámpolitika |
| **19** | Nemzetközi kapcsolatok | International Affairs | Európai Unió, RRF források, diplomácia, háborús konfliktusok |
| **20** | Alkotmányosság, kormányzati működés és választások | Government Operations | Alkotmány, Alaptörvény, Alkotmánybíróság, választási rendszer, minisztériumi felépítés |
| **21** | Állami földek és vízgazdálkodás | Public Lands & Water | Termőföld, Nemzeti Földalap, árvízvédelem, vízügy |
| **23** | Kultúra | Culture | Művészetek, színházak, kulturális örökség, NKA |

---

## 4. Elemzői nézet: `v_speeches_categorized`

Az elemzésekhez és a reprodukciós vizsgálatokhoz a következő SQL nézet ajánlott:
```sql
SELECT 
    speech_id, period_id, sitting_date, speaker_name, party_code, governing_status,
    speech_type_name, agenda_item, word_count, cap_major_code, cap_classification_method,
    primary_topic, has_past_critique, target_era
FROM v_speeches_categorized
WHERE word_count >= 200 AND is_procedural = 0;
```
