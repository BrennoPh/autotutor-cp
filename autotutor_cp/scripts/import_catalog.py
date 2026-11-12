"""Refresh public problem metadata. No statements, solutions or tests are copied."""
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit, parse_qs, urlencode, urlunsplit
import requests

ROOT=Path(__file__).resolve().parents[1]


class CSESParser(HTMLParser):
    def __init__(self):
        super().__init__();self.items=[];self.section='';self.heading=False;self.href=None;self.name=''
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag=='h2':self.heading=True;self.section=''
        if tag=='a' and '/problemset/task/' in attrs.get('href',''):
            self.href=attrs['href'];self.name=''
    def handle_data(self, value):
        if self.heading:self.section+=value
        if self.href:self.name+=value
    def handle_endtag(self, tag):
        if tag=='h2':self.heading=False
        if tag=='a' and self.href:
            self.items.append((self.href,self.name.strip(),self.section.strip()));self.href=None


def canonical(url):
    p=urlsplit(url);host=p.netloc.lower().removeprefix('www.')
    if host=='cses.fi' and '/task/' in p.path:return 'https://cses.fi/problemset/task/'+p.path.strip('/').split('/')[-1]
    if host=='usaco.org':
        params=parse_qs(p.query)
        if 'cpid' in params:return 'https://usaco.org/index.php?'+urlencode({'page':'viewproblem2','cpid':params['cpid'][0]})
    return urlunsplit(('https' if p.scheme=='http' else p.scheme,host,p.path.rstrip('/'),p.query,''))


def classify(section):
    name=section.lower().replace('_',' ')
    if any(k in name for k in ('dynamic','dp')):return 'DP'
    if 'tree' in name and 'segment' not in name:return 'Árvores'
    if any(k in name for k in ('graph','flood','flight')):return 'Grafos'
    if any(k in name for k in ('range','prefix')):return 'Prefix Sum'
    if 'binary' in name:return 'Busca Binária'
    if 'greedy' in name:return 'Guloso'
    if any(k in name for k in ('math','geo','number','counting','probability')):return 'Matemática'
    if any(k in name for k in ('string','ds','set','queue','sort')):return 'Estruturas de Dados'
    return 'Fundamentos'


def entry(title,url,section,source,source_url,difficulty='Intermediário',original_difficulty=''):
    url=canonical(url);topic=classify(section)
    return dict(id='external_'+hashlib.sha256(url.encode()).hexdigest()[:16],title=title,url=url,source=source,
        source_url=source_url,section=section,topic=topic,tags=[topic,section],difficulty=difficulty,
        original_difficulty=original_difficulty,difficulty_basis='Estimativa de organização do catálogo; não é rating oficial.',
        external=True,math_essence='Prática do tópico '+topic,core_concepts=[topic],
        approach_summary='A estratégia específica depende do enunciado no juiz original.',
        statement='Problema de '+source+', seção '+section+'. Enunciado e avaliação disponíveis na plataforma de origem.',
        complexity='Consultar enunciado',catalog_checked='2026-10-24')


def fetch(url):
    response=requests.get(url,timeout=40,headers={'User-Agent':'AutoTutorCP-catalog/1.0 (public educational metadata)'})
    response.raise_for_status();return response


def main():
    parser=CSESParser();parser.feed(fetch('https://cses.fi/problemset/').text)
    items={}
    for href,title,section in parser.items:
        difficulty='Iniciante' if section=='Introductory Problems' else ('Avançado' if section in ('Advanced Techniques','Additional Problems II') else 'Intermediário')
        item=entry(title,'https://cses.fi'+href,section,'CSES','https://cses.fi/problemset/',difficulty)
        items[item['url']]=item
    tree=fetch('https://api.github.com/repos/cpinitiative/usaco-guide/git/trees/master?recursive=1').json()['tree']
    paths=sorted(i['path'] for i in tree if i['path'].endswith('.problems.json') and i['path'].startswith(('content/2_Bronze/','content/3_Silver/')))
    def module(path):
        url='https://raw.githubusercontent.com/cpinitiative/usaco-guide/master/'+path
        return path,fetch(url).json()
    with ThreadPoolExecutor(max_workers=4) as pool:
        for path,data in pool.map(module,paths):
            section=path.rsplit('/',1)[-1].replace('.problems.json','').replace('_',' ')
            for value in data.values():
                if not isinstance(value,list):continue
                for problem in value:
                    if not isinstance(problem,dict) or not problem.get('name') or not problem.get('url','').startswith(('https://','http://')):continue
                    url=canonical(problem['url'])
                    if url in items:continue
                    source_url='https://github.com/cpinitiative/usaco-guide/blob/master/'+path
                    difficulty='Iniciante' if '/2_Bronze/' in path else 'Intermediário'
                    item=entry(problem['name'],url,section,'USACO Guide',source_url,difficulty,problem.get('difficulty',''))
                    tags=problem.get('tags',[])
                    if isinstance(tags,list):item['tags']+= [str(tag) for tag in tags]
                    items[url]=item
    if len(items)<500:raise RuntimeError(f'Only {len(items)} unique external problems found; keep the previous catalogue.')
    output={'version':1,'checked':'2026-10-24','count':len(items),'problems':list(items.values())}
    (ROOT/'data'/'external_problems.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'unique_external_problems':len(items),'CSES':sum(i['source']=='CSES' for i in items.values()),
                      'USACO_Guide':sum(i['source']=='USACO Guide' for i in items.values())}))


if __name__=='__main__':main()
