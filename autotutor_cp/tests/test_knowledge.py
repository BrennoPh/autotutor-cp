import gzip
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock,patch
import sqlite3
import pytest
from core.knowledge import KnowledgeBase
from scripts.import_knowledge import clean_markdown,frontmatter


def article(title='Breadth-first search',content=None,url='https://example.org/bfs',track='Base'):
    return dict(title=title,source='Test source',url=url,source_url=url+'?revision=known',license='CC BY-SA 4.0',license_url='https://creativecommons.org/licenses/by-sa/4.0/',authors='Test author',language='en',revision='test',track=track,topics=['graph'],tags=['bfs','grafostream'],content=content or ('Breadth-first search uses a FIFO queue. Every edge has unit weight. '+'A visited vertex is marked before insertion. '*8))


def test_index_reads_real_content_and_idempotent_compressed_json_roundtrip(tmp_path):
    kb=KnowledgeBase(tmp_path/'a.sqlite3');doc=article()
    assert kb.import_documents([doc])['inserted']==1
    assert kb.import_documents([doc])['unchanged']==1
    result=kb.search('BFS')[0]
    assert 'FIFO' in result['excerpt'] and result['url']==doc['url']
    assert kb.get(result['id'])['content']==doc['content'].strip()
    export=tmp_path/'corpus.json.gz';kb.export_json(export)
    with gzip.open(export,'rt') as stream:payload=json.load(stream)
    assert payload['documents'][0]['content']==doc['content'].strip()
    other=KnowledgeBase(tmp_path/'b.sqlite3');other.import_documents(payload['documents'])
    assert other.search('FIFO')[0]['title']==doc['title']
    assert kb.import_documents(payload['documents'])['unchanged']==1
    with kb.read() as db:
        raw=db.execute('SELECT body FROM knowledge_documents').fetchone()[0]
    assert isinstance(raw,bytes) and len(raw)<len(doc['content'].encode())


def test_update_replaces_indexed_content_and_deduplicates_identical_text(tmp_path):
    kb=KnowledgeBase(tmp_path/'a.sqlite3');doc=article(content='obsoletephrase '+('An algorithm traverses vertices. '*10))
    kb.import_documents([doc])
    assert kb.search('obsoletephrase')
    changed=dict(doc,content='newmarker '+('A different algorithm traverses edges. '*10))
    assert kb.import_documents([changed])['updated']==1
    assert not kb.search('obsoletephrase') and kb.search('newmarker')
    assert kb.import_documents([dict(changed,url='https://example.org/mirror')])['duplicate_content']==1
    assert kb.stats()['documents']==1


def test_bilingual_search_filters_and_fts_input_are_safe(tmp_path):
    kb=KnowledgeBase(tmp_path/'a.sqlite3')
    kb.import_documents([article('Depth First Search'),article('Advanced network flow','Network flow advanced. '*30,'https://example.org/flow','Complementar')])
    assert kb.search('busca em profundidade',foundation_only=True)[0]['title']=='Depth First Search'
    assert len(kb.browse(foundation_only=True))==1
    assert len(kb.browse(foundation_only=False))==2
    assert not kb.search('depth',source='Not a source')
    assert not kb.browse(topic='dp')
    kb.search('" OR title:foo*; DROP TABLE knowledge_documents; --')
    assert kb.stats()['documents']==2


def test_context_budget_citations_and_code_fragments(tmp_path):
    kb=KnowledgeBase(tmp_path/'a.sqlite3')
    text=('BFS uses a queue and unit weights. '*35)+'\n```cpp\n'+('secret_function();\n'*150)+'```\n'+('BFS marks visited vertices. '*30)
    kb.import_documents([article(content=text)])
    context,refs=kb.context('BFS',max_chars=1100)
    assert len(context)<=1100 and refs and 'https://example.org/bfs' in context
    assert 'secret_function' not in context
    assert refs[0]['license']=='CC BY-SA 4.0'
    assert kb.context('definitelyunfindableterm',max_chars=1100)==('',[])


def test_failed_import_is_atomic(tmp_path):
    kb=KnowledgeBase(tmp_path/'a.sqlite3');kb.import_documents([article()])
    with pytest.raises(ValueError):kb.import_documents([article('New','New subject. '*30,'https://example.org/new'),dict(article(),title=None)])
    assert kb.stats()['documents']==1


def test_mdx_cleaning_preserves_math_and_snippets_but_excludes_problem_solutions():
    raw='''# Prefix sums
Use $a < b$ and $P[R]-P[L-1]$.
```cpp
vector<int> data;
```
<Spoiler title="Solution">
Do not import the hidden full solution.
```cpp
int main(){return 0;}
```
</Spoiler>
<YouTube id="abcdef12345"/>
## Next explanation
This part remains.
'''
    result=clean_markdown(raw,'https://example.org/lesson','https://github.com/example/repo/blob/revision/module.mdx',True)
    assert '$a < b$' in result and 'vector<int>' in result
    assert 'hidden full solution' not in result and 'int main' not in result
    assert 'https://www.youtube.com/watch?v=abcdef12345' in result
    assert 'This part remains' in result


def test_material_generation_receives_retrieved_text_not_only_links(tmp_path,monkeypatch):
    from core.codigen_tutor import CodigenTutor
    from core.llm_client import LLMClient
    path=tmp_path/'a.sqlite3';monkeypatch.setenv('AUTOTUTOR_KNOWLEDGE_DB',str(path))
    kb=KnowledgeBase(path);kb.import_documents([article(content='BFS: rare evidence sentence about FIFO queue. '+'A visited vertex stays visited. '*12)])
    llm=LLMClient('Gemini','key','model',require_model=True)
    client=MagicMock();client.__enter__.return_value=client;client.models.generate_content.return_value=SimpleNamespace(text='Use uma fila para visitar as camadas.')
    tutor=CodigenTutor(llm)
    with patch.object(llm,'_gemini_client',return_value=client):
        result=tutor.generate_material('Explicação','Grafos','Iniciante','',learning_request='Quero aprender BFS.',length='Curto')
    prompt=client.models.generate_content.call_args.kwargs['contents']
    assert 'rare evidence sentence' in prompt and 'TRECHOS RECUPERADOS' in prompt
    assert 'Fontes recuperadas do acervo RAG' in result
    assert tutor.last_retrieval[0]['url']=='https://example.org/bfs'


def test_portable_seed_initializes_once_and_preserves_an_existing_corpus(tmp_path):
    source=KnowledgeBase(tmp_path/'source.sqlite3');source.import_documents([article()])
    package=tmp_path/'seed.json.gz';source.export_json(package)
    target=KnowledgeBase(tmp_path/'target.sqlite3')
    assert target.ensure_seeded(package) is True
    assert target.search('BFS')
    assert target.ensure_seeded(package) is False
    assert target.stats()['documents']==1


def test_beginner_portuguese_vocabulary_recovers_english_source(tmp_path):
    kb=KnowledgeBase(tmp_path/'beginner.sqlite3')
    kb.import_documents([article('Arrays and Counting', 'Arrays store values at integer indices. Counting uses frequency arrays. '*12)])
    results=kb.search('Vetores e contagem',external_only=True,content_only=True)
    assert results and results[0]['title']=='Arrays and Counting'
