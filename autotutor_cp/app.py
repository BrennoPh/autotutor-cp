"""AutoTutor Online Judge. Start with: .venv/bin/streamlit run app.py"""
import hashlib
from html import escape
import json
import os
import uuid
import math
import re
from collections import Counter
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st
import streamlit.components.v1 as components
from config import STARTER_CODE
from core.problem_bank import load_problems
from core.mini_judge import MiniJudge, JudgeError
from core.llm_client import LLMClient, AIUnavailable
from core.ollama_client import DEFAULT_LOCAL_MODEL
from core.ai_connection import update_connection, connection_label as describe_connection
from core.cloud_providers import QWEN_REGIONS
from core.autocode_engine import AutoCodeEngine
from core.codigen_tutor import CodigenTutor, CARDS
from core.rag_retriever import OIAssistantRAG
from core.progress_store import ProgressStore, DB_PATH, FIELDS
from core.learning_engine import load_curriculum
from core.ai_coach import learner_evidence,cached_analysis
from core.learning_views import render_library, render_diagnostic, render_roadmap, render_performance
from core.accounts import Accounts
from core.classrooms import Classrooms
from core.school_views import require_login, classroom_page
from core.catalog import catalog, external_problems, STUDY_SOURCES
from core.ui import styles, html, heading, badge, empty, problem_header, verdict_card, VERDICTS

st.set_page_config(page_title='AutoTutor · Online Judge', page_icon='⌘', layout='wide')
styles(st.session_state.get('theme_dark',True))
if not os.environ.get('AUTOTUTOR_KNOWLEDGE_DB'):
    from core.knowledge import KnowledgeBase
    KnowledgeBase().ensure_seeded()
store = ProgressStore(os.environ.get('AUTOTUTOR_PROGRESS_DB', str(DB_PATH)))
accounts, user = require_login(store)
school = Classrooms(store, accounts)
DEFAULTS = {'problems':load_problems(), 'history':[], 'results':{}, 'feedback':{},
            'helpers':{}, 'recommendations':{}, 'material':'', 'drafts':{},
            'ai_events':[], 'connection_checks':{}, 'available_models':{}, 'notices':[],
            'model_capabilities':{}, 'quiz_attempts':[], 'completed_lessons':[], 'study_hours':3, 'diagnostic_draft':{}, 'learning_topic':'fundamentals','theme_dark':True,'lab_preferences':{}}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# A profile belongs to the authenticated account. URL parameters cannot select another user.
profile_id = user['profile_id']
if 'perfil' in st.query_params:
    del st.query_params['perfil']
if st.session_state.get('progress_profile_id') != profile_id:
    stored = store.load(profile_id)
    for field in FIELDS:
        if field in stored:
            st.session_state[field] = stored[field]
    st.session_state.progress_profile_id = profile_id
    store.save(profile_id,st.session_state)
# Bring new local exercises to existing accounts without losing generated exercises or validated suites.
existing={p['id']:p for p in st.session_state.problems}
baseline=load_problems();base_ids={p['id'] for p in baseline}
st.session_state.problems=[existing[p['id']] if p['id'] in existing and existing[p['id']].get('std_cpp')==p.get('std_cpp') else p for p in baseline]+[p for p in st.session_state.problems if p['id'] not in base_ids]
styles(st.session_state.get('theme_dark',True))


def save_progress():
    store.save(profile_id, st.session_state)


if 'pending_level' in st.session_state:
    st.session_state.level = st.session_state.pop('pending_level')
if 'pending_lesson' in st.session_state:
    st.session_state.library_section='Aulas'
    st.session_state.learning_topic = st.session_state.pop('pending_lesson')
    st.session_state.lesson_picker = st.session_state.learning_topic

STUDY_PAGES = ['Laboratório IA','Meus estudos','Quadro Branco','Minha trilha','Biblioteca','Diagnóstico']
NAV = ['Visão geral','Laboratório IA','Meus estudos','Quadro Branco','Problemas','Aprendizado','Turmas','Meu desempenho','Configurações']
NAV_LABELS = {'Laboratório IA':'Criar estudo com IA','Meus estudos':'Meus estudos','Quadro Branco':'Quadro Branco IA','Visão geral':'Início','Problemas':'Problemas','Aprendizado':'Estudar','Turmas':'Turmas','Meu desempenho':'Progresso','Configurações':'Configurações'}
incoming_study=st.query_params.get('estudo')
if incoming_study and incoming_study!=st.session_state.get('study_url_loaded'):
    st.session_state.selected_material_id=incoming_study
    st.session_state.study_url_loaded=incoming_study
    st.session_state.pending_page='Meus estudos'
if 'pending_learning_request' in st.session_state:
    st.session_state.learning_request=st.session_state.pop('pending_learning_request')
if 'pending_concept' in st.session_state:
    requested=st.session_state.pop('pending_concept')
    if requested in CARDS:st.session_state.concept=requested
if 'pending_page' in st.session_state:
    target_page = st.session_state.pop('pending_page')
    if target_page in NAV:
        st.session_state.nav=target_page
        if target_page=='Problemas':st.session_state.problem_area='Catálogo'
        if target_page=='Meu desempenho':st.session_state.progress_section='Painel'
    elif target_page in STUDY_PAGES:
        st.session_state.nav='Aprendizado';st.session_state.study_section=target_page
    elif target_page=='Arena':
        st.session_state.nav='Problemas';st.session_state.problem_area='Arena'
    elif target_page=='Submissões':
        st.session_state.nav='Meu desempenho';st.session_state.progress_section='Submissões'
    else:
        st.session_state.nav=target_page
        if target_page=='Problemas':st.session_state.problem_area='Catálogo'
        if target_page=='Meu desempenho':st.session_state.progress_section='Painel'
if st.session_state.get('nav') not in NAV:st.session_state.nav='Visão geral'
if 'pending_problem' in st.session_state:
    st.session_state.problem_id = st.session_state.pop('pending_problem')
    st.session_state.problem_picker = st.session_state.problem_id
if 'pending_model' in st.session_state:
    target_provider, new_model = st.session_state.pop('pending_model')
    st.session_state['model_' + target_provider] = new_model
if 'pending_qwen_thinking' in st.session_state:
    st.session_state.qwen_thinking=st.session_state.pop('pending_qwen_thinking')


def go(page, pid=None):
    save_progress()
    st.session_state.pending_page = page
    if pid:
        st.session_state.pending_problem = pid
    st.rerun()


