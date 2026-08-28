#!/usr/bin/env python3
# fold_geom.py — brute force folding through geometry.
# 2D lattice HP. Sequence of H/P. Enumerate self-avoiding walks.
#   python3 scans/fold_geom.py HPPHPH
#   python3 scans/fold_geom.py HHPHHPHH --limit 200000

import sys

DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def contacts(seq, coords):
    index = {c: i for i, c in enumerate(coords)}
    n = 0
    for i, (x, y) in enumerate(coords):
        if seq[i] != "H":
            continue
        for dx, dy in DIRS:
            j = index.get((x + dx, y + dy))
            if j is not None and j > i + 1 and seq[j] == "H":
                n += 1
    return n


def brute(seq, limit=0):
    seq = seq.upper()
    if any(c not in "HP" for c in seq):
        raise SystemExit("sequence must be H/P only")
    best_e, best, seen = -1, None, 0

    def walk(coords, occupied):
        nonlocal best_e, best, seen
        if limit and seen >= limit:
            return
        if len(coords) == len(seq):
            seen += 1
            e = contacts(seq, coords)
            if e > best_e:
                best_e, best = e, list(coords)
            return
        x, y = coords[-1]
        for dx, dy in DIRS:
            nxt = (x + dx, y + dy)
            if nxt in occupied:
                continue
            occupied.add(nxt)
            coords.append(nxt)
            walk(coords, occupied)
            coords.pop()
            occupied.remove(nxt)

    origin = (0, 0)
    walk([origin], {origin})
    return best_e, best, seen


def draw(seq, coords):
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    grid = {}
    for i, (x, y) in enumerate(coords):
        grid[(x, y)] = seq[i]
    lines = []
    for y in range(max(ys), min(ys) - 1, -1):
        row = []
        for x in range(min(xs), max(xs) + 1):
            row.append(grid.get((x, y), "."))
        lines.append("".join(row))
    return "\n".join(lines)


def main():
    seq = sys.argv[1] if len(sys.argv) > 1 else "HPPHPH"
    limit = 0
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    e, coords, seen = brute(seq, limit)
    print("[*] seq", seq, "len", len(seq))
    print("[*] walks scored", seen)
    print("[*] best HH contacts", e)
    if coords:
        print("[*] coords", coords)
        print(draw(seq, coords))
    print("[*] geometry is the search space. sequence is the scoring rule.")


if __name__ == "__main__":
    main()
