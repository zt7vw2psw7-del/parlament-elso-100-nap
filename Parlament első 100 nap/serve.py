import os
import unicodedata
from http.server import HTTPServer, SimpleHTTPRequestHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class SafeHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Eltávolítjuk a query paramétereket
        path = path.split('?', 1)[0].split('#', 1)[0]
        # Mindig a BASE_DIR-ből szolgáljuk ki
        rel_path = path.lstrip('/')
        if not rel_path or rel_path == 'index.html':
            rel_path = 'parlament_100nap_riport.html'
        full_path = os.path.join(BASE_DIR, rel_path)
        return full_path

if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', 8080), SafeHandler)
    print("Szerver fut: http://127.0.0.1:8080/")
    server.serve_forever()
