"""Download pinned tutorial text only; verify Git blob hashes, never execute MDX."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import time
import requests

ROOT=Path(__file__).resolve().parents[1]


def blob_hash(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'.runtime/knowledge_sources');parser.add_argument('--repo',choices=['cpinitiative/usaco-guide','cp-algorithms/cp-algorithms']);args=parser.parse_args()
    config=json.loads((ROOT/'data/knowledge_sources.json').read_text());jobs=[]
    for source in config['sources']:
        if args.repo and source['repo']!=args.repo:continue
        repo,revision=source['repo'],source['revision']
        response=requests.get(f'https://api.github.com/repos/{repo}/git/trees/{revision}',params={'recursive':1},timeout=(5,40));response.raise_for_status();tree=response.json()
        if tree.get('truncated'):raise ValueError('Árvore incompleta; importação não iniciada.')
        for entry in tree['tree']:
            path=entry['path']
            if entry['type']=='blob' and ((path.startswith(source['prefix']) and path.endswith(source['suffix'])) or path in ('LICENSE','README.md')):
                if Path(path).is_absolute() or '..' in Path(path).parts:raise ValueError('Caminho de origem inválido.')
                jobs.append(dict(repo=repo,revision=revision,path=path,blob=entry['sha']))
    def fetch(job):
        path=args.output/job['repo']/job['path'];data=path.read_bytes() if path.exists() else b''
        if data and blob_hash(data)==job['blob']:return dict(job,status='cached')
        for attempt in range(3):
            try:
                response=requests.get(f'https://raw.githubusercontent.com/{job["repo"]}/{job["revision"]}/{job["path"]}',timeout=(5,40));response.raise_for_status();data=response.content
                if len(data)>1_500_000 or blob_hash(data)!=job['blob']:raise ValueError('Tamanho ou hash inesperado.')
                data.decode('utf-8');path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
                return dict(job,status='ok')
            except (requests.RequestException,ValueError) as exc:
                if attempt==2:return dict(job,status='error',error=str(exc)[:200])
                time.sleep(attempt+1)
    with ThreadPoolExecutor(max_workers=4) as pool:manifest=list(pool.map(fetch,jobs))
    args.output.mkdir(parents=True,exist_ok=True);(args.output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    errors=[m for m in manifest if m['status']=='error']
    print(json.dumps(dict(files=len(manifest),errors=errors),ensure_ascii=False))
    return int(bool(errors))

if __name__=='__main__':raise SystemExit(main())
