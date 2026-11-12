from pathlib import Path
import sys
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


import pytest


@pytest.fixture(autouse=True)
def synthetic_model_transport(monkeypatch):
    """Exercise real AI routing/auditing without network or model-quality claims."""
    import json,ast
    from core.learning_engine import load_curriculum
    def chat(self,model,system,prompt,json_mode=False):
        prompt=prompt.split('\n\nHISTÓRICO DO PERFIL')[0]
        if json_mode and 'Campos math_essence' in prompt:
            value=dict(math_essence='somas de prefixos',core_concepts=['prefixos'],approach_summary='Subtrair prefixos nas fronteiras')
        elif json_mode and 'ranking' in prompt:
            candidates=ast.literal_eval(prompt.splitlines()[-1])
            value={'ranking':[dict(id=c['id'],reason='Comparar estrutura e restrições.') for c in candidates]}
        elif json_mode and 'Escolha um contrato compatível' in prompt:
            data=json.loads(prompt.splitlines()[-1]);request=data['learning_request'].lower()
            chosen=next((c for c in data['candidates'] if c['id']=='segment_tree'),None) if 'seg' in request else next((c for c in data['candidates'] if c['topic']==data['reference_subject']),None)
            value=dict(seed_id=chosen['id'] if chosen else None,focus=chosen['topic'] if chosen else request,reason='Contrato compatível no transporte de teste.')
        elif json_mode and 'Adapte o problema' in prompt:
            value=json.loads(prompt.splitlines()[-1])
        elif json_mode and 'maximum_sessions' in prompt:
            data=json.loads(prompt);choices=data['resources'];selected=[]
            for types in (('aula','artigo'),('video',),('problema',)):
                resource=next((r for r in choices if r['kind'] in types),None)
                if resource:selected.append(dict(kind=resource['kind'],resource_id=resource['id'],minutes=10,objective='Estudar e aplicar o conceito.'))
            value=dict(title='Trilha DP de teste',summary='Uma primeira etapa de aprendizado.',personalization='Ajustada à preferência informada.',assumptions='Estimativas de planejamento.',sessions=[dict(title='Estado e transição',activities=selected)])
        elif json_mode and 'roadmap' in prompt:
            evidence=json.loads(prompt.split('EVIDÊNCIAS: ')[1])
            measured=any(t['answered'] or t['distinct_problems'] for t in evidence['topics'])
            value=dict(level='Avançado' if measured else 'Não avaliado',confidence='baixa',summary='Análise sintética de teste com evidências limitadas.',strengths=[],gaps=['Praticar para avaliar.'],
                roadmap=[dict(topic_id=t['id'],reason='Revisar conceitos e pré-requisitos.',action='Estudar e testar.') for t in load_curriculum()])
        elif json_mode and 'waiting' in prompt:
            roster=json.loads(prompt.split('DADOS: ')[1]);ids=[x['id'] for x in roster];n=len(ids)//3
            value=dict(teams=[dict(members=ids[i*3:i*3+3],reason='Evidência limitada, proposta de teste.') for i in range(n)],waiting=ids[n*3:],summary='Proposta de teste.')
        elif json_mode and 'steps' in system:
            value={'steps':['Identificar entrada','Analisar estado','Conferir resultado']}
        elif 'atividade de lacunas' in system:
            value='Complete o fragmento: prefixo[R] - prefixo[___]. Justifique e teste um intervalo unitário.'
        elif 'PEDIDO E PREFERÊNCIAS:' in prompt:
            prefs=json.loads(prompt.split('PEDIDO E PREFERÊNCIAS:\n')[1].split('\n\n')[0])
            value=prefs['objetivo_especifico_do_aluno']+'\n\n'+('Explicação sintética para testar o salvamento, com referências separadas. '*85 if prefs['tamanho']=='Longo' else 'Explicação sintética curta sobre o pedido do aluno.')
        else:value='Observe o caso mínimo e compare o resultado esperado com o obtido. Qual estado muda na sua tentativa?'
        return {'message':{'content':json.dumps(value,ensure_ascii=False) if json_mode else value},'done_reason':'stop'}
    monkeypatch.setattr('core.ollama_client.OllamaClient.chat',chat)


