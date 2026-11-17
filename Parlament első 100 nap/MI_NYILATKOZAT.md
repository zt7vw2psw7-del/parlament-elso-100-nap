# MI NYILATKOZAT – MESTERSÉGES INTELLIGENCIA HASZNÁLATÁRÓL

**Készítő:** Bérczi Zoltán  
**Intézmény:** ELTE Bibó István Szakkollégium  
**Kurzus:** Politikatudományi Mesterséges Intelligencia kurzus (Kurzusvezető: Sebők Miklós)  
**Kutatási téma:** Parlamenti agendabeállítás az első 100 napban: 2010 (Fidesz–KDNP) és 2026 (TISZA) összehasonlító elemzése  
**Dátum:** 2026. november 17.

---

## 1. Nyilatkozat célja és alapelvei

Jelen nyilatkozat részletesen dokumentálja, hogy a kutatási feladat megvalósítása során a szerző milyen célból, milyen mértékben és milyen eszközökkel vett igénybe Mesterséges Intelligencia (MI / LLM) technológiát. A kutatás a tudományos integritás, az átláthatóság és a teljes reprodukálhatóság elveit követi, ahol az MI kutatási asszisztensként és programozási segédeszközként funkcionált emberi irányítás és felügyelet (*Human-in-the-loop*) mellett.

---

## 2. Alkalmazott MI eszközök és szoftverkörnyezet

* **MI platform és modell:** Google Antigravity (Gemini LLM modellek), interaktív fejlesztői agent környezet terminál- és fájlhozzáféréssel.
* **Programozási nyelv:** Python 3.9 (macOS platform).
* **Adatbázis-motor:** SQLite 3 (`parlament_100nap.db`, 41 MB méret).
* **Főbb Python könyvtárak:** `sqlite3`, `re`, `matplotlib`, `fpdf2`, `openpyxl`, `json`.

---

## 3. Az adatokkal végzett munka lépésről lépésre – MI közreműködéssel

### 1. lépés: Adatgyűjtés és scraper pipeline építése (Scraping)
* **Feladat:** Az Országgyűlés hivatalos honlapjáról (`parlament.hu`) a 2010-es és a 2026-os kormányváltást követő első 100 naptári nap plenáris jegyzőkönyveinek letöltése.
* **MI szerepe:** Web scraping Python scriptek generálása (`pipeline/scraper.py`, `pipeline/batch_importer.py`), amelyek lefedték a 2010-05-14 – 2010-08-22 és 2026-05-09 – 2026-08-17 közötti üléseket.
* **Eredmény:** 100%-os ülésszintű lefedettség (gap: 0), 4 826 nyers felszólalás rögzítése.

### 2. lépés: Adatmodellezés és normalizálás (ParlLawSpeech standard)
* **Feladat:** A strukturálatlan szövegek átültetése a nemzetközi ParlLawSpeech adatbázis-szabványba.
* **MI szerepe:** SQLite relációs séma megtervezése és létrehozása:
  - `speech` (felszólalások)
  - `politician` (492 képviselő adatai)
  - `parliamentary_group` (frakciók és kormánypárti/ellenzéki státusz)
  - `bill` (127 benyújtott törvényjavaslat adatai)
  - `sitting_day`, `period`, `speech_type`, `topic_category`.

### 3. lépés: Adattisztítás és szűrés (Data Validation & Filtering)
* **Feladat:** A tartalmi elemzés szempontjából zajos tételek kiszűrése.
* **MI szerepe és szabályai:**
  1. *Hosszúsági szűrés:* A 200 szó alatti bekiabálások, rövid technikai jelzések elhagyása (maradt: 3 873 felszólalás).
  2. *Procedurális elnöki szavaztatások kiszűrése:* Regex segítségével azonosítottuk és kizártuk az elnöki szavazási határozathirdetéseket és mandátumkezelési mondatokat (`is_procedural = 1`, 60 darab), így a tiszta elemzési korpusz **3 813 érdemi felszólalásra** állt be.

