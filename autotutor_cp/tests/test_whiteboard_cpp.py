"""QA Test Suite for C++ Whiteboard Code Validation and Execution."""
from __future__ import annotations

from core.cpp_whiteboard_executor import (
    is_candidate_cpp_code,
    build_cpp_harness,
    validate_cpp_syntax,
    execute_cpp_whiteboard
)


def test_ac1_non_code_detection():
    """AC-1: Non-code notes should be cleanly identified as not_code."""
    plain_text = "Neste grafo precisamos encontrar a distância mínima entre a fonte 1 e o destino 5."
    assert is_candidate_cpp_code(plain_text) is False

    val = validate_cpp_syntax(plain_text)
    assert val["is_valid_cpp"] is False
    assert val["status"] == "not_code"
    assert "não possui estrutura de código C++" in val["message"]


def test_ac2_syntax_error_detection():
    """AC-2: Flawed C++ code should yield syntax_error with g++ output."""
    flawed_code = "int main() { int x = ; return 0; }"
    val = validate_cpp_syntax(flawed_code)
    assert val["is_valid_cpp"] is False
    assert val["status"] == "syntax_error"
    assert "error" in val["message"].lower() or "expected" in val["message"].lower()


def test_ac3_valid_full_cpp_program():
    """AC-3: Full C++ code with main() compiles and executes cleanly."""
    valid_code = (
        "#include <iostream>\n"
        "using namespace std;\n"
        "int main() {\n"
        "    cout << \"Whiteboard Graph Executed\" << endl;\n"
        "    return 0;\n"
        "}\n"
    )
    nodes = [{"id": "1", "label": "1"}, {"id": "2", "label": "2"}]
    edges = [{"from": "1", "to": "2", "directed": True}]

    res = execute_cpp_whiteboard(valid_code, nodes, edges, start_node="1")
    assert res["is_valid_cpp"] is True
    assert res["compilation_status"] == "compiled"
    assert "Whiteboard Graph Executed" in res["execution_output"]
    assert len(res["tape"]) > 0


def test_ac4_bare_function_auto_harness():
    """AC-4: Standalone CP functions without main() are auto-harnessed and compiled."""
    bare_bfs = (
        "void bfs(int start_node, const vector<vector<int>>& adj) {\n"
        "    queue<int> q;\n"
        "    q.push(start_node);\n"
        "}\n"
    )
    val = validate_cpp_syntax(bare_bfs)
    assert val["is_valid_cpp"] is True
    assert val["status"] == "compiled"


def test_ac5_infinite_loop_timeout_protection():
    """AC-5: Code with infinite loops must be terminated gracefully by timeout."""
    loop_code = (
        "int main() {\n"
        "    while(true) {}\n"
        "    return 0;\n"
        "}\n"
    )
    nodes = [{"id": "1"}]
    edges = []

    res = execute_cpp_whiteboard(loop_code, nodes, edges, timeout_sec=0.4)
    assert res["compilation_status"] == "timeout"
    assert "Timeout" in res["compiler_message"] or "TLE" in res["compiler_message"]


def test_ac6_memory_limit_containment():
    """AC-6: Memory-bomb C++ code allocating mass gigabytes must be safely trapped by RLIMIT_AS."""
    memory_bomb_code = (
        "#include <iostream>\n"
        "#include <vector>\n"
        "using namespace std;\n"
        "int main() {\n"
        "    vector<int*> v;\n"
        "    while (true) {\n"
        "        v.push_back(new int[1000000]);\n"
        "    }\n"
        "    return 0;\n"
        "}\n"
    )
    nodes = [{"id": "1", "label": "1"}]
    edges = []

    res = execute_cpp_whiteboard(memory_bomb_code, nodes, edges, timeout_sec=2.0)
    assert res["is_valid_cpp"] is True
    assert res["compilation_status"] == "runtime_error"
    assert "memória" in res["compiler_message"].lower() or "bad_alloc" in res["compiler_message"].lower() or "mle" in res["compiler_message"].lower()
