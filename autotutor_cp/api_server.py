"""Unified REST API Bridge for AutoTutor CP.

Exposes autotutor_cp core modules (problems, judge, whiteboard, tutor, assessment, progress,
accounts authentication, material writer and autocode problem generation)
as clean REST endpoints with CORS enabled for Next.js frontend (localhost:3000).
"""
import os
import sys
import re
import json
import time
import functools
import hashlib
import signal
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional

# Ensure autotutor_cp directory is on sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Auto-carregamento determinístico de variáveis de ambiente locais
_env_file = BASE_DIR / ".env"
if _env_file.exists():
    for _line in _env_file.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

from starlette.applications import Starlette
from starlette.concurrency import run_in_threadpool
from starlette.responses import JSONResponse, Response, StreamingResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

# Core Imports
from config import STARTER_CODE, TIME_LIMIT_SEC, MEMORY_LIMIT_MB, OUTPUT_LIMIT_BYTES
from core.problem_bank import load_problems
from core.mini_judge import MiniJudge, JudgeError, normalize_output
from core.llm_client import LLMClient, AIUnavailable
from core.ollama_client import DEFAULT_LOCAL_MODEL
from core.ai_connection import update_connection, connection_label
from core.codigen_tutor import CodigenTutor, CARDS
from core.progress_store import ProgressStore, DB_PATH
from core.learner_memory import LearnerMemory
from core.accounts import Accounts, AccessError
from core.autocode_engine import AutoCodeEngine
from core.whiteboard_engine import (
    WHITEBOARD_PRESETS,
    parse_graph_from_text,
    generate_algorithm_execution_tape,
    analyze_board_structure,
    generate_whiteboard_from_prompt
)
from core.cpp_whiteboard_executor import execute_cpp_whiteboard
from core.cpp_autopsy_engine import generate_algorithmic_autopsy
from core.learner_assessment import load_curriculum
from core.library import Library, resources, deep_guides, references_for, study_entry, KINDS, STATUSES
from core.knowledge import KnowledgeBase
from core.classrooms import Classrooms
from core.agent_graph import run_collaborative_agent_graph

try:
    from core.isolated_judge import IsolatedMiniJudge, isolation_available, namespace_command
except ImportError:
    IsolatedMiniJudge = None
    isolation_available = lambda: False
    namespace_command = None

# Global state instances
store = ProgressStore(os.environ.get('AUTOTUTOR_PROGRESS_DB', str(DB_PATH)))
accounts = Accounts(store)
def get_judge_instance():
    if IsolatedMiniJudge is not None and isolation_available():
        return IsolatedMiniJudge()
    return MiniJudge()

judge_instance = get_judge_instance()

# In-memory store for newly generated AI problems (so they can be queried and evaluated immediately)
GENERATED_PROBLEMS: Dict[str, Dict[str, Any]] = {}

PROBLEM_ALIASES: Dict[str, str] = {
    "binary_search": "binary",
    "binary_tree_lca": "tree",
    "trees": "tree",
    "tree_foundations": "tree",
    "greedy_interval_scheduling": "greedy",
    "prefix_sum_ranges": "prefix",
    "dsu_kruskal_mst": "graph",
    "dijkstra": "graph",
    "dijkstra_shortest_path": "graph",
    "recursion": "tree",
    "recursion_foundations": "tree",
    "foundations_stack_complexity": "tree",
    "graph_bfs_queue": "graph",
    "graph_dfs_cycles": "graph",
    "graph_dijkstra_scc": "graph",
    "dynamic_programming_intro": "dp",
    "dp_knapsack_foundations": "dp",
}

def resolve_problem_id(pid: Optional[str]) -> Optional[str]:
    if not pid:
        return pid
    cleaned = str(pid).strip()
    if cleaned in PROBLEM_ALIASES:
        return PROBLEM_ALIASES[cleaned]
    low = cleaned.lower()
    if "tree" in low or "arvor" in low or "lca" in low:
        return "tree"
    if "binar" in low or "busca" in low:
        return "binary"
    if "dp" in low or "dinam" in low or "mochila" in low:
        return "dp"
    if "greedy" in low or "gulos" in low:
        return "greedy"
    if "prefix" in low:
        return "prefix"
    if "segtree" in low or "segment" in low:
        return "segment_tree"
    if "graph" in low or "grafo" in low or "bfs" in low or "dfs" in low:
        return "graph"
    return cleaned


def get_llm_instance(provider: str = None, api_key: str = None, model: str = None) -> LLMClient:
    prov = provider or os.getenv("LLM_PROVIDER", "Gemini")
    key = (api_key if api_key is not None else (os.getenv("LLM_API_KEY") or os.getenv("GEMINI_API_KEY", ""))).strip()
    mod = model or os.getenv("LLM_MODEL") or ("gemini-3.5-flash" if prov == "Gemini" else DEFAULT_LOCAL_MODEL)
    return LLMClient(provider=prov, api_key=key, model=mod)


def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:].strip()
        try:
            return accounts.current(token)
        except Exception:
            return None
    return None


def get_active_profile_id(request: Request = None) -> str:
    if request:
        override = request.headers.get("x-profile-id")
        if override:
            return override
        user = get_current_user(request)
        if user and user.get("profile_id"):
            return user["profile_id"]
    pid = store.latest_profile_id()
    if not pid:
        pid = uuid.uuid4().hex
        store.save(pid, {"history": [], "study_hours": 3, "level": "Intermediário"})
    return pid


def get_all_problems() -> List[Dict[str, Any]]:
    base = load_problems()
    # Merge dynamically generated problems
    all_p = list(base)
    for p in GENERATED_PROBLEMS.values():
        if not any(x["id"] == p["id"] for x in all_p):
            all_p.insert(0, p)
    return all_p


# ============================================================================
# 1. AUTHENTICATION ENDPOINTS (Accounts)
# ============================================================================
async def auth_register(request: Request) -> JSONResponse:
    """POST /api/auth/register
    Body: { username, name, password, role?: 'student'|'teacher' }
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "JSON inválido."}, status_code=400)

    username = body.get("username", "").strip()
    name = body.get("name", "").strip()
    password = body.get("password", "")
    role = body.get("role", "student")

    if not username or not name or not password:
        return JSONResponse({"error": "Preencha todos os campos obrigatórios."}, status_code=400)

    try:
        user_id = accounts.register(username, name, password, role=role)
        token = accounts.login(username, password)
        user = accounts.user(user_id)
        return JSONResponse({
            "message": "Conta criada com sucesso!",
            "token": token,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "name": user["name"],
                "role": user["role"],
                "profile_id": user["profile_id"]
            }
        }, status_code=201)
    except (ValueError, AccessError) as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": f"Erro interno ao registrar conta: {e}"}, status_code=500)


async def auth_login(request: Request) -> JSONResponse:
    """POST /api/auth/login
    Body: { username, password }
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "JSON inválido."}, status_code=400)

    username = body.get("username", "").strip()
    password = body.get("password", "")

    if not username or not password:
        return JSONResponse({"error": "Informe usuário e senha."}, status_code=400)

    try:
        token = accounts.login(username, password)
        user = accounts.current(token)
        return JSONResponse({
            "token": token,
            "user": user
        })
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=401)
    except Exception as e:
        return JSONResponse({"error": f"Erro ao autenticar: {e}"}, status_code=500)


async def auth_me(request: Request) -> JSONResponse:
    """GET /api/auth/me
    Headers: Authorization: Bearer <token>
    """
    user = get_current_user(request)
    if not user:
        return JSONResponse({"authenticated": False, "user": None})
    return JSONResponse({"authenticated": True, "user": user})


async def auth_logout(request: Request) -> JSONResponse:
    """POST /api/auth/logout"""
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:].strip()
        try:
            accounts.logout(token)
        except Exception:
            pass
    return JSONResponse({"message": "Sessão encerrada com sucesso."})


# ============================================================================
# 2. PROBLEMS ENDPOINTS
# ============================================================================
async def list_problems(request: Request) -> JSONResponse:
    """GET /api/problems?topic=&difficulty=&search="""
    problems = get_all_problems()
    topic = request.query_params.get("topic")
    difficulty = request.query_params.get("difficulty")
    search = request.query_params.get("search", "").lower()

    filtered = []
    for p in problems:
        if topic and p.get("topic", "").lower() != topic.lower():
            continue
        if difficulty and p.get("difficulty", "").lower() != difficulty.lower():
            continue
        if search:
            title = p.get("title", "").lower()
            stmt = p.get("statement", "").lower()
            tags = " ".join(p.get("tags", [])).lower()
            if search not in title and search not in stmt and search not in tags:
                continue

        filtered.append({
            "id": p.get("id"),
            "title": p.get("title"),
            "topic": p.get("topic"),
            "difficulty": p.get("difficulty"),
            "tags": p.get("tags", []),
            "time_limit_sec": p.get("time_limit_sec", 2.0),
            "memory_limit_mb": p.get("memory_limit_mb", 256),
            "complexity": p.get("complexity", "O(N)"),
            "approach_summary": p.get("approach_summary", ""),
            "origin": p.get("origin", "local")
        })

    return JSONResponse({"total": len(filtered), "problems": filtered})


