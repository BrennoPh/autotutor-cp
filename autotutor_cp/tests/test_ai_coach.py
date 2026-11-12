"""AI decisions must be evidence-backed, validated and never replaced by heuristics."""
from copy import deepcopy
from unittest.mock import patch
import pytest
from core.ai_coach import (learner_evidence,analyze_learner,save_analysis,cached_analysis,
                           propose_teams,compact_roster)
from core.learning_engine import load_curriculum,grade_answers,questions_for
from core.llm_client import LLMClient,AIUnavailable
from core.ollama_client import OllamaError
from core.progress_store import ProgressStore
from core.library import Library,study_entry


def model():return LLMClient('Ollama',require_model=True)


def analysis(level='Não avaliado'):
    return dict(level=level,confidence='baixa',summary='Pouca evidência: avalie a base antes de concluir domínio.',strengths=[],gaps=['Faça o diagnóstico.'],
                roadmap=[dict(topic_id=t['id'],reason='Avaliar este conceito e seus pré-requisitos.',action='Estudar e praticar.') for t in load_curriculum()])


def students(n=4):
    return [dict(id='private-id-'+str(i),name='Aluno '+str(i),username='PRIVATE_USERNAME',local_solved=[],external_solved=[],verified_external=[],
                 quiz_correct=0,quiz_answered=0,submissions=0,topic_statistics=[],skills={'arbitrary_weight':99}) for i in range(n)]


def test_valid_analysis_uses_model_decision_instead_of_percentage_thresholds():
    qs=questions_for('diagnostic');attempt=grade_answers({q['id']:q['answer'] for q in qs})
    evidence=learner_evidence([attempt],[],[],3);client=model()
    answer=analysis('Intermediário')
    with patch.object(client,'complete',return_value=answer) as complete:
        result=analyze_learner(client,evidence)
    assert result['level']=='Intermediário' # 100% does not force Advanced anymore.
    assert '"correct":2' in complete.call_args.args[1]
    assert complete.call_args.kwargs['include_history'] is False


@pytest.mark.parametrize('mutation',['unknown_topic','duplicate_topic','missing_topic','bad_level','missing_reason','prerequisite_order','unsupported_level'])
def test_invalid_analysis_never_uses_rule_based_plan(mutation):
    answer=analysis()
    if mutation=='unknown_topic':answer['roadmap'][0]['topic_id']='invented'
    if mutation=='duplicate_topic':answer['roadmap'][1]=deepcopy(answer['roadmap'][0])
    if mutation=='missing_topic':answer['roadmap'].pop()
    if mutation=='bad_level':answer['level']='Gênio'
    if mutation=='missing_reason':answer['roadmap'][0].pop('reason')
    if mutation=='prerequisite_order':answer['roadmap'].reverse()
    if mutation=='unsupported_level':answer['level']='Avançado'
    client=model()
    with patch.object(client,'complete',return_value=answer),pytest.raises(AIUnavailable):
        analyze_learner(client,learner_evidence([],[],[]))


def test_saved_analysis_is_in_library_and_cache_is_scoped_to_evidence_and_model(tmp_path):
    store=ProgressStore(tmp_path/'test.sqlite3');client=model();evidence=learner_evidence([],[],[])
    saved=save_analysis(store,'a'*32,client,evidence,analysis())
    assert cached_analysis(store,'a'*32,evidence,client)==saved
    assert cached_analysis(store,'b'*32,evidence,client) is None
    assert cached_analysis(store,'a'*32,learner_evidence([],[],[],4),client) is None
    client.model='different'
    assert cached_analysis(store,'a'*32,evidence,client) is None
    item=Library(store).page('a'*32)['items'][0]
    assert study_entry(item)['kind']=='Análise de aprendizado'
    assert 'Trilha sugerida' in study_entry(item)['content']


def test_strict_client_failure_and_rejected_output_never_fallback():
    client=model()
    with patch('core.ollama_client.OllamaClient.request',side_effect=OllamaError('Motor desligado')):
        with pytest.raises(AIUnavailable,match='Motor desligado'):client.complete('Tutor','Pedido')
        assert client.test_connection() is False
    with pytest.raises(AIUnavailable):client.report_fallback('Conteúdo inválido')


def test_valid_team_partition_uses_anonymous_ids_and_preserves_every_participant():
    client=model();roster=students();response=dict(teams=[dict(members=['A1','A2','A0'],reason='Complementam seus tópicos; evidência limitada.')],waiting=['A3'],summary='Proposta provisória.')
    with patch.object(client,'complete',return_value=response) as complete:
        result=propose_teams(client,roster,'Complementaridade','Turma inteira')
    assert result['teams']==[['private-id-1','private-id-2','private-id-0']]
    assert result['waiting']==['private-id-3']
    prompt=complete.call_args.args[1]
    assert 'PRIVATE_USERNAME' not in prompt and 'private-id-' not in prompt and 'arbitrary_weight' not in prompt
    assert '"quiz_answered":0' in prompt


@pytest.mark.parametrize('members,waiting', [(['A0','A0','A1'],['A3']),(['A0','A1','unknown'],['A3']),(['A0','A1','A2'],[]),(['A0','A1'],['A2','A3'])])
def test_invalid_team_partition_is_rejected(members,waiting):
    client=model()
    response=dict(teams=[dict(members=members,reason='Motivo')],waiting=waiting,summary='Proposta')
    with patch.object(client,'complete',return_value=response),pytest.raises(AIUnavailable):
        propose_teams(client,students(),'Complementaridade','Turma inteira')


def test_class_evidence_keeps_measured_percentages_and_sources_separate():
    from core.ai_coach import class_evidence
    roster=students(2)
    roster[0].update(local_solved=['p1','p2'],external_solved=['e1','e2'],verified_external=['e1'])
    roster[0]['topic_statistics']=[dict(id='prefix',correct=2,answered=4,accepted_problems=1,distinct_problems=2,submissions=3)]
    roster[1]['topic_statistics']=[dict(id='prefix',correct=1,answered=2,accepted_problems=0,distinct_problems=1,submissions=1)]
    evidence=class_evidence(roster)
    assert evidence['local_accepted_total']==2
    assert evidence['external_declared_total']==2 and evidence['external_confirmed_total']==1
    assert evidence['topics']==[dict(topic='prefix',correct=3,answered=6,accepted=1,attempted_problems=3,accuracy_percent=50.0)]
