#!/usr/bin/env python3
"""2D lattice HP fold. Brute geometry, sequence only scores."""
import sys

DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def _rot(coords):
    out = [list(coords)]
    for _ in range(3):
        out.append([(y, -x) for x, y in out[-1]])
    return out


def _flip(coords):
    return [
        list(coords),
        [(-x, y) for x, y in coords],
        [(x, -y) for x, y in coords],
        [(-x, -y) for x, y in coords],
    ]


def canon(coords):
    variants = []
    for r in _rot(coords):
        for f in _flip(r):
            mx = min(x for x, _ in f)
            my = min(y for _, y in f)
            variants.append(tuple(sorted((x - mx, y - my) for x, y in f)))
    return min(variants)


def is_bend(path, k):
    """True if residue k is a 90-degree lattice hinge."""
    if k <= 0 or k >= len(path) - 1:
        return False
    ax = path[k][0] - path[k - 1][0]
    ay = path[k][1] - path[k - 1][1]
    bx = path[k + 1][0] - path[k][0]
    by = path[k + 1][1] - path[k][1]
    return ax * bx + ay * by == 0


class LatticeFolding:
    def __init__(self, sequence):
        self.sequence = sequence.upper()
        self.n = len(self.sequence)
        self.best_contacts = -1
        self.best_path = []
        self.seen = 0
        self.limit = 0
        self.bend = None
        self._optima = []

    def count_contacts(self, path):
        index = {c: i for i, c in enumerate(path)}
        n = 0
        for i, (x, y) in enumerate(path):
            if self.sequence[i] != "H":
                continue
            for dx, dy in DIRS:
                j = index.get((x + dx, y + dy))
                if j is not None and j > i + 1 and self.sequence[j] == "H":
                    n += 1
        return n

    def fold(self, limit=0, collect=False, bend=None):
        self.limit = limit
        self.bend = bend
        self.seen = 0
        self.best_contacts = -1
        self.best_path = []
        self._optima = []
        self._search([(0, 0)], {(0, 0)}, collect)
        return self.best_contacts, self.best_path

    def _ok(self, path):
        return self.bend is None or is_bend(path, self.bend)

    def _search(self, path, visited, collect):
        if self.limit and self.seen >= self.limit:
            return
        if len(path) == self.n:
            if not self._ok(path):
                return
            self.seen += 1
            c = self.count_contacts(path)
            if collect:
                self._optima.append((c, list(path)))
            if c > self.best_contacts:
                self.best_contacts = c
                self.best_path = list(path)
            return
        x, y = path[-1]
        for dx, dy in DIRS:
            nxt = (x + dx, y + dy)
            if nxt in visited:
                continue
            visited.add(nxt)
            path.append(nxt)
            self._search(path, visited, collect)
            path.pop()
            visited.remove(nxt)

    def unique_best(self):
        if not self._optima:
            return {}, 0
        best = max(e for e, _ in self._optima)
        uniq = {}
        raw = 0
        for e, p in self._optima:
            if e == best:
                raw += 1
                uniq.setdefault(canon(p), p)
        return uniq, raw

    def render_ascii(self, path):
        if not path:
            return "no fold"
        xs = [p[0] for p in path]
        ys = [p[1] for p in path]
        grid = {}
        for i, (x, y) in enumerate(path):
            grid[(x, y)] = self.sequence[i]
        lines = []
        for y in range(max(ys), min(ys) - 1, -1):
            row = [grid.get((x, y), ".") for x in range(min(xs), max(xs) + 1)]
            lines.append("".join(row))
        return "\n".join(lines)

    def contact_map(self, path):
        n = len(path)
        m = [["." for _ in range(n)] for _ in range(n)]
        index = {c: i for i, c in enumerate(path)}
        for i, (x, y) in enumerate(path):
            m[i][i] = self.sequence[i]
            if self.sequence[i] != "H":
                continue
            for dx, dy in DIRS:
                j = index.get((x + dx, y + dy))
                if j is not None and abs(i - j) > 1 and self.sequence[j] == "H":
                    m[i][j] = "*"
        hdr = "   " + "".join("%2d" % i for i in range(n))
        rows = [hdr]
        for i, row in enumerate(m):
            rows.append("%2d " % i + "".join("%2s" % c for c in row))
        return "\n".join(rows)


def main():
    args = sys.argv[1:]
    seq = "HPPHPH"
    limit = 0
    bend = None
    collect = False
    i = 0
    while i < len(args):
        if args[i] == "--limit" and i + 1 < len(args):
            limit = int(args[i + 1]); i += 2; continue
        if args[i] == "--bend" and i + 1 < len(args):
            bend = int(args[i + 1]); collect = True; i += 2; continue
        if args[i] == "--unique":
            collect = True; i += 1; continue
        if not args[i].startswith("-"):
            seq = args[i]
        i += 1
    fold = LatticeFolding(seq)
    contacts, path = fold.fold(limit=limit, collect=collect, bend=bend)
    print("[*] seq", fold.sequence, "len", fold.n)
    print("[*] bend", bend if bend is not None else "none")
    print("[*] walks scored", fold.seen, "limit", limit or "none")
    print("[*] best HH contacts", contacts)
    if collect:
        uniq, raw = fold.unique_best()
        print("[*] raw paths at best", raw)
        print("[*] unique shapes at best", len(uniq))
        if uniq:
            path = next(iter(uniq.values()))
    print("[+] fold")
    print(fold.render_ascii(path))
    if path:
        print("[+] contact map (* = non-chain HH)")
        print(fold.contact_map(path))


if __name__ == "__main__":
    main()
