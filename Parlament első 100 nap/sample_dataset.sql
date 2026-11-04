-- =====================================================================
-- MINTA REPREZENTATÍV ADATHALMAZ (2010 ÉS 2026 ELSŐ 100 NAPJÁBÓL)
-- =====================================================================

-- 1. POLITIKUSOK (2010 ÉS 2026)
INSERT OR REPLACE INTO politician (id, name, default_group_id, title) VALUES
-- 2010 politikusok
('horvath_janos', 'Dr. Horváth János', '2010_FIDESZ', 'korelnök, képviselő'),
('schmitt_pal', 'Schmitt Pál', '2010_FIDESZ', 'az Országgyűlés elnöke'),
('orban_viktor_2010', 'Orbán Viktor', '2010_FIDESZ', 'miniszterelnök'),
('semjen_zsolt_2010', 'Dr. Semjén Zsolt', '2010_KDNP', 'miniszterelnök-helyettes'),
('kover_laszlo_2010', 'Kövér László', '2010_FIDESZ', 'képviselő'),
('matolcsy_gyorgy_2010', 'Matolcsy György', '2010_FIDESZ', 'nemzetgazdasági miniszter'),
('navracsics_tibor_2010', 'Dr. Navracsics Tibor', '2010_FIDESZ', 'közigazgatási és igazságügyi miniszter'),
('mesterhazy_attila_2010', 'Mesterházy Attila', '2010_MSZP', 'frakcióvezető'),
('lendvai_ildiko_2010', 'Lendvai Ildikó', '2010_MSZP', 'képviselő'),
('vona_gabor_2010', 'Vona Gábor', '2010_JOBBIK', 'frakcióvezető'),
('schiffer_andras_2010', 'Dr. Schiffer András', '2010_LMP', 'frakcióvezető'),
('javor_benedek_2010', 'Dr. Jávor Benedek', '2010_LMP', 'képviselő'),
-- 2026 politikusok
('magyar_peter_2026', 'Magyar Péter', '2026_TISZA', 'miniszterelnök'),
('kulja_andras_2026', 'Dr. Kulja András', '2026_TISZA', 'egészségügyi miniszter / képviselő'),
('tarr_zoltan_2026', 'Tarr Zoltán', '2026_TISZA', 'képviselő / frakcióvezető'),
('orban_viktor_2026', 'Orbán Viktor', '2026_FIDESZ', 'képviselő, ellenzéki frakcióvezető'),
('kocsis_mate_2026', 'Kocsis Máté', '2026_FIDESZ', 'képviselő'),
('toroczkai_laszlo_2026', 'Toroczkai László', '2026_MI_HAZANK', 'frakcióvezető'),
('dobrev_klara_2026', 'Dobrev Klára', '2026_DK', 'frakcióvezető');

-- 2. ÜLÉSNAPOK
INSERT OR REPLACE INTO sitting_day (id, period_id, sitting_number, sitting_date, session_type, source_url) VALUES
-- 2010 ülésnapok
('2010_001', '2010', 1, '2010-05-14', 'alakuló', 'https://www.parlament.hu/orszaggyulesi-naplo-elozo-ciklusbeli-adatai'),
('2010_002', '2010', 2, '2010-05-17', 'rendes', 'https://www.parlament.hu/orszaggyulesi-naplo-elozo-ciklusbeli-adatai'),
('2010_005', '2010', 5, '2010-05-26', 'rendes', 'https://www.parlament.hu/orszaggyulesi-naplo-elozo-ciklusbeli-adatai'),
('2010_007', '2010', 7, '2010-05-29', 'rendkívüli', 'https://www.parlament.hu/orszaggyulesi-naplo-elozo-ciklusbeli-adatai'),
('2010_012', '2010', 12, '2010-06-08', 'rendkívüli', 'https://www.parlament.hu/orszaggyulesi-naplo-elozo-ciklusbeli-adatai'),
('2010_018', '2010', 18, '2010-07-22', 'rendkívüli', 'https://www.parlament.hu/orszaggyulesi-naplo-elozo-ciklusbeli-adatai'),
-- 2026 ülésnapok
('2026_001', '2026', 1, '2026-05-09', 'alakuló', 'https://www.parlament.hu/orszaggyulesi-naplo'),
('2026_002', '2026', 2, '2026-05-12', 'rendes', 'https://www.parlament.hu/orszaggyulesi-naplo'),
('2026_005', '2026', 5, '2026-05-20', 'rendes', 'https://www.parlament.hu/orszaggyulesi-naplo'),
('2026_010', '2026', 10, '2026-06-09', 'rendkívüli', 'https://www.parlament.hu/orszaggyulesi-naplo'),
('2026_016', '2026', 16, '2026-07-14', 'rendkívüli', 'https://www.parlament.hu/orszaggyulesi-naplo');

