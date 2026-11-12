"""C++ Code Validator and Simulation Engine for AutoTutor Whiteboard.

Analyzes if whiteboard text is executable C++ code, validates syntax with g++,
runs safe sandboxed execution, and outputs the synchronized simulation tape.
"""
from __future__ import annotations

import os
import re
import signal
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional

SANDBOX_MEMORY_LIMIT_MB: int = 256
SANDBOX_OUTPUT_LIMIT_BYTES: int = 65536
SANDBOX_COMPILE_TIMEOUT_SEC: float = 3.0

CPP_MARKERS = [
    r"#include", r"\bint\b", r"\bvoid\b", r"\bbool\b", r"\bauto\b",
    r"\bvector\b", r"\bqueue\b", r"\bstack\b", r"\bdeque\b",
    r"\bfor\s*\(", r"\bwhile\s*\(", r"\bcin\b", r"\bcout\b",
    r"\breturn\b", r"\bstd::", r"[{};]"
]


def is_candidate_cpp_code(text: str) -> bool:
    """Heuristic check to determine if text resembles C++ source code."""
    if not text or not text.strip():
        return False
    clean = text.strip()
    # If text is clearly prose (no semicolons, curly braces or includes)
    has_symbols = bool(re.search(r"[{};]", clean))
    matches = sum(1 for pattern in CPP_MARKERS if re.search(pattern, clean))
    return has_symbols and matches >= 2


def build_cpp_harness(raw_code: str) -> str:
    """Wraps bare C++ functions with includes and dummy main if missing."""
    code = raw_code.strip()
    has_main = bool(re.search(r"\bint\s+main\s*\(", code))
    
    headers = (
        "#include <iostream>\n"
        "#include <vector>\n"
        "#include <queue>\n"
        "#include <stack>\n"
        "#include <string>\n"
        "#include <algorithm>\n"
        "using namespace std;\n\n"
    )

    if not has_main:
        return f"{headers}{code}\n\nint main() {{ return 0; }}\n"
    elif "#include" not in code:
        return f"{headers}{code}\n"
    return code


def validate_cpp_syntax(code_text: str, timeout_sec: float = 3.0) -> Dict[str, Any]:
    """Validates C++ code against g++ compiler."""
    if not is_candidate_cpp_code(code_text):
        return {
            "is_valid_cpp": False,
            "status": "not_code",
            "message": "O texto inserido não possui estrutura de código C++ (anotação descritiva)."
        }

    harnessed_code = build_cpp_harness(code_text)

    with tempfile.TemporaryDirectory() as tmpdir:
        src_file = Path(tmpdir) / "whiteboard.cpp"
        src_file.write_text(harnessed_code, encoding="utf-8")

        cmd = ["g++", "-std=c++17", "-fsyntax-only", "-Wall", str(src_file)]
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_sec
            )
            if proc.returncode == 0:
                return {
                    "is_valid_cpp": True,
                    "status": "compiled",
                    "message": "Código C++ sintaticamente válido e compilado com sucesso."
                }
            else:
                stderr = proc.stderr
                # Clean temp path from compiler errors for human readability
                clean_err = re.sub(r"/tmp/[^:]+:", "linha ", stderr).strip()
                return {
                    "is_valid_cpp": False,
                    "status": "syntax_error",
                    "message": clean_err[:600]
                }
        except subprocess.TimeoutExpired:
            return {
                "is_valid_cpp": False,
                "status": "timeout",
                "message": "Tempo limite de compilação C++ excedido."
            }
        except Exception as e:
            return {
                "is_valid_cpp": False,
                "status": "error",
                "message": f"Falha interna ao invocar compilador C++: {e}"
            }


