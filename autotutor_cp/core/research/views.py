"""Collapsed opt-in controls. Opening this view never calls a model."""
def research_controls(store,profile_id,go):
    import streamlit as st
    from core.research.provider import ResearchConfig,BudgetLedger,configured_provider,ResearchError
    from core.research.competencies import graph
    from core.research.pipeline import ResearchPipeline,save_run
    with st.expander('Experimento de geração com recuperação de fontes'):
        config=ResearchConfig.from_env()
        if config.provider!='Gemini':
            st.caption('Configure Gemini no .env para o piloto externo.');return
        budget=BudgetLedger().report()
        st.caption(f'Gemini 3.1 Flash-Lite · somente cota gratuita · {budget["calls"]} chamadas registradas hoje. Sem teto diário local. Sem compra de créditos ou alternativa paga.')
        st.caption('Variações de contratos conhecidos, com compilação e testes isolados. Os rótulos pedagógicos ainda precisam de revisão humana.')
        show_advanced=st.checkbox('Incluir tópicos avançados',value=False,key='research_advanced')
        targets=[t for t in graph()['targets'] if show_advanced or t not in ('Segment Tree','Lazy propagation')]
        target=st.selectbox('Competência do experimento',targets,index=targets.index('Soma de prefixos'),key='research_target')
        method=st.selectbox('Contexto para geração',['bm25','competencies'],format_func=lambda x:{'bm25':'Textos relacionados ao assunto','competencies':'Textos relacionados às competências e pré-requisitos'}[x],key='research_method')
        if st.button('Gerar e verificar experimento',key='research_generate',disabled=not config.api_key or (config.max_calls is not None and budget['calls']>=config.max_calls)):
            try:
                with st.spinner('Recuperando fontes, gerando e verificando em ambiente isolado…'):
                    record,problem=ResearchPipeline(configured_provider(config)).run(target,'structured',method)
                    save_run(record,problem,'.runtime/research/interface')
                if problem:
                    st.session_state.problems.append(problem)
                    store.add_artifact(profile_id,'problem',problem['title'],problem)
                    go('Arena',problem['id'])
                else:
                    detail=record.get('error') or (record['attempts'][-1]['validation'].get('error') if record['attempts'] else 'Resposta não validada.')
                    st.error('Nenhum problema foi publicado: '+str(detail))
            except (ResearchError,ValueError) as exc:st.error(str(exc))
        st.divider()
        st.markdown('#### Estudo básico com exemplo conferido')
        from core.research.lessons import CASES,generate_lesson
        lesson_target=st.selectbox('Assunto do estudo verificado',list(CASES),key='research_lesson_target')
        request=st.text_area('O que você quer entender?',value='Explique desde a intuição, com um exemplo passo a passo e erros comuns.',max_chars=2500,key='research_lesson_request')
        st.caption('O cálculo do exemplo é conferido por software. A teoria, a justificativa e a qualidade didática continuam sujeitas à revisão do professor.')
        if st.button('Gerar estudo e conferir exemplo',key='research_lesson_generate',disabled=not config.api_key or not request.strip()):
            try:
                with st.spinner('Gerando o estudo e conferindo o exemplo…'):
                    lesson=generate_lesson(configured_provider(config),lesson_target,request)
                identifier=store.add_artifact(profile_id,'material',lesson['title'],lesson)
                st.session_state.selected_material_id=identifier
                go('Meus estudos')
            except (ResearchError,ValueError) as exc:st.error(str(exc))
