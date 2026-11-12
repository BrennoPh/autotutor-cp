"""Authentication and classroom screens, scoped to the authenticated account."""
import json
import streamlit as st
from core.accounts import Accounts, AccessError
from core.classrooms import Classrooms
from core.catalog import catalog_map
from core.team_builder import STRATEGIES
from core.ai_coach import analyze_class,propose_teams,evidence_key,compact_roster
from core.ui import heading, empty


def require_login(store):
    accounts=Accounts(store)
    user=accounts.current(st.session_state.get('auth_token'))
    if user:return accounts,user
    left,center,right=st.columns([1,1.5,1])
    with center:
        st.markdown('## AutoTutor')
        st.caption('Estude, pratique e acompanhe sua evolução.')
        login,register=st.tabs(['Entrar','Criar conta'])
        with login:
            with st.form('login_form'):
                username=st.text_input('Usuário',key='login_username',max_chars=40)
                password=st.text_input('Senha',type='password',key='login_password',max_chars=128)
                submitted=st.form_submit_button('Entrar',type='primary',use_container_width=True)
            if submitted:
                try:
                    token=accounts.login(username,password)
                    st.session_state.clear();st.session_state.auth_token=token;st.rerun()
                except ValueError as exc:st.error(str(exc))
        with register:
            with st.form('register_form'):
                name=st.text_input('Seu nome',max_chars=80,key='register_name')
                username=st.text_input('Nome de usuário',max_chars=40,key='register_username')
                role=st.selectbox('Tipo de conta',['Aluno','Professor'],key='register_role')
                password=st.text_input('Crie uma senha',type='password',max_chars=128,key='register_password')
                confirm=st.text_input('Repita a senha',type='password',max_chars=128,key='register_confirm')
                first=accounts.count()==0
                legacy=st.checkbox('Vincular o progresso local anterior a esta primeira conta',value=True,key='claim_legacy') if first and store.latest_profile_id() else False
                submitted=st.form_submit_button('Criar minha conta',type='primary',use_container_width=True)
            if submitted:
                try:
                    if password!=confirm:raise ValueError('As senhas não coincidem.')
                    accounts.register(username,name,password,'teacher' if role=='Professor' else 'student',legacy)
                    token=accounts.login(username,password)
                    st.session_state.clear();st.session_state.auth_token=token;st.rerun()
                except (ValueError,AccessError) as exc:st.error(str(exc))
        st.caption('Contas guardadas neste computador. Ao recarregar o navegador, entre novamente. A senha é armazenada como hash, nunca em texto puro.')
    st.stop()


