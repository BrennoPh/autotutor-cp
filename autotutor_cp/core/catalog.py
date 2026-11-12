"""Real external references and original local problems, kept explicitly distinct."""
from functools import lru_cache
import json
from pathlib import Path
from urllib.parse import urlsplit
from core.problem_bank import load_problems

DATA=Path(__file__).resolve().parents[1]/'data'


@lru_cache(maxsize=1)
def external_problems():
    return json.loads((DATA/'external_problems.json').read_text(encoding='utf-8'))['problems']


def catalog(local=None):
    local=list(local if local is not None else load_problems())
    ids={p['id'] for p in local}
    return local+[p for p in external_problems() if p['id'] not in ids]


def catalog_map():
    return {p['id']:p for p in catalog()}


def valid_proof(problem,url):
    if not url:return ''
    parts=urlsplit(url.strip())
    source=urlsplit(problem['url'])
    if parts.scheme!='https' or parts.username or parts.password or parts.hostname!=source.hostname:
        raise ValueError('O comprovante deve ser um link HTTPS do mesmo juiz do exercício.')
    return url.strip()[:2000]


STUDY_SOURCES=[
 {'name':'Maratona UFMG','url':'https://youtube.com/@maratonaufmg2572','kind':'Videoaulas','description':'Canal indicado para acompanhar aulas e treinos de programação competitiva.'},
 {'name':'CSES','url':'https://cses.fi/problemset/','kind':'Problemas','description':'Catálogo oficial indexado por seção. Enunciados e correção no CSES.'},
 {'name':'USACO Guide','url':'https://usaco.guide/','kind':'Trilha e problemas','description':'Módulos Bronze e Silver usados como fonte de metadados dos exercícios adicionais.'},
 {'name':'Neps Academy','url':'https://neps.academy/','kind':'Cursos e prática','description':'Conteúdo em português e exercícios. Consulte acesso e disponibilidade na plataforma.'},
 {'name':'YouKn0wWho Academy','url':'https://youkn0wwho.academy/','kind':'Cursos','description':'Recurso indicado pelo usuário; catálogo não importado automaticamente.'},
 {'name':'TLE Eliminators CP Sheet','url':'https://www.tle-eliminators.com/cp-sheet','kind':'Lista de treino','description':'Lista indicada pelo usuário; catálogo carregado por JavaScript e não importado automaticamente.'}]
