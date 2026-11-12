"""Automated tests for Socratic Hint Ladder, Zero-Leak Guardrails and Pre-Flight Evaluation.

Validates RAG attribution, LearnerMemory adaptation, and API server endpoints
as specified in .ai-memory/handoffs/spec-atual.md for the FIA coursework.
"""
import pytest
from unittest.mock import MagicMock, patch
from starlette.testclient import TestClient

from core.socratic_ladder import (
    verify_zero_leak,
    extract_memory_insight,
    generate_fallback_hint,
    evaluate_complexity_preflight,
)
from core.codigen_tutor import CodigenTutor
from api_server import app


@pytest.fixture
def sample_problem():
    return {
        "id": "cses_1666",
        "title": "Construção de Estradas",
        "topic": "Grafos",
        "family": "graph",
        "statement": "Dado um grafo com N cidades e M estradas, determine o número mínimo de novas estradas.",
        "complexity": "O(N + M)",
        "constraints": {"n_max": 200000},
        "time_limit_sec": 1.0,
        "math_essence": "Componentes conexas em grafo não-direcionado.",
        "approach_summary": "BFS/DFS para contar componentes conexas; conectar representantes com C-1 arestas.",
    }


@pytest.fixture
def sample_rag_refs():
    return [
        {
            "id": "kb_cses_ch11",
            "title": "Competitive Programmer's Handbook · Cap. 11: Fundamentos de Grafos",
            "publisher": "CSES / Antti Laaksonen",
            "url": "https://cses.fi/book/book.pdf?chapter=11-graph-basics",
        },
        {
            "id": "kb_erickson_ch5",
            "title": "Algorithms · Chapter 5: Graph Traversal",
            "publisher": "Jeff Erickson",
            "url": "https://jeffe.cs.illinois.edu/teaching/algorithms/book/05-graphs.pdf",
        },
    ]


# ============================================================================
# 1. Zero-Leak Guardrail Unit Tests
# ============================================================================

def test_zero_leak_blocks_includes_and_main():
    bad_snippets = [
        "#include <iostream>\nint main() { return 0; }",
        "void main() { std::cout << 42; }",
        "Aqui está sua solução:\n```cpp\nint main() {\n  return 0;\n}\n```",
        "using namespace std; vector<int> v;",
    ]
    for snippet in bad_snippets:
        is_safe, reason = verify_zero_leak(snippet, tier=1)
        assert not is_safe, f"Deveria ter bloqueado snippet: {snippet}"
        assert len(reason) > 0


def test_zero_leak_blocks_multiline_code_in_tiers_1_to_3():
    code_block = (
        "Pense nisso:\n"
        "```cpp\n"
        "int x = 10;\n"
        "int y = 20;\n"
        "int z = x + y;\n"
        "```"
    )
    is_safe, reason = verify_zero_leak(code_block, tier=2)
    assert not is_safe
    assert "restrito" in reason.lower() or "executável" in reason.lower()


def test_zero_leak_allows_socratic_prose_and_math():
    good_text = (
        "Considere a invariante: em um grafo com $C$ componentes conexos, "
        "quantas arestas adicionais são estritamente necessárias para tornar o grafo uniconexo? "
        "Pense no princípio de uma Árvore Geradora Mínima."
    )
    is_safe, reason = verify_zero_leak(good_text, tier=1)
    assert is_safe
    assert reason == ""


# ============================================================================
# 2. Graduated 4-Tier Ladder Progression Tests
# ============================================================================

def test_graduated_ladder_progression_tiers_1_to_4(sample_problem, sample_rag_refs):
    tutor = CodigenTutor(llm=None)

    # Tier 1
    h1 = tutor.generate_graduated_hint(sample_problem, tier=1, rag_refs=sample_rag_refs)
    assert h1["tier"] == 1
    assert h1["next_tier_available"] == 2
    assert "Invariante" in h1["hint_markdown"] or "Teorema" in h1["hint_markdown"]
    assert h1["zero_leak_verified"] is True
    assert len(h1["rag_citations"]) == 2

    # Tier 2
    h2 = tutor.generate_graduated_hint(sample_problem, tier=2, rag_refs=sample_rag_refs)
    assert h2["tier"] == 2
    assert h2["next_tier_available"] == 3
    assert "Casos de Borda" in h2["hint_markdown"] or "Mínimo" in h2["hint_markdown"]

    # Tier 3
    h3 = tutor.generate_graduated_hint(sample_problem, tier=3, rag_refs=sample_rag_refs)
    assert h3["tier"] == 3
    assert h3["next_tier_available"] == 4
    assert "Modelagem" in h3["hint_markdown"] or "Estruturas" in h3["hint_markdown"]

    # Tier 4
    h4 = tutor.generate_graduated_hint(sample_problem, tier=4, rag_refs=sample_rag_refs)
    assert h4["tier"] == 4
    assert h4["next_tier_available"] is None
    assert "Passos" in h4["hint_markdown"] or "Esqueleto" in h4["hint_markdown"]


