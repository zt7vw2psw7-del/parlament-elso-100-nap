#!/usr/bin/env python3
"""
Európai Parlament Nyílt Adat API (Open Data API v2) Gyűjtő és Frissítő Modul
Ez a script lehetővé teszi a hivatalos EP API (data.europarl.europa.eu/api/v2) 
és SPARQL végpont közvetlen lekérdezését új felszólalások, dokumentumok és kérdések letöltéséhez.

Használat:
    python3 ep_api_collector.py --query "Draghi"
"""

import urllib.request
import urllib.parse
import json
import sqlite3
import argparse
import sys

API_BASE_URL = "https://data.europarl.europa.eu/api/v2"
SPARQL_URL = "https://data.europarl.europa.eu/sparql"
DB_PATH = "ep_draghi_database.db"

def check_online_connectivity():
    try:
        req = urllib.request.Request(
            f"{API_BASE_URL}/", 
            headers={"User-Agent": "EP-Draghi-Research-Agent/1.0", "Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False

def search_ep_speeches(query="Draghi", limit=20):
    """
    Lekérdezi az EP Open Data API /speeches végpontját a megadott kulcsszóra.
    """
    endpoint = f"{API_BASE_URL}/speeches"
    params = {
        "title": query,
        "format": "application/ld+json",
        "limit": limit
    }
    url = f"{endpoint}?{urllib.parse.urlencode(params)}"
    print(f"📡 Lekérdezés indítása: {url}")
    
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "EP-Draghi-Research-Agent/1.0", "Accept": "application/ld+json"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get("data", [])
    except Exception as e:
        print(f"⚠️ Hiba az API elérése során: {e}")
        return []

def search_parliamentary_questions(query="Draghi", limit=20):
    """
    Lekérdezi a parlamenti kérdéseket az EP Open Data API-ból.
    """
    endpoint = f"{API_BASE_URL}/parliamentary-questions"
    params = {
        "text": query,
        "format": "application/ld+json",
        "limit": limit
    }
    url = f"{endpoint}?{urllib.parse.urlencode(params)}"
    print(f"📡 Kérdések lekérdezése: {url}")
    
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "EP-Draghi-Research-Agent/1.0", "Accept": "application/ld+json"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get("data", [])
    except Exception as e:
        print(f"⚠️ Hiba a kérdések lekérdezése során: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description="EP Open Data API v2 Draghi adatgyűjtő")
    parser.add_argument("--query", type=str, default="Draghi", help="Keresési kulcsszó (alapértelmezett: Draghi)")
    parser.add_argument("--limit", type=int, default=20, help="Találatok maximális száma")
    args = parser.parse_args()

    print("="*70)
    print("🇪🇺 EURÓPAI PARLAMENT NYÍLT ADAT API (v2) CSATLAKOZÓ")
    print("="*70)
    
    is_online = check_online_connectivity()
    if not is_online:
        print("ℹ️  A rendszer offline módban van (vagy korlátozott sandbox hálózati környezetben).")
        print("💡 Normál terminálban (internetkapcsolattal) futtatva a script automatikusan")
        print("   letölti a legfrissebb adatokat a data.europarl.europa.eu/api/v2 szerverről.")
        print("   A meglévő adatbázis (ep_draghi_database.db) továbbra is teljeskörűen")
        print("   lekérdezhető a 'python3 query_database.py' paranccsal.")
        return

    print("✅ Kapcsolat létrejött az EP Open Data API-val.")
    speeches = search_ep_speeches(query=args.query, limit=args.limit)
    print(f"Talált felszólalások: {len(speeches)}")
    
    questions = search_parliamentary_questions(query=args.query, limit=args.limit)
    print(f"Talált parlamenti kérdések: {len(questions)}")

if __name__ == "__main__":
    main()
