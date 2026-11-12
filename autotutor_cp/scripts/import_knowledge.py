"""Import pinned, licensed tutorial sources into the shared compact RAG database."""
import argparse
from collections import Counter
from datetime import datetime,timezone
import gzip
import hashlib
import html
import json
from pathlib import Path
import re
import sys
from urllib.parse import urljoin
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core.knowledge import KnowledgeBase,normalize

REPOS={
 'cp-algorithms/cp-algorithms':dict(source='CP-Algorithms',license='CC BY-SA 4.0',license_url='https://creativecommons.org/licenses/by-sa/4.0/',authors='CP-Algorithms contributors'),
 'cpinitiative/usaco-guide':dict(source='USACO Guide / CP Initiative',license='CC BY-NC-SA 4.0',license_url='https://creativecommons.org/licenses/by-nc-sa/4.0/',authors='USACO Guide contributors')}
LEVELS={'1_General':'general','2_Bronze':'bronze','3_Silver':'silver','4_Gold':'gold','5_Plat':'plat','6_Advanced':'adv'}
TOPICS={
 'adhoc':('ad hoc','ad-hoc','adhoc','implementation','simulation','complete search','intro cp','input output'),
 'structures':('data structures','data structure','arrays','array','sets','stack','queue','fenwick','segment tree','sparse table'),
 'prefix':('prefix sums','prefix sum','partial sums','difference array'),
 'binary':('binary search','two pointers','sliding window'),
 'sorting':('sorting','sort','comparators','coordinate compression'),
 'graph':('graph','dijkstra','breadth first','depth first','bfs','dfs','flood fill','shortest path','topological','connected component'),
 'tree':('tree','trees','binary lifting','euler tour','lca','lowest common ancestor'),
 'dp':('dynamic programming','intro dp','knapsack','memoization','recurrence','dp '),
 'greedy':('greedy','scheduling'),
 'math':('algebra','combinator','euclid','divisib','number theory','sieve','modular','exponentiation','gcd','prime'),
 'strings':('string','suffix','prefix function','kmp','z function','hashing'),
 'geometry':('geometry','polygon','convex','intersection')}
BASE_NAMES={'breadth-first-search','depth-first-search','intro-to-dp','binary_search','binary-search','euclid-algorithm','binary-exp',
 'primality_tests','sieve-of-eratosthenes','disjoint_set_union','topological-sort','dijkstra','dijkstra_sparse',
 'minimum-spanning-tree-kruskal','minimum-spanning-tree-prim','knapsack','mex','stack_queue_modification'}


def frontmatter(text):
    match=re.match(r'\A---\s*\n(.*?)\n---\s*\n',text,re.S)
    if not match:return {},text
    # Only extract scalar metadata; never execute YAML tags or MDX imports.
    values={}
    for key,value in re.findall(r'^(id|title|author|description):[ \t]*(.*)$',match.group(1),re.M):
        values[key]=value.strip().strip('\"\'')
    return values,text[match.end():]


def remove_components(text,names):
    for name in names:
        # Remove nested component blocks without treating downloaded source as code.
        pattern=re.compile(r'<(/?)'+re.escape(name)+r'\b[^>]*>',re.S)
        depth=0;start=None;spans=[]
        for match in pattern.finditer(text):
            if not match.group(1):
                if depth==0:start=match.start()
                if match.group(0).rstrip().endswith('/>'):
                    if depth==0:spans.append((match.start(),match.end()));start=None
                else:depth+=1
            elif depth:
                depth-=1
                if depth==0:spans.append((start,match.end()));start=None
        if depth and start is not None:spans.append((start,len(text)))
        for start,end in reversed(spans):text=text[:start]+'\n'+text[end:]
    return text


