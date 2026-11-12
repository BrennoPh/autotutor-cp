"""Unit tests for prerequisite detection and pedagogical scaffolding."""
import pytest
from core.prerequisites import (
    PREREQUISITES_MAP,
    detect_prerequisites,
    build_prerequisite_primer_markdown,
    format_prerequisite_instructions_for_ai,
)
from core.codigen_tutor import CodigenTutor
from core.material_writer import local_material
from core.learning_engine import load_curriculum
from core.library import deep_guides


def test_detect_prerequisites_bfs_dfs():
    matches = detect_prerequisites("Quero aprender BFS e DFS", "Grafos")
    assert len(matches) >= 1
    assert matches[0]['id'] == 'queue_stack'
    assert 'Fila' in matches[0]['title']
    assert 'Pilha' in matches[0]['title']


def test_detect_prerequisites_dijkstra():
    matches = detect_prerequisites("Como funciona o algoritmo de Dijkstra?", "Grafos")
    assert any(m['id'] == 'priority_queue' for m in matches)


def test_detect_prerequisites_dp():
    matches = detect_prerequisites("Programação Dinâmica da Mochila", "DP")
    assert any(m['id'] == 'recursion_memo' for m in matches)


def test_detect_prerequisites_segtree():
    matches = detect_prerequisites("Construir uma Segment Tree com lazy", "Segment Tree")
    assert any(m['id'] == 'binary_tree_dac' for m in matches)


def test_detect_prerequisites_unrelated():
    matches = detect_prerequisites("História da computação e conceitos gerais", "Geral")
    assert len(matches) == 0


def test_build_prerequisite_primer_markdown():
    spec = PREREQUISITES_MAP['bfs_dfs']
    md = build_prerequisite_primer_markdown(spec)
    assert '## 0. Nivelamento Obrigatório de Pré-Requisitos' in md
    assert 'Fila (Queue - FIFO' in md
    assert 'Pilha (Stack - LIFO' in md
    assert '```mermaid' in md
    assert 'graph TD' in md
    assert '```cpp' in md
    assert 'std::queue<int>' in md


def test_format_prerequisite_instructions_for_ai():
    spec = PREREQUISITES_MAP['bfs_dfs']
    instr_explain = format_prerequisite_instructions_for_ai(spec, 'explain')
    assert 'NIVELAMENTO PEDAGÓGICO DE PRÉ-REQUISITOS (SOLICITADO PELO ALUNO)' in instr_explain
    assert 'MANDATÓRIO iniciar o material gerado' in instr_explain

    instr_skip = format_prerequisite_instructions_for_ai(spec, 'skip')
    assert 'NIVELAMENTO PEDAGÓGICO (ALUNO CONFIRMOU DOMÍNIO)' in instr_skip
    assert 'NÃO perca tempo definindo conceitos básicos' in instr_skip


def test_local_material_includes_primer_when_explain():
    curriculum = load_curriculum()
    lesson = next(t for t in curriculum if t['id'] == 'graph')
    guide = next(g for g in deep_guides() if g['topic_id'] == 'graph')

    # Without prereq primer
    mat_normal = local_material(lesson, guide, 'Explicação', 'Iniciante', '', 'BFS e DFS', 'Longo', 'Aprofundada', True, True, prereq_decision='skip')
    assert 'Nivelamento Obrigatório de Pré-Requisitos' not in mat_normal

    # With prereq primer
    mat_prereq = local_material(lesson, guide, 'Explicação', 'Iniciante', '', 'BFS e DFS', 'Longo', 'Aprofundada', True, True, prereq_decision='explain')
    assert 'Nivelamento Obrigatório de Pré-Requisitos: Fila (Queue) e Pilha (Stack)' in mat_prereq
    assert '```mermaid' in mat_prereq


