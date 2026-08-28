#!/usr/bin/env python3
# fold_mcmc.py — RAM tables + Metropolis on 2D HP lattice.
# Brute is exact for n~6. This is how you go longer without 2.6^n.
#   python3 scans/fold_mcmc.py HHPHHPPHPHHP --steps 8000 --T 0.6

import hashlib
import random
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


def straight(n):
    return [(i, 0) for i in range(n)]


class Ram:
    """Layered old-school RAM: score cache + local 3-bead geometries."""

    def __init__(self):
        self.score = {}
        self.hits = 0
        self.miss = 0
        # 3-mer step pairs that stay self-avoiding locally (no immediate backstep)
        self.frag3 = []
        for a in DIRS:
            for b in DIRS:
                if (a[0] + b[0], a[1] + b[1]) != (0, 0):
                    self.frag3.append((a, b))

    def key(self, coords):
        return tuple(coords)

    def get_score(self, seq, coords):
        k = self.key(coords)
        if k in self.score:
            self.hits += 1
            return self.score[k]
        self.miss += 1
        e = contacts(seq, coords)
        self.score[k] = e
        return e


def end_flip(coords, occupied):
    n = len(coords)
    which = 0 if random.random() < 0.5 else n - 1
    nbr = coords[1] if which == 0 else coords[-2]
    opts = [(nbr[0] + dx, nbr[1] + dy) for dx, dy in DIRS]
    opts = [p for p in opts if p not in occupied or p == coords[which]]
    if not opts:
        return None
    nxt = list(coords)
    nxt[which] = random.choice(opts)
    if len(set(nxt)) != n:
        return None
    return nxt


def corner_flip(coords, occupied):
    n = len(coords)
    if n < 3:
        return None
    i = random.randint(1, n - 2)
    ax, ay = coords[i - 1]
    cx, cy = coords[i + 1]
    # corner if a and c are diagonal (manhattan 2 and not colinear)
    if abs(ax - cx) + abs(ay - cy) != 2:
        return None
    # other corner of the unit square
    cand = (ax + cx - coords[i][0], ay + cy - coords[i][1])
    if cand in occupied:
        return None
    nxt = list(coords)
    nxt[i] = cand
    return nxt


def propose(coords):
    occupied = set(coords)
    if random.random() < 0.5:
        return corner_flip(coords, occupied) or end_flip(coords, occupied)
    return end_flip(coords, occupied) or corner_flip(coords, occupied)


def metropolis(seq, steps=4000, T=0.7, seed=1):
    random.seed(seed)
    seq = seq.upper()
    ram = Ram()
    coords = straight(len(seq))
    e = ram.get_score(seq, coords)
    best_e, best = e, list(coords)
    accept = 0
    for t in range(steps):
        prop = propose(coords)
        if not prop:
            continue
        ep = ram.get_score(seq, prop)
        dE = -(ep - e)  # energy = -contacts; downhill = more contacts
        if dE <= 0 or random.random() < pow(2.718281828, -dE / T):
            coords, e = prop, ep
            accept += 1
            if e > best_e:
                best_e, best = e, list(coords)
    return {
        "best": best_e,
        "best_path": best,
        "final": e,
        "accept": accept,
        "steps": steps,
        "T": T,
        "ram_hits": ram.hits,
        "ram_miss": ram.miss,
        "ram_size": len(ram.score),
        "frag3": len(ram.frag3),
    }


def draw(seq, coords):
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    grid = {(x, y): seq[i] for i, (x, y) in enumerate(coords)}
    lines = []
    for y in range(max(ys), min(ys) - 1, -1):
        lines.append("".join(grid.get((x, y), ".") for x in range(min(xs), max(xs) + 1)))
    return "\n".join(lines)


def main():
    seq = "HHPHHPPHPHHP"
    steps, T, seed = 4000, 0.7, 1
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--steps":
            steps = int(args[i + 1]); i += 2; continue
        if args[i] == "--T":
            T = float(args[i + 1]); i += 2; continue
        if args[i] == "--seed":
            seed = int(args[i + 1]); i += 2; continue
        if not args[i].startswith("-"):
            seq = args[i]
        i += 1
    r = metropolis(seq, steps=steps, T=T, seed=seed)
    print("[*] seq", seq, "n", len(seq))
    print("[*] steps", r["steps"], "T", r["T"], "accept", r["accept"])
    print("[*] RAM hits", r["ram_hits"], "miss", r["ram_miss"], "unique confs", r["ram_size"])
    print("[*] frag3 table", r["frag3"])
    print("[*] best HH", r["best"], "final HH", r["final"])
    print(draw(seq, r["best_path"]))
    print("[*] not exact. MCMC sample + RAM cache. brute still owns n=6.")


if __name__ == "__main__":
    main()
