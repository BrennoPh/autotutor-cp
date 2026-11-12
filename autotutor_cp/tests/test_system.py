import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import DATA_PATH
from core.mini_judge import MiniJudge, JudgeError, normalize_output
from core.problem_bank import load_problems, generate_inputs, validate_input
from core.autocode_engine import AutoCodeEngine
from core.rag_retriever import OIAssistantRAG
from core.codigen_tutor import CodigenTutor


@pytest.fixture
def judge(tmp_path):
    return MiniJudge(tmp_path)


def test_verdicts_and_cleanup(judge):
    case = [{'input':'2\n', 'expected_output':'4\n'}]
    assert judge.judge('#include <iostream>\nint main(){int x;std::cin>>x;std::cout<<2*x;}', case)['verdict'] == 'AC'
    failed = judge.judge('#include <iostream>\nint main(){std::cout<<0;}', case)
    assert failed['verdict'] == 'WA'
    assert failed['failed_test']['test_id'] == 1
    assert failed['failed_test']['input'] == '2\n'
    assert judge.judge('int main(){for(;;){}}', case, .15)['verdict'] == 'TLE'
    assert judge.judge('int main(){return 1;}', case)['verdict'] == 'RE'
    assert judge.judge('this is invalid C++', case)['verdict'] == 'CE'
    assert not list(judge.workspace.iterdir())


def test_missing_compiler_and_empty_tests(judge):
    with patch('core.mini_judge.shutil.which', return_value=None):
        assert 'PATH' in judge.judge('int main(){}', [{'input':'','expected_output':''}])['message']
    with pytest.raises(ValueError):
        judge.judge('int main(){}', [])
    assert normalize_output('a  \r\nb\t\n\n') == 'a\nb'
    assert normalize_output('a b') != normalize_output('a  b')


@pytest.mark.parametrize('problem', load_problems(), ids=lambda p:p['id'])
def test_all_references_differential_and_large(problem, judge):
    validated = AutoCodeEngine(judge=judge).double_validate(problem)
    assert validated['double_validated']
    assert validated['validation']['small_cases'] > 1
    assert {c['strategy'] for c in validated['tests']} == {'small_exhaustive','random_extreme','tle_inducing'}
    assert judge.judge(problem['std_cpp'], validated['tests'])['verdict'] == 'AC'


def test_reject_bad_oracle(judge):
    import copy
    from core.problem_bank import clear_cache
    problem = copy.deepcopy(load_problems()[1])
    problem['brute_cpp'] = '#include <iostream>\nint main(){std::cout<<-99;}'
    try:
        with pytest.raises(JudgeError, match='divergência'):
            AutoCodeEngine(judge=judge).double_validate(problem)
    finally:
        clear_cache()


def test_rag_and_pedagogy():
    problems = load_problems()
    rag = OIAssistantRAG(problems)
    assert rag.retrieve('Prefix Sum soma de prefixos consultas intervalos')[0]['problem']['id'] == 'prefix'
    assert len(rag.retrieve('bfs grafo', exclude_id='graph')) == 3
    tutor = CodigenTutor()
    assert 'graph TD' in tutor.generate_flowchart(problems[0])
    assert '___' in tutor.generate_fill_in_blanks('DP')
    assert 'main(' not in tutor.diagnose_error(problems[0], 'int main(){}', {'verdict':'TLE'})


def test_reject_out_of_contract():
    with pytest.raises((ValueError, StopIteration)):
        validate_input(load_problems()[0], '2 1\n1 3\n1 2\n')


def test_local_adaptation(judge):
    result = AutoCodeEngine(judge=judge).adapt_seed(load_problems()[4], theme='Música')
    assert result['constraints']['n_max'] == 2000
    assert result['double_validated'] and result['origin'] == 'local'


def test_relative_workspace(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = MiniJudge('relative').judge('int main(){return 0;}', [{'input':'', 'expected_output':''}])
    assert result['verdict'] == 'AC'
