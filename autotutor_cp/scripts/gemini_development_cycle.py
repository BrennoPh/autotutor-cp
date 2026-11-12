#!/usr/bin/env python3
"""Run a bounded Gemini role cycle; use --dry-run before --live."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.development_cycle import DevelopmentCycle, append_project_handoff, project_memory
from core.research.provider import ResearchConfig


def main():
    parser = argparse.ArgumentParser(description='Ciclo Gemini: analista -> implementador -> revisor -> coordenador.')
    parser.add_argument('--task', required=True, help='Objetivo concreto desta execução.')
    parser.add_argument('--cycles', type=int, default=1, help='Rodadas, de 1 a 12.')
    parser.add_argument('--live', action='store_true', help='Envia chamadas ao Gemini configurado. Sem esta opção é simulação.')
    parser.add_argument('--append-handoff', action='store_true', help='Anexa somente o resultado final à memória do projeto.')
    parser.add_argument('--delay', type=float, default=15, help='Espera mínima entre chamadas Gemini ao vivo.')
    args = parser.parse_args()
    if not 0 <= args.delay <= 60:
        parser.error('--delay deve ficar entre 0 e 60 segundos.')

    if args.live:
        config = ResearchConfig.from_env()
        if not config.enabled or config.provider != 'Gemini' or not config.api_key:
            parser.error('Configure LLM_PROVIDER=Gemini e LLM_API_KEY/GEMINI_API_KEY antes de usar --live.')
        from core.llm_client import LLMClient
        client = LLMClient('Gemini', config.api_key, config.model, require_model=True)
        last_call = [0.0]

        def ask(system, prompt):
            wait = args.delay - (time.monotonic() - last_call[0])
            if last_call[0] and wait > 0:
                time.sleep(wait)
            answer = client.complete(system, prompt, include_history=False)
            last_call[0] = time.monotonic()
            if answer is None:
                raise RuntimeError('Gemini não retornou uma proposta válida.')
            return answer
    else:
        def ask(system, prompt):
            return ('SIMULAÇÃO LOCAL. O papel recebeu o contexto anterior e propõe uma tarefa verificável. '
                    'Use --live para consultar o Gemini; esta saída não representa resposta do modelo.')

    result = DevelopmentCycle(ask).run(args.task, cycles=args.cycles, memory=project_memory())
    if args.append_handoff:
        result['project_handoff'] = str(append_project_handoff(result))
    print(json.dumps({'run_id': result['run_id'], 'directory': result['directory'],
                      'project_handoff': result.get('project_handoff'), 'mode': 'live' if args.live else 'dry-run'}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('Erro no ciclo: ' + str(exc), file=sys.stderr)
        raise SystemExit(1)
