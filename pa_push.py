#!/usr/bin/env python3
# pa_push.py — append last_test / expression to Peekagate ledger.
#   python3 pa_push.py
#   python3 pa_push.py test
#   python3 pa_push.py expression

import json
import os
import sys

try:
    from urllib.request import Request, urlopen
except ImportError:
    raise SystemExit("need urllib")

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
BASE = os.environ.get("PEEKAGATE", "https://peekabot.pythonanywhere.com")
TOKEN = os.environ.get("GENOME_LEDGER_TOKEN", "")
SOURCE = os.environ.get("GENOME_SOURCE", "iphone")


def post(kind, payload):
    url = BASE.rstrip("/") + "/v1/events"
    body = json.dumps({"kind": kind, "source": SOURCE, "payload": payload}).encode("utf-8")
    headers = {"Content-Type": "application/json", "X-Source": SOURCE}
    if TOKEN:
        headers["X-Ledger-Token"] = TOKEN
    req = Request(url, data=body, headers=headers)
    try:
        raw = urlopen(req, timeout=20).read().decode("utf-8")
    except Exception as e:
        print("push fail", e)
        print("Reload PA web app after pulling ledger.py + flask_app.py")
        return None
    print(raw)
    return json.loads(raw)


def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def main():
    kind = sys.argv[1] if len(sys.argv) > 1 else "test"
    if kind == "test":
        payload = load_json(os.path.join(HERE, "notes", "last_test.json")) or {"error": "no last_test.json"}
    elif kind == "expression":
        payload = load_json(os.path.join(HERE, "notes", "expression.json")) or {"error": "no expression.json"}
    else:
        payload = {"note": " ".join(sys.argv[1:])}
        kind = "note"
    post(kind, payload)


if __name__ == "__main__":
    main()
