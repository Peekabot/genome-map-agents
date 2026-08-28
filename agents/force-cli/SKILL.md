---
name: force-cli
description: Heat-shock practice. Build a parser from scratch with BioPython or raw text. Pull data with ncbi-genome-download style CLI. No GUIs, no notebooks, no autocomplete-as-crutch. Use when memory pathways need stress.
---

# force-cli

Tight constraint session. Fifteen minutes max.

## Rules

- CLI only.
- Write or run a parser. Do not open a genome browser.
- If BioPython is missing, that ImportError is the heat-shock. Log it via living-notes.
- NCBI hint stays a command, not a wrapper app.

## Default cut

Parse a tiny FASTA string. Count N bases as ghost sequence. Log the handshake raw-fasta → gap-count into `interfaces`.

## Run

```
pip install biopython   # optional
python3 scripts/run_agent.py force-cli --query "N-runs"
```

NCBI (optional, large):

```
ncbi-genome-download --genera Escherichia --format fasta bacteria
```
