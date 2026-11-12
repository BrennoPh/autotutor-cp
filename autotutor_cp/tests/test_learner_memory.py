import json
import uuid

from core.learner_memory import LearnerMemory
from core.progress_store import ProgressStore


def test_memory_captures_artifacts_as_markdown_and_exports_portably(tmp_path):
    store = ProgressStore(tmp_path / 'progress.sqlite3')
    profile = uuid.uuid4().hex
    artifact = store.add_artifact(profile, 'material', 'BFS em camadas', {
        'concept': 'Grafos', 'learning_request': 'Quero entender BFS antes de praticar.',
        'source': 'Gemini', 'content': 'Este texto longo não deve ser duplicado no índice de memória.'
    })
    memory = LearnerMemory(store)
    exported = memory.export(profile)
    assert exported['format'] == 'autotutor-ai-memory'
    assert any(event['source_id'] == artifact for event in exported['events'])
    page = next(page for page in exported['pages'] if page['path'] == 'memoria.md')
    assert 'BFS em camadas' in page['content']
    assert 'texto longo não deve' not in page['content']
    assert (tmp_path / 'memory' / profile / 'memoria.md').is_file()
    assert 'Handoff de estudo' in memory.markdown_bundle(profile)
    assert json.loads(json.dumps(exported, ensure_ascii=False))['schema_version'] == 1


def test_memory_is_private_sanitized_and_query_ranked(tmp_path):
    store = ProgressStore(tmp_path / 'progress.sqlite3')
    owner, other = uuid.uuid4().hex, uuid.uuid4().hex
    memory = LearnerMemory(store)
    memory.capture(owner, 'chat', 'Pedido de BFS', 'Quero revisar fila e distâncias. api_key=SECRET-123')
    memory.capture(owner, 'artefato:material', 'Programação dinâmica', 'Estados e transições para DP.')
    memory.capture(other, 'chat', 'Privado', 'SEGREDO DE OUTRA PESSOA')
    recalled = memory.recall(owner, 'BFS fila distâncias')
    assert recalled and 'BFS' in recalled[0]['excerpt']
    assert 'SECRET-123' not in memory.markdown_bundle(owner)
    assert 'OUTRA PESSOA' not in memory.markdown_bundle(owner)
    assert 'dado sensível removido' in memory.markdown_bundle(owner)


def test_memory_brief_is_bounded_and_included_in_generation_context(tmp_path):
    store = ProgressStore(tmp_path / 'progress.sqlite3')
    profile = uuid.uuid4().hex
    for index in range(8):
        store.add_artifact(profile, 'material', f'Soma de prefixos {index}', {
            'concept': 'Prefix Sum', 'learning_request': 'consultas em intervalo ' + ('x' * 400),
            'content': 'não indexar ' + ('y' * 3000), 'source': 'Gemini'
        })
    brief = LearnerMemory(store).brief(profile, 'prefixos intervalos', max_chars=700)
    assert len(json.dumps(brief, ensure_ascii=False)) <= 700
    context = json.loads(store.context(profile, 'prefixos intervalos', max_chars=2500))
    assert context['learner_memory']['memory_policy'].startswith('Memória local')
    assert context['learner_memory']['recalled_pages']


def test_memory_topic_consolidation_and_retention(tmp_path):
    store = ProgressStore(tmp_path / 'progress.sqlite3')
    profile = uuid.uuid4().hex
    memory = LearnerMemory(store)

    # 1. Aluno estuda material sobre Prefix Sum
    store.add_artifact(profile, 'material', 'Introdução a Prefix Sum', {
        'concept': 'Soma de prefixos', 'learning_request': 'Quero entender consultas com sentinela.',
        'source': 'Gemini', 'content': 'Texto longo não indexado.'
    })

    # 2. Aluno submete e comete erro de indexação (Wrong Answer)
    store.add_artifact(profile, 'submission', 'Consultas de Soma', {
        'record': {'topic': 'Soma de prefixos', 'verdict': 'Wrong Answer', 'time_ms': 15},
        'source_code': 'int main(){ /* segredo do aluno */ }',
        'result': {'verdict': 'Wrong Answer'}
    })

    # 3. Diagnóstico de feedback
    store.add_artifact(profile, 'feedback', 'Diagnóstico · Consultas de Soma', {
        'concept': 'Soma de prefixos',
        'content': 'Atenção aos limites do vetor: use sentinela na posição zero para consultas 1-based.'
    })

    # Verifica páginas consolidadas em disco e no índice
    exported = memory.export(profile)
    page_paths = [p['path'] for p in exported['pages']]
    assert 'memoria.md' in page_paths
    assert 'handoff.md' in page_paths
    assert 'progresso.md' in page_paths
    assert any('soma_de_prefixos.md' in p for p in page_paths)

    topic_page = next(p for p in exported['pages'] if 'soma_de_prefixos.md' in p['path'])
    assert 'Wrong Answer' in topic_page['content']
    assert 'sentinela na posição zero' in topic_page['content']
    assert 'segredo do aluno' not in topic_page['content']

    # Recall direcionado por query
    recalled = memory.recall(profile, 'prefixos consultas sentinela')
    assert any('soma_de_prefixos.md' in item['path'] for item in recalled)


def test_rag_with_ai_memory_retention(tmp_path):
    from unittest.mock import patch
    from core.codigen_tutor import CodigenTutor
    from core.llm_client import LLMClient

    store = ProgressStore(tmp_path / 'progress.sqlite3')
    profile = uuid.uuid4().hex

    # Registra dificuldade anterior em BFS
    store.add_artifact(profile, 'submission', 'Caminho em Labirinto', {
        'record': {'topic': 'BFS e Grafos', 'verdict': 'Wrong Answer', 'time_ms': 22},
        'result': {'verdict': 'Wrong Answer'}
    })
    store.add_artifact(profile, 'feedback', 'Diagnóstico · Labirinto', {
        'concept': 'BFS e Grafos',
        'content': 'Vértices isolados precisam de inicialização com sentinela -1.'
    })

    evidence = store.learning_evidence(profile, query='BFS grafos')
    assert 'ai_memory' in evidence
    assert any('Vértices isolados' in p['excerpt'] for p in evidence['ai_memory']['recalled_pages'])

    # Geração de material via RAG conectada à AI Memory
    llm = LLMClient('Gemini', 'test', 'test', require_model=True)
    with patch.object(llm, 'complete', return_value='Explicação com reforço.') as mock_complete:
        CodigenTutor(llm).generate_material(
            'Explicação', 'Grafos', 'Iniciante', '',
            learning_request='Quero entender BFS',
            learner_evidence=evidence
        )

    system_prompt = mock_complete.call_args.args[0]
    user_prompt = mock_complete.call_args.args[1]

    assert 'AI Memory' in system_prompt
    assert 'Vértices isolados' in user_prompt
    assert 'ESTATÍSTICAS DO ALUNO' in user_prompt
