#!/usr/bin/env python3
# minhash_fold.py — neighbor filter, not identity.
#   python3 scans/minhash_fold.py
# Tokens: occupancy + HH contacts + turn shingles. Stable ids, no hash().

import random
import sys
from collections import defaultdict

DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def trans(path):
    mx = min(p[0] for p in path)
    my = min(p[1] for p in path)
    return [(x - mx, y - my) for x, y in path]


def turns(path):
    out = []
    for i in range(1, len(path) - 1):
        a = (path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1])
        b = (path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1])
        cr = a[0] * b[1] - a[1] * b[0]
        d = a[0] * b[0] + a[1] * b[1]
        if cr == 0 and d > 0:
            out.append("S")
        elif cr > 0:
            out.append("L")
        else:
            out.append("R")
    return "".join(out)


def tokens(seq, path):
    p = trans(path)
    s = set()
    for x, y in p:
        s.add("o:%d,%d" % (x, y))
    index = {c: i for i, c in enumerate(p)}
    for i, (x, y) in enumerate(p):
        if seq[i] != "H":
            continue
        for dx, dy in DIRS:
            j = index.get((x + dx, y + dy))
            if j is not None and j > i + 1 and seq[j] == "H":
                s.add("c:%d-%d" % (i, j))
    t = turns(p)
    for i in range(max(0, len(t) - 1)):
        s.add("t:" + t[i : i + 2])
    if t:
        s.add("T:" + t)
    return s


def jaccard(a, b):
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / float(len(a | b))


def tid(token, p=104729):
    n = 0
    for ch in token:
        n = (n * 131 + ord(ch)) % p
    return n


class MinHash:
    def __init__(self, h=32, seed=7):
        rng = random.Random(seed)
        self.p = 104729
        self.h = h
        self.ab = [(rng.randrange(1, self.p), rng.randrange(0, self.p)) for _ in range(h)]

    def sig(self, toks):
        ids = [tid(t, self.p) for t in toks]
        if not ids:
            return tuple(0 for _ in range(self.h))
        out = []
        for a, b in self.ab:
            m = self.p
            for x in ids:
                v = (a * x + b) % self.p
                if v < m:
                    m = v
            out.append(m)
        return tuple(out)

    def est(self, s1, s2):
        return sum(x == y for x, y in zip(s1, s2)) / float(self.h)


def enumerate_paths(seq):
    n = len(seq)
    out = []

    def walk(path, occ):
        if len(path) == n:
            out.append(list(path))
            return
        x, y = path[-1]
        for dx, dy in DIRS:
            q = (x + dx, y + dy)
            if q in occ:
                continue
            occ.add(q)
            path.append(q)
            walk(path, occ)
            path.pop()
            occ.remove(q)

    walk([(0, 0)], {(0, 0)})
    return out


def main():
    seq = sys.argv[1] if len(sys.argv) > 1 else "HPPHPH"
    paths = enumerate_paths(seq)
    step = max(1, len(paths) // 12)
    sample = paths[::step][:12]
    mh = MinHash(32, seed=7)
    feats = [tokens(seq, p) for p in sample]
    sigs = [mh.sig(f) for f in feats]
    pairs = []
    for i in range(len(sample)):
        for j in range(i + 1, len(sample)):
            jac = jaccard(feats[i], feats[j])
            est = mh.est(sigs[i], sigs[j])
            pairs.append((jac, est, abs(jac - est), i, j))
    err = sum(p[2] for p in pairs) / float(len(pairs))
    bands, rows = 8, 4
    buckets = defaultdict(list)
    for i, sig in enumerate(sigs):
        for b in range(bands):
            buckets[(b, sig[b * rows : (b + 1) * rows])].append(i)
    cand = set()
    for ids in buckets.values():
        for a in range(len(ids)):
            for b in range(a + 1, len(ids)):
                cand.add((ids[a], ids[b]))
    near = [p for p in pairs if p[0] >= 0.5]
    hit = sum(1 for p in near if (p[3], p[4]) in cand)
    print("[*] seq", seq, "walks", len(paths), "sample", len(sample))
    print("[*] pairs", len(pairs), "mean |J-MH|", round(err, 4))
    print("[*] LSH candidates", len(cand), "recall J>=0.5", hit, "/", len(near))
    print("[*] neighbor filter only. identity = exact canon / coords.")


if __name__ == "__main__":
    main()
