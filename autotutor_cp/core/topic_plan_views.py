"""A quiet topic-plan builder and dated sessions with persistent completion."""
from datetime import date,datetime
from zoneinfo import ZoneInfo
import streamlit as st
from core.learning_engine import load_curriculum
from core.topic_plans import (STYLES,WEEKDAYS,KINDS,TopicPlans,preferences,generate_plan,plan_markdown)


def render_topic_plans(store,profile_id,save,go,llm,on_ai=None):
    service=TopicPlans(store);topics={t['id']:t['title'] for t in load_curriculum()}
    st.markdown('### Uma trilha para o que você quer aprender')
    st.caption('Escolha um assunto e sua rotina. A IA organiza uma primeira etapa com aulas, artigos, vídeos e problemas reais do catálogo.')
    with st.expander('Criar uma trilha por assunto',expanded=not service.list(profile_id)):
        with st.form('topic_plan_builder'):
            topic=st.text_input('O que você quer aprender?',value='Programação dinâmica (DP)',max_chars=150,key='topic_plan_topic')
            goal=st.text_area('Seu objetivo e o que você já sabe',placeholder='Ex.: Sei usar vetores e laços. Quero entender estado, transição e mochila, praticando com problemas simples.',max_chars=1200,key='topic_plan_goal')
            first,second=st.columns(2)
            base=first.selectbox('Assunto de referência',list(topics),index=list(topics).index('dp'),format_func=lambda x:topics[x],key='topic_plan_base')
            style=second.selectbox('Como você prefere aprender?',STYLES,key='topic_plan_style')
            days=st.multiselect('Dias disponíveis',list(range(7)),default=[0,2,4],format_func=lambda d:WEEKDAYS[d],key='topic_plan_days')
            left,middle,right=st.columns(3)
            minutes=left.select_slider('Minutos por dia',options=[15,30,45,60,90,120,180],value=45,key='topic_plan_minutes')
            start=middle.date_input('Começar em',value=datetime.now(ZoneInfo('America/Maceio')).date(),format='DD/MM/YYYY',key='topic_plan_start')
            weeks=right.slider('Horizonte máximo (semanas)',1,12,4,key='topic_plan_weeks')
            st.caption('A duração será estimada pela IA dentro desse limite. É um planejamento ajustável, sem garantia de domínio ao concluir os dias.')
            submitted=st.form_submit_button('Criar trilha com IA',type='primary',key='create_topic_plan')
        if submitted:
            try:
                prefs=preferences(topic,goal,base,style,minutes,days,start,weeks)
                with st.spinner('A IA está escolhendo os recursos e estimando as sessões…'):
                    plan=generate_plan(llm,prefs,st.session_state.quiz_attempts,st.session_state.history,st.session_state.completed_lessons)
                    identifier=service.save(profile_id,plan)
                if on_ai:on_ai('Criar trilha por assunto')
                st.session_state.active_topic_plan=identifier;st.toast('Trilha salva na biblioteca.')
            except ValueError as exc:st.warning(str(exc))
    plans=service.list(profile_id)
    if not plans:return
    if 'pending_topic_plan' in st.session_state:st.session_state.active_topic_plan=st.session_state.pop('pending_topic_plan')
    ids=[p['id'] for p in plans];labels={p['id']:p['title']+' · '+p['time'] for p in plans}
    if st.session_state.get('active_topic_plan') not in ids:st.session_state.active_topic_plan=ids[0]
    identifier=st.selectbox('Suas trilhas por assunto',ids,format_func=lambda i:labels[i],key='active_topic_plan')
    plan=service.get(profile_id,identifier);progress=service.progress(profile_id,identifier)
    by_id={r['id']:r for r in plan['resources']}
    total=sum(len(s['activities']) for s in plan['sessions']);done=sum(progress.values())
    remaining=sum(a['minutes'] for i,s in enumerate(plan['sessions']) for j,a in enumerate(s['activities']) if not progress.get((i,j),False))
    st.markdown('### '+plan['title']);st.write(plan['summary']);st.caption(plan['personalization'])
    st.progress(done/total,text=f'{done}/{total} atividades concluídas · cerca de {remaining} min restantes pela estimativa da IA')
    st.caption('De '+date.fromisoformat(plan['start_date']).strftime('%d/%m/%Y')+' a '+date.fromisoformat(plan['end_date']).strftime('%d/%m/%Y')+' · '+plan['source'])
    if plan.get('parent_id'):st.caption('Esta é uma adaptação com as próximas atividades. A versão anterior e seu progresso continuam salvos.')
    with st.expander('O que a estimativa considera'):st.write(plan['assumptions'])
    for i,session in enumerate(plan['sessions']):
        complete=all(progress.get((i,j),False) for j in range(len(session['activities'])))
        with st.expander(('✓ ' if complete else '')+date.fromisoformat(session['date']).strftime('%d/%m')+' · '+session['title']+f' · ~{session["minutes"]} min',expanded=not complete and i==0):
            for j,activity in enumerate(session['activities']):
                resource=by_id.get(activity['resource_id']);name=resource['title'] if resource else 'Revisão ativa'
                st.markdown('**'+KINDS[activity['kind']]+' · '+name+f' · ~{activity["minutes"]} min**')
                st.write(activity['objective'])
                if resource:
                    if resource.get('knowledge_id'):
                        if st.button('Ler no acervo',key=f'topic_plan_read_{identifier}_{i}_{j}'):
                            st.session_state.knowledge_selected=resource['knowledge_id'];st.session_state.library_section='Acervo RAG';go('Biblioteca')
                    elif resource.get('lesson_id'):
                        if st.button('Abrir aula',key=f'topic_plan_lesson_{identifier}_{i}_{j}'):
                            st.session_state.pending_lesson=resource['lesson_id'];go('Biblioteca')
                    elif resource.get('problem_id'):
                        st.caption('Correção no AutoTutor' if resource.get('judge')=='local' else 'Problema com correção no juiz de origem')
                        if st.button('Resolver problema',key=f'topic_plan_problem_{identifier}_{i}_{j}'):go('Arena',resource['problem_id'])
                    elif resource.get('url','').startswith('https://'):
                        st.link_button('Abrir vídeo' if activity['kind']=='video' else 'Abrir referência',resource['url'])
                    if resource.get('source'):st.caption(resource['source'])
                checkbox=f'topic_plan_done_{identifier}_{i}_{j}'
                def mark(si=i,ai=j,key=checkbox):service.set_completed(profile_id,identifier,si,ai,st.session_state[key])
                st.checkbox('Concluí esta atividade',value=progress.get((i,j),False),key=checkbox,on_change=mark)
    st.download_button('Baixar minha trilha',plan_markdown(plan),identifier+'.md','text/markdown',key='topic_plan_download')
    with st.expander('Adaptar a trilha ao meu progresso'):
        feedback=st.text_area('O que funcionou e onde você travou?',placeholder='Ex.: Entendi os estados, mas prefiro mais problemas pequenos antes de mochila.',max_chars=1200,key='topic_plan_feedback')
        next_style=st.selectbox('Como quer aprender na próxima etapa?',STYLES,index=STYLES.index(plan['preferences']['style']),key='adapt_topic_style_'+identifier)
        st.caption('A IA recebe as atividades concluídas e seu relato para propor outra etapa. O plano atual permanece no histórico.')
        if st.button('Replanejar próximas sessões com IA',key='adapt_topic_plan'):
            if not feedback.strip() and not any(progress.values()):st.info('Registre alguma atividade ou descreva sua experiência antes de adaptar.')
            else:
                prefs=dict(plan['preferences']);prefs['style']=next_style;prefs['start_date']=max(prefs['start_date'],datetime.now(ZoneInfo('America/Maceio')).date().isoformat())
                previous={'title':plan['title'],'completed':[a['objective'] for i,s in enumerate(plan['sessions']) for j,a in enumerate(s['activities']) if progress.get((i,j),False)]}
                with st.spinner('A IA está ajustando sua próxima etapa…'):
                    revised=generate_plan(llm,prefs,st.session_state.quiz_attempts,st.session_state.history,st.session_state.completed_lessons,previous,feedback)
                    new_id=service.save(profile_id,revised,parent_id=identifier)
                if on_ai:on_ai('Adaptar trilha por assunto')
                st.session_state.pending_topic_plan=new_id;st.rerun()
