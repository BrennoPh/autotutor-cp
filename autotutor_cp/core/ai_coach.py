"""Model-authored learning decisions over measured, reproducible evidence."""
import hashlib
import json
from core.learning_engine import learning_stats, load_curriculum
from core.llm_client import AIUnavailable

LEVELS=('Iniciante','Intermediário','Avançado','Não avaliado')
VERSION=1


def encoded(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))


def learner_evidence(attempts,history,completed,hours=3):
    # Counts are measured here. Their interpretation belongs to the model.
    return {'topics':learning_stats(attempts,history),'completed_lessons':sorted(set(completed)),
            'hours_per_week':hours,'recent_results':[{k:h.get(k) for k in ('topic','verdict')} for h in history[-12:]]}


def evidence_key(evidence):
    return hashlib.sha256(encoded(evidence).encode()).hexdigest()


def cached_analysis(store,profile_id,evidence,llm=None):
    for item in store.artifacts(profile_id,kind='learning_analysis',limit=100):
        payload=item['payload']
        if payload.get('version')!=VERSION or payload.get('evidence_key')!=evidence_key(evidence):continue
        if llm and (payload.get('provider')!=llm.provider or payload.get('model')!=llm.model):continue
        return payload
    return None


def _text(value,limit=1800):
    return isinstance(value,str) and bool(value.strip()) and len(value)<=limit


def learner_schema():
    text={'type':'string','minLength':1,'maxLength':450}
    topic={'type':'object','properties':{'topic_id':{'type':'string','enum':[t['id'] for t in load_curriculum()]},'reason':text,'action':text},
           'required':['topic_id','reason','action'],'additionalProperties':False}
    properties={'level':{'type':'string','enum':list(LEVELS)},'confidence':{'type':'string','enum':['baixa','média','alta']},
                'summary':text,'strengths':{'type':'array','items':text,'maxItems':5},'gaps':{'type':'array','items':text,'maxItems':5},
                'roadmap':{'type':'array','items':topic,'minItems':9,'maxItems':9}}
    return {'type':'object','properties':properties,'required':list(properties),'additionalProperties':False}


def analyze_learner(llm,evidence):
    curriculum=[{k:t[k] for k in ('id','title','prerequisites')} for t in load_curriculum()]
    answer=llm.complete(
        'Você é um orientador de programação competitiva. Analise somente as evidências recebidas. '
        'Não use cortes fixos de porcentagem para decidir nível; avalie distribuição de erros, prática e lacunas. '
        'Dados insuficientes exigem incerteza explícita e nível Não avaliado. Leitura não prova domínio. '
        'Sem avaliação válida de questões ou problemas, não atribua nível. Não invente notas ou causas de erros. '
        'Respeite os pré-requisitos ao ordenar a trilha. Responda em português e JSON; todos os campos são obrigatórios.',
        'Formato: {"level":"Iniciante|Intermediário|Avançado|Não avaliado","confidence":"baixa|média|alta",'
        '"summary":"análise breve com evidências e limites","strengths":["observação"],"gaps":["observação"],'
        '"roadmap":[{"topic_id":"ID do currículo","reason":"motivo específico","action":"ação prática"}]}. '
        'Inclua cada um dos nove tópicos uma única vez, em ordem de estudo, com motivos curtos. '
        'CURRÍCULO: '+encoded(curriculum)+'\nEVIDÊNCIAS: '+encoded(evidence),learner_schema(),include_history=False)
    topics={t['id']:t for t in curriculum}
    valid=isinstance(answer,dict) and answer.get('level') in LEVELS and answer.get('confidence') in ('baixa','média','alta') and _text(answer.get('summary'))
    valid=valid and all(isinstance(answer.get(k),list) and len(answer[k])<=9 and all(_text(x,700) for x in answer[k]) for k in ('strengths','gaps'))
    plan=answer.get('roadmap') if isinstance(answer,dict) else None
    valid=valid and isinstance(plan,list) and len(plan)==len(topics)
    seen=set()
    if valid:
        for item in plan:
            if not isinstance(item,dict) or not isinstance(item.get('topic_id'),str) or item.get('topic_id') not in topics or item['topic_id'] in seen or not _text(item.get('reason'),700) or not _text(item.get('action'),700):
                valid=False;break
            if not set(topics[item['topic_id']]['prerequisites'])<=seen:
                valid=False;break
            seen.add(item['topic_id'])
    measured=any(s['answered'] or s['distinct_problems'] for s in evidence['topics'])
    if valid and not measured and answer['level']!='Não avaliado':valid=False
    if not valid:
        llm.report_fallback('A análise da IA veio incompleta, sem evidências ou com uma trilha inválida. Tente gerar novamente.')
        raise AIUnavailable('A IA não produziu uma análise válida.')
    return answer