-- 3. FELSZÓLALÁSOK (2010)
INSERT OR REPLACE INTO speech (
    id, period_id, sitting_day_id, sequence_number, speaker_name, politician_id, 
    group_id, speech_type_code, agenda_item, bill_id, start_time, end_time, 
    duration_seconds, word_count, full_text, source_url
) VALUES
(
    '2010_001_001', '2010', '2010_001', 1, 'Dr. Horváth János', 'horvath_janos', 
    '2010_FIDESZ', 'NAPIREND_ELOTTI', 'A Magyar Köztársaság Országgyűlésének alakuló ülése', NULL, 
    '10:00', '10:25', 1500, 1420,
    'Tisztelt Országgyűlés! Mélyen tisztelt Képviselőtársaim! Korelnökként tisztelettel és szeretettel köszöntöm Önöket a Magyar Köztársaság 2010-ben megválasztott új Országgyűlésének alakuló ülésén. Történelmi pillanat részesei vagyunk. A magyar választópolgárok egyértelmű akaratot nyilvánítottak: a megújulás, az összefogás és a nemzeti felemelkedés útját jelölték ki számunkra. A felelősségünk óriási. Kívánom, hogy az elkövetkező négy esztendőben a nemzet javát és a polgárok boldogulását szolgálja minden döntésünk.',
    'https://www.parlament.hu/naplo39/001/n001_0001.htm'
),
(
    '2010_005_001', '2010', '2010_005', 1, 'Dr. Semjén Zsolt', 'semjen_zsolt_2010',
    '2010_KDNP', 'EXPOZE', 'A magyar állampolgárságról szóló törvény módosítása (T/2)', 'T/2',
    '11:15', '11:45', 1800, 1850,
    'Tisztelt Elnök Úr! Tisztelt Országgyűlés! Kilencven évvel a trianoni békediktátum után, és közel hat évvel a 2004. december 5-i gyászos népszavazás után eljött a történelmi igazságtétel pillanata. Az előttünk fekvő T/2. számú törvényjavaslat célja, hogy minden magyar ember, éljen bárhol a Kárpát-medencében vagy a nagyvilágban, egyszerűsített eljárással, méltósággal visszakaphassa magyar állampolgárságát. Nem elszakadást hirdetünk, hanem a nemzet közjogi egyesítését határok átlépése nélkül.',
    'https://www.parlament.hu/naplo39/005/n005_0120.htm'
),
(
    '2010_005_002', '2010', '2010_005', 2, 'Mesterházy Attila', 'mesterhazy_attila_2010',
    '2010_MSZP', 'VEZERSZONOKI', 'A magyar állampolgárságról szóló törvény módosítása (T/2)', 'T/2',
    '11:46', '12:05', 1140, 1280,
    'Tisztelt Országgyűlés! A Magyar Szocialista Párt frakciója vallja, hogy a határon túli magyarsággal való szolidaritás nem pártpolitikai kérdés. Ugyanakkor figyelmeztetnünk kell a kormányt a javaslat diplomáciai és szomszédságpolitikai következményeire. Nem szabad kockáztatni a kétoldalú kapcsolatokat Szlovákiával vagy Romániával, és elengedhetetlen, hogy a választójog kérdését gondosan és konszenzussal kezeljük. Támogatjuk a kulturális és nemzeti kötelékek erősítését, de óvunk a felelőtlen szimbolikus politizálástól.',
    'https://www.parlament.hu/naplo39/005/n005_0125.htm'
),
(
    '2010_005_003', '2010', '2010_005', 3, 'Dr. Schiffer András', 'schiffer_andras_2010',
    '2010_LMP', 'VEZERSZONOKI', 'A magyar állampolgárságról szóló törvény módosítása (T/2)', 'T/2',
    '12:06', '12:22', 960, 1100,
    'Elnök Úr, Képviselőtársaim! A Lehet Más a Politika képviselőcsoportja úgy látja: a magyar nemzet kulturális közösség, amelynek minden tagja számít. A kettős állampolgárság megadása erkölcsi kötelesség, amit támogatunk. Ugyanakkor nem nézhetjük tétlenül, hogy a kormányoldal ezt pártpolitikai célokra használja fel. Fontosnak tartjuk a határon túli magyar szervezetek valós gazdasági és oktatási támogatását is a szimbolikus gesztusokon túlmenően.',
    'https://www.parlament.hu/naplo39/005/n005_0130.htm'
),
(
    '2010_012_001', '2010', '2010_012', 1, 'Orbán Viktor', 'orban_viktor_2010',
    '2010_FIDESZ', 'NAPIREND_ELOTTI', 'A kormány első gazdasági akciótervének ismertetése', NULL,
    '13:00', '13:40', 2400, 2600,
    'Tisztelt Ház! Tisztelt Képviselőtársaim! Az új kormány megörökölte a devizahitelek pusztító válságát, az üres államkasszát és a gazdasági stagnálást. Ma bejelentem a Nemzeti Együttműködés Kormányának 29 pontos első gazdasági akciótervét. Megadóztatjuk a pénzügyi szektort, bevezetjük a bankadót, mert a válság terheit nem a családoknak és a kisvállalkozásoknak kell viselniük, hanem azoknak a multinacionális intézményeknek is, amelyek az elmúlt évtizedben extraprofitra tettek szert. Egykulcsos, családi adórendszert vezetünk be és megvédjük a bajba jutott devizahiteleseket a kilakoltatásoktól.',
    'https://www.parlament.hu/naplo39/012/n012_0250.htm'
);

