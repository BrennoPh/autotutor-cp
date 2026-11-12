from unittest.mock import MagicMock
from types import SimpleNamespace
from core.whiteboard_engine import (
    WHITEBOARD_PRESETS,
    parse_mermaid_from_text,
    generate_ai_whiteboard_diagram,
    analyze_board_structure
)
from core.whiteboard_views import whiteboard_canvas_html
from core.progress_store import ProgressStore
from core.llm_client import LLMClient


def test_whiteboard_presets_have_valid_structure():
    assert 'dag' in WHITEBOARD_PRESETS
    assert 'cycle' in WHITEBOARD_PRESETS
    assert 'tree' in WHITEBOARD_PRESETS
    assert 'bfs_layers' in WHITEBOARD_PRESETS
    assert 'bipartite' in WHITEBOARD_PRESETS

    for key, p in WHITEBOARD_PRESETS.items():
        assert 'title' in p and len(p['title']) > 0
        assert 'description' in p and len(p['description']) > 10
        assert 'mermaid' in p and 'graph' in p['mermaid']
        assert len(p['nodes']) >= 3
        assert len(p['edges']) >= 2
        for n in p['nodes']:
            assert 'id' in n and 'x' in n and 'y' in n and 'label' in n
        for e in p['edges']:
            assert 'from' in e and 'to' in e and 'directed' in e


def test_parse_mermaid_from_text_extracts_and_sanitizes():
    raw = "Aqui está o diagrama:\n```mermaid\ngraph TD\n  N1[1 (origem)] --> N2[2]\n```\nFim."
    code = parse_mermaid_from_text(raw)
    assert code is not None
    assert 'graph TD' in code
    assert '["1 (origem)"]' in code


def test_generate_ai_whiteboard_diagram_fallback_and_completion():
    llm = LLMClient('Ollama', '', '')

    # Test fallback
    res_fallback = generate_ai_whiteboard_diagram(llm, "Quero ver um ciclo com back edge")
    assert 'Ciclo na DFS' in res_fallback['text'] or 'CICLO' in res_fallback['mermaid']

    # Test mock API completion
    llm_api = LLMClient('Gemini', 'key', 'test')
    mock_resp = "Aqui está a árvore:\n```mermaid\ngraph TD\n  A --> B\n```"
    llm_api.complete = MagicMock(return_value=mock_resp)

    res_api = generate_ai_whiteboard_diagram(llm_api, "Desenhe uma árvore")
    assert 'graph TD' in res_api['mermaid']
    assert 'A --> B' in res_api['mermaid']


def test_analyze_board_structure_generates_feedback():
    llm = LLMClient('Gemini', 'key', 'test')
    llm.complete = MagicMock(return_value="O grafo desenhado é um DAG perfeito sem ciclos.")

    feedback = analyze_board_structure(llm, "Desenhei 4 nós em linha reta 1 -> 2 -> 3 -> 4.")
    assert "DAG" in feedback


def test_whiteboard_canvas_html_contains_essential_elements():
    preset = WHITEBOARD_PRESETS['dag']
    html_code = whiteboard_canvas_html(initial_preset=preset, height=500)
    assert '<canvas id="wb-canvas">' in html_code
    assert 'btn-pen' in html_code
    assert 'btn-node' in html_code
    assert 'btn-arrow' in html_code
    assert 'btn-download' in html_code
    assert 'DAG e Ordenação Topológica' in html_code


def test_whiteboard_artifact_storage(tmp_path):
    store = ProgressStore(tmp_path / 'test_wb.sqlite3')
    profile_id = 'a' * 32
    art_id = store.add_artifact(
        profile_id,
        'whiteboard',
        'Meu Grafo de Estudo',
        {'preset': 'dag', 'analysis': 'Sem ciclos', 'source': 'GPT-4o-mini'}
    )
    items = store.artifacts(profile_id, kind='whiteboard')
    assert len(items) == 1
    assert items[0]['id'] == art_id
    assert items[0]['title'] == 'Meu Grafo de Estudo'
    assert items[0]['payload']['preset'] == 'dag'
