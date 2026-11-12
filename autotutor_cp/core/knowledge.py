"""Compact, attributed RAG corpus: compressed documents and a contentless FTS5 index."""
from collections import Counter
from contextlib import contextmanager
from datetime import datetime,timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import unicodedata
from urllib.parse import urlsplit,urlunsplit
import time
import zlib

DEFAULT_PATH=Path(__file__).resolve().parents[1]/'data'/'knowledge.sqlite3'
SCHEMA_VERSION=1
# Bilingual information-retrieval aliases, not proficiency or teaching decisions.
ALIASES={
 'segtree':'segment tree','dp':'dynamic programming','dfs':'depth first search','bfs':'breadth first search',
 'soma de prefixos':'prefix sums','somas de prefixos':'prefix sums','prefix sum':'prefix sums',
 'programacao dinamica':'dynamic programming dp','busca binaria':'binary search',
 'menor caminho':'shortest path dijkstra','menores caminhos':'shortest paths dijkstra',
 'arvore de segmentos':'segment tree','arvore de fenwick':'fenwick binary indexed tree',
 'janelas deslizantes':'sliding window two pointers','janela deslizante':'sliding window two pointers',
 'dois ponteiros':'two pointers','divisao e conquista':'divide conquer','ordenacao':'sorting sort',
 'grafos':'graph graphs','arvores':'tree trees','guloso':'greedy','estruturas de dados':'data structures',
 'matematica':'mathematics number theory','combinatoria':'combinatorics','geometria':'geometry',
 'conjuntos disjuntos':'disjoint set union dsu','uniao busca':'disjoint set union dsu',
 'arvore geradora minima':'minimum spanning tree','fluxo maximo':'maximum flow',
 'componentes fortemente conexas':'strongly connected components','exponenciacao binaria':'binary exponentiation',
 'busca em largura':'breadth first search bfs','busca em profundidade':'depth first search dfs',
 'vetores':'arrays','vetor':'array','contagem':'counting frequency',
 'simulacao':'simulation implementation','ad hoc':'simulation implementation',
 'fundamentos':'introduction complexity input output','complexidade':'complexity',
 'cadeias de caracteres':'strings','teoria dos numeros':'number theory','somatorios':'prefix sums'}
STOP=set('a an the of to and or in on for with is are be as by this that from how what why which use using can it de da do das dos e ou em um uma os as ao aos por para com que como qual quero aprender entender explique sobre assunto exemplo exemplos codigo nivel iniciante intermediario avancado explicacao material estudo voce esse essa isso sao nao mais menos'.split())


def normalize(text):
    return unicodedata.normalize('NFKD',text).encode('ascii','ignore').decode().lower()


def query_tokens(query):
    text=normalize(str(query)[:4000]);extra=' '.join(v for k,v in ALIASES.items() if re.search(r'\b'+re.escape(k)+r'\b',text))
    values=re.findall(r'[a-z0-9]{2,}',extra+' '+text)
    return list(dict.fromkeys(t for t in values if t not in STOP))[:24]


def canonical_url(url):
    parts=urlsplit(url)
    if parts.scheme=='autotutor' and parts.hostname in ('aulas','guias') and re.fullmatch(r'/[a-z0-9_-]+',parts.path):return url
    if parts.scheme!='https' or not parts.hostname or parts.username or parts.password:raise ValueError('A fonte precisa ter URL HTTPS pública sem credenciais.')
    return urlunsplit((parts.scheme,parts.netloc.lower(),parts.path.rstrip('/') or '/',parts.query,''))


