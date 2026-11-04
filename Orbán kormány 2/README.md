# Második Orbán-kormány Kormányüléseinek Adatbázisa (2010–2011)

Ez a projekt a **második Orbán-kormány első évének** elemzéséhez készült a Magyar Kormány hivatalos honlapján (**kormany.hu**) közzétett hivatalos kormányülési összefoglalók, jegyzőkönyvek és archív dokumentumok alapján.

---

## 📌 Hivatalos Források a kormany.hu-n

A kormány az **„Átlátható kormányzás”** kezdeményezés keretében hivatalosan megkezdte az Orbán-kormányok ülései összefoglalóinak nyilvánosságra hozatalát:
* **Hivatalos közzététel:** [kormany.hu/nyilvanossagra-hozzuk-az-orban-kormanyok-uleseinek-osszefoglaloit](https://kormany.hu/nyilvanossagra-hozzuk-az-orban-kormanyok-uleseinek-osszefoglaloit)
* **Központi átláthatósági aloldal:** [kormany.hu/atlathato](https://kormany.hu/atlathato)
* **Nem nyilvános (2000-es) kormányhatározatok 2010–2026:** [kormany.hu/kormanydontesek-20102026](https://kormany.hu/kormanydontesek-20102026)

### ⚠️ Az első 1 év (2010. május – 2011. május) közzétételi státusza:
1. **2010. május 31. – 2010. december 22. (1. fázis):**
   * A kormányzat a **teljes 2010-es évet közzétette** (összesen **31 kormányülés**).
   * Valamennyi üléshez elérhető a hivatalos, Közigazgatási és Igazságügyi Minisztérium (KIM) által nyilvántartott (`KIM/900/.../2010` iktatószámú) PDF dokumentum a `cdn.kormany.hu` szervereken.
2. **2011. január – 2011. május (2. fázis):**
   * A kormány hivatalos tájékoztatása szerint: *„Most elsőként a 2010-es kormányülések összefoglalóit tesszük közzé... A további éveket a nemzetbiztonsági átvilágítás után teszik közzé.”*
   * A 2011-es kormányülési emlékeztetők feloldása a nemzetbiztonsági átvilágítás függvényében folyamatos.
   * **Fontos:** A 2010-es ülések már teljes mértékben megalapozták a 2011-es év stratégiai döntéseit (2011. évi költségvetés, 2011-es EU-elnökség, magánnyugdíjpénztári államosítás, 16%-os egykulcsos SZJA, minimálbér-emelés, új Alaptörvény).

---

## 🗄️ Adatbázis Fájlok és Formátumok

A projektben az adatok több formátumban is rendelkezésre állnak az azonnali elemzéshez:

| Fájl | Formátum | Leírás |
| :--- | :--- | :--- |
| `kormanyulesek_2010.db` | **SQLite 3** | Strukturált relációs adatbázis lekérdezésekhez, BI és elemző eszközökhöz. |
| `kormanyulesek_2010.json` | **JSON** | Hierarchikus JSON adatformátum Python, JavaScript vagy webes feldolgozáshoz. |
| `kormanyulesek_2010.csv` | **CSV (UTF-8 BOM)** | Táblázatos formátum Excelhez, Google Sheets-hez vagy R/Pandas elemzésekhez. |
| `init_database.py` | **Python script** | Az adatbázis és az exportok újragenerálására szolgáló script. |
| `query.py` | **CLI eszköz** | Kényelmes terminálos kereső- és lekérdező eszköz. |

---

## 📊 Az SQLite Adatbázis Felépítése (`kormanyulesek_2010.db`)

### 1. `kormanyulesek` tábla
Tartalmazza mind a 31 közzétett kormányülés részletes adatait:
* `id` (INTEGER, PK): Sorszám (1–31)
* `datum` (TEXT): Ülés dátuma ISO formátumban (`YYYY-MM-DD`)
* `datum_szoveges` (TEXT): Magyar dátum formátum (pl. `2010. május 31.`)
* `ules_szama` (INTEGER): Kormányülések sorszáma a ciklusban
* `iktatoszam` (TEXT): Hivatalos minisztériumi iktatószám (`KIM/900/[1..31]/2010`)
* `cim` (TEXT): Hivatalos megnevezés a kormany.hu alapján
* `pdf_url` (TEXT): Közvetlen letöltési link a `cdn.kormany.hu` fájlra
* `idopont_tipus` (TEXT): Rendes / Rendkívüli / Krízisülés / Többnapos
* `oldalszam` (INTEGER): Eredeti archív dokumentum terjedelme
* `kiemelt_temak` (TEXT): Napirenden szereplő fő témák kulcsszavai
* `dontesek_es_osszefoglalo` (TEXT): Részletes háttér, kormányzati döntések és intézkedések
* `statusz` (TEXT): Hivatalos publikációs státusz

### 2. `kormanytagok` tábla
A második Orbán-kormány megalakuláskori miniszterei és államtitkárai (`nev`, `pozicio`, `tarca`, `hivatal_kezdete`, `hivatal_vege`).

### 3. `hivatalos_forrasok` tábla
A kormany.hu hivatalos hivatkozásai és archiválási leírásai.

---

## 🔍 Keresés és Használat a Terminálból (`query.py`)

A beépített parancssori eszközzel azonnal böngészhető és szűrhető az adatbázis:

### 1. Kormányülések listázása időrendben:
```bash
python3 query.py list
```

### 2. Keresés témák és döntések szerint:
```bash
# Magánnyugdíjpénztárakkal kapcsolatos döntések
python3 query.py search nyugdíj

# Vörösiszap-katasztrófával kapcsolatos rendkívüli ülések
python3 query.py search vörösiszap

# Adópolitika és gazdasági akciótervek
python3 query.py search adó

# EU-elnökség előkészületei
python3 query.py search elnökség
```

### 3. Egy konkrét ülés részletes adatlapja (ID vagy dátum alapján):
```bash
python3 query.py get 11
# vagy dátum szerint:
python3 query.py get 2010-12-22
```

### 4. Statisztikák megtekintése:
```bash
python3 query.py stats
```

### 5. Kormánytagok listája:
```bash
python3 query.py ministers
```

---

## 💡 SQL Lekérdezési Példák

Ha közvetlenül SQL-ből vagy Pythonból (pl. SQLite CLI, DBeaver, sqlite3 modul) szeretnéd elemezni az adatbázist:

```python
import sqlite3

conn = sqlite3.connect("kormanyulesek_2010.db")
c = conn.cursor()

# 1. Rendkívüli ülések listája
c.execute("SELECT datum, cim, kiemelt_temak FROM kormanyulesek WHERE idopont_tipus LIKE '%Rendkívüli%'")
for row in c.fetchall():
    print(row)

# 2. Havi ülésszám statisztika
c.execute("SELECT strftime('%Y-%m', datum) AS honap, count(*) FROM kormanyulesek GROUP BY honap")
print(c.fetchall())

conn.close()
```

---

## 📅 A 2010-es Év Kiemelt Kormányzati Döntései (Kronológia)

* **2010. május 31. (1. ülés):** Hivatalos munkakezdés, új minisztériumi struktúra és hatáskörök felosztása.
* **2010. június 6–7. és 9. (3–4. ülés):** 29 pontos Első Gazdasági Akcióterv: bankadó bevezetése, állami szféra 2 millió Ft-os bérplafonja, 98%-os végkielégítési különadó.
* **2010. július 14. (8. ülés):** Az IMF-fel való szakítás előkészítése, a szuverén gazdaságpolitika rögzítése.
* **2010. augusztus 11. (11. ülés):** Schmitt Pál látogatása; Orbán Viktor tézise: „a köztársasági elnök nem ellensúly, hanem mindkét fél az Alkotmányt őrzi”.
* **2010. szeptember 8. (14. ülés):** Audi Hungaria győri gigaberuházás állami támogatási szerződése.
* **2010. október 6–10. (17–19. ülés):** Az ajkai vörösiszap-katasztrófa azonnali kríziskezelése, veszélyhelyzet kihirdetése, Kolontár kiürítése, védőgát építése.
* **2010. október 13. (20. ülés):** A MAL Zrt. állami felügyelet alá vonása, Bakondi György kinevezése.
* **2010. október 15. (21. ülés):** Második Gazdasági Akcióterv: ágazati válságadók (energia, telekom, kiskereskedelem) és a magánnyugdíjpénztári tagdíjak átirányítása.
* **2010. október 27. (22. ülés):** Alkotmánybíróság jogköreinek szűkítése a költségvetési és adótörvények kapcsán.
* **2010. november 3. és 24. (23. és 27. ülés):** A magánnyugdíjpénztári vagyon államosítása / visszaléptetés az állami pillérbe, a Nyugdíjreform és Adósságcsökkentő Alap felállítása.
* **2010. november 10. (25. ülés):** 2011. évi költségvetés, 16%-os egykulcsos SZJA és kibővített családi adókedvezmény.
* **2010. november 17. (26. ülés):** Balog Zoltán Nemzeti Roma Stratégiájának elfogadása.
* **2010. december 8. (29. ülés):** 2011-es minimálbér (78 000 Ft) és bérminimum megállapítása.
* **2010. december 22. (31. ülés):** Kármentő Bizottsági döntés Soros György által delegált szavazati jogú tag bevonásáról a felajánlott adományokhoz; 2011-es uniós elnökség indítása.