async def get_problem_detail(request: Request) -> JSONResponse:
    """GET /api/problems/{id}"""
    problem_id = resolve_problem_id(request.path_params.get("id"))
    problems = get_all_problems()
    found = next((p for p in problems if str(p.get("id")) == str(problem_id)), None)

    if not found:
        return JSONResponse({"error": f"Problema '{problem_id}' não encontrado."}, status_code=404)

    examples = found.get("examples", [])
    if not examples and found.get("tests"):
        examples = [
            {"input": t["input"], "output": t["expected_output"], "explanation": t.get("explanation", "")}
            for t in found["tests"][:2]
        ]

    data = {
        "id": found.get("id"),
        "title": found.get("title"),
        "family": found.get("family"),
        "topic": found.get("topic"),
        "difficulty": found.get("difficulty"),
        "tags": found.get("tags", []),
        "math_essence": found.get("math_essence", ""),
        "core_concepts": found.get("core_concepts", []),
        "approach_summary": found.get("approach_summary", ""),
        "complexity": found.get("complexity", ""),
        "statement": found.get("statement", ""),
        "constraints": found.get("constraints", {}),
        "time_limit_sec": found.get("time_limit_sec", 2.0),
        "memory_limit_mb": found.get("memory_limit_mb", 256),
        "examples": examples,
        "starter_code": {
            "cpp": (found.get("starter_code", {}).get("cpp") if isinstance(found.get("starter_code"), dict) else None) or STARTER_CODE,
            "python": "import sys\n\ndef main():\n    # Digite sua solução aqui\n    pass\n\nif __name__ == '__main__':\n    main()\n"
        }
    }
    return JSONResponse(data)


# ============================================================================
# 3. JUDGE & SUBMISSIONS
# ============================================================================
def _run_python_judge_sync(source_code: str, test_cases: List[dict], time_limit: float) -> dict:
    results = []
    verdict = "AC"
    failed_test = None
    msg = "Todos os testes passaram."

    import subprocess
    import tempfile

    runner_path = BASE_DIR / "core" / "runner.py"

    with tempfile.TemporaryDirectory(prefix="py_judge_") as folder:
        script_file = Path(folder) / "solution.py"
        script_file.write_text(source_code, encoding="utf-8")

        for idx, tc in enumerate(test_cases, 1):
            t_start = time.perf_counter()

            if isolation_available() and namespace_command is not None:
                py_bin = "/usr/bin/python3" if Path("/usr/bin/python3").exists() else sys.executable
                bwrap_cmd = namespace_command(folder, [py_bin, "/work/solution.py"], writable=False)
                cmd = [
                    sys.executable,
                    str(runner_path),
                    str(time_limit),
                    str(MEMORY_LIMIT_MB),
                    str(OUTPUT_LIMIT_BYTES),
                    *bwrap_cmd
                ]
            else:
                cmd = [
                    sys.executable,
                    str(runner_path),
                    str(time_limit),
                    str(MEMORY_LIMIT_MB),
                    str(OUTPUT_LIMIT_BYTES),
                    sys.executable,
                    str(script_file)
                ]

            try:
                proc = subprocess.run(
                    cmd,
                    input=tc["input"],
                    text=True,
                    capture_output=True,
                    timeout=time_limit + 1.0
                )
                elapsed_ms = round((time.perf_counter() - t_start) * 1000, 2)
                actual = proc.stdout
                expected = tc["expected_output"]
                stderr_text = proc.stderr

                case_verdict = "AC"
                if proc.returncode != 0:
                    if "MemoryError" in stderr_text or "std::bad_alloc" in stderr_text or "out of memory" in stderr_text.lower():
                        case_verdict = "MLE"
                    elif proc.returncode in (-signal.SIGXCPU, -signal.SIGKILL, -9, 137, 128 + getattr(signal, "SIGXCPU", 24)):
                        case_verdict = "TLE"
                        if not stderr_text:
                            stderr_text = "Tempo limite excedido."
                    else:
                        case_verdict = "RE"
                elif len(proc.stdout) > OUTPUT_LIMIT_BYTES or len(proc.stderr) > OUTPUT_LIMIT_BYTES:
                    case_verdict = "RE"
                    stderr_text = "Limite de saída excedido."
                elif normalize_output(actual) != normalize_output(expected):
                    case_verdict = "WA"

                test_entry = {
                    "test_id": idx,
                    "execution_time_ms": elapsed_ms,
                    "verdict": case_verdict,
                    "input": tc["input"],
                    "expected_output": expected,
                    "actual_output": actual[:10000],
                    "stderr": stderr_text[:16000]
                }

                if test_entry["verdict"] != "AC":
                    verdict = test_entry["verdict"]
                    failed_test = test_entry
                    if verdict == "MLE":
                        msg = "Limite de memória excedido (MLE)."
                    elif verdict == "RE":
                        msg = stderr_text[:1000] if stderr_text else "Erro em tempo de execução."
                    elif verdict == "WA":
                        msg = "Saída diferente do esperado."
                    results.append(test_entry)
                    break

                results.append(test_entry)

            except subprocess.TimeoutExpired:
                elapsed_ms = round((time.perf_counter() - t_start) * 1000, 2)
                verdict = "TLE"
                failed_test = {
                    "test_id": idx,
                    "execution_time_ms": elapsed_ms,
                    "verdict": "TLE",
                    "input": tc["input"],
                    "expected_output": tc["expected_output"],
                    "actual_output": "",
                    "stderr": "Tempo limite excedido."
                }
                msg = "Tempo limite excedido."
                results.append(failed_test)
                break

    return {
        "verdict": verdict,
        "tests": results,
        "failed_test": failed_test,
        "message": msg
    }


async def submit_solution(request: Request) -> JSONResponse:
    """POST /api/judge/submit
    Body: { problem_id, source_code, language: 'cpp' | 'python' }
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Corpo da requisição JSON inválido."}, status_code=400)

    problem_id = resolve_problem_id(body.get("problem_id"))
    source_code = body.get("source_code", "")
    language = body.get("language", "cpp").lower()

    if not problem_id or not source_code.strip():
        return JSONResponse({"error": "Parâmetros 'problem_id' e 'source_code' são obrigatórios."}, status_code=400)

    problems = get_all_problems()
    problem = next((p for p in problems if str(p.get("id")) == str(problem_id)), None)
    if not problem:
        return JSONResponse({"error": f"Problema '{problem_id}' não encontrado."}, status_code=404)

    test_cases = problem.get("tests", [])
    if not test_cases:
        return JSONResponse({"error": "Nenhum caso de teste associado a este problema."}, status_code=400)

    time_limit = problem.get("time_limit_sec", TIME_LIMIT_SEC)

    try:
        if language in ("python", "py"):
            judge_result = await run_in_threadpool(_run_python_judge_sync, source_code, test_cases, time_limit)
        else:
            current_judge = get_judge_instance()
            judge_result = await run_in_threadpool(current_judge.judge, source_code, test_cases, time_limit)

    except JudgeError as e:
        judge_result = {
            "verdict": "CE",
            "message": str(e),
            "tests": [],
            "failed_test": None
        }
    except Exception as e:
        judge_result = {
            "verdict": "RE",
            "message": f"Erro de infraestrutura do juiz: {str(e)}",
            "tests": [],
            "failed_test": None
        }

    pid = get_active_profile_id(request)
    elapsed_max = max((r.get("execution_time_ms", 0) for r in judge_result.get("tests", [])), default=0)
    record = {
        "problem_id": problem["id"],
        "problem": problem["title"],
        "topic": problem.get("topic", "Geral"),
        "verdict": judge_result["verdict"],
        "time_ms": elapsed_max,
        "language": language.upper(),
        "timestamp": time.time()
    }
    try:
        def _persist_submission():
            profile_data = store.load(pid) or {}
            history = profile_data.get("history", [])
            history.append(record)
            profile_data["history"] = history
            store.save(pid, profile_data)
            store.add_artifact(pid, "submission", problem["title"], {
                "record": record,
                "source_code": source_code,
                "result": judge_result
            })
        await run_in_threadpool(_persist_submission)
    except Exception as e:
        print(f"[Warning] Falha ao persistir submissão no SQLite: {e}")

    return JSONResponse({
        "verdict": judge_result["verdict"],
        "message": judge_result.get("message", ""),
        "execution_time_ms": elapsed_max,
        "tests_passed": len([t for t in judge_result.get("tests", []) if t.get("verdict") == "AC"]),
        "total_tests": len(test_cases),
        "failed_test": judge_result.get("failed_test"),
        "tests": judge_result.get("tests", [])
    })


# ============================================================================
# 4. AI CONTENT GENERATION & MATERIAL WRITER (/api/ai/generate-material)
# ============================================================================
async def generate_material_endpoint(request: Request) -> JSONResponse:
    """POST /api/ai/generate-material
    Body: { kind, concept, level, theme, learning_request, length, depth, include_examples, include_exercises }
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "JSON inválido."}, status_code=400)

    LEVEL_MAP = {
        "iniciante": "Iniciante",
        "intermediario": "Intermediário",
        "intermediário": "Intermediário",
        "avancado": "Avançado",
        "avançado": "Avançado"
    }
    raw_level = str(body.get("level", "Iniciante")).strip().lower()
    level = LEVEL_MAP.get(raw_level, "Iniciante")

    DEPTH_MAP = {
        "rapida": "Rápida",
        "rápida": "Rápida",
        "padrao": "Padrão",
        "padrão": "Padrão",
        "aprofundada": "Aprofundada",
        "passo a passo": "Passo a passo"
    }
    raw_depth = str(body.get("depth", "Aprofundada")).strip().lower()
    depth = DEPTH_MAP.get(raw_depth, "Aprofundada")

    LENGTH_MAP = {
        "curto": "Curto",
        "medio": "Médio",
        "médio": "Médio",
        "longo": "Longo"
    }
    raw_length = str(body.get("length", "Longo")).strip().lower()
    length = LENGTH_MAP.get(raw_length, "Longo")

    concept = body.get("concept") or body.get("topic") or "Grafos"
    theme = body.get("theme", "Maratona e Competições")
    learning_request = body.get("learning_request", "").strip()
    include_examples = body.get("include_examples", True)
    include_exercises = body.get("include_exercises", True)
    kind = body.get("kind", "Conceitual")

    llm = get_llm_instance()
    tutor = CodigenTutor(llm)

    try:
        markdown_content = await run_in_threadpool(
            tutor.generate_material,
            kind=kind,
            concept=concept,
            level=level,
            theme=theme,
            learning_request=learning_request,
            length=length,
            depth=depth,
            include_examples=include_examples,
            include_exercises=include_exercises
        )

        title = f"{kind}: {concept} ({level})"
        pid = get_active_profile_id(request)
        artifact_id = None

        # Extração de preset de quadro branco (WhiteboardPreset) para integração Obsidian Canvas
        whiteboard_preset = None
        mermaid_match = re.search(r"```mermaid\s*\n(.*?)\n```", markdown_content, re.S)
        if mermaid_match:
            mermaid_code = mermaid_match.group(1).strip()
            parsed_nodes = []
            parsed_edges = []
            for m in re.finditer(r'([A-Za-z0-9_]+)\["([^"]+)"\]', mermaid_code):
                parsed_nodes.append({"id": m.group(1), "label": m.group(2)})
            for m in re.finditer(r'([A-Za-z0-9_]+)\s*(?:-->|-.->|==>)\s*([A-Za-z0-9_]+)', mermaid_code):
                parsed_edges.append({"from": m.group(1), "to": m.group(2), "directed": True})
            if parsed_nodes:
                algo = "bfs" if "bfs" in concept.lower() else ("dfs" if "dfs" in concept.lower() else "custom_cpp")
                whiteboard_preset = {
                    "topic": concept,
                    "algorithm": algo,
                    "mermaid": mermaid_code,
                    "nodes": parsed_nodes,
                    "edges": parsed_edges
                }

        try:
            artifact_id = await run_in_threadpool(
                store.add_artifact,
                pid, "material", title, {
                    "title": title,
                    "concept": concept,
                    "level": level,
                    "markdown": markdown_content,
                    "whiteboard_preset": whiteboard_preset,
                    "generated_at": time.time(),
                    "provider": llm.provider
                }
            )
        except Exception as e:
            print(f"[Warning] Falha ao salvar material em artifacts: {e}")

        return JSONResponse({
            "title": title,
            "markdown": markdown_content,
            "concept": concept,
            "level": level,
            "artifact_id": artifact_id,
            "whiteboard_preset": whiteboard_preset,
            "sources": getattr(tutor, "last_retrieval", [])
        })

    except Exception as e:
        return JSONResponse({
            "error": f"Erro na geração de material didático: {str(e)}",
            "fallback_available": True
        }, status_code=500)


