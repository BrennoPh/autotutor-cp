"""Chunk-level lexical/dense/hybrid retrieval with optional diversity and metadata.

    Metadata alignment uses editorial keyword weak labels, not trained relevance.
    No ranking-quality metric is emitted without explicit relevance judgments.
"""
from pathlib import Path
import hashlib,json,re,time
import numpy as np
import requests
from core.knowledge import KnowledgeBase,normalize,query_tokens
from core.research.competencies import graph
from core.research.provider import ResearchError

def corpus(kb):
    with kb.read() as db:
        rows=db.execute("SELECT d.*,c.id chunk_id,c.start_offset,c.end_offset,c.heading FROM knowledge_documents d JOIN knowledge_chunks c ON c.document_id=d.id WHERE d.url LIKE 'https://%' AND d.kind NOT IN ('reference','video_reference','problem_reference') ORDER BY d.id,c.position").fetchall()
    texts={};items=[]
    for row in rows:
        doc=kb._document(row,True) if row['id'] not in texts else texts[row['id']]
        texts[row['id']]=doc
        content=re.sub(r'```.*?```','',doc['content'][row['start_offset']:row['end_offset']],flags=re.S).strip()
        if len(content)<100 or re.search(r'#\s*include|\bmain\s*\(',content):continue
        items.append({'id':doc['id'],'chunk_id':row['chunk_id'],'title':doc['title'],'heading':row['heading'],'url':doc['url'],'license':doc['license'],
            'checksum':doc['checksum'],'excerpt':content,'source':doc['source']})
    return items

def reciprocal_rank_fusion(groups,k=60):
    scores={};items={}
    for group in groups:
        for i,item in enumerate(group,1):
            key=(item['id'],item['chunk_id']);scores[key]=scores.get(key,0)+1/(k+i);items[key]=item
    return [dict(items[key],retrieval_score=scores[key]) for key in sorted(scores,key=scores.get,reverse=True)]

def term_set(text):return set(query_tokens(text))
def similarity(a,b):
    aa,bb=term_set(a),term_set(b)
    return len(aa&bb)/max(1,len(aa|bb))

def diversify(items,limit=3,weight=.7):
    pool=list(items);selected=[]
    if not pool:return []
    best=max(float(x.get('retrieval_score',1)) for x in pool) or 1
    while pool and len(selected)<limit:
        chosen=max(pool,key=lambda x:weight*float(x.get('retrieval_score',1))/best-(1-weight)*max([similarity(x['excerpt'],y['excerpt']) for y in selected] or [0]))
        selected.append(chosen);pool.remove(chosen)
    return selected

class DenseIndex:
    def __init__(self,items,cache=None,embed=None):
        self.items=items;self.model='all-minilm:22m';self.embed=embed or self._embed
        self.path=Path(cache or Path(__file__).resolve().parents[2]/'.runtime/research/dense.npz')
        self.digest=hashlib.sha256(json.dumps([(x['id'],x['chunk_id'],x['checksum']) for x in items]).encode()).hexdigest()
        self.vectors=None
    def _embed(self,texts):
        with requests.Session() as session:
            session.trust_env=False
            response=session.post('http://127.0.0.1:11434/api/embed',json={'model':self.model,'input':texts,'keep_alive':0,'options':{'num_thread':2,'num_batch':128}},timeout=(3,60))
            response.raise_for_status();m=np.asarray(response.json()['embeddings'],dtype=np.float32)
        return m/np.maximum(np.linalg.norm(m,axis=1,keepdims=True),1e-8)
    def build(self):
        if self.path.exists():
            with np.load(self.path,allow_pickle=False) as data:
                if str(data['digest'])==self.digest and str(data['model'])==self.model:self.vectors=data['vectors'];return
        arrays=[]
        for i in range(0,len(self.items),24):arrays.append(self.embed([x['title']+'\n'+x['heading']+'\n'+x['excerpt'][:1600] for x in self.items[i:i+24]]))
        if not arrays:raise ResearchError('Corpus externo vazio.')
        self.vectors=np.vstack(arrays);self.path.parent.mkdir(parents=True,exist_ok=True)
        np.savez_compressed(self.path,vectors=self.vectors,digest=self.digest,model=self.model)
    def search(self,query,k=18):
        if self.vectors is None:self.build()
        vector=self.embed([query])[0];scores=self.vectors@vector
        return [dict(self.items[int(i)],retrieval_score=float(scores[i])) for i in np.argsort(-scores)[:k]]

