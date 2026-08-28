---
name: living-notes
description: Epigenetic iteration. Treat notes and code as expression that changes after runtime failures. Use after a parse error, missing pip, failed clone, or wrong mental model. Writes into notes/expression.json. Pairs with ClawBio or scientific-agent-skills in the local loop.
---

# living-notes

DNA (the map) stays. Expression (this file) mutates.

## Process

1. Append the raw error to `failures`.
2. Promote the last failure into a new `ghost_gaps` entry with status `expressed`.
3. Do not delete structural genes to hide a mistake.
4. Next session starts from the mutated JSON, not from a clean README.

## Local loop drop-ins

- https://github.com/ClawBio/ClawBio
- https://github.com/K-Dense-AI/scientific-agent-skills
- Existing Peekabot runtimes. pythonista-one-cut, NullClaw, autonomous-agentic-node.

## Run

```
python3 scripts/run_agent.py living-notes --error "ImportError: Bio"
```
