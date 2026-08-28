# fetch_any.py — iSH and Pythonista
#   python3 fetch_any.py
#   python3 fetch_any.py http://192.168.1.47:8000/genome-map-agents.tar.gz
#   python3 fetch_any.py https://github.com/Peekabot/genome-map-agents/archive/refs/heads/main.tar.gz

import os, sys, tarfile, tempfile, urllib.request

DEFAULT = "https://github.com/Peekabot/genome-map-agents/archive/refs/heads/main.tar.gz"
URL = sys.argv[1] if len(sys.argv) > 1 else DEFAULT

home = os.path.expanduser("~")
tries = [
    os.path.join(home, "Documents", "incoming"),
    os.path.join(home, "incoming"),
    os.path.join(os.getcwd(), "incoming"),
    tempfile.gettempdir(),
]
dest = None
for p in tries:
    try:
        os.makedirs(p, exist_ok=True)
        t = os.path.join(p, ".w")
        open(t, "w").close()
        os.remove(t)
        dest = p
        break
    except OSError:
        continue
if dest is None:
    raise SystemExit("no writable folder")

name = os.path.basename(URL.split("?")[0]) or "pack.bin"
tmp = os.path.join(dest, name)

def hook(n, bs, total):
    got = n * bs
    if total and total > 0:
        sys.stdout.write("\r%3d%%" % min(100, got * 100 // total))
    else:
        sys.stdout.write("\r%d" % got)
    sys.stdout.flush()

print("GET", URL)
print("dest", dest)
urllib.request.urlretrieve(URL, tmp, hook)
print("\nsaved", tmp)

if tmp.endswith(".tar.gz") or tmp.endswith(".tgz") or tmp.endswith(".tar"):
    with tarfile.open(tmp, "r:*") as t:
        for m in t.getmembers():
            if ".git" in m.name.replace("\\", "/").split("/"):
                continue
            t.extract(m, dest)
    print("extracted ->", dest)
    print(os.listdir(dest))
