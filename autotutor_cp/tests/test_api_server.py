"""Automated endpoint tests for AutoTutor CP REST API Gateway (api_server.py)."""
import pytest
from starlette.testclient import TestClient
from unittest.mock import patch, MagicMock

from autotutor_cp.api_server import app
from core.progress_store import ProgressStore
from core.accounts import Accounts


@pytest.fixture
def isolated_client(tmp_path, monkeypatch):
    """Fixture que isola o banco de dados SQLite para cada teste em tmp_path."""
    test_db = tmp_path / "test_api_progress.sqlite3"
    temp_store = ProgressStore(str(test_db))
    monkeypatch.setattr("autotutor_cp.api_server.store", temp_store)
    monkeypatch.setattr("autotutor_cp.api_server.accounts", Accounts(temp_store))
    client = TestClient(app)
    return client


class TestJudgeEndpoints:
    """Suíte de validação de submissão do juiz (/api/judge/submit)."""

    def test_submit_empty_body_returns_400(self, isolated_client):
        resp = isolated_client.post("/api/judge/submit", json={})
        assert resp.status_code == 400
        assert "obrigatórios" in resp.json().get("error", "")

    def test_submit_missing_source_code_returns_400(self, isolated_client):
        resp = isolated_client.post("/api/judge/submit", json={"problem_id": "prefix"})
        assert resp.status_code == 400

    def test_submit_nonexistent_problem_returns_404(self, isolated_client):
        resp = isolated_client.post("/api/judge/submit", json={
            "problem_id": "problema_inexistente_9999",
            "source_code": "int main() {}",
            "language": "cpp"
        })
        assert resp.status_code == 404
        assert "não encontrado" in resp.json().get("error", "")

    def test_submit_cpp_ac_mocked(self, isolated_client):
        """Valida que o contrato JSON de sucesso para C++ respeita o schema de produção."""
        mock_result = {
            "verdict": "AC",
            "tests": [
                {
                    "test_id": 1,
                    "execution_time_ms": 12.5,
                    "verdict": "AC",
                    "input": "4 3\n1 2 3 4\n1 4\n2 3\n4 4\n",
                    "expected_output": "10\n5\n4\n",
                    "actual_output": "10\n5\n4\n",
                    "stderr": ""
                }
            ],
            "failed_test": None,
            "message": "Todos os testes passaram."
        }

        with patch("autotutor_cp.api_server.MiniJudge.judge", return_value=mock_result):
            resp = isolated_client.post("/api/judge/submit", json={
                "problem_id": "prefix",
                "source_code": '#include <iostream>\nint main(){ std::cout << "10\\n5\\n4\\n"; return 0; }',
                "language": "cpp"
            })

            assert resp.status_code == 200
            data = resp.json()
            assert data["verdict"] == "AC"
            assert data["tests_passed"] == 1
            assert data["total_tests"] == len(data["tests"]) or data["total_tests"] > 0
            assert data["failed_test"] is None

    def test_submit_cpp_tle_mocked(self, isolated_client):
        """Valida emissão de TLE quando o juiz sinaliza timeout."""
        mock_result = {
            "verdict": "TLE",
            "tests": [
                {
                    "test_id": 1,
                    "execution_time_ms": 2005.0,
                    "verdict": "TLE",
                    "input": "4 3\n1 2 3 4\n1 4\n2 3\n4 4\n",
                    "expected_output": "10\n5\n4\n",
                    "actual_output": "",
                    "stderr": "Tempo limite excedido."
                }
            ],
            "failed_test": {
                "test_id": 1,
                "execution_time_ms": 2005.0,
                "verdict": "TLE"
            },
            "message": "Tempo limite excedido."
        }

        with patch("autotutor_cp.api_server.MiniJudge.judge", return_value=mock_result):
            resp = isolated_client.post("/api/judge/submit", json={
                "problem_id": "prefix",
                "source_code": "int main() { while(true); }",
                "language": "cpp"
            })

            assert resp.status_code == 200
            data = resp.json()
            assert data["verdict"] == "TLE"
            assert data["failed_test"] is not None

    def test_submit_python_ac(self, isolated_client):
        """Execução real de Python com código correto passando pelo runner com limites."""
        valid_py = """import sys
data = sys.stdin.read().split()
if data:
    n, q = int(data[0]), int(data[1])
    arr = [int(x) for x in data[2:2+n]]
    pref = [0] * (n + 1)
    for i in range(n):
        pref[i+1] = pref[i] + arr[i]
    idx = 2 + n
    for _ in range(q):
        l, r = int(data[idx]), int(data[idx+1])
        idx += 2
        print(pref[r] - pref[l-1])
"""
        resp = isolated_client.post("/api/judge/submit", json={
            "problem_id": "prefix",
            "source_code": valid_py,
            "language": "python"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["verdict"] == "AC"
        assert data["tests_passed"] > 0
        assert data["failed_test"] is None

    def test_submit_python_mle(self, isolated_client):
        """Execução de Python que estoura limites de memória deve retornar veredito canônico MLE."""
        mle_py = """
a = [0] * (10**9)
print('10')
"""
        resp = isolated_client.post("/api/judge/submit", json={
            "problem_id": "prefix",
            "source_code": mle_py,
            "language": "python"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["verdict"] == "MLE"
        assert data["failed_test"] is not None
        assert "memória" in data["message"].lower() or "mle" in data["message"].lower()

    def test_submit_python_tle(self, isolated_client):
        """Execução de Python que entra em loop infinito deve retornar TLE."""
        tle_py = """
while True:
    pass
"""
        resp = isolated_client.post("/api/judge/submit", json={
            "problem_id": "prefix",
            "source_code": tle_py,
            "language": "python"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["verdict"] == "TLE"
        assert data["failed_test"] is not None


class TestProblemEndpoints:
    """Valida catálogo de problemas (/api/problems)."""

    def test_list_problems_returns_200(self, isolated_client):
        resp = isolated_client.get("/api/problems")
        assert resp.status_code == 200
        data = resp.json()
        assert "problems" in data
        assert isinstance(data["problems"], list)
        assert len(data["problems"]) > 0

    def test_get_problem_detail_valid(self, isolated_client):
        resp = isolated_client.get("/api/problems/prefix")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "prefix"
        assert "title" in data
        assert "statement" in data

    def test_get_problem_detail_aliases_resolve_correctly(self, isolated_client):
        """Aliases históricos e de trilhas devem resolver diretamente para o problema correto sem 404."""
        aliases = [
            ("binary_search", "binary"),
            ("binary_tree_lca", "tree"),
            ("trees", "tree"),
            ("greedy_interval_scheduling", "greedy"),
            ("prefix_sum_ranges", "prefix"),
            ("recursion", "tree"),
        ]
        for alias, target_id in aliases:
            resp = isolated_client.get(f"/api/problems/{alias}")
            assert resp.status_code == 200, f"Alias {alias} retornou status {resp.status_code}"
            data = resp.json()
            assert data["id"] == target_id, f"Alias {alias} esperava ID {target_id}, recebeu {data['id']}"

    def test_get_problem_detail_not_found(self, isolated_client):
        resp = isolated_client.get("/api/problems/nao_existe")
        assert resp.status_code == 404


class TestProgressEndpoints:
    """Valida otimização de payload e desacoplamento em /api/progress e /api/progress/materials."""

    def test_progress_default_returns_lightweight_payload(self, isolated_client):
        from autotutor_cp.api_server import store
        pid = "c3c9024f085b4f4c83120167003900a8"
        store.save(pid, {"history": [], "study_hours": 3, "level": "Intermediário"})
        # Seed 46 materials to simulate production workload
        for i in range(46):
            store.add_artifact(pid, "material", f"Material {i}", {
                "concept": "Grafos",
                "markdown": "# Conteúdo Extenso\n" + ("Linha de estudo detalhada com explicações teóricas.\n" * 100)
            })

        resp = isolated_client.get("/api/progress", headers={"x-profile-id": pid})
        assert resp.status_code == 200
        data = resp.json()

        # Payload must be lightweight (< 2 KB)
        assert len(resp.content) < 2048, f"Payload size was {len(resp.content)} bytes, expected < 2048"

        # Check fields
        assert data["materials_count"] == 46
        assert "materials" in data
        assert "saved_materials" in data
        assert len(data["materials"]) <= 5

        # Check lightweight schema
        first = data["materials"][0]
        assert "id" in first
        assert "title" in first
        assert "created_at" in first
        # Crucial: bulky payload or markdown should NOT be present in lightweight item
        assert "payload" not in first
        assert "data" not in first

    def test_progress_include_materials_returns_full_body(self, isolated_client):
        from autotutor_cp.api_server import store
        pid = "c3c9024f085b4f4c83120167003900a8"
        store.save(pid, {"history": [], "study_hours": 3, "level": "Intermediário"})
        store.add_artifact(pid, "material", "Material Detalhado", {
            "concept": "DP",
            "markdown": "# Programação Dinâmica\nMemoization e Tabulação."
        })

        resp = isolated_client.get("/api/progress?include_materials=true", headers={"x-profile-id": pid})
        assert resp.status_code == 200
        data = resp.json()
        assert data["materials_count"] >= 1
        first = data["materials"][0]
        assert "payload" in first
        assert "markdown" in first["payload"]
        # Duplicate data/payload object should be eliminated
        assert "data" not in first

    def test_progress_materials_endpoint_pagination(self, isolated_client):
        from autotutor_cp.api_server import store
        pid = "c3c9024f085b4f4c83120167003900a8"
        store.save(pid, {"history": [], "study_hours": 3, "level": "Intermediário"})
        for i in range(15):
            store.add_artifact(pid, "material", f"Material Pag {i}", {"index": i, "markdown": f"Doc {i}"})

        resp = isolated_client.get("/api/progress/materials?limit=5&offset=0", headers={"x-profile-id": pid})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 15
        assert len(data["materials"]) == 5
        assert "payload" in data["materials"][0]

    def test_progress_materials_detail_by_id(self, isolated_client):
        from autotutor_cp.api_server import store
        pid = "c3c9024f085b4f4c83120167003900a8"
        store.save(pid, {"history": [], "study_hours": 3, "level": "Intermediário"})
        mat_id = store.add_artifact(pid, "material", "Material Específico", {
            "concept": "SegTree",
            "markdown": "# SegTree Content"
        })

        resp = isolated_client.get(f"/api/progress/materials/{mat_id}", headers={"x-profile-id": pid})
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == mat_id
        assert data["title"] == "Material Específico"
        assert data["payload"]["concept"] == "SegTree"

    def test_toggle_lesson_completion_success(self, isolated_client):
        """Valida marcação e desmarcação de aulas concluídas com persistência em completed_lessons."""
        pid = "a1b2c3d4e5f60718293a4b5c6d7e8f90"
        # 1. Marca como concluída explicitamente
        resp = isolated_client.post(
            "/api/progress/lessons/complete",
            json={"lesson_id": "bfs_dfs_foundations", "completed": True},
            headers={"x-profile-id": pid}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["completed"] is True
        assert "bfs_dfs_foundations" in data["completed_lessons"]

        # 2. Verifica se GET /api/progress reflete a lição concluída
        prog_resp = isolated_client.get("/api/progress", headers={"x-profile-id": pid})
        assert prog_resp.status_code == 200
        prog_data = prog_resp.json()
        assert "completed_lessons" in prog_data
        assert "bfs_dfs_foundations" in prog_data["completed_lessons"]

        # 3. Adiciona outra lição via toggle
        resp2 = isolated_client.post(
            "/api/progress/lessons/complete",
            json={"lesson_id": "dijkstra_shortest_path"},
            headers={"x-profile-id": pid}
        )
        assert resp2.status_code == 200
        assert resp2.json()["completed"] is True
        assert "dijkstra_shortest_path" in resp2.json()["completed_lessons"]
        assert len(resp2.json()["completed_lessons"]) == 2

        # 4. Desmarca lição explicitamente com completed=False
        resp3 = isolated_client.post(
            "/api/progress/lessons/complete",
            json={"lesson_id": "bfs_dfs_foundations", "completed": False},
            headers={"x-profile-id": pid}
        )
        assert resp3.status_code == 200
        assert resp3.json()["completed"] is False
        assert "bfs_dfs_foundations" not in resp3.json()["completed_lessons"]
        assert "dijkstra_shortest_path" in resp3.json()["completed_lessons"]

    def test_toggle_lesson_completion_validation_errors(self, isolated_client):
        """Rejeita requisições com dados ausentes ou inválidos."""
        # Body vazio
        resp1 = isolated_client.post("/api/progress/lessons/complete", json={})
        assert resp1.status_code == 400

        # lesson_id vazio
        resp2 = isolated_client.post("/api/progress/lessons/complete", json={"lesson_id": "   "})
        assert resp2.status_code == 400

    def test_reset_profile_endpoint(self, isolated_client):
        """Valida que POST /api/progress/reset restaura o perfil para o estado inicial virgem."""
        from autotutor_cp.api_server import store
        pid = "a1b2c3d4e5f60718293a4b5c6d7e8f90"
        # Seed profile with data
        store.save(pid, {
            "history": [{"verdict": "AC"}],
            "study_hours": 10,
            "level": "Avançado",
            "completed_lessons": ["bfs_dfs_foundations"],
            "onboarding_completed": True,
            "diagnostic_score": 80,
            "material": "Conteúdo anterior",
        })
        store.add_artifact(pid, "material", "Material Teste", {"content": "ABC"})

        resp = isolated_client.post("/api/progress/reset", headers={"x-profile-id": pid})
        assert resp.status_code == 200
        assert resp.json()["success"] is True
        assert resp.json()["clear_client_storage"] is True

        # Check GET /api/progress after reset
        prog_resp = isolated_client.get("/api/progress", headers={"x-profile-id": pid})
        assert prog_resp.status_code == 200
        prog_data = prog_resp.json()
        assert prog_data["completed_lessons"] == []
        assert prog_data["onboarding_completed"] is False
        assert prog_data["diagnostic_score"] is None
        assert prog_data["materials_count"] == 0


class TestPerformanceAndCaching:
    """Valida caches em memória para catálogos estáticos e base de conhecimento."""

    def test_problem_bank_caching_and_clear(self):
        from core.problem_bank import load_problems, clear_cache
        clear_cache()
        info_before = load_problems.cache_info()
        p1 = load_problems()
        p2 = load_problems()
        assert p1 is p2
        info_after = load_problems.cache_info()
        assert info_after.hits >= 1

        clear_cache()
        info_cleared = load_problems.cache_info()
        assert info_cleared.hits == 0

    def test_library_caching_and_clear(self):
        from core.library import resources, deep_guides, clear_cache
        clear_cache()
        r1 = resources()
        r2 = resources()
        assert r1 is r2
        g1 = deep_guides()
        g2 = deep_guides()
        assert g1 is g2
        clear_cache()

    def test_knowledge_stats_caching_and_clear(self, tmp_path):
        from core.knowledge import KnowledgeBase
        kb = KnowledgeBase(tmp_path / "test_kb.sqlite3")
        # Empty stats cached
        s1 = kb.stats()
        s2 = kb.stats()
        assert s1 == s2
        kb.clear_stats_cache()


class TestAssessmentEndpoints:
    """Valida fluxo de onboarding e diagnóstico (/api/assessment)."""

    def test_submit_assessment_with_bearer_token(self, isolated_client):
        """Valida que o payload com IDs adaptativos pontua corretamente autenticado via Bearer token."""
        from autotutor_cp.api_server import accounts, store
        user_id = accounts.register("artursilveira", "Artur Silveira", "SenhaForte123")
        token = accounts.login("artursilveira", "SenhaForte123")
        user = accounts.user(user_id)
        pid = user["profile_id"]

        # Respostas do Artur: 1 acerto (q5=b), 4 erros
        payload = {
            "target_goal": "maratona",
            "hours_per_day": 2,
            "language": "cpp",
            "answers": {
                "q1_complexity": "a",
                "q2_recursion_stack": "b",
                "q3_bfs_queue": "a",
                "q4_dfs_cycles": "a",
                "q5_dp_memo": "b"
            }
        }
        resp = isolated_client.post(
            "/api/assessment/submit",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["score"] == 20
        assert data["level"] == "Iniciante"
        assert data["correct_count"] == 1
        assert data["total_questions"] == 5
        assert "Programação Dinâmica e Subestrutura Ótima" in data["strong_topics"]
        assert len(data["gap_topics"]) == 4

        # Verifica persistência no store vinculado ao usuário autenticado
        saved = store.load(pid)
        assert saved["onboarding_completed"] is True
        assert saved["diagnostic_score"] == 20
        assert saved["level"] == "Iniciante"
        assert "Programação Dinâmica e Subestrutura Ótima" in saved["strong_topics"]

    def test_submit_assessment_with_x_profile_id(self, isolated_client):
        """Valida avaliação com x-profile-id explícito e 100% de acertos."""
        import uuid
        from autotutor_cp.api_server import store
        pid = uuid.uuid4().hex
        store.save(pid, {"onboarding_completed": False, "level": "Novato"})

        payload = {
            "answers": {
                "q1_complexity": "b",
                "q2_recursion_stack": "c",
                "q3_bfs_queue": "c",
                "q4_dfs_cycles": "b",
                "q5_dp_memo": "b"
            }
        }
        resp = isolated_client.post(
            "/api/assessment/submit",
            json=payload,
            headers={"x-profile-id": pid}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["score"] == 100
        assert data["level"] == "Avançado"
        assert data["correct_count"] == 5
        assert len(data["strong_topics"]) == 5
        assert len(data["gap_topics"]) == 0

        saved = store.load(pid)
        assert saved["onboarding_completed"] is True
        assert saved["diagnostic_score"] == 100
        assert saved["level"] == "Avançado"

