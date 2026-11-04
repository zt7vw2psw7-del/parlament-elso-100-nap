# Házirend és Projekt Leírás (GEMINI.md / AGENTS.md)

## Projekt összefoglaló
A 2010-es és a 2026-os országgyűlés első 100 napjának összehasonlító politikatudományi elemzése (ELTE Bibó István Szakkollégium / Sebők Miklós AI óra).

## Szabályok és vezérelvek az ágensek számára
1. **Adatbázis integritása:**
   - Az adatbázis SQLite formátumú (`parlament_100nap.db`), a projekt almappájában található.
   - A törvényjavaslatok és felszólalások kategorizálása a CAP Master Codebook (Comparative Agendas Project) szerint történik (21 főkategória, 209 alkategória).
   - Felszólalások szűrése: csak a 200 szó feletti érdemi felszólalásokat elemezzük, a tapsokat és közbekiabálásokat szűrjük.
2. **Kód és szkriptek:**
   - A pipeline szkriptek a `pipeline/` mappában helyezkednek el.
   - Python kódok futtatásakor ügyeljünk a függőségekre és az UTF-8 kódolásra.
3. **Riportok és exportok:**
   - Az exportok az `exports/` mappába kerülnek CSV formátumban.
   - Az interaktív riport a `riport.html` / `parlament_100nap_riport.html` fájlban érhető el.
4. **Biztonság és verziókezelés:**
   - Semmilyen API kulcsot, jelszót vagy személyes adatot ne töltsünk fel a verziókövetőbe.
   - A nagy adatbázis fájlok (`.db`, `.zip`) a `.gitignore` által ki vannak zárva.
