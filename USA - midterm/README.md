# 🇺🇸 USA Időközi Választások 2026 Figyelő Portál

> **Megbízható hírek, közvélemény-kutatások és mandátumbecslések az amerikai Képviselőházhoz (Alsóház) és Szenátushoz (Felsőház) kapcsolódóan.**

---

## 📌 Áttekintés

Ez a modern, reszponzív webalkalmazás kifejezetten a 2026. november 3-i amerikai félidős (midterm) választások nyomon követésére készült. Kiszűri a félrevezető és kattintásvadász híreket, és **kizárólag a legmagasabb minősítésű közvélemény-kutatók** és a **vezető független nemzetközi hírügynökségek** adatait jeleníti meg.

---

## ✨ Főbb Funkciók

### 1. 🏛️ Grafikus Mandátumbecslések és Ábrák
- **Felsőház (Szenátus - 100 mandátum):**
  - **Interaktív félköríves parlament (Hemicycle):** 100 egyedi szék megjelenítése pártállás és esélyesség szerint színezve (Demokrata kék, Csatatér sárga, Republikánus piros).
  - Székre mutatva megjelenik az adott mandátum kategóriája.
  - 51 fős többségi küszöbvonal.
  - 7 kiemelt csatatér állam mélyelemzése (Texas, Michigan, Ohio, Iowa, Maine, Észak-Karolina, Alaszka) jelöltekkel és felmérési átlagokkal.
- **Alsóház (Képviselőház - 435 mandátum):**
  - Szegmentált mandátummérleg a 218 fős többségi választóvonallal.
  - Várható mandátumsávok (Demokrata: 224–235, Republikánus: 200–211).
  - Többségszerzési valószínűségi mutatók (Win Probability Gauge).
- **Országos Szavazatarány (Generic Congressional Ballot):**
  - Súlyozott átlag (Demokrata: 50.6% vs. Republikánus: 42.3%, +8.3 Dem előny).

### 2. 📈 Szűrhető Közvélemény-kutatási Adatbázis
- Valós idejű szabadszavas kereső (államra, jelöltre, kutatóra).
- Kategóriaszűrők: *Minden felmérés*, *Országos*, *Szenátus*, *Képviselőház*.
- **Megbízhatósági jelvények:** Minden kutató mellett ott a szakmai minősítés (pl. **A+**, **A**, **A-**, **B+**).
- Részletes adatok: mintanagyság, szavazótípus (RV/LV), hibahatár, pártarányok, közvetlen forráshivatkozás.