class ResearchRetriever:
    METHODS=('none','bm25','semantic','hybrid','hybrid_rerank','hybrid_mmr','competencies')
    def __init__(self,kb=None,dense=None):
        self.kb=kb or KnowledgeBase();self.dense=dense;self.last_report={}
    def retrieve(self,query,method='bm25',competencies=(),limit=3,max_chars=2200):
        if method not in self.METHODS:raise ValueError('Método de recuperação inválido.')
        start=time.monotonic()
        if method=='none':self.last_report={'method':method,'seconds':0,'sources':[]};return '',[]
        lexical=self.kb.search(query,limit=18,per_document=2,external_only=True,content_only=True,prefer_foundation=True)
        items=[dict(x,excerpt=x['context_excerpt'],retrieval_score=x['score']) for x in lexical if x['context_excerpt'].strip()]
        if method in ('semantic','hybrid','hybrid_rerank','hybrid_mmr'):
            try:
                if self.dense is None:self.dense=DenseIndex(corpus(self.kb))
                dense=self.dense.search(query)
            except (requests.RequestException,KeyError,ValueError) as exc:raise ResearchError('Embeddings locais indisponíveis; não houve troca silenciosa para BM25.') from exc
            items=dense if method=='semantic' else reciprocal_rank_fusion([items,dense])
        nodes={n['id']:n for n in graph()['nodes']}
        wanted=list(dict.fromkeys([*competencies,*[p for c in competencies if c in nodes for p in nodes[c]['prerequisites']]]))
        def alignment(item):
            text=normalize(item['title']+' '+item['heading']+' '+item['excerpt'])
            return sum(any(normalize(t) in text for t in nodes[c]['terms']) for c in wanted if c in nodes)
        if method=='competencies':
            expanded=query+' '+' '.join(t for c in wanted if c in nodes for t in nodes[c]['terms'])
            items=[dict(x,excerpt=x['context_excerpt'],retrieval_score=x['score']) for x in self.kb.search(expanded,limit=18,external_only=True,content_only=True)]
            items.sort(key=alignment,reverse=True)
        if method=='hybrid_rerank':
            # Explicit lightweight lexical/metadata reranker, not a neural model.
            items.sort(key=lambda x:alignment(x)+similarity(query,x['title']+' '+x['excerpt']),reverse=True)
        unique=[];seen=set()
        for x in items:
            if x['id'] not in seen:unique.append(x);seen.add(x['id'])
        picked=diversify(unique,limit) if method=='hybrid_mmr' else unique[:limit]
        context=[];refs=[];remaining=max_chars
        for item in picked:
            header=f'[{len(refs)+1}] {item["title"]}\n{item["url"]}\nLicença: {item["license"]}\n'
            room=min(max_chars//limit-len(header),remaining-len(header)-2)
            if room<80:continue
            text=item['excerpt'][:room];block=header+text;context.append(block);remaining-=len(block)+2
            refs.append({k:item[k] for k in ('id','chunk_id','title','url','license','retrieval_score')})
        self.last_report={'method':method,'seconds':round(time.monotonic()-start,4),'sources':refs,'context_chars':len('\n\n'.join(context)),
            'competency_labels':'keyword-based weak labels, unreviewed','index_digest':self.dense.digest if self.dense else None,
            'redundancy_jaccard':round(sum(similarity(a['excerpt'],b['excerpt']) for i,a in enumerate(picked) for b in picked[i+1:])/max(1,len(picked)*(len(picked)-1)/2),4)}
        return '\n\n'.join(context),refs

def ranking_metrics(ranked,relevance,k=3,*,reviewed=False,complete=False):
    if not reviewed or not complete:return {'status':'not_evaluated','reason':'Requer julgamentos revisados e universo relevante completo.'}
    positives={i for i,v in relevance.items() if v>0};top=ranked[:k]
    if not positives:raise ValueError('Gabarito sem documentos relevantes.')
    dcg=sum((2**relevance.get(i,0)-1)/np.log2(j+2) for j,i in enumerate(top))
    ideal=sum((2**v-1)/np.log2(j+2) for j,v in enumerate(sorted(relevance.values(),reverse=True)[:k]))
    return {'precision_at_k':len(set(top)&positives)/k,'recall_at_k':len(set(top)&positives)/len(positives),
        'reciprocal_rank':next((1/(j+1) for j,i in enumerate(ranked) if i in positives),0),'ndcg_at_k':float(dcg/ideal) if ideal else 0}