# ============================================================================
# 5. AUTOCODE ENGINE: COMPETITIVE PROBLEM GENERATOR (/api/ai/generate-problem)
# ============================================================================
async def generate_problem_endpoint(request: Request) -> JSONResponse:
    """POST /api/ai/generate-problem
    Body: { level, concept, theme, learning_request }
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "JSON inválido."}, status_code=400)

    level = body.get("level", "Iniciante")
    concept = body.get("concept", "Grafos")
    theme = body.get("theme", "Exploração Espacial")
    learning_request = body.get("learning_request", "").strip()

    llm = get_llm_instance()
    engine = AutoCodeEngine(llm=llm, judge=judge_instance)

    try:
        problem = engine.generate_problem(
            level=level,
            concept=concept,
            theme=theme,
            learning_request=learning_request,
            allow_review=True
        )
    except Exception as exc:
        # Fallback to local reserve contract if LLM cannot choose or quota is exceeded
        all_seeds = load_problems()
        matching_seed = next((p for p in all_seeds if concept.lower() in p.get("topic", "").lower() or concept.lower() in p.get("family", "").lower()), all_seeds[0])
        try:
            problem = engine.adapt_seed(matching_seed, level=level, concept=concept, theme=theme, learning_request=learning_request)
        except Exception:
            from copy import deepcopy
            problem = deepcopy(matching_seed)
            problem["id"] = "generated_" + uuid.uuid4().hex[:10]
            problem["title"] = f"{theme}: {matching_seed['title']}"
            problem["difficulty"] = level
            problem["origin"] = "local_reserve"
        problem["fallback_used"] = True

    # Store in dynamic catalog
    p_id = problem["id"]
    GENERATED_PROBLEMS[p_id] = problem

    return JSONResponse({
        "id": p_id,
        "title": problem["title"],
        "difficulty": problem["difficulty"],
        "topic": problem.get("topic", concept),
        "statement": problem["statement"],
        "complexity": problem.get("complexity", "O(V+E)"),
        "starter_code": {
            "cpp": STARTER_CODE,
            "python": "import sys\n\ndef main():\n    pass\n\nif __name__ == '__main__':\n    main()\n"
        },
        "examples": problem.get("examples", []),
        "total_tests": len(problem.get("tests", [])),
        "fallback_used": problem.get("fallback_used", False),
        "redirect_url": f"/workspace?problem={p_id}"
    })


def _generate_track_fallback(prompt: str, difficulty: Optional[str] = None, subject: Optional[str] = None) -> Dict[str, Any]:
    p = prompt.lower().strip()
    diff = difficulty or "Intermediário"
    if "iniciante" in p:
        diff = "Iniciante"
    elif "avançad" in p or "avancad" in p:
        diff = "Avançado"

    # 1. Estruturas de dados / Árvores
    if any(k in p for k in ["árvore", "arvore", "bst", "avl", "balanceada", "rubro", "estrutura"]):
        has_avl = "balanceada" in p or "avl" in p or "rubro" in p
        return {
            "title": "Estruturas de Dados Hierárquicas: Árvores Binárias e Balanceadas" if has_avl else "Estruturas de Dados: Árvores Binárias de Busca e Balanceamento",
            "subject": "Estruturas de Dados",
            "difficulty": diff,
            "description": "Domine a construção de nós, percursos recursivos, Árvores de Busca (BST) e técnicas de balanceamento (AVL e Rotações) para maratonas em C++.",
            "modules": [
                {
                    "title": "Módulo 1: Árvore Binária de Busca (BST) e Percursos",
                    "description": "Ponteiros, alocação de nós e travessias In-Order, Pre-Order e Post-Order em O(N).",
                    "estimatedMinutes": 35,
                    "lessons": ["Estrutura de Nós em C++", "Inserção e Busca Binária O(log N)", "Remoção com Sucessor In-Order"]
                },
                {
                    "title": "Módulo 2: Árvores Balanceadas (AVL) & Fator de Balanceamento",
                    "description": "Cálculo de altura de subárvores e detecção de desbalanceamento (-2, +2).",
                    "estimatedMinutes": 45,
                    "lessons": ["Fator de Balanceamento", "Rotações Simples (Esquerda e Direita)", "Rotações Duplas (LR e RL)"]
                },
                {
                    "title": "Módulo 3: Árvores Rubro-Negras & A STL do C++",
                    "description": "Propriedades das cores preta e vermelha, e como o std::set e std::map operam na prática.",
                    "estimatedMinutes": 40,
                    "lessons": ["Propriedades da Árvore Rubro-Negra", "std::set e std::map com Funções Customizadas", "lower_bound e upper_bound"]
                },
                {
                    "title": "Módulo 4: Árvores de Intervalos & Resolução de Desafios",
                    "description": "Consultas e atualizações em tempo logarítmico e resolução de problemas na Arena.",
                    "estimatedMinutes": 50,
                    "lessons": ["Segment Tree e Árvore Fenwick", "Desafio Prático no Juiz C++", "Análise Assintótica no Pior Caso"]
                }
            ],
            "fallback_used": True
        }

    # 2. Programação Dinâmica
    if any(k in p for k in ["dp", "dinâmica", "dinamica", "mochila", "subsequência", "subsequencia", "memoization"]):
        return {
            "title": "Especialização em Programação Dinâmica & Transição de Estados",
            "subject": "Programação Dinâmica",
            "difficulty": diff,
            "description": "Aprenda a decompor problemas com subestrutura ótima, formular a Equação de Bellman e comprimir o espaço de memória.",
            "modules": [
                {
                    "title": "Módulo 1: Fundamentos de DP e Memoization (Top-Down)",
                    "description": "Transformando soluções exponenciais em tempo linear através de cache de estados.",
                    "estimatedMinutes": 30,
                    "lessons": ["Fibonacci e Escadas", "Mochila 0/1 com Memoization"]
                },
                {
                    "title": "Módulo 2: Tabulação (Bottom-Up) e Otimização 1D",
                    "description": "Construção de tabelas iterativas e compressão de espaço de O(N*W) para O(W).",
                    "estimatedMinutes": 45,
                    "lessons": ["Iteração Reversa em Vetor 1D", "Problema do Troco de Moedas"]
                },
                {
                    "title": "Módulo 3: Subsequências e Recuperação de Caminho",
                    "description": "Maior Subsequência Comum (LCS), Maior Subsequência Crescente (LIS) e reconstrução.",
                    "estimatedMinutes": 50,
                    "lessons": ["LCS em 2D", "LIS em O(N log N) com Busca Binária", "Recuperação do Vetor de Escolhas"]
                }
            ],
            "fallback_used": True
        }

    # 3. Grafos
    if any(k in p for k in ["grafo", "bfs", "dfs", "dijkstra", "fluxo", "caminho", "rede"]):
        return {
            "title": "Domínio em Teoria dos Grafos & Algoritmos de Travessia",
            "subject": "Grafos & Travessias",
            "difficulty": diff,
            "description": "Do básico de representação em listas de adjacência até caminhos mínimos com pesos e árvores geradoras.",
            "modules": [
                {
                    "title": "Módulo 1: Representações e Travessias Fundamentais",
                    "description": "Listas de adjacência, BFS com Fila FIFO e DFS recursiva com Call Stack.",
                    "estimatedMinutes": 35,
                    "lessons": ["std::vector<vector<int>> em C++", "BFS e Invariante de Camadas", "DFS e Detecção de Ciclos"]
                },
                {
                    "title": "Módulo 2: Caminhos Mínimos com Pesos",
                    "description": "Dijkstra com std::priority_queue e Bellman-Ford para arestas com pesos negativos.",
                    "estimatedMinutes": 45,
                    "lessons": ["Algoritmo de Dijkstra O((V+E) log V)", "Relaxamento de Arestas", "Bellman-Ford e Detecção de Ciclo Negativo"]
                },
                {
                    "title": "Módulo 3: Árvores Geradoras Mínimas & DSU",
                    "description": "Agrupamento de componentes com Disjoint Set Union e Algoritmo de Kruskal.",
                    "estimatedMinutes": 40,
                    "lessons": ["Union-Find com Compressão de Caminho", "Kruskal para AGM", "Componentes Fortemente Conexas (Tarjan)"]
                }
            ],
            "fallback_used": True
        }

    # 4. Fallback Geral
    clean_topic = prompt.strip().title() if len(prompt.strip()) < 40 else "Algoritmos e Estruturas de Dados"
    return {
        "title": f"Trilha de Especialização: {clean_topic}",
        "subject": subject or "Ciência da Computação",
        "difficulty": diff,
        "description": f"Plano de estudo customizado cobrindo {prompt.strip()} com fundamentação matemática, implementação em C++ e problemas no juiz.",
        "modules": [
            {
                "title": f"Módulo 1: Fundamentos de {clean_topic}",
                "description": "Definição de conceitos, modelagem inicial e estruturas essenciais.",
                "estimatedMinutes": 30,
                "lessons": ["Introdução e Motivação", "Estruturação Básica em C++"]
            },
            {
                "title": f"Módulo 2: Algoritmos e Otimizações",
                "description": "Implementação eficiente de técnicas clássicas e análise assintótica.",
                "estimatedMinutes": 45,
                "lessons": ["Implementação Canônica", "Casos de Borda e Invariantes"]
            },
            {
                "title": f"Módulo 3: Resolução de Desafios no Juiz Online",
                "description": "Exercícios práticos de maratona com submissão e verificação em tempo real.",
                "estimatedMinutes": 50,
                "lessons": ["Resolução Guiada de Problema", "Otimizações de Memória e Tempo"]
            }
        ],
        "fallback_used": True
    }


async def generate_track_endpoint(request: Request) -> JSONResponse:
    """POST /api/ai/generate-track
    Body: { prompt: str, difficulty?: str, subject?: str }
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "JSON inválido."}, status_code=400)

    prompt = (body.get("prompt") or "").strip()
    if not prompt:
        return JSONResponse({"error": "O campo 'prompt' é obrigatório."}, status_code=400)

    difficulty = body.get("difficulty")
    subject = body.get("subject")

    fallback = _generate_track_fallback(prompt, difficulty, subject)

    llm = get_llm_instance()
    if not llm:
        return JSONResponse(fallback)

    system_prompt = (
        "Você é o Arquiteto Pedagógico do AutoTutor CP, especialista em Maratonas de Programação e Ciência da Computação. "
        "Sua tarefa é criar uma trilha de estudo estruturada e completa com base no pedido em linguagem natural do aluno. "
        "A resposta DEVE ser estritamente um JSON válido contendo exatamente as chaves: "
        "'title' (string), 'subject' (string), 'difficulty' ('Iniciante' | 'Intermediário' | 'Avançado'), "
        "'description' (string com 2 a 3 frases explicativas), e 'modules' (lista com 3 a 5 módulos). "
        "Cada módulo DEVE ter as chaves: 'title' (string), 'description' (string), 'estimatedMinutes' (número inteiro de 20 a 60), e 'lessons' (lista de 2 a 4 strings). "
        "Não inclua blocos de markdown adicionais fora do JSON."
    )

    user_query = f"Gere a trilha pedagógica para o seguinte pedido do aluno: \"{prompt}\"."
    if difficulty:
        user_query += f" Nível de dificuldade alvo: {difficulty}."
    if subject:
        user_query += f" Disciplina/Área: {subject}."

    def _call_llm():
        try:
            raw = llm.complete(system_prompt, user_query, include_history=False)
            if not raw:
                return None
            clean = raw.strip()
            clean = re.sub(r"^```(?:json)?\s*", "", clean, flags=re.MULTILINE)
            clean = re.sub(r"\s*```$", "", clean, flags=re.MULTILINE).strip()
            start = clean.find("{")
            end = clean.rfind("}")
            if start != -1 and end != -1:
                clean = clean[start:end+1]
            data = json.loads(clean)
            if "title" in data and "modules" in data and isinstance(data["modules"], list) and len(data["modules"]) > 0:
                data["fallback_used"] = False
                return data
        except Exception as e:
            print(f"[Warning] Falha ao processar retorno LLM da trilha: {e}")
        return None

    try:
        result = await run_in_threadpool(_call_llm)
        if result:
            return JSONResponse(result)
    except Exception as e:
        print(f"[Warning] Erro ao gerar trilha com IA: {e}")

    return JSONResponse(fallback)


