"""Dated, sourced suggestions. Selecting a suggestion never triggers a paid request."""
from functools import lru_cache
import json
from pathlib import Path


@lru_cache(maxsize=1)
def recommendations():
    return json.loads((Path(__file__).resolve().parents[1]/'data/model_recommendations.json').read_text())


def render_model_recommendations(provider):
    import streamlit as st
    data=recommendations();item=data['providers'].get(provider)
    if not item:return
    with st.expander('Qual modelo usar neste sistema?'):
        st.caption('Recomendações verificadas em '+data['reviewed_at']+'. São candidatos para avaliação, sem teste próprio comparando as APIs.')
        if item.get('experimental'):
            st.write(item['reason']);return
        for name,label in [('quality','Priorizar qualidade'),('balanced','Uso diário e custo')]:
            choice=item[name]
            st.markdown('**'+label+': '+choice['title']+'**')
            st.write(choice['reason'])
            st.markdown('[Documentação do modelo]('+choice['url']+')')
            if st.button('Usar '+choice['title'],key='model_recommendation_'+provider+'_'+name):
                st.session_state.pending_model=(provider,choice['model'])
                if provider=='Qwen':st.session_state.pending_qwen_thinking=choice.get('thinking',False)
                st.rerun()
        st.caption('Selecionar altera somente o modelo. Use Testar conexão para conferir acesso, cota e geração real.')
