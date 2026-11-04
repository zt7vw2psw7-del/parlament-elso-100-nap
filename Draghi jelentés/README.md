# Európai Parlamenti Draghi-Jelentés Adatbázis (2024–2026)

Ez a projekt egy átfogó, strukturált adatbázist és elemző eszközkészletet biztosít a Mario Draghi által készített **„The future of European competitiveness”** (Az európai versenyképesség jövője) című jelentés Európai Parlamenti (EP) lecsapódásáról.

---

## 📌 Háttér és időrend

* **Megjelenés dátuma:** 2024. szeptember 9.
* **Hivatalos plenáris bemutató az EP-ben:** 2024. szeptember 17. (Strasbourg)
* **Időtáv:** A 10. Európai Parlamenti ciklus kezdete (2024. nyár) óta eltelt ~2 év, amely során a jelentés az EU gazdasági, ipari és intézményi napirendjének alapdokumentumává vált.

---

## 🗄️ Az Adatbázis felépítése (`ep_draghi_database.db`)

Az SQLite adatbázis és a mellékelt CSV fájlok 5 fő területet fednek le:

1. **`official_acts`** (`ep_official_acts.csv`):
   * Hivatalos parlamenti eljárások, jogalkotási (COD) és saját kezdeményezésű (INI) jelentések, állásfoglalások (RSP).
   * Kiemelt eljárások:
     * `2024/2116(INI)`: A beruházások finanszírozása és a Tőkepiaci Unió (Markus Ferber - EPP)
     * `2025/2013(INI)`: A Draghi-jelentés intézményi aspektusai és a döntéshozatal reformja (Brando Benifei - S&D)
     * `2025/0555(COD)`: Európai Versenyképességi Alap rendelet (Christian Ehler - EPP)
     * `2024/2871(RSP)`: Állásfoglalás az autóipar válságáról és a CO2-flottacélokról
     * `2025/0821(COD)`: Első Bürokráciacsökkentési Omnibusz (25%-os tehercsökkentés KKV-knak)

2. **`plenary_debates`** (`ep_plenary_debates.csv`):
   * A Draghi-jelentéssel és a versenyképességi csomaggal foglalkozó kiemelt plenáris vitanapok részletei (2024. szept. 17., 2024. okt. 9., 2025. febr. 12., 2025. szept. 8., 2025. nov. 24., 2026. febr. 11.).

3. **`speeches`** (`ep_speeches.csv`):
   * Intézményi vezetők (Mario Draghi, Ursula von der Leyen, Orbán Viktor mint tanácsi elnök), frakcióvezetők (Manfred Weber, Iratxe García, Jordan Bardella, Nicola Procaccini, Valérie Hayer, Bas Eickhout), valamint magyar képviselők (Magyar Péter, Gál Kinga, Dobrev Klára, Dömötör Csaba) felszólalásai, beszédrészletei és politikai álláspontjai.

4. **`parliamentary_questions`** (`ep_parliamentary_questions.csv`):
   * Képviselői írásbeli (E-) és prioritásos (P-), valamint szóbeli (O-) kérdések az Európai Bizottsághoz a Draghi-jelentés ajánlásainak végrehajtásáról (közös adósság, energiaárak, KKV-adminisztráció, védelmi kötvények).

5. **`thematic_pillars`** (`ep_draghi_thematic_summary.csv`):
   * A jelentés 5 kulcspillére:
     * **PILLAR_1:** Termelékenység és Innovációs Szakadék (Tech, K+F, AI)
     * **PILLAR_2:** Dekarbonizáció és Energiaköltségek (Clean Industrial Deal, energiaárak)
     * **PILLAR_3:** Biztonság és Függőségek Csökkentése (Védelem, kritikus nyersanyagok)
     * **PILLAR_4:** Finanszírozás és Tőkepiaci Unió (Évi 800 Mrd € beruházás, közös hitel vita)
     * **PILLAR_5:** Intézményi Reform és Dereguláció (25% bürokráciacsökkentés, gyorsított eljárások)

---

## 🚀 Használati útmutató

### 1. Adatbázis lekérdezése terminálból (`query_database.py`)

A mellékelt parancssori eszközzel azonnal lekérdezhető az adatbázis:

```bash
# Általános statisztikai összegzés megjelenítése:
python3 query_database.py --stats

# Összes rögzített felszólalás listázása:
python3 query_database.py --speeches

# Felszólalások szűrése frakció szerint (pl. EPP, PfE, S&D, Renew):
python3 query_database.py --group EPP

# Szűrés konkrét Draghi-pillérre (pl. PILLAR_4 = Finanszírozás):
python3 query_database.py --pillar PILLAR_4

# Hivatalos jogalkotási és nem jogalkotási aktusok:
python3 query_database.py --acts

# Magyar képviselők megszólalásai és kérdései:
python3 query_database.py --hungarian

# Szabadszavas keresés az adatbázisban (pl. hitel, energia, autóipar):
python3 query_database.py --search "energia"
```

### 2. Exportálás és táblázatkezelők (Excel / Numbers)

Minden tábla elérhető `.csv` formátumban UTF-8 kódolással:
* `ep_official_acts.csv`
* `ep_plenary_debates.csv`
* `ep_speeches.csv`
* `ep_parliamentary_questions.csv`
* `ep_draghi_thematic_summary.csv`

Bármikor újragenerálható:
```bash
python3 build_database.py
```

### 3. Élő EP Open Data API frissítő (`ep_api_collector.py`)

A script közvetlenül kapcsolódik az Európai Parlament nyílt adat végpontjaihoz (`data.europarl.europa.eu/api/v2`):
```bash
python3 ep_api_collector.py --query "Draghi" --limit 50
```

---

## 📊 Főbb politikai törésvonalak az EP-ben

* **Közös adósságkibocsátás (Safe Assets / Eurobonds):** Az S&D, a Renew és a zöldek egy része támogatja; az EPP megosztott (inkább a magántőke bevonását és a CMU-t preferálja); a Patrióták (PfE) és az ECR élesen elutasítja.
* **Dereguláció és Green Deal:** Az EPP, az ECR és a PfE a bürokratikus jelentéstételi terhek (CSRD, taxonómia) azonnali lefaragását és a zöld tiltások (pl. 2035-ös belső égésű motorok tiltása) lazítását követeli; a zöldek és az S&D óvnak a szociális és környezetvédelmi normák lebontásától.
