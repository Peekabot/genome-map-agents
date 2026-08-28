# genome-map-agents

Four sub-agents + a notes/articles dashboard.
Phone is a window. Same phone != same localhost.
Write to Pythonista `~/Documents`, not Files Provider.

## Dashboard

Pythonista: `fetch_py.py` then open `run.py` (`MODE = "dash"`) and tap Run.
Safari / Pythonista browser: use the printed IP if you are in the other app.
Same app: `http://127.0.0.1:8765/`

iSH:

```sh
python3 dashboard.py 8765
```

Pages: `/` notes · `/articles` · `/new` · `/run` (sequence-map from the form).
Articles live in `notes/articles/*.md`. Living state is `notes/expression.json`.

## Pythonista ingest

Run `fetch_py.py`. Archive:
`https://github.com/Peekabot/genome-map-agents/archive/refs/heads/main.tar.gz`

## iSH → tarball → Pythonista

```sh
git clone --depth 1 https://github.com/Peekabot/genome-map-agents.git
cd genome-map-agents
sh pack_serve.sh .
```

Pythonista: `fetch_any.py http://ISH_INET:8000/genome-map-agents.tar.gz`
Same-phone HTTP flakes → `fetch_py.py` instead.
