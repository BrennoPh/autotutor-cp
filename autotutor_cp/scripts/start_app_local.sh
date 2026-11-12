#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
AI_PID=''
cleanup() { if [[ -n "$AI_PID" ]]; then kill "$AI_PID" 2>/dev/null || true; fi; }
trap cleanup EXIT
trap 'exit 130' INT TERM
if ! curl --noproxy '*' --silent --fail --max-time 2 http://127.0.0.1:11434/api/version >/dev/null; then
    mkdir -p .runtime
    bash scripts/start_local_ai.sh >.runtime/ollama.log 2>&1 &
    AI_PID=$!
    for attempt in {1..30}; do
        if curl --noproxy '*' --silent --fail --max-time 1 http://127.0.0.1:11434/api/version >/dev/null; then break; fi
        if ! kill -0 "$AI_PID" 2>/dev/null; then cat .runtime/ollama.log >&2; exit 1; fi
        sleep 0.5
    done
fi
if [[ -x .venv/bin/python ]]; then PYTHON_BIN=.venv/bin/python; else PYTHON_BIN=python3; fi
"$PYTHON_BIN" -m streamlit run app.py --server.address 127.0.0.1 --server.port 8502 --server.headless true --browser.gatherUsageStats false