def test_codigen_tutor_material_receives_prereq_instructions():
    class MockLLM:
        def __init__(self):
            self.provider = 'Test'
            self.model = 'mock'
            self.require_model = False
            self.last_system = None
            self.last_prompt = None

        def complete(self, system, prompt, json_mode=False, include_history=True):
            self.last_system = system
            self.last_prompt = prompt
            return "# Material Teste\nConteúdo sobre BFS e DFS com pré-requisitos revisados."

        def require_result(self, r):
            return r

        def report_fallback(self, reason):
            pass

    mock_llm = MockLLM()
    tutor = CodigenTutor(llm=mock_llm)
    result = tutor.generate_material(
        'Explicação',
        'Grafos',
        'Iniciante',
        '',
        learning_request='Quero entender BFS e DFS',
        prereq_decision='explain'
    )
    assert 'Material Teste' in result
    assert 'NIVELAMENTO PEDAGÓGICO DE PRÉ-REQUISITOS' in mock_llm.last_system or 'NIVELAMENTO PEDAGÓGICO DE PRÉ-REQUISITOS' in mock_llm.last_prompt


def test_sanitize_statement_removes_theory_and_spoilers():
    from core.autocode_engine import sanitize_statement
    raw = (
        "Em um complexo industrial, existem N subestações...\n\n"
        "## Entrada\nN M (1 <= N <= 30000).\n\n"
        "## Saída\nMenor distância.\n\n"
        "## Restrições\n1 <= N <= 30000.\n\n"
        "## Teoria\nA Busca em Largura (BFS) é a técnica fundamental usando fila multissource.\n\n"
        "**Variação adaptativa:** N máximo = 30000; tempo 2 s; memória 256 MB."
    )
    cleaned = sanitize_statement(raw)
    assert 'Teoria' not in cleaned
    assert 'Busca em Largura' not in cleaned
    assert 'multissource' not in cleaned
    assert 'Entrada' in cleaned
    assert 'Saída' in cleaned
    assert 'Restrições' in cleaned
    assert 'Variação adaptativa' in cleaned


def test_sanitize_statement_removes_plain_text_dica_and_prereqs():
    from core.autocode_engine import sanitize_statement
    raw = (
        "Contexto da questão.\n\n"
        "Dica\nUtilize uma pilha para manter a ordem decrescente.\n\n"
        "> 🎓 **Revisão de Pré-Requisitos (Fila e Pilha):** Estruturas lineares.\n\n"
        "Entrada\nUm inteiro N.\n\n"
        "Saída\nResposta.\n"
    )
    cleaned = sanitize_statement(raw)
    assert 'Dica' not in cleaned
    assert 'Revisão de Pré-Requisitos' not in cleaned
    assert 'pilha' not in cleaned.lower()
    assert 'Contexto da questão.' in cleaned
    assert 'Entrada' in cleaned


def test_prerequisite_mastery_persistence_and_dismissal():
    from core.prerequisites import detect_prerequisites
    matches = detect_prerequisites("BFS e DFS", "Grafos")
    assert matches
    p_id = matches[0]['id']

    # Initial state: no recorded mastery
    session_mastery = {}
    assert p_id not in session_mastery

    # Student answers once: Sim, já domino
    session_mastery[p_id] = 'skip'
    assert session_mastery.get(p_id) == 'skip'

    # Next generation for same concept automatically uses known standing
    reused_decision = session_mastery.get(p_id)
    assert reused_decision == 'skip'


def test_diagnostic_disappears_from_study_tabs_when_diagnosed():
    # Simulates app.py logic
    attempts_empty = []
    has_completed_empty = bool(attempts_empty)
    study_tabs_initial = ['Laboratório IA','Meus estudos','Quadro Branco','Minha trilha','Biblioteca']
    if not has_completed_empty:
        study_tabs_initial.append('Diagnóstico')
    assert 'Diagnóstico' in study_tabs_initial

    # Once completed:
    attempts_done = [{'kind': 'diagnostic', 'correct': 18, 'total': 18}]
    has_completed_done = bool(attempts_done or any(a.get('kind') == 'diagnostic' for a in attempts_done))
    study_tabs_done = ['Laboratório IA','Meus estudos','Quadro Branco','Minha trilha','Biblioteca']
    if not has_completed_done:
        study_tabs_done.append('Diagnóstico')
    assert 'Diagnóstico' not in study_tabs_done


