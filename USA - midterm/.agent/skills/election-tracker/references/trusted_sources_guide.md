# Hiteles Források és Módszertani Útmutató Bármely Országra

Ez a dokumentum rögzíti azokat a minőségi szempontokat, amelyek alapján egy adott ország választási portálja kizárólag megbízható adatokat használhat fel.

---

## 🛡️ 1. Média Források Kiválasztása (Tier-1 Követelmények)

Minden célország esetén az alábbi típusú sajtóorgánumokat kell választani:
1. **Hivatalos Nemzeti és Nemzetközi Hírügynökségek:**
   - USA / Globális: Associated Press (AP), Reuters, AFP, Bloomberg.
   - Németország: DPA (Deutsche Presse-Agentur).
   - Egyesült Királyság: PA Media (Press Association), BBC News.
   - Franciaország: AFP (Agence France-Presse).
   - Magyarország: Független tényfeltáró és ellenőrzött szerkesztőségek (Telex, 24.hu, HVG, 444).
2. **Kizárási Kritériumok:**
   - Pártközeli bulvárlapok vagy állami propagandacsatornák kizárása.
   - Névtelen vagy szerző nélküli álhíroldalak automatikus tiltása.
   - Minden cikkhez kötelező a közvetlen forráshivatkozás és az eredeti megjelenési időbélyeg.

---

## 📊 2. Közvélemény-kutatók Akkreditálása & Minősítése

Minden felmérés mellett kötelező feltüntetni a megbízhatósági minősítést:

Besorolás | Kritériumok | Példák Intézetekre
:--- | :--- | :---
**A+** | Kettős ellenőrzésű véletlenszerű mintavétel, teljes módszertani transzparencia, történelmileg 1.5% alatti hibahatár | Siena College/NYT, Infratest dimap (Németország)
**A / A-** | Akadémiai vagy vezető nemzeti intézet, telefonos és online panel hibrid mintavétel, nyilvános súlyozási mátrix | Marist Poll, YouGov UK, Forschungsgruppe Wahlen, Medián (Magyarország)
**B+** | Nemzetközi szabványos online panelek, rendszeres audit | Ipsos, Forsa, Survation, Závecz Research
**Tiltott** | Módszertan nélküli online kattintásos szavazások, párt által fizetett belső mérések | Kizárva az aggregátorból

---

## 🔍 3. Kulcsszó- és Médiafigyelő Algoritmus

A "Nap Fontos Eseményei" és a "Heti Összefoglaló" generálásának logikája:
1. **RSS / API Hírek Letöltése:** Naponta legalább 3 független forrásból.
2. **Kulcsszó-Gyakoriság Vizsgálata:**
   - Pártnevek, vezető politikusok, gazdasági kulcsszavak (pl. *infláció, munkahelyek, adók, egészségügy*).
   - Témacsoportosítás (Cluster Analysis).
3. **Kiemelt Hatás (Impact Score):**
   - Ha egy hír több mint 3 független forrásban egyszerre címlapos, a besorolása `Kritikus` vagy `Magas`.
