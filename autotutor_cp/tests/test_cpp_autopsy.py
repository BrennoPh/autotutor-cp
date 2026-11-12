"""Suíte de Testes Automatizados para a Autópsia Algorítmica e Time-Machine C++.

Homologa os critérios de aceite [AC-1 a AC-4] definidos na especificação técnica.
"""
import pytest
from starlette.testclient import TestClient
from core.cpp_autopsy_engine import (
    generate_algorithmic_autopsy,
    run_bfs_autopsy,
    run_dfs_autopsy,
    build_adjacency,
)
from api_server import app


@pytest.fixture
def sample_graph():
    nodes = [{"id": "1", "label": "A"}, {"id": "2", "label": "B"}, {"id": "3", "label": "C"}]
    edges = [
        {"from": "1", "to": "2", "directed": True},
        {"from": "2", "to": "3", "directed": True},
    ]
    return nodes, edges


def test_ac1_build_adjacency(sample_graph):
    nodes, edges = sample_graph
    adj = build_adjacency(nodes, edges)
    assert "1" in adj
    assert adj["1"] == ["2"]
    assert adj["2"] == ["3"]
    assert adj["3"] == []


def test_ac2_bfs_timeline_generation(sample_graph):
    nodes, edges = sample_graph
    adj = build_adjacency(nodes, edges)
    result = run_bfs_autopsy(adj, start_node="1")

    assert result["status"] == "success"
    assert result["total_steps"] > 0
    assert result["failure_step"] is None

    # Verifica que todos os nós foram visitados
    timeline = result["timeline"]
    visited_nodes = set(timeline[-1]["visited"])
    assert visited_nodes == {"1", "2", "3"}


def test_ac3_dfs_cycle_detection():
    # Grafo com ciclo: 1 -> 2 -> 3 -> 1
    nodes = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
    edges = [
        {"from": "1", "to": "2", "directed": True},
        {"from": "2", "to": "3", "directed": True},
        {"from": "3", "to": "1", "directed": True},
    ]
    adj = build_adjacency(nodes, edges)
    result = run_dfs_autopsy(adj, start_node="1")

    assert result["status"] == "success"
    # Evento de ciclo deve ter sido registrado
    cycle_events = [f for f in result["timeline"] if f["event"] == "back_edge_cycle"]
    assert len(cycle_events) >= 1
    assert cycle_events[0]["variables"]["cycle_detected"] is True


def test_ac4_tle_containment():
    # Grafo em loop infinito simulado com limite estrito de 5 passos
    nodes = [{"id": "1"}, {"id": "2"}]
    edges = [
        {"from": "1", "to": "2", "directed": False},
        {"from": "2", "to": "1", "directed": False},
    ]
    adj = build_adjacency(nodes, edges)
    result = run_bfs_autopsy(adj, start_node="1", max_steps=4)

    assert result["status"] == "tle"
    assert result["failure_step"] is not None
    assert "Limite" in result["failure_reason"]


def test_ac5_autopsy_endpoint_api(sample_graph):
    nodes, edges = sample_graph
    client = TestClient(app)

    payload = {
        "code_text": "#include <iostream>\nusing namespace std;\nint main() { cout << 42 << endl; return 0; }",
        "nodes": nodes,
        "edges": edges,
        "algorithm": "bfs",
        "start_node": "1",
        "max_steps": 100
    }
    response = client.post("/api/whiteboard/autopsy", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    assert "timeline" in data
    assert len(data["timeline"]) > 0
    assert data["cpp_validation"]["is_valid_cpp"] is True
