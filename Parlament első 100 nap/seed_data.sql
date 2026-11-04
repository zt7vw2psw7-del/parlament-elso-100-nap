-- =====================================================================
-- KEZDŐADATOK (TÖRZSDATOK: KORSZAKOK, FRAKCIÓK, TÍPUSOK, TÉMATILISTÁK)
-- =====================================================================

-- 1. KORSZAKOK
INSERT OR REPLACE INTO period (id, name, inaugural_date, end_date, description) VALUES
('2010', '2010-es kormányváltás utáni 100 nap', '2010-05-14', '2010-08-22', 'A 2010. május 14-i parlamenti alakuló üléstől számított 100 napos időszak (tavaszi és nyári rendkívüli ülésszak).'),
('2026', '2026-os kormányváltás utáni 100 nap', '2026-05-09', '2026-08-17', 'A 2026. május 9-i parlamenti alakuló üléstől számított 100 napos időszak (tavaszi és nyári rendkívüli ülésszak).');

-- 2. KÉPVISELŐCSOPORTOK / FRAKCIÓK (2010)
INSERT OR REPLACE INTO parliamentary_group (id, period_id, code, name, governing_status, seats, color_hex) VALUES
('2010_FIDESZ', '2010', 'FIDESZ', 'Fidesz - Magyar Polgári Szövetség', 'kormany', 227, '#FF6A00'),
('2010_KDNP', '2010', 'KDNP', 'Kereszténydemokrata Néppárt', 'kormany', 36, '#004B87'),
('2010_MSZP', '2010', 'MSZP', 'Magyar Szocialista Párt', 'ellenzek', 59, '#DC143C'),
('2010_JOBBIK', '2010', 'JOBBIK', 'Jobbik Magyarországért Mozgalom', 'ellenzek', 47, '#008080'),
('2010_LMP', '2010', 'LMP', 'Lehet Más a Politika', 'ellenzek', 16, '#7AC142'),
('2010_FGT', '2010', 'FÜGGETLEN', 'Független képviselők', 'semleges', 1, '#888888');

-- KÉPVISELŐCSOPORTOK / FRAKCIÓK (2026)
INSERT OR REPLACE INTO parliamentary_group (id, period_id, code, name, governing_status, seats, color_hex) VALUES
('2026_TISZA', '2026', 'TISZA', 'Tisztelet és Szabadság Párt', 'kormany', 106, '#0B3B60'),
('2026_FIDESZ', '2026', 'FIDESZ', 'Fidesz - Magyar Polgári Szövetség', 'ellenzek', 65, '#FF6A00'),
('2026_KDNP', '2026', 'KDNP', 'Kereszténydemokrata Néppárt', 'ellenzek', 12, '#004B87'),
('2026_MI_HAZANK', '2026', 'MI_HAZANK', 'Mi Hazánk Mozgalom', 'ellenzek', 9, '#2E6F40'),
('2026_DK', '2026', 'DK', 'Demokratikus Koalíció', 'ellenzek', 6, '#0088CC'),
('2026_FGT', '2026', 'FÜGGETLEN', 'Független képviselők', 'semleges', 1, '#888888');

-- 3. FELSZÓLALÁS TÍPUSOK
INSERT OR REPLACE INTO speech_type (code, name, description) VALUES
('NAPIREND_ELOTTI', 'Napirend előtti felszólalás', 'Az ülésnap elején elhangzó, kiemelt politikai jelentőségű felszólalás.'),
('EXPOZE', 'Előterjesztői expozé', 'A törvényjavaslatot vagy határozati javaslatot beterjesztő miniszter vagy képviselő bevezető beszéde.'),
('VEZERSZONOKI', 'Vezérszónoki felszólalás', 'Az egyes képviselőcsoportok kijelölt vezérszónokainak hivatalos pártálláspontot kifejtő beszéde.'),
('HOZZASZOLAS', 'Általános és részletes vita felszólalás', 'Egyéni és frakció-hozzászólás a napirendi pont érdemi vitájában.'),
('KETPERCES', 'Kétperces felszólalás', 'Rövid, közvetlen reflexió az előző felszólalásra.'),
('UGYRENDI', 'Ügyrendi felszólalás', 'Az Országgyűlés működésének, tárgyalási rendjének szabályaival kapcsolatos indítvány.'),
('ZARSZO', 'Előterjesztői zárszó', 'A vita lezárásakor az előterjesztő összefoglaló beszéde a szavazás előtt.'),
('INTERPELLACIO_SZOBELI', 'Interpelláció elmondása', 'A képviselő által a miniszternek vagy miniszterelnöknek címzett számonkérés szóbeli kifejtése.'),
('AZONNALI_KERDES', 'Azonnali kérdés elmondása', 'Közvetlen, rövid kérdés a kormány tagjaihoz.'),
('KORMANYZATI_VALASZ', 'Kormányzati válasz / viszontválasz', 'Miniszteri vagy államtitkári válasz az interpellációra, azonnali kérdésre vagy felszólalásra.');

