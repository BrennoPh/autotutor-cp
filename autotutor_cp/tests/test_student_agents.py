"""Synthetic agents test real integration with an explicitly replaced model transport."""
import json
from unittest.mock import patch
import pytest
from core.isolated_judge import isolation_available
from core.research.competencies import specification
from core.research.pipeline import validate_problem
from scripts.run_research_pilot import OfflineFixture
from scripts.validate_student_agents import SCENARIOS, declared_topic_correct, numeric_probe_correct, run_simulation, save_report

@pytest.mark.parametrize('scenario', SCENARIOS, ids=[x['agent'] for x in SCENARIOS])
def test_agent_numeric_probes_use_independent_reference(scenario):
    assert numeric_probe_correct(scenario['target'], scenario['probe'])
    assert not numeric_probe_correct(scenario['target'], {'invented': 99})


def test_agent_topic_contract_check_rejects_misrouting():
    assert declared_topic_correct({'topic': 'Prefix Sum', 'contract_id': 'prefix'}, 'Soma de prefixos')
    assert not declared_topic_correct({'topic': 'DP', 'contract_id': 'prefix'}, 'Soma de prefixos')
    assert not declared_topic_correct({'topic': 'Prefix Sum', 'contract_id': 'dp'}, 'Soma de prefixos')


@pytest.mark.parametrize('field,value', [('topic', 'DP'), ('target_competencies', ['dp_state'])])
def test_backend_rejects_swapped_topic_or_missing_competencies_before_execution(field, value):
    response = json.loads(OfflineFixture('Soma de prefixos').generate('', '').text)
    response[field] = value
    with patch('core.research.pipeline.isolation_available', side_effect=AssertionError('Invalid metadata must never reach execution')):
        report, problem = validate_problem(response, specification('Soma de prefixos'))
    assert problem is None and not report['compiled'] and report['error']


def test_agents_fail_closed_without_execution_sandbox(tmp_path):
    with patch('scripts.validate_student_agents.isolation_available', return_value=False):
        report = run_simulation()
    assert report['status'] == 'blocked' and report['external_calls'] == 0
    save_report(report, tmp_path)
    assert json.loads((tmp_path/'report.json').read_text())['status'] == 'blocked'


@pytest.mark.skipif(not isolation_available(), reason='bubblewrap required; no host execution fallback')
def test_four_students_teacher_and_fault_injection_without_network(tmp_path):
    # Any accidental model/network operation makes this test fail.
    with patch('requests.sessions.Session.request', side_effect=AssertionError('External network forbidden')), patch('urllib.request.urlopen', side_effect=AssertionError('Ollama/network forbidden')):
        report = run_simulation()
    assert report['status'] == 'passed', [x for x in report['checks'] if not x['passed']]
    assert report['temporary_database_destroyed'] and report['external_calls'] == report['ollama_calls'] == 0
    assert len(report['agents']) == 5
    assert all(a['independent_cases'] > 0 for a in report['agents'] if a['role'] == 'student')
    assert 'Seg' not in ' '.join(a.get('target', '') for a in report['agents'])
    save_report(report, tmp_path)
    assert (tmp_path/'report.md').exists()