def start(username='test_student'):
    import os
    from core.accounts import Accounts
    from core.progress_store import ProgressStore
    accounts=Accounts(ProgressStore(os.environ['AUTOTUTOR_PROGRESS_DB']))
    try:accounts.register(username,'Aluno teste','test-password')
    except ValueError:pass
    app=AppTest.from_file(str(ROOT / 'app.py'), default_timeout=120)
    app.session_state['auth_token']=accounts.login(username,'test-password')
    app.session_state['provider']='Ollama'
    return app.run()


def navigate(app, page):
    app.session_state['pending_page']=page
    app.run()
    assert not app.exception


def test_ui_submission_helpers_and_material():
    app = start()
    navigate(app, 'Arena')
    app.selectbox(key='problem_picker').select('dp').run()
    app.text_area(key='code_dp').set_value('int main(){return 1;}')
    app.button(key='submit').click().run()
    assert not app.exception
    assert app.session_state['results']['dp']['verdict'] == 'RE'
    assert len(app.session_state['history']) == 1
    next(b for b in app.button if 'Lacunas' in b.label).click().run()
    assert '___' in app.session_state['helpers']['dp'][1]
    navigate(app, 'Laboratório IA')
    next(b for b in app.button if 'Gerar material' in b.label).click().run()
    assert app.session_state['material']
    assert not app.exception


def test_ui_generation_and_recommendation_navigation():
    app = start()
    navigate(app, 'Laboratório IA')
    next(b for b in app.button if 'Criar problema' in b.label).click().run()
    assert not app.exception
    selected = app.session_state['problem_id']
    assert selected.startswith('generated_')
    p = next(p for p in app.session_state['problems'] if p['id'] == selected)
    assert p['double_validated']
    assert app.session_state['active_page'] == 'Arena'
    app.text_area(key='code_' + selected).set_value(p['std_cpp'])
    app.button(key='submit').click().run()
    assert not app.exception
    assert app.session_state['results'][selected]['verdict'] == 'AC'
    next(b for b in app.button if 'Buscar problemas similares' in b.label or 'Buscar semelhantes' in b.label or 'Recomendar' in b.label).click().run()
    next(b for b in app.button if 'Praticar este problema' in b.label).click().run()
    assert not app.exception
    assert app.session_state['problem_id'] != selected


def test_catalog_filters_and_draft_survives_navigation():
    app = start()
    navigate(app, 'Problemas')
    app.text_input(key='catalog_search').set_value('Energia').run()
    assert len([b for b in app.button if b.key.startswith('solve_')]) == 1
    app.button(key='solve_prefix').click().run()
    assert app.session_state['active_page'] == 'Arena'
    app.text_area(key='code_prefix').set_value('int main(){return 7;}').run()
    navigate(app, 'Submissões')
    navigate(app, 'Arena')
    assert app.text_area(key='code_prefix').value == 'int main(){return 7;}'
    assert not app.exception


def test_provider_selection_does_not_claim_failure_or_send_requests():
    app = start()
    navigate(app, 'Configurações')
    app.selectbox(key='provider').select('Gemini').run()
    app.text_input(key='api_key').set_value('example-key-not-real').run()
    assert not app.exception
    assert not app.session_state['ai_events']
    assert not app.session_state['connection_checks']
    assert any('configurada' in item.value for item in app.info)
    navigate(app, 'Problemas')
    assert app.text_input(key='api_key').value == 'example-key-not-real'
    assert not app.warning


def test_connection_check_renders_real_provider_status_without_exposing_key():
    from unittest.mock import MagicMock, patch
    from types import SimpleNamespace
    from google.genai.errors import ClientError
    app = start()
    navigate(app, 'Configurações')
    app.selectbox(key='provider').select('Gemini').run()
    secret = 'AIza-PRIVATE-EXAMPLE-NOT-A-REAL-KEY'
    app.text_input(key='api_key').set_value(secret).run()
    client = MagicMock()
    client.__enter__.return_value = client
    client.models.generate_content.side_effect = ClientError(429, {'error':{'code':429, 'message':'quota exceeded ' + secret}})
    with patch('core.llm_client.LLMClient._gemini_client', return_value=client):
        next(b for b in app.button if b.label == 'Testar conexão').click().run()
    assert not app.exception
    assert any('cota' in item.value for item in app.warning)
    assert secret not in str(app.session_state['ai_events'])
    client.models.generate_content.side_effect = None
    client.models.generate_content.return_value = SimpleNamespace(text='Conexão confirmada.')
    with patch('core.llm_client.LLMClient._gemini_client', return_value=client):
        next(b for b in app.button if b.label == 'Testar conexão').click().run()
    assert not app.exception
    assert any('sucesso' in item.value for item in app.success)