# ============================================================================
# 6. WHITEBOARD & GRAPH ENGINE
# ============================================================================
async def get_whiteboard_presets(request: Request) -> JSONResponse:
    """GET /api/whiteboard/presets"""
    return JSONResponse({"presets": WHITEBOARD_PRESETS})


async def parse_graph_endpoint(request: Request) -> JSONResponse:
    """POST /api/whiteboard/parse-graph
    Body: { raw_text: "1 2\\n1 3\\n2 4" }
    """
    body = await request.json()
    raw_text = body.get("raw_text", "")
    preset_name = body.get("preset_name")

    nodes, edges = parse_graph_from_text(raw_text, preset_name)
    return JSONResponse({"nodes": nodes, "edges": edges})


async def simulate_algorithm_endpoint(request: Request) -> JSONResponse:
    """POST /api/whiteboard/simulate
    Body: { code_text, nodes, edges, start_node, max_steps }
    """
    body = await request.json()
    code_text = body.get("code_text") or body.get("code", "")
    nodes = body.get("nodes", [])
    edges = body.get("edges", [])
    start_node = body.get("start_node") or body.get("root_node")
    max_steps = min(500, int(body.get("max_steps", 500)))

    result = execute_cpp_whiteboard(code_text, nodes, edges, start_node, max_steps)
    return JSONResponse(result)


async def autopsy_algorithm_endpoint(request: Request) -> JSONResponse:
    """POST /api/whiteboard/autopsy
    Body: { code_text, nodes, edges, algorithm, start_node, max_steps }
    """
    body = await request.json()
    code_text = body.get("code_text") or body.get("code", "")
    nodes = body.get("nodes", [])
    edges = body.get("edges", [])
    algorithm = body.get("algorithm", "bfs")
    start_node = body.get("start_node") or body.get("root_node")
    max_steps = min(500, int(body.get("max_steps", 200)))

    result = generate_algorithmic_autopsy(
        code_text=code_text,
        nodes=nodes,
        edges=edges,
        algorithm=algorithm,
        start_node=start_node,
        max_steps=max_steps
    )
    return JSONResponse(result)


async def analyze_board_endpoint(request: Request) -> JSONResponse:
    """POST /api/whiteboard/analyze
    Body: { nodes, edges }
    """
    body = await request.json()
    nodes = body.get("nodes", [])
    edges = body.get("edges", [])

    llm = get_llm_instance()

    nodes_summary = ", ".join([f"{n.get('id')}:{n.get('label', n.get('id'))}" for n in nodes])
    edges_summary = ", ".join([f"{e.get('from')}->{e.get('to')}" for e in edges])
    notes = f"Nós do Grafo: [{nodes_summary}]. Arestas: [{edges_summary}]."

    analysis = analyze_board_structure(llm, notes)
    return JSONResponse({"analysis": analysis})


async def whiteboard_ai_prompt_endpoint(request: Request) -> JSONResponse:
    """POST /api/whiteboard/prompt
    Gera dinamicamente topologia e código C++ a partir de prompt em linguagem natural.
    Body: { prompt: str, current_nodes?: list, current_edges?: list }
    """
    body = await request.json()
    prompt = body.get("prompt", "").strip()
    nodes = body.get("current_nodes", [])
    edges = body.get("current_edges", [])
    llm = get_llm_instance()

    result = generate_whiteboard_from_prompt(prompt, nodes, edges, llm)
    return JSONResponse(result)


# ============================================================================
# 7. AI TUTOR SOCRATIC CHAT & MULTI-AGENT COLLABORATION (LangGraph + Akita Memory)
# ============================================================================
async def collaborative_chat_endpoint(request: Request) -> JSONResponse:
    """POST /api/agents/collaborative-chat
    Explicit LangGraph Multi-Agent Orchestration with Akita AI-Memory.
    Diagnostic Agent, Material Writer, AutoCode, Whiteboard and Socratic Tutor
    feed inputs and outputs into each other in a coordinated graph.
    """
    body = await request.json()
    user = get_current_user(request)
    if user and user.get("id"):
        body["student_id"] = user["id"]

    llm = get_llm_instance()
    result = run_collaborative_agent_graph(body, store, llm)
    return JSONResponse(result)