### 3. 📰 Hiteles Hírfolyam & Média Elemzések
- **🔥 A Nap Fontos Eseményei (Országos Médiafigyelés):**
  - **Kulcsszó- és témaelemzés:** a vezető amerikai hírügynökségek (AP, Reuters, NYT, WSJ, Politico) által legtöbbet említett kifejezések (pl. *#Trump Kampánykörút*, *#Infláció & Üzemanyagárak*, *#Fehér Ház vs. Média Per*, *#Szenátusi Csataterek*).
  - A nap legmagasabb hatású (impact score) országos hírei.
- **📅 A Hét Összefoglalója (Weekly Digest):**
  - Heti szerkesztőségi konszenzus és politikai tanulságok.
  - 4 kulcsfontosságú stratégiai fordulat a félidős kampányban.
  - Heti mélyelemzések a The New York Times és a The Wall Street Journal hasábjairól.
- **📰 Összesített Hírfolyam:** Időrendi cikkfolyam közvetlen forráshivatkozásokkal.

### 4. 🔴 Trump Figyelő (Trump Tracker)
- **💬 Truth Social és Nyilvános Bejegyzések:**
  - Donald Trump elnök legfrissebb nyilatkozatai, bejegyzései és kampánybeszédei.
  - **Független Tényellenőrzés & Kontextus:** Minden megszólaláshoz az AP és a Reuters független tényszerű háttere.
- **📍 32 Napos Nemzeti Kampánykörút & Nagygyűlések:**
  - San Antonio (Texas), Oklahoma City, Mobile (Alabama), Grand Rapids (Michigan) eseményei és tervezett állomásai.
- **⚡ Kiemelt Kampányígéretek és Fókusz Témák:**
  - $5,000 kongresszusi osztalék ígérete, kormányzati TV-hirdetési hullám, szövetségi szavazóköri felügyelet.
- **📊 Elnöki Népszerűségi Barométer:**
  - RealClearPolitics és 538 súlyozott átlag (39.8% támogatás vs. 56.4% elutasítás) és ennek történelmi összefüggése a félidős mandátumveszteségekkel.

### 5. 🔄 Napi Automatikus Frissítés & 1-Kattintásos Szinkronizáció
- A fejlécben található **"🔄 Frissítés most"** gombbal azonnal elindítható az adatok frissítése.
- Háttérben futó automatikus időzítés naponta.
- `updater.py` szkript, amely szükség esetén manuálisan vagy cronból is futtatható.

---

## 🛡️ Szigorúan Ellenőrzött Források

### Hiteles Média:
- **Associated Press (AP):** A legrégebbi és leghitelesebb amerikai hírügynökség.
- **Reuters:** Globális tényalapú hírügynökség.
- **The New York Times & The Wall Street Journal:** Vezető amerikai napilapok mélyreható elemzésekkel.
- **Politico:** Washingtoni kongresszusi szakportál.
- **BBC News & PBS NewsHour:** Független, kiegyensúlyozott közszolgálati tudósítások.

### Megbízható Közvélemény-kutatók és Elemzők:
- **Siena College / The New York Times (A+ minősítés):** A legpontosabb amerikai felmérő intézet.
- **Marist College Poll (A minősítés):** Akadémiai független felmérések.
- **Monmouth University Polling Institute (A minősítés)**
- **Emerson College Polling (A- minősítés)**
- **Quinnipiac University Poll (A- minősítés)**
- **The Cook Political Report & Sabato's Crystal Ball:** A legelismertebb kétpárti választási prognózis intézetek.
- **RealClearPolitics & 538 / ABC News:** Súlyozott országos aggregátorok.

---

## 🚀 Indítás és Használat

### 1. Opció: Egyszerű indítás (Ajánlott)
Nyiss meg egy terminált a mappában, és futtasd:
```bash
./start.sh
```
Ez elindítja a helyi szervert és automatikusan megnyitja az oldalt a böngésződben a `http://localhost:8080` címen!

### 2. Opció: Közvetlen megnyitás (szerver nélkül)
Egyszerűen kattints duplán az `index.html` fájlra a Finderben! Az oldal beépített biztonsági tartalékkal rendelkezik, így bármilyen modern böngészőben (Safari, Chrome) azonnal működik.

### 3. Opció: Kézi frissítés futtatása parancssorból
```bash
python3 updater.py
```

---

## 📁 Fájlszerkezet

```
USA - midterm/
├── index.html           # A weboldal fő felülete
├── css/
│   └── styles.css       # Reszponzív modern dizájn, sötét/világos mód
├── js/
│   ├── app.js           # Alkalmazáslogika, szűrők, számláló, témakezelő
│   ├── charts.js        # Szenátusi félköríves parlament és mérlegábrák
│   └── fallback_data.js # Helyi biztonsági másolat adatcsomag
├── data/
│   ├── projections.json # Szenátusi és Képviselőházi előrejelzések
│   ├── polls.json       # Közvélemény-kutatások adatbázisa
│   └── news.json        # Válogatott hiteles híranyagok
├── updater.py           # Automatikus adatfrissítő motor
├── server.py            # Helyi kiszolgáló szerver API végpontokkal
├── start.sh             # 1-kattintásos indítószkript macOS-re
└── README.md            # Részletes dokumentáció
```
