import json
import sqlite3
import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from core.learning_engine import (load_curriculum, questions_for, grade_answers, learning_stats,
                                  estimate_level, build_roadmap, next_step)
from core.learning_views import lesson_markdown, slides_html, diagram
from core.progress_store import ProgressStore
from core.llm_client import LLMClient
from core.codigen_tutor import CodigenTutor


def answers(kind='diagnostic',topic=None):
    return {q['id']:q['answer'] for q in questions_for(kind,topic)}


def test_curriculum_is_complete_and_links_are_sourced():
    topics=load_curriculum()
    assert len(topics)==9
    assert len(questions_for('diagnostic'))==18
    assert len(questions_for('review'))==18
    for t in topics:
        assert len(t['slides'])>=20
        assert len(t['sections'])==4
        assert all(len(s['body'])>250 for s in t['sections'])
        assert len(lesson_markdown(t))>2000
        assert len(t['videos'])==2
        assert all(v['source_url'].startswith('https://aocpc-community.github.io/') for v in t['videos'])
        assert all(len(v['url'].split('v=')[1])==11 for v in t['videos'])
        deck=slides_html(t)
        assert deck.count('<section class="slide"')==len(t['slides'])
        assert 'ArrowRight' in deck and 'window.print()' in deck
        assert 'role="img"' in diagram(t['id'])


def test_grading_no_defaults_and_level_foundation_gate():
    with pytest.raises(ValueError):grade_answers({})
    all_right=answers()
    attempt=grade_answers(all_right)
    assert attempt['correct']==18 and estimate_level([attempt])['level']=='Avançado'
    for q in questions_for('diagnostic','fundamentals'):
        all_right[q['id']]=(q['answer']+1)%len(q['options'])
    assert estimate_level([grade_answers(all_right)])['level']=='Iniciante'
    all_right[next(iter(all_right))]=True
    with pytest.raises(ValueError):grade_answers(all_right)


def test_retries_count_unique_questions_and_latest_problem_outcomes():
    correct=answers('review','prefix')
    first=grade_answers(correct,'review','prefix')
    wrong={qid:(a+1)%4 for qid,a in correct.items()}
    second=grade_answers(wrong,'review','prefix')
    history=[{'problem_id':'prefix','topic':'Prefix Sum','verdict':'AC'},
             {'problem_id':'prefix','topic':'Prefix Sum','verdict':'WA'}]
    row=next(s for s in learning_stats([first,second],history) if s['id']=='prefix')
    assert row['answered']==2 and row['correct']==0
    assert row['distinct_problems']==1 and row['accepted_problems']==0
    unknown=next(s for s in learning_stats([],[]) if s['id']=='graph')
    assert unknown['accuracy'] is None


def test_roadmap_handles_prerequisites_and_explains_weakness():
    assert next_step([],[],[])['topic']['id']=='fundamentals'
    initial=answers()
    for topic in ('graph','tree'):
        for q in questions_for('diagnostic',topic):initial[q['id']]=(q['answer']+1)%4
    attempt=grade_answers(initial)
    assert next_step([attempt],[],[])['topic']['id']=='graph'
    plan=build_roadmap([attempt],[],[])
    tree=next(p for p in plan if p['topic']['id']=='tree')
    assert tree['blocked_by']==['graph']
    assert next(p for p in plan if p['topic']['id']=='graph')['status']=='Reforçar agora'


def test_sqlite_persists_profiles_and_excludes_credentials(tmp_path):
    path=tmp_path/'progress.sqlite3';a=uuid.uuid4().hex;b=uuid.uuid4().hex
    store=ProgressStore(path)
    store.save(a,{'history':[{'topic':'DP','verdict':'WA','problem':'x'}],'api_key':'NEVER_SAVE','material':'Uma explicação','quiz_attempts':[]})
    store.add_artifact(a,'material','DP',{'concept':'DP','content':'Estado e transição'})
    assert ProgressStore(path).load(a)['material']=='Uma explicação'
    assert store.load(b)=={} and not store.artifacts(b)
    assert 'api_key' not in store.load(a)
    assert store.counts(a)['artifacts']==1
    with sqlite3.connect(path) as db:
        assert 'NEVER_SAVE' not in db.execute('SELECT payload FROM profiles').fetchone()[0]
    with pytest.raises(ValueError):store.load('../outside')


