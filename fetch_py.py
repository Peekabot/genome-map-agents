# fetch_py.py — run in Pythonista, no edits
import os, tarfile, tempfile, urllib.request

URL = "https://github.com/Peekabot/genome-map-agents/archive/refs/heads/main.tar.gz"
dest = os.path.expanduser("~/Documents/incoming")
os.makedirs(dest, exist_ok=True)
tmp = os.path.join(tempfile.gettempdir(), "genome-map-agents.tar.gz")

def hook(n, bs, total):
    got = n * bs
    if total and total > 0:
        print("\r%3d%%" % min(100, got * 100 // total), end="")
    else:
        print("\r%d bytes" % got, end="")

print("GET", URL)
try:
    urllib.request.urlretrieve(URL, tmp, hook)
except Exception:
    URL = "https://github.com/Peekabot/genome-map-agents/archive/refs/heads/master.tar.gz"
    print("\nretry", URL)
    urllib.request.urlretrieve(URL, tmp, hook)

print("\nextract")
with tarfile.open(tmp, "r:*") as t:
    for m in t.getmembers():
        if ".git" in m.name.replace("\\", "/").split("/"):
            continue
        t.extract(m, dest)

print("done ->", dest)
print(os.listdir(dest))
print("open incoming/genome-map-agents-main/run.py")