-- FELSZÓLALÁSOK (2026)
INSERT OR REPLACE INTO speech (
    id, period_id, sitting_day_id, sequence_number, speaker_name, politician_id, 
    group_id, speech_type_code, agenda_item, bill_id, start_time, end_time, 
    duration_seconds, word_count, full_text, source_url
) VALUES
(
    '2026_001_001', '2026', '2026_001', 1, 'Magyar Péter', 'magyar_peter_2026',
    '2026_TISZA', 'NAPIREND_ELOTTI', 'A 2026-ban megalakult új Országgyűlés céljai és a rendszerszintű megújulás', NULL,
    '10:10', '10:45', 2100, 2450,
    'Tisztelt Országgyűlés! Magyar Polgártársaim! Egy új korszak hajnalán állunk ma itt ebben a teremben. A magyar nép a 2026. áprilisi választásokon egyértelműen és megkérdőjelezhetetlenül kimondta: véget ért a megosztottság, az intézményesített korrupció és az ország elszigeteltségének korszaka. Az új kormány első 100 napjának feladata a jogállam helyreállítása, a csatlakozás az Európai Ügyészséghez, az uniós források azonnali hazahozatala, valamint a romokban heverő egészségügy és oktatás azonnali mentőcsomagjának elindítása. Nem lesz bosszú, de lesz törvényes számonkérés és elszámoltatás minden egyes ellopott forintért.',
    'https://www.parlament.hu/naplo42/001/n001_0005.htm'
),
(
    '2026_001_002', '2026', '2026_001', 2, 'Kocsis Máté', 'kocsis_mate_2026',
    '2026_FIDESZ', 'VEZERSZONOKI', 'Frakcióálláspont az új Országgyűlés alakulásáról', NULL,
    '10:46', '11:10', 1440, 1600,
    'Tisztelt Ház! A Fidesz-KDNP képviselőcsoportja tudomásul veszi a választók akaratát, és a nemzeti szuverenitás rendíthetetlen védelmezőjeként ellenzékből folytatja a munkát. Figyelmeztetjük a most kormányra lépőket: nem engedjük, hogy a nemzeti függetlenséget Brüsszelnek árusítsák ki, hogy megnyissák a határokat a migráció előtt, vagy felszámolják a 16 év alatt felépített családtámogatási rendszert és rezsicsökkentést. Kemény, de határozott ellenzéke leszünk ennek a kormánynak.',
    'https://www.parlament.hu/naplo42/001/n001_0012.htm'
),
(
    '2026_005_001', '2026', '2026_005', 1, 'Dr. Kulja András', 'kulja_andras_2026',
    '2026_TISZA', 'EXPOZE', 'Egészségügyi sürgősségi stabilizációs csomag és szakdolgozói béremelés (T/4)', 'T/4',
    '11:00', '11:30', 1800, 1920,
    'Tisztelt Elnök Úr! Képviselőtársaim! Orvosként és most az egészségügyért felelős miniszterként fájdalmas látni, milyen állapotban vette át az ország az egészségügyi ellátórendszert. Több tízezer fős ápolóhiány, hónapokig tartó műtéti várólisták és eladósodott kórházak. A T/4. számú sürgősségi javaslat azonnali 25%-os béremelést biztosít az egészségügyi szakdolgozóknak és védőnőknek, és létrehozza az Országos Betegbiztonsági Alapot a kórházi adósságok rendezésére és a várólisták felezésére.',
    'https://www.parlament.hu/naplo42/005/n005_0045.htm'
),
(
    '2026_005_002', '2026', '2026_005', 2, 'Toroczkai László', 'toroczkai_laszlo_2026',
    '2026_MI_HAZANK', 'VEZERSZONOKI', 'Egészségügyi sürgősségi stabilizációs csomag és szakdolgozói béremelés (T/4)', 'T/4',
    '11:31', '11:50', 1140, 1250,
    'Tisztelt Országgyűlés! A Mi Hazánk Mozgalom támogatja a szakdolgozók bérének emelését, hiszen éveken át követeltük ezt a parlamentben. Ugyanakkor látnunk kell a források hátterét is: nem fogadjuk el, ha a béremelés fedezetéül külföldi hiteleket vesznek fel, vagy ha a gyógyszergyárak és magánbiztosítók érdekeit engedik érvényesülni a közegészségügy rovására.',
    'https://www.parlament.hu/naplo42/005/n005_0050.htm'
);

