#!/usr/bin/env python3
# tests/runner.py — smallest smoke. Pythonista tap, iSH CLI, Shortcuts URL.
# Writes notes/last_test.json for Shortcuts to read back.

import json
import os
import sys
from datetime import datetime

try:
    from datetime import timezone
    def now():
        return datetime.now(timezone.utc).isoformat()
except Exception:
    def now():
        return datetime.utcnow().isoformat() + "Z"

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if "__file__" in dir() else os.getcwd()
sys.path.insert(0, os.path.join(HERE, "scans"))
sys.path.insert(0, os.path.join(HERE, "scripts"))
os.chdir(HERE)
OUT = os.path.join(HERE, "notes", "last_test.json")


def write(payload):
    d = os.path.dirname(OUT)
    if not os.path.isdir(d):
        os.makedirs(d)
    payload["ts"] = now()
    with open(OUT, "w") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    print(json.dumps(payload))
    return payload


def test_fold():
    from alpha_code import analyze_structure
    target = os.path.join(HERE, "scans", "gap_scanner.py")
    folds = analyze_structure(target)
    fold = folds[0] if folds else {}
    ok = fold.get("status") == "folded" and "Gap" in (fold.get("classes") or [])
    return {
        "name": "fold",
        "ok": ok,
        "file": fold.get("file"),
        "classes": fold.get("classes"),
        "functions": fold.get("functions"),
        "imports": fold.get("imports"),
        "error": fold.get("error"),
    }


def test_map():
    from run_agent import sequence_map, load_notes
    sequence_map("genomics-for-builders")
    n = load_notes()
    ok = bool(n.get("structural_genes"))
    return {
        "name": "sequence-map",
        "ok": ok,
        "topic": n.get("topic"),
        "genes": len(n.get("structural_genes") or []),
    }


def test_files():
    need = [
        "scans/alpha_code.py",
        "scans/gap_scanner.py",
        "dashboard.py",
        "notes/expression.json",
    ]
    missing = [p for p in need if not os.path.exists(os.path.join(HERE, p))]
    return {"name": "files", "ok": not missing, "missing": missing}


def run_all():
    results = []
    for fn in (test_files, test_fold, test_map):
        try:
            results.append(fn())
        except Exception as e:
            results.append({"name": fn.__name__, "ok": False, "error": str(e)})
    ok = all(r.get("ok") for r in results)
    return write({"ok": ok, "results": results, "root": HERE})


if __name__ == "__main__":
    run_all()
