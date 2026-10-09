# theme.lhxl.chat 全站复制计数 API
# GET  /api/counts -> {"风格名": N, ...}
# POST /api/count  body {"name":"风格名"} -> {"name":..., "count": N}
# 存储：counts.json 文件；仅监听 127.0.0.1，由 Caddy 反代对外
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'counts.json')
LOCK = Lock()

SESSIONS = {}  # ponytail: 在线会话存内存，进程重启即清零——“当前在线”本就是瞬时态
ONLINE_WINDOW = 300  # 5 分钟内心跳算在线



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


# 启动时预热内存缓存
_cache = load()

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
                self._json(_cache)
        elif self.path == '/api/online':
            with LOCK:
                self._prune()
                self._json({'online': len(SESSIONS)})
        else:
            self._json({'error': 'not found'}, 404)

    @staticmethod
    def _prune():
        now = time.time()
        for k in [k for k, v in SESSIONS.items() if now - v > ONLINE_WINDOW]:
            SESSIONS.pop(k, None)

    def do_POST(self):
        if self.path == '/api/heartbeat':
            n = int(self.headers.get('Content-Length') or 0)
            try:
                sid = str(json.loads(self.rfile.read(n) or b'{}').get('sid', ''))[:64].strip()
            except Exception:
                sid = ''
            if not sid:
                return self._json({'error': 'bad request'}, 400)
            with LOCK:
                SESSIONS[sid] = time.time()
                self._prune()
                self._json({'online': len(SESSIONS)})
            return
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
            _cache[name] = _cache.get(name, 0) + 1
            save(_cache)
            count = _cache[name]
        self._json({'name': name, 'count': count})

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    ThreadingHTTPServer(('127.0.0.1', 8750), Handler).serve_forever()
