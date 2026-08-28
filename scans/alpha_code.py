#!/usr/bin/env python3
# alpha_code.py — 1D source → structural map. iSH / Pythonista / CI.
#   python3 scans/alpha_code.py dashboard.py
#   python3 scans/alpha_code.py scans/

import ast
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


def repo_root():
    start = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
    cur = start
    for _ in range(6):
        if os.path.isdir(os.path.join(cur, "notes")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return os.path.dirname(start)


ROOT = repo_root()
NOTES = os.path.join(ROOT, "notes", "expression.json")


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
        "folds": [],
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


def import_names(node):
    out = []
    if isinstance(node, ast.Import):
        for alias in node.names:
            out.append(alias.name)
    elif isinstance(node, ast.ImportFrom):
        mod = node.module or ""
        for alias in node.names:
            out.append(mod + "." + alias.name if mod else alias.name)
    return out


def fold_file(path):
    rel = os.path.relpath(path, ROOT)
    try:
        with open(path) as f:
            src = f.read()
    except Exception as e:
        return {"file": rel, "error": str(e), "status": "unfoldable"}
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return {
            "file": rel,
            "error": "SyntaxError:%s:%s" % (e.lineno, e.msg),
            "status": "misfold",
        }
    fns, cls, imps, calls = [], [], [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            fns.append(node.name)
        elif isinstance(node, ast.ClassDef):
            cls.append(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            imps.extend(import_names(node))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            calls.append(node.func.id)
    ghosts = []
    if not fns and not cls:
        ghosts.append("no functions or classes")
    if "TODO" in src or "FIXME" in src:
        ghosts.append("TODO/FIXME")
    if "pass" in src.split():
        ghosts.append("bare pass")
    return {
        "file": rel,
        "classes": cls,
        "functions": fns,
        "imports": sorted(set(imps)),
        "calls": sorted(set(calls))[:24],
        "ghosts": ghosts,
        "status": "folded",
    }


def walk_target(target):
    if os.path.isfile(target) and target.endswith(".py"):
        return [fold_file(target)]
    out = []
    if os.path.isdir(target):
        for root, dirs, files in os.walk(target):
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "incoming")]
            for name in files:
                if name.endswith(".py"):
                    out.append(fold_file(os.path.join(root, name)))
    return out


def analyze_structure(target_path):
    print("[*] Folding", target_path)
    if not os.path.exists(target_path):
        print("[-] Target not found:", target_path)
        return []
    folds = walk_target(target_path)
    for fold in folds:
        print("[+]", fold.get("file"), fold.get("status"))
        if fold.get("status") == "folded":
            print("    classes:", fold["classes"] or "-")
            print("    functions:", fold["functions"] or "-")
            print("    imports:", fold["imports"] or "-")
            if fold.get("ghosts"):
                print("    ghosts:", fold["ghosts"])
        else:
            print("    error:", fold.get("error"))
    data = load_notes()
    data["folds"] = folds
    for fold in folds:
        if fold.get("status") != "folded":
            data.setdefault("failures", []).append(
                {"step": "alpha_code", "file": fold.get("file"), "error": fold.get("error")}
            )
        for g in fold.get("ghosts") or []:
            data.setdefault("ghost_gaps", []).append(
                {"id": (fold.get("file") or "") + ":" + g, "status": "isolated", "from": "alpha_code"}
            )
        if fold.get("imports"):
            data.setdefault("interfaces", []).append(
                {"from": fold.get("file"), "to": fold["imports"], "kind": "import"}
            )
    save_notes(data)
    print("[*] wrote", NOTES)
    return folds


if __name__ == "__main__":
    raw = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "scans")
    target = raw if os.path.isabs(raw) else os.path.join(os.getcwd(), raw)
    if not os.path.exists(target):
        target = os.path.join(ROOT, raw)
    analyze_structure(target)
