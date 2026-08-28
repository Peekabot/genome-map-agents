# genome-map-agents

Four sub-agents that treat a technical subject like an unmapped genome.
Smallest cut. Phone is a window. Notes mutate after runtime failure.

## Agents

| Agent | Metaphor | Trigger |
|---|---|---|
| `sequence-map` | structural genes + TOC | first recon of a topic |
| `find-gaps` | ghost / dark regions | isolate unknowns, annotate what unmapped code does |
| `force-cli` | heat-shock | parsers from scratch, no GUI |
| `living-notes` | epigenetic expression | rewrite notes after errors |

## Two-minute start (iSH)

```sh
git clone https://github.com/Peekabot/genome-map-agents.git
cd genome-map-agents
python3 scripts/run_agent.py sequence-map --topic "YOUR_TOPIC"
```

Pythonista: use `pack_serve.sh` then fetch tarball (same pipeline as pythonista-one-cut).

## First piece scripted

`sequence-map` — table of contents from learngenomics.dev + Awesome-Bioinformatics patterns.
Run the other three only after a map exists in `notes/expression.json`.
