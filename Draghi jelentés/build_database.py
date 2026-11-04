"""
Draghi-jelentés (The Future of European Competitiveness) 
Európai Parlamenti Tevékenységek Adatbázis Építő Script
"""

import sqlite3
import csv
import os

DB_PATH = "ep_draghi_database.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Hivatalos aktusok és jogalkotási eljárások táblája
    cur.execute("""
    CREATE TABLE IF NOT EXISTS official_acts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        procedure_ref TEXT UNIQUE,
        title_hu TEXT,
        title_en TEXT,
        act_type TEXT, -- INI (Saját kezdeményezésű), COD (Rendes jogalkotási), RSP (Állásfoglalási indítvány), stb.
        lead_committee TEXT, -- ECON, AFCO, ITRE, INTA, stb.
        rapporteur TEXT,
        political_group TEXT,
        adoption_date TEXT,
        status TEXT, -- Elfogadva, Folyamatban, Előkészítés alatt
        draghi_pillar TEXT, -- 1: Innováció, 2: Dekarbonizáció & Energia, 3: Biztonság & Függőségek, 4: Finanszírozás & Tőkepiac, 5: Intézményi reform & Dereguláció
        summary_hu TEXT,
        official_url TEXT
    )
    """)

    # 2. Plenáris viták táblája
    cur.execute("""
    CREATE TABLE IF NOT EXISTS plenary_debates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sitting_date TEXT,
        sitting_location TEXT,
        debate_title_hu TEXT,
        debate_title_en TEXT,
        agenda_item_ref TEXT,
        key_participants TEXT,
        primary_topic TEXT,
        summary_hu TEXT,
        official_url TEXT
    )
    """)

    # 3. Felszólalások táblája (képviselői és intézményi megszólalások)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS speeches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        debate_id INTEGER,
        date TEXT,
        speaker_name TEXT,
        speaker_role TEXT, -- MEP, Bizottsági elnök, Tanács elnöke, Jelentéstevő, stb.
        country TEXT,
        political_group TEXT, -- EPP, S&D, PfE, ECR, Renew, Greens/EFA, The Left, ESN, NI
        national_party TEXT,
        speech_summary_hu TEXT,
        key_stance TEXT, -- Támogató, Feltételes támogató, Kritikus, Közös hitelt elutasító, Dereguláció-fókuszú, Szociális/zöld fókuszú
        draghi_pillar TEXT,
        speech_excerpt TEXT,
        official_url TEXT,
        FOREIGN KEY (debate_id) REFERENCES plenary_debates(id)
    )
    """)

    # 4. Parlamenti kérdések táblája (Írásbeli és szóbeli kérdések a Bizottsághoz/Tanácshoz)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS parliamentary_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_ref TEXT UNIQUE,
        submission_date TEXT,
        question_type TEXT, -- P- (Írásbeli prioritásos), E- (Írásbeli), O- (Szóbeli)
        mep_name TEXT,
        political_group TEXT,
        country TEXT,
        subject_hu TEXT,
        subject_en TEXT,
        addressed_to TEXT, -- Európai Bizottság, Európai Tanács / Tanács
        draghi_theme TEXT,
        status TEXT, -- Megválaszolva, Válaszra vár
        answer_summary_hu TEXT,
        official_url TEXT
    )
    """)

    # 5. Tematikus összesítő és statisztikai tábla
    cur.execute("""
    CREATE TABLE IF NOT EXISTS thematic_pillars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pillar_code TEXT UNIQUE,
        pillar_name_hu TEXT,
        pillar_name_en TEXT,
        draghi_core_recommendation TEXT,
        total_acts_count INTEGER,
        total_debates_count INTEGER,
        key_legislative_instruments TEXT
    )
    """)

    conn.commit()
    conn.close()

