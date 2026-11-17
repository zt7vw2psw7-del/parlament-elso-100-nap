# Parl100Nap: Magyar Parlamenti Összehasonlító Korpusz (2010 vs. 2026) — Adat-kódkönyv (Data Codebook)

**VERZIÓ:** 1.0  
**DÁTUM:** 2026-11-11  
**SZERZŐ:** Berczi Zoltán  
**PROJEKT:** ELTE Bibó István Szakkollégium / Sebők Miklós AI óra  
**LICENC:** Creative Commons Attribution 4.0 International (CC-BY 4.0)  
**REDIZITÓRIUM:** `https://github.com/zt7vw2psw7-del/parlament-elso-100-nap.git`

---

## 1. Bevezetés (Introduction)

A **Parl100Nap** korpusz a 2010-es kormányváltás és a 2026-os parlamenti ciklus első 100 napjának összehasonlító politikatudományi vizsgálatára létrehozott strukturált szöveges adatbázis. A korpusz magában foglalja a plenáris felszólalásokat, a benyújtott törvényjavaslatokat és az írásbeli/szóbeli parlamenti kérdéseket. 

A korpusz célja a törvényhozási prioritások, a vitastílus és a politikai napirend feltárása a Comparative Agendas Project (CAP) Master Codebook tematikus taxonómiája és modern szöveganalitikai eszközök segítségével.

---

## 2. Lefedettség és Adatgyűjtés (Coverage & Data Collection)

A korpusz a Magyar Országgyűlés hivatalos adatait dolgozza fel az alakuló üléstől számított első 100 naptári napban mindkét ciklusban.

### 1. Táblázat: A korpusz lefedettsége és megfigyelési egységei

| Korpusz egység | Időszak | Megfigyelések száma ($N$) | Változók száma | Időkeret | Forrás |
|---|---|---|---|---|---|
| **Felszólalások (`speech`)** | 2010 | 2 334 | 24 | 2010.05.14 – 2010.08.21 | parlament.hu / Országgyűlési Napló |
| **Felszólalások (`speech`)** | 2026 | 1 539 | 24 | 2026.05.09 – 2026.08.16 | parlament.hu / WebAPI & Napló |
| **Törvényjavaslatok (`bill`)** | 2010 | 66 | 25 | 2010.05.14 – 2010.08.21 | parlament.hu / Irományok |
| **Törvényjavaslatok (`bill`)** | 2026 | 61 | 25 | 2026.05.09 – 2026.08.16 | parlament.hu / Irományok |
| **Kérdések (`question`)** | 2010 | 659 | 10 | 2010.05.14 – 2010.08.21 | parlament.hu / Kérdések |
| **Kérdések (`question`)** | 2026 | 1 366 | 10 | 2026.05.09 – 2026.08.16 | parlament.hu / Kérdések |
| **Képviselői aktivitás (`mp`)** | Összes | 492 | 7 | 2010 & 2026 | Rekord-összekapcsolt profil |

**Adatgyűjtési és szűrési protokoll:**
- A nyers szövegeket egyedi lekérdezésekkel, archivált HTML és WebAPI forrásokból gyűjtöttük össze.
- **Szűrési szabály:** A 200 szónál rövidebb technikai, eljárási felszólalásokat (pl. szünetek elrendelése, bejelentések), valamint a zárójeles reakciókat (taps, közbekiabálás, derültség) a standard minőségbiztosítás érdekében szűrtük.

---

## 3. Adatstruktúra és Változók (Data Structure & Variables)

- **Fájlformátumok:** SQLite adatbázis (`parlament_100nap.db`) és szabványos vesszővel tagolt szövegfájlok (`.csv`).
- **Karakterkódolás:** UTF-8 (BOM-mal a CSV-k esetében az Excel-kompatibilitás miatt).
- **Összekapcsoló kulcsok (Cross-corpus linking keys):**
  - `period_id`: Parlamenti ciklus azonosítója (`2010`, `2026`).
  - `speaker_name` / `submitter_names`: Politikai aktori névkapcsolat.
  - `cap_major_code`: Tematikus kapcsoló a CAP 21 főkategóriájához.

### 2. Táblázat: Felszólalások törzsváltozói (`felszolalasok_kategorizalva.csv`)

