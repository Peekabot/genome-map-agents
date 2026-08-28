---
name: find-gaps
description: Isolate unknown regions after a sequence-map exists. Use to flag ghost DNA, unmapped functions, or code whose behavior is not annotated. Patterns from DeepVariant and eggnog-mapper — isolate then annotate, do not run full pipelines by default.
---

# find-gaps

Requires `notes/expression.json` with a topic from sequence-map.

## Process

1. Refuse to run if `topic` is null.
2. Take one query (function, file, concept) as an unmapped locus.
3. Append a gap record. Status starts at `isolated`.
4. Annotation means a one-line guess of what the unknown does, plus which tool-pattern would confirm it.
5. Do not install DeepVariant or eggnog-mapper unless the user explicitly asks. The pattern is isolate-then-label.

## Patterns

- DeepVariant — treat messy input as something to call, not to memorize.
- eggnog-mapper — assign a function to an unknown by orthology / analogy.

## Run

```
python3 scripts/run_agent.py find-gaps --query "VCF FILTER field"
```
