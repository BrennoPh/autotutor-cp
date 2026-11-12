"""Persistent personal library over existing artifacts, with curated and unverified links."""
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit
import hashlib
import json
import re
from core.learning_engine import load_curriculum

DATA=Path(__file__).resolve().parents[1]/'data'
KINDS={'topic_plan':'Trilha por assunto','learning_analysis':'Análise de aprendizado','class_analysis':'Análise de turma','material':'Material de estudo','helper':'Orientação de código','feedback':'Diagnóstico de solução','problem':'Problema gerado','recommendations':'Recomendações','resource':'Referência salva'}
STATUSES=['Quero estudar','Estudando','Estudado']


@lru_cache(maxsize=1)
def resources():return json.loads((DATA/'study_resources.json').read_text(encoding='utf-8'))['resources']


@lru_cache(maxsize=1)
def deep_guides():return json.loads((DATA/'deep_guides.json').read_text(encoding='utf-8'))['guides']


def clear_cache():
    """Clear cached resources and guides."""
    resources.cache_clear()
    deep_guides.cache_clear()


def references_for(concept,limit=6):
    topic=next((t['id'] for t in load_curriculum() if t['id']==concept or t['title']==concept),None)
    candidates=[r for r in resources() if topic in r['topics']]
    candidates.sort(key=lambda r:(r['kind']!='Artigo',r['kind']!='Vídeo',r['title']))
    articles=[r for r in candidates if r['kind']=='Artigo'][:3]
    videos=[r for r in candidates if r['kind']=='Vídeo'][:2]
    return (articles+videos+[r for r in candidates if r not in articles+videos])[:limit]


def references_for_query(query,limit=5,exclude_urls=()):
    """Recommend topic-matched links; metadata is never theoretical evidence."""
    from core.knowledge import KnowledgeBase,query_tokens
    terms=set(query_tokens(query));candidates=[];seen=set(exclude_urls)
    if not terms:return []
    kb=KnowledgeBase()
    for item in kb.search(query,limit=30,per_document=1,external_only=True,reference_only=True):
        candidates.append(dict(title=item['title'],url=item['url'],publisher=item['source'],
            kind='Vídeo' if item.get('kind')=='video_reference' else 'Problema' if item.get('kind')=='problem_reference' else 'Referência',
            verification='Referência indexada; texto completo não consultado',score=item['score']))
    for item in resources():
        words=set(query_tokens(item['title']+' '+' '.join(item.get('topics',[]))+' '+item.get('description','')))
        score=len(terms & words)
        if score:candidates.append(dict(item,score=score))
    candidates.sort(key=lambda r:r['score'],reverse=True)
    video=next((r for r in candidates if r['kind']=='Vídeo' and r['url'] not in seen),None)
    if video:candidates=[video]+[r for r in candidates if r is not video]
    result=[];seen_titles=set()
    for item in candidates:
        title_key=(item['title'].casefold(),item.get('publisher',''))
        if item['url'] in seen or title_key in seen_titles or not safe_url(item['url']):continue
        seen.add(item['url']);seen_titles.add(title_key);result.append({k:v for k,v in item.items() if k!='score'})
        if len(result)>=limit:break
    return result


def safe_url(value):
    if not isinstance(value,str) or len(value)>2000:return None
    value=value.strip()
    try:p=urlsplit(value)
    except ValueError:return None
    if p.scheme!='https' or not p.hostname or p.username or p.password or any(c in value for c in ('\n','\r',' ','<','>','"')):return None
    return value


def content_links(content,attached=()):
    curated={r['url'].rstrip('/'):r for r in resources()};found={}
    for r in attached:
        if isinstance(r,dict) and safe_url(r.get('url')):found[r['url']]=curated.get(r['url'].rstrip('/'),dict(r,verification='Link gerado ou informado; não verificado'))
    for title,url in re.findall(r'\[([^\]\n]+)\]\((https://[^\s)]+)\)',content or ''):
        if safe_url(url):found[url]=curated.get(url.rstrip('/'),dict(title=title,url=url,kind='Link',verification='Link gerado ou informado; não verificado'))
    return list(found.values())


def study_entry(item):
    """Only expose educational fields. Generated reference solutions stay private."""
    value=item['payload'];kind=item['kind'];content=value.get('content','');topic=value.get('concept') or value.get('topic','')
    if kind=='problem':content=value.get('statement','');topic=value.get('topic','')
    elif kind=='resource':content=value.get('summary','')
    elif kind=='recommendations':
        content='\n\n'.join('### '+r['title']+'\n'+r.get('reason','') for r in value.get('items',[]))
    if kind=='helper' and item['title'].startswith('Anotações'):content='```cpp\n'+content+'\n```'
    links=content_links(content,value.get('references',[]))
    if kind=='resource' and safe_url(value.get('url')):links=content_links('',[value])
    if not links and topic:links=references_for(topic)
    return dict(id=item['id'],title=item['title'],kind=KINDS[kind],content=content,topic=topic,
                source=value.get('source',value.get('origin','Registro local')),time=item['time'],links=links,
                problem_id=value.get('id') if kind=='problem' else value.get('problem_id'),
                learning_request=value.get('learning_request',''),preferences=value.get('preferences',{}),
                recommendations=value.get('items',[]) if kind=='recommendations' else [])