| Változó | Leírás |
|---|---|
| `speech_id` | Egyedi felszólalás-azonosító (`YYYY_DDD_NNN`). |
| `period_id` | Parlamenti időszak (`2010` vagy `2026`). |
| `period_name` | Az időszak ember által olvasható megnevezése. |
| `sitting_date` | Az ülésnap dátuma (`YYYY-MM-DD`). |
| `sitting_number` | Az ülés sorszáma a ciklusban. |
| `speaker_name` | A felszólaló képviselő hivatalos neve. |
| `group_name` | A képviselő frakciójának/pártjának teljes neve. |
| `governing_status` | Kormányzati pozíció (`kormany`, `ellenzek`, `fuggetlen`). |
| `speech_type_name` | A felszólalás típusa (pl. napirend előtti, vezérszónoki, általános vita). |
| `agenda_item` | A felszólaláshoz kapcsolódó napirendi pont vagy törvényjavaslat címe. |
| `word_count` | A tisztított felszólalás szószáma ($\ge 200$). |
| `cap_major_code` | Comparative Agendas Project főkategória kód (1–23, 11 és 22 kivételével). |
| `cap_subtopic_code` | CAP alkategória kód (209 téma alapján). |
| `primary_topic` | A CAP főkategória magyar elnevezése. |
| `primary_topic_en` | A CAP főkategória hivatalos angol elnevezése. |
| `confidence` | A gépi témabesorolás megbízhatósági pontszáma (0.0 – 1.0). |
| `summary` | A beszéd automatikusan generált tartalmi összefoglalója. |
| `has_past_critique` | Bináris indikátor: tartalmaz-e múltba mutató politikai kritikát (1/0). |
| `critique_intensity` | A múltkritika intenzitása (alacsony, közepes, magas). |
| `past_critique_mentions` | Múltbéli hivatkozások gyakorisága. |
| `source_url` | Hivatkozás a parlament.hu hivatalos jegyzőkönyvi oldalára. |

### 3. Táblázat: Törvényjavaslatok törzsváltozói (`torvenyjavaslatok_kategorizalva.csv`)

| Változó | Leírás |
|---|---|
| `bill_id` | Egyedi törvényjavaslat azonosító (`YYYY_T_N`). |
| `bill_number` | Hivatalos irományszám (pl. `T/9`). |
| `title` | A törvényjavaslat hivatalos teljes címe. |
| `short_title` | A javaslat rövidített, köznyelvi címe. |
| `affected_law` | A javaslat által módosított hatályos jogszabály. |
| `bill_type` | Javaslat jellege (új törvény, módosítás, határozat). |
| `submitter_names` | A beterjesztő(k) neve (vesszővel elválasztva több szerző esetén). |
| `submitter_party` | A beterjesztő politikai frakciója. |
| `submission_date` | Benyújtás dátuma (`YYYY-MM-DD`). |
| `status` | Parlamenti státusz (`elfogadva`, `elutasitva`, `tárgyalás alatt`). |
| `is_enacted` | Bináris változó: hatályba lépett-e a törvény (1 = igen, 0 = nem). |
| `yes_votes` | A zárószavazáson leadott igen szavazatok száma. |
| `no_votes` | A zárószavazáson leadott nem szavazatok száma. |
| `abstain_votes` | Tartózkodó szavazatok száma. |
| `cap_major_code` | A javaslat elsődleges CAP témakódja. |

---

## 4. Validáció és Minőségbiztosítás (Validation)

Az adathalmaz a ParlLawSpeech módszertani előírásai szerint 5 független validációs ellenőrzésen esett át (`/datavalidation`):
1. **Teljesség és duplikátum-mentesség:** Minden egyedi azonosító egyedi, hiányzó szövegmező nincs ($N_{\text{missing}} = 0$).
2. **Metaadat-inspekció:** A párt- és képviselőnevek egységesítettek, az ID-formátumok reguláris kifejezésekkel teszteltek (0 hiba).
3. **Keresztkapcsolatok (Record Linkage):** 492 képviselői profil feloldása a beszédek, javaslatok és kérdések összekapcsolásával.
4. **Kódolás és tisztítás:** 0 db hibás UTF-8 / mojibake karakter.
5. **vscrape teljesség (Reconciliation):** $\text{kinyert} + \text{magyarázott} = \text{hivatalos darabszám}$ (0 eltérés).

---

## 5. Adathozzáférés és Idézés (Data Access & Citation)

A korpusz nyílt hozzáférésű a tudományos közösség számára a CC-BY 4.0 licenc alatt.

**Javasolt hivatkozás:**
```bibtex
@misc{berczi2026parl100nap,
  author = {Berczi, Zolt{\'{a}}n},
  title = {Parl100Nap: Magyar Parlamenti {\"{O}}sszehasonl{\'{i}}t{\'{o}} Korpusz (2010 vs. 2026)},
  year = {2026},
  publisher = {GitHub},
  howpublished = {\url{https://github.com/zt7vw2psw7-del/parlament-elso-100-nap}}
}
```