def generate_dynamic_socratic_response(problem: Optional[Dict[str, Any]], code: str, message: str, action: str, judge_result: Optional[Dict[str, Any]] = None) -> str:
    """Gera orientação socrática dinâmica, contextualizada e estritamente em C++."""
    prob_title = problem.get("title", "Problema Algorítmico") if problem else "Algoritmos em C++"
    prob_topic = problem.get("topic", "Estruturas de Dados") if problem else "Grafos & Algoritmos"
    complexity = problem.get("complexity", "O(N log N)") if problem else "O(N)"
    
    # Análise de padrões do código C++
    code_clean = code.strip()
    has_includes = "#include" in code_clean
    has_cin = "cin >>" in code_clean or "std::cin" in code_clean
    has_queue = "queue<" in code_clean or "priority_queue<" in code_clean
    has_vector = "vector<" in code_clean
    has_recursion = bool(re.search(r'\b(\w+)\s*\([^)]*\)\s*\{[^}]*\b\1\s*\(', code_clean))
    nested_loops = len(re.findall(r'\b(for|while)\b', code_clean)) >= 2
    
    verdict = (judge_result or {}).get("verdict")

    if verdict == "TLE":
        obs = f"Seu código C++ possui laços repetitivos ({'aninhados' if nested_loops else 'sequenciais'}). "
        return (
            f"⏱️ **Análise de Limite de Tempo (TLE) para '{prob_title}':**\n\n"
            f"{obs}A meta assintótica para este problema é **{complexity}**.\n\n"
            f"> *Pergunta Socrática:* Se $N = 10^5$, quantas operações seu algoritmo executa no pior caso? "
            f"Qual invariante ou estrutura STL (como `std::unordered_map` ou ordenação prévia) permitiria responder cada consulta em $O(1)$ ou $O(\\log N)$?"
        )
    elif verdict == "WA":
        return (
            f"🎯 **Análise de Divergência Lógica (Wrong Answer) em '{prob_title}':**\n\n"
            f"O resultado produzido pelo seu executável C++ divergiu da saída esperada pelo juiz.\n\n"
            f"> *Provocação Didática:* Trace o estado das suas variáveis (`cin >> ...`) para uma entrada mínima de borda "
            f"(ex: $N=1$, valores negativos ou grafo com nós isolados). A condição de parada dos seus laços está cobrindo todos os índices?"
        )
    elif verdict == "RE" or verdict == "CE":
        return (
            f"🛠️ **Diagnóstico de Compilação/Execução C++ em '{prob_title}':**\n\n"
            f"O compilador GCC ou o runtime interceptou uma falha crítica ({verdict}).\n\n"
            f"> *Checagem Guiada:* Verifique se você declarou vetores com tamanho suficiente (`vector<int> v(n + 1)`), "
            f"se há divisão por zero ou acesso fora dos limites (`vector::at` ou `v[i]` com `i < 0`)."
        )
    elif action == "explain":
        return (
            f"💡 **Arquitetura do seu Código C++ para '{prob_title}':**\n\n"
            f"- **Entrada e STL:** {'Utiliza estruturas STL da C++ Standard Library' if has_vector or has_queue else 'Código direto sem contêineres complexos'}.\n"
            f"- **Fluxo de Controle:** {'Contém chamadas recursivas estruturadas' if has_recursion else 'Abordagem puramente iterativa'}.\n\n"
            f"> *Reflexão de Eficiência:* Qual é a complexidade de espaço da sua solução? O uso de memória obedece ao limite de 256MB sem vazamento em heap?"
        )
    else:
        # Pergunta socrática direta
        return (
            f"🧠 **Orientação do AutoTutor CP ({prob_topic} · {prob_title}):**\n\n"
            f"Para avançar na resolução desta questão em C++, considere a propriedade fundamental do tópico:\n\n"
            f"> *Reflexão:* Como você modela a transição de um estado para o próximo? "
            f"Se você estiver usando `vector<vector<int>>` para representar adjacências, qual é a garantia de que nenhum vértice é reprocessado infinitamente?\n\n"
            f"Você gostaria de projetar este problema diretamente no **Quadro Branco** para visualizar a execução passo a passo?"
        )


async def tutor_chat_endpoint(request: Request) -> JSONResponse:
    """POST /api/tutor/chat
    Body: {
      message: str,
      action?: 'diagnose' | 'hint' | 'explain' | 'simplify',
      problem_id?: str,
      code?: str,
      judge_result?: dict,
      collaborative?: bool
    }
    """
    body = await request.json()
    message = body.get("message", "")
    action = body.get("action", "hint")
    problem_id = resolve_problem_id(body.get("problem_id"))
    code = body.get("code", "")
    judge_result = body.get("judge_result")
    use_collaborative = body.get("collaborative", True)

    problem = None
    if problem_id:
        problems = get_all_problems()
        problem = next((p for p in problems if str(p.get("id")) == str(problem_id)), None)

    llm = get_llm_instance()

    # 1. First attempt: LangGraph collaborative multi-agent execution with Akita memory
    if use_collaborative:
        try:
            user = get_current_user(request)
            if user and user.get("id"):
                body["student_id"] = user["id"]
            if problem and problem.get("topic"):
                body["topic"] = problem.get("topic")

            graph_result = run_collaborative_agent_graph(body, store, llm)
            reply_text = graph_result.get("reply", "").strip()
            if reply_text and "Nenhum" not in reply_text:
                return JSONResponse({
                    "reply": reply_text,
                    "action": action,
                    "provider": llm.provider,
                    "collaborative": True,
                    "agent_trail": graph_result.get("agent_trail", []),
                    "diagnostic_output": graph_result.get("diagnostic_output"),
                    "material_output": graph_result.get("material_output"),
                    "problem_output": graph_result.get("problem_output"),
                    "whiteboard_output": graph_result.get("whiteboard_output"),
                    "recalled_memory": graph_result.get("recalled_memory", {})
                })
        except Exception as e:
            print(f"[Tutor Chat] LangGraph multi-agent fallback triggered: {e}")

    # 2. Resilient Single Tutor with C++ Dynamic Intelligence
    tutor = CodigenTutor(llm)
    response_text = ""
    try:
        if action == "diagnose" and problem and judge_result:
            response_text = tutor.diagnose_error(problem, code, judge_result)
        elif action == "explain" and problem:
            response_text = tutor.explain_code(code)
        else:
            system_prompt = (
                "Você é o AutoTutor CP, um tutor socrático especialista em maratona de programação competitiva em C++. "
                "Responda sempre em português, com tom assertivo, didático e encorajador. "
                "Todas as análises e sugestões de código devem ser estritamente em C++17 (nada de Python). "
                "Nunca forneça a solução pronta mastigada. Guie o aluno com perguntas provocativas, "
                "invariantes conceituais e limites assintóticos."
            )
            full_prompt = f"Problema: {problem.get('title') if problem else 'Algoritmos em C++'}\n\nCódigo do Aluno (C++):\n{code}\n\nDúvida:\n{message}"
            raw_reply = llm.complete(system_prompt, full_prompt)
            if raw_reply and len(raw_reply.strip()) > 30:
                response_text = raw_reply.strip()
            else:
                response_text = generate_dynamic_socratic_response(problem, code, message, action, judge_result)
    except Exception:
        response_text = generate_dynamic_socratic_response(problem, code, message, action, judge_result)

    return JSONResponse({
        "reply": response_text,
        "action": action,
        "provider": llm.provider,
        "collaborative": False
    })


async def tutor_hints_endpoint(request: Request) -> JSONResponse:
    """POST /api/tutor/hints
    Body: {
      problem_id: str,
      student_id?: str,
      current_code?: str,
      tier?: int (1-4),
      user_query?: str
    }
    Returns Graduated 4-Tier Hint with RAG citations and LearnerMemory context.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}

    problem_id = resolve_problem_id(str(body.get("problem_id", "")).strip())
    tier = int(body.get("tier", 1) or 1)
    current_code = body.get("current_code", "")
    user_query = body.get("user_query", "")

    # Retrieve student identity (from body or auth header)
    student_id = body.get("student_id")
    if not student_id:
        student_id = get_active_profile_id(request)

    # Load problem
    problems = get_all_problems()
    problem = next((p for p in problems if str(p.get("id")) == problem_id), None)
    if not problem:
        problem = problems[0] if problems else {
            "id": problem_id or "generic",
            "title": "Problema de Algoritmos",
            "topic": "Grafos",
            "family": "graph",
            "statement": "Análise algorítmica e implementação.",
            "complexity": "O(N)",
            "constraints": {"n_max": 100000},
            "math_essence": "Invariante algorítmica fundamental.",
            "approach_summary": "Travessia estruturada e preservação de estado."
        }

    topic = problem.get("topic") or problem.get("family", "Geral")

    # 1. RAG Retrieval via KnowledgeBase
    kb = KnowledgeBase()
    query = f"{topic} {problem.get('title', '')} {user_query}".strip()
    rag_context, rag_refs = kb.context(query, max_chars=3000, external_only=True)

    # 2. AI Memory Retrieval via LearnerMemory
    learner_mem = LearnerMemory(store)
    memory_evidence = None
    if student_id:
        try:
            memory_evidence = learner_mem.brief(student_id, topic, max_chars=1200)
        except Exception:
            memory_evidence = None

    # 3. Socratic Tutor generation with Zero-Leak Guardrail
    llm = get_llm_instance()
    tutor = CodigenTutor(llm)
    hint_result = tutor.generate_graduated_hint(
        problem=problem,
        tier=tier,
        rag_context=rag_context,
        rag_refs=rag_refs,
        memory_evidence=memory_evidence,
        current_code=current_code,
        user_query=user_query
    )

    return JSONResponse(hint_result)


async def tutor_preflight_endpoint(request: Request) -> JSONResponse:
    """POST /api/tutor/preflight
    Body: {
      problem_id: str,
      proposed_complexity: str,
      chosen_structure: str,
      estimated_ops?: int
    }
    Evaluates asymptotic complexity and edge cases before code execution.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}

    problem_id = resolve_problem_id(str(body.get("problem_id", "")).strip())
    proposed_complexity = str(body.get("proposed_complexity", "O(N)")).strip()
    chosen_structure = str(body.get("chosen_structure", "Vetor")).strip()
    estimated_ops = body.get("estimated_ops")
    if estimated_ops is not None:
        try:
            estimated_ops = int(estimated_ops)
        except (ValueError, TypeError):
            estimated_ops = None

    problems = get_all_problems()
    problem = next((p for p in problems if str(p.get("id")) == problem_id), None)
    if not problem:
        problem = problems[0] if problems else {
            "id": problem_id or "generic",
            "title": "Problema de Algoritmos",
            "topic": "Grafos",
            "family": "graph",
            "complexity": "O(N + M)",
            "constraints": {"n_max": 200000},
            "time_limit_sec": 1.0
        }

    llm = get_llm_instance()
    tutor = CodigenTutor(llm)
    preflight_result = tutor.evaluate_preflight(
        problem=problem,
        proposed_complexity=proposed_complexity,
        chosen_structure=chosen_structure,
        estimated_ops=estimated_ops
    )

    return JSONResponse(preflight_result)



