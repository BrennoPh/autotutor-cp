from copy import deepcopy
from unittest.mock import patch
import pytest
from core.problem_bank import load_problems,generate_inputs,validate_input
from core.autocode_engine import AutoCodeEngine
from core.llm_client import LLMClient,AIUnavailable
from core.mini_judge import MiniJudge,JudgeError


def seed():return next(p for p in load_problems() if p['id']=='segment_tree')


def test_segment_tree_contract_generates_valid_updates_and_range_queries():
    p=seed();p['constraints']['n_max']=16
    cases=generate_inputs(p)
    assert len(cases)>30 and all(validate_input(p,c['input']) for c in cases)
    assert {c['strategy'] for c in cases}=={'small_exhaustive','random_extreme','tle_inducing'}
    for text in ['2 1\n1 2\n2 0 2\n','2 1\n1 2\n1 3 9\n','2 1\n1 2\n3 1 2\n','2 1\n1 2\n2 2 1\n','2 1\n1 2\n1 1 -1\n','2 1\n1 2\n2 1 2\n99']:
        with pytest.raises(ValueError):validate_input(p,text)


@pytest.mark.parametrize('learning_request',['Quero aprender SegTree','SegTreee','Segment Tree com mínimo','árvore de segmentos'])
def test_explicit_segment_tree_cannot_route_to_dp(learning_request):
    llm=LLMClient('Gemini','key','test',require_model=True)
    with patch.object(llm,'complete',return_value=dict(seed_id='dp',focus='DP')),pytest.raises(AIUnavailable):
        AutoCodeEngine(llm).generate_problem(concept='DP',learning_request=learning_request)


def test_request_is_used_for_both_routing_and_generation_without_prior_dp_history(tmp_path):
    p=seed();llm=LLMClient('Gemini','key','test',require_model=True)
    answer={k:p[k] for k in ('title','statement','std_cpp','brute_cpp')}
    with patch.object(llm,'complete',side_effect=[dict(seed_id=p['id'],focus='Segment Tree'),answer]) as complete:
        result=AutoCodeEngine(llm,MiniJudge(tmp_path)).generate_problem(concept='DP',learning_request='Quero estudar SegTree com atualizações e consultas de mínimo')
    assert result['family']=='segtree' and result['topic']=='Segment Tree'
    assert result['validation']['contract_seed_id']=='segment_tree'
    assert all('SegTree' in call.args[1] and call.kwargs['include_history'] is False for call in complete.call_args_list)


def test_two_matching_model_programs_cannot_change_the_original_contract(tmp_path):
    p=seed();p['examples']=[]
    wrong={k:p[k] for k in ('title','statement','std_cpp','brute_cpp')}
    wrong['std_cpp']=wrong['std_cpp'].replace('min(', 'max(').replace('LLONG_MAX','LLONG_MIN')
    wrong['brute_cpp']=wrong['brute_cpp'].replace('min(', 'max(').replace('LLONG_MAX','LLONG_MIN')
    llm=LLMClient('Gemini','key','test',require_model=True)
    with patch.object(llm,'complete',return_value=wrong),pytest.raises(JudgeError,match='objetivo do contrato'):
        AutoCodeEngine(llm,MiniJudge(tmp_path)).adapt_seed(p,concept='Segment Tree')
