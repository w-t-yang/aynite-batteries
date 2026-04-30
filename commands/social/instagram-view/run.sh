#!/usr/bin/env bash
# instagram-view — Fetch Instagram profile pictures and generate HTML gallery
# Invoke with: > instagram-view --file ~/accounts.txt [--count 5] [--output ./gallery]
#
# Always exits 0 so Aynite displays the JSON output.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/scripts/generate.py"

OUTPUT=$(python3 "$PYTHON_SCRIPT" "$@" 2>&1) || true
echo "$OUTPUT"