def test_learning_diagnostic_roadmap_library_and_charts():
    from core.learning_engine import questions_for
    app=start()
    navigate(app,'Meu desempenho')
    assert not app.exception
    assert not app.get('vega_lite_chart')
    navigate(app,'Diagnóstico')
    assert app.button(key='finish_diagnostic').disabled
    questions=questions_for('diagnostic')
    for stage in range(3):
        app.selectbox(key='diagnostic_stage').set_value(stage).run()
        for q in questions[stage*6:(stage+1)*6]:
            app.radio(key='diagnostic_'+q['id']).set_value(q['answer']).run()
    app.button(key='finish_diagnostic').click().run()
    assert not app.exception
    assert app.session_state['quiz_attempts'][-1]['correct']==18
    app.button(key='diagnostic_ai').click().run()
    app.button(key='use_estimated_level').click().run()
    assert app.selectbox(key='level').value=='Avançado'
    navigate(app,'Minha trilha')
    app.button(key='roadmap_prefix').click().run()
    assert app.session_state['active_page']=='Biblioteca'
    assert app.selectbox(key='lesson_picker').value=='prefix'
    app.button(key='complete_prefix').click().run()
    assert 'prefix' in app.session_state['completed_lessons']
    for q in questions_for('review','prefix'):
        app.radio(key='review_'+q['id']).set_value(q['answer'])
    next(b for b in app.button if b.label=='Corrigir fixação').click().run()
    assert not app.exception
    assert app.session_state['quiz_attempts'][-1]['correct']==2
    navigate(app,'Meu desempenho')
    assert not app.exception
    assert len(app.get('vega_lite_chart'))>=2


def test_generated_materials_and_quiz_progress_survive_new_session():
    from core.learning_engine import grade_answers,questions_for
    app=start()
    pid=app.session_state['progress_profile_id']
    navigate(app,'Laboratório IA')
    next(b for b in app.button if 'Gerar material' in b.label).click().run()
    material=app.session_state['material']
    assert len(material)>2500
    second=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120)
    second=start()
    second.query_params['perfil']='another-profile'
    second.run()
    assert second.session_state['progress_profile_id']==pid
    assert 'perfil' not in second.query_params
    assert not second.exception
    assert second.session_state['material']==material
    navigate(second,'Laboratório IA')
    assert any(b.key=='lab_saved' for b in second.button)
    navigate(second,'Meus estudos')
    next(b for b in second.button if b.label=='Abrir estudo →').click().run()
    assert second.session_state['active_page']=='Meus estudos'
    assert any('Explicação sintética' in m.value for m in second.markdown)
    navigate(second,'Configurações')
    assert any('conteúdos' in e.value for e in second.markdown)
    second.button(key='logout').click().run()
    assert any(b.label=='Entrar' for b in second.button)
    second=start('other_student')
    assert not second.exception
    assert second.session_state['progress_profile_id']!=pid
    assert not second.session_state['material']
    assert not second.session_state['quiz_attempts']


def test_registration_gate_and_teacher_classroom_interface():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120).run()
    assert not app.exception
    app.text_input(key='register_name').set_value('Professora teste')
    app.text_input(key='register_username').set_value('professora')
    app.selectbox(key='register_role').set_value('Professor')
    app.text_input(key='register_password').set_value('test-password')
    app.text_input(key='register_confirm').set_value('test-password')
    next(b for b in app.button if b.label=='Criar minha conta').click().run()
    assert not app.exception
    navigate(app,'Turmas')
    next(t for t in app.text_input if t.label=='Nome da turma').set_value('Turma teste')
    next(b for b in app.button if b.label=='Criar turma').click().run()
    assert not app.exception
    import os
    from core.accounts import Accounts
    from core.classrooms import Classrooms
    from core.progress_store import ProgressStore
    store=ProgressStore(os.environ['AUTOTUTOR_PROGRESS_DB']);accounts=Accounts(store);school=Classrooms(store,accounts)
    teacher=accounts.current(app.session_state['auth_token'])
    classroom=school.list_for(teacher['id'])[0]
    for i in range(4):
        uid=accounts.register('member'+str(i),'Aluno '+str(i),'test-password')
        school.join(uid,classroom['invite_code'])
    app.run()
    app.button(key='build_teams').click().run()
    assert not app.exception
    proposal=app.session_state['team_proposal']['payload']
    assert len(proposal['teams'])==1 and len(proposal['waiting'])==1
    app.button(key='save_teams').click().run()
    assert not app.exception
    assert len(school.formations(teacher['id'],classroom['id']))==1