-- 4. KÉRDÉSEK ÉS INTERPELLÁCIÓK
INSERT OR REPLACE INTO question (
    id, period_id, document_number, question_type, title, submitter_name, 
    submitter_group_id, target_person, target_ministry, submission_date, 
    answered_date, question_text, answer_text, responder_name, 
    accepted_by_submitter, accepted_by_parliament, source_url
) VALUES
-- 2010 kérdések
(
    '2010_K_0001', '2010', 'K/45', 'interpellacio', 
    'Milyen lépéseket tesz a kormány a devizahitelesek védelmében?', 
    'Vona Gábor', '2010_JOBBIK', 'Orbán Viktor miniszterelnök', 'Miniszterelnökség', 
    '2010-06-01', '2010-06-07',
    'Tisztelt Miniszterelnök Úr! Családok százezrei sodródtak a csőd szélére a svájci frank alapú hitelek árfolyamrobbanása miatt. Követeljük a kilakoltatási moratórium azonnali meghosszabbítását és az árfolyam rögzítését!',
    'Tisztelt Képviselő Úr! A kormány azonnal elrendelte a kilakoltatási moratóriumot, bevezeti a bankadót, és nem engedi, hogy a bankok a veszteségeiket a magyar családokra hárítsák.',
    'Matolcsy György nemzetgazdasági miniszter', 0, 1,
    'https://www.parlament.hu/irom39/00045/00045.htm'
),
(
    '2010_K_0002', '2010', 'K/78', 'azonnali_kerdes',
    'Hogyan biztosítja a kormány a Sajó és a Hernád menti árvízkárok enyhítését?',
    'Lendvai Ildikó', '2010_MSZP', 'Pintér Sándor belügyminiszter', 'Belügyminisztérium',
    '2010-05-25', '2010-05-31',
    'A rendkívüli májusi esőzések miatt Borsodban és Észak-Magyarországon települések kerültek víz alá. Mikor kapják meg a károsult családok a rendkívüli segélyeket?',
    'A védekezésben a honvédség, a katasztrófavédelem és a rendőrség teljes létszámban részt vesz. A kárfelmérés folyamatos, a kormány azonnali kárenyhítési alapot nyitott meg.',
    'Dr. Pintér Sándor belügyminiszter', 1, 1,
    'https://www.parlament.hu/irom39/00078/00078.htm'
),
-- 2026 kérdések
(
    '2026_K_0001', '2026', 'K/12', 'azonnali_kerdes',
    'Mikor érkeznek meg a visszatartott uniós források a magyar gazdaságba?',
    'Orbán Viktor', '2026_FIDESZ', 'Magyar Péter miniszterelnök', 'Miniszterelnökség',
    '2026-05-18', '2026-05-20',
    'Tisztelt Miniszterelnök Úr! A választási kampányban azzal hitegették a választókat, hogy a kormányváltás után azonnal megérkeznek az uniós milliárdok. Mikor lát ebből egyetlen centet is a magyar költségvetés, és milyen szuverenitási árat fizetnek érte Brüsszelnek?',
    'Tisztelt Frakcióvezető Úr! Az Európai Ügyészséghez való csatlakozással és a független igazságszolgáltatás helyreállításával a zárolt források első 3 milliárd eurós részlete már a nyáron lehívhatóvá válik. A szuverenitást nem mi adjuk fel, Önök zálogosították el az országot az értelmetlen korrupciós küzdelmekkel.',
    'Magyar Péter miniszterelnök', 0, 1,
    'https://www.parlament.hu/irom42/00012/00012.htm'
),
(
    '2026_K_0002', '2026', 'I/35', 'interpellacio',
    'Milyen garanciák vannak a pedagógusok életpályamodelljének és a sztrájkjog helyreállítására?',
    'Dobrev Klára', '2026_DK', 'Oktatási miniszter', 'Oktatási Minisztérium',
    '2026-06-02', '2026-06-08',
    'Az oktatás válsága nem tűr halasztást. A státusztörvény eltörlése mellett konkrét garanciákat követelünk a pedagógusi autonómiára és a valós sztrájkjog visszaállítására!',
    'A kormány első törvénycsomagja hatályon kívül helyezte a korábbi kényszerítő rendelkezéseket, és a szakszervezetekkel közösen dolgozunk az új oktatási alaptörvényen.',
    'Oktatási államtitkár', 1, 1,
    'https://www.parlament.hu/irom42/00035/00035.htm'
);