def classroom_page(store,accounts,user,go,llm):
    service=Classrooms(store,accounts)
    heading('TURMAS','Aprender em equipe.', 'Crie uma turma ou acompanhe as atividades da sua sala.')
    teacher=user['role']=='teacher'
    with st.expander('Criar turma' if teacher else 'Entrar em uma turma'):
        if teacher:
            with st.form('create_class'):
                name=st.text_input('Nome da turma',max_chars=100)
                description=st.text_area('Descrição',max_chars=1000,height=80)
                submitted=st.form_submit_button('Criar turma',type='primary')
            if submitted:
                try:
                    st.session_state.selected_class=service.create(user['id'],name,description)
                    st.rerun()
                except (ValueError,AccessError) as exc:st.error(str(exc))
        else:
            with st.form('join_class'):
                code=st.text_input('Código da turma',max_chars=20)
                st.caption('Ao entrar, você compartilha com o professor seu resumo de desempenho, questões respondidas e conclusões de exercícios. Conversas privadas com a IA não aparecem no painel da turma.')
                submitted=st.form_submit_button('Entrar na turma',type='primary')
            if submitted:
                try:
                    st.session_state.selected_class=service.join(user['id'],code);st.rerun()
                except (ValueError,AccessError) as exc:st.error(str(exc))
    classes=service.list_for(user['id'])
    if not classes:
        empty('Nenhuma turma ainda','Crie sua primeira turma.' if teacher else 'Peça ao professor o código da turma.')
        return
    mapping={c['id']:c for c in classes}
    selected=st.session_state.get('selected_class')
    if selected not in mapping:selected=classes[0]['id']
    class_id=st.selectbox('Turma',list(mapping),index=list(mapping).index(selected),format_func=lambda x:mapping[x]['name'],key='class_picker')
    st.session_state.selected_class=class_id
    classroom=mapping[class_id]
    if classroom['description']:st.caption(classroom['description'])
    problems=catalog_map()
    if teacher:
        with st.expander('Código para os alunos entrarem'):
            st.code(classroom['invite_code'],language='text')
        panel,assignments,teams,assessments=st.tabs(['Acompanhamento','Listas de prática','Formar trios','Avaliações individuais'])
        roster=service.roster(user['id'],class_id)
        with assessments:
            if not roster:
                st.info('Entre com alunos na turma para acompanhar avaliações individuais.')
            else:
                chosen=st.selectbox('Aluno para avaliação',[m['id'] for m in roster],format_func=lambda uid:next(m['name'] for m in roster if m['id']==uid),key='assessment_student')
                from core.assessment_views import render_class_assessments
                render_class_assessments(store,accounts,user,service,class_id,chosen,key='teacher_assessment')
        with panel:
            if not roster:
                empty('Aguardando os alunos','Compartilhe o código da turma por um canal de sua escolha.')
            else:
                cols=st.columns(3)
                cols[0].metric('Alunos',len(roster))
                cols[1].metric('Problemas locais aceitos',sum(len(m['local_solved']) for m in roster))
                cols[2].metric('Conclusões externas declaradas',sum(len(m['external_solved']) for m in roster))
                rows=[{'Aluno':m['name'],'Usuário':m['username'],'Nível':m['level'],'Origem do nível':m['level_source'],
                       'AC local':len(m['local_solved']),'Externos declarados':len(m['external_solved']),
                       'Externos confirmados':len(m['verified_external']),
                       'Questões':m['quiz_answered'],'Acertos':m['quiz_correct'],'Tentativas C++':m['submissions']} for m in roster]
                st.dataframe(rows,hide_index=True,use_container_width=True)
                st.download_button('Exportar resumo da turma',json.dumps(rows,ensure_ascii=False,indent=2),'turma.json','application/json')
                class_key=evidence_key({'class_id':class_id,'roster':compact_roster(roster)})
                if st.button('Analisar turma com IA',key='class_ai'):
                    with st.spinner('A IA está analisando a turma…'):
                        content=analyze_class(llm,roster)
                        store.add_artifact(user['profile_id'],'class_analysis','Análise da turma · '+classroom['name'],
                            dict(content=content,class_id=class_id,evidence_key=class_key,source=llm.provider+' · '+llm.model,model=llm.model))
                analyses=store.artifacts(user['profile_id'],kind='class_analysis',limit=100)
                current=next((a for a in analyses if a['payload'].get('evidence_key')==class_key and a['payload'].get('model')==llm.model),None)
                if current:st.markdown(current['payload']['content'])
                st.caption('A interpretação da turma é feita pelo modelo e salva na biblioteca privada do professor.')
                with st.expander('Ver um aluno'):
                    members={m['id']:m for m in roster}
                    uid=st.selectbox('Aluno',list(members),format_func=lambda x:members[x]['name'],key='monitor_student')
                    member=members[uid]
                    st.caption('Taxa de acerto observada por tópico, sem pesos de habilidade predefinidos.')
                    if member['skills']:
                        st.bar_chart([{'Tópico':topic,'Acerto':value} for topic,value in member['skills'].items()],x='Tópico',y='Acerto')
                    else:st.caption('Este aluno ainda não respondeu questões por assunto.')
                    pending={pid:r for pid,r in member['external'].items() if r['status']=='solved' and not r['verified'] and pid in problems and problems[pid].get('external')}
                    if pending:
                        pid=st.selectbox('Conclusão externa a revisar',list(pending),format_func=lambda x:problems[x]['title'],key='verify_problem')
                        if pending[pid]['proof_url']:st.markdown('[Abrir comprovante]('+pending[pid]['proof_url']+')')
                        st.caption('Confirme somente após conferir a conclusão no juiz de origem. Isso não produz um AC do Mini-Judge.')
                        if st.button('Confirmar conclusão como professor',key='verify_external'):
                            service.verify_external(user['id'],class_id,uid,pid);st.rerun()
        with assignments:
            with st.expander('Nova lista de prática'):
                with st.form('create_assignment'):
                    title=st.text_input('Título da lista',max_chars=120)
                    selected_problems=st.multiselect('Problemas',list(problems),format_func=lambda x:problems[x]['title']+' · '+problems[x].get('source','Local'),max_selections=100)
                    submitted=st.form_submit_button('Publicar na turma',type='primary')
                if submitted:
                    try:service.create_assignment(user['id'],class_id,title,selected_problems);st.rerun()
                    except ValueError as exc:st.error(str(exc))
            for assignment in service.assignments(user['id'],class_id):
                with st.expander(assignment['title']+f' · {len(assignment["problem_ids"])} problemas'):
                    for pid in assignment['problem_ids']:
                        p=problems.get(pid)
                        if p:st.write(p['title']+' · '+p.get('source','Local'))
                    if roster:
                        rows=[]
                        for m in roster:
                            solved=set(m['local_solved'])|set(m['external_solved'])
                            rows.append({'Aluno':m['name'],'Já concluídos':len(solved & set(assignment['problem_ids'])),'Total':len(assignment['problem_ids'])})
                        st.dataframe(rows,hide_index=True)
                        st.caption('Inclui conclusões anteriores à lista. As externas podem ser autodeclaradas.')
        with teams:
            if len(roster)<3:
                empty('São necessários pelo menos três alunos','Os alunos precisam entrar na turma para participar da formação.')
            else:
                level_filter=st.multiselect('Níveis participantes',['Iniciante','Intermediário','Avançado','Não avaliado'],default=['Iniciante','Intermediário','Avançado','Não avaliado'],key='team_levels')
                candidates=[m for m in roster if m['level'] in level_filter]
                selected_students=st.multiselect('Alunos participantes',[m['id'] for m in candidates],default=[m['id'] for m in candidates],format_func=lambda x:next(m['name'] for m in roster if m['id']==x),key='team_students')
                options=st.columns(2)
                strategy=options[0].selectbox('Estratégia',STRATEGIES,key='team_strategy')
                mode=options[1].selectbox('Objetivo',['Turma inteira','Melhor trio'],key='team_mode')
                with st.expander('Entender os critérios'):
                    st.write('A IA recebe estatísticas por assunto e a estratégia escolhida para propor e justificar os grupos. A proposta não garante um ótimo global. Para este modelo leve, selecione até 30 alunos por rodada.')
                    st.caption('O modelo recebe participantes identificados por códigos, sem conversas privadas. ACs locais, conclusões confirmadas e autodeclarações são identificados separadamente.')
                proposal_key=evidence_key(dict(class_id=class_id,roster=compact_roster([m for m in roster if m['id'] in selected_students]),participants=selected_students,strategy=strategy,mode=mode,provider=llm.provider,model=llm.model))
                if st.button('Sugerir formação',type='primary',disabled=len(selected_students)<3,key='build_teams'):
                    with st.spinner('Comparando as combinações…'):
                        try:
                            proposal=propose_teams(llm,[m for m in roster if m['id'] in selected_students],strategy,mode)
                            st.session_state.team_proposal={'class_id':class_id,'payload':proposal,'roster_ids':selected_students,'evidence_key':proposal_key}
                        except ValueError as exc:st.warning(str(exc))
                stored=st.session_state.get('team_proposal')
                if stored and stored['class_id']==class_id and stored.get('evidence_key')==proposal_key:
                    proposal=stored['payload'];names={m['id']:m['name'] for m in roster}
                    st.caption(proposal['method']+' · Confira as justificativas com as estatísticas antes de salvar.')
                    for i,team in enumerate(proposal['details'],1):
                        st.markdown(f'**Trio {i}: '+', '.join(team['names'])+'**')
                        st.caption(team['reason'])
                    if proposal['waiting']:st.info('Fora dos trios nesta proposta: '+', '.join(names.get(uid,'Aluno') for uid in proposal['waiting']))
                    st.caption(proposal['note'])
                    if st.button('Salvar formação na turma',key='save_teams'):
                        try:service.save_formation(user['id'],class_id,proposal['strategy'],proposal);st.success('Formação salva. Os alunos podem consultar o próprio trio.')
                        except (ValueError,AccessError) as exc:st.warning(str(exc))
            for formation in service.formations(user['id'],class_id):
                with st.expander('Formação salva · '+formation['strategy']+' · '+formation['time']):
                    for i,names in enumerate(formation['teams'],1):st.write(f'Trio {i}: '+', '.join(names))
                    if formation['waiting']:st.caption('Aguardando: '+', '.join(formation['waiting']))
    else:
        lists,my_teams,my_assessments=st.tabs(['Listas de prática','Meu trio','Avaliação com professor'])
        with my_assessments:
            from core.assessment_views import render_class_assessments
            render_class_assessments(store,accounts,user,service,class_id,user['id'],key='student_assessment')
        with lists:
            assignments=service.assignments(user['id'],class_id)
            if not assignments:empty('Nenhuma lista publicada','As listas do professor aparecerão aqui.')
            external=service.external_for(user['id'])
            for assignment in assignments:
                with st.expander(assignment['title'],expanded=True):
                    for pid in assignment['problem_ids']:
                        problem=problems.get(pid)
                        if not problem:continue
                        cols=st.columns([4,1]);cols[0].write(problem['title'])
                        if pid in external and external[pid]['status']=='solved':cols[0].caption('Conclusão externa registrada')
                        if cols[1].button('Abrir →',key='assignment_'+assignment['id']+'_'+pid):go('Arena',pid)
        with my_teams:
            formations=service.formations(user['id'],class_id)
            if not formations:empty('Seu trio ainda não foi definido','O professor pode montar e salvar uma formação para a turma.')
            for formation in formations:
                for names in formation['teams']:st.write('**'+', '.join(names)+'**')
                if formation['waiting']:st.caption('Você está fora dos trios nesta formação.')
                st.caption(formation['strategy']+' · '+formation['time'])
