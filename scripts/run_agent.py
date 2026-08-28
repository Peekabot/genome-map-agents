#!/usr/bin/env python3
"""Dispatch one sub-agent. Works in iSH and Pythonista. No Bio required."""
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


def _root():
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


ROOT = _root()
NOTES = os.path.join(ROOT, "notes", "expression.json")
AGENTS = ("sequence-map", "find-gaps", "force-cli", "living-notes")


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


def parse_fasta(text):
    recs = []
    name, buf = None, []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if name is not None:
                seq = "".join(buf).upper()
                recs.append({"id": name, "len": len(seq), "n_count": seq.count("N")})
            name, buf = line[1:].split()[0], []
        else:
            buf.append(line)
    if name is not None:
        seq = "".join(buf).upper()
        recs.append({"id": name, "len": len(seq), "n_count": seq.count("N")})
    return recs


def sequence_map(topic):
    data = load_notes()
    data["topic"] = topic
    data["structural_genes"] = [
        {"id": "formats", "name": "sequence formats (FASTA/FASTQ/VCF)", "source": "learngenomics.dev"},
        {"id": "alignment", "name": "alignment vs assembly", "source": "learngenomics.dev"},
        {"id": "variation", "name": "variant calling as gap isolation", "source": "deepvariant pattern"},
        {"id": "annotation", "name": "functional annotation of unknowns", "source": "eggnog-mapper pattern"},
        {"id": "ontology", "name": "when a trait is expressed", "source": "GO / goatools"},
        {"id": "tool-index", "name": "field index", "source": "danielecook/Awesome-Bioinformatics"},
    ]
    if not data.get("ghost_gaps"):
        data["ghost_gaps"] = [
            {"id": "unknown-region", "note": "regions with no annotation yet"},
            {"id": "tool-handshake", "note": "how CLI tools pass files between stages"},
        ]
    save_notes(data)
    print("sequence-map wrote", NOTES)
    for g in data["structural_genes"]:
        print(" -", g["id"], "|", g["name"])
    print("next AGENT = find-gaps")


def find_gaps(query):
    data = load_notes()
    if not data.get("topic"):
        print("no map yet. set AGENT = sequence-map first.")
        return
    q = query or "unmapped"
    gap = {
        "id": q.replace(" ", "-")[:40],
        "query": q,
        "annotate_with": ["eggnog-mapper-pattern", "deepvariant-pattern"],
        "status": "isolated",
    }
    existing = {g.get("id") for g in data["ghost_gaps"]}
    if gap["id"] not in existing:
        data["ghost_gaps"].append(gap)
    save_notes(data)
    print("isolated gap:", gap["id"])
    print("next AGENT = force-cli")


def force_cli(query):
    data = load_notes()
    demo = ">ghost\nATGCGTNNTAANNGC\n"
    recs = parse_fasta(demo)
    print("raw fasta parse (no Bio)", recs)
    try:
        from Bio.SeqIO import parse as bio_parse  # noqa: F401
        print("Bio present — unused. heat-shock already passed via raw parser.")
    except Exception as e:
        data.setdefault("failures", []).append({"step": "force-cli", "error": type(e).__name__})
        print("Bio absent (expected on Pythonista). raw parser stands.")
    data.setdefault("interfaces", []).append(
        {"from": "raw-fasta", "to": "gap-count", "query": query, "result": recs}
    )
    save_notes(data)
    print("logged handshake", NOTES)
    print("NCBI stays a command in iSH, not a GUI:")
    print("  ncbi-genome-download --genera Escherichia --format fasta bacteria")
    print("next AGENT = living-notes")


def living_notes(error):
    data = load_notes()
    if error:
        data.setdefault("failures", []).append({"error": error, "absorbed": True})
    if data.get("failures"):
        last = data["failures"][-1]
        data.setdefault("ghost_gaps", []).append(
            {"id": "fail-" + str(len(data["failures"])), "from_failure": last, "status": "expressed"}
        )
    save_notes(data)
    print("expression updated. failures:", len(data.get("failures") or []))
    print(NOTES)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    agent = argv[0] if argv else "sequence-map"
    topic, query, error = "genomics-for-builders", "", ""
    i = 1
    while i < len(argv):
        if argv[i] == "--topic" and i + 1 < len(argv):
            topic = argv[i + 1]; i += 2; continue
        if argv[i] == "--query" and i + 1 < len(argv):
            query = argv[i + 1]; i += 2; continue
        if argv[i] == "--error" and i + 1 < len(argv):
            error = argv[i + 1]; i += 2; continue
        i += 1
    if agent == "sequence-map":
        sequence_map(topic)
    elif agent == "find-gaps":
        find_gaps(query or "unmapped-region")
    elif agent == "force-cli":
        force_cli(query)
    elif agent == "living-notes":
        living_notes(error)
    else:
        print("agents:", ", ".join(AGENTS))


if __name__ == "__main__":
    main()
