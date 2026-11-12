"""Individual specialized agent nodes for LangGraph multi-agent collaboration."""
from __future__ import annotations

import json
import uuid
from typing import Dict, Any, Optional

from core.agent_state import AutoTutorGraphState
from core.learner_memory import LearnerMemory
from core.codigen_tutor import CodigenTutor, CARDS
from core.autocode_engine import AutoCodeEngine
from core.problem_bank import load_problems
from core.llm_client import LLMClient, AIUnavailable


def _ensure_valid_profile_id(raw_id: str) -> str:
    """Ensures a compliant 32-hex UUID for LearnerMemory isolation."""
    try:
        return uuid.UUID(str(raw_id)).hex
    except Exception:
        return uuid.uuid5(uuid.NAMESPACE_DNS, str(raw_id or "default_user")).hex


def ai_memory_recall_node(state: AutoTutorGraphState, memory: LearnerMemory) -> Dict[str, Any]:
    """Node 1: Akita AI-Memory Recall Stage.
    Retrieves previous struggles, topic notes, and handoffs before any agent answers.
    """
    profile_id = _ensure_valid_profile_id(state.get("student_id", "default_user"))
    query = f"{state.get('user_message', '')} {state.get('topic', '')}".strip()
    
    brief_data = memory.brief(profile_id, query)
    recalled_pages = brief_data.get("recalled_pages", [])
    
    context_lines = []
    for page in recalled_pages:
        context_lines.append(f"[{page.get('title')}]: {page.get('excerpt')}")
    
    memory_text = "\n".join(context_lines) if context_lines else "Nenhum histórico anterior registrado para este tópico."
    trail = list(state.get("agent_trail", []))
    trail.append("ai_memory_recall")

    return {
        "student_id": profile_id,
        "recalled_memory": brief_data,
        "memory_context_text": memory_text,
        "agent_trail": trail
    }


def diagnostic_agent_node(
    state: AutoTutorGraphState,
    llm: LLMClient,
    tutor: CodigenTutor
) -> Dict[str, Any]:
    """Node 2: Code Diagnostic Chat Agent.
    Interprets compiler messages, judge verdicts (WA/TLE/CE) and locates the conceptual root-cause.
    """
    code = state.get("code", "")
    judge_result = state.get("judge_result") or {}
    topic = state.get("topic") or "Algoritmos"
    mem_context = state.get("memory_context_text", "")
    
    problem = {
        "id": state.get("problem_id") or "prob_temp",
        "title": topic,
        "topic": topic,
        "statement": f"Resolva o problema sobre {topic}.",
        "complexity": "O(N) ou O(N log N)",
        "approach_summary": f"Abordagem esperada baseada na invariante de {topic}."
    }
    diagnosis_text = ""
    
    try:
        if judge_result and code:
            diagnosis_text = tutor.diagnose_error(problem, code, judge_result)
        elif code:
            system_prompt = (
                "Você é o Agente Especialista em Diagnóstico de Código C++ para Maratona. "
                "Identifique invariant breaks, off-by-one, overflow de 32 bits, ou sentinelas incorretos. "
                f"Contexto do histórico do aluno (Akita Memory):\n{mem_context}"
            )
            user_prompt = f"Tópico: {topic}\nCódigo:\n{code}\nDúvida do Aluno:\n{state.get('user_message')}"
            diagnosis_text = llm.complete(system_prompt, user_prompt)
    except AIUnavailable:
        diagnosis_text = f"Análise estática: verifique condições de contorno e limites assintóticos para {topic}."

    if not diagnosis_text:
        verdict = judge_result.get("verdict", "Submissão")
        diagnosis_text = f"Diagnóstico do Juiz: Veredito {verdict}. Verifique casos de teste mínimos e invariante de estado."

    trail = list(state.get("agent_trail", []))
    trail.append("diagnostic_agent")

    diagnostic_payload = {
        "verdict": judge_result.get("verdict", "N/A"),
        "diagnosis": diagnosis_text,
        "topic": topic
    }

    return {
        "diagnostic_output": diagnostic_payload,
        "agent_trail": trail
    }


