---
name: election-tracker
description: >-
  Builds, scaffolds, and maintains data-driven election tracking dashboards and portals
  for any country (e.g. USA, Germany, UK, France, Hungary, Poland, etc.).
  Generates interactive parliamentary hemicycle charts, seat distribution bars,
  reputable poll aggregators with reliability grades, daily/weekly trending keyword analyzers,
  key leader monitors (e.g. Trump/Scholz/Starmer/Orbán), and automated daily data updater pipelines.
---

# 🗳️ Election Tracker Skill (Nemzetközi Választási Portál Építő)

Ez a skill megtanítja az ágensnek, hogyan építsen fel és tartson karban **bármely országra** egy professzionális, megbízható és interaktív választási figyelő weboldalt.

---

## 📌 Mikor használd ezt a skillt?

Aktiváld ezt a skillt, amikor a felhasználó:
- Egy adott ország választásaihoz (pl. Németország, Nagy-Britannia, Magyarország, Franciaország, Lengyelország, stb.) szeretne információs portált vagy grafikont készíteni.
- Parlamenti mandátumbecslést, félköríves üléstermi (Hemicycle) ábrát vagy többségi mérleget kér.
- Közvélemény-kutatási aggregátort igényel szigorú megbízhatósági szűrőkkel (A+, A besorolás).
- Napi vagy heti média-kulcsszóelemzést, illetve kulcspolitikus-figyelőt (pl. miniszterelnök/elnök nyilatkozatok, tényellenőrzés) szeretne hozzáadni.

---

## 🏛️ Parlamenti Adatbázis & Paraméterek

Mielőtt elkezded a fejlesztést, nézd meg a [country_parliaments.md](./references/country_parliaments.md) dokumentumot a pontos mandátumszámokért és küszöbértékekért:

| Ország | Törvényhozás | Összes Mandátum | Többségi Küszöb | Megjegyzés |
| :--- | :--- | :--- | :--- | :--- |
| **USA** | Szenátus / Képviselőház | 100 / 435 | 51 / 218 | Kétkamarás, félidős és elnökválasztás |
| **Németország** | Bundestag | 630 | 316 | 5%-os bejutási küszöb |
| **Egyesült Királyság** | House of Commons | 650 | 326 | Westminsteri egyéni körzetek |
| **Magyarország** | Országgyűlés | 199 | 100 (133 kétharmad) | Vegyes rendszer (106 egyéni + 93 lista) |
| **Franciaország** | Assemblée Nationale | 577 | 289 | Kétfordulós rendszer |
| **Lengyelország** | Sejm | 460 | 231 | D'Hondt arányos rendszer |

---

## 🚀 Lépésről-lépésre Eljárásrend

### 1. Lépés: Automatikus Projektváz Generálás
Használd a mellékelt generáló szkriptet egy új projekt könyvtár felépítéséhez:
```bash
python3 .agent/skills/election-tracker/scripts/scaffold_country.py --country <orszag_kod> --output <cel_mappa>
```
*Támogatott kódok:* `germany`, `uk`, `hungary`, `france` vagy egyedi konfiguráció.

### 2. Lépés: Hiteles Források Beállítása
Konzultálj a [trusted_sources_guide.md](./references/trusted_sources_guide.md) útmutatóval:
- Csak Tier-1 hírügynökségeket és Pulitzer- vagy nemzetközileg elismert szerkesztőségeket használj.
- Minden kutatóintézet mellé tegyél minőségi jelvényt: **A+**, **A**, **A-**, **B+**.
- Zárj ki minden nem reprezentatív vagy pártfinanszírozott belső felmérést!

### 3. Lépés: Interaktív Grafikai Elemek (Hemicycle & Mérleg)
A portálnak tartalmaznia kell:
1. **Matematikai Félkör (Hemicycle SVG):**
   - Koncentrikus íveken elhelyezett pontok (székek).
   - Rákattintva vagy rámutatva az infografika azonnal jelenítse meg az adott mandátum adatait (képviselő/jelölt neve, pártja, esélyessége).
2. **Többségi Mérleg (Balance Bar):**
   - Vízszintes sáv a biztos, valószínű és csatatér székek arányaival és a többségi vonallal.

### 4. Lépés: Hírelemzés és Kulcsszófigyelő
A hírfolyamot három szintre oszd:
- **A Nap Legfontosabb Eseményei:** a média által legtöbbet említett kulcsszavak felhője (mentions számlálóval) és a nap kiemelt sztorija.
- **A Hét Összefoglalója:** a 4 legfontosabb stratégiai tanulság és szerkesztőségi mélyelemzés.
- **Időrendi Hírfolyam:** megbízható cikkek listája közvetlen forráslinkekkel.

### 5. Lépés: Vezető Politikus Figyelő (Leader Tracker)
Hozd létre az adott ország kulcspolitikusának figyelőjét (pl. Németország: Kancellárfigyelő, Magyarország: Miniszterelnök-jelölt Figyelő):
- Hivatalos és közösségi bejegyzések idővonala.
- **Független Tényellenőrzés (Fact-Check):** minden vitatott állítás mellé ellenőrzött kontextus.
- Kampányállomások és nagygyűlések naptára.
- Népszerűségi mutatók (Approval Rating).

### 6. Lépés: Napi Automata Frissítés Beállítása
- Hozz létre egy `updater.py` szkriptet és egy helyi kiszolgálót (`server.py`).
- Az Antigravity `schedule` eszközével állíts be egy állandó napi időzítőt:
  ```
  CronExpression: "0 8 * * *"
  IsDaemon: true
  Prompt: "Futtasd le a napi frissítést az [Ország] választási portálhoz..."
  ```
