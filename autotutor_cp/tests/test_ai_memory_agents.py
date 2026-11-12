"""Automated test validating the synthetic student agents AI Memory evaluation."""
import json
from scripts.evaluate_ai_memory_agents import run_experiment


def test_ai_memory_evaluation_experiment():
    results = run_experiment()
    assert results["metadata"]["safety_checks_passed"] is True
    metrics = results["metrics"]
    assert metrics["retention_recall_rate_baseline"] == 0.0
    assert metrics["retention_recall_rate_ai_memory"] == 1.0
    assert metrics["zero_leakage_compliance"] == 1.0
    assert metrics["false_mastery_attribution_rate"] == 0.0
    assert metrics["avg_consolidation_time_ms"] < 600.0
    assert metrics["avg_brief_size_chars"] <= 1200
    assert len(results["sessions"]) == 6
    for session in results["sessions"]:
        assert session["ai_memory_retained_gap"] is True
        assert session["safety_verified"] is True
        assert "progresso.md" in session["consolidated_pages"]
        assert "handoff.md" in session["consolidated_pages"]
        assert any("topicos/" in page for page in session["consolidated_pages"])
