"""Explicit, class-scoped Gemini assessment requests and teacher decisions."""
import streamlit as st
from core.accounts import AccessError
from core.learner_assessment import LearnerAssessmentService
from core.research.provider import ResearchConfig, ResearchError

STATUS={'pending':'Aguardando revisão do professor','approved':'Aprovada pelo professor',
        'revision_requested':'Professor solicitou revisão','rejected':'Rejeitada pelo professor'}
METRIC={'answered':'Questões respondidas','correct':'Acertos','distinct_problems':'Problemas distintos',
        'accepted_problems':'Último resultado aceito','submissions':'Submissões','compile_errors':'Erros de compilação'}


def render_class_assessments(store,accounts,user,classrooms,class_id,student_id,*,key='assessment'):
    service=LearnerAssessmentService(store,accounts,classrooms)
    st.markdown('### Avaliação de aprendizagem com Gemini')
    st.caption('A IA propõe próximos passos. O professor confere as evidências, registra um parecer e pode aprovar, pedir revisão ou rejeitar. A proposta não substitui nota ou avaliação docente.')
    try:
        snapshot=service.evidence(user['id'],class_id,student_id)
        records=service.list_for(user['id'],class_id,student_id)
        config=ResearchConfig.from_env()
    except (AccessError,ValueError) as exc:
        st.error(str(exc));return
    if not snapshot['sufficient_evidence']:
        st.info('Ainda há pouca evidência distinta. A análise deve permanecer inconclusiva; leituras e tentativas repetidas não comprovam domínio.')
    with st.expander('Conferir estatísticas enviadas à IA'):
        st.dataframe([{'Assunto':t['topic_id'],**{METRIC[m]:t[m] for m in METRIC}} for t in snapshot['topics']],hide_index=True,use_container_width=True)
        st.caption('Somente contagens e códigos de assuntos são enviados. Nome, usuário, turma, conversas, código e dados de login ficam neste computador.')
    enabled=config.provider=='Gemini' and bool(config.api_key) and config.enabled
    st.caption('Gemini 3.1 Flash-Lite · cota gratuita do provedor · sem teto diário local e sem alternativa paga. Reabrir uma análise atualizada reutiliza o resultado salvo.')
    if not enabled:st.info('Configure a chave Gemini no arquivo local .env para solicitar uma avaliação.')
    if st.button('Solicitar avaliação com Gemini',key=key+'_generate',disabled=not enabled,type='primary'):
        try:
            with st.spinner('Analisando as estatísticas e conferindo as citações…'):
                result=service.generate(user['id'],class_id,student_id,allow_real_data=True)
            st.success('Avaliação salva para revisão.' if not result.get('cached') else 'Avaliação atualizada recuperada, sem nova chamada à API.')
            records=service.list_for(user['id'],class_id,student_id)
        except (ResearchError,AccessError,ValueError) as exc:st.error(str(exc))
    if not records:
        st.caption('Nenhuma avaliação compartilhada nesta turma.');return
    for index,record in enumerate(records[:10]):
        proposal=record['assessment'];rid=record['id'];stale=record['stale']
        with st.expander(STATUS[record['status']]+' · '+record['created_at'],expanded=index==0):
            if stale:st.warning('As atividades mudaram desde esta análise. Gere uma nova avaliação antes de aprovar.')
            st.markdown('**Hipótese de nível:** '+proposal['level']+' · Confiança declarada: '+proposal['confidence'])
            st.write(proposal['summary'])
            by_id={t['evidence_id']:t for t in record['snapshot']['topics']}
            st.markdown('**Evidências citadas e verificadas**')
            for observation in proposal['observations']:
                topic=by_id[observation['evidence_id']]['topic_id']
                st.write(f"{topic} · {METRIC[observation['metric']]}: {observation['value']}")
                st.caption(observation['interpretation'])
            st.markdown('**Próximos passos propostos**')
            for action in proposal['next_steps']:st.write(action['topic_id']+': '+action['action'])
            st.caption('Modelo: '+record['model']+'. Contagens citadas foram conferidas automaticamente. Interpretações e recomendações ainda precisam do julgamento do professor.')
            if record['teacher_comment']:
                st.markdown('**Parecer do professor**');st.write(record['teacher_comment'])
            if user['role']=='teacher':
                with st.form(key+'_review_'+rid):
                    decision=st.selectbox('Parecer',['approved','revision_requested','rejected'],format_func=lambda d:{'approved':'Aprovar proposta','revision_requested':'Solicitar revisão','rejected':'Rejeitar proposta'}[d],key=key+'_decision_'+rid)
                    comment=st.text_area('Justificativa do professor',max_chars=2000,key=key+'_comment_'+rid)
                    submitted=st.form_submit_button('Registrar parecer')
                if submitted:
                    try:
                        service.review(user['id'],rid,decision,comment);st.rerun()
                    except (ResearchError,AccessError,ValueError) as exc:st.error(str(exc))
            if record['reviews']:
                with st.expander('Histórico dos pareceres'):
                    for review in record['reviews']:
                        st.write(STATUS[review['decision']]+' · '+review['created_at']);st.caption(review['comment'])
