#!/bin/bash
# Compatibility entry. All commands share the native Windows/macOS Python CLI.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
exec "${ADU_PYTHON:-python3}" -X utf8 "$HERE/pipeline.py" "$@"
