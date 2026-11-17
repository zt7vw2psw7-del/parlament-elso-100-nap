# OPPONENSI ÉRTÉKELÉSI ÚTMUTATÓ ÉS REPRODUKCIÓS JELENTÉS
**Kurzus:** Sebők Miklós AI óra • Bibó István Szakkollégium  
**Cél:** Egy hallgatótárs parlamenti / szövegbányászati elemzésének szisztematikus ellenőrzése, reprodukciója és szóbeli opponálása a 4. blokkon.  
**Készítette:** Berczi Zoltán

---

## I. Áttekintő Reprodukciós Adatlap (Reproducibility Checklist)

| Ellenőrzési szempont | Elvárt standard | Megfelelt? (🟢 / 🟡 / 🔴) | Megjegyzések, észrevételek |
|---|---|:---:|---|
| **1. GitHub repó elérhetőség** | Klónozható, privát/publikus repó, tiszta struktúra | [ ] | Van `.gitignore`, nincsenek benne jelszavak/személyes adatok? |
| **2. Futtatási környezet** | `requirements.txt` vagy környezeti leírás | [ ] | Egy parancsból feláll a Python környezet? |
| **3. Adat-kódkönyv (Codebook)** | ParlLawSpeech standard (változók, egység, forrás) | [ ] | Egyértelmű, mit jelent egy sor a táblázatban? |
| **4. Reprodukálhatóság** | A szkriptek lefutnak és azonos számokat adnak | [ ] | `script.py` &rarr; azonos táblázatok és ábrák születnek? |
| **5. Elemzési egység tisztasága** | Szűrési szabályok dokumentálva | [ ] | Kiszűrték a <200 szavas eljárási mondatokat és tapsokat? |
| **6. Kódolói megbízhatóság** | Kézi vs. gépi teszt (Cohen-kappa) | [ ] | &kappa; &ge; 0,60 (ideálisan &ge; 0,80)? |

---

## II. Szóbeli Vita: 5 Célzott Kérdés az Opponált Társnak

Amikor bemutatja az elemzését, az alábbi módszertani és tartalmi kérdésekkel tudod szakmailag tesztelni a munkáját:

### 1. Kérdés a megfigyelési egységről (Unit of Analysis):
> *„Milyen szinten végezted a tematikus kódolást? Teljes felszólalásokra adtál egyetlen témacímkét, vagy mondatszintre (quasi-sentences) bontottad a szövegeket? Ha egy egész beszédre csak egy témát adtál, hogyan kezelted, amikor a képviselő egyszerre beszélt a költségvetésről és az egészségügyről?”*  
> 👉 **Mit figyelj a válaszban:** Ha nem bontotta mondatokra, felmerül a felületes kódolás veszélye, amit te a saját kutatásodban sikeresen feloldottál.

### 2. Kérdés a kódolói egyezésről (Inter-coder Reliability & Kappa):
> *„Végeztél kódolói megbízhatósági tesztet (pl. `/vcoder-agreement` vagy Cohen's kappa)? Mekkora lett a kappa értéke, és mely kategóriákban volt a legnagyobb a nézeteltérés az ember és a gép között?”*  
> 👉 **Mit figyelj a válaszban:** Tudja-e a saját hibaszázalékát, vagy csak vakon megbízott a nyelvi modellben.

### 3. Kérdés a teljességről (Completeness & vscrape):
> *„Összevetetted a lekapart soraid számát a hivatalos parlamenti napló adataival (`vscrape` / `check_complete.py`)? Minden hiányzó tétel indokolt (`explained_count`), vagy maradt ismeretlen eltérés a hivatalos és a kinyert számok között?”*

### 4. Kérdés a felelősségáthárítás / múltkritika operacionalizálásáról:
> *„Hogyan definiáltad a múltkritikát? Szótáralapú kulcsszavakkal vagy szemantikai modellel szűrtél? Hogyan biztosítottad, hogy a pusztán történelmi visszatekintések ne keveredjenek össze a valódi politikai hibáztatással?”*

### 5. Kérdés a jogalkotási hatékonyság értelmezéséről:
> *„A törvények elfogadási arányát a parlament hatékonyságaként vagy a fékek és egyensúlyok hiányaként értelmezed? Mennyiben torzítja az eredményt a frakciók fegyelme?”*

---

## III. Írásos Reprodukciós Sablon (Leadandó az órán)

```markdown
# Reprodukciós és Minőségbiztosítási Jelentés
Opponens: Berczi Zoltán
Értékelt hallgató neve: _______________________
Projekt / Repó címe: _______________________

1. Futtatási teszt:
   - Klónozás sikeressége: [Sikeres / Hibára futott]
   - Adatbázis újragenerálása: [Azonos számokat adott / Eltérés volt]
   - Eltérés leírása (ha volt): 

2. Módszertani erősségek:
   - ...
   - ...

3. Kritikai észrevételek és javaslatok:
   - ...
   - ...

4. Összegző minősítés: [Elfogadva / Kisebb javítással elfogadva / Újrafuttatás szükséges]
```
