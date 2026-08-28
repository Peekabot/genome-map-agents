---
name: force-cli
description: Heat-shock practice on iSH or Pythonista. Raw FASTA parser is the default. BioPython is optional and usually absent on the phone. No GUIs, no notebooks.
---

# force-cli

Fifteen minutes max. CLI or Pythonista console only.

## Rules

- Default parser is the raw one in `scripts/run_agent.py`. No Bio import required.
- If Bio is missing, log it and keep going. That is the heat-shock.
- NCBI download stays an iSH command. Do not wrap it for Pythonista.

## Run

Pythonista: set `AGENT = "force-cli"` in `run.py` and tap Run.

iSH:

```
python3 scripts/run_agent.py force-cli --query "N-runs"
```
