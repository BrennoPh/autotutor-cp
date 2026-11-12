#!/usr/bin/env python3
"""Hook executado automaticamente pelo Antigravity ao finalizar um turno de chat."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
STATE_FILE = BASE_DIR / ".ai-memory" / "handoffs" / "pipeline_state.json"

if STATE_FILE.exists():
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        data["last_checked_at"] = datetime.now(timezone.utc).isoformat()
        STATE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass
sys.exit(0)
