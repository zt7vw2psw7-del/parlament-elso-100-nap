#!/bin/bash
# =====================================================================
# 🏛️ Hivatalos Parlamenti WebAPI Automata Letöltő Script
# =====================================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "================================================================="
echo "   PARLAMENTI WEBAPI - 100 NAPOS ADATBÁZIS ÉPÍTŐ ÉS SZINKRONIZÁLÓ "
echo "================================================================="

if ! command -v python3 &> /dev/null; then
    echo "❌ Hiba: A python3 nem található a rendszeren."
    exit 1
fi

python3 "$DIR/pipeline/api_fetcher.py" "$@"

echo ""
echo "📈 Frissített adatbázis statisztika:"
sqlite3 "$DIR/parlament_100nap.db" "
SELECT 
    p.name AS korszak,
    COUNT(DISTINCT s.sitting_day_id) AS ulesnapok,
    COUNT(s.id) AS felszolalasok,
    SUM(s.word_count) AS osszes_szoszam,
    SUM(CASE WHEN v.has_past_critique = 1 THEN 1 ELSE 0 END) AS multat_biralo_beszedek
FROM period p
LEFT JOIN speech s ON p.id = s.period_id
LEFT JOIN v_speeches_categorized v ON s.id = v.speech_id
GROUP BY p.name;
" -header -column

echo ""
echo "✨ Kész! Az adatok letöltve a 'parlament_100nap.db' adatbázisba és exportálva a 'exports/' mappába."