-- 5. BESOROLÁSOK (SPEECH & QUESTION CLASSIFICATIONS)
INSERT OR REPLACE INTO speech_classification (
    speech_id, primary_topic_code, secondary_topic_code, confidence, summary, 
    extracted_keywords, classification_method
) VALUES
('2010_001_001', 'EGYEB_UGYRENDI', 'JOGALLAM_ALKOTMANY', 0.98, 'A 2010-es Országgyűlés alakuló ülésének korelnöki megnyitója a választói felhatalmazásról és a nemzeti megújulásról.', 'alakuló ülés, korelnök, nemzet, képviselők, felelősség', 'human_curated'),
('2010_005_001', 'NEMZETPOLITIKA', 'JOGALLAM_ALKOTMANY', 0.99, 'Kettős állampolgárságról szóló törvényjavaslat (T/2) előterjesztői expozéja a külhoni magyarság közjogi egyesítéséről.', 'kettős állampolgárság, Trianon, határon túli magyarság, honosítás', 'human_curated'),
('2010_005_002', 'NEMZETPOLITIKA', 'KULUGY_EU_HONVEDELM', 0.94, 'Az MSZP frakció álláspontja a kettős állampolgárságról, felhívva a figyelmet a jószomszédi kapcsolatok és a választójog kockázataira.', 'nemzeti szolidaritás, Szlovákia, Románia, diplomácia, választójog', 'human_curated'),
('2010_005_003', 'NEMZETPOLITIKA', 'SZOCIALPOLITIKA_CSALAD', 0.92, 'Az LMP vezérszónoki beszéde a kulturális nemzetegyesítés mellett és a politikai haszonszerzés ellen.', 'LMP, nemzet, kultúra, oktatás, határon túli támogatások', 'human_curated'),
('2010_012_001', 'MAKROGAZDASAG', 'SZOCIALPOLITIKA_CSALAD', 0.99, 'A kormány 29 pontos első gazdasági akcióterve: bankadó bevezetése, egykulcsos családi adózás és devizahiteles védelem.', 'akcióterv, bankadó, devizahitel, kilakoltatás, egykulcsos adó', 'human_curated'),
('2026_001_001', 'JOGALLAM_ALKOTMANY', 'KORRUPCIO_ELSZAMOLTATO', 0.98, 'Az új miniszterelnök alakuló ülésen elmondott programbeszéde az Európai Ügyészségről, uniós forrásokról és elszámoltatásról.', 'kormányváltás, jogállam, Európai Ügyészség, elszámoltatás, oktatás, egészségügy', 'human_curated'),
('2026_001_002', 'JOGALLAM_ALKOTMANY', 'KULUGY_EU_HONVEDELM', 0.96, 'A Fidesz vezérszónoka a nemzeti szuverenitás megvédéséről és a határozott ellenzéki szerepvállalásról.', 'szuverenitás, ellenzék, családtámogatás, rezsicsökkentés, migráció', 'human_curated'),
('2026_005_001', 'EGESZSEGUGY', 'SZOCIALPOLITIKA_CSALAD', 0.99, 'Egészségügyi sürgősségi törvényjavaslat az ápolói béremelésről és a kórházi várólisták lefaragásáról.', 'egészségügy, ápolók, béremelés, kórházi adósság, várólisták', 'human_curated'),
('2026_005_002', 'EGESZSEGUGY', 'MAKROGAZDASAG', 0.91, 'A Mi Hazánk vezérszónoki álláspontja a szakdolgozói béremelés támogatásáról és a külföldi hitelfelvételek elutasításáról.', 'egészségügy, bérkövetelés, hitelfelvétel, gyógyszeripar', 'human_curated');

