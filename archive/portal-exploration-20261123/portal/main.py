"""Loopback-only HTTP adapter for the first portal slice. Run python -m portal.main."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import urlsplit
from .analytics import scenario
from .snapshot import build

WEB = Path(__file__).parent / 'web'

def handler(snapshot, reference=None):
    class Handler(BaseHTTPRequestHandler):
        def send(self, status, body, content_type='application/json; charset=utf-8'):
            if isinstance(body, dict): body = json.dumps(body, allow_nan=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(body)
        def do_GET(self):
            path = urlsplit(self.path).path
            if path == '/api/snapshot': return self.send(200, snapshot)
            if path == '/api/reference' and reference: return self.send(200, reference)
            assets = {'/': ('index.html', 'text/html; charset=utf-8'), '/app.js': ('app.js', 'text/javascript; charset=utf-8'), '/styles.css': ('styles.css', 'text/css; charset=utf-8')}
            if path not in assets: return self.send(404, {'error': 'Not found'})
            filename, content_type = assets[path]
            self.send(200, (WEB / filename).read_bytes(), content_type)
        def do_POST(self):
            if self.path != '/api/scenario': return self.send(404, {'error': 'Not found'})
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 4096: raise ValueError('Expected a JSON command of 1-4096 bytes')
                if self.headers.get('Content-Type', '').split(';')[0].strip() != 'application/json': raise ValueError('Content-Type must be application/json')
                command = json.loads(self.rfile.read(length))
                selected = reference if reference and isinstance(command, dict) and command.get('company_id') == reference['company']['id'] else snapshot
                value = scenario(selected, command)
            except (ValueError, TypeError, KeyError) as exc:
                return self.send(400, {'error': str(exc)})
            self.send(200, value)
    return Handler

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8766)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), handler(build(), build(reference=True)))
    print(f'IPO-Ready portal: http://127.0.0.1:{server.server_port}', flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()

if __name__ == '__main__': main()