with st.sidebar:
    html('<div class="brand"><div class="brand-mark">&lt;/&gt;</div><div><strong>AutoTutor</strong><small>PRÁTICA E APRENDIZADO</small></div></div>')
    def reset_primary_page():
        st.session_state.problem_area='Catálogo';st.session_state.progress_section='Painel'
    primary_page = st.radio('Navegação', NAV, format_func=lambda x:NAV_LABELS[x], key='nav', label_visibility='collapsed',on_change=reset_primary_page)
    with st.expander('Preferências'):
        st.toggle('Tema escuro',key='theme_dark')
        level = st.selectbox('Nível de prática', ['Iniciante','Intermediário','Avançado'], key='level')
    history = st.session_state.history
    solved_titles = {h['problem'] for h in history if h['verdict']=='AC'}
    with st.expander('Assistente IA',expanded=primary_page=='Configurações'):
        if st.session_state.get('provider')=='Local':st.session_state.provider='Ollama'
        if not st.session_state.get('light_local_migrated'):
            if st.session_state.get('model_Ollama') in (None,'qwen2.5:3b'):st.session_state.model_Ollama=DEFAULT_LOCAL_MODEL
            st.session_state.light_local_migrated=True
        def switch_provider_key():
            keys=st.session_state.setdefault('_provider_keys',{})
            old=st.session_state.get('_key_provider')
            if old:keys[old]=st.session_state.get('api_key','')
            st.session_state.api_key=keys.get(st.session_state.provider,'')
            st.session_state._key_provider=st.session_state.provider
        provider = st.selectbox('Motor de IA', ['Ollama','Gemini','OpenAI','DeepSeek','Qwen'], format_func=lambda x:{'Ollama':'IA local · Llama 1B','Qwen':'Qwen · API Alibaba Cloud','DeepSeek':'DeepSeek · API'}.get(x,x), key='provider',on_change=switch_provider_key)
        st.session_state._key_provider=provider
        api_key = st.text_input('Chave de API', type='password', disabled=provider=='Ollama', key='api_key',help='Somente na memória desta sessão.')
        default_model={'Ollama':DEFAULT_LOCAL_MODEL,'Gemini':'gemini-3.1-flash-lite','OpenAI':'gpt-4o-mini','DeepSeek':'deepseek-flash','Qwen':'qwen-plus'}[provider]
        if 'model_'+provider not in st.session_state:st.session_state['model_'+provider]=default_model
        model=st.text_input('Modelo',key='model_'+provider)
        qwen_region='Singapura';qwen_workspace='';qwen_thinking=False
        if provider=='Qwen':
            qwen_region=st.selectbox('Região da API Qwen',list(QWEN_REGIONS),key='qwen_region')
            qwen_workspace=st.text_input('ID do workspace (opcional)',key='qwen_workspace',max_chars=64,help='Preencha se a sua conta usar um domínio dedicado de workspace.')
            qwen_thinking=st.toggle('Modelo Qwen exige raciocínio ativo',key='qwen_thinking',value=False,help='Ative para modelos que recusam desativar o raciocínio. Para JSON, escolha um modelo compatível.')
            st.caption('Use a chave do Alibaba Cloud Model Studio da região selecionada. A chave do chat Qwen não substitui a chave da API.')
        elif provider=='DeepSeek':
            st.caption('Use uma chave da plataforma de API DeepSeek. O modelo pode ser alterado ou consultado nas configurações.')
        if provider=='Ollama':
            st.caption('Executa neste computador, sem chave. Selecionar o motor não envia uma solicitação.')
            st.caption('Llama 3.2 1B · modelo leve experimental. Usa dois núcleos e libera a memória após cada resposta. Revise as explicações; as falhas não são substituídas por textos prontos.')
    st.divider()
    st.caption(user['name']+' · '+('Professor' if user['role']=='teacher' else 'Aluno'))
    if st.button('Sair da conta',key='logout',use_container_width=True):
        save_progress();accounts.logout(st.session_state.auth_token)
        st.session_state.clear();st.query_params.clear();st.rerun()
page=primary_page
if primary_page=='Aprendizado':page=st.session_state.get('study_section','Minha trilha')
elif primary_page=='Problemas' and st.session_state.get('problem_area')=='Arena':page='Arena'
elif primary_page=='Meu desempenho' and st.session_state.get('progress_section')=='Submissões':page='Submissões'
st.session_state.active_page=page


llm = LLMClient(provider, api_key, model, capabilities=st.session_state.model_capabilities,
                context_provider=lambda query:store.context(profile_id, query,max_chars=1500 if provider=='Ollama' else 7000),
                audit_callback=lambda record:store.log_model_call(profile_id,record), require_model=True,
                qwen_region=qwen_region,qwen_workspace=qwen_workspace,qwen_thinking=qwen_thinking)
