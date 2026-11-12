"""Read/search the attributed corpus without sending a request to an AI provider."""
import streamlit as st
from core.knowledge import KnowledgeBase
from core.library import Library

TOPICS={'all':'Todos','fundamentals':'Fundamentos','adhoc':'Ad hoc e implementação','structures':'Vetores e estruturas',
        'sorting':'Ordenação','prefix':'Soma de prefixos','binary':'Busca binária e dois ponteiros',
        'graph':'Grafos · BFS e DFS','tree':'Árvores','dp':'Programação dinâmica','greedy':'Guloso','math':'Matemática','strings':'Strings','geometry':'Geometria'}


def article_markdown(article):
    result=article['content']+'\n\n---\n\n'
    result+='Fonte: '+article['source']+' · '+article.get('authors','')+'\n\n'
    if article['url'].startswith('https://'):result+='Original: '+article['url']+'\n\n'
    if article.get('source_url'):result+='Versão consultada: '+article['source_url']+'\n\n'
    result+='Licença: '+article['license']+' '+article.get('license_url','')+'\n\n'+article.get('adaptation','')
    return result


def render_knowledge(store,profile_id,go=None):
    from core.library_views import notes
    kb=KnowledgeBase();stats=kb.stats()
    st.markdown('### Uma base para começar e consultar')
    if not stats['documents']:
        st.info('O acervo ainda não foi importado nesta instalação.');return
    st.caption(f'{stats["documents"]} conteúdos · {stats["chunks"]} trechos pesquisáveis · {stats["bytes"]/1024/1024:.1f} MB no banco. Fontes, créditos e licenças ficam junto de cada texto.')
    st.caption('A busca usa o texto importado. A IA recebe os trechos encontrados quando gera materiais e recomendações; importar conteúdo não treina seus pesos.')
    from pathlib import Path
    import json
    report_path=Path(__file__).resolve().parents[1]/'data'/'study_sources_report.json'
    if report_path.exists():
        with st.expander('O que foi importado de cada fonte'):
            report=json.loads(report_path.read_text())
            for source in report['sources']:
                st.markdown('**'+source['source']+'** · '+source['status'])
                st.caption(str(source.get('reference_count',0))+' referências · '+source.get('detail',source.get('error','')))
            st.caption('Referências são links pesquisáveis. Apenas textos completos entram como evidência teórica no RAG. Aulas autorais continuam disponíveis para leitura, mas não fundamentam novos materiais de IA.')
    col1,col2=st.columns([2,1])
    query=col1.text_input('Buscar no acervo',placeholder='BFS, DFS, ad hoc, soma de prefixos…',key='knowledge_query')
    if query.strip() and go:
        from core.practice_context import queue_practice
        context=dict(request=query.strip(),concept='',level=st.session_state.get('level','Iniciante'),theme='',source_title='Busca: '+query.strip())
        st.session_state.last_practice_context=context
        if st.button('Criar problema sobre esta busca →',key='knowledge_practice'):
            queue_practice(st.session_state,context,go)
    topic=col2.selectbox('Assunto do acervo',list(TOPICS),format_func=lambda x:TOPICS[x],key='knowledge_topic')
    left,right=st.columns([1,2])
    foundation=left.toggle('Começar pela base',value=True,key='knowledge_foundation')
    sources=['Todas']+[s['source'] for s in stats['sources']]
    source=right.selectbox('Fonte do conteúdo',sources,key='knowledge_source')
    filters=dict(source=None if source=='Todas' else source,topic=None if topic=='all' else topic,foundation_only=foundation)
    entries=kb.search(query,limit=10,per_document=1,**filters) if query.strip() else kb.browse(limit=15,**filters)
    st.caption('Português e inglês. Aulas autorais em português e referências internacionais; a explicação da IA continua em português.')
    if not entries:st.info('Nenhum resultado com esses filtros. Tente outro termo ou desative o filtro de base.')
    for item in entries:
        with st.container(border=True):
            st.markdown('**'+item['title']+'**')
            st.caption(item['source']+' · '+('Referência: texto completo não importado' if item.get('kind','').endswith('reference') else 'Texto disponível')+' · '+item.get('language',''))
            st.write(item['excerpt'][:500].replace('```',''))
            if st.button('Ler conteúdo',key='knowledge_read_'+item['id']):st.session_state.knowledge_selected=item['id']
    identifier=st.session_state.get('knowledge_selected')
    article=kb.get(identifier) if identifier else None
    if article:
        st.divider();st.markdown('## '+article['title'])
        if go:
            from core.practice_context import queue_practice
            if st.button('Criar problema sobre este conteúdo →',key='knowledge_article_practice'):
                queue_practice(st.session_state,dict(request=article['title'],concept='',level=st.session_state.get('level','Iniciante'),theme='',source_id=article['id'],source_title=article['title']),go)
        st.caption(article['source']+' · '+article.get('authors','')+' · '+article['license'])
        if article['url'].startswith('https://'):st.link_button('Abrir fonte original',article['url'])
        with st.expander('Créditos, versão e licença'):
            if article.get('license_url'):st.markdown('[Texto da licença]('+article['license_url']+')')
            if article.get('source_url'):st.markdown('[Versão importada da fonte]('+article['source_url']+')')
            st.write(article.get('adaptation',''))
        st.markdown(article['content'])
        st.download_button('Baixar texto com os créditos',article_markdown(article),article['id']+'.md','text/markdown',key='knowledge_download')
        notes(Library(store),profile_id,article['id'])
