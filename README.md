# genome-map-agents

Four sub-agents. Phone is a window. Same phone != same localhost.
Write to Pythonista `~/Documents`, not Files Provider.

## Pythonista (no iSH hop)

1. Run `fetch_py.py` as-is.
2. Open `incoming/genome-map-agents-main/run.py`.
3. Edit `AGENT` / `TOPIC` at the top. Run.

Direct archive:
`https://github.com/Peekabot/genome-map-agents/archive/refs/heads/main.tar.gz`

## iSH → tarball → Pythonista

```sh
cd ~
git clone --depth 1 https://github.com/Peekabot/genome-map-agents.git
cd genome-map-agents
sh pack_serve.sh .
# print inet from ifconfig — not 127.0.0.1
```

Pythonista: `fetch_any.py http://ISH_INET:8000/genome-map-agents.tar.gz`

Same-phone HTTP often refuses. Then skip pack_serve and use `fetch_py.py` (GitHub direct).

## iSH CLI

```sh
python3 run.py
python3 scripts/run_agent.py sequence-map --topic "genomics-for-builders"
python3 scripts/run_agent.py find-gaps --query "VCF FILTER"
python3 scripts/run_agent.py force-cli --query "N-runs"
python3 scripts/run_agent.py living-notes --error "paste error"
```

No pip required. BioPython is optional heat-shock, not a dependency.
Notes live in `notes/expression.json`.
