"""Dedicated, owner-scoped reading pages for AI-generated studies."""
import json
import math
import re
from html import escape
import streamlit as st
from core.library import Library,study_entry
from core.ui import heading,html,empty,badge


def material(store, profile_id, material_id):
    store.validate_id(profile_id)
    if not isinstance(material_id,str) or not re.fullmatch(r'[a-f0-9]{32}',material_id):return None
    with store.connect() as db:
        row=db.execute("SELECT id,kind,title,payload,created_at FROM artifacts WHERE id=? AND profile_id=? AND kind='material'",(material_id,profile_id)).fetchone()
    return dict(id=row[0],kind=row[1],title=row[2],payload=json.loads(row[3]),time=row[4]) if row else None


def sections(content):
    result=[];lines=[];title='Introdução';fence=None
    for line in content.splitlines():
        marker=re.match(r'^\s*(`{3,}|~{3,})',line)
        if marker:
            char=marker[1][0]
            if fence==char:fence=None
            elif fence is None:fence=char
        match=re.match(r'^#{1,3}\s+(.+?)\s*#*$',line) if fence is None else None
        if match:
            if lines:result.append((title,'\n'.join(lines).strip()))
            title=match[1];lines=[line]
        else:lines.append(line)
    if lines:result.append((title,'\n'.join(lines).strip()))
    return [(t,b) for t,b in result if b]


def open_study(material_id,go):
    st.session_state.selected_material_id=material_id
    st.query_params['estudo']=material_id
    st.session_state.study_url_loaded=material_id
    go('Meus estudos')


def study_cards(store,profile_id,go,limit=12,key='studies'):
    items=store.artifacts(profile_id,kind='material',limit=100)
    if limit>3:
        search=st.text_input('Buscar meus estudos',placeholder='Assunto, título ou objetivo…',key=key+'_search')
        items=[i for i in items if search.casefold() in (i['title']+' '+i['payload'].get('learning_request','')).casefold()]
    if not items:
        empty('Seu próximo estudo começa com uma pergunta','Crie uma explicação no Laboratório IA. Ela ficará salva aqui para continuar depois.')
        if st.button('Criar meu primeiro estudo →',key=key+'_create',type='primary'):go('Laboratório IA')
        return
    for item in items[:limit]:
        payload=item['payload'];text=payload.get('content','');minutes=max(1,math.ceil(len(text.split())/200))
        with st.container(border=True):
            st.caption(payload.get('concept','Estudo')+' · '+str(minutes)+' min de leitura · '+Library(store).get_state(profile_id,item['id'])['status'])
            st.markdown('### '+item['title'])
            st.write((payload.get('learning_request') or 'Explicação com conceitos, exemplos e referências.')[:240])
            if st.button('Abrir estudo →',key=key+'_'+item['id'],use_container_width=True):open_study(item['id'],go)