def clean_markdown(text,url,source_url,usaco=False):
    protected=[]
    def protect(match):
        protected.append(match.group(0));return 'RAGPROTECTEDTOKEN'+str(len(protected)-1)+'ENDTOKEN'
    text=re.sub(r'```[^\n]*\n.*?```|\$\$.*?\$\$|\$(?:\\.|[^$\n])+\$',protect,text,flags=re.S)
    text=re.sub(r'<!--.*?-->','',text,flags=re.S)
    text=re.sub(r'<YouTube\b[^>]*?\bid\s*=\s*[\"\']([^\"\']+)[\"\'][^>]*/>',lambda m:'\n[Vídeo recomendado na fonte](https://www.youtube.com/watch?v='+m.group(1)+')\n',text,flags=re.I|re.S)
    text=remove_components(text,['Spoiler','Problems','Resources','FocusProblem'])
    if usaco:
        # Published problem editorials and third-party quoted excerpts are outside this tutorial pack.
        text=re.sub(r'^>.*(?:\n>.*)*','',text,flags=re.M)
        lines=text.splitlines(keepends=True);kept=[];skip=None
        for line in lines:
            match=re.match(r'^(#{1,6})\s+(.+)',line)
            if match:
                depth=len(match.group(1));title=match.group(2).strip().lower()
                if skip is not None and depth<=skip:skip=None
                if re.match(r'(?:solution|solutions|video solution|practice problems|problemset)\b',title):skip=depth
            if skip is None:kept.append(line)
        text=''.join(kept)
    text=re.sub(r'^\s*(?:import|export)\s+[^\n]+\n','',text,flags=re.M)
    text=re.sub(r'\{%.*?%\}','',text,flags=re.S)
    text=re.sub(r'<\/?[A-Za-z][^>]*>','',text)
    text=re.sub(r'RAGPROTECTEDTOKEN(\d+)ENDTOKEN',lambda m:protected[int(m.group(1))],text)
    text=re.sub(r'```[^\n]*\n(.*?)```',lambda m:'' if re.search(r'#\s*include|\bmain\s*\(',m.group(1)) else m.group(0),text,flags=re.S)
    def link(m):
        title,destination=m.group(1),m.group(2)
        if destination.startswith(('http://','https://','#','mailto:')):return m.group(0)
        if destination.endswith(('.md','.mdx')):absolute=urljoin(source_url,destination)
        else:absolute=urljoin(url,destination)
        return '['+title+']('+absolute+')'
    text=re.sub(r'!?\[([^\]\n]*)\]\(([^\s)]+)\)',link,text)
    text=re.sub(r'\n{3,}','\n\n',text)
    return html.unescape(text).strip()


def classify(title,path):
    value=normalize(title+' '+path.replace('_',' ').replace('-',' '))
    topics=[topic for topic,terms in TOPICS.items() if any(term in value for term in terms)]
    return topics or ['fundamentals']


def from_sources(root):
    manifest=json.loads((root/'manifest.json').read_text());records=[];skipped=[]
    for record in manifest:
        repo,path,revision=record['repo'],record['path'],record['revision']
        if repo not in REPOS or not path.endswith(('.md','.mdx')) or path=='README.md':continue
        if record['status']=='error':skipped.append(dict(path=path,reason='download failed'));continue
        usaco=repo.startswith('cpinitiative/')
        if not usaco and Path(path).stem in ('index','navigation','contrib','code_of_conduct','tags'):continue
        if usaco and any(x in path for x in ('Adding_Solution','Contributing','Editor','Contributors','cp-resources')):continue
        meta,text=frontmatter((root/repo/path).read_text())
        title=meta.get('title') or next(iter(re.findall(r'^#\s+(.+)$',text,re.M)),Path(path).stem.replace('-',' ').replace('_',' '))
        source_url=f'https://github.com/{repo}/blob/{revision}/{path}'
        if usaco:
            if not meta.get('id'):skipped.append(dict(path=path,reason='no public module ID'));continue
            level=LEVELS.get(Path(path).parts[1],'general');url='https://usaco.guide/'+level+'/'+meta['id']
            track='Base' if level in ('general','bronze','silver') or Path(path).stem in ('Intro_DP','Knapsack_DP') else 'Complementar'
        else:
            url='https://cp-algorithms.com/'+path.removeprefix('src/').removesuffix('.md')+'.html'
            track='Base' if Path(path).stem in BASE_NAMES else 'Complementar'
        body=clean_markdown(text,url,source_url,usaco)
        if len(body)<350 or len(re.findall(r'\w+',body))<55:
            skipped.append(dict(path=path,reason='too little tutorial prose after cleaning'));continue
        topics=classify(title,path)
        records.append(dict(REPOS[repo],url=url,source_url=source_url,title=title,authors=meta.get('author') or REPOS[repo]['authors'],language='en',revision=revision,
            kind='article',track=track,topics=topics,tags=topics+[normalize(title)],content=body,
            adaptation='Conversão automática de Markdown/MDX para texto de estudo; removidos componentes, blocos de solução de problemas e programas completos. Ilustrações mantidas como links. Não é tradução nem revisão pedagógica integral.'))
    return records,skipped