def test_external_problem_uses_official_judge_and_own_status():
    from core.catalog import external_problems
    app=start();p=next(p for p in __import__('core.catalog',fromlist=['catalog']).catalog() if p.get('external'))
    app.session_state['pending_problem']=p['id']
    navigate(app,'Arena')
    assert not app.exception
    assert not any(b.key=='submit' for b in app.button)
    app.button(key='external_solved_'+p['id']).click().run()
    assert not app.exception
    assert any('autodeclarada' in s.value for s in app.success)
    navigate(app,'Problemas')
    app.selectbox(key='catalog_source').select('CSES').run()
    assert not app.exception
    assert len([b for b in app.button if b.key.startswith('solve_')])==20
    assert app.selectbox(key='catalog_page').options[-1]=='20'


def test_library_automatically_shows_material_guides_resources_and_notes():
    app=start();navigate(app,'Laboratório IA')
    next(b for b in app.button if 'Gerar material' in b.label).click().run()
    navigate(app,'Biblioteca')
    app.radio(key='library_section').set_value('Minha coleção').run()
    assert not app.exception
    next(b for b in app.button if b.label=='Abrir página de estudo →').click().run()
    note=next(t for t in app.text_area if t.label=='O que entendi e o que preciso revisar')
    note.set_value('Rever o estado vazio')
    next(b for b in app.button if b.label=='Salvar anotações').click().run()
    assert not app.exception
    navigate(app,'Biblioteca')
    app.radio(key='library_section').set_value('Guias de aprofundamento').run()
    assert not app.exception
    assert app.selectbox(key='deep_guide_picker').options
    app.radio(key='library_section').set_value('Referências').run()
    assert not app.exception
    app.selectbox(key='reference_kind').set_value('Vídeo').run()
    next(b for b in app.button if b.label=='Salvar na minha coleção').click().run()
    app.radio(key='library_section').set_value('Minha coleção').run()
    assert not app.exception
    app.selectbox(key='collection_kind').set_value('resource').run()
    assert any('Vídeo' in e.value for e in app.caption) or any('Referência salva' in e.label for e in app.expander)
    app.button(key='logout').click().run()
    second=start();navigate(second,'Biblioteca')
    second.radio(key='library_section').set_value('Minha coleção').run()
    assert not second.exception
    next(b for b in second.button if b.label=='Abrir página de estudo →').click().run()
    assert any(t.value=='Rever o estado vazio' for t in second.text_area)


def test_promoted_cses_task_is_judged_locally_and_added_to_old_profile():
    from core.problem_bank import load_problems
    from core.progress_store import ProgressStore
    import os
    app=start();pid=app.session_state['progress_profile_id']
    store=ProgressStore(os.environ['AUTOTUTOR_PROGRESS_DB']);state=store.load(pid)
    state['problems']=load_problems()[:6];store.save(pid,state)
    app=start()
    assert len(app.session_state['problems'])==len(load_problems())
    task=next(p for p in load_problems() if p.get('local_task')=='missing')
    app.session_state['pending_problem']=task['id'];navigate(app,'Arena')
    assert not app.exception
    app.text_area(key='code_'+task['id']).set_value(task['std_cpp'])
    app.button(key='submit').click().run()
    assert not app.exception
    assert app.session_state['results'][task['id']]['verdict']=='AC'
    assert app.session_state['history'][-1]['problem_id']==task['id']
    app.toggle(key='flow_'+task['id']).set_value(True).run()
    assert not app.exception


