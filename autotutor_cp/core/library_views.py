"""Quiet, searchable views for guides, web references and all saved learning artifacts."""
import math
import streamlit as st
from core.library import Library, resources, deep_guides, references_for, study_entry, KINDS, STATUSES
from core.learning_engine import load_curriculum
from core.ui import empty


def notes(library,profile_id,item_id):
    current=library.get_state(profile_id,item_id)
    with st.expander('Meu estudo e anotações'):
        with st.form('library_notes_'+item_id):
            status=st.selectbox('Meu andamento',STATUSES,index=STATUSES.index(current['status']),key='study_status_'+item_id)
            note=st.text_area('Minhas anotações',value=current['note'],max_chars=4000,key='study_note_'+item_id)
            submitted=st.form_submit_button('Salvar meu estudo')
        if submitted:
            library.set_state(profile_id,item_id,status,note);st.success('Andamento e anotações salvos.')


def reference_card(resource,library,profile_id,key,save_button=True):
    st.caption(resource.get('publisher','Referência')+' · '+resource.get('language','Idioma não informado'))
    if resource.get('summary'):st.write(resource['summary'])
    st.link_button('Abrir referência ↗',resource['url'])
    if resource.get('source_url') and resource['source_url']!=resource['url']:st.markdown('[Origem da recomendação]('+resource['source_url']+')')
    st.caption(resource.get('verification','Link não verificado')+(' · '+resource['checked'] if resource.get('checked') else ''))
    if resource.get('kind')=='Vídeo' and st.toggle('Assistir aqui',key='embed_ref_'+key):st.video(resource['url'])
    if save_button and st.button('Salvar na minha coleção',key='save_ref_'+key):
        library.save_resource(profile_id,resource);st.success('Referência salva na sua coleção.')


def render_guides(library,profile_id,go,problems):
    guides={g['id']:g for g in deep_guides()}
    gid=st.selectbox('Guia de aprofundamento',list(guides),format_func=lambda x:guides[x]['title'],key='deep_guide_picker')
    guide=guides[gid];topic=next(t for t in load_curriculum() if t['id']==guide['topic_id'])
    st.caption(guide['author']+' · cerca de '+str(guide['minutes'])+' min · pré-requisitos: '+guide['prerequisites'])
    st.markdown('## '+guide['title'])
    for section in guide['sections']:
        st.markdown('### '+section['title']);st.write(section['body'])
    from core.learning_views import diagram
    with st.expander('Rever a ilustração do assunto'):st.markdown(diagram(guide['topic_id']),unsafe_allow_html=True)
    st.markdown('### Pratique a explicação')
    for i,exercise in enumerate(guide['exercises'],1):
        st.write(f'**{i}.** '+exercise['prompt'])
        with st.expander('Conferir raciocínio · '+str(i)):st.write(exercise['answer'])
    st.markdown('### Para continuar estudando')
    st.caption('Leituras complementares consultadas na curadoria. O guia acima é um texto autoral; as fontes mantêm seus próprios autores e versões.')
    for r in references_for(topic['title'],4):
        with st.expander(r['title']):reference_card(r,library,profile_id,gid+r['id'])
    local=[p for p in problems if not p.get('external') and p['topic']==topic['title']]
    if local:
        pid=st.selectbox('Prática com correção no AutoTutor',[p['id'] for p in local],format_func=lambda x:next(p['title'] for p in local if p['id']==x),key='deep_practice_'+gid)
        if st.button('Abrir na arena →',key='deep_solve_'+gid):go('Arena',pid)
    text='# '+guide['title']+'\n\n'+'\n\n'.join('## '+s['title']+'\n'+s['body'] for s in guide['sections'])
    text+='\n\n## Exercícios comentados\n'+'\n\n'.join(e['prompt']+'\n\n'+e['answer'] for e in guide['exercises'])
    text+='\n\n## Referências complementares\n'+'\n'.join('- ['+r['title']+']('+r['url']+')' for r in references_for(topic['title']))
    st.download_button('Baixar guia para estudar offline',text,gid+'.md','text/markdown')
    notes(library,profile_id,gid)