def chunks(text,size=1800):
    start=0;position=0;headings=list(re.finditer(r'^#{1,6}\s+(.+)$',text,re.M));heading='';cursor=0
    while start<len(text):
        end=min(len(text),start+size)
        if end<len(text):
            split=text.rfind('\n\n',start+size//2,end)
            if split<0:split=text.rfind('\n',start+size//2,end)
            if split<0:split=text.rfind(' ',start+size//2,end)
            if split>=0:end=split+1
        while cursor<len(headings) and headings[cursor].start()<=start:
            heading=headings[cursor].group(1)[:250];cursor+=1
        yield position,start,end,heading
        position+=1;start=end


class KnowledgeBase:
    def __init__(self,path=None):
        self.path=Path(path or os.environ.get('AUTOTUTOR_KNOWLEDGE_DB',str(DEFAULT_PATH)))

    def ensure_seeded(self,package=None):
        """Restore the portable public corpus once, without touching an existing database."""
        if self.path.exists():return False
        package=Path(package or DEFAULT_PATH.with_name('knowledge.json.gz'))
        if not package.exists():return False
        with gzip.open(package,'rt',encoding='utf-8') as stream:payload=json.load(stream)
        if payload.get('schema_version')!=SCHEMA_VERSION or not isinstance(payload.get('documents'),list):raise ValueError('Pacote inicial de conhecimento inválido.')
        self.import_documents(payload['documents'])
        return True

    @contextmanager
    def read(self):
        connection=sqlite3.connect(self.path.resolve().as_uri()+'?mode=ro',uri=True,timeout=10)
        connection.row_factory=sqlite3.Row
        try:yield connection
        finally:connection.close()

    def import_documents(self,documents):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        report=Counter();now=datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.path,timeout=30) as db:
            db.executescript('''CREATE TABLE IF NOT EXISTS knowledge_documents (
                id TEXT PRIMARY KEY,url TEXT NOT NULL UNIQUE,source TEXT NOT NULL,title TEXT NOT NULL,
                language TEXT NOT NULL,license TEXT NOT NULL,kind TEXT NOT NULL,checksum TEXT NOT NULL,
                metadata TEXT NOT NULL,body BLOB NOT NULL);
                CREATE TABLE IF NOT EXISTS knowledge_meta (key TEXT PRIMARY KEY,value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS knowledge_chunks (
                id INTEGER PRIMARY KEY,document_id TEXT NOT NULL,position INTEGER NOT NULL,
                start_offset INTEGER NOT NULL,end_offset INTEGER NOT NULL,heading TEXT NOT NULL);
                CREATE INDEX IF NOT EXISTS knowledge_chunks_document ON knowledge_chunks(document_id);
                CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(title,tags,body,
                content='',tokenize='unicode61 remove_diacritics 2');''')
            for document in documents:
                value=dict(document);text=value.pop('content','').strip()
                if len(text)<160:report['too_short']+=1;continue
                if len(text)>1_000_000:raise ValueError('Documento excede o limite de texto.')
                for field in ('title','source','license'):
                    if not isinstance(value.get(field),str) or not value[field].strip():raise ValueError('Documento sem '+field)
                value['url']=canonical_url(value['url']);value['title']=value['title'][:300]
                identifier='kb_'+hashlib.sha256(value['url'].encode()).hexdigest()[:32]
                checksum=hashlib.sha256(text.encode()).hexdigest()
                previous=db.execute('SELECT checksum,metadata FROM knowledge_documents WHERE id=?',(identifier,)).fetchone()
                # Keep an import timestamp stable when a repeat has identical metadata/content.
                value.pop('id',None);value.pop('imported_at',None);value.pop('checksum',None)
                metadata=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
                if previous and previous==(checksum,metadata):report['unchanged']+=1;continue
                duplicate=db.execute('SELECT id FROM knowledge_documents WHERE checksum=? AND id!=?',(checksum,identifier)).fetchone()
                if duplicate:report['duplicate_content']+=1;continue
                db.execute('INSERT OR REPLACE INTO knowledge_documents VALUES (?,?,?,?,?,?,?,?,?,?)',(
                    identifier,value['url'],value['source'],value['title'],value.get('language','en'),value['license'],
                    value.get('kind','article'),checksum,metadata,zlib.compress(text.encode(),9)))
                db.execute('DELETE FROM knowledge_chunks WHERE document_id=?',(identifier,))
                db.executemany('INSERT INTO knowledge_chunks(document_id,position,start_offset,end_offset,heading) VALUES (?,?,?,?,?)',
                    [(identifier,*item) for item in chunks(text)])
                report['updated' if previous else 'inserted']+=1
            if report['inserted'] or report['updated']:
                db.execute("INSERT INTO knowledge_fts(knowledge_fts) VALUES('delete-all')")
                for row in db.execute('SELECT id,title,metadata,body FROM knowledge_documents').fetchall():
                    text=zlib.decompress(row[3]).decode();meta=json.loads(row[2]);tags=' '.join(meta.get('tags',[]))
                    for item in db.execute('SELECT id,start_offset,end_offset,heading FROM knowledge_chunks WHERE document_id=?',(row[0],)).fetchall():
                        db.execute('INSERT INTO knowledge_fts(rowid,title,tags,body) VALUES (?,?,?,?)',(item[0],row[1]+' '+item[3],tags,text[item[1]:item[2]]))
                db.execute("INSERT INTO knowledge_fts(knowledge_fts) VALUES('optimize')")
            if report['inserted'] or report['updated']:db.execute('INSERT OR REPLACE INTO knowledge_meta VALUES (?,?)',('updated_at',now))
            db.execute('PRAGMA user_version='+str(SCHEMA_VERSION))
        KnowledgeBase.clear_stats_cache(self.path)
        return dict(report)

    @staticmethod
    def _document(row,with_content=False):
        value=json.loads(row['metadata']);value.update(id=row['id'],checksum=row['checksum'])
        if with_content:value['content']=zlib.decompress(row['body']).decode()
        return value

    _stats_cache = {}

    def stats(self, ttl: float = 60.0):
        if not self.path.exists():return dict(documents=0,chunks=0,bytes=0,sources=[],languages=[],tracks=[])
        path_key = str(self.path.resolve())
        mtime = self.path.stat().st_mtime
        now = time.time()
        cached = KnowledgeBase._stats_cache.get(path_key)
        if cached and cached.get('mtime') == mtime and (now - cached.get('timestamp', 0) < ttl):
            return dict(cached['data'])
        with self.read() as db:
            data = dict(documents=db.execute('SELECT COUNT(*) FROM knowledge_documents').fetchone()[0],
                chunks=db.execute('SELECT COUNT(*) FROM knowledge_chunks').fetchone()[0],bytes=self.path.stat().st_size,
                sources=[dict(source=r[0],documents=r[1]) for r in db.execute('SELECT source,COUNT(*) FROM knowledge_documents GROUP BY source ORDER BY source')],
                tracks=[dict(track=r[0],documents=r[1]) for r in db.execute("SELECT json_extract(metadata,'$.track'),COUNT(*) FROM knowledge_documents GROUP BY 1")],
                languages=[r[0] for r in db.execute('SELECT DISTINCT language FROM knowledge_documents ORDER BY language')])
        KnowledgeBase._stats_cache[path_key] = {'mtime': mtime, 'timestamp': now, 'data': data}
        return dict(data)

    @classmethod
    def clear_stats_cache(cls, path=None):
        if path:
            cls._stats_cache.pop(str(Path(path).resolve()), None)
        else:
            cls._stats_cache.clear()

    def get(self,identifier):
        if not self.path.exists():return None
        with self.read() as db:row=db.execute('SELECT * FROM knowledge_documents WHERE id=?',(identifier,)).fetchone()
        return self._document(row,True) if row else None

    def search(self,query,limit=6,source=None,per_document=2,foundation_only=False,topic=None,external_only=False,content_only=False,reference_only=False,prefer_foundation=False):
        if not self.path.exists():return []
        if not 1<=limit<=30:raise ValueError('Limite de busca inválido.')
        terms=query_tokens(query)
        if not terms:return []
        expression=' OR '.join('"'+t+'"' for t in terms)
        sql='''SELECT d.*,c.id AS chunk_id,c.heading,c.start_offset,c.end_offset,
            bm25(knowledge_fts,6.0,3.0,1.0) AS rank
            FROM knowledge_fts JOIN knowledge_chunks c ON knowledge_fts.rowid=c.id
            JOIN knowledge_documents d ON d.id=c.document_id WHERE knowledge_fts MATCH ?'''
        args=[expression]
        if source:sql+=' AND d.source=?';args.append(source)
        if external_only:sql+=" AND d.url LIKE 'https://%'"
        if content_only:sql+=" AND d.kind NOT IN ('reference','video_reference','problem_reference')"
        if reference_only:sql+=" AND d.kind IN ('reference','video_reference','problem_reference')"
        if foundation_only:sql+=" AND json_extract(d.metadata,'$.track')='Base'"
        if topic:sql+=" AND EXISTS (SELECT 1 FROM json_each(d.metadata,'$.topics') WHERE value=?)";args.append(topic)
        sql+=' ORDER BY rank,c.id LIMIT ?';args.append(limit*12)
        with self.read() as db:rows=db.execute(sql,args).fetchall()
        # BM25 alone can overvalue a rare abbreviation inside an advanced article.
        # Title matches and optional foundation preference improve topical precision.
        normalized=normalize(str(query))
        phrases=[normalized]+[re.sub(r' (?:dp|bfs|dfs)$','',v) for k,v in ALIASES.items() if re.search(r'\b'+re.escape(k)+r'\b',normalized)]
        def relevance(row):
            title=normalize(row['title']);bonus=0
            for phrase in phrases:
                if title==phrase or title in ('introduction to '+phrase,'intro to '+phrase):bonus=max(bonus,25)
                elif phrase in title:bonus=max(bonus,8)
            if prefer_foundation and json.loads(row['metadata']).get('track')=='Base':bonus+=6
            return -row['rank']+bonus
        rows=sorted(rows,key=relevance,reverse=True)
        result=[];used=Counter();texts={};prose={}
        for row in rows:
            identifier=row['id']
            if used[identifier]>=per_document:continue
            if identifier not in texts:
                texts[identifier]=zlib.decompress(row['body']).decode()
                prose[identifier]=re.sub(r'```[^\n]*\n.*?```',lambda m:' '*len(m.group(0)),texts[identifier],flags=re.S)
            value=self._document(row);value.update(chunk_id=row['chunk_id'],heading=row['heading'],
                excerpt=texts[identifier][row['start_offset']:row['end_offset']],context_excerpt=prose[identifier][row['start_offset']:row['end_offset']],score=round(relevance(row),6))
            result.append(value);used[identifier]+=1
            if len(result)==limit:break
        return result

    def browse(self,source=None,topic=None,foundation_only=True,limit=15):
        if not self.path.exists():return []
        sql='SELECT * FROM knowledge_documents WHERE 1=1';args=[]
        if source:sql+=' AND source=?';args.append(source)
        if foundation_only:sql+=" AND json_extract(metadata,'$.track')='Base'"
        if topic:sql+=" AND EXISTS (SELECT 1 FROM json_each(metadata,'$.topics') WHERE value=?)";args.append(topic)
        sql+=" ORDER BY CASE language WHEN 'pt-BR' THEN 0 ELSE 1 END,title LIMIT ?";args.append(min(max(limit,1),50))
        with self.read() as db:rows=db.execute(sql,args).fetchall()
        return [dict(self._document(row),excerpt=zlib.decompress(row['body']).decode()[:700]) for row in rows]

    def context(self,query,max_chars=5000,limit=4,foundation_only=False,external_only=True,prefer_foundation=False):
        """Only retrieved prose enters the model; source facts are data, never instructions."""
        output=[];refs=[];used=set();remaining=max_chars
        for item in self.search(query,limit=limit,per_document=1,foundation_only=foundation_only,external_only=external_only,content_only=True,prefer_foundation=prefer_foundation):
            excerpt=item['context_excerpt'].strip()
            # Avoid feeding a fragment cut in the middle of a complete program.
            if not excerpt or re.search(r'#\s*include|\bmain\s*\(',excerpt):continue
            label='R'+str(len(refs)+1) if item['id'] not in used else next(r['label'] for r in refs if r['id']==item['id'])
            origin=item['url'] if item['url'].startswith('https://') else 'Biblioteca do AutoTutor · '+item['title']
            header=f'[{label}] {item["title"]}\nFonte: {origin}\nLicença: {item["license"]}\n'
            if remaining<len(header)+180:break
            excerpt=excerpt[:min(1800,max(250,max_chars//max(1,limit)-len(header)-2),remaining-len(header)-2)]
            output.append(header+excerpt);remaining-=len(header)+len(excerpt)+2
            if item['id'] not in used:
                refs.append(dict(id=item['id'],chunk_id=item['chunk_id'],score=item['score'],label=label,title=item['title'],url=item['url'],publisher=item['source'],
                                 authors=item.get('authors',''),license=item['license'],license_url=item.get('license_url',''),source_url=item.get('source_url',item['url']),kind='Artigo',verification='Texto importado com origem e licença'))
                used.add(item['id'])
        return '\n\n'.join(output),refs

    def export_json(self,destination):
        target=Path(destination);target.parent.mkdir(parents=True,exist_ok=True)
        with self.read() as db:docs=[self._document(row,True) for row in db.execute('SELECT * FROM knowledge_documents ORDER BY id')]
        payload=dict(schema_version=SCHEMA_VERSION,documents=docs)
        opener=gzip.open if str(target).endswith('.gz') else open
        with opener(target,'wt',encoding='utf-8') as stream:json.dump(payload,stream,ensure_ascii=False,separators=(',',':'))
        return dict(documents=len(docs),bytes=target.stat().st_size)
