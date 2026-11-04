#!/bin/bash
# =====================================================================
# 🏛️ Parlamenti Felszólalások és Kérdések Kötegelt Importálója
# 1.2-es Megoldás: Helyi HTML/XML/JSON fájlok egykattintásos betöltése
# =====================================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "================================================================="
echo "   PARLAMENTI ADATBÁZIS - AUTOMATIKUS IMPORTÁLÓ ÉS BESOROLÓ       "
echo "================================================================="

if ! command -v python3 &> /dev/null; then
    echo "❌ Hiba: A python3 nem található a rendszeren."
    exit 1
fi

python3 "$DIR/pipeline/batch_importer.py"

echo ""
echo "📈 Aktuális adatbázis statisztika:"
sqlite3 "$DIR/parlament_100nap.db" "
SELECT 
    p.name AS korszak,
    COUNT(DISTINCT s.sitting_day_id) AS ulesnapok,
    COUNT(s.id) AS felszolalasok_szama,
    ROUND(SUM(s.word_count) / 1000.0, 1) AS ezer_szoszam
FROM period p
LEFT JOIN speech s ON p.id = s.period_id
GROUP BY p.name;
" -header -column

echo ""
echo "✨ Kész! Az adatok betöltve a 'parlament_100nap.db' fájlba és exportálva az 'exports/' mappába."