class Library:
    def __init__(self,store):
        self.store=store
        with store.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS library_state (profile_id TEXT NOT NULL,item_id TEXT NOT NULL,status TEXT NOT NULL,note TEXT NOT NULL,updated_at TEXT NOT NULL,PRIMARY KEY(profile_id,item_id))')

    def page(self,profile_id,search='',kind=None,status=None,page=1,page_size=12):
        self.store.validate_id(profile_id)
        if kind and kind not in KINDS:raise ValueError('Tipo inválido.')
        if status and status not in STATUSES:raise ValueError('Situação inválida.')
        if page<1 or not 1<=page_size<=50:raise ValueError('Página inválida.')
        where='a.profile_id=? AND a.kind IN ('+','.join('?' for _ in KINDS)+')';args=[profile_id,*KINDS]
        if kind:where+=' AND a.kind=?';args.append(kind)
        if search:
            escaped=search[:200].replace('\\','\\\\').replace('%','\\%').replace('_','\\_')
            where+=" AND (a.title LIKE ? ESCAPE '\\' OR a.payload LIKE ? ESCAPE '\\')";args.extend(['%'+escaped+'%']*2)
        if status:where+=" AND COALESCE(s.status,'Quero estudar')=?";args.append(status)
        query=' FROM artifacts a LEFT JOIN library_state s ON s.profile_id=a.profile_id AND s.item_id=a.id WHERE '+where
        with self.store.connect() as db:
            total=db.execute('SELECT COUNT(*)'+query,args).fetchone()[0]
            rows=db.execute('SELECT a.id,a.kind,a.title,a.payload,a.created_at,COALESCE(s.status,\'Quero estudar\'),COALESCE(s.note,\'\')'+query+' ORDER BY a.rowid DESC LIMIT ? OFFSET ?',args+[page_size,(page-1)*page_size]).fetchall()
        return dict(total=total,items=[dict(id=r[0],kind=r[1],title=r[2],payload=json.loads(r[3]),time=r[4],status=r[5],note=r[6]) for r in rows])

    def get_state(self,profile_id,item_id):
        self.store.validate_id(profile_id)
        with self.store.connect() as db:row=db.execute('SELECT status,note FROM library_state WHERE profile_id=? AND item_id=?',(profile_id,item_id)).fetchone()
        return dict(status=row[0],note=row[1]) if row else dict(status=STATUSES[0],note='')

    def set_state(self,profile_id,item_id,status,note=''):
        self.store.validate_id(profile_id)
        if status not in STATUSES or len(note)>4000:raise ValueError('Situação ou anotação inválida.')
        public={r['id'] for r in resources()}|{g['id'] for g in deep_guides()}
        if item_id.startswith('kb_'):
            from core.knowledge import KnowledgeBase
            if KnowledgeBase().get(item_id):public.add(item_id)
        with self.store.connect() as db:
            if item_id not in public and not db.execute('SELECT 1 FROM artifacts WHERE profile_id=? AND id=? AND kind IN ('+','.join('?' for _ in KINDS)+')',(profile_id,item_id,*KINDS)).fetchone():raise PermissionError('Conteúdo não pertence à sua biblioteca.')
            db.execute('INSERT INTO library_state VALUES (?,?,?,?,?) ON CONFLICT(profile_id,item_id) DO UPDATE SET status=excluded.status,note=excluded.note,updated_at=excluded.updated_at',(profile_id,item_id,status,note,self.store.now()))
        from core.learner_memory import LearnerMemory
        LearnerMemory(self.store).capture(profile_id,'biblioteca',f'Conteúdo marcado como {status}',f'Item: {item_id}. Anotação: {note}',item_id+'|'+status+'|'+hashlib.sha256(note.encode()).hexdigest()[:12])

    def save_resource(self,profile_id,resource):
        self.store.validate_id(profile_id);url=safe_url(resource.get('url'))
        if not url or not 1<=len(resource.get('title','').strip())<=200:raise ValueError('Informe título e um link HTTPS válido.')
        identifier=hashlib.sha256((profile_id+'|resource|'+url).encode()).hexdigest()
        clean={k:resource[k] for k in ('title','url','kind','publisher','summary','verification','source_url','checked') if k in resource}
        clean.update(url=url,source='Referência salva',verification=resource.get('verification','Link informado pelo aluno; não verificado'))
        with self.store.connect() as db:db.execute('INSERT OR IGNORE INTO artifacts VALUES (?,?,?,?,?,?)',(identifier,profile_id,'resource',resource['title'].strip(),json.dumps(clean,ensure_ascii=False),self.store.now()))
        return identifier
