#!/usr/bin/env python3
"""2D lattice HP fold. Brute geometry, sequence only scores."""
import sys

DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


class LatticeFolding:
    def __init__(self, sequence):
        self.sequence = sequence.upper()
        self.n = len(self.sequence)
        self.best_contacts = -1
        self.best_path = []
        self.seen = 0
        self.limit = 0

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

    def fold(self, limit=0):
        self.limit = limit
        self.seen = 0
        self.best_contacts = -1
        self.best_path = []
        start = (0, 0)
        self._search([start], {start})
        return self.best_contacts, self.best_path

    def _search(self, path, visited):
        if self.limit and self.seen >= self.limit:
            return
        if len(path) == self.n:
            self.seen += 1
            c = self.count_contacts(path)
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
            self._search(path, visited)
            path.pop()
            visited.remove(nxt)

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
        m = [[ "." for _ in range(n)] for _ in range(n)]
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
    seq = sys.argv[1] if len(sys.argv) > 1 else "HPPHPH"
    limit = 0
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    fold = LatticeFolding(seq)
    contacts, path = fold.fold(limit=limit)
    print("[*] seq", fold.sequence, "len", fold.n)
    print("[*] walks scored", fold.seen, "limit", limit or "none")
    print("[*] best HH contacts", contacts)
    print("[+] fold")
    print(fold.render_ascii(path))
    print("[+] contact map (* = non-chain HH)")
    print(fold.contact_map(path))


if __name__ == "__main__":
    main()
