import json
from pathlib import Path

from core.development_cycle import DevelopmentCycle, ROLES, project_memory, sanitize


def test_role_cycle_passes_each_response_to_the_next_role_and_writes_handoff(tmp_path):
    calls = []

    def ask(system, prompt):
        calls.append((system, prompt))
        return 'resposta-' + str(len(calls))

    result = DevelopmentCycle(ask, tmp_path).run('Melhorar a explicação de BFS', cycles=2, memory='Memória de teste')
    assert len(calls) == len(ROLES) * 2
    assert 'resposta-1' in calls[1][1]
    assert 'resposta-4' in calls[4][1]
    assert result['cycles'][-1]['next_task'] == 'resposta-8'
    saved = json.loads((Path(result['directory']) / 'ciclo-01.json').read_text(encoding='utf-8'))
    assert saved['turns'][0]['role'] == 'analista'
    assert (Path(result['directory']) / 'handoff.md').is_file()


def test_cycle_sanitizes_secrets_and_bounds_cycles(tmp_path):
    assert 'SECRET' not in sanitize('api_key=SECRET')
    cycle = DevelopmentCycle(lambda _s, _p: 'ok', tmp_path)
    try:
        cycle.run('x', cycles=13, memory='m')
    except ValueError as exc:
        assert '1 a 12' in str(exc)
    else:
        raise AssertionError('O limite de ciclos deveria ser aplicado.')


def test_project_memory_loads_the_durable_handoff():
    memory = project_memory()
    assert 'AutoTutor' in memory
    assert 'dado sensível removido' not in memory
