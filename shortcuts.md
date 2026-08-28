# Shortcuts → Pythonista test runner

Do not hit `127.0.0.1` from Shortcuts. That is not Pythonista.
Two paths: URL scheme (reliable) and HTTP (only if the dash is already running and you have a device inet).

## A. URL scheme (use this)

1. Keep Pythonista running once so the script path exists.
2. New Shortcut, one action: **Open URL**

If you used `fetch_py.py` (GitHub tar):

```
pythonista3://run?script=incoming/genome-map-agents-main/tests/runner.py
```

If you used iSH `pack_serve` (`src/`):

```
pythonista3://run?script=incoming/src/tests/runner.py
```

3. Optional second action after a 2s **Wait**: **Get File**
   `On My iPhone/Pythonista 3/incoming/.../notes/last_test.json`
4. **Get Dictionary from Input** → show `ok`.

Add to Home Screen. That is the test trigger.

## B. HTTP (dash must already be up)

Pythonista `run.py` with `MODE = "dash"`. Leave it running.
Shortcut **Get Contents of URL** (GET):

```
http://PHONE_INET:8765/api/test
http://PHONE_INET:8765/api/health
http://PHONE_INET:8765/api/last
http://PHONE_INET:8765/api/fold
```

`PHONE_INET` is the line dashboard prints that is not 127.0.0.1.
If there is no inet, use path A.

## Response shape

```json
{"ok": true, "results": [{"name": "files", "ok": true}, {"name": "fold", "ok": true}, {"name": "sequence-map", "ok": true}]}
```
