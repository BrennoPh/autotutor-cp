#!/usr/bin/env python3
"""Bounded AutoTutor development cycle driven by named Antigravity agents."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.development_cycle import AntigravityTransport, DevelopmentCycle, append_project_handoff, project_memory


def main():
    parser = argparse.ArgumentParser(description='Ciclo AntiGravity: analista -> implementador -> revisor -> coordenador.')
    parser.add_argument('--task', required=True, help='Uma tarefa pequena e verificável.')
    parser.add_argument('--cycles', type=int, default=1, help='Rodadas de 1 a 12.')
    parser.add_argument('--live', action='store_true', help='Executa agy usando a sessão AntiGravity já autenticada.')
    parser.add_argument('--append-handoff', action='store_true', help='Salva a proposta final na memória de projeto.')
    parser.add_argument('--timeout', type=int, default=180, help='Tempo máximo por agente, em segundos.')
    args = parser.parse_args()
    if not 30 <= args.timeout <= 900:
        parser.error('--timeout deve ficar entre 30 e 900 segundos.')
    result = DevelopmentCycle(AntigravityTransport(live=args.live, timeout=args.timeout)).run(
        args.task, cycles=args.cycles, memory=project_memory())
    if args.append_handoff:
        result['project_handoff'] = str(append_project_handoff(result))
    print(json.dumps({'run_id': result['run_id'], 'directory': result['directory'],
                      'mode': 'antigravity-live' if args.live else 'antigravity-dry-run',
                      'project_handoff': result.get('project_handoff')}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('Erro no ciclo AntiGravity: ' + str(exc), file=sys.stderr)
        raise SystemExit(1)