def save_analysis(store,profile_id,llm,evidence,answer):
    payload=dict(answer,version=VERSION,evidence_key=evidence_key(evidence),provider=llm.provider,model=llm.model,
                 content=analysis_markdown(answer),source=llm.provider+' · '+llm.model,concept='Aprendizado')
    store.add_artifact(profile_id,'learning_analysis','Análise de aprendizado · '+llm.model,payload)
    return payload


def analysis_markdown(answer):
    topics={t['id']:t['title'] for t in load_curriculum()}
    text='## Análise de aprendizado\n\n'+answer['summary']+'\n\nNível sugerido: '+answer['level']+' · Confiança: '+answer['confidence']
    for title,key in [('Pontos fortes','strengths'),('O que investigar','gaps')]:
        text+='\n\n### '+title+'\n'+'\n'.join('- '+s for s in answer[key])
    text+='\n\n### Trilha sugerida\n'
    for i,item in enumerate(answer['roadmap'],1):text+=f'\n{i}. **{topics[item["topic_id"]]}** — {item["reason"]} {item["action"]}\n'
    return text


def compact_roster(roster):
    # Excludes usernames, conversations, API credentials and hand-weighted skill scores.
    return [dict(id='A'+str(i),statistics=[{'topic':s['id'],'quiz':{'correct':s['correct'],'answered':s['answered'],'accuracy_percent':round(s['correct']/s['answered']*100,1) if s['answered'] else None},'problems':{'accepted':s['accepted_problems'],'distinct':s['distinct_problems']},'compile_errors':s['compile_errors']} for s in m.get('topic_statistics',[]) if s['answered'] or s['submissions']],
                 local_accepted=len(m['local_solved']),accepted_problem_ids=m['local_solved'][:20],external_declared=len(m['external_solved']),
                 confirmed_external_ids=m['verified_external'][:20],problem_list_limit=20,
                 external_confirmed=len(m['verified_external']),quiz_correct=m['quiz_correct'],
                 quiz_answered=m['quiz_answered'],submissions=m['submissions']) for i,m in enumerate(roster)]


def class_evidence(roster):
    topics={}
    for member in roster:
        for s in member.get('topic_statistics',[]):
            if not (s['answered'] or s['submissions']):continue
            item=topics.setdefault(s['id'],dict(topic=s['id'],correct=0,answered=0,accepted=0,attempted_problems=0))
            item['correct']+=s['correct'];item['answered']+=s['answered']
            item['accepted']+=s['accepted_problems'];item['attempted_problems']+=s['distinct_problems']
    for item in topics.values():item['accuracy_percent']=round(item['correct']/item['answered']*100,1) if item['answered'] else None
    return dict(students=len(roster),local_accepted_total=sum(len(m['local_solved']) for m in roster),
                external_declared_total=sum(len(m['external_solved']) for m in roster),
                external_confirmed_total=sum(len(m['verified_external']) for m in roster),topics=list(topics.values()))


