#!/bin/sh
# pack_serve.sh — iSH or PC. Pack folder or clone, tar.gz, HTTP serve.
# usage:
#   sh pack_serve.sh
#   sh pack_serve.sh /path/to/dir
#   sh pack_serve.sh https://github.com/Peekabot/genome-map-agents.git
#   sh pack_serve.sh URL_OR_DIR 8000

set -e
SRC="${1:-.}"
PORT="${2:-8000}"
STAGING="${TMPDIR:-/tmp}/ps_$$"
mkdir -p "$STAGING"
trap 'rm -rf "$STAGING"' EXIT

if echo "$SRC" | grep -qE '^https?://|^git@'; then
  git clone --depth 1 "$SRC" "$STAGING/src"
  NAME=$(basename "$SRC" .git)
else
  cp -R "$SRC" "$STAGING/src"
  NAME=$(basename "$(cd "$SRC" && pwd)")
fi

rm -rf "$STAGING/src/.git"
tar -C "$STAGING" -czf "$STAGING/${NAME}.tar.gz" src
cd "$STAGING"
IP=$(ip route get 1 2>/dev/null | awk '{print $7; exit}' || true)
[ -z "$IP" ] && IP=$(ifconfig 2>/dev/null | awk '/inet / && $2 !~ /^127/ {print $2; exit}')
[ -z "$IP" ] && IP=127.0.0.1
echo "GET http://${IP}:${PORT}/${NAME}.tar.gz"
echo "Pythonista must use that IP, not 127.0.0.1"
echo "Ctrl-C when Pythonista finishes"
python3 -m http.server "$PORT"