def material_writer_agent_node(state: AutoTutorGraphState, llm: LLMClient) -> Dict[str, Any]:
    """Node 3: Conceptual Deepening / Material Writer Agent.
    Synthesizes concise micro-lessons when a conceptual gap or prerequisite is detected.
    """
    topic = state.get("topic") or "Fundamentos de Programação Competitiva"
    diag = state.get("diagnostic_output") or {}
    diag_summary = diag.get("diagnosis", "")

    system_prompt = (
        "Você é o Agente Especialista em Produção de Conteúdo Pedagógico de Algoritmos. "
        "Produza uma síntese didática direta focada no erro diagnosticado. "
        "Explique a intuição matemática/lógica, a invariante essencial e um exemplo mínimo."
    )
    user_prompt = (
        f"Tópico: {topic}\n"
        f"Erro diagnosticado previamente pelo Agente Diagnóstico:\n{diag_summary}\n"
        f"Pergunta do aluno:\n{state.get('user_message')}"
    )

    try:
        content = llm.complete(system_prompt, user_prompt)
    except AIUnavailable:
        card = CARDS.get(topic, ("Conceito", "Revise a invariante principal.", "Definição formal"))
        content = f"### {card[0]}\n\n{card[1]}\n\n> **Invariante:** {card[2]}"

    trail = list(state.get("agent_trail", []))
    trail.append("material_writer_agent")

    return {
        "material_output": {
            "title": f"Micro-guia: {topic}",
            "body": content,
            "topic": topic
        },
        "agent_trail": trail
    }


def problem_generator_agent_node(
    state: AutoTutorGraphState,
    llm: LLMClient,
    autocode: AutoCodeEngine
) -> Dict[str, Any]:
    """Node 4: AutoCode Practice Agent.
    Generates a targeted challenge tailored specifically to the diagnosed difficulty.
    """
    topic = state.get("topic") or "Simulação e Ad Hoc"
    diag = state.get("diagnostic_output") or {}
    focus = diag.get("diagnosis", state.get("user_message", ""))

    try:
        new_prob = autocode.generate_problem(
            level="Iniciante",
            concept=topic,
            theme="Fixação de Padrão",
            learning_request=f"Foco na superação do erro: {focus[:200]}"
        )
    except Exception:
        new_prob = {
            "id": f"drill_{uuid.uuid4().hex[:8]}",
            "title": f"Desafio de Fixação: {topic}",
            "statement": f"Implemente uma solução que mantenha estritamente a invariante de {topic}.",
            "topic": topic,
            "difficulty": "Iniciante"
        }

    trail = list(state.get("agent_trail", []))
    trail.append("problem_generator_agent")

    return {
        "problem_output": new_prob,
        "agent_trail": trail
    }


def whiteboard_agent_node(state: AutoTutorGraphState, llm: LLMClient) -> Dict[str, Any]:
    """Node 5: Whiteboard / Algorithmic Topology Analyzer Agent.
    Connects graph traces and topological diagrams into the conversation.
    """
    user_msg = state.get("user_message", "")
    system_prompt = (
        "Você é o Agente Especialista em Visualização de Grafos e Estruturas de Dados do AutoTutor. "
        "Analise a representação topológica, nós, arestas e ordem de visitação."
    )
    try:
        analysis = llm.complete(system_prompt, f"Entrada do aluno:\n{user_msg}")
    except AIUnavailable:
        analysis = "Visualização de grafo: confirme se a lista de adjacência é 0-based ou 1-based."

    trail = list(state.get("agent_trail", []))
    trail.append("whiteboard_agent")

    return {
        "whiteboard_output": {"analysis": analysis},
        "agent_trail": trail
    }