### 4. lépés: Szakpolitikai témaosztályozás (Comparative Agendas Project – CAP)
* **Feladat:** A felszólalások és törvényjavaslatok besorolása a CAP 21 fő témakategóriájába.
* **MI szerepe:**
  1. *Törvényjavaslat-kapcsolás:* Az irományszámot (`T/...`, `H/...`) tartalmazó napirendek automatikus összekötése az érintett törvénnyel, átörökítve a törvényjavaslat témáját.
  2. *Szóhatáros regex szabályrendszer:* 21 kategóriára kiterjedő minták (`\bgyes\b`, `\badó\b`, `\báfa\b` stb.), kizárva a részszavak (pl. „egyes”, „megyei”) téves találatait.

### 5. lépés: Tanári visszajelzések beépítése – A Roll-down torzítás korrekciója
* **Probléma (Sebők Miklós visszajelzése):** Korábban a nem kategorizálható felszólalások alapértelmezetten a CAP 20 (Kormányzati működés) kategóriába estek, mesterségesen 43,8%-ra növelve annak arányát.
* **Megoldás MI segítségével (`pipeline/reclassify_rolldown.py`):**
  1. Elkülönítettük a **valódi CAP 20** kulcsszavait (alkotmány, önkormányzat, közigazgatás stb. – 957 felszólalás).
  2. A roll-down miatt CAP 20-ba került rekordokat a teljes szövegen újraosztályoztuk: **620 felszólalás valós szakpolitikai kategóriát kapott** (legtöbb: CAP 13 Szociálpolitika, CAP 12 Jog, CAP 1 Makrogazdaság).
  3. A továbbra sem besorolható 119 felszólalás megkapta a `rolldown_unclassified` módszertani jelölést.
  4. Ennek hatására a CAP 20 aránya 43,8%-ról **27,6%-ra normalizálódott**.
  5. Az üres változókat (`target_era`, `excerpts`) egységesítettük `'N/A'` értékkel, a pártokat `party_code` szerint normalizáltuk.

### 6. lépés: Coder Agreement és megbízhatósági tesztelés (Validáció)
* **Feladat:** Intercoder reliability mérés emberi kódolás bevonásával.
* **MI szerepe:**
  1. Véletlenszerű 20 elemű minta generálása és exportálása Excel fájlba (`coder_agreement_20_felszólalás.xlsx`), kizárólag a kontextussal és szöveggel (a gép kódja nélkül, vaktesztként).
  2. A szerző által kitöltött kézi kódok beolvasása, összehasonlítása az algoritmikus kódokkal.
  3. Cohen-féle kappa ($\kappa$) számítás: a procedurális szűrés után **$\kappa = 0,611$** (közepes/jó egyezés; a mondatszintű pilot mintán $\kappa = 0,800$).
  4. Az eltérések tartalmi elemzése (kettős kódolási határesetek, pl. turizmus/árfolyam = CAP 1 vs. CAP 15).

### 7. lépés: Vizualizáció, dokumentáció és reprodukálható repó
* **MI szerepe:**
  - Három tudományos minőségű ábra generálása `matplotlib` segítségével.
  - Szigorúan 3 oldalas tudományos elemzés megszerkesztése PDF formátumban `fpdf2` segítségével (`parlament_100nap_elemzes_3oldal.pdf`).
  - Kódkönyv és opponensi útmutató frissítése.
  - Összesített leadandó csomag és ZIP archívum összeállítása az Asztalon.

---

## 4. Emberi közreműködés és felelősségvállalás (Human-in-the-Loop)

A kutatás minden fázisában a hallgató (Bérczi Zoltán) hozta meg a stratégiai és módszertani döntéseket:
1. **Feladatszabás és irányítás:** A kutatási fókusz (2010 vs. 2026 első 100 nap), az elemzési egység és a szűrési feltételek meghatározása.
2. **Kézi annotáció:** A 20 elemű coder-agreement mintán a független kézi kódolást a hallgató önállóan, az AI kódjainak ismerete nélkül végezte el.
3. **Kritikai felülvizsgálat:** A kurzusvezetői (Sebők Miklós) észrevételek értelmezése, a roll-down torzítás megszüntetésére és a procedurális esetek kizárására vonatkozó döntés meghozatala.
4. **Eredmények validálása:** A kapott politikatudományi trendek szakmai ellenőrzése és jóváhagyása.

---

*Budapest, 2026. november 17.*  
**Bérczi Zoltán s.k.**