def test_lab_specific_goal_preferences_are_saved_with_material_and_restored():
    from core.progress_store import ProgressStore
    import os
    app=start();navigate(app,'Laboratório IA')
    app.text_area(key='learning_request').set_value('Quero entender a ordem dos laços da DP.').run()
    app.selectbox(key='material_length').set_value('Curto').run()
    app.selectbox(key='material_depth').set_value('Passo a passo').run()
    app.checkbox(key='material_examples').set_value(False).run()
    app.checkbox(key='material_exercises').set_value(False).run()
    next(b for b in app.button if 'Gerar material' in b.label).click().run()
    assert not app.exception
    material=app.session_state['material']
    assert 'Quero entender a ordem dos laços da DP.' in material
    assert 'Exemplo passo a passo' not in material
    store=ProgressStore(os.environ['AUTOTUTOR_PROGRESS_DB'])
    artifact=store.artifacts(app.session_state['progress_profile_id'],'material')[0]
    assert artifact['payload']['learning_request']=='Quero entender a ordem dos laços da DP.'
    assert artifact['payload']['preferences']==dict(length='Curto',depth='Passo a passo',include_examples=False,include_exercises=False,target_chars=None)
    navigate(app,'Biblioteca');navigate(app,'Laboratório IA')
    assert app.text_area(key='learning_request').value=='Quero entender a ordem dos laços da DP.'
    second=start();navigate(second,'Laboratório IA')
    assert not second.exception
    assert second.selectbox(key='material_length').value=='Curto'
    assert second.selectbox(key='material_depth').value=='Passo a passo'
    assert not second.checkbox(key='material_examples').value


def test_ollama_is_the_default_and_connection_requires_no_api_key():
    from unittest.mock import patch
    app=start()
    new=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120)
    new.session_state['auth_token']=app.session_state['auth_token']
    with patch('core.ollama_client.OllamaClient.request') as request:
        new.run()
        assert not new.exception
        assert new.selectbox(key='provider').value=='Ollama'
        assert new.text_input(key='model_Ollama').value=='llama3.2:1b'
        assert new.text_input(key='api_key').disabled
        request.assert_not_called()
        navigate(new,'Configurações')
        assert not next(b for b in new.button if b.label=='Testar conexão').disabled
        assert not next(b for b in new.button if b.label=='Buscar modelos disponíveis').disabled
        request.return_value={'message':{'content':'Conexão confirmada.'}}
        next(b for b in new.button if b.label=='Testar conexão').click().run()
        assert not new.exception
        assert new.session_state['ai_events'][-1]['provider']=='Ollama'
        assert new.session_state['ai_events'][-1]['source']=='api'


def test_model_failure_displays_error_without_creating_fallback_material(monkeypatch):
    from core.ollama_client import OllamaError
    from core.progress_store import ProgressStore
    import os
    app=start();navigate(app,'Laboratório IA')
    def unavailable(*args,**kwargs):raise OllamaError('Motor indisponível no teste')
    monkeypatch.setattr('core.ollama_client.OllamaClient.chat',unavailable)
    next(b for b in app.button if 'Gerar material' in b.label).click().run()
    assert not app.exception
    assert any('Motor indisponível' in e.value for e in app.error)
    assert not app.session_state['material']
    store=ProgressStore(os.environ['AUTOTUTOR_PROGRESS_DB'])
    assert not store.artifacts(app.session_state['progress_profile_id'],'material')


def test_cloud_provider_keys_are_separate_and_qwen_region_changes_connection_scope():
    from types import SimpleNamespace
    from unittest.mock import MagicMock,patch
    app=start();navigate(app,'Configurações')
    app.selectbox(key='provider').set_value('DeepSeek').run()
    assert app.text_input(key='model_DeepSeek').value=='deepseek-flash'
    app.text_input(key='api_key').set_value('deepseek-test-secret').run()
    app.selectbox(key='provider').set_value('Qwen').run()
    assert app.text_input(key='api_key').value==''
    assert app.text_input(key='model_Qwen').value=='qwen-plus'
    app.text_input(key='api_key').set_value('qwen-test-secret').run()
    client=MagicMock();client.__enter__.return_value=client
    client.chat.completions.create.return_value=SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='Conexão confirmada.'),finish_reason='stop')])
    with patch('openai.OpenAI',return_value=client) as sdk:
        next(b for b in app.button if b.label=='Testar conexão').click().run()
    assert not app.exception
    assert sdk.call_args.kwargs['api_key']=='qwen-test-secret'
    assert sdk.call_args.kwargs['base_url']=='https://dashscope-intl.aliyuncs.com/compatible-mode/v1'
    assert app.session_state['ai_events'][-1]['provider']=='Qwen'
    assert 'qwen-test-secret' not in str(app.session_state['ai_events'])
    app.selectbox(key='qwen_region').set_value('China · Pequim').run()
    assert any('não testada' in item.value for item in app.markdown)
    app.selectbox(key='provider').set_value('DeepSeek').run()
    assert app.text_input(key='api_key').value=='deepseek-test-secret'
    app.selectbox(key='provider').set_value('Qwen').run()
    assert app.text_input(key='api_key').value=='qwen-test-secret'
    assert not app.exception


