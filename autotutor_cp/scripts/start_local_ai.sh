#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -x "$ROOT/.runtime/ollama/bin/ollama" ]]; then
    OLLAMA_BIN="$ROOT/.runtime/ollama/bin/ollama"
elif command -v ollama >/dev/null 2>&1; then
    OLLAMA_BIN="$(command -v ollama)"
else
    echo 'Ollama não encontrado. Instale o Ollama ou extraia o pacote oficial em .runtime/ollama.' >&2
    exit 1
fi
export OLLAMA_HOST=127.0.0.1:11434
export OLLAMA_MODELS="$ROOT/.models"
export OLLAMA_NO_CLOUD=1
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_CONTEXT_LENGTH=4096
export OLLAMA_KEEP_ALIVE=0
exec "$OLLAMA_BIN" serve