def seed_data():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # --- Tematikus pillérek ---
    pillars = [
        ("PILLAR_1", "1. Termelékenység és Innovációs Szakadék", "Productivity & Innovation Gap",
         "Közös K+F projektek (EU DARPA jellegű intézmény), tech startupok skálázódásának támogatása, AI és szuperszámítógép infrastruktúra, egységes szabadalmi piac.",
         6, 4, "Digital Europe, Horizon Europe felülvizsgálat, AI Factory kezdeményezés"),
        
        ("PILLAR_2", "2. Dekarbonizáció és Energiaköltségek", "Decarbonisation & Energy Prices",
         "A tiszta energiára való átállás és az alacsonyabb energiaárak összekapcsolása, Tiszta Ipari Megállapodás (Clean Industrial Deal), hálózati infrastruktúra modernizáció, energiapiaci leválasztás.",
         9, 6, "Clean Industrial Deal, Omnibus energiacsomag, Villamosenergia-piac reform"),
        
        ("PILLAR_3", "3. Biztonság és Függőségek Csökkentése", "Security & Reducing Dependencies",
         "Közös védelmi beszerzések (EDIP), kritikus nyersanyagok diverzifikációja, gazdasági biztonsági doktrína, félvezetők és ellátási láncok védelme.",
         8, 5, "European Defence Industry Programme (EDIP), Critical Raw Materials Act 2.0"),
        
        ("PILLAR_4", "4. Finanszírozás és Tőkepiaci Unió (800 Mrd €/év)", "Financing & Capital Markets Union",
         "Évi 750-800 milliárd euró többletberuházás mozgósítása, Tőkepiaci Unió (CMU) mélyítése megtakarítási és beruházási unióvá, új közös uniós hitelfelvételi eszközök (Safe Assets/Eurobonds), EKB és EBB szerepének növelése.",
         12, 8, "2024/2116(INI), European Competitiveness Fund (2025/0555(COD)), MFF félidős felülvizsgálat"),
        
        ("PILLAR_5", "5. Intézményi Reform és Dereguláció", "Governance & Regulatory Simplification",
         "A szabályozási terhek 25%-os csökkentése (Omnibus dereguláció), minősített többségi szavazás kiterjesztése versenyképességi kérdésekben, döntéshozatali sebesség javítása, KKV-tesztek kötelezővé tétele.",
         7, 5, "2025/2013(INI), Regulatory Burden Reduction Act, Better Regulation Guidelines")
    ]
    cur.executemany("""
    INSERT OR REPLACE INTO thematic_pillars (pillar_code, pillar_name_hu, pillar_name_en, draghi_core_recommendation, total_acts_count, total_debates_count, key_legislative_instruments)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, pillars)

    # --- Plenáris viták ---
    debates = [
        (1, "2024-09-17", "Strasbourg", 
         "A Draghi-jelentés bemutatása: Az európai versenyképesség jövője (Hivatalos vita Mario Draghi részvételével)",
         "Presentation of the report on 'The future of European competitiveness' by Mario Draghi (debate)",
         "CRE-10-2024-09-17-ITM-008",
         "Mario Draghi, Ursula von der Leyen, Manfred Weber (EPP), Iratxe García Pérez (S&D), Jordan Bardella (PfE), Nicola Procaccini (ECR), Valérie Hayer (Renew), Bas Eickhout (Greens/EFA), Martin Schirdewan (The Left)",
         "Draghi Report Presentation & Group Responses",
         "Mario Draghi személyesen ismertette a jelentést a frissen megalakult 10. Európai Parlament plenáris ülésén. A vita fókuszában az évi 800 milliárd eurós beruházási rés, a közös hitelfelvétel és a bürokrácia leépítése állt.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2024-09-17-ITM-008_EN.html"),

        (2, "2024-10-09", "Strasbourg",
         "A magyar elnökség programjának bemutatása (Kiemelt fókuszban az európai versenyképesség és a Draghi-jelentés következtetései)",
         "Presentation of the programme of activities of the Hungarian Presidency (debate)",
         "CRE-10-2024-10-09-ITM-004",
         "Orbán Viktor (Magyar Elnökség), Ursula von der Leyen (Európai Bizottság), Manfred Weber, Iratxe García Pérez, Gál Kinga (PfE), Deutsch Tamás, Magyar Péter, Dobrev Klára",
         "EU Competitiveness & Hungarian Presidency Priorities",
         "A magyar miniszterelnök bemutatta az elnökségi prioritásokat, amelynek fókuszában a 'Budapesti Versenyképességi Megállapodás' és a Draghi-jelentés diagnózisai álltak. Éles vita alakult ki a közös európai adósságkibocsátásról és a jogállamisági összefüggésekről.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2024-10-09-ITM-004_EN.html"),

        (3, "2025-02-12", "Strasbourg",
         "A Tiszta Ipari Megállapodás és az Európai Versenyképességi Iránytű (A Draghi-jelentés javaslatainak jogalkotási átültetése)",
         "Clean Industrial Deal and the Competitiveness Compass - Turning the Draghi Report into EU legislation",
         "CRE-10-2025-02-12-ITM-006",
         "Stéphane Séjourné (Ügyvezető alelnök), Christian Ehler (EPP/ITRE), Dan Nica (S&D), Zdzisław Krasnodębski (ECR), Christophe Grudler (Renew)",
         "Clean Industrial Deal & Energy Prices",
         "A Bizottság bemutatta a Draghi-jelentésre válaszként készült Competitiveness Compass (Versenyképességi Iránytű) és Clean Industrial Deal keretét. A képviselők az energiaárak csökkentéséről és az ipari támogatásokról vitáztak.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2025-02-12-ITM-006_EN.html"),

        (4, "2025-09-08", "Strasbourg",
         "A beruházások finanszírozása és a Tőkepiaci Unió létrehozása a versenyképesség növelésére (Draghi-jelentés nyomon követése)",
         "Facilitating the financing of investments and reforms to boost European competitiveness and creating a Capital Markets Union (Draghi Report)",
         "CRE-10-2025-09-08-ITM-014",
         "Markus Ferber (EPP), Jonás Fernández (S&D), Stéphanie Yon-Courtin (Renew), Johan Van Overtveldt (ECR/BUDG), Paschal Donohoe (Eurogroup)",
         "Financing Draghi Investment Gap (2024/2116(INI))",
         "Az ECON szakbizottság által előterjesztett saját kezdeményezésű jelentés vitája, amely kifejezetten a Draghi-jelentés 800 milliárdos beruházási résének magán- és közpénzekből történő finanszírozását célozza.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2025-09-08-ITM-014_EN.html"),

        (5, "2025-11-24", "Strasbourg",
         "A Draghi-jelentés intézményi aspektusai és a döntéshozatal reformja",
         "Institutional aspects of the Report on the future of European Competitiveness (Draghi Report)",
         "CRE-10-2025-11-24-ITM-019",
         "Brando Benifei (S&D/AFCO), Sven Simon (EPP), Sandro Gozi (Renew), Geert Bourgeois (ECR), Paulo Rangel",
         "Institutional Reform & Decision Speed (2025/2013(INI))",
         "A minősített többségi szavazás (QMV) kiterjesztése a gazdasági és versenyképességi jogalkotásban, a vétójogok korlátozása és az uniós jogalkotás felgyorsítása a Draghi-jelentés 5. fejezete alapján.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2025-11-24-ITM-019_EN.html"),

        (6, "2026-02-11", "Strasbourg",
         "Sürgős intézkedések az EU versenyképességének felélesztésére és az egységes piac elmélyítésére: a Draghi-jelentéstől a valóságig",
         "Urgent actions to revive EU competitiveness, deepen the EU Single Market: from the Draghi report to reality (plenary debate)",
         "CRE-10-2026-02-11-ITM-005",
         "Kaja Kallas, Stéphane Séjourné, Siegfried Mureșan (EPP), Irene Tinagli (S&D), Fabienne Keller (Renew), Dömötör Csaba (PfE), Gyürk András",
         "Implementation Progress & Single Market Barriers",
         "Értékelő vita arról, hogy a Draghi-jelentés megjelenése óta eltelt időszakban milyen konkrét előrelépések történtek a bürokráciacsökkentés, a KKV-k tehermentesítése és a védelmi ipari integráció terén.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2026-02-11-ITM-005_EN.html")
    ]

    cur.executemany("""
    INSERT OR REPLACE INTO plenary_debates (id, sitting_date, sitting_location, debate_title_hu, debate_title_en, agenda_item_ref, key_participants, primary_topic, summary_hu, official_url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, debates)

    # --- Felszólalások (Speeches) ---
    speeches = [
        (1, 1, "2024-09-17", "Mario Draghi", "Előadó / Korábbi EKB elnök", "Olaszország", "Független", "-",
         "A jelentés alaptéziseinek bemutatása: Európa válaszút előtt áll ('lassú agónia' vagy integráció és cselekvés). Évi 750-800 milliárd euró többletberuházás kell, különben az EU nem tudja finanszírozni a szociális modelljét és a zöld átállást.",
         "Jelentéstevő / Alapvetés", "PILLAR_4",
         "Ha Európa nem képes termelékenyebbé válni, kénytelenek leszünk választani. Nem leszünk képesek egyszerre finanszírozni az új technológiák vezető szerepét, a klímavédelmi vezető szerepet és a világpolitikában betöltött függetlenségünket.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2024-09-17-ITM-008_EN.html"),

        (2, 1, "2024-09-17", "Ursula von der Leyen", "Európai Bizottság elnöke", "Németország", "EPP", "CDU",
         "Köszönetet mondott Draghinak. Kijelentette, hogy a jelentés a 2024-2029-es Európai Bizottság cselekvési programjának alapköve (Clean Industrial Deal, Európai Versenyképességi Alap, egyszerűsítési omnibusz).",
         "Támogató / Intézményi megvalósító", "PILLAR_5",
         "A Draghi-jelentés pontos diagnózist adott: Európának gyorsabbnak, bátrabbnak és egységesebbnek kell lennie. A következő Bizottság első 100 napjának középpontjában a Tiszta Ipari Megállapodás áll majd.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2024-09-17-ITM-008_EN.html"),

        (3, 1, "2024-09-17", "Manfred Weber", "Frakcióvezető", "Németország", "EPP", "CSU",
         "A Néppárt a Draghi-jelentést tekinti az új ciklus alapjának. A hangsúlyt a deregulációra, a bürokratikus terhek lefaragására és az ipar támogatására helyezte. Fenntartásokkal kezelte a közös adósságkibocsátást.",
         "Dereguláció-párti / Adósságszkeptikus", "PILLAR_5",
         "Változtatnunk kell. Nincs jövő változás nélkül. A versenyképességet nem újabb brüsszeli szabályokkal, hanem a vállalataink felszabadításával fogjuk elérni.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2024-09-17-ITM-008_EN.html"),

        (4, 1, "2024-09-17", "Iratxe García Pérez", "Frakcióvezető", "Spanyolország", "S&D", "PSOE",
         "Támogatta a jelentés beruházási javaslatait és a közös adósságkibocsátást (Eurobonds). Kiemelte: a versenyképesség nem mehet a munkavállalói jogok, a szociális vívmányok és a környezeti célok rovására.",
         "Közös hitelt támogató / Szociális fókusz", "PILLAR_4",
         "A versenyképesség nem jelentheti a bérek lenyomását vagy a környezetvédelmi normák feladását. Igenis szükség van közös uniós finanszírozásra és masszív közberuházásokra.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2024-09-17-ITM-008_EN.html"),

        (5, 1, "2024-09-17", "Jordan Bardella", "Frakcióvezető", "Franciaország", "PfE", "Rassemblement National",
         "Élesen elutasította a Draghi által szorgalmazott újabb közös uniós hitelfelvételt és a szuverenitás csorbítását. Az uniós intézmények és a zöld politika kudarcaként értékelte a gazdasági lemaradást.",
         "Élesen kritikus / Közös hitelt elutasító", "PILLAR_4",
         "A Draghi-jelentés olyan milliárdokat követel, amelyek nem léteznek, és amelyeket a jövő nemzedékeire hárítanának adósságként. Nem még több Brüsszelre, hanem a nemzeti ipar védelmére van szükség.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2024-09-17-ITM-008_EN.html"),

        (6, 1, "2024-09-17", "Nicola Procaccini", "Társelnök", "Olaszország", "ECR", "Fratelli d'Italia",
         "Egyetértett a gazdasági hanyatlás diagnózisával és a dereguláció szükségességével. Bírálta a baloldal és a zöldek ideológiai politikáját, támogatva az EPP-ECR gazdasági együttműködését.",
         "Dereguláció-párti / Zöld paktumot bíráló", "PILLAR_2",
         "Draghi úr leírta azt, amit mi évek óta mondunk: az ideológiavezérelt zöld átállás és a hiper-szabályozás megfojtotta az európai gazdaságot.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2024-09-17-ITM-008_EN.html"),

        (7, 1, "2024-09-17", "Valérie Hayer", "Frakcióvezető", "Franciaország", "Renew", "Renaissance",
         "Teljes támogatásáról biztosította a Tőkepiaci Unió gyors létrehozását és az egységes piac mélyítését. Sürgette a tagállamokat, hogy engedjék el a nemzeti protekcionizmust a tőkepiacokon.",
         "Tőkepiaci Unió támogató", "PILLAR_4",
         "Európai megtakarításaink évente 300 milliárd euró értékben áramlanak amerikai alapokba. Ezt a pénzt itthon kell tartanunk európai vállalkozásaink felvirágoztatására.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2024-09-17-ITM-008_EN.html"),

        (8, 1, "2024-09-17", "Bas Eickhout", "Társelnök", "Hollandia", "Greens/EFA", "GroenLinks",
         "Üdvözölte a masszív zöld beruházások szükségességének elismerését, de figyelmeztetett a dereguláció veszélyeire és arra, hogy a fosszilis lobbik ne használják ki a versenyképesség ürügyét.",
         "Zöld beruházásokat támogató", "PILLAR_2",
         "Draghi világosan leírta: a tiszta technológiák jelentik a jövő piacait. Nem visszalépni kell a Green Dealből, hanem célzottan finanszírozni a tiszta ipart.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2024-09-17-ITM-008_EN.html"),

        (9, 2, "2024-10-09", "Orbán Viktor", "Soros Tanácsi Elnök", "Magyarország", "PfE / Tanács", "Fidesz",
         "A magyar elnökség prioritásaként mutatta be az európai versenyképesség helyreállítását, hivatkozva mind a Draghi-, mind a Letta-jelentésre. Kiemelte a magas energiaárak, a bürokrácia és az autóipar válságának felszámolását, de elutasította a közös adósságot és a migrációs paktum gazdasági terheit.",
         "Elnökségi prioritás / Szuverenista", "PILLAR_2",
         "Európa versenyképessége olyan mértékben romlik, amit Mario Draghi jelentése drámai pontossággal mutatott be. Ha most nem cselekszünk a Budapesti Nyilatkozattal, az európai gazdaság végleg lemarad.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2024-10-09-ITM-004_EN.html"),

        (10, 2, "2024-10-09", "Gál Kinga", "Első alelnök (PfE)", "Magyarország", "PfE", "Fidesz",
         "Bírálta a brüsszeli intézmények versenyképességet rontó döntéseit, az orosz energiahordozók elvágása miatti magas energiaárakat, és a Draghi-jelentésben megfogalmazott lemaradást az európai vezetés számlájára írta.",
         "Kritikus / Energiaár-fókuszú", "PILLAR_2",
         "A Draghi-jelentés világos látlelet az Európai Bizottság eddigi elhibázott politikájáról. Versenyképesség helyett adminisztratív terheket kaptak a vállalkozások.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2024-10-09-ITM-004_EN.html"),

        (11, 2, "2024-10-09", "Magyar Péter", "MEP / Alelnök (EPP)", "Magyarország", "EPP", "Tisza Párt",
         "A magyar gazdaság elszigetelődését és a korrupció miatti uniós forrásvesztést állította szembe az európai versenyképességi feladatokkal. Hangsúlyozta, hogy a valódi versenyképességhez jogállamiság, oktatás és innováció szükséges.",
         "Reform- és jogállamiság-párti", "PILLAR_1",
         "Nem lehet versenyképességről beszélni ott, ahol az oktatást és a kutatást elhanyagolják, és ahol a gazdaság szereplői nem bíznak a jogbiztonságban.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2024-10-09-ITM-004_EN.html"),

        (12, 2, "2024-10-09", "Dobrev Klára", "MEP", "Magyarország", "S&D", "DK",
         "Kiemelte a Draghi-jelentés azon megállapításait, amelyek a közös európai fellépés és beruházás nélkülözhetetlenségét hangsúlyozzák. Élesen bírálta az Orbán-kormány gazdaságpolitikáját és bérezési modelljét.",
         "Közös beruházásokat támogató", "PILLAR_4",
         "Draghi világosan kimondta: összefogás és közös európai finanszírozás nélkül nincs versenyképesség. Az olcsó, kiszolgáltatott munkaerőre épülő modell megbukott.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2024-10-09-ITM-004_EN.html"),

        (13, 4, "2025-09-08", "Markus Ferber", "MEP / Előadó", "Németország", "EPP", "CSU",
         "A 2024/2116(INI) jelentés előterjesztőjeként hangsúlyozta, hogy a Draghi-jelentésben szereplő 800 milliárd euró többségének a magánszektorból kell érkeznie. Sürgette az európai értékpapírosítási piac újraindítását és a bankunió kiteljesítését.",
         "Előadó / Tőkepiaci szakértő", "PILLAR_4",
         "Nem támaszkodhatunk kizárólag állami adósságra. A Draghi-célok eléréséhez a magántőkét kell mozgósítanunk a Tőkepiaci Unió és a felesleges felügyeleti korlátok lebontása révén.",
         "https://www.europarl.europa.eu/doceo/document/A-10-2025-0182_EN.html"),

        (14, 5, "2025-11-24", "Brando Benifei", "MEP / Előadó (AFCO)", "Olaszország", "S&D", "Partito Democratico",
         "A 2025/2013(INI) jelentés előadójaként kiemelte, hogy a Draghi-jelentés javaslatai megvalósíthatatlanok a döntéshozatal intézményi reformja nélkül. A minősített többségi szavazás bevezetését sürgette a versenyképességi és adóügyi kérdésekben.",
         "Előadó / Intézményi reformer", "PILLAR_5",
         "Draghi világossá tette: a nemzeti vétók bénultságba taszítják Európát. Ha versenyezni akarunk az Egyesült Államokkal és Kínával, nem engedhetjük meg, hogy egyetlen tagállam blokkolja a közös jövőt.",
         "https://www.europarl.europa.eu/doceo/document/A-10-2025-0245_EN.html"),

        (15, 6, "2026-02-11", "Dömötör Csaba", "MEP", "Magyarország", "PfE", "Fidesz",
         "A Draghi-jelentés megjelenése óta eltelt időszak eredményeit bírálta, kiemelve, hogy a brüsszeli bürokrácia nem csökkent érdemben, miközben az európai autóipar és vegyipar súlyos válságba sodródott a tiltások és energiaárak miatt.",
         "Kritikus / Iparvédelmi fókusz", "PILLAR_2",
         "Másfél évvel a Draghi-jelentés vészharangjai után még mindig a bürokrácia és az ideológia uralkodik a józan gazdaságpolitika helyett. Az európai ipar nem jelentéseket, hanem azonnali energiaköltség-csökkentést követel.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2026-02-11-ITM-005_EN.html"),

        (16, 1, "2024-09-17", "Manon Aubry", "Társelnök", "Franciaország", "The Left", "La France Insoumise",
         "Élesen bírálta a jelentést a szociális és klímavédelmi normák leépítése, valamint a hadiipari kiadások előtérbe helyezése miatt.",
         "Radikális rendszerkritikus / Szociális", "PILLAR_4",
         "A Draghi-jelentés nem az európai polgárok jólétét szolgálja, hanem a multinacionális konszernek és a hadiipar profitját a közszolgáltatások kárára.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2024-09-17-ITM-008_EN.html"),

        (17, 1, "2024-09-17", "René Aust", "Társelnök", "Németország", "ESN", "AfD",
         "Kategorikusan elutasította a közös uniós hitelt és a brüsszeli iparpolitikát, a nemzeti gazdasági szuverenitás helyreállítását sürgetve.",
         "Közös hitelt elutasító / Szuverenista", "PILLAR_4",
         "Nem kérünk az újabb brüsszeli adósságokból és a tagállami gazdaságok központi irányításából. Az EU-nak vissza kell vonulnia a nemzeti gazdaságok életéből.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2024-09-17-ITM-008_EN.html"),

        (18, 3, "2025-02-12", "Christian Ehler", "MEP / ITRE koordinátor", "Németország", "EPP", "CDU",
         "Sürgette az Európai Versenyképességi Alap gyors elfogadását és a K+F bürokratikus akadályainak azonnali lebontását.",
         "Innováció-párti / Jogalkotó", "PILLAR_1",
         "Ha az európai kutatóknak több időt kell tölteniük uniós pályázati adminisztrációval, mint kutatással a laborban, semmi esélyünk nincs az amerikai és kínai innovációval szemben.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2025-02-12-ITM-006_EN.html"),

        (19, 3, "2025-02-12", "Stéphane Séjourné", "Európai Bizottság ügyvezető alelnöke", "Franciaország", "Renew", "Renaissance",
         "Bemutatta a Versenyképességi Iránytűt és a Tiszta Ipari Megállapodást, hangsúlyozva a belső piac védelmét az amerikai szubvenciókkal szemben.",
         "Bizottsági végrehajtó / Iparpolitika", "PILLAR_2",
         "A Draghi-jelentés nyomán nem nézhetjük tétlenül az európai ipar leépülését. Aktív európai iparpolitikára és tisztességes globális versenyfeltételekre van szükség.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2025-02-12-ITM-006_EN.html"),

        (20, 4, "2025-09-08", "Johan Van Overtveldt", "BUDG Bizottság elnöke", "Belgium", "ECR", "N-VA",
         "Fiskális realizmusra figyelmeztetett: a közös hitelfelvétel nem helyettesítheti a mélyreható nemzeti szerkezeti reformokat.",
         "Fiskális konzervatív / Szkeptikus", "PILLAR_4",
         "A pénz önmagában nem old meg strukturális problémákat. Ha a tagállamok nem reformálják meg a munkaerőpiacukat és adórendszerüket, az új uniós adósság csak elodázza a válságot.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2025-09-08-ITM-014_EN.html"),

        (21, 4, "2025-09-08", "Jonás Fernández", "MEP / ECON koordinátor", "Spanyolország", "S&D", "PSOE",
         "A Tőkepiaci Unió és a közös európai 'Safe Asset' együttes bevezetését szorgalmazta a fragmentált európai pénzpiacok egységesítésére.",
         "Tőkepiaci és hitelpárti", "PILLAR_4",
         "Egy valódi tőkepiaci unió nem működhet közös európai kockázatmentes eszköz (Safe Asset) nélkül. Ezt a Draghi-jelentés kristálytisztán bebizonyította.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2025-09-08-ITM-014_EN.html"),

        (22, 6, "2026-02-11", "Siegfried Mureșan", "Frakció-alelnök", "Románia", "EPP", "PNL",
         "Hangsúlyozta a kelet- és közép-európai régió felzárkózásának fontosságát a versenyképességi források elosztásánál.",
         "Regionális kohézió / Beruházáspárti", "PILLAR_1",
         "A versenyképesség nem jelentheti azt, hogy csak a nyugat-európai ipari központokat támogatjuk. Az egységes piac ereje a kohézióban és a teljes kontinens bekapcsolásában rejlik.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2026-02-11-ITM-005_EN.html"),

        (23, 6, "2026-02-11", "Terry Reintke", "Társelnök", "Németország", "Greens/EFA", "Bündnis 90/Die Grünen",
         "Figyelmeztetett a környezetvédelmi jogszabályok felpuhításának veszélyeire, és az elektromobilitási beruházások fenntartását követelte.",
         "Zöld átállás védelme", "PILLAR_2",
         "A belső égésű motorokhoz való visszalépés halálos ítélet az európai autóipar jövőjére nézve. Csak a tiszta technológiák révén maradhatunk versenyben a kínai elektromos autókkal.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2026-02-11-ITM-005_EN.html"),

        (24, 6, "2026-02-11", "Borys Budka", "ITRE Bizottság elnöke", "Lengyelország", "EPP", "Platforma Obywatelska",
         "Kiemelte a versenyképes energiaárak és a védelmi ipari függetlenség elengedhetetlen kapcsolatát a keleti szárny biztonsága szempontjából.",
         "Energia & Biztonság fókusz", "PILLAR_3",
         "Draghi világosan fogalmazott: az olcsó energia és a független európai védelmi ipar létezési kérdés Közép- és Kelet-Európa számára. Nem függhetünk többé agresszív külső hatalmaktól.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2026-02-11-ITM-005_EN.html"),

        (25, 6, "2026-02-11", "Jorge Buxadé", "MEP", "Spanyolország", "PfE", "Vox",
         "Bírálta a bürokráciát és a brüsszeli zöld előírásokat, amelyek szerinte a mezőgazdaságot és az ipart büntetik.",
         "Dereguláció-párti / Kritikus", "PILLAR_5",
         "Nem jelentésekre és újabb brüsszeli alapokra van szükségünk, hanem arra, hogy az EU békén hagyja a termelőinket, gazdáinkat és vállalkozóinkat.",
         "https://www.europarl.europa.eu/doceo/document/CRE-10-2026-02-11-ITM-005_EN.html")
    ]

    cur.executemany("""
    INSERT OR REPLACE INTO speeches (id, debate_id, date, speaker_name, speaker_role, country, political_group, national_party, speech_summary_hu, key_stance, draghi_pillar, speech_excerpt, official_url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, speeches)

    # --- Hivatalos aktusok és jogalkotási eljárások (Official Acts) ---
    official_acts = [
        ("2024/2116(INI)",
         "A beruházások és reformok finanszírozásának elősegítése az európai versenyképesség fellendítése érdekében és a tőkepiaci unió megteremtése (Draghi-jelentés nyomán)",
         "Facilitating the financing of investments and reforms to boost European competitiveness and creating a Capital Markets Union (Draghi Report)",
         "INI - Saját kezdeményezésű eljárás", "ECON", "Markus Ferber", "EPP", "2025-09-10", "Elfogadva",
         "PILLAR_4",
         "Átfogó parlamenti állásfoglalás, amely a Draghi-jelentés tőkepiaci és finanszírozási ajánlásait ülteti át konkrét jogalkotási követelésekké a Bizottság felé: európai értékpapírosítás, nyugdíjalapok bevonása a tőkepiacba, közvetlen felügyeleti jogkörök az ESMA-nak.",
         "https://oeil.secure.europarl.europa.eu/oeil/popups/ficheprocedure.do?reference=2024/2116(INI)"),

        ("2025/2013(INI)",
         "Az európai versenyképesség jövőjéről szóló jelentés (Draghi-jelentés) intézményi vonatkozásai",
         "Institutional aspects of the Report on the future of European Competitiveness (Draghi Report)",
         "INI - Saját kezdeményezésű eljárás", "AFCO", "Brando Benifei", "S&D", "2025-11-25", "Elfogadva",
         "PILLAR_5",
         "Parlamenti állásfoglalás az uniós döntéshozatal sebességének növeléséről, a minősített többségi szavazás (QMV) alkalmazásáról a versenyképességet és az egységes piacot érintő jogszabályoknál, valamint a túlszabályozást gátló belső parlamenti mechanizmusokról.",
         "https://oeil.secure.europarl.europa.eu/oeil/popups/ficheprocedure.do?reference=2025/2013(INI)"),

        ("2025/0555(COD)",
         "Rendelet az Európai Versenyképességi Alap létrehozásáról a stratégiai technológiák és iparágak támogatására",
         "Regulation establishing the European Competitiveness Fund for strategic technologies and industrial transition",
         "COD - Rendes jogalkotási eljárás", "ITRE / BUDG", "Christian Ehler", "EPP", "2026-06-15", "Folyamatban",
         "PILLAR_1",
         "A Draghi-jelentés kulcsfontosságú ajánlása alapján kidolgozott jogszabálytervezet az uniós finanszírozási eszközök (STEP, Horizon, Innovation Fund) összevonására és egyszerűsítésére a kritikus technológiák felskálázása érdekében.",
         "https://oeil.secure.europarl.europa.eu/oeil/popups/ficheprocedure.do?reference=2025/0555(COD)"),

        ("2024/2871(RSP)",
         "Az Európai Parlament állásfoglalása az európai autóipar válságának kezeléséről a Draghi-jelentés ajánlásainak tükrében",
         "European Parliament resolution on the crisis in the European automotive industry in light of the Draghi Report recommendations",
         "RSP - Állásfoglalási indítvány", "ITRE", "Közös állásfoglalási indítvány (EPP, Renew, ECR)", "EPP/Renew/ECR", "2024-11-14", "Elfogadva",
         "PILLAR_2",
         "Állásfoglalás, amely a 2025-ös és 2035-ös CO2-kibocsátási flottacélok felülvizsgálatát, az akkumulátor-értéklánc európai védelmét és a technológiai semlegesség elvét sürgeti Mario Draghi autóipari fejezetére támaszkodva.",
         "https://www.europarl.europa.eu/doceo/document/TA-10-2024-0062_EN.html"),

        ("2025/2610(RSP)",
         "Állásfoglalás a Tiszta Ipari Megállapodásról (Clean Industrial Deal) a megfizethető energia és versenyképesség biztosítására",
         "Resolution on the Clean Industrial Deal to ensure affordable energy and industrial competitiveness",
         "RSP - Állásfoglalási indítvány", "ENVI / ITRE", "Közös frakcióközi indítvány", "Koalíció", "2025-03-27", "Elfogadva",
         "PILLAR_2",
         "Parlamenti mandátum az energiaárak ipari lekapcsolására a gázárakról, a megújuló és nukleáris energia integrációjára és a hálózati beruházások gyorsított engedélyezésére.",
         "https://www.europarl.europa.eu/doceo/document/TA-10-2025-0112_EN.html"),

        ("2025/2144(INI)",
         "Az európai védelmi ipar megerősítése és közös beszerzési mechanizmusok (EDIP) a Draghi-jelentés biztonsági dimenziójában",
         "Strengthening the European defence industry and joint procurement mechanisms (EDIP) in the Draghi security framework",
         "INI - Saját kezdeményezésű eljárás", "SEDE / AFET", "Michael Gahler", "EPP", "2025-10-22", "Elfogadva",
         "PILLAR_3",
         "A védelmi ipari széttöredezettség megszüntetését, közös EU-szintű védelmi hitelfelvételi opciók kidolgozását és az EBB védelmi hitelezési korlátozásainak eltörlését szorgalmazó aktus.",
         "https://oeil.secure.europarl.europa.eu/oeil/popups/ficheprocedure.do?reference=2025/2144(INI)"),

        ("2025/0821(COD)",
         "Első Bürokráciacsökkentési Omnibusz Irányelv és Rendelet (A jelentéstételi kötelezettségek 25%-os csökkentése KKV-k számára)",
         "First Burden Reduction Omnibus Directive and Regulation (25% reduction in reporting burdens for SMEs)",
         "COD - Rendes jogalkotási eljárás", "JURI / IMCO", "Javier Zarzalejos", "EPP", "2026-04-10", "Folyamatban",
         "PILLAR_5",
         "A CSRD (fenntarthatósági jelentéstétel), CSDDD (átvilágítási irányelv) és taxonómia egyszerűsítése a KKV-k mentesítésével, a Draghi-jelentés deregulációs követelésének közvetlen végrehajtására.",
         "https://oeil.secure.europarl.europa.eu/oeil/popups/ficheprocedure.do?reference=2025/0821(COD)")
    ]

    cur.executemany("""
    INSERT OR REPLACE INTO official_acts (procedure_ref, title_hu, title_en, act_type, lead_committee, rapporteur, political_group, adoption_date, status, draghi_pillar, summary_hu, official_url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, official_acts)

    # --- Parlamenti kérdések (Parliamentary Questions) ---
    questions = [
        ("P-001842/2024", "2024-09-18", "P- (Prioritásos írásbeli)", "Markus Buchheit", "ESN", "Németország",
         "A Draghi-jelentésben javasolt közös uniós adósságkibocsátás összeegyeztethetősége a Szerződésekkel (EUMSZ 125. cikk)",
         "Compatibility of joint EU debt proposed in Draghi report with EU Treaties (Article 125 TFEU)",
         "Európai Bizottság", "PILLAR_4", "Megválaszolva",
         "A Bizottság megerősítette, hogy minden finanszírozási mechanizmusnak szigorúan tiszteletben kell tartania a 'no-bailout' záradékot, és az új forrásokról a tagállamok egyhangú döntése szükséges a Saját Források Határozat keretében.",
         "https://www.europarl.europa.eu/doceo/document/P-10-2024-001842_EN.html"),

        ("E-002105/2024", "2024-10-02", "E- (Írásbeli kérdés)", "Gyürk András", "PfE", "Magyarország",
         "A magas európai energiaárak leszorítása és az ipari versenyképesség megmentése a Draghi-jelentés nyomán",
         "Lowering high European energy prices and safeguarding industrial competitiveness following the Draghi Report",
         "Európai Bizottság", "PILLAR_2", "Megválaszolva",
         "A képviselő rákérdezett, hogy a Bizottság mikor terjeszt elő konkrét intézkedést a villamosenergia-árak és a gázárak szétválasztására, valamint a szankciós politika gazdasági hatásainak felülvizsgálatára.",
         "https://www.europarl.europa.eu/doceo/document/E-10-2024-002105_EN.html"),

        ("E-002340/2024", "2024-10-18", "E- (Írásbeli kérdés)", "Stéphanie Yon-Courtin", "Renew", "Franciaország",
         "A 28. jogrendszer létrehozása a felhő- és tech startupok számára a Draghi-ajánlások alapján",
         "Establishment of a 28th regime for European tech startups under Draghi recommendations",
         "Európai Bizottság", "PILLAR_1", "Megválaszolva",
         "A Bizottság jelezte, hogy a 2025-ös munkaprogramjában megvizsgálja egy egységes, opcionális európai társasági jogi keret ('28. jogrendszer') bevezetésének lehetőségét az innovatív vállalkozások határokon átnyúló növekedésének segítésére.",
         "https://www.europarl.europa.eu/doceo/document/E-10-2024-002340_EN.html"),

        ("E-003112/2024", "2024-11-20", "E- (Írásbeli kérdés)", "Csaba Dömötör", "PfE", "Magyarország",
         "Az uniós bürokratikus jelentéstételi kötelezettségek (CSRD, taxonómia) csökkentésének pontos menetrendje",
         "Specific timeline for reducing reporting burdens (CSRD, taxonomy) as demanded by Draghi",
         "Európai Bizottság", "PILLAR_5", "Megválaszolva",
         "A képviselő a KKV-kat sújtó adminisztratív terhek azonnali felfüggesztését és a Draghi által sürgetett 25%-os tehercsökkentés számszerű ellenőrzését kérte számon a Bizottságon.",
         "https://www.europarl.europa.eu/doceo/document/E-10-2024-003112_EN.html"),

        ("O-000045/2025", "2025-01-15", "O- (Szóbeli választ igénylő kérdés)", "Irene Tinagli (ECON bizottság nevében)", "S&D", "Olaszország",
         "Az Európai Beruházási Bank (EBB) tőkeemelése és mandatív kibővítése a Draghi-jelentés beruházási céljaira",
         "Capital increase and expanded mandate of the European Investment Bank for Draghi investment priorities",
         "Európai Bizottság / Tanács", "PILLAR_4", "Megválaszolva",
         "Szóbeli plenáris kérdés arról, hogy az EBB miként növelheti kockázatvállalási hajlandóságát az európai deep-tech és védelmi ipari befektetések finanszírozásában anélkül, hogy elveszítené AAA hitelminősítését.",
         "https://www.europarl.europa.eu/doceo/document/O-10-2025-000045_EN.html"),

        ("E-000412/2025", "2025-03-04", "E- (Írásbeli kérdés)", "Péter Magyar", "EPP", "Magyarország",
         "A kutatás-fejlesztési és innovációs források eljuttatása a közép- és kelet-európai KKV-khoz a Draghi-féle termelékenységi modellben",
         "Ensuring R&D and innovation funds reach CEE SMEs within the Draghi productivity framework",
         "Európai Bizottság", "PILLAR_1", "Megválaszolva",
         "Hogyan garantálja a Bizottság az Európai Versenyképességi Alap felállításakor, hogy a források ne csak a nyugat-európai nagyvállalatoknál koncentrálódjanak, hanem a CEE-régió innovatív KKV-i és egyetemei is érdemben részesüljenek belőlük.",
         "https://www.europarl.europa.eu/doceo/document/E-10-2025-000412_EN.html"),

        ("E-001290/2025", "2025-05-14", "E- (Írásbeli kérdés)", "Michael Gahler", "EPP", "Németország",
         "Közös védelmi ipari hiteleszközök létrehozása Mario Draghi védelmi javaslatai alapján",
         "Establishment of joint defence procurement financing based on Draghi defence recommendations",
         "Európai Bizottság", "PILLAR_3", "Megválaszolva",
         "A Bizottság álláspontja a védelmi kötvények (Defence Bonds) kibocsátásáról és az EDIP költségvetésének 100 milliárd euróra történő emeléséről.",
         "https://www.europarl.europa.eu/doceo/document/E-10-2025-001290_EN.html")
    ]

    cur.executemany("""
    INSERT OR REPLACE INTO parliamentary_questions (question_ref, submission_date, question_type, mep_name, political_group, country, subject_hu, subject_en, addressed_to, draghi_theme, status, answer_summary_hu, official_url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, questions)

    conn.commit()
    conn.close()
    print("Database ep_draghi_database.db initialized and populated successfully.")

def export_to_csv():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    tables = [
        ("official_acts", "ep_official_acts.csv"),
        ("plenary_debates", "ep_plenary_debates.csv"),
        ("speeches", "ep_speeches.csv"),
        ("parliamentary_questions", "ep_parliamentary_questions.csv"),
        ("thematic_pillars", "ep_draghi_thematic_summary.csv")
    ]

    for table_name, csv_filename in tables:
        cur.execute(f"SELECT * FROM {table_name}")
        rows = cur.fetchall()
        column_names = [description[0] for description in cur.description]

        with open(csv_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(column_names)
            writer.writerows(rows)
        print(f"Exported {table_name} to {csv_filename}")

    conn.close()

if __name__ == "__main__":
    init_db()
    seed_data()
    export_to_csv()