def test_knowledge_library_search_read_and_notes_without_ai_calls():
    from core.knowledge import KnowledgeBase
    import os
    kb=KnowledgeBase(os.environ['AUTOTUTOR_KNOWLEDGE_DB'])
    kb.import_documents([dict(title='BFS: busca em largura',url='https://example.org/bfs',source='Fonte de teste',license='CC BY-SA 4.0',language='pt-BR',track='Base',topics=['graph'],tags=['bfs'],content='BFS usa uma fila FIFO e percorre camadas. '*20)])
    app=start();navigate(app,'Biblioteca')
    app.radio(key='library_section').set_value('Acervo RAG').run()
    app.text_input(key='knowledge_query').set_value('BFS').run()
    next(b for b in app.button if b.label=='Ler conteúdo').click().run()
    assert not app.exception and not app.session_state['ai_events']
    assert any('fila FIFO' in m.value for m in app.markdown)
    next(t for t in app.text_area if t.label=='Minhas anotações').set_value('Rever a ordem da fila.')
    next(b for b in app.button if b.label=='Salvar meu estudo').click().run()
    assert not app.exception


def test_sourced_model_suggestion_changes_model_without_sending_a_request():
    from unittest.mock import patch
    app=start();navigate(app,'Configurações')
    app.selectbox(key='provider').set_value('Qwen').run()
    app.text_input(key='api_key').set_value('qwen-test').run()
    with patch('openai.OpenAI') as client:
        app.button(key='model_recommendation_Qwen_quality').click().run()
        client.assert_not_called()
    assert not app.exception
    assert app.text_input(key='model_Qwen').value=='qwen3.8-max'
    assert app.toggle(key='qwen_thinking').value is True
    assert app.text_input(key='api_key').value=='qwen-test'


def test_topic_plan_creation_progress_adaptation_and_library_archive():
    from core.topic_plans import TopicPlans
    from core.progress_store import ProgressStore
    import os
    app=start();navigate(app,'Minha trilha')
    app.radio(key='roadmap_mode').set_value('Por assunto').run()
    app.selectbox(key='topic_plan_style').set_value('Aprendo resolvendo problemas')
    app.text_area(key='topic_plan_goal').set_value('Quero aprender estado e transição.')
    app.button(key='create_topic_plan').click().run()
    assert not app.exception
    identifier=app.session_state['active_topic_plan']
    assert any('Trilha DP de teste' in m.value for m in app.markdown)
    check=next(c for c in app.checkbox if c.key.startswith('topic_plan_done_'))
    check.set_value(True).run()
    store=ProgressStore(os.environ['AUTOTUTOR_PROGRESS_DB']);service=TopicPlans(store);profile=app.session_state['progress_profile_id']
    assert service.progress(profile,identifier)[(0,0)] is True
    app.text_area(key='topic_plan_feedback').set_value('Prefiro mais problemas pequenos.').run()
    app.selectbox(key='adapt_topic_style_'+identifier).set_value('Prefiro vídeos e exemplos')
    app.button(key='adapt_topic_plan').click().run()
    assert not app.exception
    revised=app.session_state['active_topic_plan']
    assert revised!=identifier and service.get(profile,revised)['parent_id']==identifier
    assert service.get(profile,revised)['preferences']['style']=='Prefiro vídeos e exemplos'
    assert service.get(profile,identifier)['preferences']['style']=='Aprendo resolvendo problemas'
    assert service.progress(profile,identifier)[(0,0)] is True
    navigate(app,'Biblioteca');app.radio(key='library_section').set_value('Minha coleção').run()
    app.selectbox(key='collection_kind').set_value('topic_plan').run()
    assert not app.exception
    assert any('Trilha DP de teste' in e.label for e in app.expander)


