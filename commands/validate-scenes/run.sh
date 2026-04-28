#!/bin/bash

# Separate flags from the target file
FLAGS=""
TARGET_FILE=""

for arg in "$@"; do
  if [[ $arg == --* ]]; then
    FLAGS="$FLAGS $arg"
  else
    if [ -z "$TARGET_FILE" ]; then
      TARGET_FILE="$arg"
    fi
  fi
done

# Fallback to active file if no path provided
TARGET_FILE="${TARGET_FILE:-$AYNITE_CURRENT_FILE}"

if [ -z "$TARGET_FILE" ]; then
  echo "❌ Error: No target file specified."
  echo "Usage: >validate-scenes [--fix] <path_to_file.md>"
  exit 1
fi

# Determine script path relative to this run.sh
SCRIPT_PATH="$(dirname "$0")/scripts/validate.py"

# Execute validation with optional flags
python3 "$SCRIPT_PATH" "$TARGET_FILE" $FLAGS
