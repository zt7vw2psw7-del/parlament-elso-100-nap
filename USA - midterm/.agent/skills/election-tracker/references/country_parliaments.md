# Nemzetközi Parlamenti és Választási Referencia-Útmutató

Ez a dokumentum a különböző országok törvényhozási felépítését, mandátumszámait, többségi küszöbeit és választási sajátosságait tartalmazza az `election-tracker` skill számára.

---

## 🌍 Országok Törvényhozási Adatbázisa

### 1. 🇺🇸 Amerikai Egyesült Államok (United States)
- **Típus:** Kétkamarás elnöki köztársaság
- **Felsőház (Szenátus / Senate):**
  - Összes mandátum: **100** (államonként 2)
  - Többségi küszöb: **51** (vagy 50 + alelnök)
  - Választási ciklus: 6 év (kétévente 1/3 megújul)
- **Alsóház (Képviselőház / House of Representatives):**
  - Összes mandátum: **435**
  - Többségi küszöb: **218**
  - Választási ciklus: 2 év (mind a 435 szék újraválasztásra kerül)

### 2. 🇩🇪 Németország (Germany)
- **Típus:** Szövetségi parlamentáris köztársaság
- **Bundestag (Szövetségi Gyűlés):**
  - Összes mandátum: **630** (az új választási reform szerint rögzített létszám)
  - Többségi küszöb: **316**
  - Választási küszöb (Sperrklausel): **5%** vagy 3 egyéni mandátum
  - Főbb pártok: CDU/CSU (fekete/kék), SPD (piros), Zöldek (zöld), FDP (sárga), AfD (világoskék), BSW (lila), Die Linke (sötétpiros).
  - Megbízható közvélemény-kutatók: Infratest dimap (ARD), Forschungsgruppe Wahlen (ZDF), Forsa, INSA, Allensbach.

### 3. 🇬🇧 Egyesült Királyság (United Kingdom)
- **Típus:** Alkotmányos monarchia, parlamentáris demokrácia (Westminsteri rendszer)
- **House of Commons (Közösségi Ház):**
  - Összes mandátum: **650** (egyéni választókerületi rendszer - FPTP)
  - Többségi küszöb: **326** (a gyakorlatban a Sinn Féin képviselők távolmaradása miatt ~320)
  - Főbb pártok: Labour (piros), Conservative (kék), Liberal Democrats (sárga), Reform UK (ciánkék), Zöldek (zöld), SNP (sárga-fekete).
  - Megbízható kutatók: YouGov (A), Ipsos UK, Survation, Deltapoll, Opinium.

### 4. 🇭🇺 Magyarország (Hungary)
- **Típus:** Parlamentáris köztársaság
- **Országgyűlés (Egykamarás):**
  - Összes mandátum: **199** (106 egyéni választókerület + 93 országos pártlistás)
  - Egyszerű többség: **100** mandátum
  - Kétharmados (alkotmányozó) többség: **133** mandátum
  - Választási küszöb: **5%** (önálló pártlista), 10% (kétpárti lista), 15% (három vagy több párt).
  - Megbízható / Független kutatók: Medián, IDEA Intézet, 21 Kutatóközpont, Závecz Research, Republikon.

### 5. 🇫🇷 Franciaország (France)
- **Típus:** Félelnöki köztársaság
- **Assemblée Nationale (Nemzetgyűlés):**
  - Összes mandátum: **577** (kétfordulós egyéni választási rendszer)
  - Abszolút többség: **289**
  - Főbb tömbök: Nouveau Front Populaire / Baloldali szövetség, Ensemble / Elnöki tábor, Rassemblement National (RN) / Jobboldal, Les Républicains.
  - Megbízható kutatók: Ipsos France, Ifop, Harris Interactive, Elabe, OpinionWay.

### 6. 🇵🇱 Lengyelország (Poland)
- **Típus:** Parlamentáris köztársaság
- **Sejm (Alsóház):**
  - Összes mandátum: **460**
  - Többségi küszöb: **231**
  - Senat (Felsőház): **100** mandátum (többség: 51)
  - Megbízható kutatók: IBRiS, CBOS, United Surveys, Pollster.

---

## 🎨 Parlamenti Félkör (Hemicycle) Számítási Képlet

A 100–650 mandátumos parlamentek matematikai modellezése koncentrikus köríveken:
$$x = X_0 + R \cdot \cos(\theta), \quad y = Y_0 - R \cdot \sin(\theta)$$
Ahol:
- $\theta \in [0, \pi]$ (0°-tól 180°-ig terjedő félkör).
- A gyűrűk száma: 3–6 ív a terem méretétől függően.
- A székek balról jobbra politikai spektrum szerint rendezettek (Baloldal $\to$ Közép / Független $\to$ Jobboldal).
