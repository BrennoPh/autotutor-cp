from copy import deepcopy
import json
from unittest.mock import patch
import pytest
from core.topic_plans import preferences,generate_plan,TopicPlans
from core.llm_client import LLMClient,AIUnavailable
from core.progress_store import ProgressStore
from core.library import Library,study_entry

RESOURCES=[dict(id='A0',kind='aula',title='Estados e transições',lesson_id='dp',source='AutoTutor',url=''),
           dict(id='V0',kind='video',title='DP introdutória',url='https://www.youtube.com/watch?v=test',source='Test source'),
           dict(id='P0',kind='problema',title='Escolhas',problem_id='dp',judge='local',url='',source='AutoTutor')]


def prefs():return preferences('DP','Sei usar vetores e laços.','dp','Aprendo resolvendo problemas',45,[0,2,4],'2026-11-04',4)


def reply():return dict(title='Primeiros passos em DP',summary='Aprender estados antes de mochila.',personalization='Praticar em exemplos pequenos após a introdução.',assumptions='Tempo estimado, ajuste após a primeira sessão.',sessions=[
    dict(title='Estado e transição',activities=[dict(kind='aula',resource_id='A0',minutes=15,objective='Definir um estado.'),dict(kind='video',resource_id='V0',minutes=10,objective='Conferir o exemplo.'),dict(kind='problema',resource_id='P0',minutes=20,objective='Tentar uma transição.')]),
    dict(title='Praticar e revisar',activities=[dict(kind='revisao',resource_id=None,minutes=15,objective='Explicar a recorrência.'),dict(kind='problema',resource_id='P0',minutes=20,objective='Revisar casos mínimos.')])])


def generate(answer=None,p=None):
    client=LLMClient('Gemini','key','model',require_model=True)
    with patch('core.topic_plans.candidate_resources',return_value=RESOURCES),patch.object(client,'complete',return_value=answer or reply()) as complete:
        plan=generate_plan(client,p or prefs(),[],[],[])
    return plan,complete


def test_model_selects_duration_and_calendar_uses_only_user_available_days():
    plan,complete=generate()
    assert plan['estimated_minutes']==80
    assert [s['date'] for s in plan['sessions']]==['2026-11-04','2026-11-06']
    request=json.loads(complete.call_args.args[1])
    assert request['preferences']['style']=='Aprendo resolvendo problemas'
    assert request['resources']==RESOURCES
    assert complete.call_args.kwargs['include_history'] is False


@pytest.mark.parametrize('mutation',['unknown_resource','wrong_kind','over_budget','float_time','no_video','no_sessions','invented_url'])
def test_invalid_ai_plans_are_rejected_without_rule_based_replacement(mutation):
    value=reply()
    if mutation=='unknown_resource':value['sessions'][0]['activities'][0]['resource_id']='invented'
    if mutation=='wrong_kind':value['sessions'][0]['activities'][0]['kind']='problema'
    if mutation=='over_budget':value['sessions'][0]['activities'][0]['minutes']=45
    if mutation=='float_time':value['sessions'][0]['activities'][0]['minutes']=15.5
    if mutation=='no_video':value['sessions'][0]['activities'].pop(1)
    if mutation=='no_sessions':value['sessions']=[]
    if mutation=='invented_url':value['summary']='Leia https://invented.example'
    with pytest.raises(AIUnavailable):generate(value)


def test_plan_progress_is_private_persistent_exported_and_adaptation_keeps_history(tmp_path):
    store=ProgressStore(tmp_path/'progress.sqlite3');service=TopicPlans(store);profile='a'*32;other='b'*32
    plan,_=generate();identifier=service.save(profile,plan)
    service.set_completed(profile,identifier,0,0,True)
    assert TopicPlans(store).progress(profile,identifier)=={(0,0):True}
    with pytest.raises(PermissionError):service.set_completed(other,identifier,0,0,True)
    with pytest.raises(ValueError):service.set_completed(profile,identifier,-1,0,True)
    revised=service.save(profile,plan,parent_id=identifier)
    assert service.get(profile,revised)['parent_id']==identifier
    assert service.progress(profile,identifier)=={(0,0):True}
    assert service.progress(profile,revised)=={}
    entry=study_entry(Library(store).page(profile,kind='topic_plan')['items'][0])
    assert entry['kind']=='Trilha por assunto' and '2026-11-04' in entry['content']
    export=store.export_profile(profile)
    assert export['topic_plan_progress'][0]['completed'] is True
    assert not service.list(other)


def test_invalid_calendar_is_rejected_before_model_calls():
    with pytest.raises(ValueError):preferences('DP','','dp','Equilibrado',45,[],'2026-11-04',4)
    with pytest.raises(ValueError):preferences('DP','','dp','Equilibrado',45,[7],'2026-11-04',4)
