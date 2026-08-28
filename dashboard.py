#!/usr/bin/env python3
# dashboard.py — notes + articles. stdlib only. iSH and Pythonista.
#   python3 dashboard.py
#   python3 dashboard.py 8765
# Phone: open the printed IP, not 127.0.0.1 from the other app.

import json
import os
import socket
import sys
from datetime import datetime

try:
    from datetime import timezone
    def now():
        return datetime.now(timezone.utc).isoformat()
except Exception:
    def now():
        return datetime.utcnow().isoformat() + "Z"

try:
    from urllib.parse import parse_qs, unquote
except ImportError:
    from urlparse import parse_qs, unquote  # noqa: F401

from http.server import BaseHTTPRequestHandler, HTTPServer

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
NOTES = os.path.join(HERE, "notes", "expression.json")
ART_DIR = os.path.join(HERE, "notes", "articles")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765


def load_notes():
    if os.path.exists(NOTES):
        with open(NOTES) as f:
            return json.load(f)
    return {
        "topic": None,
        "structural_genes": [],
        "ghost_gaps": [],
        "interfaces": [],
        "failures": [],
        "updated": None,
    }


def save_notes(data):
    data["updated"] = now()
    d = os.path.dirname(NOTES)
    if not os.path.isdir(d):
        os.makedirs(d)
    with open(NOTES, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def list_articles():
    if not os.path.isdir(ART_DIR):
        os.makedirs(ART_DIR)
    out = []
    for name in sorted(os.listdir(ART_DIR)):
        if name.endswith(".md") or name.endswith(".txt"):
            path = os.path.join(ART_DIR, name)
            title = name.rsplit(".", 1)[0].replace("-", " ")
            try:
                with open(path) as f:
                    first = f.readline().strip().lstrip("# ").strip()
                if first:
                    title = first
            except Exception:
                pass
            out.append({"slug": name, "title": title})
    return out


def read_article(slug):
    slug = os.path.basename(slug)
    path = os.path.join(ART_DIR, slug)
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        return f.read()


def write_article(title, body):
    if not os.path.isdir(ART_DIR):
        os.makedirs(ART_DIR)
    slug = "".join(c if c.isalnum() or c in "-_" else "-" for c in title.lower()).strip("-")
    if not slug:
        slug = "note-" + now().replace(":", "").replace("-", "")[:15]
    if not slug.endswith(".md"):
        slug += ".md"
    path = os.path.join(ART_DIR, slug)
    with open(path, "w") as f:
        f.write("# " + title + "\n\n" + body + "\n")
    return slug


def esc(s):
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def md_lite(text):
    lines = []
    for raw in text.splitlines():
        t = raw.rstrip()
        if t.startswith("# "):
            lines.append("<h1>%s</h1>" % esc(t[2:]))
        elif t.startswith("## "):
            lines.append("<h2>%s</h2>" % esc(t[3:]))
        elif t.startswith("- "):
            lines.append("<div class='li'>• %s</div>" % esc(t[2:]))
        elif t.startswith("http://") or t.startswith("https://"):
            lines.append('<p><a href="%s">%s</a></p>' % (esc(t), esc(t)))
        elif not t:
            lines.append("<br>")
        else:
            lines.append("<p>%s</p>" % esc(t))
    return "\n".join(lines)


CSS = """
:root { --bg:#0d0f12; --card:#161a20; --fg:#e8eaed; --mut:#8b93a0; --acc:#7dd3a8; --line:#2a313c; }
* { box-sizing:border-box; }
body { margin:0; font:16px/1.45 -apple-system,system-ui,sans-serif; background:var(--bg); color:var(--fg); }
header { padding:16px 18px; border-bottom:1px solid var(--line); position:sticky; top:0; background:var(--bg); }
header a { color:var(--acc); text-decoration:none; margin-right:14px; }
h1,h2 { font-size:18px; margin:0 0 8px; }
main { padding:16px 18px 48px; max-width:720px; }
.card { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:12px 14px; margin:0 0 12px; }
.mut { color:var(--mut); font-size:13px; }
row { display:block; padding:6px 0; border-bottom:1px solid var(--line); }
row:last-child { border-bottom:0; }
input,textarea { width:100%; background:#0d0f12; color:var(--fg); border:1px solid var(--line); border-radius:8px; padding:10px; font:inherit; }
textarea { min-height:120px; }
button { background:var(--acc); color:#0d0f12; border:0; border-radius:8px; padding:10px 14px; font-weight:600; }
.li { padding:2px 0; }
a { color:var(--acc); }
"""


def page(title, body):
    return (
        "<!doctype html><meta name=viewport content='width=device-width,initial-scale=1'>"
        "<title>%s</title><style>%s</style>"
        "<header><a href='/'>notes</a><a href='/articles'>articles</a>"
        "<a href='/new'>new</a><a href='/run'>run map</a></header>"
        "<main>%s</main>" % (esc(title), CSS, body)
    )


def home():
    n = load_notes()
    bits = ["<div class='card'><h1>%s</h1><div class='mut'>updated %s</div></div>" % (
        esc(n.get("topic") or "no topic yet — run sequence-map"),
        esc(n.get("updated") or "—"),
    )]
    for key, label in (
        ("structural_genes", "structural genes"),
        ("ghost_gaps", "ghost gaps"),
        ("interfaces", "interfaces"),
        ("failures", "failures / expression"),
    ):
        items = n.get(key) or []
        rows = []
        for it in items:
            if isinstance(it, dict):
                rows.append("<row>%s</row>" % esc(json.dumps(it, ensure_ascii=False)))
            else:
                rows.append("<row>%s</row>" % esc(it))
        bits.append(
            "<div class='card'><h2>%s (%d)</h2>%s</div>"
            % (label, len(items), "".join(rows) or "<div class='mut'>empty</div>")
        )
    arts = list_articles()
    bits.append(
        "<div class='card'><h2>articles (%d)</h2>%s</div>"
        % (
            len(arts),
            "".join("<row><a href='/a/%s'>%s</a></row>" % (esc(a["slug"]), esc(a["title"])) for a in arts)
            or "<div class='mut'>none</div>",
        )
    )
    return page("notes", "".join(bits))


def articles_page():
    arts = list_articles()
    body = "<div class='card'><h1>articles</h1>" + (
        "".join("<row><a href='/a/%s'>%s</a></row>" % (esc(a["slug"]), esc(a["title"])) for a in arts)
        or "<div class='mut'>none yet</div>"
    ) + "</div>"
    return page("articles", body)


def article_page(slug):
    text = read_article(slug)
    if text is None:
        return page("missing", "<div class='card'>not found</div>")
    return page(slug, "<div class='card'>%s</div>" % md_lite(text))


def new_page(msg=""):
    extra = ("<div class='mut'>%s</div>" % esc(msg)) if msg else ""
    return page(
        "new",
        extra
        + "<div class='card'><h1>new article</h1>"
        + "<form method=post action='/new'>"
        + "<p><input name=title placeholder='title'></p>"
        + "<p><textarea name=body placeholder='markdown or plain'></textarea></p>"
        + "<p><button>save article</button></p></form></div>"
        + "<div class='card'><h1>append gap</h1>"
        + "<form method=post action='/gap'>"
        + "<p><input name=query placeholder='unknown / ghost region'></p>"
        + "<p><button>isolate gap</button></p></form></div>",
    )


def run_page():
    return page(
        "run",
        "<div class='card'><h1>run map</h1>"
        "<form method=post action='/run'>"
        "<p><input name=topic placeholder='topic' value='genomics-for-builders'></p>"
        "<p><button>sequence-map this topic</button></p></form>"
        "<p class='mut'>writes notes/expression.json then bounce home</p></div>",
    )


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


class H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stdout.write("%s\n" % (fmt % args))

    def _ok(self, html):
        raw = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _redir(self, loc):
        self.send_response(303)
        self.send_header("Location", loc)
        self.end_headers()

    def _form(self):
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n).decode("utf-8", "replace") if n else ""
        q = parse_qs(raw, keep_blank_values=True)
        return {k: (v[0] if v else "") for k, v in q.items()}

    def do_GET(self):
        path = unquote(self.path.split("?", 1)[0])
        if path == "/":
            return self._ok(home())
        if path == "/articles":
            return self._ok(articles_page())
        if path == "/new":
            return self._ok(new_page())
        if path == "/run":
            return self._ok(run_page())
        if path.startswith("/a/"):
            return self._ok(article_page(path[3:]))
        self.send_error(404)

    def do_POST(self):
        path = unquote(self.path.split("?", 1)[0])
        form = self._form()
        if path == "/new":
            title = (form.get("title") or "untitled").strip()
            body = form.get("body") or ""
            write_article(title, body)
            return self._redir("/articles")
        if path == "/gap":
            q = (form.get("query") or "").strip()
            if q:
                data = load_notes()
                data.setdefault("ghost_gaps", []).append(
                    {"id": q.replace(" ", "-")[:40], "query": q, "status": "isolated"}
                )
                save_notes(data)
            return self._redir("/")
        if path == "/run":
            topic = (form.get("topic") or "genomics-for-builders").strip()
            sys.path.insert(0, os.path.join(HERE, "scripts"))
            from run_agent import sequence_map
            sequence_map(topic)
            return self._redir("/")
        self.send_error(404)


def main():
    if not os.path.isdir(ART_DIR):
        os.makedirs(ART_DIR)
    print("notes", NOTES)
    print("articles", ART_DIR)
    print("this app  http://127.0.0.1:%s/" % PORT)
    for ip in ips():
        print("other app http://%s:%s/" % (ip, PORT))
    HTTPServer(("0.0.0.0", PORT), H).serve_forever()


if __name__ == "__main__":
    main()
