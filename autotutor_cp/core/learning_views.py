"""Study screens, original teaching diagrams and learner-data visualizations."""
from html import escape
import json
from pathlib import Path

import altair as alt
import streamlit as st
import streamlit.components.v1 as components
from core.learning_engine import (load_curriculum, questions_for, question_bank, grade_answers,
                                 learning_stats, verdict_counts, lesson_markdown)
from core.ui import heading, html, badge, empty


def diagram(topic_id, step=0):
    """Schematic, editable SVG diagrams; no remote images or invented metrics."""
    parts = []
    def text(x,y,value,size=16,color='var(--ink,#334155)'):
        parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="middle">{escape(str(value))}</text>')
    def box(x,y,value,active=False,width=58):
        parts.append(f'<rect x="{x}" y="{y}" width="{width}" height="42" rx="8" fill="{"#4f46e5" if active else "var(--surface-alt,#eef2ff)"}" stroke="#d6daf3"/>')
        text(x+width/2,y+27,value,color='#ffffff' if active else 'var(--ink,#334155)')
    captions = {
        'prefix':'Somar [2,4]: P[4] − P[1] = 10 − 2 = 8',
        'binary':['Intervalo [0,7]; meio 3 tem valor 7','Alvo 11 é maior: manter posições [4,7]','Meio 5 tem valor 11: encontrado'][min(step,2)],
        'dp':'formas[5] = formas[4] + formas[3] = 5 + 3 = 8',
        'structures':['Fila após inserir 12, 7 e 5','FIFO: sai 12; 7 fica na frente'][min(step,1)],
        'math':['mdc(48,18)','mdc(18,12)','mdc(12,6)','mdc(6,0) = 6'][min(step,3)],
        'fundamentals':'Dois laços: 4 × 4 = 16 pares de posições',
        'greedy':'Menor término permite selecionar três intervalos',
        'graph':f'BFS a partir de A · camada {step}',
        'tree':'Estrela: altura a partir de C = 1; diâmetro = 2'}
    caption = captions[topic_id]
    text(300,30,caption,15)
    if topic_id in ('prefix','binary','dp','structures'):
        values = {'prefix':[2,4,1,3],'binary':[1,3,5,7,9,11,13,15], 'dp':[1,1,2,3,5,8],
                  'structures':[12,7,5] if step == 0 else [7,5]}[topic_id]
        width = min(62, 500 / len(values))
        start = (600 - len(values)*(width+5))/2
        for i,value in enumerate(values):
            active = (topic_id=='prefix' and i>=1) or (topic_id=='binary' and i==(3 if step==0 else 5)) or (topic_id=='dp' and i in (3,4,5))
            box(start+i*(width+5),75,value,active,width)
            text(start+i*(width+5)+width/2,140,i+(1 if topic_id=='prefix' else 0),12,'var(--muted,#64748b)')
        if topic_id=='prefix':
            text(95,190,'Prefixos',13)
            for i,value in enumerate([0,2,6,7,10]):
                box(165+i*65,163,value,i in (1,4))
        elif topic_id=='dp':
            text(300,198,'Cada estado soma os dois anteriores',14)
        elif topic_id=='structures':
            text(300,198,'Frente → ordem de atendimento → fim',14)
        else:
            text(300,198,'Alvo = 11 · índices começam em zero',14)
    elif topic_id in ('graph','tree'):
        if topic_id=='tree':
            nodes={'C':(300,100),'A':(150,195),'B':(300,195),'D':(450,195)}
            edges=[('C','A'),('C','B'),('C','D')]
            distances={'C':0,'A':1,'B':1,'D':1}
        else:
            nodes={'A':(90,125),'B':(230,75),'C':(230,185),'D':(390,75),'E':(390,185),'F':(525,185)}
            edges=[('A','B'),('A','C'),('B','D'),('C','E'),('E','F')]
            distances={'A':0,'B':1,'C':1,'D':2,'E':2,'F':3}
        for a,b in edges:
            x,y=nodes[a]; x2,y2=nodes[b]
            parts.append(f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" stroke="#a5add2" stroke-width="3"/>')
        for name,(x,y) in nodes.items():
            active = topic_id=='tree' or distances[name] <= step
            parts.append(f'<circle cx="{x}" cy="{y}" r="22" fill="{"#4f46e5" if active else "var(--surface-alt,#e9edf7)"}"/>')
            text(x,y+5,name,16,'#ffffff' if active else 'var(--muted,#64748b)')
            if topic_id=='graph':text(x,y+39,f'd={distances[name]}' if active else 'não descoberto',12)
    elif topic_id=='math':
        values=[(48,18),(18,12),(12,6),(6,0)]
        for i,(a,b) in enumerate(values):
            box(38+i*145,100,f'{a}, {b}',i==step,110)
            if i<3:text(167+i*145,128,'→',20)
        text(300,192,'A cada troca, o conjunto de divisores comuns é preservado',13)
    elif topic_id=='fundamentals':
        for i in range(4):
            for j in range(4):
                box(175+j*62,60+i*43,f'{i},{j}',i==step,52)
    else:
        intervals=[(0,6,'Uma escolha longa',False),(0,2,'Evento 1',True),(2,4,'Evento 2',True),(4,6,'Evento 3',True)]
        for i,(start,end,label,chosen) in enumerate(intervals):
            y=60+i*41
            text(82,y+24,label,12)
            parts.append(f'<rect x="{165+start*60}" y="{y}" width="{(end-start)*60-3}" height="28" rx="5" fill="{"#4f46e5" if chosen else "#cbd5e1"}"/>')
        for i in range(7):text(165+i*60,240,i,12)
    return '<div style="overflow-x:auto"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 265" role="img" aria-label="'+escape(caption,quote=True)+'" style="width:100%;min-width:600px;height:auto;font-family:Arial,sans-serif"><title>'+escape(caption)+'</title>'+''.join(parts)+'</svg></div>'


def slides_html(topic):
    sections = []
    for i,slide in enumerate(topic['slides']):
        bullets=''.join('<li>'+escape(p)+'</li>' for p in slide.get('points',[]))
        if 'body' in slide and slide['body']:
            bullets+=f'<div>{escape(slide["body"])}</div>'
        visual=diagram(topic['id']) if i==5 else ''
        notes=escape(slide.get('notes',''))
        sections.append(f'<section class="slide" aria-label="Slide {i+1}"><small>{escape(topic["title"])} · {i+1}/{len(topic["slides"])}</small><h1>{escape(slide["title"])}</h1><ul>{bullets}</ul>{visual}<details><summary>Notas de estudo</summary><p>{notes}</p></details></section>')
    return '''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AutoTutor · '''+escape(topic['title'])+'''</title><style>
body{font-family:system-ui,sans-serif;background:#f5f7fb;color:#17233b;margin:0;padding:24px}main{max-width:1000px;margin:auto}.slide{display:none;background:white;padding:38px;border-radius:18px;min-height:440px;box-sizing:border-box}.slide.active{display:block}h1{font-size:clamp(24px,4vw,42px);line-height:1.2}small{color:#6859cc}li{font-size:20px;line-height:1.6;margin:14px 0}p{line-height:1.8}nav{display:flex;gap:12px;align-items:center;margin:20px 0}button{padding:12px 18px;background:#4f46e5;color:white;border:0;border-radius:8px;font-size:16px}button:disabled{opacity:.4}svg{max-height:250px}details{margin-top:20px;color:#64748b}@media(max-width:500px){body{padding:12px}.slide{padding:24px}li{font-size:17px}}@media print{nav{display:none}.slide{display:block!important;break-after:page;min-height:0;border-radius:0;padding:20px}details{display:block}}
</style><main>'''+''.join(sections)+'''<nav aria-label="Navegar slides"><button id="prev">← Anterior</button><span id="count" aria-live="polite"></span><button id="next">Próximo →</button><button onclick="window.print()">Imprimir / PDF</button></nav><p>Material autoral de estudo · AutoTutor-CP. Os exemplos são didáticos.</p></main><script>
const slides=[...document.querySelectorAll('.slide')];let index=0;function draw(){slides.forEach((s,i)=>s.classList.toggle('active',i===index));document.getElementById('count').textContent=`${index+1} / ${slides.length}`;document.getElementById('prev').disabled=index===0;document.getElementById('next').disabled=index===slides.length-1}document.getElementById('prev').onclick=()=>{index=Math.max(0,index-1);draw()};document.getElementById('next').onclick=()=>{index=Math.min(slides.length-1,index+1);draw()};document.addEventListener('keydown',e=>{if(e.key==='ArrowRight')document.getElementById('next').click();if(e.key==='ArrowLeft')document.getElementById('prev').click()});draw();
</script></html>'''


def render_feedback(attempt):
    bank=question_bank()
    st.success(f'{attempt["correct"]} de {attempt["total"]} respostas corretas')
    for answer in attempt['answers']:
        q=bank[answer['question_id']]
        correct=answer['selected']==q['answer']
        with st.expander(('✓ ' if correct else 'Revisar · ') + q['prompt']):
            st.write('Sua resposta: '+q['options'][answer['selected']])
            if not correct:st.write('Resposta esperada: '+q['options'][q['answer']])
            st.write(q['explanation'])


def learner_analysis_panel(store,profile_id,llm,*,key):
    from core.ai_coach import learner_evidence,cached_analysis,analyze_learner,save_analysis
    evidence=learner_evidence(st.session_state.quiz_attempts,st.session_state.history,
                              st.session_state.completed_lessons,st.session_state.get('study_hours',3))
    result=cached_analysis(store,profile_id,evidence,llm)
    st.caption('A IA interpreta seus resultados e propõe nível e trilha. As estatísticas são calculadas a partir das suas atividades.')
    st.caption('Para solicitar uma avaliação com Gemini e receber o parecer do professor, abra Turmas → Avaliação com professor. Essa avaliação é compartilhada apenas com o professor da turma.')
    if st.button('Atualizar análise com IA' if result else 'Analisar meu aprendizado com IA',key=key,type='primary'):
        with st.spinner('A IA está analisando suas evidências…'):
            answer=analyze_learner(llm,evidence)
            result=save_analysis(store,profile_id,llm,evidence,answer)
    if result:
        st.markdown('**Nível sugerido pela IA:** '+result['level']+' · Confiança '+result['confidence'])
        st.write(result['summary'])
        st.caption('Modelo: '+result['model']+' · Confiança declarada pelo próprio modelo, sem calibração. Análise salva na biblioteca. Novas atividades exigem uma nova análise.')
    else:st.info('Gere uma análise para receber uma interpretação personalizada. Ainda não há análise atualizada deste modelo.')
    return result


def render_diagnostic(store, profile_id, save, go, llm):
    heading('SEU PONTO DE PARTIDA','O que você já sabe?', '18 perguntas, sem cronômetro. A estimativa inicial serve para orientar a prática, não como certificação.')
    result=learner_analysis_panel(store,profile_id,llm,key='diagnostic_ai')
    if result and result['level']!='Não avaliado':
        if st.button('Usar este nível na prática',key='use_estimated_level'):
            st.session_state.pending_level=result['level'];st.rerun()
    with st.expander('Como funciona a avaliação'):
        st.write('O modelo recebe acertos, erros e resultados por assunto. Ele estima o nível e explica a incerteza, sem faixas fixas de porcentagem. O gabarito continua determinando quais alternativas estão corretas.')
    st.caption('Você pode responder por etapas. Suas escolhas só entram nas estatísticas ao concluir o diagnóstico.')
    if 'diagnostic_draft' not in st.session_state:st.session_state.diagnostic_draft={}
    questions=questions_for('diagnostic')
    answered=len(st.session_state.diagnostic_draft)
    st.progress(answered/len(questions), text=f'{answered} de {len(questions)} respondidas')
    stage=st.selectbox('Etapa do diagnóstico',[0,1,2],format_func=lambda x:['1 · Fundamentos, estruturas e prefixos','2 · Busca binária, matemática e guloso','3 · DP, grafos e árvores'][x],key='diagnostic_stage')
    for question in questions[stage*6:(stage+1)*6]:
        qid=question['id']
        def keep_answer(question_id=qid):
            selected=st.session_state['diagnostic_'+question_id]
            if selected is not None:st.session_state.diagnostic_draft[question_id]=selected
        selected=st.session_state.diagnostic_draft.get(qid)
        st.radio(question['prompt'],list(range(len(question['options']))),format_func=lambda x,q=question:q['options'][x],
                 index=selected,key='diagnostic_'+qid,on_change=keep_answer)
    if st.button('Concluir diagnóstico',type='primary',disabled=answered<len(questions),key='finish_diagnostic'):
        attempt=grade_answers(st.session_state.diagnostic_draft)
        st.session_state.quiz_attempts.append(attempt)
        store.add_artifact(profile_id,'quiz','Diagnóstico inicial',attempt)
        save(); st.rerun()
    if any(a.get('kind')=='diagnostic' for a in st.session_state.quiz_attempts):
        with st.expander('Conferir respostas do último diagnóstico'):
            render_feedback(next(a for a in reversed(st.session_state.quiz_attempts) if a['kind']=='diagnostic'))


def render_roadmap(store,profile_id,save,go,llm,on_ai=None):
    mode=st.radio('Tipo de trilha',['Plano geral','Por assunto'],horizontal=True,key='roadmap_mode')
    if mode=='Por assunto':
        from core.topic_plan_views import render_topic_plans
        render_topic_plans(store,profile_id,save,go,llm,on_ai);return
    heading('UMA TRILHA PARA VOCÊ','Seu próximo passo tem um motivo.', 'A IA considera suas atividades, os pré-requisitos e seu tempo disponível.')
    st.slider('Tempo disponível por semana (horas)',1,12,key='study_hours',on_change=save)
    result=learner_analysis_panel(store,profile_id,llm,key='roadmap_ai')
    if not result:
        if st.button('Fazer diagnóstico →',key='roadmap_to_diagnostic'):go('Diagnóstico')
        return
    topics={t['id']:t for t in load_curriculum()}
    for i,item in enumerate(result['roadmap'],1):
        topic=topics[item['topic_id']]
        with st.container(border=True):
            st.markdown(f'**{i:02d} · {topic["title"]}**')
            st.write(item['reason']);st.caption(item['action'])
            if st.button('Estudar →',key='roadmap_'+topic['id']):
                st.session_state.pending_lesson=topic['id'];go('Biblioteca')


def render_library(store,profile_id,save,go,problems):
    heading('BIBLIOTECA DE APRENDIZADO','Entenda. Visualize. Coloque em prática.', 'Aulas, guias de aprofundamento, referências selecionadas e sua coleção de conteúdos salvos.')
    from core.library_views import library_section
    if library_section(store,profile_id,go,problems):return
    topics={t['id']:t for t in load_curriculum()}
    if st.session_state.get('learning_topic') not in topics:st.session_state.learning_topic='fundamentals'
    if 'lesson_picker' not in st.session_state:
        st.session_state.lesson_picker=st.session_state.learning_topic
    selected=st.selectbox('Assunto',list(topics),format_func=lambda x:topics[x]['title'],index=None,key='lesson_picker')
    if selected is None:
        empty('Escolha um assunto','Selecione um módulo para abrir a aula, os slides e a fixação.')
        return
    st.session_state.learning_topic=selected
    topic=topics[selected]
    html(badge(f'~{topic["minutes"]} min')+badge(f'{len(topic["slides"])} slides','indigo')+badge('Material autoral · disponível sem API'))
    tabs=st.tabs(['Aula completa','Slides','Visualização','Vídeos','Fixação'])
    from core.library import references_for
    from core.library_views import reference_card
    from core.library import Library
    library=Library(store)
    with tabs[0]:
        st.markdown('### '+topic['title']);st.write(topic['summary'])
        st.markdown('#### Ao concluir, você deverá conseguir')
        for objective in topic['objectives']:st.markdown('- '+objective)
        for section in topic['sections']:
            st.markdown('### '+section['title']);st.write(section['body'])
        st.markdown('### Exemplo passo a passo');st.write(topic['example']['story'])
        for i,line in enumerate(topic['example']['trace'],1):st.markdown(f'**{i}.** {line}')
        st.code(topic['example']['code'],language='cpp')
        html(diagram(selected))
        st.markdown('### Erros frequentes')
        for pitfall in topic['pitfalls']:st.markdown('- '+pitfall)
        st.markdown('### Experimente por conta própria');st.write(topic['challenge'])
        studied=selected in st.session_state.completed_lessons
        if st.button('Aula já marcada como estudada' if studied else 'Marcar aula como estudada ✓',disabled=studied,key='complete_'+selected):
            st.session_state.completed_lessons.append(selected)
            store.add_artifact(profile_id,'lesson_event',topic['title'],{'topic_id':selected,'event':'studied'})
            save();st.rerun()
        st.caption('Marcar a leitura registra seu estudo; os acertos e a prática continuam sendo medidos separadamente.')
        st.download_button('Baixar aula em Markdown',lesson_markdown(topic),selected+'.md','text/markdown',key='download_lesson_'+selected)
    with tabs[1]:
        num_slides=len(topic['slides'])
        slide_key='slide_curriculum_'+selected
        if slide_key not in st.session_state:
            st.session_state[slide_key]=1
        curr_slide=st.session_state[slide_key]

        nav_col1,nav_col2,nav_col3=st.columns([1,2,1])
        with nav_col1:
            if st.button('← Anterior',disabled=(curr_slide<=1),key='btn_prev_curric_'+selected,use_container_width=True):
                st.session_state[slide_key]=max(1,curr_slide-1)
                st.rerun()
        with nav_col2:
            slide_labels=[f'Slide {i+1}/{num_slides}: {s.get("title","")[:38]}' for i,s in enumerate(topic['slides'])]
            selected_idx=st.selectbox(
                'Slide',
                range(num_slides),
                format_func=lambda i:slide_labels[i],
                index=curr_slide-1,
                key='sel_curric_slide_'+selected,
                label_visibility='collapsed'
            )
            if selected_idx+1!=curr_slide:
                st.session_state[slide_key]=selected_idx+1
                st.rerun()
        with nav_col3:
            if st.button('Próximo →',disabled=(curr_slide>=num_slides),key='btn_next_curric_'+selected,use_container_width=True):
                st.session_state[slide_key]=min(num_slides,curr_slide+1)
                st.rerun()

        st.progress(curr_slide/num_slides)
        slide_index=curr_slide
        slide=topic['slides'][slide_index-1]
        with st.container(border=True):
            st.caption(f'{topic["title"].upper()} · Slide {slide_index}/{num_slides}')
            st.markdown('## '+slide['title'])
            for point in slide.get('points',[]):st.markdown('- '+point)
            if 'body' in slide and slide['body']:st.markdown(slide['body'])
            if slide_index==6:html(diagram(selected))
        with st.expander('Notas de estudo deste slide'):
            st.write(slide.get('notes',''))
        st.download_button('Baixar apresentação interativa',slides_html(topic),selected+'-slides.html','text/html',key='download_slides_'+selected)
        st.caption('O arquivo HTML funciona sem internet, aceita as setas do teclado e pode ser impresso ou salvo como PDF pelo navegador.')
    with tabs[2]:
        ranges={'binary':2,'graph':3,'structures':1,'math':3,'fundamentals':3}
        step=st.slider('Etapa da demonstração',0,ranges[selected],0,key='visual_step_'+selected) if selected in ranges else 0
        html(diagram(selected,step))
        st.write(topic['example']['story'])
        st.caption('Ilustração didática com dados do exemplo; não representa o seu desempenho.')
    with tabs[3]:
        from core.catalog import STUDY_SOURCES
        with st.expander('Mais fontes de estudo'):
            for resource in STUDY_SOURCES:st.markdown('['+resource['name']+']('+resource['url']+') · '+resource['kind'])
        st.write('Seleção de aulas em português, relacionadas ao assunto e listadas no catálogo educacional do AoCPC.')
        for i,video in enumerate(topic['videos']):
            with st.container(border=True):
                st.markdown('#### '+video['title'])
                st.caption(video['publisher']+' · '+video['language'])
                st.markdown(f'[Assistir no YouTube ↗]({video["url"]}) · [Fonte da recomendação]({video["source_url"]})')
                if st.toggle('Abrir vídeo nesta página',key='video_'+selected+'_'+str(i)):
                    st.video(video['url'])
        with st.expander('Leituras e vídeos adicionais para este assunto'):
            for r in references_for(topic['title']):
                st.markdown('**'+r['title']+'**')
                reference_card(r,library,profile_id,'lesson_'+selected+r['id'])
        from core.book_catalog import books_for_topic
        topic_books = books_for_topic(selected)
        if topic_books:
            with st.expander('📚 Livros clássicos recomendados para este assunto', expanded=True):
                st.write('Capítulos selecionados nas maiores obras de referência de algoritmos e maratona:')
                for b in topic_books:
                    with st.container(border=True):
                        oa_tag = ' · :green-background[Acesso Aberto]' if b['open_access'] else ''
                        st.markdown(f"**[{b['title']}]({b['url']})**" + oa_tag)
                        st.caption(f"Autores: {', '.join(b['authors'])} · {b['edition']} ({b['publisher']})")
                        st.markdown(f"📖 **Capítulo indicado:** {b['chapter_reading']}")
                        st.caption(b['overview'])
        st.caption('Links conferidos no catálogo em 24/10/2026. Disponibilidade, anúncios e incorporação dependem do YouTube. Assistir a um vídeo não marca domínio do assunto.')
    with tabs[4]:
        st.markdown('### Confira o que ficou')
        st.caption('A correção só aparece após enviar. Ao repetir, as estatísticas usam a sua resposta mais recente para cada questão.')
        with st.form('review_form_'+selected):
            answers={}
            for question in questions_for('review',selected):
                choice=st.radio(question['prompt'],list(range(len(question['options']))),format_func=lambda x,q=question:q['options'][x],index=None,key='review_'+question['id'])
                answers[question['id']]=choice
            submitted=st.form_submit_button('Corrigir fixação',type='primary')
        if submitted:
            try:
                attempt=grade_answers(answers,'review',selected)
                st.session_state.quiz_attempts.append(attempt)
                store.add_artifact(profile_id,'quiz','Fixação · '+topic['title'],attempt)
                save();st.rerun()
            except ValueError as exc:st.warning(str(exc))
        latest=next((a for a in reversed(st.session_state.quiz_attempts) if a.get('kind')=='review' and a.get('topic_id')==selected),None)
        if latest:render_feedback(latest)
        related=[p for p in problems if p['topic']==topic['title'] and not p.get('external')]
        for problem in related[:2]:
            if st.button('Praticar: '+problem['title'],key='lesson_practice_'+problem['id']):go('Arena',problem['id'])
        if not related:st.caption('Este módulo não tem um problema específico no banco atual. Use o exercício proposto e o laboratório para continuar.')


def render_performance(store,profile_id,save,go,llm):
    heading('EVIDÊNCIAS DO SEU APRENDIZADO','Veja onde está avançando.', 'Dados do seu perfil local. Leituras, questões e resultados de programação são apresentados separadamente.')
    attempts=st.session_state.quiz_attempts;history=st.session_state.history
    stats=learning_stats(attempts,history)
    measured=[s for s in stats if s['answered']]
    answered=sum(s['answered'] for s in stats);correct=sum(s['correct'] for s in stats)
    accepted=sum(h.get('verdict')=='AC' for h in history)
    columns=st.columns(4)
    for column,label,value in zip(columns,['Questões distintas respondidas','Acerto nas questões','Submissões aceitas','Aulas marcadas como estudadas'],
        [answered,f'{correct/answered:.0%}' if answered else '—',f'{accepted}/{len(history)}' if history else '—',len(st.session_state.completed_lessons)]):
        column.metric(label,value)
    if not answered and not history:
        empty('Seu painel começa com evidências reais','Faça o diagnóstico ou envie uma solução. O painel será preenchido com seus resultados.','◈')
        if st.button('Fazer diagnóstico →',key='performance_diagnostic'):go('Diagnóstico')
        return
    if measured:
        st.markdown('### Acerto por assunto')
        records=[{'Assunto':s['title'],'Acerto (%)':round(s['accuracy']*100,1),'Corretas':s['correct'],'Respondidas':s['answered']} for s in measured]
        chart=alt.Chart(alt.Data(values=records)).mark_bar(color='#6055dc',cornerRadiusEnd=4).encode(
            x=alt.X('Acerto (%):Q',scale=alt.Scale(domain=[0,100]),title='Respostas corretas (%)'),
            y=alt.Y('Assunto:N',sort='-x',title='Assunto'),tooltip=['Assunto:N','Corretas:Q','Respondidas:Q','Acerto (%):Q']).properties(height=max(220,len(records)*37))
        color='#dce5f0' if st.session_state.get('theme_dark',True) else '#202b3d'
        chart=chart.properties(background='transparent').configure_view(strokeOpacity=0).configure_axis(labelColor=color,titleColor=color,gridOpacity=.15).configure_legend(labelColor=color,titleColor=color)
        st.altair_chart(chart,width='stretch')
        st.caption('Fonte: questionários deste perfil. Cada questão contribui apenas com a resposta mais recente. Assuntos não avaliados não recebem nota zero. Duas questões por tópico ainda são pouca evidência.')
    analysis=learner_analysis_panel(store,profile_id,llm,key='performance_ai')
    if analysis:
        left,right=st.columns(2)
        with left:
            st.markdown('#### Pontos fortes segundo a IA')
            for value in analysis['strengths']:st.write(value)
        with right:
            st.markdown('#### O que investigar segundo a IA')
            for value in analysis['gaps']:st.write(value)
    if attempts:
        st.markdown('### Resultados ao longo das atividades')
        points=[{'Atividade':i,'Acerto (%)':round(a['correct']/a['total']*100,1),'Tipo':'Diagnóstico' if a['kind']=='diagnostic' else 'Fixação',
                 'Questões':a['total']} for i,a in enumerate(attempts,1)]
        chart=alt.Chart(alt.Data(values=points)).mark_line(point=True,color='#4f46e5').encode(
            x=alt.X('Atividade:O',title='Atividade em ordem de realização'),y=alt.Y('Acerto (%):Q',scale=alt.Scale(domain=[0,100])),
            tooltip=['Atividade:O','Tipo:N','Acerto (%):Q','Questões:Q']).properties(height=220)
        color='#dce5f0' if st.session_state.get('theme_dark',True) else '#202b3d'
        chart=chart.properties(background='transparent').configure_view(strokeOpacity=0).configure_axis(labelColor=color,titleColor=color,gridOpacity=.15).configure_legend(labelColor=color,titleColor=color)
        st.altair_chart(chart,width='stretch')
        st.caption('Atividades podem ter assuntos, dificuldades e quantidades diferentes. A linha mostra resultados observados, não uma medida padronizada de domínio.')
    if history:
        st.markdown('### Resultados no juiz')
        verdicts=verdict_counts(history)
        chart=alt.Chart(alt.Data(values=verdicts)).mark_arc(innerRadius=65).encode(theta='Submissões:Q',
            color=alt.Color('Veredito:N',scale=alt.Scale(domain=['AC','WA','TLE','RE','CE'],range=['#10a779','#e6a23c','#d47b46','#d86180','#8b7ace'])),
            tooltip=['Veredito:N','Submissões:Q']).properties(height=250)
        color='#dce5f0' if st.session_state.get('theme_dark',True) else '#202b3d'
        chart=chart.properties(background='transparent').configure_view(strokeOpacity=0).configure_axis(labelColor=color,titleColor=color,gridOpacity=.15).configure_legend(labelColor=color,titleColor=color)
        st.altair_chart(chart,width='stretch')
        st.caption('Fonte: todas as submissões deste perfil. CE indica falha de compilação; o veredito isolado não identifica a causa nem prova dificuldade conceitual.')
        for s in stats:
            if s['distinct_problems']:
                st.write(f'**{s["title"]}** · {s["accepted_problems"]}/{s["distinct_problems"]} problemas com última submissão aceita · {s["submissions"]} tentativas no total.')
    has_diag = any(a.get('kind') == 'diagnostic' for a in attempts)
    if has_diag:
        st.divider()
        with st.expander('Refazer teste de diagnóstico inicial'):
            st.caption('Você já realizou o diagnóstico inicial e tem seu ponto de partida registrado. Se quiser refazer as 18 perguntas para atualizar sua estimativa, clique abaixo:')
            if st.button('Refazer diagnóstico inicial →', key='redo_diagnostic_btn'):
                go('Diagnóstico')
