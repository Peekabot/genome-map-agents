---
name: alpha-fold
description: AlphaFold-style structural parser for code. Use when a raw 1D script, directory, or unannotated file needs a fold map of classes, functions, imports, and ghost gaps. Writes notes/expression.json.
---

# alpha-fold

1D sequence (source text) → predicted topology (AST graph).
Does not run DeepMind AlphaFold. Same shape of problem.

## Run

iSH:

```
python3 scans/alpha_code.py dashboard.py
python3 scans/alpha_code.py .
```

Pythonista: set in `run.py`

```
MODE = "fold"
TARGET = "dashboard.py"
```

CI folds the repo on every Python push via `.github/workflows/ghost_ci.yml`.
