#!/usr/bin/env python3
"""Dispatch one sub-agent. Two-minute start."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "notes" / "expression.json"
AGENTS = ("sequence-map", "find-gaps", "force-cli", "living-notes")


def load_notes():
    if NOTES.exists():
        return json.loads(NOTES.read_text())
    return {
        "topic": None,
        "structural_genes": [],
        "ghost_gaps": [],
        "interfaces": [],
        "failures": [],
        "updated": None,
    }


def save_notes(data):
    data["updated"] = datetime.now(timezone.utc).isoformat()
    NOTES.parent.mkdir(parents=True, exist_ok=True)
    NOTES.write_text(json.dumps(data, indent=2) + "\n")


def sequence_map(topic):
    data = load_notes()
    data["topic"] = topic
    # Structural genes = recon headings, not trivia.
    data["structural_genes"] = [
        {"id": "formats", "name": "sequence formats (FASTA/FASTQ/VCF)", "source": "learngenomics.dev"},
        {"id": "alignment", "name": "alignment vs assembly", "source": "learngenomics.dev"},
        {"id": "variation", "name": "variant calling as gap isolation", "source": "deepvariant pattern"},
        {"id": "annotation", "name": "functional annotation of unknowns", "source": "eggnog-mapper pattern"},
        {"id": "ontology", "name": "when a trait is expressed", "source": "GO / goatools"},
        {"id": "tool-index", "name": "field index", "source": "danielecook/Awesome-Bioinformatics"},
    ]
    if not data["ghost_gaps"]:
        data["ghost_gaps"] = [
            {"id": "unknown-region", "note": "regions with no annotation yet"},
            {"id": "tool-handshake", "note": "how CLI tools pass files between stages"},
        ]
    save_notes(data)
    print("sequence-map wrote", NOTES)
    for g in data["structural_genes"]:
        print(" -", g["id"], "|", g["name"])
    print("next: python3 scripts/run_agent.py find-gaps")


def find_gaps(query):
    data = load_notes()
    if not data.get("topic"):
        print("no map yet. run sequence-map first.")
        return
    gap = {
        "id": (query or "unmapped").replace(" ", "-")[:40],
        "query": query,
        "annotate_with": ["eggnog-mapper-pattern", "deepvariant-pattern"],
        "status": "isolated",
    }
    existing = {g.get("id") for g in data["ghost_gaps"]}
    if gap["id"] not in existing:
        data["ghost_gaps"].append(gap)
    save_notes(data)
    print("isolated gap:", gap["id"])
    print("annotation is a note, not a full DeepVariant run.")
    print("next heat-shock: python3 scripts/run_agent.py force-cli --query", gap["id"])


def force_cli(query):
    """Heat-shock: tiny BioPython parse, no GUI. Optional NCBI hint only."""
    data = load_notes()
    recs = []
    try:
        from Bio.Seq import Seq
        from Bio.SeqRecord import SeqRecord
        from Bio import SeqIO
        from io import StringIO

        demo = ">ghost\\nATGCGTNNTAANNGC\\n"
        for rec in SeqIO.parse(StringIO(demo.replace("\\\\n", "\n")), "fasta"):
            n_count = str(rec.seq).upper().count("N")
            recs.append({"id": rec.id, "len": len(rec.seq), "n_count": n_count})
        print("biopython parse ok", recs)
    except ImportError:
        print("biopython missing. pip install biopython  OR treat this as the heat-shock.")
        data["failures"].append({"step": "force-cli", "error": "ImportError: Bio"})
        save_notes(data)
        recs = [{"id": "manual", "note": query or "write parser without Bio"}]

    data["interfaces"].append(
        {
            "from": "raw-fasta",
            "to": "gap-count",
            "query": query,
            "result": recs,
        }
    )
    save_notes(data)
    print("logged interface handshake to notes/expression.json")
    print("NCBI pull (do not wrap in GUI):")
    print("  ncbi-genome-download --genera Escherichia --format fasta bacteria")
    print("next: python3 scripts/run_agent.py living-notes --error 'paste build error'")


def living_notes(error):
    data = load_notes()
    if error:
        data["failures"].append({"error": error, "absorbed": True})
    # Expression changes after failure: promote last failure into a ghost or interface.
    if data["failures"]:
        last = data["failures"][-1]
        gid = "fail-" + str(len(data["failures"]))
        data["ghost_gaps"].append({"id": gid, "from_failure": last, "status": "expressed"})
    save_notes(data)
    print("expression updated. failures now:", len(data["failures"]))
    print(NOTES)


def main():
    p = argparse.ArgumentParser(description="genome-map sub-agent dispatcher")
    p.add_argument("agent", choices=AGENTS)
    p.add_argument("--topic", default="genomics-for-builders")
    p.add_argument("--query", default="")
    p.add_argument("--error", default="")
    args = p.parse_args()
    if args.agent == "sequence-map":
        sequence_map(args.topic)
    elif args.agent == "find-gaps":
        find_gaps(args.query or "unmapped-region")
    elif args.agent == "force-cli":
        force_cli(args.query)
    else:
        living_notes(args.error)


if __name__ == "__main__":
    main()
