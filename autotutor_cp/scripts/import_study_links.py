"""Index public study metadata; distinguish references from licensed full text.
No login, private endpoints, video downloads, or execution of downloaded JS.
"""
import argparse,json,re,hashlib
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import unquote,urlsplit,urljoin
from xml.etree import ElementTree
import requests
from core.knowledge import KnowledgeBase,query_tokens,canonical_url
from scripts.import_catalog import CSESParser

SOURCES={
 'Maratona UFMG':'https://www.youtube.com/@maratonaufmg2572/videos',
 'CSES':'https://cses.fi/problemset/',
 'USACO Guide':'https://usaco.guide/',
 'Neps Academy':'https://neps.academy/sitemap.xml',
 'YouKn0wWho Academy':'https://youkn0wwho.academy/topic-list',
 'TLE Eliminators':'https://www.tle-eliminators.com/cp-sheet'}

def walk(value):
    if isinstance(value,dict):
        yield value
        for child in value.values():yield from walk(child)
    elif isinstance(value,list):
        for child in value:yield from walk(child)

def reference(title,url,source,source_url,kind='reference',section='',inferred=False):
    title=title.strip()[:300];url=canonical_url(url)
    return dict(title=title,url=url,source=source,source_url=source_url,authors=source,
        license='Metadados públicos; conteúdo original não reproduzido',language='pt-BR' if source in ('Neps Academy','Maratona UFMG') else 'en',
        kind=kind,track='Referências',topics=[],tags=query_tokens(title+' '+section),title_inferred_from_url=inferred,
        content=f'# {title}\nFonte: {source}.\nURL: {url}\nSeção de origem: {section or source_url}.\nRegistro de descoberta para recomendar estudo. Apenas título, endereço e classificação pública foram indexados. Não contém aula, enunciado completo, solução, vídeo ou transcrição. Não usar como evidência teórica.',
        adaptation='Referência de navegação; não é texto completo nem material gerado pela IA.')

def youtube_records(data,url):
    result={}
    for node in walk(data):
        if node.get('contentType')=='LOCKUP_CONTENT_TYPE_VIDEO':
            identifier=node.get('contentId','');title=node.get('metadata',{}).get('lockupMetadataViewModel',{}).get('title',{}).get('content','')
        elif 'videoRenderer' in node:
            v=node['videoRenderer'];identifier=v.get('videoId','');title=''.join(r.get('text','') for r in v.get('title',{}).get('runs',[]))
        else:continue
        if re.fullmatch(r'[\w-]{11}',identifier) and title:result[identifier]=reference(title,'https://www.youtube.com/watch?v='+identifier,'Maratona UFMG',url,'video_reference')
    return list(result.values())

