#!/usr/bin/env python3
"""Daemon Observador Autônomo (Zero-Touch SDLC Watcher).

Monitora em tempo real o arquivo `.ai-memory/handoffs/pipeline_state.json`.
Assim que uma IA atualiza o estado, o Daemon assume a execução imediatamente:
- NÃO exige copiar e colar nada.
- Envia notificações visuais nativas do Ubuntu desktop (notify-send).
- Executa a etapa seguinte (Backend -> QA -> Frontend) de forma autônoma.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
STATE_FILE = BASE_DIR / ".ai-memory" / "handoffs" / "pipeline_state.json"
HANDOFF_FILE = BASE_DIR / ".ai-memory" / "handoffs" / "projeto-atual.md"


def get_python_exe() -> str:
    venv_py = BASE_DIR / "autotutor_cp" / ".venv" / "bin" / "python3"
    if venv_py.exists():
        return str(venv_py)
    return sys.executable


def notify(title: str, msg: str, urgency: str = "normal"):
    """Emite notificação visual no desktop Linux."""
    try:
        subprocess.run(["notify-send", "-u", urgency, title, msg], check=False)
    except Exception:
        pass


def log(msg: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [AutoTutor Daemon] {msg}", flush=True)


def process_state(data: dict) -> bool:
    stage = data.get("active_stage")
    status = data.get("status")
    feature = data.get("current_feature", "Feature")
    last_by = data.get("last_output_by")

    if status == "APPROVED" or stage == "DONE":
        return False

    log(f"Nova transição detectada: Stage={stage}, Status={status}, Por={last_by}")

    # 1. ESTÁGIO QA (Execução de testes)
    if stage == "QA":
        notify("🧪 AutoTutor QA", f"Executando suíte de testes para: {feature}")
        test_file = data.get("artifacts", {}).get("test_file") or "autotutor_cp/tests/test_study_pages.py"
        test_cmd = [get_python_exe(), "-m", "pytest", test_file, "-v"]
        res = subprocess.run(test_cmd, cwd=str(BASE_DIR), capture_output=True, text=True)

        if res.returncode == 0:
            notify("✅ AutoTutor SDLC", f"Testes 100% APROVADOS para: {feature}")
            data["status"] = "APPROVED"
            data["active_stage"] = "DONE"
            data["last_output_by"] = "QA-Daemon"
            data["artifacts"]["test_status"] = "PASSED"
            data["artifacts"]["feedback"] = "Todos os testes automatizados passaram com sucesso."
            data["next_action"] = "Ciclo finalizado com sucesso. Barramento pronto para nova demanda."
            
            # Registra no handoff Akita
            if HANDOFF_FILE.exists():
                with open(HANDOFF_FILE, "a", encoding="utf-8") as f:
                    f.write(f"\n\n### Entrega Homologada (Zero-Touch Daemon): {feature}\n- Data: {datetime.now().isoformat()}\n- Status: 100% Aprovado\n")
        else:
            notify("❌ AutoTutor QA", f"Falha nos testes. Devolvendo ao Backend...", "critical")
            data["status"] = "FAILED"
            data["active_stage"] = "BACKEND"
            data["last_output_by"] = "QA-Daemon"
            data["artifacts"]["test_status"] = "FAILED"
            data["artifacts"]["feedback"] = (res.stderr or res.stdout)[:500]
            data["next_action"] = "Backend: corrigir erros apontados pelo QA-Daemon."

        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        STATE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return True

    # 2. ESTÁGIO FRONTEND (Validação de Build)
    elif stage == "FRONTEND":
        notify("🎨 AutoTutor Front-End", f"Compilando e validando UI para: {feature}")
        res = subprocess.run(["npx", "tsc", "--noEmit"], cwd=str(BASE_DIR / "frontend"), capture_output=True, text=True)
        if res.returncode == 0:
            notify("✅ Front-End Validado", "TypeScript 100% verde. Encaminhando para QA...")
            data["active_stage"] = "QA"
            data["last_output_by"] = "Frontend-Daemon"
            data["updated_at"] = datetime.now(timezone.utc).isoformat()
            STATE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            return True

    return False


def watch_loop():
    log("Iniciando observador contínuo em segundo plano...")
    notify("⚡ AutoTutor SDLC Daemon", "Observador contínuo ativado (Zero Copy-Paste)")
    last_mtime = 0

    while True:
        try:
            if STATE_FILE.exists():
                mtime = os.path.getmtime(STATE_FILE)
                if mtime != last_mtime:
                    last_mtime = mtime
                    content = STATE_FILE.read_text(encoding="utf-8")
                    try:
                        state_data = json.loads(content)
                        if process_state(state_data):
                            last_mtime = os.path.getmtime(STATE_FILE)
                    except json.JSONDecodeError:
                        pass
            time.sleep(1.0)
        except KeyboardInterrupt:
            break
        except Exception as e:
            log(f"Erro no loop: {e}")
            time.sleep(2.0)


if __name__ == "__main__":
    watch_loop()
