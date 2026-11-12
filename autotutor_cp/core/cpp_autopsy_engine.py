"""Motor de Autópsia Algorítmica & Time-Machine para o Quadro Branco C++.

Permite viajar no tempo pela execução de algoritmos sobre grafos/estruturas,
registrando cada frame da fita temporal e diagnosticando o ponto exato de falha.
"""
from __future__ import annotations

from typing import Dict, Any, List, Optional, Set
from collections import deque
from core.cpp_whiteboard_executor import validate_cpp_syntax


def build_adjacency(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]]
) -> Dict[str, List[str]]:
    """Constrói lista de adjacência padronizada a partir dos nós e arestas."""
    adj: Dict[str, List[str]] = {str(n.get("id", "")): [] for n in nodes}
    for e in edges:
        u = str(e.get("from", e.get("source", e.get("u", ""))))
        v = str(e.get("to", e.get("target", e.get("v", ""))))
        directed = bool(e.get("directed", False))
        if u in adj:
            adj[u].append(v)
        else:
            adj[u] = [v]
        if not directed:
            if v in adj:
                adj[v].append(u)
            else:
                adj[v] = [u]
    return adj


def run_bfs_autopsy(
    adj: Dict[str, List[str]],
    start_node: str,
    max_steps: int = 150
) -> Dict[str, Any]:
    """Gera a fita temporal completa para o algoritmo BFS."""
    timeline: List[Dict[str, Any]] = []
    visited: Set[str] = set()
    queue: deque[str] = deque([start_node])
    visited.add(start_node)

    step = 0
    timeline.append({
        "step": step,
        "event": "init",
        "active_node": start_node,
        "active_edge": None,
        "variables": {"queue_size": len(queue), "curr": start_node},
        "visited": list(visited),
        "explanation": f"Inicializando BFS a partir do nó raiz '{start_node}'."
    })

    failure_step = None
    failure_reason = None

    while queue:
        step += 1
        if step > max_steps:
            failure_step = step - 1
            failure_reason = "Limite máximo de passos excedido (potencial ciclo infinito ou TLE)."
            break

        curr = queue.popleft()
        neighbors = adj.get(curr, [])

        timeline.append({
            "step": step,
            "event": "dequeue",
            "active_node": curr,
            "active_edge": None,
            "variables": {"queue_size": len(queue), "curr": curr, "neighbors_count": len(neighbors)},
            "visited": list(visited),
            "explanation": f"Processando vértice '{curr}'. Explorando {len(neighbors)} vizinho(s)."
        })

        for nxt in neighbors:
            step += 1
            if step > max_steps:
                failure_step = step - 1
                failure_reason = "Limite máximo de passos excedido durante expansão de arestas."
                break

            edge_key = f"{curr}->{nxt}"
            if nxt not in visited:
                visited.add(nxt)
                queue.append(nxt)
                timeline.append({
                    "step": step,
                    "event": "visit_edge",
                    "active_node": nxt,
                    "active_edge": {"from": curr, "to": nxt},
                    "variables": {"queue_size": len(queue), "visiting": nxt},
                    "visited": list(visited),
                    "explanation": f"Aresta ({curr} -> {nxt}) percorrida. Vértice '{nxt}' enfileirado."
                })
            else:
                timeline.append({
                    "step": step,
                    "event": "cross_edge",
                    "active_node": curr,
                    "active_edge": {"from": curr, "to": nxt},
                    "variables": {"queue_size": len(queue), "already_visited": nxt},
                    "visited": list(visited),
                    "explanation": f"Aresta cruzada: vértice '{nxt}' já foi visitado previamente."
                })

        if failure_step is not None:
            break

    return {
        "status": "tle" if failure_step is not None else "success",
        "total_steps": len(timeline),
        "failure_step": failure_step,
        "failure_reason": failure_reason,
        "timeline": timeline
    }


def run_dfs_autopsy(
    adj: Dict[str, List[str]],
    start_node: str,
    max_steps: int = 150
) -> Dict[str, Any]:
    """Gera a fita temporal de autópsia para o algoritmo DFS com detecção de ciclos."""
    timeline: List[Dict[str, Any]] = []
    visited: Set[str] = set()
    in_stack: Set[str] = set()
    step = 0
    failure_step = None
    failure_reason = None

    def dfs(u: str, parent: Optional[str] = None):
        nonlocal step, failure_step, failure_reason
        step += 1
        if step > max_steps:
            failure_step = step - 1
            failure_reason = "Limite máximo de profundidade ou passos excedido (TLE)."
            return

        visited.add(u)
        in_stack.add(u)

        timeline.append({
            "step": step,
            "event": "enter_dfs",
            "active_node": u,
            "active_edge": {"from": parent, "to": u} if parent else None,
            "variables": {"current_node": u, "parent": parent, "stack_depth": len(in_stack)},
            "visited": list(visited),
            "explanation": f"Entrando na chamada recursiva para o vértice '{u}'."
        })

        for v in adj.get(u, []):
            if v == parent:
                continue
            if v in in_stack:
                # Ciclo identificado
                step += 1
                timeline.append({
                    "step": step,
                    "event": "back_edge_cycle",
                    "active_node": v,
                    "active_edge": {"from": u, "to": v},
                    "variables": {"cycle_detected": True, "back_to": v},
                    "visited": list(visited),
                    "explanation": f"⚠️ Aresta de retorno detectada ({u} -> {v}): ciclo no grafo!"
                })
            elif v not in visited:
                dfs(v, u)
                if failure_step is not None:
                    return

        in_stack.remove(u)
        step += 1
        timeline.append({
            "step": step,
            "event": "leave_dfs",
            "active_node": u,
            "active_edge": None,
            "variables": {"completed_node": u, "stack_depth": len(in_stack)},
            "visited": list(visited),
            "explanation": f"Retornando da recursão: processamento de '{u}' finalizado."
        })

    dfs(start_node)
    return {
        "status": "tle" if failure_step is not None else "success",
        "total_steps": len(timeline),
        "failure_step": failure_step,
        "failure_reason": failure_reason,
        "timeline": timeline
    }


def generate_algorithmic_autopsy(
    code_text: str,
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    algorithm: str = "bfs",
    start_node: Optional[str] = None,
    max_steps: int = 200
) -> Dict[str, Any]:
    """Ponto de entrada unificado para execução e autópsia temporal de grafos."""
    validation = validate_cpp_syntax(code_text)
    if not nodes:
        return {
            "status": "error",
            "message": "Nenhum nó fornecido no grafo para simulação.",
            "total_steps": 0,
            "failure_step": None,
            "timeline": []
        }

    adj = build_adjacency(nodes, edges)
    root = str(start_node) if start_node and str(start_node) in adj else list(adj.keys())[0]

    algo_norm = algorithm.lower().strip()
    if "dfs" in algo_norm:
        autopsy = run_dfs_autopsy(adj, root, max_steps=max_steps)
    else:
        autopsy = run_bfs_autopsy(adj, root, max_steps=max_steps)

    autopsy["cpp_validation"] = validation
    return autopsy