try:
    from core.isolated_judge import IsolatedMiniJudge, isolation_available
    from core.mini_judge import MiniJudge
    judge = IsolatedMiniJudge() if isolation_available() else MiniJudge()
    tutor = CodigenTutor(llm)
    engine = AutoCodeEngine(llm, judge)
    rag = OIAssistantRAG(catalog(), llm)
    fingerprint = hashlib.sha256(f'{provider}|{llm.model}|{llm.api_key}|{qwen_region}|{qwen_workspace}|{qwen_thinking}'.encode()).hexdigest()
    connection = st.session_state.connection_checks.get(fingerprint)
    connection_label, connection_tone = describe_connection(provider, llm.enabled, connection)


    def capture_ai(operation):
        events = list(llm.events)
        llm.events.clear()
        for event in events:
            event.update(operation=operation, time=datetime.now(ZoneInfo('America/Maceio')).isoformat(timespec='seconds'))
            st.session_state.ai_events.append(event)
        st.session_state.ai_events = st.session_state.ai_events[-40:]
        successes = [e for e in events if e['source'] == 'api']
        errors = [e for e in events if e['source'] == 'local']
        updated = update_connection(st.session_state.connection_checks.get(fingerprint), events)
        if updated:
            st.session_state.connection_checks[fingerprint] = updated
        for event in errors + [e for e in events if e['source'] == 'notice']:
            st.session_state.notices.append(event['message'])
        save_progress()
        return 'local' if errors or not successes else provider


    def show_notices():
        notices = list(st.session_state.get('notices', []))
        st.session_state.notices = []
        for message in dict.fromkeys(notices):
            st.warning(message)


    html(f'<div class="topbar"><strong>{escape(NAV_LABELS[primary_page])}</strong><span>{escape(user["name"])}</span></div>')
    if primary_page=='Aprendizado':
        has_completed_diagnostic = bool(
            st.session_state.get('quiz_attempts')
            or any(a.get('kind') == 'diagnostic' for a in st.session_state.get('quiz_attempts', []))
            or (store and profile_id and store.artifacts(profile_id, 'quiz'))
        )
        study_tabs = ['Laboratório IA','Meus estudos','Quadro Branco','Minha trilha','Biblioteca']
        if not has_completed_diagnostic or st.session_state.get('study_section') == 'Diagnóstico':
            study_tabs.append('Diagnóstico')
        current_study_section = st.session_state.get('study_section', 'Minha trilha')
        if current_study_section not in study_tabs:
            current_study_section = 'Minha trilha'
            st.session_state.study_section = current_study_section
        st.radio('Área de estudo', study_tabs, key='study_section', horizontal=True, label_visibility='collapsed')
    elif primary_page=='Meu desempenho':
        st.radio('Área de progresso',['Painel','Submissões'],key='progress_section',horizontal=True,label_visibility='collapsed')
    show_notices()
    problems = catalog(st.session_state.problems)
    external_status = school.external_for(user["id"])
    solved_ids = {h.get("problem_id") for h in history if h["verdict"]=="AC"} | {pid for pid,value in external_status.items() if value["status"]=="solved" and any(p['id']==pid and p.get('external') for p in problems)}
    by_id = {p['id']:p for p in problems}
    if st.session_state.get('problem_id') not in by_id:
        st.session_state.problem_id = problems[0]['id']


    def metrics():
        total = len(history)
        accepted = sum(h['verdict'] == 'AC' for h in history)
        with st.container(key='metrics_grid'):
            columns = st.columns(4)
            for column,label,value in zip(columns, ['Problemas disponíveis','Problemas resolvidos','Suas submissões','Taxa de acerto'],
                                          [len(problems),len(solved_titles),total,f'{accepted/total:.0%}' if total else '—']):
                column.metric(label, value)


    def problem_row(p, number):
        with st.container(border=True, key='row_' + p['id']):
            number_col, title_col, difficulty_col, action_col = st.columns([.5,4,1.4,1.25], vertical_alignment='center')
            number_col.markdown(f'<div class="problem-number">{number:04d}</div>', unsafe_allow_html=True)
            with title_col:
                html(f'<div class="catalog-title">{escape(p["title"])}</div>'
                     f'<div class="catalog-meta">{escape(p["topic"])} · {escape(p.get("source","Juiz local"))}'
                     f'{" · Juiz externo" if p.get("external") else " · Correção aqui"}'
                     f'{" · Validação dupla ✓" if p.get("double_validated") else ""}</div>')
            with difficulty_col:
                tone = {'Iniciante':'easy','Intermediário':'medium','Avançado':'hard'}[p['difficulty']]
                html(badge(p['difficulty'], tone))
                if p['id'] in solved_ids:
                    html('<div class="catalog-meta" style="color:var(--success)">✓ Resolvido</div>')
            if action_col.button('Ver exercício →' if p.get('external') else 'Resolver aqui →', key='solve_' + p['id'], use_container_width=True):
                go('Arena', p['id'])


    if page == 'Visão geral':
        html('<section class="workspace-hero"><div class="eyebrow">SEU TREINO COMEÇA AQUI</div><h1>Entenda. Pratique. Evolua.</h1><p>Do primeiro algoritmo à próxima competição. Organize o estudo, entenda os fundamentos e teste suas ideias no juiz.</p><div class="hero-tags"><span>Fundamentos</span><span>Estudo com IA</span><span>Juiz C++17</span></div></section>')
        quick=st.columns(4,gap='medium')
        for col,label,description,target,key in zip(quick,
            ['Criar estudo com IA','Meus estudos','Montar uma trilha','Explorar a biblioteca'],
            ['Explique o que quer aprender.','Retome suas páginas de leitura.','Organize assunto, dias e prática.','Encontre aulas, artigos e vídeos.'],
            ['Laboratório IA','Meus estudos','Minha trilha','Biblioteca'],
            ['quick_create','quick_studies','quick_path','quick_library']):
            with col:
                with st.container(border=True):
                    st.markdown('### '+label);st.caption(description)
                    if st.button('Abrir →',key=key,use_container_width=True):go(target)
        st.markdown('### Sua próxima prática')
        evidence=learner_evidence(st.session_state.quiz_attempts,history,st.session_state.completed_lessons,st.session_state.study_hours)
        analysis=cached_analysis(store,profile_id,evidence,llm)
        recommendation=analysis['roadmap'][0] if analysis else None
        topic_names={t['id']:t['title'] for t in load_curriculum()}
        study,practice=st.columns(2,gap='large')
        with study:
            with st.container(border=True):
                st.markdown('### '+(topic_names[recommendation['topic_id']] if recommendation else 'Sua trilha de estudo'))
                st.caption('Sua próxima sugestão de estudo.')
                if st.button('Continuar estudando →',type='primary',key='home_study'):
                    if recommendation:st.session_state.pending_lesson=recommendation['topic_id']
                    go('Biblioteca' if recommendation else 'Minha trilha')
        with practice:
            with st.container(border=True):
                st.markdown('### '+str(len(problems))+' problemas')
                st.caption(f'{len(st.session_state.problems)} com correção aqui; os demais com referência externa.')
                if st.button('Escolher um desafio →',key='home_catalog'):go('Problemas')
        has_completed_diagnostic = bool(
            st.session_state.get('quiz_attempts')
            or any(a.get('kind') == 'diagnostic' for a in st.session_state.get('quiz_attempts', []))
            or (store and profile_id and store.artifacts(profile_id, 'quiz'))
        )
        if not has_completed_diagnostic:
            st.caption('Ainda não sabe por onde começar? O diagnóstico ajuda a orientar a sua trilha.')
            if st.button('Fazer diagnóstico inicial',key='home_diagnostic'):go('Diagnóstico')
        if user['role']=='teacher':
            if st.button('Acompanhar minhas turmas →',key='home_classes'):go('Turmas')

        st.divider();st.markdown('### Continue uma leitura')
        from core.study_pages import study_cards
        study_cards(store,profile_id,go,limit=3,key='home_studies')
        st.markdown('### Explore os fundamentos')
        foundation=st.columns(3)
        for i,(label,subject) in enumerate([('01 · Complexidade e implementação','Matemática'),('02 · Prefixos e busca binária','Prefix Sum'),('03 · BFS, DFS e árvores','Grafos'),('04 · Programação dinâmica','DP'),('05 · Guloso e argumentos de correção','Guloso'),('06 · Segment Tree e intervalos','Segment Tree')]):
            if foundation[i%3].button(label,key='foundation_'+str(i),use_container_width=True):
                st.session_state.pending_learning_request='Quero estudar '+label.split(' · ')[1]+' desde os fundamentos de programação competitiva.'
                st.session_state.pending_concept=subject;go('Laboratório IA')
    elif page == 'Turmas':
        classroom_page(store,accounts,user,go,llm)

    elif page == 'Diagnóstico':
        render_diagnostic(store,profile_id,save_progress,go,llm)
    elif page == 'Minha trilha':
        render_roadmap(store,profile_id,save_progress,go,llm,on_ai=capture_ai)
    elif page == 'Meus estudos':
        from core.study_pages import render_studies
        render_studies(store,profile_id,go,problems)
    elif page == 'Quadro Branco':
        from core.whiteboard_views import render_whiteboard
        render_whiteboard(store,profile_id,go,llm,user)
    elif page == 'Biblioteca':
        render_library(store,profile_id,save_progress,go,problems)
    elif page == 'Meu desempenho':
        render_performance(store,profile_id,save_progress,go,llm)

    elif page == 'Problemas':
        heading('','Problemas','Escolha um assunto e pratique no seu ritmo.')
        search_col,topic_col,source_col,judge_col=st.columns([2,1,1,1])
        search=search_col.text_input('Buscar',placeholder='Título ou conceito…',key='catalog_search')
        topic=topic_col.selectbox('Assunto',['Todos']+sorted({p['topic'] for p in problems}),key='catalog_topic')
        source=source_col.selectbox('Fonte',['Todas','Juiz local','CSES','USACO Guide'],key='catalog_source')
        judge_filter=judge_col.selectbox('Correção',['Todas','Dentro do AutoTutor','Juiz externo'],key='catalog_judge')
        with st.expander('Mais filtros'):
            options=st.columns(2)
            difficulty=options[0].selectbox('Nível',['Todas','Iniciante','Intermediário','Avançado'],key='catalog_difficulty')
            status=options[1].selectbox('Situação',['Todos','Não resolvidos','Resolvidos'],key='catalog_status')
            st.caption('Os níveis dos exercícios externos são estimativas para organizar o catálogo; não são ratings oficiais.')
        filtered=[p for p in problems if (not search or search.casefold() in (p['title']+' '+' '.join(p['tags'])).casefold())
                  and (topic=='Todos' or p['topic']==topic) and (source=='Todas' or (source=='Juiz local' and not p.get('external')) or p.get('source','Juiz local')==source)
                  and (judge_filter=='Todas' or bool(p.get('external'))==(judge_filter=='Juiz externo'))
                  and (difficulty=='Todas' or p['difficulty']==difficulty)
                  and (status=='Todos' or (p['id'] in solved_ids)==(status=='Resolvidos'))]
        total_pages=max(1,math.ceil(len(filtered)/20))
        if st.session_state.get('catalog_page',1)>total_pages:st.session_state.catalog_page=1
        page_number=st.selectbox('Página',list(range(1,total_pages+1)),key='catalog_page')
        start=(page_number-1)*20
        st.caption(f'{len(filtered)} problemas · página {page_number}/{total_pages} · {len(st.session_state.problems)} corrigidos localmente')
        for p in filtered[start:start+20]:problem_row(p,problems.index(p)+1)
        if not filtered:empty('Nenhum resultado','Tente outro termo ou altere os filtros.')

    elif page == 'Arena':
        choice, back = st.columns([4,1])
        pid = choice.selectbox('Problema em prática', list(by_id), format_func=lambda x:by_id[x]['title'], index=list(by_id).index(st.session_state.problem_id), key='problem_picker', label_visibility='collapsed')
        if back.button('← Problemas', use_container_width=True):
            go('Problemas')
        p = by_id[pid]
        if p.get('practice_mode')=='review':st.info('Revisão do mesmo contrato: este problema pratica novamente o objetivo já usado, com nova geração e testes. Não representa um algoritmo novo.')
        st.session_state.problem_id = pid
        if p.get('external'):
            heading('',p['title'],p['source']+' · '+p['section'])
            st.caption('Enunciado e submissão no juiz de origem. A conclusão registrada aqui é externa, não um AC do Mini-Judge.')
            st.link_button('Abrir enunciado oficial ↗',p['url'],type='primary')
            with st.expander('Sobre este exercício'):
                st.write('Assunto: '+p['topic'])
                st.caption(p['difficulty_basis'])
                st.markdown('[Fonte do catálogo]('+p['source_url']+')')
            previous=external_status.get(pid)
            if previous:st.success(('Conclusão confirmada por professor' if previous['verified'] else 'Conclusão autodeclarada') if previous['status']=='solved' else 'Em andamento')
            proof=st.text_input('Link da sua submissão no juiz (opcional)',value=previous['proof_url'] if previous else '',key='proof_'+pid)
            actions=st.columns(2)
            for column,label,new_status in [(actions[0],'Marcar em andamento','in_progress'),(actions[1],'Registrar como resolvido','solved')]:
                if column.button(label,key='external_'+new_status+'_'+pid):
                    try:school.record_external(user['id'],pid,new_status,proof);st.rerun()
                    except ValueError as exc:st.warning(str(exc))
            if st.button('Estudar este assunto',key='external_study'):
                match=next((t for t in load_curriculum() if t['title']==p['topic']),None)
                if match:st.session_state.pending_lesson=match['id']
                go('Biblioteca')
            save_progress()
            st.stop()
        problem_header(p,problems.index(p)+1,p['id'] in solved_ids)
        if p.get('local_task'):st.caption('Correção dentro do AutoTutor · enunciado adaptado do CSES · testes próprios, não oficiais. Seu AC é local.')
        statement_col, editor_col = st.columns([1,1.1], gap='large')
        with statement_col:
            with st.container(border=True):
                statement_tab, tips_tab, similar_tab = st.tabs(['Enunciado','Tutor & dicas','Similares'])
                with statement_tab:
                    # The title is already in the page header.
                    from core.autocode_engine import sanitize_statement
                    statement = sanitize_statement(p['statement'])
                    if statement.startswith('## '):
                        statement = statement.split('\n', 1)[-1].lstrip()
                    st.markdown(statement)
                    for i,example in enumerate(p['examples'], 1):
                        st.markdown(f'#### Exemplo {i}')
                        sample_cols = st.columns(2)
                        sample_cols[0].caption('ENTRADA'); sample_cols[0].code(example['input'], language='text')
                        sample_cols[1].caption('SAÍDA'); sample_cols[1].code(example['expected_output'], language='text')
                    if p.get('double_validated'):
                        st.caption('✓ Testes verificados por validação dupla')
                        with st.expander('Verificação dos testes'):
                            st.json(p['validation'])
                with tips_tab:
                    st.markdown('#### Um empurrão na direção certa')
                    st.markdown(st.session_state.feedback.get(pid, 'Escreva sua primeira tentativa. Depois de submeter, vamos investigar juntos os pontos que precisam de atenção.'))
                    if pid in st.session_state.get('feedback_sources', {}):
                        st.caption('Orientação por ' + st.session_state.feedback_sources[pid])
                    prereqs_p = p.get('prerequisites')
                    if not prereqs_p:
                        from core.prerequisites import detect_prerequisites
                        detected = detect_prerequisites(p.get('statement', ''), p.get('topic', ''))
                        if detected:
                            prereqs_p = detected[0]
                    if prereqs_p:
                        from core.prerequisites import build_prerequisite_primer_markdown
                        with st.expander(f"🎓 Revisar estruturas e conceitos base ({prereqs_p['title']})"):
                            st.markdown(build_prerequisite_primer_markdown(prereqs_p))
                    if st.toggle('Explorar a estratégia visual', key='flow_' + pid):
                        st.caption('Complexidade de referência: ' + p['complexity'])
                        graph_key=hashlib.sha256((llm.provider+'|'+llm.model+'|'+p['statement']).encode()).hexdigest()
                        graphs=st.session_state.setdefault('ai_flowcharts',{})
                        if graph_key not in graphs:
                            graphs[graph_key]=tutor.generate_flowchart(p)
                            store.add_artifact(profile_id,'helper','Fluxograma · '+p['title'],dict(content=graphs[graph_key],concept=p['topic'],source=llm.provider+' · '+llm.model))
                            capture_ai('Gerar fluxograma')
                        graph=graphs[graph_key]
                        source = json.dumps(graph).replace('<', '\\u003c')
                        components.html('''<div id="diagram"></div><script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
    mermaid.initialize({startOnLoad:false,securityLevel:'strict',theme:'neutral'});
    const {svg}=await mermaid.render('flow', ''' + source + ''');
    document.getElementById('diagram').innerHTML=svg;</script>''', height=490, scrolling=True)
                        with st.expander('Ver fonte Mermaid'):
                            st.code(graph, language='mermaid')
                with similar_tab:
                    query = st.text_area('Qual conceito você quer praticar?', placeholder='Ex.: somas em intervalos, menor caminho…', key='query_' + pid, height=95)
                    if st.button('Buscar problemas similares', key='search_' + pid, use_container_width=True):
                        with st.spinner('Encontrando padrões em comum…'):
                            st.session_state.recommendations[pid] = rag.retrieve(query or p['statement'], exclude_id=pid)
                        rec_source=capture_ai('Buscar problemas similares')
                        store.add_artifact(profile_id,'recommendations','Prática recomendada · '+p['title'],{'problem_id':pid,'concept':p['topic'],'source':rec_source,'references':rag.last_retrieval,'items':[{'id':r['problem']['id'],'title':r['problem']['title'],'reason':r['reason']} for r in st.session_state.recommendations[pid]]})
                        st.rerun()
                    recommendations = st.session_state.recommendations.get(pid, [])
                    if not recommendations:
                        st.caption('Peça uma recomendação ou envie sua primeira solução para encontrar desafios relacionados.')
                    for item in recommendations:
                        target = item['problem']
                        st.markdown('#### ' + target['title'])
                        st.write(item['reason'])
                        with st.expander('Por que este problema?'):
                            st.json(item['vector_scores'])
                        if st.button('Praticar este problema →', key='practice_' + pid + '_' + target['id']):
                            go('Arena', target['id'])
        with editor_col:
            with st.container(border=True):
                label_col,language_col = st.columns([2,1])
                label_col.markdown('#### Sua solução')
                language_col.markdown(badge('C++17 · GCC', 'indigo'), unsafe_allow_html=True)
                def save_draft():
                    st.session_state.drafts[pid] = st.session_state['code_' + pid]
                    save_progress()
                code = st.text_area('Editor de código C++17', value=st.session_state.drafts.get(pid, STARTER_CODE), height=400,
                                    key='code_' + pid, max_chars=100000, on_change=save_draft, label_visibility='collapsed')
                st.caption(f'{len(code.splitlines())} linhas · limite de {p["time_limit_sec"]} s por teste · memória {p["memory_limit_mb"]} MB')
                submit = st.button('Submeter solução →', type='primary', use_container_width=True, key='submit')
                helper_cols = st.columns(3)
                if helper_cols[0].button('Explicar código', use_container_width=True):
                    with st.spinner('Lendo sua solução…'):
                        st.session_state.helpers[pid] = ('text', tutor.explain_code(code))
                    helper_source=capture_ai('Explicar código')
                    store.add_artifact(profile_id,'helper','Explicação · '+p['title'],{'problem_id':pid,'concept':p['topic'],'content':st.session_state.helpers[pid][1],'source':helper_source})
                    save_progress()
                    st.toast('Explicação disponível abaixo do editor.')
                    st.rerun()
                if helper_cols[1].button('Anotar código', use_container_width=True):
                    st.session_state.helpers[pid] = ('code', tutor.annotate_line_by_line(code))
                    store.add_artifact(profile_id,'helper','Anotações · '+p['title'],{'problem_id':pid,'concept':p['topic'],'content':st.session_state.helpers[pid][1],'source':'local'})
                    save_progress()
                    st.toast('Anotações disponíveis abaixo do editor.')
                    st.rerun()
                if helper_cols[2].button('Lacunas', use_container_width=True):
                    st.session_state.helpers[pid] = ('text', tutor.generate_fill_in_blanks(p['topic'], history))
                    store.add_artifact(profile_id,'helper','Lacunas · '+p['title'],{'problem_id':pid,'concept':p['topic'],'content':st.session_state.helpers[pid][1],'source':'local'})
                    save_progress()
                    st.rerun()
            helper = st.session_state.helpers.get(pid)
            if helper:
                with st.expander('Orientação sobre seu código', expanded=True):
                    if helper[0] == 'code':
                        st.code(helper[1], language='cpp')
                    else:
                        st.markdown(helper[1])
            if submit:
                st.session_state.drafts[pid] = code
                try:
                    with st.status('Avaliando sua solução…', expanded=True) as evaluation:
                        if not p.get('double_validated'):
                            st.write('Preparando e verificando os casos de teste…')
                            p = engine.double_validate(p)
                            st.session_state.problems = [p if item['id']==pid else item for item in st.session_state.problems]
                        st.write('Compilando C++17 e executando os testes…')
                        result = judge.judge(code, p['tests'], p['time_limit_sec'])
                        result['code_hash'] = hashlib.sha256(code.encode()).hexdigest()
                        st.session_state.results[pid] = result
                        elapsed = max((r['execution_time_ms'] for r in result['tests']), default=0)
                        entry = {'id':len(history)+1,'problem_id':pid, 'problem':p['title'], 'topic':p['topic'],
                                 'verdict':result['verdict'], 'time_ms':round(elapsed, 2), 'language':'C++17',
                                 'time':datetime.now(ZoneInfo('America/Maceio')).isoformat(timespec='seconds')}
                        st.session_state.history.append(entry)
                        store.add_artifact(profile_id,'submission',p['title'],{'record':entry,'source_code':code,'result':result})
                        save_progress()
                        st.write('Veredito: ' + VERDICTS[result['verdict']])
                        st.session_state.feedback[pid] = tutor.diagnose_error(p, code, result, history[-10:])
                        source = capture_ai('Diagnóstico de submissão')
                        if 'feedback_sources' not in st.session_state:
                            st.session_state.feedback_sources = {}
                        st.session_state.feedback_sources[pid] = source
                        # Recommendations are explicitly generated by the selected model in the Similares tab.
                        st.session_state.recommendations.pop(pid,None)
                        store.add_artifact(profile_id,'feedback','Diagnóstico · '+p['title'],{'problem_id':pid,'concept':p['topic'],'content':st.session_state.feedback[pid],'source':st.session_state.feedback_sources[pid]})
                        save_progress()
                        evaluation.update(label='Avaliação concluída', state='complete', expanded=False)
                    st.rerun()
                except (JudgeError, ValueError, OSError) as exc:
                    st.error('Não foi possível julgar: ' + str(exc)[:1600])
            result = st.session_state.results.get(pid)
            if not result:
                empty('Pronto para sua primeira tentativa?', 'Envie sua solução para acompanhar o veredito e os testes executados.', '⌘')
            else:
                if result['code_hash'] != hashlib.sha256(code.encode()).hexdigest():
                    st.caption('Você alterou o código. O resultado abaixo corresponde à última submissão.')
                verdict_card(result)
                with st.expander('Detalhes da avaliação', expanded=result['verdict'] != 'AC'):
                    rows = [{'Teste':r['test_id'],'Grupo':r['strategy'],'Resultado':r['verdict'],'Tempo (ms)':r['execution_time_ms']} for r in result['tests']]
                    if rows:
                        st.dataframe(rows, hide_index=True, use_container_width=True)
                    if result['message']:
                        st.code(result['message'][:16000], language='text')
                    failed = result.get('failed_test')
                    if failed:
                        for label,key in [('Entrada','input'),('Esperado','expected_output'),('Obtido','actual_output')]:
                            st.caption(label + (' (prévia)' if len(failed[key])>8000 else ''))
                            st.code(failed[key][:8000], language='text')
                        st.download_button('Baixar caso completo', json.dumps(failed, ensure_ascii=False, indent=2), 'caso_falho.json', 'application/json')

    elif page == 'Submissões':
        heading('SEU PERCURSO', 'Toda tentativa conta.', 'Acompanhe seus resultados e volte aos problemas com uma nova ideia.')
        metrics()
        if not history:
            empty('Sua história começa com uma submissão', 'Escolha um problema e envie sua primeira solução. Seus resultados aparecerão aqui.', '↗')
            if st.button('Encontrar um desafio →', type='primary'):
                go('Problemas')
        else:
            filter_cols = st.columns([1,3])
            verdict_filter = filter_cols[0].selectbox('Filtrar veredito', ['Todos'] + list(VERDICTS), key='verdict_filter')
            rows = [h for h in reversed(history) if verdict_filter == 'Todos' or h['verdict'] == verdict_filter]
            if rows:
                st.dataframe(rows, hide_index=True, use_container_width=True)
            else:
                empty('Nenhuma submissão com este veredito', 'Escolha outro filtro para ver suas tentativas.')
            st.download_button('Exportar histórico', json.dumps(history, ensure_ascii=False, indent=2), 'historico.json', 'application/json')
            selected_history = st.selectbox('Reabrir um problema', list(dict.fromkeys(h.get('problem_id') for h in reversed(history) if h.get('problem_id') in by_id)),
                                            format_func=lambda x:by_id[x]['title'], key='history_problem')
            if selected_history and st.button('Voltar à arena →'):
                go('Arena', selected_history)
            st.caption('Abra Meu desempenho para solicitar à IA uma análise das suas tentativas.')

    elif page == 'Laboratório IA':
        from core.research.views import research_controls
        research_controls(store,profile_id,go)
        pending_practice=st.session_state.pop('pending_practice',None)
        if pending_practice:
            try:
                with st.spinner('Criando problema sobre '+pending_practice['request'][:100]+'…'):
                    generated=engine.generate_problem(pending_practice.get('level','Iniciante'),pending_practice.get('concept',''),pending_practice.get('theme',''),learning_request=pending_practice['request'],recent_problems=[p for p in st.session_state.problems if p.get('seed_id')][-8:],allow_review=True)
                generated['study_origin']=pending_practice
                capture_ai('Criar problema do estudo')
                st.session_state.problems.append(generated)
                store.add_artifact(profile_id,'problem',generated['title'],generated)
                go('Arena',generated['id'])
            except (JudgeError,ValueError,OSError) as exc:
                capture_ai('Criar problema do estudo')
                st.error('Não foi possível criar um problema validado desse assunto: '+str(exc)[:1200])
        heading('APRENDA DO SEU JEITO', 'Uma nova forma de destravar ideias.', 'Crie materiais e desafios no seu nível, com temas que fazem sentido para você.')
        from core.practice_context import study_context,queue_practice
        latest_context=st.session_state.get('last_practice_context')
        if not latest_context:
            latest_items=store.artifacts(profile_id,kind='material',limit=1)
            if latest_items:latest_context=study_context(latest_items[0])
        if latest_context:
            st.caption('Último assunto estudado ou pesquisado: '+latest_context['request'][:200])
            if st.button('Criar problema do último assunto →',key='practice_latest'):
                queue_practice(st.session_state,latest_context,go)
        controls, output = st.columns([2,1], gap='large')
        with controls:
            with st.container(border=True):
                st.markdown('### O que vamos aprender hoje?')
                from core.material_preferences import LENGTHS, DEPTHS, DEFAULT_PREFERENCES
                for pref,default in DEFAULT_PREFERENCES.items():
                    if pref not in st.session_state:st.session_state[pref]=st.session_state.lab_preferences.get(pref,default)
                def remember_lab_preferences():
                    st.session_state.lab_preferences={key:st.session_state[key] for key in DEFAULT_PREFERENCES}
                    save_progress()
                learning_request=st.text_area('O que você quer aprender?',placeholder='Ex.: Quero aprender Segment Tree desde os pré-requisitos, com consultas de mínimo, atualizações, prova de correção e exemplos passo a passo. Quero cerca de 5000 caracteres.',
                                              key='learning_request',height=180,max_chars=2000,on_change=remember_lab_preferences)
                length_col,depth_col=st.columns(2)
                material_length=length_col.selectbox('Tamanho do texto',list(LENGTHS),key='material_length',on_change=remember_lab_preferences)
                material_depth=depth_col.selectbox('Profundidade',list(DEPTHS),key='material_depth',on_change=remember_lab_preferences)
                concept = st.selectbox('Assunto de referência', list(CARDS), key='concept')
                study_level=st.selectbox('Nível deste estudo',['Iniciante','Intermediário','Avançado'],index=['Iniciante','Intermediário','Avançado'].index(level),key='lab_level')
                kind = st.selectbox('Tipo de material', ['Explicação','Exemplo Comentado','Exercício Prático'], key='material_kind')
                with st.container():
                    theme = st.text_input('Tema de interesse (opcional)', key='theme', max_chars=100)

                    include_examples=st.checkbox('Incluir exemplos',key='material_examples',on_change=remember_lab_preferences)
                    include_exercises=st.checkbox('Incluir exercícios',key='material_exercises',on_change=remember_lab_preferences)
                target_chars=st.number_input('Meta de caracteres do estudo',min_value=500,max_value=20000,step=500,key='material_target_chars',disabled=material_length!='Longo',on_change=remember_lab_preferences,help='Para conteúdos longos, 5000 caracteres ou mais permitem desenvolver teoria e exemplos. Uma quantidade explícita no pedido tem prioridade.')
                lower,upper=LENGTHS[material_length]
                from core.prerequisites import detect_prerequisites, build_prerequisite_primer_markdown
                detected_prereqs = detect_prerequisites(learning_request, concept)
                prereq_decision = None
                if detected_prereqs:
                    p_spec = detected_prereqs[0]
                    known_mastery = st.session_state.setdefault('prereq_mastery', {}).get(p_spec['id'])
                    reopen_key = f"reopen_prereq_{p_spec['id']}"
                    is_editing = st.session_state.get(reopen_key, False)

                    if known_mastery and not is_editing:
                        prereq_decision = known_mastery
                        col_stat, col_btn = st.columns([3, 1])
                        with col_stat:
                            if known_mastery == 'skip':
                                st.caption(f"✓ Nivelamento salvo: você já domina **{p_spec['title']}**.")
                            else:
                                st.caption(f"ℹ️ Nivelamento salvo: modo revisão de **{p_spec['title']}** ativo.")
                        with col_btn:
                            if st.button("Alterar", key=f"btn_edit_prereq_{p_spec['id']}", help="Clique para alterar seu nível prévio sobre este assunto"):
                                st.session_state[reopen_key] = True
                                st.rerun()
                    else:
                        with st.container(border=True):
                            st.markdown(f"**🎓 Guia Pedagógico de Pré-Requisitos: {p_spec['title']}**")
                            st.caption(f"Identificamos que este estudo requer conceitos base: {p_spec['description']}")
                            default_idx = 0 if known_mastery != 'explain' else 1
                            p_choice = st.radio(
                                "Você já domina esses conceitos previamente?",
                                [
                                    "Sim, já domino! (Ir direto ao algoritmo avançado)",
                                    "Não / Quero revisar (Explicar pré-requisitos antes)"
                                ],
                                index=default_idx,
                                horizontal=True,
                                key=f"prereq_choice_{p_spec['id']}",
                                help="Se escolher revisar, o material e as explicações começarão detalhando as estruturas fundamentais (operações FIFO vs LIFO, ilustrações e código) antes de avançar."
                            )
                            prereq_decision = 'explain' if 'Quero revisar' in p_choice else 'skip'
                            st.session_state.prereq_mastery[p_spec['id']] = prereq_decision
                            if is_editing:
                                if st.button("Salvar nivelamento", key=f"save_prereq_{p_spec['id']}"):
                                    st.session_state[reopen_key] = False
                                    st.rerun()
                            with st.expander(f"👀 Ver resumo rápido de {p_spec['title']}"):
                                st.markdown(build_prerequisite_primer_markdown(p_spec))
                st.caption(f'Cerca de {lower}–{upper} palavras, além das referências. O tamanho pode variar.')
                st.caption(f'Nível: {study_level} · Motor: {provider}')
                if st.button('Gerar material →', type='primary', use_container_width=True):
                    with st.status('Criando seu estudo…',expanded=True) as generation_status:
                        st.write('Consultando o acervo e preparando uma explicação para o seu pedido.')
                        st.session_state.material = tutor.generate_material(kind, concept, study_level, theme, learning_request=learning_request, length=material_length, depth=material_depth, include_examples=include_examples, include_exercises=include_exercises, target_chars=target_chars if material_length=='Longo' else None, learner_evidence=store.learning_evidence(profile_id, query=learning_request.strip() or concept), prereq_decision=prereq_decision)
                    st.session_state.material_source = capture_ai('Gerar material')
                    from core.library import references_for
                    first_heading=re.match(r'^#{1,2}\s+(.+)',st.session_state.material.lstrip())
                    study_title=first_heading[1].strip()[:160] if first_heading else (learning_request[:160] or kind+' · '+concept)
                    material_id=store.add_artifact(profile_id,'material',study_title,{'content':st.session_state.material,'concept':concept,'level':study_level,'theme':theme,'type':kind,'source':st.session_state.material_source,'references':tutor.last_recommendations+tutor.last_retrieval,'retrieved_sources':tutor.last_retrieval,'retrieval_query':learning_request.strip() or concept,'learning_request':learning_request,'prereq_decision':prereq_decision,'preferences':{'length':material_length,'depth':material_depth,'include_examples':include_examples,'include_exercises':include_exercises,'target_chars':target_chars if material_length=='Longo' else None}})
                    save_progress()
                    from core.study_pages import open_study
                    open_study(material_id,go)
                st.divider()
                st.markdown('#### Quer colocar em prática?')
                st.caption('A IA escolhe entre 39 contratos com testes locais, priorizando contratos diferentes dos oito últimos usados. Quando só houver um compatível, ele será identificado como revisão do mesmo contrato.')
                if st.button('Criar problema adaptativo →', use_container_width=True):
                    try:
                        with st.spinner('Criando e verificando os testes…'):
                            generated = engine.generate_problem(study_level, concept, theme, learning_request=learning_request,
                                recent_problems=[p for p in st.session_state.problems if p.get('seed_id')][-8:],allow_review=True,prereq_decision=prereq_decision)
                        capture_ai('Criar problema adaptativo')
                        st.session_state.problems.append(generated)
                        store.add_artifact(profile_id,'problem',generated['title'],generated)
                        go('Arena', generated['id'])
                    except (JudgeError, ValueError, OSError) as exc:
                        capture_ai('Criar problema adaptativo')
                        show_notices()
                        st.error('O exercício não passou na validação e não foi publicado: ' + str(exc)[:1600])
            html('<div class="tip-card"><h3>Orientação, na medida certa.</h3><p>O tutor oferece perguntas e pistas. Você continua sendo quem encontra a solução.</p></div>')
        with output:
            with st.container(border=True):
                st.markdown('### Como seu estudo é criado')
                st.markdown('**1. Defina o objetivo**\n\nDiga o assunto, as dúvidas e os pré-requisitos que quer revisar.\n\n**2. Escolha a profundidade**\n\nPeça teoria, complexidade, exemplos rastreados e exercícios.\n\n**3. Leia na sua página**\n\nO estudo fica salvo com sumário, anotações e referências.')
                st.caption('A IA usa seu pedido e os textos recuperados do acervo. Revise resultados e exemplos.')
            st.caption(connection_label)
            if st.button('Configurar assistente IA',key='lab_config',use_container_width=True):go('Configurações')
            if st.button('Ver meus estudos salvos →',key='lab_saved',use_container_width=True):
                st.session_state.pop('selected_material_id',None);st.query_params.pop('estudo',None);go('Meus estudos')
            if st.session_state.material:
                st.caption('Seu último material continua salvo na biblioteca.')


    elif page == 'Configurações':
        heading('SEU WORKSPACE', 'Deixe tudo pronto para praticar.', 'Conecte seu assistente, verifique o acesso e acompanhe o estado real da integração.')
        settings, info = st.columns([1.65,1], gap='large')
        with settings:
            with st.container(border=True):
                st.markdown('#### Conexão com a inteligência artificial')
                st.caption('Escolha o motor e o modelo em “Assistente IA”, na barra lateral. Ollama usa o modelo instalado neste computador; Gemini, OpenAI, DeepSeek e Qwen por API precisam de chave.')
                st.write('**Status:** ' + connection_label)
                from core.model_recommendations import render_model_recommendations
                render_model_recommendations(provider)
                if provider=='Ollama' and not connection:
                    st.info('Llama local selecionado. Inicie scripts/start_local_ai.sh e use Testar conexão para confirmar a geração real. Nenhuma chave é necessária. O teste de conexão não avalia a correção das explicações.')
                elif not llm.enabled:
                    st.info('Preencha a chave e o modelo na barra lateral. A chave ainda não foi enviada nem verificada.')
                elif connection:
                    (st.success if connection.get('status', 'verified') == 'verified' and connection['ok'] else st.warning)(connection['message'])
                    if connection.get('last_success_at'):
                        st.caption('Última resposta recebida: ' + connection['last_success_at'])
                    st.caption('O status descreve a última operação; não há conexão permanente nem prazo de expiração configurado pelo sistema.')
                else:
                    st.info('Sua chave está configurada. Teste a conexão para confirmar se o modelo responde.')
                buttons = st.columns(2)
                if buttons[0].button('Testar conexão', type='primary', disabled=not llm.enabled, use_container_width=True):
                    with st.spinner('Verificando o Gemini com uma mensagem curta (15 s de espera)…' if provider=='Gemini' else 'Enviando uma mensagem curta ao modelo…', show_time=True):
                        ok = llm.test_connection()
                    capture_ai('Testar conexão')
                    st.rerun()
                if buttons[1].button('Buscar modelos disponíveis', disabled=provider!='Ollama' and not api_key.strip(), use_container_width=True):
                    with st.spinner('Consultando os modelos disponíveis…'):
                        available = llm.list_models()
                    capture_ai('Listar modelos')
                    st.session_state.available_models[fingerprint] = available
                    st.rerun()
                available = st.session_state.available_models.get(fingerprint, [])
                if available:
                    candidate = st.selectbox('Modelos retornados pela API', available, key='available_' + fingerprint)
                    st.caption('A listagem confirma a consulta ao catálogo. O teste de conexão confirma a geração de texto.')
                    if st.button('Usar modelo selecionado'):
                        st.session_state.pending_model = (provider,candidate)
                        st.rerun()
            with st.expander('Diagnóstico das últimas operações', expanded=bool(connection and not connection['ok'])):
                events = st.session_state.ai_events
                if not events:
                    st.caption('Nenhuma chamada de IA foi realizada nesta sessão.')
                for event in reversed(events[-8:]):
                    st.markdown(f'**{event["operation"]}** · {event["provider"]} · {event["time"]}')
                    st.write(event['message'])
                    if event.get('code'):
                        st.caption('Código HTTP: ' + str(event['code']))
                    if event.get('detail'):
                        st.code(event['detail'], language='text')
            with st.container(border=True):
                st.markdown('#### Seu banco local e histórico')
                counts = store.counts(profile_id)
                st.write(f'Perfil **{profile_id[:8]}** · {counts["artifacts"]} registros de atividades e conteúdos · {counts["model_calls"]} chamadas de IA registradas.')
                st.caption('Seu progresso pertence a esta conta e fica salvo no banco local. Entre novamente para retomar de qualquer sessão neste app.')
                st.caption('Antes de cada geração, a IA recebe um resumo limitado das respostas, dificuldades, submissões recentes e trechos de materiais relacionados. Isso fornece contexto; não altera os pesos do modelo.')
                st.download_button('Exportar dados do perfil',json.dumps(store.export_profile(profile_id),ensure_ascii=False,indent=2),'perfil-'+profile_id[:8]+'.json','application/json',key='export_profile')
                from core.learner_memory import LearnerMemory
                memory=LearnerMemory(store)
                memory_export=memory.export(profile_id)
                st.markdown('##### Memória de estudo e handoff')
                st.caption('A memória registra atividades e interações sanitizadas, consolida páginas Markdown locais e recupera somente um resumo limitado na próxima geração. Ela não presume domínio a partir de uma leitura.')
                st.write(f'{len(memory_export["events"])} observações · {len(memory_export["pages"])} páginas Markdown · sem chamadas extras à IA')
                memory_columns=st.columns(2)
                memory_columns[0].download_button('Exportar memória (.json)',json.dumps(memory_export,ensure_ascii=False,indent=2),'memoria-'+profile_id[:8]+'.json','application/json',key='export_memory_json',use_container_width=True)
                memory_columns[1].download_button('Baixar handoff (.md)',memory.markdown_bundle(profile_id),'handoff-estudos-'+profile_id[:8]+'.md','text/markdown',key='export_memory_markdown',use_container_width=True)
                with st.expander('Onde os dados ficam guardados'):
                    st.code(str(store.path),language='text')
                    st.caption('Tabelas: profiles, artifacts, model_calls e índice de memória. As páginas Markdown ficam na pasta memory ao lado do banco. As chaves de API não são persistidas.')
            with st.expander('Ambiente de avaliação e dados da sessão'):
                st.write('O juiz executa C++ localmente com timeout e limites de recursos em POSIX. Os programas mantêm as permissões do usuário: este protótipo deve rodar em ambiente local confiável. Para submissões públicas, utilize contêiner ou VM isolada.')
                st.caption('As contas têm senha protegida por hash e sessões com expiração. Cada aluno acessa o próprio perfil; professores acompanham apenas suas turmas. A execução de C++ continua destinada a um ambiente local confiável.')
        with info:
            with st.container(border=True):
                st.markdown('#### O que cada modo oferece')
                st.markdown('**Llama / Ollama**  \nModelo de linguagem executado neste computador. Usa os mesmos recursos de histórico, tutoria e busca assistida, sem chave externa.')
                st.markdown('**Gemini, OpenAI, DeepSeek ou Qwen por API**  \nExplicações contextualizadas, geração de materiais e reformulação de desafios com validação.')
                st.caption('Se o modelo falhar, a operação mostra o motivo e permite tentar novamente. Não gera respostas por regras ou modelos de texto.')
            html('<div class="tip-card"><h3>Está configurado, mas não respondeu?</h3><p>Teste a conexão primeiro. Um erro de cota pede verificar os limites da conta; um modelo indisponível pede consultar o catálogo. São situações diferentes e agora aparecem separadamente.</p></div>')

    # Persist successful model events from learning/classroom views as well.
    if llm.events:capture_ai('Análise e tutoria')
    save_progress()

except AIUnavailable as exc:
    if 'capture_ai' in globals():capture_ai('Operação de IA interrompida')
    st.error(str(exc))
    st.caption('Nenhuma orientação automática por regras foi usada. Confira o motor em Configurações e tente novamente. Seus resultados já registrados continuam salvos.')
    save_progress()