# ============================================================================
# 8. ONBOARDING & DIAGNOSTIC ASSESSMENT
# ============================================================================
async def get_assessment_quiz(request: Request) -> JSONResponse:
    """GET /api/assessment/onboarding"""
    curriculum = load_curriculum()
    questions = []
    for topic in curriculum:
        for q in topic.get("questions", []):
            questions.append({
                "id": q.get("id"),
                "topic": topic.get("title"),
                "prompt": q.get("prompt"),
                "options": q.get("options", []),
            })
    return JSONResponse({"total": len(questions), "questions": questions[:6]})


DIAGNOSTIC_ANSWER_KEY = {
    "q1_complexity": {"answer": "b", "topic": "Análise Assintótica e Complexidade"},
    "q2_recursion_stack": {"answer": "c", "topic": "Recursão e Pilha de Execução"},
    "q3_bfs_queue": {"answer": "c", "topic": "Fila (Queue) e Invariante de Camadas da BFS"},
    "q4_dfs_cycles": {"answer": "b", "topic": "Detecção de Ciclos e Arestas de Retorno"},
    "q5_dp_memo": {"answer": "b", "topic": "Programação Dinâmica e Subestrutura Ótima"}
}


async def submit_assessment(request: Request) -> JSONResponse:
    """POST /api/assessment/submit
    Body: { target_goal, hours_per_day, language, answers: { question_id: selected_index } }
    """
    body = await request.json()
    answers = body.get("answers", {})

    curriculum = load_curriculum()
    q_map = {}
    for topic in curriculum:
        for q in topic.get("questions", []):
            q_map[q.get("id")] = q

    correct = 0
    total = len(answers) or 1
    gap_topics = []
    strong_topics = []

    for qid, ans in answers.items():
        if qid in DIAGNOSTIC_ANSWER_KEY:
            expected = DIAGNOSTIC_ANSWER_KEY[qid]["answer"]
            topic_name = DIAGNOSTIC_ANSWER_KEY[qid]["topic"]
            str_ans = str(ans).strip().lower()
            if str_ans in ("0", "1", "2", "3"):
                str_ans = chr(ord('a') + int(str_ans))

            is_correct = (str_ans == expected) or (qid == "q3_bfs_queue" and str_ans in ("b", "c"))
            if is_correct:
                correct += 1
                strong_topics.append(topic_name)
            else:
                gap_topics.append(topic_name)
        elif qid in q_map:
            q_obj = q_map[qid]
            try:
                ans_int = int(ans)
            except Exception:
                ans_int = -1
            if ans_int == q_obj.get("answer"):
                correct += 1
                strong_topics.append(q_obj.get("prompt", "")[:40])
            else:
                gap_topics.append(q_obj.get("prompt", "")[:40])

    score = round((correct / max(total, 1)) * 100)
    level = "Iniciante" if score < 40 else ("Intermediário" if score < 75 else "Avançado")

    profile_id = get_active_profile_id(request)
    try:
        p_data = store.load(profile_id) or {}
        p_data["level"] = level
        p_data["diagnostic_score"] = score
        p_data["strong_topics"] = strong_topics
        p_data["gap_topics"] = gap_topics
        p_data["onboarding_completed"] = True
        store.save(profile_id, p_data)
    except Exception as e:
        print(f"[Warning] Falha ao persistir avaliação: {e}")

    return JSONResponse({
        "score": score,
        "level": level,
        "correct_count": correct,
        "total_questions": total,
        "strong_topics": strong_topics,
        "gap_topics": gap_topics
    })


# ============================================================================
# 9. PROGRESS & SPACED REPETITION
# ============================================================================
async def get_progress(request: Request) -> JSONResponse:
    """GET /api/progress
    Optimized progress endpoint:
    - Returns materials_count and a lightweight list of recent materials ({id, title, created_at})
    - Omits full markdown bodies by default to reduce payload from ~834 KB to <2 KB
    - Supports ?include_materials=true to include complete markdown payloads without data/payload duplication
    - Supports ?limit=N to adjust the number of lightweight materials returned (default: 4)
    - Supports ?history_limit=N to adjust recent submission history returned (default: 2)
    """
    pid = get_active_profile_id(request)
    data = await run_in_threadpool(store.load, pid) or {}

    history = data.get("history", [])
    solved = len([h for h in history if h.get("verdict") == "AC"])
    streak_days = max(1, min(len(history), 14))

    include_materials = request.query_params.get("include_materials", "false").lower() in ("true", "1", "yes")
    default_limit = 50 if include_materials else 4
    try:
        limit = int(request.query_params.get("limit", default_limit))
    except (ValueError, TypeError):
        limit = default_limit

    try:
        history_limit = int(request.query_params.get("history_limit", 2))
    except (ValueError, TypeError):
        history_limit = 2

    # Retrieve saved materials
    materials = []
    total_materials = 0
    try:
        artifacts = await run_in_threadpool(store.artifacts, pid, "material")
        total_materials = len(artifacts)
        for art in artifacts[:limit]:
            created_at = art.get("time") or art.get("created_at")
            if include_materials:
                payload = art.get("payload") or art.get("data") or {}
                materials.append({
                    "id": art.get("id"),
                    "title": art.get("title"),
                    "created_at": created_at,
                    "payload": payload,
                })
            else:
                materials.append({
                    "id": art.get("id"),
                    "title": art.get("title"),
                    "created_at": created_at,
                })
    except Exception:
        pass

    last_act = history[-1].get("timestamp") if history else (artifacts[0].get("time") if artifacts else None)
    if isinstance(last_act, (int, float)):
        import datetime
        last_activity = datetime.datetime.fromtimestamp(last_act, tz=datetime.timezone.utc).isoformat()
    elif isinstance(last_act, str):
        last_activity = last_act
    else:
        last_activity = None

    recent_history = list(reversed(history[-history_limit:])) if history_limit > 0 else []

    return JSONResponse({
        "profile_id": pid,
        "total_submissions": len(history),
        "solved_count": solved,
        "level": data.get("level", "Intermediário"),
        "study_hours": data.get("study_hours", 3),
        "streak_days": streak_days,
        "last_activity": last_activity,
        "history": recent_history,
        "materials_count": total_materials,
        "materials": materials,
        "saved_materials": materials,
        "completed_lessons": data.get("completed_lessons", []),
        "onboarding_completed": data.get("onboarding_completed", False),
        "diagnostic_score": data.get("diagnostic_score"),
        "strong_topics": data.get("strong_topics", []),
        "gap_topics": data.get("gap_topics", []),
    })


async def get_saved_materials(request: Request) -> JSONResponse:
    """GET /api/progress/materials or /api/progress/materials/{material_id}
    Retrieves full saved materials on-demand.
    """
    pid = get_active_profile_id(request)
    material_id = request.path_params.get("material_id")
    try:
        artifacts = await run_in_threadpool(store.artifacts, pid, "material")
    except Exception:
        artifacts = []

    if material_id:
        art = next((a for a in artifacts if str(a.get("id")) == str(material_id)), None)
        if not art:
            return JSONResponse({"error": "Material não encontrado."}, status_code=404)
        payload = art.get("payload") or art.get("data") or {}
        return JSONResponse({
            "id": art.get("id"),
            "title": art.get("title"),
            "created_at": art.get("time") or art.get("created_at"),
            "payload": payload,
        })

    try:
        limit = min(100, max(1, int(request.query_params.get("limit", "50"))))
        offset = max(0, int(request.query_params.get("offset", "0")))
    except (ValueError, TypeError):
        limit = 50
        offset = 0

    result = []
    for art in artifacts[offset:offset + limit]:
        payload = art.get("payload") or art.get("data") or {}
        result.append({
            "id": art.get("id"),
            "title": art.get("title"),
            "created_at": art.get("time") or art.get("created_at"),
            "payload": payload,
        })

    return JSONResponse({
        "materials": result,
        "total": len(artifacts),
        "limit": limit,
        "offset": offset
    })


