#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -x "$SCRIPT_DIR/venv/bin/python" ]; then
  PYTHON_BIN="$SCRIPT_DIR/venv/bin/python"
elif [ -x "$SCRIPT_DIR/siaenv/bin/python" ]; then
  PYTHON_BIN="$SCRIPT_DIR/siaenv/bin/python"
else
  PYTHON_BIN="python3"
fi

"$PYTHON_BIN" atualiza_sentenciados_p2.py
"$PYTHON_BIN" atualiza_visitantes_p2.py