def local_lessons():
    from core.learning_engine import load_curriculum,lesson_markdown
    from core.library import deep_guides
    records=[]
    for topic in load_curriculum():
        records.append(dict(title=topic['title']+' · Aula introdutória',url='autotutor://aulas/'+topic['id'],source='AutoTutor · material autoral',authors='AutoTutor-CP',
            license='Material autoral do projeto',license_url='',language='pt-BR',kind='lesson',track='Base',topics=[topic['id']],tags=[topic['id'],topic['title']],revision='local-v1',
            content=lesson_markdown(topic),adaptation='Aula já incluída no projeto, agora indexada para consulta pelo RAG.'))
    for guide in deep_guides():
        body='# '+guide['title']+'\n\n'+'\n\n'.join('## '+s['title']+'\n'+s['body'] for s in guide['sections'])
        records.append(dict(title=guide['title'],url='autotutor://guias/'+guide['topic_id'],source='AutoTutor · material autoral',authors=guide.get('author','AutoTutor-CP'),
            license='Material autoral do projeto',license_url='',language='pt-BR',kind='guide',track='Base',topics=[guide['topic_id']],tags=[guide['topic_id'],guide['title']],revision='local-v1',content=body,
            adaptation='Guia já incluído no projeto, agora indexado para consulta pelo RAG.'))
    adhoc=Path(__file__).resolve().parents[1]/'data'/'basics_adhoc.md'
    if adhoc.exists():records.append(dict(title='Ad hoc e implementação: do enunciado ao algoritmo',url='autotutor://aulas/adhoc',source='AutoTutor · material autoral',authors='AutoTutor-CP',license='Material autoral do projeto',license_url='',language='pt-BR',kind='lesson',track='Base',topics=['adhoc','fundamentals'],tags=['adhoc','ad hoc','implementacao','simulation'],revision='local-v1',content=adhoc.read_text(),adaptation='Introdução autoral de apoio às referências USACO Guide.'))
    return records


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--sources',type=Path);parser.add_argument('--database',type=Path);parser.add_argument('--export',type=Path);parser.add_argument('--import-json',type=Path)
    args=parser.parse_args();kb=KnowledgeBase(args.database);skipped=[]
    if args.import_json:
        opener=gzip.open if str(args.import_json).endswith('.gz') else open
        with opener(args.import_json,'rt',encoding='utf-8') as stream:payload=json.load(stream)
        if payload.get('schema_version')!=1 or not isinstance(payload.get('documents'),list):raise ValueError('Pacote JSON inválido.')
        documents=payload['documents']
    else:
        if not args.sources:parser.error('Informe --sources ou --import-json.')
        documents,skipped=from_sources(args.sources);documents+=local_lessons()
    result=kb.import_documents(documents)
    report=dict(imported_at=datetime.now(timezone.utc).isoformat(),result=result,stats=kb.stats(),skipped=skipped)
    if args.export:report['export']=kb.export_json(args.export)
    output=kb.path.with_suffix('.import.json');output.write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
