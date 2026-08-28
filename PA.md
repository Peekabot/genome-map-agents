# Immutable ledger on PythonAnywhere

Host: `https://peekabot.pythonanywhere.com`

Phone keeps the working copy. PA keeps the chain. No UPDATE, no DELETE on `/v1/*`.

## PA box (once)

```sh
cd ~/mysite   # or wherever flask_app.py lives
# pull Peekabot/pythonanywhere so ledger.py and flask_app.py are current
# Web tab → Reload
```

SQLite file: `genome_ledger.db` next to `ledger.py`.
Optional: set `GENOME_LEDGER_TOKEN` in the PA WSGI file, then send `X-Ledger-Token`.

## Endpoints

| Method | Path | Role |
|---|---|---|
| POST | `/v1/events` | append `{kind, source, payload}` |
| GET | `/v1/events?kind=test&limit=50` | newest first |
| GET | `/v1/events/<id>` | one row |
| GET | `/v1/head` | latest hash |
| GET | `/v1/verify` | walk sha256 chain |

Old Peekagate `/api/state` is still mutable. Do not put folds there.

## iPhone

After `tests/runner.py`:

```sh
python3 pa_push.py test
python3 pa_push.py expression
```

Shortcuts: Open URL runner, Wait, then a second script `pa_push.py` or Get Contents of URL POST to `/v1/events`.
