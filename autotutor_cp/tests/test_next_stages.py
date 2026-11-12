from unittest.mock import patch
import pytest
from core.extended_judge import validate,oracle
from core.problem_bank import load_problems,generate_inputs
from core.autocode_engine import AutoCodeEngine
from core.llm_client import LLMClient
from core.codigen_tutor import CodigenTutor
from core.progress_store import ProgressStore


def test_five_different_contracts_per_target_topic():
    problems=load_problems()
    for topic in ('Segment Tree','DP','Grafos'):
        items=[p for p in problems if p['topic']==topic]
        assert len({p['math_essence'] for p in items})>=5
        llm=LLMClient('Gemini','test','test',require_model=True);engine=AutoCodeEngine(llm);history=[]
        for selected in items[:5]:
            with patch.object(llm,'complete',return_value={'seed_id':selected['id'],'focus':topic}),patch.object(engine,'adapt_seed',return_value={'seed_id':selected['id']}) as adapt:
                result=engine.generate_problem(concept=topic,learning_request=topic,recent_problems=history)
            history.append(result)
        assert len({p['seed_id'] for p in history})==5


def test_new_grammars_reject_invalid_inputs_and_match_hand_calculated_answers():
    problems={p['extended_task']:p for p in load_problems() if p.get('extended_task')}
    for task,p in problems.items():
        for example in p['examples']:
            assert validate(p,example['input'])
            assert oracle(task,example['input'],small=True)==example['expected_output']
        for invalid in ('0 1\n','1 30001\n','1 1\n','x y\n'):
            with pytest.raises(ValueError):validate(p,invalid)
    assert oracle('bipartite','3 3\n1 2\n1 3\n2 3\n',True)=='NO\n'
    assert oracle('cycle','4 3\n1 2\n1 3\n2 3\n',True)=='YES\n'
    with pytest.raises(ValueError):validate(problems['range_add_sum'],'1 1\n0\n1 1 1 -1\n')
    with pytest.raises(ValueError):validate(problems['components'],'2 2\n1 2\n1 2\n')


def test_numeric_evidence_never_includes_previous_material_or_other_user(tmp_path):
    store=ProgressStore(tmp_path/'progress.db');owner='a'*32;other='b'*32
    store.add_artifact(owner,'material','Old DP',{'content':'SECRET_OLD_TEXT'})
    store.add_artifact(other,'material','Private',{'content':'OTHER_USER_SECRET'})
    evidence=store.learning_evidence(owner)
    assert 'SECRET' not in str(evidence) and 'related_previous_materials' not in evidence
    llm=LLMClient('Gemini','test','test',require_model=True)
    with patch.object(llm,'complete',return_value='Uma explicação.') as complete:
        CodigenTutor(llm).generate_material('Explicação','DP','Iniciante','',learning_request='SegTree',learner_evidence=evidence)
    assert 'ESTATÍSTICAS DO ALUNO' in complete.call_args.args[1]
    assert 'SegTree' in complete.call_args.args[1]
    assert complete.call_args.kwargs['include_history'] is False
