#!/usr/bin/env bash
# start.sh - Launch US Midterms 2026 Dashboard and open in default browser

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "Indítás: USA Midterms 2026 Dashboard..."

# Run updater once to ensure fresh data
python3 updater.py

# Launch server in background
python3 server.py &
SERVER_PID=$!

sleep 1

# Open in default macOS browser
open "http://localhost:8080"

echo "A weboldal megnyílt a böngészőben (http://localhost:8080)."
echo "A szerver háttérben fut (PID: $SERVER_PID)."
echo "A leállításhoz zárd be a terminál ablakot vagy futtasd: kill $SERVER_PID"

wait $SERVER_PID
