#!/usr/bin/env python3
# api.py — JSON only. Shortcuts Get Contents of URL.
#   python3 api.py 8765
# Paths: /api/health /api/test /api/fold /api/last

import json
import os
import socket
import sys

from http.server import BaseHTTPRequestHandler, HTTPServer

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
sys.path.insert(0, os.path.join(HERE, "tests"))
sys.path.insert(0, os.path.join(HERE, "scans"))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
LAST = os.path.join(HERE, "notes", "last_test.json")


def ips():
    found = set()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        found.add(s.getsockname()[0])
        s.close()
    except Exception:
        pass
    found.discard("127.0.0.1")
    return sorted(found) or ["127.0.0.1"]


def body_for(path):
    if path in ("/", "/api/health"):
        return {"ok": True, "service": "genome-map", "root": HERE}
    if path == "/api/last":
        if os.path.exists(LAST):
            with open(LAST) as f:
                return json.load(f)
        return {"ok": False, "error": "no last_test.json yet"}
    if path == "/api/test":
        from runner import run_all
        return run_all()
    if path == "/api/fold":
        from runner import test_fold, write
        r = test_fold()
        return write({"ok": r.get("ok"), "results": [r], "root": HERE})
    return None


class H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stdout.write("%s\n" % (fmt % args))

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        data = body_for(path)
        if data is None:
            self.send_error(404)
            return
        raw = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self):
        self.do_GET()


def main():
    print("api", HERE)
    print("this app  http://127.0.0.1:%s/api/health" % PORT)
    for ip in ips():
        print("Shortcuts http://%s:%s/api/test" % (ip, PORT))
    HTTPServer(("0.0.0.0", PORT), H).serve_forever()


if __name__ == "__main__":
    main()