INSERT OR REPLACE INTO question_classification (
    question_id, primary_topic_code, secondary_topic_code, confidence, summary,
    extracted_keywords, classification_method
) VALUES
('2010_K_0001', 'MAKROGAZDASAG', 'SZOCIALPOLITIKA_CSALAD', 0.97, 'Interpelláció a devizahitelesek megsegítéséről és a kilakoltatási moratóriumról.', 'devizahitel, frankhitel, kilakoltatás, bankadó', 'human_curated'),
('2010_K_0002', 'ENERGIA_KORNYEZET', 'SZOCIALPOLITIKA_CSALAD', 0.95, 'Azonnali kérdés az észak-magyarországi árvízkárok enyhítéséről és az azonnali állami segélyekről.', 'árvíz, Sajó, Hernád, kárenyhítés, katasztrófavédelem', 'human_curated'),
('2026_K_0001', 'KULUGY_EU_HONVEDELM', 'MAKROGAZDASAG', 0.98, 'Azonnali kérdés az Európai Ügyészséghez való csatlakozásról és az uniós források beérkezésének határidejéről.', 'uniós források, Európai Ügyészség, szuverenitás, költségvetés', 'human_curated'),
('2026_K_0002', 'OKTATAS_KUTATAS', 'SZOCIALPOLITIKA_CSALAD', 0.96, 'Interpelláció a pedagógus státusztörvény kivezetéséről és a pedagógusi sztrájkjog helyreállításáról.', 'oktatás, pedagógus, státusztörvény, sztrájkjog, szakszervezet', 'human_curated');
