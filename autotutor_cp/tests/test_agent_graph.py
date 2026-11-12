"""Tests for LangGraph Multi-Agent Collaboration and Akita AI-Memory integration."""
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from core.progress_store import ProgressStore
from core.learner_memory import LearnerMemory
from core.codigen_tutor import CodigenTutor
from core.autocode_engine import AutoCodeEngine
from core.agent_graph import build_collaborative_graph, run_collaborative_agent_graph
from core.agent_nodes import _ensure_valid_profile_id


def test_ensure_valid_profile_id():
    uuid_hex = "c3c9024f085b4f4c83120167003900a8"
    assert _ensure_valid_profile_id(uuid_hex) == uuid_hex

    deterministic_id = _ensure_valid_profile_id("user_test_123")
    assert len(deterministic_id) == 32
    assert _ensure_valid_profile_id("user_test_123") == deterministic_id


def test_langgraph_diagnostic_to_tutor_pipeline():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "progress.sqlite3"
        store = ProgressStore(db_path)
        mem = LearnerMemory(store)

        mock_llm = MagicMock()
        mock_llm.complete.return_value = "Como você está calculando o sentinela no índice 0?"

        tutor = CodigenTutor(mock_llm)
        autocode = MagicMock()

        graph = build_collaborative_graph(mem, mock_llm, tutor, autocode)

        state = {
            "student_id": "test_student",
            "topic": "Soma de prefixos",
            "user_message": "Por que meu código deu Wrong Answer?",
            "action": "diagnose",
            "code": "int query(int L, int R) { return pref[R] - pref[L]; }",
            "judge_result": {"verdict": "Wrong Answer", "failed_case": 2},
            "agent_trail": []
        }

        config = {"configurable": {"thread_id": "test_thread_1"}}
        result = graph.invoke(state, config=config)

        # Verify all expected agents collaborated in sequence
        trail = result.get("agent_trail", [])
        assert "ai_memory_recall" in trail
        assert "diagnostic_agent" in trail
        assert "socratic_tutor_agent" in trail
        assert "ai_memory_consolidate" in trail

        # Verify cross-agent input passing: diagnostic output was produced and fed into tutor
        assert result.get("diagnostic_output") is not None
        assert "sentinela" in result["diagnostic_output"]["diagnosis"].lower()
        assert result.get("final_reply") != ""


def test_langgraph_drill_generation_chain():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "progress.sqlite3"
        store = ProgressStore(db_path)

        payload = {
            "student_id": "student_alpha",
            "topic": "BFS e Grafos",
            "message": "Quero um exercício para praticar inicialização com sentinela.",
            "action": "problem",
            "code": "int dist[100];",
            "judge_result": {"verdict": "Wrong Answer"}
        }

        result = run_collaborative_agent_graph(payload, store)
        trail = result.get("agent_trail", [])

        assert "ai_memory_recall" in trail
        assert "problem_generator_agent" in trail
        assert "socratic_tutor_agent" in trail
        assert "ai_memory_consolidate" in trail
        assert result.get("problem_output") is not None
        assert "BFS" in result["problem_output"].get("topic", "") or "Grafos" in result["problem_output"].get("topic", "")


def test_akita_memory_persistence_across_collaborative_chats():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "progress.sqlite3"
        store = ProgressStore(db_path)
        mem = LearnerMemory(store)

        profile_id = _ensure_valid_profile_id("student_beta")

        # Session 1: Student gets diagnosed and Akita saves the handoff
        payload_1 = {
            "student_id": profile_id,
            "topic": "Soma de prefixos",
            "message": "Estou com WA em consultas cumulativas.",
            "action": "diagnose",
            "code": "int ans = p[r] - p[l];",
            "judge_result": {"verdict": "Wrong Answer"}
        }
        res_1 = run_collaborative_agent_graph(payload_1, store)
        assert "ai_memory_consolidate" in res_1["agent_trail"]

        # Check that Akita Markdown files were generated on disk
        profile_dir = Path(tmpdir) / "memory" / profile_id
        assert (profile_dir / "memoria.md").exists()
        assert (profile_dir / "handoff.md").exists()

        # Session 2: A different chat begins. It recalls the previous struggle!
        payload_2 = {
            "student_id": profile_id,
            "topic": "Soma de prefixos",
            "message": "Quero tentar de novo.",
            "action": "auto"
        }
        res_2 = run_collaborative_agent_graph(payload_2, store)
        assert res_2.get("recalled_memory") is not None