def analyze_class(llm,roster):
    result=llm.complete('Você é um assistente de professor. Interprete os dados agregados de programação competitiva. '
        'Os números e porcentagens já foram calculados: use-os exatamente, sem inventar nem recalcular valores. '
        'Diferencie aceites locais, confirmações externas e autodeclarações. Não atribua causas sem evidência. '
        'Explique padrões, limitações e ações concretas. Responda em português, até 250 palavras.',
        'DADOS MEDIDOS DA TURMA (correct=acertos; answered=questões respondidas; accuracy_percent=porcentagem de acerto; '
        'accepted=problemas com última submissão aceita, somados entre alunos): '+encoded(class_evidence(roster)),include_history=False)
    if not _text(result,5000):
        llm.report_fallback('A IA não produziu uma análise válida da turma.')
        raise AIUnavailable('Sem análise da turma.')
    return result


def propose_teams(llm,roster,strategy,mode):
    if strategy not in ('Complementaridade','Equilíbrio entre trios','Níveis semelhantes') or mode not in ('Turma inteira','Melhor trio'):raise ValueError('Selecione estratégia e objetivo válidos.')
    if len({m['id'] for m in roster})!=len(roster):raise ValueError('Há participantes repetidos na seleção.')
    if len(roster)<3:raise ValueError('Selecione pelo menos três alunos.')
    if len(roster)>30:raise ValueError('Para este modelo leve, selecione até 30 alunos por rodada.')
    data=compact_roster(roster);by_id={x['id']:m for x,m in zip(data,roster)}
    text={'type':'string','minLength':1,'maxLength':450}
    identifier={'type':'string','enum':list(by_id)}
    group={'type':'object','properties':{'members':{'type':'array','items':identifier,'minItems':3,'maxItems':3},'reason':text},'required':['members','reason'],'additionalProperties':False}
    number=1 if mode=='Melhor trio' else len(roster)//3
    schema={'type':'object','properties':{'teams':{'type':'array','items':group,'minItems':number,'maxItems':number},
            'waiting':{'type':'array','items':identifier,'minItems':len(roster)-number*3,'maxItems':len(roster)-number*3},'summary':text},
            'required':['teams','waiting','summary'],'additionalProperties':False}
    result=llm.complete('Você forma trios de programação competitiva a partir de evidências. '
        'Use somente IDs fornecidos, uma vez por participante. Não use notas fixas ou pesos predefinidos. '
        'Todos os participantes são elegíveis. Não invente nota mínima para participar, nem critérios de exclusão. '
        'Explique como os resultados sustentam cada escolha e reconheça pouca evidência. '
        'Responda em português e JSON. Não afirme garantir o melhor resultado em competição.',
        'Formato {"teams":[{"members":["A0","A1","A2"],"reason":"justificativa"}],"waiting":["A3"],"summary":"limites da proposta"}. '
        'Objetivo: '+mode+'. Estratégia: '+strategy+'. '
        'Turma inteira: forme o máximo de trios; Melhor trio: forme exatamente um trio. '
        'Todos os restantes devem constar em waiting. DADOS: '+encoded(data),schema,include_history=False)
    valid=isinstance(result,dict) and isinstance(result.get('teams'),list) and isinstance(result.get('waiting'),list) and _text(result.get('summary'))
    groups=result['teams'] if valid else [];waiting=result['waiting'] if valid else []
    participants=[]
    if valid:
        for group in groups:
            if not isinstance(group,dict) or not isinstance(group.get('members'),list) or len(group['members'])!=3 or not _text(group.get('reason'),1000):valid=False;break
            participants.extend(group['members'])
        participants+=waiting
        valid=valid and all(isinstance(i,str) and i in by_id for i in participants)
        valid=valid and len(participants)==len(by_id) and len(set(participants))==len(participants)
        valid=valid and len(groups)==(1 if mode=='Melhor trio' else len(roster)//3)
    if not valid:
        llm.report_fallback('A IA propôs uma formação inválida ou incompleta. Nenhum trio foi salvo; tente novamente.')
        raise AIUnavailable('Formação inválida.')
    details=[dict(members=[by_id[i]['id'] for i in g['members']],names=[by_id[i]['name'] for i in g['members']],reason=g['reason']) for g in groups]
    return dict(teams=[d['members'] for d in details],waiting=[by_id[i]['id'] for i in waiting],details=details,
                strategy=strategy,method='Proposta por IA · '+llm.model,note=result['summary'],provider=llm.provider,model=llm.model)
