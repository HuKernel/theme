# theme.lhxl.chat 全站复制计数 API
# GET  /api/counts -> {"风格名": N, ...}
# POST /api/count  body {"name":"风格名"} -> {"name":..., "count": N}
# 存储：counts.json 文件；仅监听 127.0.0.1，由 Caddy 反代对外
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'counts.json')
LOCK = Lock()


def load():
    try:
        with open(DB, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def save(d):
    tmp = DB + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.replace(tmp, DB)


class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/api/counts':
            with LOCK:
                self._json(load())
        else:
            self._json({'error': 'not found'}, 404)

    def do_POST(self):
        if self.path != '/api/count':
            return self._json({'error': 'not found'}, 404)
        n = int(self.headers.get('Content-Length') or 0)
        try:
            name = str(json.loads(self.rfile.read(n) or b'{}').get('name', ''))[:80].strip()
        except Exception:
            name = ''
        if not name:
            return self._json({'error': 'bad request'}, 400)
        with LOCK:
            d = load()
            d[name] = d.get(name, 0) + 1
            save(d)
            count = d[name]
        self._json({'name': name, 'count': count})

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    ThreadingHTTPServer(('127.0.0.1', 8750), Handler).serve_forever()
