#!/usr/bin/env python3
"""
Adatbázis inicializáló script: Második Orbán-kormány kormányülései (kormany.hu alapján)
Forrás:
- https://kormany.hu/nyilvanossagra-hozzuk-az-orban-kormanyok-uleseinek-osszefoglaloit
- https://kormany.hu/atlathato
- https://kormany.hu/kormanydontesek-20102026
"""

import sqlite3
import json
import csv
import os

DB_FILE = "kormanyulesek_2010.db"
JSON_FILE = "kormanyulesek_2010.json"
CSV_FILE = "kormanyulesek_2010.csv"

# A 2010-es időszak 31 kormányülésének adatai a kormany.hu hivatalos közzététele alapján
MEETINGS = [
    {
        "id": 1,
        "datum": "2010-05-31",
        "datum_szoveges": "2010. május 31.",
        "ules_szama": 1,
        "iktatoszam": "KIM/900/1/2010",
        "cim": "Összefoglaló a 2010. május 31-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/c/c0/c07/c071ae922afbd4f61c8b9be0d62572b.pdf",
        "idopont_tipus": "Rendes (alakuló utáni első munkanap)",
        "oldalszam": 2,
        "kiemelt_temak": "Kormányzati struktúra kialakítása, minisztériumok feladatkörei, államigazgatási átvilágítás, bürokráciacsökkentés",
        "dontesek_es_osszefoglalo": "A második Orbán-kormány 2010. május 29-i parlamenti eskütételét követő legelső hivatalos munkanapi kormányülése. Napirenden szerepelt az új minisztériumi struktúra (Közigazgatási és Igazságügyi Minisztérium, Nemzetgazdasági Minisztérium, Belügyminisztérium, Nemzeti Erőforrás Minisztérium, Nemzeti Fejlesztési Minisztérium, Vidékfejlesztési Minisztérium, Honvédelmi Minisztérium, Külügyminisztérium) feladat- és hatásköreinek elosztása, a kormány ügyrendjének megállapítása és az államháztartás átvilágításának elrendelése.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 2,
        "datum": "2010-06-05",
        "datum_szoveges": "2010. június 5.",
        "ules_szama": 2,
        "iktatoszam": "KIM/900/2/2010",
        "cim": "Összefoglaló a 2010. június 5-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/f/f0/f05/f05533ca8ed9b569b130503f7b7300d.pdf",
        "idopont_tipus": "Rendes / hétvégi rendkívüli felkészülés",
        "oldalszam": 2,
        "kiemelt_temak": "Államháztartási helyzetértékelés, Varga-bizottság jelentése, 2010-es költségvetési hiánycél",
        "dontesek_es_osszefoglalo": "A Varga Mihály államtitkár által vezetett tényfeltáró bizottság jelentésének megtárgyalása az államháztartás valós helyzetéről. Döntés született a 3,8%-os GDP-arányos hiánycél tartásáról és az ahhoz szükséges azonnali költségvetési beavatkozások, kiadáscsökkentések és zárolások elvi jóváhagyásáról.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 3,
        "datum": "2010-06-06",
        "datum_szoveges": "2010. június 6-7.",
        "ules_szama": 3,
        "iktatoszam": "KIM/900/3/2010",
        "cim": "Összefoglaló a 2010. június 6-7-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/2/2a/2ac/2accb5b33624560a63451adb0ecf486.pdf",
        "idopont_tipus": "Többnapos kihelyezett ülés",
        "oldalszam": 2,
        "kiemelt_temak": "Első Gazdasági Akcióterv előkészítése, bankadó koncepciója, családi adózás és egykulcsos SZJA",
        "dontesek_es_osszefoglalo": "Kétnapos stratégiai kormányülés a gazdasági intézkedési csomag kidolgozására. Döntés a pénzügyi szervezetek különadójának (bankadó) bevezetéséről, a kis- és középvállalkozások adóterheinek csökkentéséről, valamint az arányos egykulcsos személyi jövedelemadó és a családi adókedvezmény kiterjesztésének elvi alapjairól.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 4,
        "datum": "2010-06-09",
        "datum_szoveges": "2010. június 9.",
        "ules_szama": 4,
        "iktatoszam": "KIM/900/4/2010",
        "cim": "Összefoglaló a 2010. június 9-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/9/97/970/970b02c43e4ac3390c18bac9570abcf.pdf",
        "idopont_tipus": "Rendes",
        "oldalszam": 2,
        "kiemelt_temak": "29 pontos Első Gazdasági Akcióterv véglegesítése, állami bérplafon (2 millió Ft), 98%-os végkielégítési különadó",
        "dontesek_es_osszefoglalo": "A 29 pontból álló Első Gazdasági Akcióterv törvényjavaslatainak és kormányrendeleteinek jóváhagyása. Döntés született az állami szférában a 2 millió forintos havi bérplafon bevezetéséről, a kiugró mértékű állami végkielégítések 98%-os különadójáról, valamint a devizahitelek nyilvántartási tilalmáról.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 5,
        "datum": "2010-06-15",
        "datum_szoveges": "2010. június 15.",
        "ules_szama": 5,
        "iktatoszam": "KIM/900/5/2010",
        "cim": "Összefoglaló a 2010. június 15-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/7/77/779/7790028f3d64e84014e50a4d2ccb836.pdf",
        "idopont_tipus": "Rendes",
        "oldalszam": 2,
        "kiemelt_temak": "Észak-magyarországi árvízi védekezés, Borsod megyei kárenyhítés, újjáépítési kormánybiztosság",
        "dontesek_es_osszefoglalo": "A május-júniusi súlyos árvizek és belvizek által okozott károk felmérése és a helyreállítás azonnali feladatai (Borsod-Abaúj-Zemplén megye, Hernád és Sajó völgye). Döntés árvízi újjáépítési kormánybiztos kinevezéséről, a károsult családok gyorssegélyéről és a védművek megerősítésének finanszírozásáról.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 6,
        "datum": "2010-06-30",
        "datum_szoveges": "2010. június 30.",
        "ules_szama": 6,
        "iktatoszam": "KIM/900/6/2010",
        "cim": "Összefoglaló a 2010. június 30-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/9/98/98d/98dc5a5f9435a93fbdce7e42d380939.pdf",
        "idopont_tipus": "Rendes",
        "oldalszam": 2,
        "kiemelt_temak": "Társasági adó csökkentése (10%-os kulcs kkv-knak), költségvetési zárolások, államigazgatási létszámstop",
        "dontesek_es_osszefoglalo": "A társasági adó 10%-ra csökkentésének szabályai a vállalkozások 500 millió forintos eredményéig. Kormányzati megtakarítási intézkedések, minisztériumi dologi kiadások csökkentése és a közigazgatási létszámstop elrendelése a hiánycél garantálása érdekében.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 7,
        "datum": "2010-07-07",
        "datum_szoveges": "2010. július 7.",
        "ules_szama": 7,
        "iktatoszam": "KIM/900/7/2010",
        "cim": "Összefoglaló a 2010. július 7-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/7/7f/7fe/7fe7ff9eb27cdbc6a74d3527fde3bf1.pdf",
        "idopont_tipus": "Rendes",
        "oldalszam": 2,
        "kiemelt_temak": "Egyszerűsített honosítási eljárás végrehajtása, Nemzeti Együttműködés Nyilatkozata kifüggesztése",
        "dontesek_es_osszefoglalo": "A határon túli magyarok egyszerűsített honosításáról szóló törvény hatálybalépéséhez kapcsolódó kormányrendeletek és konzuli eljárási szabályok elfogadása (2011. január 1-jei indulással). A Nemzeti Együttműködés Nyilatkozata közhivatalokban történő kötelező elhelyezésének szabályozása.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 8,
        "datum": "2010-07-14",
        "datum_szoveges": "2010. július 14.",
        "ules_szama": 8,
        "iktatoszam": "KIM/900/8/2010",
        "cim": "Összefoglaló a 2010. július 14-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/4/45/457/4573a83885c24c3b5c4e0b00579dd1b.pdf",
        "idopont_tipus": "Rendes",
        "oldalszam": 2,
        "kiemelt_temak": "IMF/EU hitelmegállapodás felülvizsgálata, tárgyalási pozíciók, gazdaságpolitikai szuverenitás",
        "dontesek_es_osszefoglalo": "A Nemzetközi Valutaalappal (IMF) és az Európai Bizottsággal folytatandó felülvizsgálati tárgyalások pozíciójának rögzítése. A kormány kinyilvánította, hogy nem kér újabb IMF-készenléti hitelt, és nem hajt végre a nemzetközi szervezetek által javasolt lakossági megszorító intézkedéseket.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 9,
        "datum": "2010-07-20",
        "datum_szoveges": "2010. július 20.",
        "ules_szama": 9,
        "iktatoszam": "KIM/900/9/2010",
        "cim": "Összefoglaló a 2010. július 20-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/7/75/75a/75a115e6a987f2aabb6a7aff9a696f3.pdf",
        "idopont_tipus": "Rendes",
        "oldalszam": 2,
        "kiemelt_temak": "Kormányhivatalok felállítása (fővárosi és megyei szinten), Jó Állam koncepció, Magyary Zoltán Program",
        "dontesek_es_osszefoglalo": "A dekoncentrált államigazgatási szervek integrációját célzó fővárosi és megyei kormányhivatalok jogi és szervezeti kereteinek megtárgyalása (KIM előterjesztés). A Jó Állam és az egyablakos ügyintézés alapjainak lerakása.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 10,
        "datum": "2010-07-28",
        "datum_szoveges": "2010. július 28.",
        "ules_szama": 10,
        "iktatoszam": "KIM/900/10/2010",
        "cim": "Összefoglaló a 2010. július 28-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/3/3a/3a0/3a000b2d39f196426182966bcc424b3.pdf",
        "idopont_tipus": "Rendes",
        "oldalszam": 2,
        "kiemelt_temak": "IMF tárgyalások megszakadása utáni gazdasági stratégia, devizahitelesek védelme, kilakoltatási moratórium",
        "dontesek_es_osszefoglalo": "A 2010. július közepén megszakadt IMF-tárgyalásokat követő piaci reakciók értékelése és az önálló magyar gazdaságpolitika megerősítése. Döntés a lakáscélú devizahitelek felmondási és kilakoltatási moratóriumának meghosszabbításáról az árfolyamválság kezelésére.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 11,
        "datum": "2010-08-11",
        "datum_szoveges": "2010. augusztus 11.",
        "ules_szama": 11,
        "iktatoszam": "KIM/900/11/2010",
        "cim": "Összefoglaló a 2010. augusztus 11-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/7/75/75d/75d76a21d510a62fdbab51c7cef6178.pdf",
        "idopont_tipus": "Kiemelt ünnepi / rendes",
        "oldalszam": 6,
        "kiemelt_temak": "Schmitt Pál köztársasági elnök látogatása, Alkotmány őrzése és új Alaptörvény előkészítése",
        "dontesek_es_osszefoglalo": "A kormányülés kiemelt eseménye volt a hivatalba lépett Schmitt Pál köztársasági elnök látogatása. Orbán Viktor történelmi jelentőségű kijelentést tett az állami hatalmi ágak viszonyáról: „A köztársasági elnök nem ellensúly, hanem mind a köztársasági elnök, mind pedig a Kormány tagjai őrzik az Alkotmányt.” Az ülésen tárgyalták az új Alaptörvény kodifikációs folyamatának elindítását is.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 12,
        "datum": "2010-08-24",
        "datum_szoveges": "2010. augusztus 24.",
        "ules_szama": 12,
        "iktatoszam": "KIM/900/12/2010",
        "cim": "Összefoglaló a 2010. augusztus 24-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/0/08/085/085f5537c0b6a759381df5bb4ea37f2.pdf",
        "idopont_tipus": "Rendes",
        "oldalszam": 2,
        "kiemelt_temak": "Őszi törvényalkotási program, rendvédelem megerősítése, rendőrségi létszámbővítés",
        "dontesek_es_osszefoglalo": "Pintér Sándor belügyminiszter előterjesztése a közbiztonság megerősítésére: a rendőrség létszámának 3500 fős bővítése, a körzeti megbízotti hálózat visszaállítása és a rendvédelmi szervek felszerelésének korszerűsítése. Az őszi parlamenti ülésszak törvényjavaslatainak ütemezése.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 13,
        "datum": "2010-09-01",
        "datum_szoveges": "2010. szeptember 1.",
        "ules_szama": 13,
        "iktatoszam": "KIM/900/13/2010",
        "cim": "Összefoglaló a 2010. szeptember 1-jei kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/c/ce/ce1/ce12875df8daa1bef7988c0d6deea47.pdf",
        "idopont_tipus": "Rendes",
        "oldalszam": 2,
        "kiemelt_temak": "2011. évi költségvetés tervezési irányelvei, tanévkezdés és oktatáspolitikai átalakítás",
        "dontesek_es_osszefoglalo": "A 2011-es költségvetés makrogazdasági sarokszámainak rögzítése. A Réthelyi Miklós vezette NEFMI beszámolója az iskolakezdésről, valamint a tankötelezettségi korhatár és a köznevelési rendszer átalakításának előkészítő munkálatairól.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 14,
        "datum": "2010-09-08",
        "datum_szoveges": "2010. szeptember 8.",
        "ules_szama": 14,
        "iktatoszam": "KIM/900/14/2010",
        "cim": "Összefoglaló a 2010. szeptember 8-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/5/5a/5aa/5aae3af0d103cc1b794f6cdea10abd5.pdf",
        "idopont_tipus": "Rendes",
        "oldalszam": 2,
        "kiemelt_temak": "AUDI Hungaria győri gigaberuházás támogatása, iparfejlesztési prioritások",
        "dontesek_es_osszefoglalo": "Kormányzati döntés a győri Audi járműgyár 900 millió eurós kapacitásbővítéséhez nyújtandó egyedi kormánydöntésen (EKD) alapuló állami támogatásról, infrastrukturális fejlesztésekről és a kapcsolódó uniós bejelentési kötelezettségekről.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 15,
        "datum": "2010-09-22",
        "datum_szoveges": "2010. szeptember 22.",
        "ules_szama": 15,
        "iktatoszam": "KIM/900/15/2010",
        "cim": "Összefoglaló a 2010. szeptember 22-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/9/9e/9ef/9ef7980dc687283adad5a4d23df59d9.pdf",
        "idopont_tipus": "Rendes",
        "oldalszam": 2,
        "kiemelt_temak": "2011. évi magyar EU-elnökség felkészülése, Duna Stratégia, Roma Stratégia uniós szinten",
        "dontesek_es_osszefoglalo": "Martonyi János külügyminiszter előterjesztése a 2011 első felében esedékes magyar elnökség prioritásairól: az európai Duna Régió Stratégia elfogadása, a közös európai roma keretstratégia megalkotása, Horvátország uniós csatlakozási tárgyalásainak lezárása és az energiabiztonság.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 16,
        "datum": "2010-09-29",
        "datum_szoveges": "2010. szeptember 29.",
        "ules_szama": 16,
        "iktatoszam": "KIM/900/16/2010",
        "cim": "Összefoglaló a 2010. szeptember 29-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/7/7e/7ed/7edefd5ad074b23570789b7b86c5e89.pdf",
        "idopont_tipus": "Rendes",
        "oldalszam": 2,
        "kiemelt_temak": "Önkormányzati választási felkészülés, makrogazdasági pálya, 2011-es adótörvények",
        "dontesek_es_osszefoglalo": "Az őszi önkormányzati választásokat megelőző utolsó rendes kormányülés. Az adórendszer átalakítását (egyéni és társasági adózás) célzó törvénytervezetek szövegezésének előkészítése és a költségvetési hiánypálya vizsgálata.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 17,
        "datum": "2010-10-06",
        "datum_szoveges": "2010. október 6., délelőtt",
        "ules_szama": 17,
        "iktatoszam": "KIM/900/17/2010",
        "cim": "Összefoglaló a 2010. október 6., délelőtti kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/e/ea/ea0/ea09e65dc9550d8a368cdaad9d77672.pdf",
        "idopont_tipus": "Rendkívüli krízisülés (délelőtt)",
        "oldalszam": 2,
        "kiemelt_temak": "Ajkai vörösiszap-katasztrófa (2010. okt. 4.), veszélyhelyzet kihirdetése 3 megyére",
        "dontesek_es_osszefoglalo": "Rendkívüli kormányülés a magyar történelem legsúlyosabb ipari katasztrófája ügyében (MAL Zrt. ajkai timföldgyár X. zagykazettájának átszakadása). A kormány veszélyhelyzetet hirdetett Veszprém, Győr-Moson-Sopron és Vas megyére, elrendelte a katasztrófavédelem és a honvédség teljes mozgósítását, a Torna-patak és a Marcal mentesítését, valamint a lakosság segélyezését.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 18,
        "datum": "2010-10-06",
        "datum_szoveges": "2010. október 6., délután",
        "ules_szama": 18,
        "iktatoszam": "KIM/900/18/2010",
        "cim": "Összefoglaló a 2010. október 6., délutáni kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/d/d3/d36/d360beb0bc7796cc20161976c29e184.pdf",
        "idopont_tipus": "Rendkívüli krízisülés (délután)",
        "oldalszam": 2,
        "kiemelt_temak": "Vörösiszap-katasztrófa felelősségvizsgálat, MAL Zrt. vizsgálata, Duna védelme",
        "dontesek_es_osszefoglalo": "A délelőtti ülés közvetlen folytatása a legfrissebb terepi jelentések alapján. A kormány döntött a szennyeződés Dunába jutásának minden áron történő megakadályozásáról (gipszezés, savazás a Marcalon), a felelősség büntetőjogi és anyagi kivizsgálásáról, valamint Devecser és Kolontár lakóinak ideiglenes elhelyezéséről.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 19,
        "datum": "2010-10-10",
        "datum_szoveges": "2010. október 10.",
        "ules_szama": 19,
        "iktatoszam": "KIM/900/19/2010",
        "cim": "Összefoglaló a 2010. október 10-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/7/76/765/765177b36197e645be5ce637d921c07.pdf",
        "idopont_tipus": "Rendkívüli (vasárnap)",
        "oldalszam": 2,
        "kiemelt_temak": "Kolontár teljes kitelepítése, gátomlás veszélye, védőgát építése",
        "dontesek_es_osszefoglalo": "Vasárnapi rendkívüli ülés az ajkai zagytározó északi gátfalának megrepedése miatt. Kolontár teljes lakosságának azonnali evakuálása és Devecser felkészítése a kitelepítésre. Döntés született egy új védőgát rohamtempójú felépítéséről Kolontáron a honvédség és a katasztrófavédelem irányításával.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 20,
        "datum": "2010-10-13",
        "datum_szoveges": "2010. október 13.",
        "ules_szama": 20,
        "iktatoszam": "KIM/900/20/2010",
        "cim": "Összefoglaló a 2010. október 13-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/7/7b/7bc/7bc5bc34ca7520dd2db4fbf6c2c633a.pdf",
        "idopont_tipus": "Rendes",
        "oldalszam": 2,
        "kiemelt_temak": "Katasztrófavédelmi törvény sürgősségi módosítása, MAL Zrt. állami felügyelet alá vonása",
        "dontesek_es_osszefoglalo": "A katasztrófavédelmi törvény módosításának jóváhagyása, amely lehetővé tette az ipari katasztrófát okozó vállalat állami felügyelet alá vonását. Bakondi György kinevezése a MAL Zrt. élére kormánybiztosként, a cég vagyonának és működésének állami ellenőrzése a kártérítések és a biztonságos újraindítás érdekében.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 21,
        "datum": "2010-10-15",
        "datum_szoveges": "2010. október 15.",
        "ules_szama": 21,
        "iktatoszam": "KIM/900/21/2010",
        "cim": "Összefoglaló a 2010. október 15-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/b/b7/b75/b752770a7294f8cf9661c6e672bd8bc.pdf",
        "idopont_tipus": "Rendkívüli",
        "oldalszam": 2,
        "kiemelt_temak": "Második Gazdasági Akcióterv: ágazati válságadók, magánnyugdíjpénztári tagdíjak átmeneti átirányítása",
        "dontesek_es_osszefoglalo": "A Második Gazdasági Akcióterv bejelentése: ágazati különadók (válságadók) kivetése az energiaszektorra, a telekommunikációs vállalatokra és a kiskereskedelmi multicégekre évi 161 milliárd forint értékben. Döntés a magánnyugdíjpénztári befizetések 14 hónapos átirányításáról a költségvetésbe a hiány elkerülésére.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 22,
        "datum": "2010-10-27",
        "datum_szoveges": "2010. október 27.",
        "ules_szama": 22,
        "iktatoszam": "KIM/900/22/2010",
        "cim": "Összefoglaló a 2010. október 27-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/a/ac/ac0/ac0d1bae2ae71bb42cfb47ccadf998c.pdf",
        "idopont_tipus": "Rendes",
        "oldalszam": 2,
        "kiemelt_temak": "Alkotmánybíróság jogköreinek szűkítése, költségvetési tárgyú törvények felülvizsgálata",
        "dontesek_es_osszefoglalo": "Törvényjavaslat az Alkotmánybíróság hatáskörének korlátozására a 98%-os különadót megsemmisítő AB-döntést követően. A kormány kezdeményezte, hogy a költségvetési, adó-, illeték- és járuléktörvények ne legyenek megsemmisíthetőek alkotmánybírósági úton mindaddig, amíg az államadósság meghaladja a GDP 50%-át.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 23,
        "datum": "2010-11-03",
        "datum_szoveges": "2010. november 3.",
        "ules_szama": 23,
        "iktatoszam": "KIM/900/23/2010",
        "cim": "Összefoglaló a 2010. november 3-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/6/6b/6bd/6bd310ca46d0f465cbfab89aa68c791.pdf",
        "idopont_tipus": "Rendes",
        "oldalszam": 2,
        "kiemelt_temak": "Nyugdíjrendszer átfogó átalakítása (államosítási koncepció), Nyugdíjreform és Adósságcsökkentő Alap",
        "dontesek_es_osszefoglalo": "Matolcsy György előterjesztése a nyugdíjrendszer strukturális reformjáról: a kötelező magánnyugdíjpénztári rendszer kivezetéséről, az egyéni számlák állami pillérben történő megnyitásáról, és a Nyugdíjreform és Adósságcsökkentő Alap létrehozásáról az államadósság közvetlen csökkentésére a magánpénztári vagyonból.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 24,
        "datum": "2010-11-07",
        "datum_szoveges": "2010. november 7.",
        "ules_szama": 24,
        "iktatoszam": "KIM/900/24/2010",
        "cim": "Összefoglaló a 2010. november 7-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/7/70/707/7077421f68a807554f35b2fd4e94a4f.pdf",
        "idopont_tipus": "Rendkívüli (vasárnap)",
        "oldalszam": 2,
        "kiemelt_temak": "Alkotmánymódosítás véglegesítése, költségvetési felelősségi szabályok beépítése",
        "dontesek_es_osszefoglalo": "Rendkívüli hétvégi kormányülés az Alkotmánybíróság jogköreit szűkítő alkotmánymódosítás parlamenti zárószavazására történő felkészülésről és a költségvetési stabilitási garanciák kodifikálásáról.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 25,
        "datum": "2010-11-10",
        "datum_szoveges": "2010. november 10.",
        "ules_szama": 25,
        "iktatoszam": "KIM/900/25/2010",
        "cim": "Összefoglaló a 2010. november 10-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/a/a0/a04/a04531560247a214ddb3c3fbd8b0e08.pdf",
        "idopont_tipus": "Rendes",
        "oldalszam": 2,
        "kiemelt_temak": "2011. évi költségvetési törvényjavaslat benyújtása, 16%-os egykulcsos SZJA bevezetése",
        "dontesek_es_osszefoglalo": "A 2011. évi központi költségvetés törvénytervezetének végleges jóváhagyása. Az egykulcsos, 16%-os személyi jövedelemadó és a jelentősen kibővített, gyermekenként járó családi adókedvezmény beépítése a költségvetési fejezetekbe.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 26,
        "datum": "2010-11-17",
        "datum_szoveges": "2010. november 17.",
        "ules_szama": 26,
        "iktatoszam": "KIM/900/26/2010",
        "cim": "Összefoglaló a 2010. november 17-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/e/ed/edb/edb1bd9d557417f7b654cd102cef0b7.pdf",
        "idopont_tipus": "Rendes",
        "oldalszam": 2,
        "kiemelt_temak": "Balog Zoltán Nemzeti Társadalmi Felzárkózási és Romaügyi Stratégiája",
        "dontesek_es_osszefoglalo": "Balog Zoltán társadalmi felzárkózásért felelős államtitkár előterjesztése a romaügyi stratégiáról. A felzárkózási program oktatási, lakhatási, munkaerőpiaci és szociális pilléreinek jóváhagyása, mely egyúttal a 2011-es magyar EU-elnökség kiemelt európai dossziéjának alapját képezte.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 27,
        "datum": "2010-11-24",
        "datum_szoveges": "2010. november 24.",
        "ules_szama": 27,
        "iktatoszam": "KIM/900/27/2010",
        "cim": "Összefoglaló a 2010. november 24-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/0/00/00f/00fc55c365afb267c00bc946873aecf.pdf",
        "idopont_tipus": "Rendes",
        "oldalszam": 2,
        "kiemelt_temak": "Nyugdíjpénztári törvény véglegesítése (visszalépés az állami rendszerbe, államadósság-csökkentés)",
        "dontesek_es_osszefoglalo": "A nyugdíjpénztárakról szóló törvényjavaslat parlamenti benyújtásának jóváhagyása: a magánpénztári tagok visszalépésének szabályozása az állami TB-rendszerbe 2011. január 31-ig, valamint a közel 3000 milliárd forintos magánnyugdíjpénztári vagyon állami átvételének mechanizmusa.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 28,
        "datum": "2010-12-02",
        "datum_szoveges": "2010. december 2.",
        "ules_szama": 28,
        "iktatoszam": "KIM/900/28/2010",
        "cim": "Összefoglaló a 2010. december 2-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/6/6b/6bc/6bc942e846505650a9576e48334dc26.pdf",
        "idopont_tipus": "Rendes",
        "oldalszam": 2,
        "kiemelt_temak": "2011-es EU-elnökség brüsszeli kihelyezett ülése és menetrendje, elnökségi program",
        "dontesek_es_osszefoglalo": "A kormány jóváhagyta az Európai Unió Tanácsának 2011. január 1-jén kezdődő magyar soros elnökségének részletes munkatervét, a brüsszeli kihelyezett kormányülés forgatókönyvét és az Európai Bizottsággal való közös ülések feladatait.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 29,
        "datum": "2010-12-08",
        "datum_szoveges": "2010. december 8.",
        "ules_szama": 29,
        "iktatoszam": "KIM/900/29/2010",
        "cim": "Összefoglaló a 2010. december 8-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/0/07/07c/07ca9ec78f092b81548f76eba79fc29.pdf",
        "idopont_tipus": "Rendes",
        "oldalszam": 2,
        "kiemelt_temak": "Minimálbér és garantált bérminimum 2011. évi emelése (OÉT tárgyalások), 2011-es adótörvények",
        "dontesek_es_osszefoglalo": "A kötelező legkisebb munkabér (minimálbér) 78 000 forintra, a garantált bérminimum 94 000 forintra történő emeléséről szóló kormányrendelet elfogadása az Országos Érdekegyeztető Tanáccsal (OÉT) folytatott tárgyalások alapján.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 30,
        "datum": "2010-12-15",
        "datum_szoveges": "2010. december 15.",
        "ules_szama": 30,
        "iktatoszam": "KIM/900/30/2010",
        "cim": "Összefoglaló a 2010. december 15-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/a/a4/a4c/a4c4b867b6a4bd75fd110c319ca9e7a.pdf",
        "idopont_tipus": "Rendes",
        "oldalszam": 2,
        "kiemelt_temak": "2011-es felsőoktatási felvételi keretszámok, 2011. évi Népszámlálás, médiatörvény",
        "dontesek_es_osszefoglalo": "A 2011/2012-es tanévben államilag támogatott képzésben felvehető hallgatói létszámkeretek (keretszámok) meghatározása. A 2011. évi országos népszámlálás előkészítéséről szóló jogszabályok, valamint az új médiatörvény-tervezet véglegesítése.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    },
    {
        "id": 31,
        "datum": "2010-12-22",
        "datum_szoveges": "2010. december 22.",
        "ules_szama": 31,
        "iktatoszam": "KIM/900/31/2010",
        "cim": "Összefoglaló a 2010. december 22-i kormányülésről",
        "pdf_url": "https://cdn.kormany.hu/uploads/sheets/f/fb/fb7/fb7258b446c2d820bdb196f6470d3cb.pdf",
        "idopont_tipus": "Rendes / évzáró",
        "oldalszam": 2,
        "kiemelt_temak": "Vörösiszap Kármentő Bizottság (Soros György által delegált tag), 2010-es év értékelése, EU-elnökség rajtja",
        "dontesek_es_osszefoglalo": "Az év utolsó kormányülése. Döntés született arról, hogy a vörösiszap-katasztrófa kapcsán Soros György által felajánlott támogatások átlátható felhasználása érdekében a „Soros György által meghatározott személy szavazati joggal helyet kap a Kármentő Bizottságban”. A kormány értékelte a hivatalba lépés óta eltelt 7 hónap eredményeit és elindította az uniós elnökség operatív működését.",
        "statusz": "Hivatalosan közzétéve a kormany.hu-n"
    }
]

# Kormánytagok és tisztségek a második Orbán-kormányban (2010-2011)
MINISTERS = [
    ("Orbán Viktor", "Miniszterelnök", "Miniszterelnökség", "2010-05-29", "2014-06-06"),
    ("Semjén Zsolt", "Miniszterelnök-helyettes, tárca nélküli miniszter", "Nemzetpolitika, egyházügy, nemzetiségek", "2010-05-29", "2014-06-06"),
    ("Navracsics Tibor", "Közigazgatási és igazságügyi miniszter, miniszterelnök-helyettes", "Közigazgatási és Igazságügyi Minisztérium (KIM)", "2010-05-29", "2014-06-06"),
    ("Pintér Sándor", "Belügyminiszter", "Belügyminisztérium (BM)", "2010-05-29", "2014-06-06"),
    ("Matolcsy György", "Nemzetgazdasági miniszter", "Nemzetgazdasági Minisztérium (NGM)", "2010-05-29", "2013-03-03"),
    ("Martonyi János", "Külügyminiszter", "Külügyminisztérium (KÜM)", "2010-05-29", "2014-06-06"),
    ("Hende Csaba", "Honvédelmi miniszter", "Honvédelmi Minisztérium (HM)", "2010-05-29", "2014-06-06"),
    ("Réthelyi Miklós", "Nemzeti erőforrás miniszter", "Nemzeti Erőforrás Minisztérium (NEFMI)", "2010-05-29", "2012-05-13"),
    ("Fellegi Tamás", "Nemzeti fejlesztési miniszter", "Nemzeti Fejlesztési Minisztérium (NFM)", "2010-05-29", "2011-12-14"),
    ("Fazekas Sándor", "Vidékfejlesztési miniszter", "Vidékfejlesztési Minisztérium (VM)", "2010-05-29", "2014-06-06"),
    ("Varga Mihály", "Miniszterelnökséget vezető államtitkár", "Miniszterelnökség", "2010-05-29", "2012-06-01"),
    ("Szijjártó Péter", "Miniszterelnöki szóvivő", "Miniszterelnökség", "2010-05-29", "2012-06-01"),
    ("Balog Zoltán", "Társadalmi felzárkózásért felelős államtitkár", "KIM", "2010-06-02", "2012-05-13")
]

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Táblák létrehozása
    c.execute("""
    CREATE TABLE IF NOT EXISTS kormanyulesek (
        id INTEGER PRIMARY KEY,
        datum TEXT NOT NULL,
        datum_szoveges TEXT NOT NULL,
        ules_szama INTEGER NOT NULL,
        iktatoszam TEXT NOT NULL,
        cim TEXT NOT NULL,
        pdf_url TEXT NOT NULL,
        idopont_tipus TEXT NOT NULL,
        oldalszam INTEGER,
        kiemelt_temak TEXT,
        dontesek_es_osszefoglalo TEXT,
        statusz TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS kormanytagok (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nev TEXT NOT NULL,
        pozicio TEXT NOT NULL,
        tarca TEXT NOT NULL,
        hivatal_kezdete TEXT,
        hivatal_vege TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS hivatalos_forrasok (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        megnevezes TEXT NOT NULL,
        url TEXT NOT NULL,
        leiras TEXT
    )
    """)

    # Adatok feltöltése
    c.execute("DELETE FROM kormanyulesek")
    for m in MEETINGS:
        c.execute("""
        INSERT INTO kormanyulesek (id, datum, datum_szoveges, ules_szama, iktatoszam, cim, pdf_url, idopont_tipus, oldalszam, kiemelt_temak, dontesek_es_osszefoglalo, statusz)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            m["id"], m["datum"], m["datum_szoveges"], m["ules_szama"], m["iktatoszam"],
            m["cim"], m["pdf_url"], m["idopont_tipus"], m["oldalszam"],
            m["kiemelt_temak"], m["dontesek_es_osszefoglalo"], m["statusz"]
        ))

    c.execute("DELETE FROM kormanytagok")
    for min_item in MINISTERS:
        c.execute("""
        INSERT INTO kormanytagok (nev, pozicio, tarca, hivatal_kezdete, hivatal_vege)
        VALUES (?, ?, ?, ?, ?)
        """, min_item)

    c.execute("DELETE FROM hivatalos_forrasok")
    forrasok = [
        ("Kormányülések összefoglalóinak közzététele", "https://kormany.hu/nyilvanossagra-hozzuk-az-orban-kormanyok-uleseinek-osszefoglaloit", "Hivatalos kormányzati közlemény és PDF-tár a 2010-es ülésekről"),
        ("Átlátható kormányzás portál", "https://kormany.hu/atlathato", "Közérdekű adatok, archív döntések, feljelentések és vizsgálatok központi oldala"),
        ("Nem nyilvános kormányhatározatok 2010-2026", "https://kormany.hu/kormanydontesek-20102026", "A 2000-es határozatok évenkénti hivatalos PDF listái (köztük 2010 és 2011)"),
        ("Közigazgatási és Igazságügyi Minisztérium Iratkezelése", "KIM/900/.../2010", "A kormányülések jegyzőkönyveinek és emlékeztetőinek hivatalos iktatási jelzete")
    ]
    for forr in forrasok:
        c.execute("INSERT INTO hivatalos_forrasok (megnevezes, url, leiras) VALUES (?, ?, ?)", forr)

    conn.commit()
    conn.close()
    print(f"Adatbázis sikeresen létrehozva: {DB_FILE}")

def export_json():
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "kormany": "Második Orbán-kormány (2010-2014)",
            "idoszak": "2010. május 31. - 2010. december 22. (első közzétett fázis)",
            "forras": "kormany.hu (hivatalos kormányzati portál)",
            "ulesek_szama": len(MEETINGS),
            "kormanyulesek": MEETINGS,
            "kormanytagok": [{"nev": m[0], "pozicio": m[1], "tarca": m[2], "kezdete": m[3], "vege": m[4]} for m in MINISTERS]
        }, f, ensure_ascii=False, indent=2)
    print(f"JSON export sikeresen mentve: {JSON_FILE}")

def export_csv():
    fieldnames = ["id", "datum", "datum_szoveges", "ules_szama", "iktatoszam", "cim", "idopont_tipus", "oldalszam", "kiemelt_temak", "dontesek_es_osszefoglalo", "pdf_url", "statusz"]
    with open(CSV_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        for m in MEETINGS:
            writer.writerow(m)
    print(f"CSV export sikeresen mentve: {CSV_FILE}")

if __name__ == "__main__":
    init_db()
    export_json()
    export_csv()
