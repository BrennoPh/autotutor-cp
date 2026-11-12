from core.progress_store import ProgressStore
from core.study_pages import material,sections
from core.llm_client import LLMClient
from core.codigen_tutor import CodigenTutor
from unittest.mock import MagicMock,patch
from types import SimpleNamespace


def test_study_permalink_only_opens_owners_material(tmp_path):
    store=ProgressStore(tmp_path/'study.sqlite3');owner='a'*32;other='b'*32
    mid=store.add_artifact(owner,'material','Meu estudo',dict(content='# Introdução\nTexto',concept='DP'))
    assert material(store,owner,mid)['payload']['content'].startswith('# Introdução')
    assert material(store,other,mid) is None
    assert material(store,owner,"' OR 1=1 --") is None
    pid=store.add_artifact(owner,'problem','Código privado',dict(std_cpp='private'))
    assert material(store,owner,pid) is None


def test_reader_sumary_does_not_split_code_blocks():
    parts=sections('## Intuição\nTexto\n```cpp\n# include <x>\n```\n## Complexidade\nO(log n)')
    assert [t for t,_ in parts]==['Intuição','Complexidade']
    assert '# include <x>' in parts[0][1]


def test_long_segment_tree_material_receives_requested_characters_and_cp_foundations():
    llm=LLMClient('Gemini','key','test',require_model=True)
    client=MagicMock();client.__enter__.return_value=client
    client.models.generate_content.return_value=SimpleNamespace(text='## Intuição\n'+'Explicação teórica e um exemplo rastreado. '*150)
    with patch.object(llm,'_gemini_client',return_value=client):
        result=CodigenTutor(llm).generate_material('Explicação','Segment Tree','Iniciante','',learning_request='Quero 5000 caracteres sobre SegTree',length='Longo',depth='Aprofundada')
    prompt=client.models.generate_content.call_args.kwargs['contents']
    assert '5000 caracteres úteis' in prompt and 'invariantes e correção' in prompt
    assert 'complexidade de tempo e memória' in prompt
    assert len(result)>5000


def test_mermaid_diagram_in_material_is_supported_and_not_rejected_as_code():
    llm=LLMClient('Gemini','key','test',require_model=True)
    # A Mermaid diagram with more than 25 lines and parentheses in labels
    mermaid_lines = ['```mermaid', 'graph TD']
    for i in range(1, 30):
        mermaid_lines.append(f'  N{i}[{i} (vertice_{i})] --> N{i+1}[{i+1} (vertice_{i+1})]')
    mermaid_lines.append('```')
    content = '# Aula Completa de Grafos\n' + '\n'.join(mermaid_lines) + '\n\nExplicação passo a passo da busca.'
    client=MagicMock();client.__enter__.return_value=client
    client.models.generate_content.return_value=SimpleNamespace(text=content)
    with patch.object(llm,'_gemini_client',return_value=client):
        result=CodigenTutor(llm).generate_material('Explicação','Grafos','Iniciante','',learning_request='Aula visual de BFS e DFS',length='Longo')
    assert llm.last_source == 'api'
    assert '```mermaid' in result
    # Ensure parentheses inside labels were quoted
    assert '["1 (vertice_1)"]' in result
    assert 'Aula Completa de Grafos' in result


def test_lecture_prompts_mandate_mermaid_and_execution_trace():
    llm=LLMClient('Gemini','key','test',require_model=True)
    client=MagicMock();client.__enter__.return_value=client
    client.models.generate_content.return_value=SimpleNamespace(text='## Aula\nConteúdo visual e trace.')
    with patch.object(llm,'_gemini_client',return_value=client):
        CodigenTutor(llm).generate_material('Explicação','Grafos','Iniciante','',learning_request='Busca em grafos e DFS',include_examples=True)
    prompt=client.models.generate_content.call_args.kwargs['contents']
    assert 'REPRESENTAÇÃO VISUAL OBRIGATÓRIA (Mermaid)' in prompt
    assert 'RASTREAMENTO PASSO A PASSO (Trace de Execução)' in prompt
    assert 'ARMADILHAS DE MARATONA' in prompt
    assert 'CLASSIFICAÇÃO DAS 4 ARESTAS DA DFS' in prompt
    assert 'Back Edge' in prompt
    assert 'MÁQUINA DE ESTADOS DAS CORES' in prompt
    assert 'DISTINÇÃO ESTRUTURAL RIGOROSA' in prompt


def test_local_material_includes_mermaid_for_graph_topics():
    tutor=CodigenTutor()
    mat = tutor.generate_material('Explicação','Grafos','Iniciante','',include_examples=True,length='Longo')
    assert '```mermaid' in mat
    assert 'graph LR' in mat or 'graph TD' in mat
    assert 'Classificação das 4 Arestas na DFS' in mat
    assert 'Back Edge' in mat


def test_study_page_sections_are_slide_ready():
    content = '# 1. Introdução aos Grafos\nTexto 1\n## 2. Busca em Profundidade\nTexto 2\n## 3. Classificação das Arestas\nTexto 3'
    chunks = sections(content)
    assert len(chunks) == 3
    assert chunks[0][0] == '1. Introdução aos Grafos'
    assert chunks[1][0] == '2. Busca em Profundidade'
    assert chunks[2][0] == '3. Classificação das Arestas'
    assert 'Texto 1' in chunks[0][1]
    assert 'Texto 2' in chunks[1][1]
    assert 'Texto 3' in chunks[2][1]