def socratic_tutor_agent_node(
    state: AutoTutorGraphState,
    llm: LLMClient,
    tutor: CodigenTutor
) -> Dict[str, Any]:
    """Node 6: Socratic Pedagogical Orchestrator Agent.
    Reads inputs produced by ALL upstream chat agents and delivers the final pedagogical response.
    """
    user_msg = state.get("user_message", "")
    code = state.get("code", "")
    topic = state.get("topic") or "Algoritmos"
    mem_context = state.get("memory_context_text", "")
    
    # Harvest inputs from upstream collaborating agents
    diag = state.get("diagnostic_output") or {}
    material = state.get("material_output") or {}
    problem = state.get("problem_output") or {}
    whiteboard = state.get("whiteboard_output") or {}

    collaborative_inputs = []
    if diag.get("diagnosis"):
        collaborative_inputs.append(f"🔍 [Diagnóstico do Juiz]: {diag['diagnosis']}")
    if material.get("body"):
        collaborative_inputs.append(f"📚 [Material Conceitual Produzido]: {material['body'][:350]}...")
    if problem.get("title"):
        collaborative_inputs.append(f"🎯 [Desafio de Fixação Criado]: {problem.get('title')}")
    if whiteboard.get("analysis"):
        collaborative_inputs.append(f"📊 [Laboratório de Grafos]: {whiteboard.get('analysis')}")

    collab_brief = "\n\n".join(collaborative_inputs)

    system_prompt = (
        "Você é o Tutor Socrático do AutoTutor CP. Responda em português, tom encorajador e didático. "
        "Você coordena uma equipe de agentes especialistas (Diagnóstico, Juiz, Gerador de Conteúdo e Memória Akita). "
        "NUNCA entregue a resposta pronta ou código mastigado. Guie o aluno com perguntas reflexivas, "
        "invariantes conceituais e pequenas verificações.\n"
        f"Histórico relevante do aluno (Akita Memory):\n{mem_context}\n\n"
        f"Insumos recebidos dos outros agentes da equipe:\n{collab_brief}"
    )

    user_prompt = (
        f"Tópico: {topic}\n"
        f"Mensagem do Aluno: {user_msg}\n"
        f"Código Atual:\n{code if code else 'Nenhum código submetido no momento.'}"
    )

    try:
        reply = llm.complete(system_prompt, user_prompt)
    except AIUnavailable:
        card = CARDS.get(topic, ("Conceito", "Revise a invariante principal.", "Definição formal"))
        reply = (
            f"**Orientação Socrática ({card[0]}):**\n\n"
            f"Com base na análise da nossa equipe de agentes, considere: {card[1]}\n\n"
            f"> *Invariante chave:* {card[2]}\n\n"
            f"Qual variável de controle você precisa atualizar primeiro a cada iteração?"
        )

    trail = list(state.get("agent_trail", []))
    trail.append("socratic_tutor_agent")

    return {
        "tutor_response": reply,
        "final_reply": reply,
        "agent_trail": trail
    }


def ai_memory_consolidate_node(state: AutoTutorGraphState, memory: LearnerMemory) -> Dict[str, Any]:
    """Node 7: Akita AI-Memory Consolidation & Handoff Stage.
    Captures observations and updates Markdown pages (memoria.md, handoff.md, topicos/).
    """
    profile_id = _ensure_valid_profile_id(state.get("student_id", "default_user"))
    topic = state.get("topic") or "Geral"
    reply = str(state.get("final_reply") or state.get("tutor_response") or "")
    user_msg = str(state.get("user_message") or "")
    diag = state.get("diagnostic_output") or {}
    diag_str = str(diag.get("diagnosis") or "N/A")

    interaction_record = {
        "provider": "LangGraph-MultiAgent",
        "model": "AutoTutor-Team",
        "prompt": f"[{topic}] {user_msg}",
        "response": f"Diagnóstico: {diag_str[:120]} | Tutor: {reply[:300]}"
    }

    try:
        memory.capture_model_call(profile_id, interaction_record)
        if diag.get("diagnosis"):
            memory.capture_artifact(
                profile_id,
                "feedback",
                f"Diagnóstico Colaborativo · {topic}",
                {"topic": topic, "content": diag.get("diagnosis")},
                source_id="langgraph_multi_agent"
            )
        memory.consolidate(profile_id)
    except Exception:
        pass

    trail = list(state.get("agent_trail", []))
    trail.append("ai_memory_consolidate")

    return {"agent_trail": trail}
