# serve_here.py — iSH and Pythonista
# Other side: python3 fetch_any.py http://THAT_IP:8000/FILENAME

import os
import socket
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
ROOT = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
try:
    os.chdir(ROOT)
except Exception:
    ROOT = os.getcwd()

def ips():
    found = set()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        found.add(s.getsockname()[0])
        s.close()
    except Exception:
        pass
    try:
        found.add(socket.gethostbyname(socket.gethostname()))
    except Exception:
        pass
    found.discard("127.0.0.1")
    found.discard("0.0.0.0")
    return sorted(found) or ["127.0.0.1"]

print("serving", os.getcwd(), "on port", PORT)
print("this app 127.0.0.1:%s  (same app only)" % PORT)
for ip in ips():
    print("GET http://%s:%s/" % (ip, PORT))
print("other app must use an IP line, not 127.0.0.1")
print("Ctrl-C to stop")

if sys.version_info[0] >= 3:
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    HTTPServer(("0.0.0.0", PORT), SimpleHTTPRequestHandler).serve_forever()