def test_temporary_gemini_overload_preserves_configuration_and_last_verification():
    from unittest.mock import MagicMock,patch
    from types import SimpleNamespace
    from google.genai.errors import ServerError
    app=start();navigate(app,'Configurações')
    app.selectbox(key='provider').select('Gemini').run()
    secret='example-session-secret'
    app.text_input(key='api_key').set_value(secret).run()
    client=MagicMock();client.__enter__.return_value=client
    client.models.generate_content.return_value=SimpleNamespace(text='Conexão confirmada.')
    with patch('core.llm_client.LLMClient._gemini_client',return_value=client):
        next(b for b in app.button if b.label=='Testar conexão').click().run()
    fingerprint=next(iter(app.session_state['connection_checks']))
    first=app.session_state['connection_checks'][fingerprint].copy()
    assert first['ok'] and first['last_success_at']
    client.models.generate_content.side_effect=ServerError(503,{'error':{'message':'This model is currently experiencing high demand.'}})
    with patch('core.llm_client.LLMClient._gemini_client',return_value=client):
        next(b for b in app.button if b.label=='Testar conexão').click().run()
    assert not app.exception
    failed=app.session_state['connection_checks'][fingerprint]
    assert failed['status']=='temporary_error' and not failed['ok']
    assert failed['last_success_at']==first['last_success_at']
    assert any('instabilidade temporária' in m.value for m in app.markdown)
    assert any('sobrecarr' in w.value for w in app.warning)
    assert app.text_input(key='api_key').value==secret
    navigate(app,'Problemas');navigate(app,'Configurações')
    assert app.session_state['connection_checks'][fingerprint]==failed
    client.models.generate_content.side_effect=None
    with patch('core.llm_client.LLMClient._gemini_client',return_value=client):
        next(b for b in app.button if b.label=='Testar conexão').click().run()
    assert app.session_state['connection_checks'][fingerprint]['status']=='verified'
    assert secret not in str(app.session_state['ai_events'])


def test_specific_segment_tree_request_generates_its_own_contract():
    app=start();navigate(app,'Laboratório IA')
    app.selectbox(key='concept').select('DP').run()
    app.text_area(key='learning_request').set_value('Quero praticar SegTree com atualização pontual e mínimo em intervalo.').run()
    next(b for b in app.button if 'Criar problema' in b.label).click().run()
    assert not app.exception
    p=next(p for p in app.session_state['problems'] if p['id']==app.session_state['problem_id'])
    assert p['topic']=='Segment Tree' and p['family']=='segtree' and p['double_validated']
    assert p['validation']['contract_seed_id']=='segment_tree'


def test_generated_study_opens_dedicated_reader_with_notes_and_saved_collection():
    app=start();navigate(app,'Laboratório IA')
    app.selectbox(key='concept').select('Segment Tree').run()
    app.text_area(key='learning_request').set_value('Quero aprender SegTree com 5000 caracteres e detalhes de correção e complexidade.').run()
    next(b for b in app.button if 'Gerar material' in b.label).click().run()
    assert not app.exception
    assert app.session_state['active_page']=='Meus estudos'
    assert app.query_params['estudo']==app.session_state['selected_material_id']
    assert any('Segment Tree' in m.value for m in app.markdown)
    assert next(b for b in app.button if b.key=='study_done')
    app.button(key='study_done').click().run()
    assert not app.exception
    assert any('Estudado' in m.value for m in app.markdown)
    app.button(key='study_back').click().run()
    assert not app.exception
    assert any(b.label=='Abrir estudo →' for b in app.button)
    navigate(app,'Biblioteca')
    app.radio(key='library_section').set_value('Minha coleção').run()
    assert any(b.label=='Abrir página de estudo →' for b in app.button)


def test_existing_qwen_selection_migrates_to_lighter_llama_without_api_request():
    from unittest.mock import patch
    app=start()
    new=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120)
    new.session_state['auth_token']=app.session_state['auth_token']
    new.session_state['provider']='Ollama'
    new.session_state['model_Ollama']='qwen2.5:3b'
    new.session_state['qwen_migrated']=True
    with patch('core.ollama_client.OllamaClient.request') as request:
        new.run()
    assert not new.exception
    assert new.text_input(key='model_Ollama').value=='llama3.2:1b'
    request.assert_not_called()


def test_problem_is_generated_directly_from_current_study_even_with_dp_dropdown():
    app=start();navigate(app,'Laboratório IA')
    app.selectbox(key='concept').select('DP').run()
    request='Quero aprender SegTree com atualizações pontuais e mínimo.'
    app.text_area(key='learning_request').set_value(request).run()
    next(b for b in app.button if b.label=='Gerar material →').click().run()
    assert app.session_state['active_page']=='Meus estudos'
    app.button(key='study_practice').click().run()
    assert not app.exception
    assert app.session_state['active_page']=='Arena'
    generated=next(p for p in app.session_state['problems'] if p['id']==app.session_state['problem_id'])
    assert generated['topic']=='Segment Tree'
    assert generated['learning_request']==request
    assert generated['study_origin']['request']==request