def render_references(library,profile_id):
    topics={t['id']:t['title'] for t in load_curriculum()}
    cols=st.columns([2,1,1]);search=cols[0].text_input('Buscar referência',key='reference_search',placeholder='Vídeo, autor ou conceito…')
    topic=cols[1].selectbox('Assunto da referência',['all']+list(topics),format_func=lambda x:'Todos' if x=='all' else topics[x],key='reference_topic')
    kind=cols[2].selectbox('Formato',['Todos','Artigo','Vídeo','Curso','Canal','Site'],key='reference_kind')
    filtered=[r for r in resources() if (not search or search.casefold() in (r['title']+' '+r['publisher']+' '+r['summary']).casefold()) and (topic=='all' or topic in r['topics'] or not r['topics']) and (kind=='Todos' or kind==r['kind'])]
    st.caption(f'{len(filtered)} referências · resumos e links salvos localmente; reprodução e páginas externas precisam de internet.')
    pages=max(1,math.ceil(len(filtered)/10))
    if st.session_state.get('reference_page',1)>pages:st.session_state.reference_page=1
    page=st.selectbox('Página de referências',list(range(1,pages+1)),key='reference_page')
    for r in filtered[(page-1)*10:page*10]:
        with st.expander(r['title']+' · '+r['kind']):
            reference_card(r,library,profile_id,r['id']);notes(library,profile_id,r['id'])
    if not filtered:empty('Nenhuma referência encontrada','Tente outro assunto ou formato.')
    with st.expander('Guardar um link que encontrei'):
        with st.form('save_own_reference'):
            title=st.text_input('Título da referência',max_chars=200)
            url=st.text_input('Endereço HTTPS',max_chars=2000)
            summary=st.text_area('Por que quero estudar',max_chars=2000)
            submitted=st.form_submit_button('Guardar na minha coleção')
        if submitted:
            try:library.save_resource(profile_id,dict(title=title,url=url,summary=summary));st.success('Link guardado. Ele aparecerá em Minha coleção como referência não verificada.')
            except ValueError as exc:st.warning(str(exc))


def render_collection(library,profile_id,go,problems):
    st.caption('Materiais, explicações de código, diagnósticos, exercícios gerados e recomendações são arquivados automaticamente nesta conta. Referências podem ser guardadas com um clique.')
    cols=st.columns([2,1,1]);search=cols[0].text_input('Buscar na minha coleção',key='collection_search',placeholder='Título, assunto ou trecho…')
    kind=cols[1].selectbox('Tipo de conteúdo',['all']+list(KINDS),format_func=lambda x:'Todos' if x=='all' else KINDS[x],key='collection_kind')
    status=cols[2].selectbox('Andamento',['Todos']+STATUSES,key='collection_status')
    args=dict(search=search,kind=None if kind=='all' else kind,status=None if status=='Todos' else status)
    result=library.page(profile_id,**args);pages=max(1,math.ceil(result['total']/12))
    if st.session_state.get('collection_page',1)>pages:st.session_state.collection_page=1
    page=st.selectbox('Página da coleção',list(range(1,pages+1)),key='collection_page')
    if page!=1:result=library.page(profile_id,page=page,**args)
    st.caption(f'{result["total"]} itens salvos · página {page}/{pages}. Conteúdo gerado por IA pode conter erros; links fora da curadoria são indicados como não verificados.')
    available={p['id'] for p in problems}
    if not result['items']:
        empty('Sua coleção está pronta para receber conteúdos','Gere um material no Laboratório IA ou salve uma referência. Os conteúdos anteriores desta conta também aparecem aqui.')
        if st.button('Criar material de estudo →',key='collection_generate'):go('Laboratório IA')
    for index,item in enumerate(result['items']):
        entry=study_entry(item)
        if item['kind']=='material':
            with st.container(border=True):
                st.markdown('### '+entry['title']);st.caption(entry['time']+' · '+item['status'])
                st.write(entry['learning_request'] or entry['topic'])
                if st.button('Abrir página de estudo →',key='collection_open_'+entry['id']):
                    from core.study_pages import open_study
                    open_study(entry['id'],go)
            continue
        with st.expander(entry['title']+' · '+entry['kind'],expanded=index==0):
            st.caption(entry['time']+' · origem: '+entry['source']+' · '+item['status'])
            if entry['learning_request']:st.write('**Seu objetivo:** '+entry['learning_request'])
            prefs=entry['preferences']
            if prefs:st.caption('Preferências: '+prefs.get('length','')+' · '+prefs.get('depth','')+' · '+('com exemplos' if prefs.get('include_examples') else 'sem exemplos')+' · '+('com exercícios' if prefs.get('include_exercises') else 'sem exercícios'))
            st.markdown(entry['content'])
            if entry['problem_id'] in available:
                if st.button('Voltar ao problema →',key='collection_problem_'+entry['id']):go('Arena',entry['problem_id'])
            for rec in entry['recommendations']:
                if rec.get('id') in available and st.button('Praticar: '+rec['title'],key='collection_rec_'+entry['id']+rec['id']):go('Arena',rec['id'])
            if entry['links']:
                with st.expander('Referências para este conteúdo'):
                    for r in entry['links']:
                        st.markdown('**'+r['title']+'**')
                        reference_card(r,library,profile_id,entry['id']+str(r.get('id',r['url'])))
            st.download_button('Baixar conteúdo',entry['content'],entry['id']+'.md','text/markdown',key='download_collection_'+entry['id'])
            notes(library,profile_id,entry['id'])


def library_section(store,profile_id,go,problems):
    section=st.radio('Explorar biblioteca',['Aulas','Acervo RAG','Guias de aprofundamento','Referências','Minha coleção'],horizontal=True,key='library_section')
    library=Library(store)
    if section=='Aulas':return False
    if section=='Acervo RAG':
        from core.knowledge_views import render_knowledge
        render_knowledge(store,profile_id,go)
    elif section=='Guias de aprofundamento':render_guides(library,profile_id,go,problems)
    elif section=='Referências':render_references(library,profile_id)
    else:render_collection(library,profile_id,go,problems)
    return True
