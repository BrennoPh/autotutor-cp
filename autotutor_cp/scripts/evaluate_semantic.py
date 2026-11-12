"""Optional embedding experiment on external full text; never changes production search."""
import json,re,time,sys,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import requests
from core.knowledge import KnowledgeBase

CASES=[
 ('BFS','breadth.first|graph traversal'),('DFS','depth.first|graph traversal'),
 ('soma de prefixos','prefix sum'),('programação dinâmica','dynamic programming|introduction to dp'),
 ('Segment Tree','segment tree|point update range sum'),('busca binária','binary search'),
 ('menor quantidade de arestas para chegar a cada vértice sem pesos','breadth.first'),
 ('guardar respostas dos subproblemas para não recalcular','dynamic programming|introduction to dp'),
 ('calcular total entre duas posições de uma lista imutável','prefix sum'),
 ('mudar um elemento e consultar a soma de um intervalo','segment tree|point update range sum'),
 ('percorrer vizinhos até o fim e depois voltar no grafo','depth.first'),
 ('encontrar o primeiro valor que satisfaz uma condição monótona','binary search')]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--model',default='all-minilm:22m');parser.add_argument('--output',type=Path,default=Path('.runtime/semantic-comparison.json'));args=parser.parse_args()
    kb=KnowledgeBase();s=requests.Session();s.trust_env=False
    with kb.read() as db:documents=[kb._document(r,True) for r in db.execute("SELECT * FROM knowledge_documents WHERE url LIKE 'https://%' AND kind NOT IN ('reference','video_reference','problem_reference') ORDER BY id")]
    def embed(texts):
        r=s.post('http://127.0.0.1:11434/api/embed',json={'model':args.model,'input':texts,'keep_alive':0,'options':{'num_thread':2,'num_batch':128}},timeout=(3,90));r.raise_for_status()
        matrix=np.asarray(r.json()['embeddings'],dtype=np.float32)
        return matrix/np.maximum(np.linalg.norm(matrix,axis=1,keepdims=True),1e-8)
    start=time.monotonic();vectors=[]
    for i in range(0,len(documents),16):
        vectors.append(embed([d['title']+'\n'+d['content'][:1200] for d in documents[i:i+16]]));print('indexados',min(i+16,len(documents)),flush=True)
    matrix=np.vstack(vectors);queries=embed([q for q,_ in CASES]);checks=[]
    for (query,pattern),vector in zip(CASES,queries):
        semantic=[documents[int(i)] for i in np.argsort(-(matrix@vector))[:10]]
        lexical=kb.search(query,limit=10,per_document=1,external_only=True,content_only=True,prefer_foundation=True)
        scores={};by_id={}
        for group in (semantic,lexical):
            for i,d in enumerate(group):scores[d['id']]=scores.get(d['id'],0)+1/(60+i);by_id[d['id']]=d
        hybrid=[by_id[k] for k in sorted(scores,key=scores.get,reverse=True)]
        check={'query':query}
        for name,items in [('lexical',lexical),('semantic',semantic),('hybrid',hybrid)]:
            titles=[d['title'] for d in items[:3]];check[name]={'titles':titles,'hit_at_3':any(re.search(pattern,t,re.I) for t in titles)}
        checks.append(check)
    totals={name:sum(c[name]['hit_at_3'] for c in checks) for name in ('lexical','semantic','hybrid')}
    report={'model':args.model,'documents':len(documents),'checks':checks,'totals':totals,'total_queries':len(CASES),'seconds':round(time.monotonic()-start,2),'embedding_bytes':matrix.nbytes,'production_enabled':False,'decision':'Busca lexical permanece padrão. Avaliação pequena; conferir qualidade e desempenho antes de ativar embeddings.','scope':'Representações por título e início do documento; comparação tópica em português, não qualidade das respostas.'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2))
    np.savez_compressed(args.output.with_suffix('.npz'),vectors=matrix,ids=np.asarray([d['id'] for d in documents]))
    print(totals,flush=True)

if __name__=='__main__':main()
