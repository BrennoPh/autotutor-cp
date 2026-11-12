"""LangGraph Multi-Agent Orchestrator for AutoTutor CP.

Chains all specialized agents (Diagnostic, Material Writer, AutoCode, Whiteboard,
Socratic Tutor) with Akita's AI-Memory (capture -> consolidate -> recall -> handoff).
"""
from __future__ import annotations

import uuid
from typing import Dict, Any, Optional

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from core.agent_state import AutoTutorGraphState
from core.agent_nodes import (
    ai_memory_recall_node,
    diagnostic_agent_node,
    material_writer_agent_node,
    problem_generator_agent_node,
    whiteboard_agent_node,
    socratic_tutor_agent_node,
    ai_memory_consolidate_node,
    _ensure_valid_profile_id
)
from core.learner_memory import LearnerMemory
from core.codigen_tutor import CodigenTutor
from core.autocode_engine import AutoCodeEngine
from core.llm_client import LLMClient


def route_after_memory(state: AutoTutorGraphState) -> str:
    """Routes to the primary specialist based on context and request."""
    action = state.get("action", "auto")
    has_code = bool(state.get("code", "").strip())
    has_judge = bool(state.get("judge_result"))

    if action == "whiteboard":
        return "whiteboard_agent"
    if action == "material":
        return "material_writer_agent"
    if action == "problem":
        return "problem_generator_agent"
    if action in ("diagnose", "hint") or has_code or has_judge:
        return "diagnostic_agent"
    return "socratic_tutor_agent"


def route_after_diagnosis(state: AutoTutorGraphState) -> str:
    """Chains diagnosis output into downstream generator or directly to tutor."""
    action = state.get("action", "auto")
    if action in ("drill", "problem"):
        return "problem_generator_agent"
    if action == "material":
        return "material_writer_agent"
    return "socratic_tutor_agent"


def build_collaborative_graph(
    memory: LearnerMemory,
    llm: LLMClient,
    tutor: CodigenTutor,
    autocode: AutoCodeEngine,
    checkpointer: Optional[MemorySaver] = None
):
    """Builds and compiles the unified LangGraph multi-agent graph."""
    builder = StateGraph(AutoTutorGraphState)

    # 1. Register all specialized agent nodes
    builder.add_node("ai_memory_recall", lambda s: ai_memory_recall_node(s, memory))
    builder.add_node("diagnostic_agent", lambda s: diagnostic_agent_node(s, llm, tutor))
    builder.add_node("material_writer_agent", lambda s: material_writer_agent_node(s, llm))
    builder.add_node("problem_generator_agent", lambda s: problem_generator_agent_node(s, llm, autocode))
    builder.add_node("whiteboard_agent", lambda s: whiteboard_agent_node(s, llm))
    builder.add_node("socratic_tutor_agent", lambda s: socratic_tutor_agent_node(s, llm, tutor))
    builder.add_node("ai_memory_consolidate", lambda s: ai_memory_consolidate_node(s, memory))

    # 2. Start with Akita Memory Recall
    builder.add_edge(START, "ai_memory_recall")

    # 3. Dynamic routing based on conversation context
    builder.add_conditional_edges(
        "ai_memory_recall",
        route_after_memory,
        {
            "diagnostic_agent": "diagnostic_agent",
            "material_writer_agent": "material_writer_agent",
            "problem_generator_agent": "problem_generator_agent",
            "whiteboard_agent": "whiteboard_agent",
            "socratic_tutor_agent": "socratic_tutor_agent",
        }
    )

    # 4. Cross-chat handoffs into Socratic Tutor
    builder.add_conditional_edges(
        "diagnostic_agent",
        route_after_diagnosis,
        {
            "problem_generator_agent": "problem_generator_agent",
            "material_writer_agent": "material_writer_agent",
            "socratic_tutor_agent": "socratic_tutor_agent"
        }
    )
    builder.add_edge("material_writer_agent", "socratic_tutor_agent")
    builder.add_edge("problem_generator_agent", "socratic_tutor_agent")
    builder.add_edge("whiteboard_agent", "socratic_tutor_agent")

    # 5. Final consolidation back to Akita Memory
    builder.add_edge("socratic_tutor_agent", "ai_memory_consolidate")
    builder.add_edge("ai_memory_consolidate", END)

    return builder.compile(checkpointer=checkpointer or MemorySaver())


def run_collaborative_agent_graph(
    payload: Dict[str, Any],
    store: Any,
    llm: Optional[LLMClient] = None
) -> Dict[str, Any]:
    """Top-level helper to execute the LangGraph multi-agent collaborative chat."""
    from core.mini_judge import MiniJudge
    
    llm_instance = llm or LLMClient()
    memory = LearnerMemory(store)
    tutor = CodigenTutor(llm_instance)
    autocode = AutoCodeEngine(llm_instance, MiniJudge())

    graph = build_collaborative_graph(memory, llm_instance, tutor, autocode)

    profile_id = _ensure_valid_profile_id(payload.get("student_id") or payload.get("user_id") or "default_user")
    thread_id = payload.get("thread_id") or f"thread_{profile_id[:8]}"

    initial_state: AutoTutorGraphState = {
        "student_id": profile_id,
        "problem_id": payload.get("problem_id"),
        "topic": payload.get("topic") or "Algoritmos",
        "user_message": payload.get("message") or payload.get("user_message") or "",
        "action": payload.get("action") or "auto",
        "thread_id": thread_id,
        "code": payload.get("code") or "",
        "judge_result": payload.get("judge_result"),
        "agent_trail": []
    }

    config = {"configurable": {"thread_id": thread_id}}
    final_state = graph.invoke(initial_state, config=config)

    return {
        "reply": final_state.get("final_reply") or final_state.get("tutor_response") or "",
        "agent_trail": final_state.get("agent_trail", []),
        "action": payload.get("action", "auto"),
        "diagnostic_output": final_state.get("diagnostic_output"),
        "material_output": final_state.get("material_output"),
        "problem_output": final_state.get("problem_output"),
        "whiteboard_output": final_state.get("whiteboard_output"),
        "recalled_memory": final_state.get("recalled_memory", {}),
        "thread_id": thread_id
    }