def test_search_can_generate_a_problem_and_a_review_without_changing_topic():
    from core.knowledge import KnowledgeBase
    KnowledgeBase().import_documents([dict(title='Segment Tree',source='Test',url='https://example.org/segment-tree',content='Segment trees support range queries. '*30,license='CC0',topics=['tree'],tags=['segtree'])])
    app=start();navigate(app,'Biblioteca')
    app.radio(key='library_section').set_value('Acervo RAG').run()
    app.text_input(key='knowledge_query').set_value('SegTree com mínimo').run()
    app.button(key='knowledge_practice').click().run()
    assert not app.exception and app.session_state['active_page']=='Arena'
    first=app.session_state['problem_id']
    navigate(app,'Laboratório IA')
    app.button(key='practice_latest').click().run()
    assert not app.exception and app.session_state['active_page']=='Arena'
    generated=next(p for p in app.session_state['problems'] if p['id']==app.session_state['problem_id'])
    assert generated['id']!=first and generated['topic']=='Segment Tree'
    assert generated['practice_mode']=='review'


def test_research_defaults_to_foundations_and_advanced_is_opt_in():
    app=start()
    navigate(app,'Laboratório IA')
    assert not app.exception
    target=app.selectbox(key='research_target')
    assert target.value=='Soma de prefixos'
    assert 'Fundamentos e simulação' in target.options
    assert 'Segment Tree' not in target.options
    app.checkbox(key='research_advanced').set_value(True).run()
    assert not app.exception
    assert 'Segment Tree' in app.selectbox(key='research_target').options


def test_teacher_can_review_gemini_proposal_and_student_sees_only_own_assessment():
    import os,json
    from unittest.mock import patch
    from core.progress_store import ProgressStore
    from core.accounts import Accounts
    from core.classrooms import Classrooms
    from core.learner_assessment import LearnerAssessmentService
    from core.research.provider import Generation
    store=ProgressStore(os.environ['AUTOTUTOR_PROGRESS_DB']);accounts=Accounts(store);school=Classrooms(store,accounts)
    teacher=accounts.register('review_teacher','Professor teste','test-password','teacher')
    student=accounts.register('review_student','Aluno teste','test-password')
    cid=school.create(teacher,'Turma de avaliação');school.join(student,school._class(teacher,cid)['invite_code'])
    class Fixture:
        model='fixture-ui-not-gemini'
        def generate(self,system,prompt,schema):
            snap=json.loads(prompt);topic=snap['topics'][0]
            value={'level':'Inconclusivo','confidence':'baixa','summary':'Amostra limitada para avaliação.',
                   'observations':[{'evidence_id':topic['evidence_id'],'metric':'answered','value':topic['answered'],'interpretation':'Necessário observar a prática.'}],
                   'next_steps':[{'topic_id':topic['topic_id'],'evidence_ids':[topic['evidence_id']],'action':'Revisar fundamentos com exemplos.'}]}
            return Generation(json.dumps(value),{},self.model,0,'test')
    service=LearnerAssessmentService(store,accounts,school,Fixture());record=service.generate(student,cid,student,synthetic=True)
    with patch('core.learner_assessment.configured_provider',side_effect=AssertionError('Rendering must not send requests')):
        app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120);app.session_state['auth_token']=accounts.login('review_student','test-password');app.session_state['provider']='Ollama';app.run();navigate(app,'Turmas')
        assert not app.exception
        assert any(t.label=='Avaliação com professor' for t in app.tabs)
        assert not any(t.label=='Justificativa do professor' for t in app.text_area)
        teacher_app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120);teacher_app.session_state['auth_token']=accounts.login('review_teacher','test-password');teacher_app.session_state['provider']='Ollama';teacher_app.run();navigate(teacher_app,'Turmas')
        assert not teacher_app.exception
        teacher_app.text_area(key='teacher_assessment_comment_'+record['id']).set_value('Concordo com a incerteza; acompanhar a próxima atividade.')
        next(b for b in teacher_app.button if b.label=='Registrar parecer').click().run()
        assert not teacher_app.exception
        assert service.get(student,record['id'])['status']=='approved'
        app.run();assert not app.exception
        assert any('Concordo com a incerteza' in str(t.value) for t in app.markdown)
