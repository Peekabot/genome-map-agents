---
name: sequence-map
description: First reconnaissance of a technical topic treated as an unmapped genome. Use when starting a subject, building a TOC, or listing structural genes before details. Sources are learngenomics.dev and Awesome-Bioinformatics.
---

# sequence-map

Do not dive into trivia. Scan structure only.

## Process

1. Read the topic like a table of contents, not a textbook.
2. Write 5-8 structural genes into `notes/expression.json` under `structural_genes`.
3. Each gene needs `id`, `name`, `source`.
4. Seed `ghost_gaps` with 2 unnamed holes. Do not fill them here.
5. Stop. Hand off to `find-gaps`.

## Sources (recon only)

- https://github.com/stjude/learngenomics.dev
- https://github.com/danielecook/Awesome-Bioinformatics
- https://github.com/GoekeLab/awesome-genomic-skills

## Run

```
python3 scripts/run_agent.py sequence-map --topic "TOPIC"
```

If the topic is not genomics, keep the same shape. Replace gene names with the subject's core modules and interfaces.
