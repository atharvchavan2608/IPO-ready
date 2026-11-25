"""Run: python app/main.py. Local-only demonstration; no external services."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
import json
from engine import build_report

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed=urlsplit(self.path)
        if parsed.path=='/api/report':
            try:
                report=build_report(parse_qs(parsed.query).get('period',['FY21'])[0])
                content=json.dumps(report,allow_nan=False).encode()
                mime='application/json'
            except ValueError as exc:
                self.send_error(400,str(exc));return
        elif parsed.path=='/':
            content=Path(__file__).with_name('index.html').read_bytes();mime='text/html; charset=utf-8'
        else:
            self.send_error(404);return
        self.send_response(200)
        self.send_header('Content-Type',mime)
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.end_headers();self.wfile.write(content)

if __name__=='__main__':
    print('IPO-Ready demo: http://127.0.0.1:8765',flush=True)
    ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
