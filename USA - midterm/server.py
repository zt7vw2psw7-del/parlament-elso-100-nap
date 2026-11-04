#!/usr/bin/env python3
"""
server.py - Lightweight local web server for US Midterm Elections Dashboard.
Serves static dashboard files and handles /api/update calls for instant data refresh.
Uses strictly Python 3 standard library (no pip packages needed).
"""

import os
import sys
import json
import socket
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
import updater

PORT = 8080
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRUTH_ARCHIVE_FILE = os.path.join(BASE_DIR, "data", "truth_archive.json")

_TRUTH_CACHE = None
_TRUTH_CACHE_MTIME = 0

def get_truth_posts():
    global _TRUTH_CACHE, _TRUTH_CACHE_MTIME
    if not os.path.exists(TRUTH_ARCHIVE_FILE):
        return []
    try:
        mtime = os.path.getmtime(TRUTH_ARCHIVE_FILE)
        if _TRUTH_CACHE is None or mtime != _TRUTH_CACHE_MTIME:
            with open(TRUTH_ARCHIVE_FILE, "r", encoding="utf-8") as f:
                _TRUTH_CACHE = json.load(f)
            _TRUTH_CACHE_MTIME = mtime
        return _TRUTH_CACHE
    except Exception as e:
        sys.stderr.write(f"[Server] Truth cache error: {e}\n")
        return _TRUTH_CACHE or []

class MidtermServerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        
        if parsed.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            status = {
                "server": "online",
                "port": PORT,
                "project": "US Midterms 2026 Tracker"
            }
            self.wfile.write(json.dumps(status).encode("utf-8"))
            return

        if parsed.path == "/api/truth-posts":
            params = urllib.parse.parse_qs(parsed.query)
            try:
                page = max(1, int(params.get("page", ["1"])[0]))
            except ValueError:
                page = 1
            try:
                limit = max(5, min(int(params.get("limit", ["25"])[0]), 100))
            except ValueError:
                limit = 25

            q = params.get("q", [""])[0].strip().lower()
            sort_by = params.get("sort", ["newest"])[0]
            has_media = params.get("has_media", [""])[0].lower() in ("1", "true", "yes")
            topic = params.get("topic", [""])[0].strip().lower()

            all_posts = get_truth_posts()
            results = all_posts

            if q:
                results = [p for p in results if q in (p.get("content") or "").lower()]

            if has_media:
                results = [p for p in results if len(p.get("media", [])) > 0]

            if topic and topic != "all":
                topic_keywords = {
                    "election": ["election", "midterm", "vote", "ballot", "republican", "democrat", "senate", "house", "poll", "rally", "paxton", "victory"],
                    "economy": ["tariff", "tariffs", "inflation", "economy", "tax", "taxes", "jobs", "trade", "dollar", "china", "manufacturing", "energy", "oil"],
                    "border": ["border", "wall", "migrant", "migrants", "immigration", "illegal", "ice", "patrol", "invasion", "cartel", "texas"],
                    "legal": ["court", "judge", "doj", "fbi", "witch hunt", "indictment", "trial", "lawyer", "justice", "prosecutor"],
                    "china": ["china", "xi", "beijing", "chinese", "taiwan"],
                    "foreign": ["ukraine", "iran", "israel", "russia", "peace", "war", "nato", "putin", "gaza"]
                }
                keywords = topic_keywords.get(topic, [topic])
                results = [p for p in results if any(kw in (p.get("content") or "").lower() for kw in keywords)]

            if sort_by == "likes":
                results = sorted(results, key=lambda x: x.get("favourites_count", 0), reverse=True)
            elif sort_by == "retruths":
                results = sorted(results, key=lambda x: x.get("reblogs_count", 0), reverse=True)
            elif sort_by == "oldest":
                results = sorted(results, key=lambda x: x.get("created_at", ""))
            elif sort_by == "newest":
                results = sorted(results, key=lambda x: x.get("created_at", ""), reverse=True)

            total_items = len(results)
            total_pages = max(1, (total_items + limit - 1) // limit)
            page = max(1, min(page, total_pages)) if total_items > 0 else 1
            start = (page - 1) * limit
            end = start + limit
            paged_posts = results[start:end]

            response = {
                "status": "ok",
                "total": len(all_posts),
                "filtered_total": total_items,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "posts": paged_posts
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))
            return

        if parsed.path == "/api/truth-stats":
            all_posts = get_truth_posts()
            media_count = sum(1 for p in all_posts if p.get("media"))
            latest_post = all_posts[0] if all_posts else None
            top_post = max(all_posts, key=lambda x: x.get("favourites_count", 0)) if all_posts else None

            stats = {
                "total_posts": len(all_posts),
                "total_media_posts": media_count,
                "latest_post_date": latest_post.get("created_at") if latest_post else None,
                "top_liked_post": {
                    "id": top_post.get("id"),
                    "text": (top_post.get("content") or "")[:140],
                    "likes": top_post.get("favourites_count", 0),
                    "retruths": top_post.get("reblogs_count", 0),
                    "date": top_post.get("created_at"),
                    "url": top_post.get("url")
                } if top_post else None,
                "first_post_date": all_posts[-1].get("created_at") if all_posts else None
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(stats, ensure_ascii=False).encode("utf-8"))
            return
        
        # Default static file handling
        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/update":
            try:
                result = updater.run_update()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
            return
        
        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        # Clean terminal logging
        sys.stderr.write(f"[Server] {self.address_string()} - {format % args}\n")

def find_available_port(start_port):
    port = start_port
    while port < start_port + 50:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
        port += 1
    return start_port

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

def run():
    global PORT
    PORT = find_available_port(PORT)
    server_address = ('0.0.0.0', PORT)
    httpd = HTTPServer(server_address, MidtermServerHandler)
    local_ip = get_local_ip()
    print("=" * 65)
    print(f"🚀 USA Midterm 2026 Tracker Elindult!")
    print(f"📍 Helyi gép elérése:       http://localhost:{PORT}")
    print(f"📱 Azonos Wi-Fi hálózaton:  http://{local_ip}:{PORT}")
    print(f"🔄 Napi automata frissítő:  Aktív (updater.py)")
    print(f"🛑 Leállítás: Ctrl+C")
    print("=" * 65)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nA szerver leállt.")
        httpd.server_close()

if __name__ == '__main__':
    run()
