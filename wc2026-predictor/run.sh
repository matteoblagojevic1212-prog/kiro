#!/usr/bin/env bash
# Launch the World Cup 2026 Predictor.
cd "$(dirname "$0")" || exit 1
PYTHON=python3
command -v $PYTHON >/dev/null 2>&1 || PYTHON=python
echo "Starting World Cup 2026 Predictor..."
echo "Open http://localhost:${PORT:-8000} in your browser."
exec $PYTHON server.py
