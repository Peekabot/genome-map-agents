#!/usr/bin/env python3
"""Tiny fold target. One file, three names."""
import json
import os


class Gap:
    def __init__(self, name):
        self.name = name


def load_gaps(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        data = json.load(f)
    return data.get("ghost_gaps") or []


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gaps = load_gaps(os.path.join(root, "notes", "expression.json"))
    print("gaps", len(gaps))
    for g in gaps:
        print(" -", g.get("id", g))


if __name__ == "__main__":
    main()