-- 4. TÉMAKATEGÓRIÁK (Standard politikatudományi / CAP-kompatibilis nómenklatúra)
INSERT OR REPLACE INTO topic_category (code, name, description, keywords) VALUES
('MAKROGAZDASAG', 'Makrogazdaság és Pénzügyek', 'Költségvetés, infláció, adórendszer, gazdasági növekedés, államadósság, devizahitelek, bankadó.', 'adó, áfa, jövedelemadó, költségvetés, hiány, államadósság, infláció, bankadó, forint, gazdasági csomag'),
('JOGALLAM_ALKOTMANY', 'Alkotmányosság, Jogállam és Igazságszolgáltatás', 'Alkotmánymódosítások, Alaptörvény, bíróságok, ügyészség, választójogi törvény, jogállamiság, fékek és egyensúlyok.', 'alkotmány, alkotmánymódosítás, bíróság, ügyészség, választási törvény, jogállam, igazságügy, eljárásrend'),
('NEMZETPOLITIKA', 'Nemzetpolitika és Határon túli magyarság', 'Kettős állampolgárság, Trianon-emléknap, határon túli magyar közösségek támogatása, autonómia.', 'kettős állampolgárság, határon túli, trianon, nemzeti összetartozás, határon túli magyarok, autonómia'),
('SZOCIALPOLITIKA_CSALAD', 'Szociálpolitika, Család és Munkaerőpiac', 'Családtámogatások, nyugdíjak, segélyezés, közmunka, foglalkoztatottság, gyermekvállalás ösztönzése.', 'családi pótlék, gyes, gyed, nyugdíj, munkanélküliség, szociális segély, közmunka, munkabér, minimálbér'),
('EGESZSEGUGY', 'Egészségügy és Betegellátás', 'Kórházak helyzete, orvosok és ápolók bérezése, várólisták, gyógyszerellátás, egészségbiztosítás.', 'kórház, orvos, ápoló, várólista, betegellátás, oep, társadalombiztosítás, gyógyszer, egészségügy'),
('OKTATAS_KUTATAS', 'Oktatás, Felsőoktatás és Kutatás', 'Közoktatás, egyetemi autonómia, pedagógusbérek, szakképzés, MTA, kutatás-fejlesztés.', 'iskola, egyetem, tanár, pedagógus, diák, felsőoktatás, tankötelezettség, szakképzés, oktatás, tananyag'),
('KORRUPCIO_ELSZAMOLTATO', 'Korrupció, Elszámoltatás és Átláthatóság', 'Kormányváltás utáni elszámoltatás, közpénzek ellenőrzése, közbeszerzések, vagyonnyilatkozatok, korrupcióellenes intézkedések.', 'elszámoltatás, vizsgálóbizottság, visszaélés, korrupció, közbeszerzés, közpénz, vagyonosodás, átláthatóság'),
('ENERGIA_KORNYEZET', 'Energia, Klímapolitika és Környezetvédelem', 'Energiabiztonság, áram- és gázárak, rezsicsökkentés / piaci árak, megújuló energia, környezetvédelem, árvízvédelem.', 'energia, földgáz, villamosenergia, paksi atomerőmű, megújuló, árvíz, gátak, zöld, környezetvédelem, rezsi'),
('KULUGY_EU_HONVEDELM', 'Külügy, Európai Unió és Biztonságpolitika', 'EU-s kapcsolatok, uniós források, NATO, nemzetközi szerződések, honvédelem, haderőfejlesztés.', 'európai unió, brüsszel, eu támogatás, nato, külpolitika, nagykövet, diplomácia, honvédség, biztonság'),
('MEDIA_KOMMUNIKACIO', 'Média, Tájékoztatás és Digitális Ügyek', 'Közmédia átalakítása, Médiatanács, sajtószabadság, telekommunikáció, digitalizáció.', 'média, sajtószabadság, közmédia, mti, médiatörvény, ortt, hírközlés, internet, tájékoztatás'),
('KOZIGAZGATAS_ONKORMANYZAT', 'Közigazgatás és Önkormányzatok', 'Közigazgatási reform, minisztériumok átszervezése, kormányhivatalok, helyi önkormányzatok jogkörei és finanszírozása.', 'önkormányzat, polgármester, minisztérium, közigazgatás, bürokrácia, járás, kormányhivatal, közszolgálat'),
('MEZOGAZDASAG_VIDEK', 'Agrárium és Vidékfejlesztés', 'Földbérlet, mezőgazdasági támogatások, gazdák helyzete, élelmiszerbiztonság, természeti károk.', 'mezőgazdaság, gazda, földbérlet, földügyek, agrártámogatás, vetőmag, termés, aszály, vidékfejlesztés'),
('EGYEB_UGYRENDI', 'Parlamenti Működés és Protokoll', 'Ülésrend, jegyzők, eskütevés, bizottsági helyek elosztása, ceremoniális megemlékezések.', 'eskü, napirend, bizottság megalakulása, tisztségviselő, korelnök, jegyzőkönyv, szavazatszámlálás');