# ============================================================================
# 3. Learner Memory Cognitive Adaptation Tests
# ============================================================================

def test_memory_adaptation_triggers():
    # Recursion/RE memory
    mem_re = {"recalled_pages": [{"excerpt": "Diagnóstico: falha com Runtime Error (RE) devido a recursão profunda na DFS"}]}
    trigger_re, adapt_re = extract_memory_insight(mem_re, "Grafos")
    assert "Runtime Error" in trigger_re or "recursão" in trigger_re
    assert "iterativa" in adapt_re or "parada" in adapt_re

    # TLE memory
    mem_tle = {"recalled_pages": [{"excerpt": "Observado TLE em caso grande; laços aninhados"}]}
    trigger_tle, adapt_tle = extract_memory_insight(mem_tle, "Grafos")
    assert "Time Limit" in trigger_tle or "TLE" in trigger_tle

    # WA/Overflow memory
    mem_wa = {"recalled_pages": [{"excerpt": "Submissão rejeitada com Wrong Answer em valores grandes de teste"}]}
    trigger_wa, adapt_wa = extract_memory_insight(mem_wa, "Grafos")
    assert "extremos" in trigger_wa or "WA" in trigger_wa or "Wrong Answer" in trigger_wa


# ============================================================================
# 4. Pre-Flight Complexity Evaluation Tests
# ============================================================================

def test_preflight_approves_viable_solution(sample_problem):
    res = evaluate_complexity_preflight(
        sample_problem,
        proposed_complexity="O(N + M)",
        chosen_structure="Lista de Adjacência",
        estimated_ops=400000,
    )
    assert res["status"] == "APPROVED"
    assert res["verdict_preview"] == "VIABLE"
    assert len(res["edge_cases_to_watch"]) >= 3


def test_preflight_warns_on_quadratic_complexity(sample_problem):
    res = evaluate_complexity_preflight(
        sample_problem,
        proposed_complexity="O(N^2)",
        chosen_structure="Busca exaustiva",
    )
    assert res["verdict_preview"] == "TLE_RISK"
    assert res["status"] in ("WARNING", "REJECTED")


def test_preflight_detects_mle_on_dense_matrix_for_sparse_graph(sample_problem):
    res = evaluate_complexity_preflight(
        sample_problem,
        proposed_complexity="O(N + M)",
        chosen_structure="Matriz de Adjacência",
    )
    assert res["status"] == "WARNING"
    assert res["verdict_preview"] == "MLE_RISK"
    assert "Memória" in res["feedback"] or "MLE" in res["feedback"]


# ============================================================================
# 5. API Server Integration Tests
# ============================================================================

def test_api_hints_endpoint_success():
    client = TestClient(app)
    response = client.post("/api/tutor/hints", json={
        "problem_id": "graph",
        "tier": 1,
        "user_query": "Não sei como começar",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["tier"] == 1
    assert data["zero_leak_verified"] is True
    assert isinstance(data["rag_citations"], list)
    assert len(data["title"]) > 0


def test_api_hints_endpoint_zero_leak_fallback_when_llm_leaks():
    client = TestClient(app)
    leaked_llm_reply = "#include <iostream>\nint main() { std::cout << 'cheat'; return 0; }"

    with patch("core.llm_client.LLMClient.complete", return_value=leaked_llm_reply):
        response = client.post("/api/tutor/hints", json={
            "problem_id": "graph",
            "tier": 1,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["zero_leak_verified"] is True
        assert "#include" not in data["hint_markdown"]
        assert "main()" not in data["hint_markdown"]


def test_api_preflight_endpoint_success():
    client = TestClient(app)
    response = client.post("/api/tutor/preflight", json={
        "problem_id": "graph",
        "proposed_complexity": "O(V + E)",
        "chosen_structure": "Lista de Adjacência",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "APPROVED"
    assert data["verdict_preview"] == "VIABLE"
    assert "edge_cases_to_watch" in data