def execute_cpp_whiteboard(
    code_text: str,
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    start_node: Optional[str] = None,
    max_steps: int = 500,
    timeout_sec: float = 1.5
) -> Dict[str, Any]:
    """Validates, compiles, and generates synchronized execution tape for whiteboard."""
    from core.whiteboard_engine import generate_algorithm_execution_tape

    validation = validate_cpp_syntax(code_text)
    tape = generate_algorithm_execution_tape(code_text, nodes, edges, start_node, max_steps)
    
    execution_output = ""
    # If code contains main() and passed compilation, attempt safe run with graph input
    if validation["status"] == "compiled" and "int main" in code_text:
        harnessed = build_cpp_harness(code_text)
        with tempfile.TemporaryDirectory() as tmpdir:
            src_file = Path(tmpdir) / "prog.cpp"
            bin_file = Path(tmpdir) / "prog.bin"
            src_file.write_text(harnessed, encoding="utf-8")

            try:
                build = subprocess.run(
                    ["g++", "-O2", "-std=c++17", "-Wall", str(src_file), "-o", str(bin_file)],
                    capture_output=True,
                    text=True,
                    timeout=3.0
                )
            except subprocess.TimeoutExpired:
                validation["is_valid_cpp"] = False
                validation["status"] = "timeout"
                validation["message"] = "Tempo limite de compilação C++ excedido."
                build = None

            if build and build.returncode == 0:
                # Graph input: V E \n u v ...
                input_data = f"{len(nodes)} {len(edges)}\n" + "\n".join(
                    f"{e.get('from', e.get('source', e.get('u', '')))} {e.get('to', e.get('target', e.get('v', '')))}"
                    for e in edges
                ) + "\n"

                runner_path = Path(__file__).resolve().parent / "runner.py"
                if os.name == "posix" and runner_path.exists():
                    cmd = [
                        sys.executable,
                        str(runner_path),
                        str(timeout_sec),
                        str(SANDBOX_MEMORY_LIMIT_MB),
                        str(SANDBOX_OUTPUT_LIMIT_BYTES),
                        str(bin_file)
                    ]
                else:
                    cmd = [str(bin_file)]

                proc = None
                try:
                    proc = subprocess.Popen(
                        cmd,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        start_new_session=(os.name == "posix")
                    )
                    stdout_bytes, stderr_bytes = proc.communicate(
                        input_data.encode("utf-8"),
                        timeout=timeout_sec
                    )
                    stdout_str = stdout_bytes.decode(errors="replace")
                    stderr_str = stderr_bytes.decode(errors="replace")

                    if proc.returncode != 0:
                        if (b"std::bad_alloc" in stderr_bytes or "bad_alloc" in stderr_str or
                            proc.returncode in (-9, 137, -6)):
                            validation["status"] = "runtime_error"
                            validation["message"] = "Limite de memória excedido (MLE / std::bad_alloc)."
                        else:
                            validation["status"] = "runtime_error"
                            validation["message"] = f"Execução finalizada com erro em tempo de execução (código {proc.returncode})."
                        execution_output = stderr_str[:800] or stdout_str[:800]
                    else:
                        execution_output = stdout_str[:800]

                except subprocess.TimeoutExpired:
                    validation["status"] = "timeout"
                    validation["message"] = "Execução C++ interrompida por Timeout (TLE)."
                finally:
                    if proc is not None:
                        if os.name == "posix":
                            try:
                                os.killpg(proc.pid, signal.SIGKILL)
                            except (ProcessLookupError, OSError):
                                proc.poll()
                        elif proc.poll() is None:
                            proc.kill()
                        proc.wait()
            elif build and build.returncode != 0:
                clean_err = re.sub(r"/tmp/[^:]+:", "linha ", build.stderr).strip()
                validation["is_valid_cpp"] = False
                validation["status"] = "syntax_error"
                validation["message"] = clean_err[:600]

    return {
        "is_valid_cpp": validation["is_valid_cpp"],
        "compilation_status": validation["status"],
        "compiler_message": validation["message"],
        "execution_output": execution_output,
        "tape": tape,
        "total_steps": len(tape)
    }
