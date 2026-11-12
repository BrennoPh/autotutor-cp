"""AI-authored topic plans, real catalog resources, calendar constraints and private progress."""
from datetime import date,timedelta
import json
import re
from core.knowledge import KnowledgeBase
from core.learning_engine import load_curriculum,learning_stats
from core.library import resources
from core.catalog import catalog
from core.llm_client import AIUnavailable

STYLES=['Equilibrado','Aprendo resolvendo problemas','Prefiro teoria antes da prática','Prefiro vídeos e exemplos']
WEEKDAYS=['Segunda','Terça','Quarta','Quinta','Sexta','Sábado','Domingo']
KINDS={'aula':'Aula','artigo':'Artigo / blog','video':'Vídeo','problema':'Problema','revisao':'Revisão'}


def preferences(topic,goal,base_topic,style,minutes,weekdays,start_date,max_weeks):
    if not isinstance(topic,str) or not 2<=len(topic.strip())<=150:raise ValueError('Informe um assunto de 2 a 150 caracteres.')
    if not isinstance(goal,str) or len(goal)>1200:raise ValueError('Descreva seu objetivo em até 1200 caracteres.')
    if not isinstance(base_topic,str) or base_topic not in {t['id'] for t in load_curriculum()}:raise ValueError('Escolha um assunto de referência válido.')
    if style not in STYLES or type(minutes) is not int or not 15<=minutes<=180:raise ValueError('Escolha uma preferência e um tempo diário válido.')
    if not isinstance(weekdays,list) or not weekdays or any(type(d) is not int or not 0<=d<=6 for d in weekdays) or len(set(weekdays))!=len(weekdays):raise ValueError('Escolha pelo menos um dia da semana, sem repetições.')
    if type(max_weeks) is not int or not 1<=max_weeks<=12:raise ValueError('Escolha um horizonte entre 1 e 12 semanas.')
    start=date.fromisoformat(str(start_date))
    return dict(topic=topic.strip(),goal=goal.strip(),base_topic=base_topic,style=style,minutes=minutes,weekdays=sorted(weekdays),start_date=start.isoformat(),max_weeks=max_weeks)


def available_dates(prefs):
    start=date.fromisoformat(prefs['start_date'])
    return [(start+timedelta(days=i)).isoformat() for i in range(prefs['max_weeks']*7) if (start+timedelta(days=i)).weekday() in prefs['weekdays']]


def candidate_resources(prefs):
    topic=next(t for t in load_curriculum() if t['id']==prefs['base_topic']);kb=KnowledgeBase();result=[]
    for hit in kb.search(prefs['topic']+' '+prefs['goal']+' '+topic['title'],limit=6,per_document=1,foundation_only=True):
        result.append(dict(id='A'+str(len(result)),kind='aula' if hit.get('kind') in ('lesson','guide') else 'artigo',title=hit['title'],
            url=hit['url'],knowledge_id=hit['id'],description=hit.get('context_excerpt',hit['excerpt'])[:400],source=hit['source'],license=hit['license']))
    if not result:
        result.append(dict(id='A0',kind='aula',title=topic['title'],url='',lesson_id=topic['id'],description=topic['summary'],source='Biblioteca do AutoTutor'))
    known=set()
    for resource in resources():
        if prefs['base_topic'] not in resource['topics']:continue
        kind='video' if resource['kind']=='Vídeo' else 'artigo'
        if kind!='video':continue
        if resource['url'] in known:continue
        known.add(resource['url'])
        result.append(dict(id='V'+str(len(known)-1),kind=kind,title=resource['title'],url=resource['url'],description=resource.get('summary','')[:250],source=resource['publisher']))
        if len(known)==3:break
    # URLs embedded in imported modules remain links; no video/transcript is downloaded.
    if not known:
        for hit in kb.search(prefs['topic'],limit=3,per_document=1,foundation_only=True):
            doc=kb.get(hit['id'])
            for title,url in re.findall(r'\[([^\]]+)\]\((https://www.youtube.com/watch\?v=[A-Za-z0-9_-]+)\)',doc['content']):
                if url not in known:
                    known.add(url);result.append(dict(id='V'+str(len(known)-1),kind='video',title=title,url=url,description='Vídeo indicado no módulo '+hit['title'],source=hit['source']))
                if len(known)==3:break
            if len(known)==3:break
    problems=[p for p in catalog() if p['topic']==topic['title']]
    problems.sort(key=lambda p:(bool(p.get('external')),{'Iniciante':0,'Intermediário':1,'Avançado':2}.get(p['difficulty'],3),p['title']))
    for i,problem in enumerate(problems[:14]):
        result.append(dict(id='P'+str(i),kind='problema',title=problem['title'],problem_id=problem['id'],url=problem.get('source_url',''),
            description=problem.get('math_essence','')[:220],difficulty=problem['difficulty'],judge='externo' if problem.get('external') else 'local',source=problem.get('source','AutoTutor')))
    return result


