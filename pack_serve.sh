#!/bin/sh
# iSH: tar without .git, serve for Pythonista fetch
set -e
OUT=${1:-/tmp/genome-map-agents.tar}
tar --exclude='.git' --exclude='__pycache__' -cf "$OUT" .
echo "packed $OUT"
python3 -m http.server 8000