async def toggle_lesson_completion(request: Request) -> JSONResponse:
    """POST /api/progress/lessons/complete
    Body: { lesson_id: str, completed?: bool }
    Marks or toggles a lesson as completed/pending for the active profile.
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Corpo da requisição JSON inválido."}, status_code=400)

    lesson_id = str(body.get("lesson_id", "")).strip()
    if not lesson_id:
        return JSONResponse({"error": "Parâmetro 'lesson_id' é obrigatório."}, status_code=400)

    pid = get_active_profile_id(request)
    data = await run_in_threadpool(store.load, pid) or {}
    completed_list = list(data.get("completed_lessons", []))

    if "completed" in body:
        target_state = bool(body["completed"])
        if target_state and lesson_id not in completed_list:
            completed_list.append(lesson_id)
        elif not target_state and lesson_id in completed_list:
            completed_list = [l for l in completed_list if l != lesson_id]
        is_completed = target_state
    else:
        # Toggle
        if lesson_id in completed_list:
            completed_list = [l for l in completed_list if l != lesson_id]
            is_completed = False
        else:
            completed_list.append(lesson_id)
            is_completed = True

    data["completed_lessons"] = completed_list
    await run_in_threadpool(store.save, pid, data)

    return JSONResponse({
        "success": True,
        "lesson_id": lesson_id,
        "completed": is_completed,
        "completed_lessons": completed_list,
        "total_completed": len(completed_list),
    })


async def reset_profile_endpoint(request: Request) -> JSONResponse:
    """POST /api/progress/reset
    Completely resets the active profile to 0:
    - Clears all artifacts
    - Clears memory events, pages, fts, audit
    - Clears library state
    - Clears model calls
    - Clears external progress
    - Resets profile payload to empty initial state
    """
    pid = get_active_profile_id(request)

    def _do_reset():
        with store.connect() as db:
            db.execute("DELETE FROM artifacts WHERE profile_id=?", (pid,))
            db.execute("DELETE FROM memory_events WHERE profile_id=?", (pid,))
            db.execute("DELETE FROM memory_pages WHERE profile_id=?", (pid,))
            db.execute("DELETE FROM memory_fts WHERE profile_id=?", (pid,))
            db.execute("DELETE FROM memory_audit WHERE profile_id=?", (pid,))
            db.execute("DELETE FROM library_state WHERE profile_id=?", (pid,))
            db.execute("DELETE FROM model_calls WHERE profile_id=?", (pid,))
            u_row = db.execute("SELECT id FROM users WHERE profile_id=?", (pid,)).fetchone()
            if u_row:
                db.execute("DELETE FROM external_progress WHERE user_id=?", (u_row[0],))

        base_problems = [p for p in load_problems() if p["id"] in ["graph", "dp", "binary", "greedy", "prefix", "tree"]]
        clean_payload = {
            "history": [],
            "quiz_attempts": [],
            "completed_lessons": [],
            "study_hours": 0,
            "problems": base_problems,
            "results": {},
            "feedback": {},
            "feedback_sources": {},
            "helpers": {},
            "recommendations": {},
            "material": "",
            "material_source": "",
            "drafts": {},
            "ai_events": [],
            "model_capabilities": {},
            "level": "Iniciante",
            "diagnostic_draft": {},
            "learning_topic": "fundamentals",
            "theme_dark": True,
            "lab_preferences": {},
            "onboarding_completed": False,
            "diagnostic_score": None,
            "strong_topics": [],
            "gap_topics": []
        }
        store.save(pid, clean_payload)

    await run_in_threadpool(_do_reset)

    return JSONResponse({
        "success": True,
        "message": "Perfil totalmente zerado com sucesso.",
        "profile_id": pid,
        "clear_client_storage": True
    })


# ============================================================================
# 10. AI CREDENTIALS, CONFIG & CONNECTION PING
# ============================================================================
async def get_llm_config(request: Request) -> JSONResponse:
    """GET /api/config/llm"""
    provider = os.getenv("LLM_PROVIDER", "Gemini")
    raw_key = os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY", "")
    masked_key = (raw_key[:4] + "..." + raw_key[-4:]) if len(raw_key) > 8 else ("Configurada" if raw_key else "Não informada")
    model = os.getenv("LLM_MODEL", DEFAULT_LOCAL_MODEL if provider == "Ollama" else "gemini-3.5-flash")

    return JSONResponse({
        "provider": provider,
        "masked_key": masked_key,
        "model": model,
        "available_providers": ["Gemini", "OpenAI", "DeepSeek", "Qwen", "Ollama"],
        "recommended_models": {
            "Gemini": ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.6-flash"],
            "OpenAI": ["gpt-4o", "gpt-4o-mini"],
            "DeepSeek": ["deepseek-chat", "deepseek-coder"],
            "Qwen": ["qwen-plus", "qwen-turbo"],
            "Ollama": ["qwen2.5-coder:7b", "deepseek-r1:7b", "llama3.1:8b"]
        }
    })


async def save_llm_config(request: Request) -> JSONResponse:
    """POST /api/config/save-llm
    Body: { provider, api_key, model }
    """
    body = await request.json()
    provider = body.get("provider", "Gemini")
    api_key = body.get("api_key", "").strip()
    model = body.get("model", "").strip() or ("gemini-3.5-flash" if provider == "Gemini" else DEFAULT_LOCAL_MODEL)

    if provider:
        os.environ["LLM_PROVIDER"] = provider
    if api_key:
        os.environ["LLM_API_KEY"] = api_key
        if provider == "Gemini":
            os.environ["GEMINI_API_KEY"] = api_key
    if model:
        os.environ["LLM_MODEL"] = model

    # Persistência atômica no arquivo .env local
    try:
        env_lines = []
        keys_set = set()
        if _env_file.exists():
            for line in _env_file.read_text(encoding="utf-8").splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.split("=", 1)
                    k = k.strip()
                    if k == "LLM_PROVIDER":
                        env_lines.append(f"LLM_PROVIDER={provider}")
                        keys_set.add("LLM_PROVIDER")
                    elif k in ("LLM_API_KEY", "GEMINI_API_KEY") and api_key:
                        env_lines.append(f"{k}={api_key}")
                        keys_set.add(k)
                    elif k == "LLM_MODEL":
                        env_lines.append(f"LLM_MODEL={model}")
                        keys_set.add("LLM_MODEL")
                    else:
                        env_lines.append(line)
                else:
                    env_lines.append(line)

        if "LLM_PROVIDER" not in keys_set:
            env_lines.append(f"LLM_PROVIDER={provider}")
        if api_key and "LLM_API_KEY" not in keys_set:
            env_lines.append(f"LLM_API_KEY={api_key}")
        if "LLM_MODEL" not in keys_set:
            env_lines.append(f"LLM_MODEL={model}")

        _env_file.write_text("\n".join(env_lines) + "\n", encoding="utf-8")
    except Exception as e:
        print(f"[AutoTutor] Aviso ao persistir .env: {e}")

    return JSONResponse({
        "ok": True,
        "message": f"Configuração de IA salva com sucesso ({provider} · {model})!",
        "provider": provider,
        "model": model
    })


async def ping_llm(request: Request) -> JSONResponse:
    """POST /api/config/ping
    Body: { provider?: str, api_key?: str, model?: str }
    """
    t_start = time.perf_counter()
    body = await request.json() if request.headers.get("content-type") == "application/json" else {}
    provider = body.get("provider") or os.getenv("LLM_PROVIDER", "Gemini")
    api_key = (body.get("api_key") or os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY", "")).strip()
    model = (body.get("model") or os.getenv("LLM_MODEL") or ("gemini-3.5-flash" if provider == "Gemini" else DEFAULT_LOCAL_MODEL)).strip()

    llm = get_llm_instance(provider=provider, api_key=api_key, model=model)
    is_ok = llm.test_connection()
    latency_ms = round((time.perf_counter() - t_start) * 1000)

    if is_ok:
        return JSONResponse({
            "ok": True,
            "provider": provider,
            "status": "verified",
            "message": f"{provider} · Conexão verificada com sucesso ({model})!",
            "latency_ms": latency_ms,
            "status_code": 200
        })

    last_event = llm.events[-1] if llm.events else {}
    err_code = last_event.get("code")
    err_msg = last_event.get("message") or llm.last_error or "Falha de conexão com o provedor."
    detail = last_event.get("detail", "")
    lowered = (err_msg + " " + detail).lower()

    if err_code == 404 or "not found" in lowered or "not available" in lowered:
        status = "model_error"
        status_code = 404
        message = f"{provider} · Modelo '{model}' indisponível ou descontinuado. Sugestão: gemini-3.5-flash"
    elif err_code == 429 or "quota" in lowered or "rate limit" in lowered:
        status = "quota_error"
        status_code = 429
        message = f"{provider} · Limite de cota/requisições atingido (HTTP 429)."
    elif err_code == 503 or "high demand" in lowered or "unavailable" in lowered:
        status = "temporary_error"
        status_code = 503
        message = f"{provider} · Modelo temporariamente sobrecarregado (HTTP 503). Tente gemini-3.5-flash."
    elif err_code in (401, 403) or not api_key:
        status = "credentials_error"
        status_code = 401
        message = f"{provider} · Chave de API inválida ou sem permissão."
    else:
        status = "request_error"
        status_code = err_code or 400
        message = f"{provider} · {err_msg}"

    return JSONResponse({
        "ok": False,
        "provider": provider,
        "status": status,
        "message": message,
        "latency_ms": latency_ms,
        "status_code": status_code,
        "detail": detail
    })


async def list_llm_models(request: Request) -> JSONResponse:
    """GET /api/config/models?provider=Gemini&api_key=..."""
    provider = request.query_params.get("provider") or os.getenv("LLM_PROVIDER", "Gemini")
    api_key = (request.query_params.get("api_key") or os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY", "")).strip()
    llm = get_llm_instance(provider=provider, api_key=api_key)
    models = llm.list_models()
    return JSONResponse({
        "provider": provider,
        "models": models,
        "recommended": ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.6-flash"] if provider == "Gemini" else []
    })


def resolve_profile_id(raw_id: Optional[str]) -> str:
    """Valida ou busca um profile_id hexadecimal de 32 chars válido."""
    if raw_id:
        try:
            if uuid.UUID(raw_id).hex == raw_id:
                return raw_id
        except Exception:
            pass
    with store.connect() as db:
        row = db.execute("SELECT id FROM profiles ORDER BY updated_at DESC LIMIT 1").fetchone()
        if row:
            return row[0]
    return uuid.uuid4().hex


# ============================================================================
# LIBRARY & KNOWLEDGE BASE ENDPOINTS
# ============================================================================
DATA_DIR = Path(__file__).resolve().parent / "data"

@functools.lru_cache(maxsize=1)
def _load_canonical_books():
    books_file = DATA_DIR / "canonical_books.json"
    if books_file.exists():
        try:
            raw = json.loads(books_file.read_text(encoding="utf-8"))
            return raw.get("books", [])
        except Exception as e:
            print(f"[API Server] Erro lendo canonical_books.json: {e}")
    return []


async def get_library_books(request: Request) -> JSONResponse:
    """GET /api/library/books
    Retorna o catálogo de livros canônicos e guias de aprofundamento com cache em memória.
    """
    books = await run_in_threadpool(_load_canonical_books)
    guides = await run_in_threadpool(deep_guides)
    return JSONResponse({
        "books": books,
        "guides": guides
    })


async def search_library_knowledge(request: Request) -> JSONResponse:
    """GET /api/library/search?q=grafos&topic=&limit=12
    Pesquisa documentos no acervo RAG (knowledge.sqlite3) e recursos curados.
    Executa I/O SQLite e contagem de estatísticas em pool não-bloqueante.
    """
    query = request.query_params.get("q", "").strip()
    topic = request.query_params.get("topic")
    limit = min(30, max(1, int(request.query_params.get("limit", 12))))

    kb = KnowledgeBase()
    results = []
    if query:
        try:
            results = await run_in_threadpool(kb.search, query, limit=limit, topic=topic)
        except Exception as e:
            print(f"[API Server] Erro na busca KnowledgeBase: {e}")
            results = []

    curated = await run_in_threadpool(resources)
    if not query:
        matched_curated = curated[:limit]
    else:
        q_lower = query.lower()
        matched_curated = [
            r for r in curated
            if q_lower in r.get("title", "").lower() or q_lower in r.get("summary", "").lower() or any(q_lower in t.lower() for t in r.get("topics", []))
        ][:limit]

    stats = await run_in_threadpool(kb.stats)

    return JSONResponse({
        "query": query,
        "results": results,
        "curated_resources": matched_curated,
        "stats": stats
    })


async def get_library_document(request: Request) -> JSONResponse:
    """GET /api/library/document/{id}
    Retorna o texto integral de um artigo do acervo ou guia de aprofundamento.
    """
    doc_id = request.path_params.get("id")
    if doc_id.startswith("deep_"):
        guides = {g["id"]: g for g in deep_guides()}
        guide = guides.get(doc_id)
        if not guide:
            return JSONResponse({"error": "Guia de aprofundamento não encontrado"}, status_code=404)
        return JSONResponse({"type": "guide", "data": guide})

    kb = KnowledgeBase()
    doc = kb.get(doc_id)
    if not doc:
        return JSONResponse({"error": "Documento não encontrado no acervo"}, status_code=404)
    return JSONResponse({"type": "document", "data": doc})


async def get_library_collection(request: Request) -> JSONResponse:
    """GET /api/library/collection?profile_id=&search=&kind=&status=&page=1
    Retorna os estudos, artigos e materiais salvos do aluno com notas e status.
    """
    raw_pid = request.query_params.get("profile_id")
    profile_id = resolve_profile_id(raw_pid)
    search = request.query_params.get("search", "")
    kind = request.query_params.get("kind")
    status = request.query_params.get("status")
    page = max(1, int(request.query_params.get("page", 1)))

    lib = Library(store)
    try:
        data = lib.page(
            profile_id=profile_id,
            search=search,
            kind=kind if kind in KINDS else None,
            status=status if status in STATUSES else None,
            page=page,
            page_size=12
        )
        return JSONResponse(data)
    except Exception as e:
        print(f"[API Server] Erro em library.page: {e}")
        return JSONResponse({"total": 0, "items": []})


async def set_library_state(request: Request) -> JSONResponse:
    """POST /api/library/state
    Body: { profile_id, item_id, status, note }
    Atualiza status ("Quero estudar", "Estudando", "Estudado") e anotações.
    """
    body = await request.json()
    raw_pid = body.get("profile_id")
    profile_id = resolve_profile_id(raw_pid)
    item_id = body.get("item_id")
    status = body.get("status", "Estudando")
    note = body.get("note", "")

    if not item_id:
        return JSONResponse({"error": "item_id obrigatório"}, status_code=400)

    lib = Library(store)
    try:
        lib.set_state(profile_id=profile_id, item_id=item_id, status=status, note=note)
        return JSONResponse({"ok": True, "message": "Estado da biblioteca atualizado"})
    except Exception as e:
        print(f"[API Server] Erro em set_library_state: {e}")
        return JSONResponse({"error": str(e)}, status_code=400)


async def save_library_resource(request: Request) -> JSONResponse:
    """POST /api/library/save-resource
    Body: { profile_id, resource: { title, url, summary, kind } }
    """
    body = await request.json()
    raw_pid = body.get("profile_id")
    profile_id = resolve_profile_id(raw_pid)
    resource = body.get("resource", {})

    lib = Library(store)
    try:
        identifier = lib.save_resource(profile_id=profile_id, resource=resource)
        return JSONResponse({"ok": True, "id": identifier, "message": "Recurso salvo na coleção"})
    except Exception as e:
        print(f"[API Server] Erro em save_library_resource: {e}")
        return JSONResponse({"error": str(e)}, status_code=400)


# ============================================================================
# ROUTING & ASGI APP
# ============================================================================
routes = [
    # Auth
    Route("/api/auth/register", auth_register, methods=["POST"]),
    Route("/api/auth/login", auth_login, methods=["POST"]),
    Route("/api/auth/me", auth_me, methods=["GET"]),
    Route("/api/auth/logout", auth_logout, methods=["POST"]),

    # Problems & Judge
    Route("/api/problems", list_problems, methods=["GET"]),
    Route("/api/problems/{id}", get_problem_detail, methods=["GET"]),
    Route("/api/judge/submit", submit_solution, methods=["POST"]),

    # AI Content & Problem Generators
    Route("/api/ai/generate-material", generate_material_endpoint, methods=["POST"]),
    Route("/api/ai/generate-problem", generate_problem_endpoint, methods=["POST"]),
    Route("/api/ai/generate-track", generate_track_endpoint, methods=["POST"]),

    # Whiteboard
    Route("/api/whiteboard/presets", get_whiteboard_presets, methods=["GET"]),
    Route("/api/whiteboard/parse-graph", parse_graph_endpoint, methods=["POST"]),
    Route("/api/whiteboard/simulate", simulate_algorithm_endpoint, methods=["POST"]),
    Route("/api/whiteboard/autopsy", autopsy_algorithm_endpoint, methods=["POST"]),
    Route("/api/whiteboard/prompt", whiteboard_ai_prompt_endpoint, methods=["POST"]),
    Route("/api/whiteboard/analyze", analyze_board_endpoint, methods=["POST"]),

    # Tutor Chat, Socratic Graduated Hints & Pre-Flight
    Route("/api/tutor/chat", tutor_chat_endpoint, methods=["POST"]),
    Route("/api/tutor/hints", tutor_hints_endpoint, methods=["POST"]),
    Route("/api/tutor/preflight", tutor_preflight_endpoint, methods=["POST"]),
    Route("/api/agents/collaborative-chat", collaborative_chat_endpoint, methods=["POST"]),
    Route("/api/agents/graph", collaborative_chat_endpoint, methods=["POST"]),

    # Assessment & Progress
    Route("/api/assessment/onboarding", get_assessment_quiz, methods=["GET"]),
    Route("/api/assessment/submit", submit_assessment, methods=["POST"]),
    Route("/api/progress", get_progress, methods=["GET"]),
    Route("/api/progress/reset", reset_profile_endpoint, methods=["POST"]),
    Route("/api/progress/lessons/complete", toggle_lesson_completion, methods=["POST"]),
    Route("/api/progress/materials", get_saved_materials, methods=["GET"]),
    Route("/api/progress/materials/{material_id}", get_saved_materials, methods=["GET"]),

    # Library & Knowledge Base
    Route("/api/library/books", get_library_books, methods=["GET"]),
    Route("/api/library/search", search_library_knowledge, methods=["GET"]),
    Route("/api/library/document/{id}", get_library_document, methods=["GET"]),
    Route("/api/library/collection", get_library_collection, methods=["GET"]),
    Route("/api/library/state", set_library_state, methods=["POST"]),
    Route("/api/library/save-resource", save_library_resource, methods=["POST"]),

    # Config
    Route("/api/config/llm", get_llm_config, methods=["GET"]),
    Route("/api/config/models", list_llm_models, methods=["GET"]),
    Route("/api/config/save-llm", save_llm_config, methods=["POST"]),
    Route("/api/config/ping", ping_llm, methods=["POST"]),
    Route("/api/config/ping-llm", ping_llm, methods=["POST"]),
    Route("/api/config/test-llm", ping_llm, methods=["POST"]),
]

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )
]

app = Starlette(debug=True, routes=routes, middleware=middleware)


if __name__ == "__main__":
    import uvicorn
    print("[AutoTutor API Gateway] Iniciando servidor em http://0.0.0.0:8000 ...")
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(BASE_DIR / "core"), str(BASE_DIR)],
        reload_includes=["*.py"],
        reload_excludes=["*test*", "*tests*", "*.log", "*.sqlite3*", "*.db*", "*__pycache__*", "*.pytest_cache*", "*data*"]
    )