def plan_schema(ids,max_sessions,minutes):
    text={'type':'string','minLength':1,'maxLength':450}
    activity={'type':'object','properties':{'kind':{'type':'string','enum':list(KINDS)},'resource_id':{'anyOf':[{'type':'string','enum':ids},{'type':'null'}]},'minutes':{'type':'integer','minimum':5,'maximum':minutes},'objective':text},'required':['kind','resource_id','minutes','objective'],'additionalProperties':False}
    session={'type':'object','properties':{'title':text,'activities':{'type':'array','items':activity,'minItems':1,'maxItems':4}},'required':['title','activities'],'additionalProperties':False}
    return {'type':'object','properties':{'title':text,'summary':text,'personalization':text,'assumptions':text,'sessions':{'type':'array','items':session,'minItems':1,'maxItems':max_sessions}},'required':['title','summary','personalization','assumptions','sessions'],'additionalProperties':False}


def _text(value):return isinstance(value,str) and 1<=len(value.strip())<=1200 and not re.search(r'https?://',value)


def generate_plan(llm,prefs,attempts,history,completed,previous=None,feedback=''):
    # Revalidate persisted preferences before dates or a provider call.
    prefs=preferences(**{k:prefs[k] for k in ('topic','goal','base_topic','style','minutes','weekdays','start_date','max_weeks')})
    candidates=candidate_resources(prefs)
    if llm.provider=='Ollama':
        limits={'aula':2,'artigo':2,'video':2,'problema':6};counts={};selected=[]
        for resource in candidates:
            kind=resource['kind']
            if counts.get(kind,0)>=limits.get(kind,1):continue
            selected.append(dict(resource,description=resource.get('description','')[:180]));counts[kind]=counts.get(kind,0)+1
        candidates=selected
    by_id={r['id']:r for r in candidates};dates=available_dates(prefs)
    maximum=min(len(dates),8 if llm.provider=='Ollama' else 24)
    evidence=[{k:s[k] for k in ('id','answered','correct','distinct_problems','accepted_problems')} for s in learning_stats(attempts,history) if s['answered'] or s['submissions']]
    prompt={'preferences':prefs,'maximum_sessions':maximum,'evidence':evidence,'read_lessons':completed,'resources':candidates,'feedback':feedback[:1200]}
    if previous:prompt['previous_progress']={'title':previous.get('title','')[:180],'completed_count':len(previous.get('completed',[])),'completed':[x[:140] for x in previous.get('completed',[])[-10:]]}
    response=llm.complete('Você planeja uma trilha de programação competitiva em português. '
        'A IA deve estimar o número de sessões e os minutos de cada atividade, dentro da disponibilidade do aluno. '
        'Personalize conforme a preferência de aprender com problemas, teoria ou vídeos; explique a escolha. '
        'Comece pelos pré-requisitos realmente necessários e intercale teoria, artigos, vídeos disponíveis, problemas e revisão. '
        'Use SOMENTE IDs do catálogo recebido, respeitando o tipo do recurso. Não invente links, testes ou resultados do aluno. '
        'O tipo revisao pode ter resource_id=null. Inclua aula/artigo e problema quando disponíveis; inclua vídeo quando disponível. '
        'Cada sessão precisa caber no orçamento diário. Se o tema exceder o horizonte, explicite o recorte e a incerteza. '
        'Prefira uma primeira etapa pequena e viável, com até 10 sessões quando isso bastar. '
        'Não trate marcações de estudo como domínio. Ao adaptar, concentre-se no que falta, preservando o histórico. '
        'Retorne apenas JSON, com title, summary, personalization, assumptions e sessions; cada sessão tem title e activities; '
        'cada atividade tem kind, resource_id, minutes e objective. Não retorne datas nem URLs: o sistema aplica o calendário e os links reais.',
        json.dumps(prompt,ensure_ascii=False,separators=(',',':')),plan_schema(list(by_id),maximum,prefs['minutes']),include_history=False)
    valid=isinstance(response,dict) and all(_text(response.get(k)) for k in ('title','summary','personalization','assumptions'))
    sessions=response.get('sessions') if isinstance(response,dict) else None
    valid=valid and isinstance(sessions,list) and 1<=len(sessions)<=maximum
    used=set()
    if valid:
        for session in sessions:
            if not isinstance(session,dict) or not _text(session.get('title')) or not isinstance(session.get('activities'),list) or not 1<=len(session['activities'])<=4:valid=False;break
            total=0
            for activity in session['activities']:
                if not isinstance(activity,dict) or not isinstance(activity.get('kind'),str) or activity.get('kind') not in KINDS or type(activity.get('minutes')) is not int or not 5<=activity['minutes']<=prefs['minutes'] or not _text(activity.get('objective')):valid=False;break
                rid=activity.get('resource_id')
                if activity['kind']=='revisao' and rid is None:pass
                elif not isinstance(rid,str) or rid not in by_id or by_id[rid]['kind']!=activity['kind']:valid=False;break
                total+=activity['minutes'];used.add(activity['kind'])
            if total>prefs['minutes']:valid=False
            if not valid:break
    if any(r['kind'] in ('aula','artigo') for r in candidates) and not used.intersection(('aula','artigo')):valid=False
    for required in ('video','problema'):
        if any(r['kind']==required for r in candidates) and required not in used:valid=False
    if not valid:
        llm.report_fallback('A IA retornou uma trilha incompleta, com recurso inválido ou tempo acima da sua disponibilidade. Nenhuma trilha por regras foi criada.')
        raise AIUnavailable('A IA não produziu uma trilha válida.')
    for day,session in zip(dates,sessions):
        session['date']=day;session['minutes']=sum(a['minutes'] for a in session['activities'])
    return dict(response,preferences=prefs,resources=candidates,provider=llm.provider,model=llm.model,
                source=llm.provider+' · '+llm.model,estimated_minutes=sum(s['minutes'] for s in sessions),
                start_date=sessions[0]['date'],end_date=sessions[-1]['date'],feedback=feedback,version=1)


