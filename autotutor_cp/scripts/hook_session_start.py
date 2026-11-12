#!/usr/bin/env python3
"""Hook executado automaticamente pelo Antigravity ao iniciar uma sessão de chat."""
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
STATE_FILE = BASE_DIR / ".ai-memory" / "handoffs" / "pipeline_state.json"

if STATE_FILE.exists():
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        print("\n" + "=" * 70)
        print("⚡ [AutoTutor SDLC Bus · Barramento de Integração Contínua]")
        print(f"📌 Feature Atual:  {data.get('current_feature', 'N/A')}")
        print(f"🎯 Estágio Ativo:  {data.get('active_stage', 'N/A')} (Status: {data.get('status', 'N/A')})")
        print(f"📤 Último Output:  {data.get('last_output_by', 'N/A')}")
        print(f"👉 Próxima Ação:   {data.get('next_action', 'N/A')}")
        if data.get('artifacts', {}).get('feedback'):
            print(f"🔍 Feedback/Logs:  {data['artifacts']['feedback'][:180]}...")
        print("=" * 70 + "\n")
    except Exception as e:
        pass
sys.exit(0)
