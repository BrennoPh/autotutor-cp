"""Typed state definitions for LangGraph multi-agent collaboration in AutoTutor CP."""
from __future__ import annotations

from typing import TypedDict, Optional, List, Dict, Any


class AutoTutorGraphState(TypedDict, total=False):
    """Shared state passed between all specialized agents in the LangGraph workflow."""
    # Identification & Tenant context
    student_id: str
    problem_id: Optional[str]
    topic: str

    # Direct User Query & Session
    user_message: str
    action: str  # 'auto' | 'diagnose' | 'hint' | 'explain' | 'material' | 'problem' | 'whiteboard'
    thread_id: str

    # Code & Test execution results from Arena/Judge
    code: str
    judge_result: Optional[Dict[str, Any]]

    # Akita AI-Memory State (Capture -> Consolidate -> Recall -> Handoff)
    recalled_memory: Dict[str, Any]
    memory_context_text: str

    # Cross-Agent Intermediate Outputs (Each agent inputs into the other)
    diagnostic_output: Optional[Dict[str, Any]]
    material_output: Optional[Dict[str, Any]]
    problem_output: Optional[Dict[str, Any]]
    whiteboard_output: Optional[Dict[str, Any]]
    tutor_response: Optional[str]

    # Execution traceability & handoff audit
    agent_trail: List[str]
    final_reply: str