def test_context_is_bounded_valid_json_and_uses_real_history(tmp_path):
    store=ProgressStore(tmp_path/'db.sqlite3');pid=uuid.uuid4().hex
    attempt=grade_answers(answers())
    store.save(pid,{'quiz_attempts':[attempt],'history':[{'problem':'Energia','topic':'Prefix Sum','verdict':'WA'}],
                    'level':'Intermediário','api_key':'NEVER_SAVE','completed_lessons':['fundamentals']})
    store.add_artifact(pid,'material','Prefix Sum',{'concept':'Prefix Sum','content':'Prefixo vazio e subtração de intervalos.'})
    context=store.context(pid,'Explicar Prefix Sum', max_chars=7000)
    assert 'Prefixo vazio' in context and 'WA' in context and 'NEVER_SAVE' not in context
    json.loads(context)
    short=store.context(pid,'Prefix Sum',max_chars=1000)
    assert len(short)<=1000
    json.loads(short)


def test_model_receives_history_and_audit_is_redacted(tmp_path):
    store=ProgressStore(tmp_path/'db.sqlite3');pid=uuid.uuid4().hex
    store.save(pid,{'history':[{'problem':'Rotas','topic':'Grafos','verdict':'WA'}]})
    llm=LLMClient('Gemini','private-key','model',context_provider=lambda p:store.context(pid,p),
                  audit_callback=lambda r:store.log_model_call(pid,r))
    client=MagicMock();client.__enter__.return_value=client
    client.models.generate_content.return_value=SimpleNamespace(text='Uma pista personalizada.')
    with patch.object(llm,'_gemini_client',return_value=client):
        assert llm.complete('Tutor','Explique grafos')
    request=client.models.generate_content.call_args.kwargs['contents']
    assert 'HISTÓRICO DO PERFIL' in request and 'Rotas' in request
    assert store.counts(pid)['model_calls']==1
    with sqlite3.connect(store.path) as db:
        record=json.loads(db.execute('SELECT payload FROM model_calls').fetchone()[0])
    assert record['context_chars']>0 and 'private-key' not in json.dumps(record)
    client.models.generate_content.reset_mock()
    with patch.object(llm,'_gemini_client',return_value=client):assert llm.test_connection()
    assert 'HISTÓRICO DO PERFIL' not in client.models.generate_content.call_args.kwargs['contents']


def test_local_explanations_are_substantial():
    result=CodigenTutor().generate_material('Explicação','DP','Iniciante','Jogos')
    assert len(result)>2500
    assert 'estado' in result and 'Exemplo passo a passo' in result and 'Para continuar estudando' in result
    assert 'seu conteúdo completo não foi usado' in result


def test_export_includes_all_archived_materials_and_model_calls(tmp_path):
    store=ProgressStore(tmp_path/'db.sqlite3');pid=uuid.uuid4().hex
    store.save(pid,{'history':[]})
    store.add_artifact(pid,'material','Primeiro',{'content':'Texto A'})
    store.add_artifact(pid,'material','Segundo',{'content':'Texto B'})
    store.log_model_call(pid,{'provider':'Gemini','model':'preview','prompt':'Pergunta','response':'Resposta','api_key':'NOT_SAVED'})
    exported=store.export_profile(pid)
    assert len(exported['artifacts'])==2
    assert exported['model_calls'][0]['payload']['response']=='Resposta'
    assert 'NOT_SAVED' not in json.dumps(exported)
    assert store.latest_profile_id()==pid