def plan_markdown(plan):
    by_id={r['id']:r for r in plan['resources']}
    result='# '+plan['title']+'\n\n'+plan['summary']+'\n\n'+plan['personalization']+'\n\nEstimativa: '+str(plan['estimated_minutes'])+' minutos, de '+plan['start_date']+' a '+plan['end_date']+'.\n\n'+plan['assumptions']
    for session in plan['sessions']:
        result+='\n\n## '+session['date']+' · '+session['title']+'\n'
        for activity in session['activities']:
            resource=by_id.get(activity['resource_id']);name=resource['title'] if resource else 'Revisão ativa'
            if resource and resource.get('url','').startswith('https://'):name='['+name+']('+resource['url']+')'
            result+='\n- '+KINDS[activity['kind']]+' · '+str(activity['minutes'])+' min · '+name+': '+activity['objective']
    return result


class TopicPlans:
    def __init__(self,store):
        self.store=store
        with store.connect() as db:db.execute('CREATE TABLE IF NOT EXISTS topic_plan_progress (profile_id TEXT NOT NULL,plan_id TEXT NOT NULL,session_index INTEGER NOT NULL,activity_index INTEGER NOT NULL,completed INTEGER NOT NULL,updated_at TEXT NOT NULL,PRIMARY KEY(profile_id,plan_id,session_index,activity_index))')

    def list(self,profile_id):return self.store.artifacts(profile_id,kind='topic_plan',limit=100)

    def get(self,profile_id,plan_id):
        self.store.validate_id(profile_id)
        with self.store.connect() as db:row=db.execute("SELECT id,payload FROM artifacts WHERE id=? AND profile_id=? AND kind='topic_plan'",(plan_id,profile_id)).fetchone()
        if not row:raise PermissionError('Esta trilha não pertence a esta conta.')
        return json.loads(row[1])

    def save(self,profile_id,plan,parent_id=None):
        if parent_id:self.get(profile_id,parent_id)
        value=dict(plan,content=plan_markdown(plan),concept=plan['preferences']['topic'],parent_id=parent_id,
                   references=[dict(r,publisher=r.get('source','')) for r in plan['resources'] if r.get('url','').startswith('https://')])
        return self.store.add_artifact(profile_id,'topic_plan',plan['title'],value)

    def progress(self,profile_id,plan_id):
        self.get(profile_id,plan_id)
        with self.store.connect() as db:rows=db.execute('SELECT session_index,activity_index,completed FROM topic_plan_progress WHERE profile_id=? AND plan_id=?',(profile_id,plan_id)).fetchall()
        return {(r[0],r[1]):bool(r[2]) for r in rows}

    def set_completed(self,profile_id,plan_id,session_index,activity_index,completed):
        plan=self.get(profile_id,plan_id)
        if type(session_index) is not int or type(activity_index) is not int or not 0<=session_index<len(plan['sessions']) or not 0<=activity_index<len(plan['sessions'][session_index]['activities']) or type(completed) is not bool:raise ValueError('Atividade inválida.')
        with self.store.connect() as db:db.execute('INSERT OR REPLACE INTO topic_plan_progress VALUES (?,?,?,?,?,?)',(profile_id,plan_id,session_index,activity_index,int(completed),self.store.now()))