def render_studies(store,profile_id,go,problems):
    selected=st.session_state.get('selected_material_id')
    if not selected:
        heading('SUA BIBLIOTECA PESSOAL','Meus estudos','Retome suas leituras. Cada conteúdo tem uma página própria e permanece salvo na sua conta.')
        if st.button('Novo estudo com IA →',type='primary',key='studies_new'):go('Laboratório IA')
        study_cards(store,profile_id,go)
        return
    item=material(store,profile_id,selected)
    if not item:
        st.warning('Este estudo não foi encontrado nesta conta.')
        if st.button('Voltar aos meus estudos',key='study_missing_back'):
            st.session_state.pop('selected_material_id',None);st.query_params.pop('estudo',None);st.rerun()
        return
    from core.practice_context import study_context,queue_practice
    practice=study_context(item)
    st.session_state.last_practice_context=practice
    entry=study_entry(item);library=Library(store);state=library.get_state(profile_id,selected)
    top=st.columns([2,1,1])
    if top[0].button('← Meus estudos',key='study_back'):
        st.session_state.pop('selected_material_id',None);st.query_params.pop('estudo',None);st.rerun()
    top[1].download_button('Baixar estudo',entry['content'],selected+'.md','text/markdown',use_container_width=True)
    if top[2].button('Criar outro estudo',key='study_new',use_container_width=True):go('Laboratório IA')
    heading('CADERNO DE PROGRAMAÇÃO COMPETITIVA',entry['title'],entry['learning_request'])
    count=len(entry['content']);minutes=max(1,math.ceil(len(entry['content'].split())/200))
    html('<div class="study-meta">'+badge(entry['topic'],'indigo')+badge(str(minutes)+' min de leitura')+badge(f'{count:,} caracteres'.replace(',','.'))+badge(state['status'],'accepted' if state['status']=='Estudado' else 'neutral')+'</div>')
    st.caption('Gerado por '+entry['source']+' · salvo em '+entry['time']+' · revise as conclusões da IA.')
    if item['payload'].get('validation',{}).get('pedagogical_review')=='pending_human_review':
        st.warning('Somente o resultado do exemplo foi conferido automaticamente. A explicação, os índices, a complexidade e as fontes ainda precisam de revisão pedagógica.')
    chunks=sections(entry['content'])
    if not chunks:
        chunks=[(entry['title'] or 'Introdução',entry['content'])]

    view_mode=st.radio(
        'Modo de visualização',
        ['📖 Artigo contínuo', '🖥️ Apresentação em Slides'],
        horizontal=True,
        key='study_view_mode_'+selected,
        help='Alterne entre o formato clássico de leitura completa ou slides focados passo a passo.'
    )

    if view_mode=='📖 Artigo contínuo':
        toc,article=st.columns([1,3],gap='large')
        with toc:
            st.markdown('#### Nesta página')
            html('<nav class="study-toc" aria-label="Sumário do estudo">'+''.join('<a href="#study-section-'+str(i)+'">'+escape(t)+'</a>' for i,(t,_) in enumerate(chunks))+'</nav>')
            st.divider()
            if st.button('✓ Marcar como estudado' if state['status']!='Estudado' else 'Retomar estudo',key='study_done',use_container_width=True):
                library.set_state(profile_id,selected,'Estudado' if state['status']!='Estudado' else 'Estudando',state['note']);st.rerun()
            if st.button('Criar problema deste estudo →',key='study_practice',use_container_width=True):
                queue_practice(st.session_state,practice,go)
            st.caption('Você pode reabrir esta página pelo endereço atual. O acesso pertence à sua conta.')
        with article:
            with st.container(key='study_article'):
                for i,(_,body) in enumerate(chunks):
                    html('<span id="study-section-'+str(i)+'" class="study-anchor"></span>')
                    st.markdown(body)
            st.divider();st.markdown('### Minhas anotações')
            with st.form('study_notes_'+selected):
                note=st.text_area('O que entendi e o que preciso revisar',value=state['note'],max_chars=4000,height=150)
                if st.form_submit_button('Salvar anotações'):
                    library.set_state(profile_id,selected,state['status'],note);st.success('Anotações salvas.')
    else:
        total_slides=len(chunks)
        slide_key='study_slide_idx_'+selected
        if slide_key not in st.session_state:
            st.session_state[slide_key]=0
        current_idx=max(0,min(st.session_state[slide_key],total_slides-1))

        nav_col1,nav_col2,nav_col3=st.columns([1,2,1])
        with nav_col1:
            if st.button('← Slide anterior',disabled=(current_idx==0),key='study_slide_prev_'+selected,use_container_width=True):
                st.session_state[slide_key]=current_idx-1
                st.rerun()
        with nav_col2:
            slide_labels=[f'{i+1}/{total_slides}: {t[:42]}' for i,(t,_) in enumerate(chunks)]
            selected_idx=st.selectbox(
                'Slide atual',
                range(total_slides),
                format_func=lambda i:slide_labels[i],
                index=current_idx,
                key='study_slide_picker_'+selected,
                label_visibility='collapsed'
            )
            if selected_idx!=current_idx:
                st.session_state[slide_key]=selected_idx
                st.rerun()
        with nav_col3:
            if st.button('Próximo slide →',disabled=(current_idx>=total_slides-1),key='study_slide_next_'+selected,use_container_width=True):
                st.session_state[slide_key]=current_idx+1
                st.rerun()

        st.progress((current_idx+1)/total_slides)

        curr_title,curr_body=chunks[current_idx]
        with st.container(border=True):
            st.caption(f'{entry["topic"].upper()} · Slide {current_idx+1} de {total_slides}')
            st.markdown(f'## {curr_title}')
            st.markdown(curr_body)

        act_col1,act_col2=st.columns(2)
        with act_col1:
            if st.button('✓ Marcar como estudado' if state['status']!='Estudado' else 'Retomar estudo',key='study_done_slide',use_container_width=True):
                library.set_state(profile_id,selected,'Estudado' if state['status']!='Estudado' else 'Estudando',state['note']);st.rerun()
        with act_col2:
            if st.button('Criar problema deste estudo →',key='study_practice_slide',use_container_width=True):
                queue_practice(st.session_state,practice,go)

        st.divider();st.markdown('### Minhas anotações')
        with st.form('study_notes_slide_'+selected):
            note=st.text_area('O que entendi e o que preciso revisar',value=state['note'],max_chars=4000,height=150)
            if st.form_submit_button('Salvar anotações'):
                library.set_state(profile_id,selected,state['status'],note);st.success('Anotações salvas.')