def academy_records(script,source_url):
    """Extract literal public metadata without evaluating JavaScript."""
    stack=[];quoted=False;escaped=False;records={}
    for i,char in enumerate(script):
        if quoted:
            if escaped:escaped=False
            elif char=='\\':escaped=True
            elif char=='"':quoted=False
            continue
        if char=='"':quoted=True
        elif char=='{':stack.append(i)
        elif char=='}' and stack:
            start=stack.pop()
            if i-start>8000:continue
            block=script[start:i+1];fields={}
            for key in ('problem_title','problem_url'):
                match=re.search(r'\b'+key+r':("(?:\\.|[^"\\])*")',block)
                if match:
                    try:fields[key]=json.loads(match[1])
                    except ValueError:pass
            if len(fields)==2 and fields['problem_url'].startswith('https://'):
                url=fields['problem_url'];records[url]=reference(fields['problem_title'],url,'YouKn0wWho Academy',source_url,'problem_reference')
                topics=re.search(r'topics:(\[[^\]]*\])',block)
                if topics:
                    try:records[url]['tags']+=[v.replace('_',' ') for v in json.loads(topics[1]) if isinstance(v,str)]
                    except ValueError:pass
    return list(records.values())

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--database',type=Path,required=True);parser.add_argument('--report',type=Path,required=True);parser.add_argument('--cache',type=Path,required=True)
    args=parser.parse_args();args.cache.mkdir(parents=True,exist_ok=True)
    report={'checked_at':datetime.now(timezone.utc).isoformat(),'sources':[]};docs=[]
    def fetch(url):
        path=args.cache/(hashlib.sha256(url.encode()).hexdigest()+'.html')
        if path.exists():return path.read_text()
        r=requests.get(url,timeout=(5,30),headers={'User-Agent':'AutoTutorCP/1.0 public educational catalogue'});r.raise_for_status()
        if len(r.content)>8_000_000:raise ValueError('Fonte excede tamanho permitido.')
        path.write_text(r.text);return r.text
    for source,url in SOURCES.items():
        found=[];status='referências públicas';detail=''
        try:
            text=fetch(url)
            if source=='CSES':
                parser=CSESParser();parser.feed(text)
                found=[reference(title,'https://cses.fi'+href,source,url,'problem_reference',section) for href,title,section in parser.items]
                detail='Títulos e seções dos problemas; enunciados e testes oficiais não importados.'
            elif source=='Neps Academy':
                tree=ElementTree.fromstring(text)
                for node in tree.iter():
                    if not node.tag.endswith('loc'):continue
                    link=node.text or '';parts=urlsplit(link).path.strip('/').split('/')
                    if len(parts)<3 or parts[0]!='br' or parts[1] not in ('exercise','course','blog','videos','math-exercise'):continue
                    title=unquote(parts[-1]).replace('-',' ').strip()
                    if title.isdigit():continue
                    found.append(reference(title,link,source,url,'video_reference' if parts[1]=='videos' else 'problem_reference' if 'exercise' in parts[1] else 'reference',parts[1],True))
                detail='Endereços públicos em português com títulos derivados da URL. IDs numéricos sem título, perfis e discussões excluídos; cursos e enunciados não copiados.'
            elif source=='Maratona UFMG':
                match=re.search(r'var ytInitialData = (.*?);</script>',text)
                if match:found=youtube_records(json.loads(match[1]),url)
                detail='Vídeos expostos na página pública; sem transcrições. Não inclui vídeos privados ou páginas adicionais.'
            elif source=='USACO Guide':
                with KnowledgeBase(args.database).read() as db:
                    count=db.execute("SELECT count(*) FROM knowledge_documents WHERE url LIKE 'https://usaco.guide/%' AND kind='article'").fetchone()[0]
                status='tutoriais com texto importado';detail=f'{count} módulos na versão fixada, com licença. Limpeza de MDX; soluções e trechos de terceiros excluídos.'
            elif source=='YouKn0wWho Academy':
                asset=re.search(r'src="([^"]+/pages/topic-list-[^"]+\.js)"',text)
                if asset:found=academy_records(fetch(urljoin(url,asset[1])),url)
                detail='Referências públicas da lista de assuntos. Aulas, soluções e conteúdo dos destinos não copiados.'
            else:
                found=[reference('TLE · CP-31 Sheet',url,source,url)]
                endpoint='https://backend-2.tle-eliminators.com/public/cp-sheet/no-auth-fetch-problems'
                try:
                    payload=json.loads(fetch(endpoint))
                    for row in walk(payload):
                        title=row.get('problemName') or row.get('problem_title') or row.get('name')
                        link=row.get('problemUrl') or row.get('problem_url') or row.get('url')
                        if isinstance(title,str) and isinstance(link,str) and link.startswith('https://'):
                            found.append(reference(title,link,source,url,'problem_reference'))
                    status='referências públicas' if len(found)>1 else 'parcial: formato do catálogo não reconhecido'
                    detail='Somente metadados públicos; soluções e vídeos não copiados.'
                except requests.HTTPError as exc:
                    status='parcial: catálogo recusou acesso (HTTP '+str(exc.response.status_code)+')'
                    detail='Link inicial indexado. A consulta pública no-auth-fetch-problems recusou a origem; problemas e vídeos da lista não foram importados.'

            docs+=found;report['sources'].append(dict(source=source,url=url,status=status,reference_count=len(found),detail=detail))
        except (requests.RequestException,ValueError,ElementTree.ParseError) as exc:
            report['sources'].append(dict(source=source,url=url,status='não importado',error=type(exc).__name__))
    merged={}
    for document in docs:
        url=document['url']
        if url not in merged:merged[url]=document
        merged[url].setdefault('discovered_in',[])
        if document['source_url'] not in merged[url]['discovered_in']:merged[url]['discovered_in'].append(document['source_url'])
        merged[url]['tags']=list(dict.fromkeys(merged[url]['tags']+document['tags']))
    kb=KnowledgeBase(args.database)
    # A link index must never overwrite an existing full-text article.
    with kb.read() as db:full_urls={r[0] for r in db.execute("SELECT url FROM knowledge_documents WHERE kind NOT IN ('reference','video_reference','problem_reference')")}
    report['import']=kb.import_documents(d for u,d in merged.items() if u not in full_urls);report['stats']=kb.stats();report['unique_references_in_batch']=len(merged)
    args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
