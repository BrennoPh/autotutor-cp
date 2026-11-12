## 2026-11-07T16:00:27Z
You are teamwork_worker: Backend Performance & Spec Architect.
Your working directory is: /home/brenno/Downloads/Nuvem/Projeto_IA/.agents/teamwork/teamwork_worker_backend
You MUST read /home/brenno/Downloads/Nuvem/Projeto_IA/.agents/teamwork/ORIGINAL_REQUEST.md before starting work.
Also read:
- /home/brenno/Downloads/Nuvem/Projeto_IA/.agents/teamwork/PROJECT.md
- /home/brenno/Downloads/Nuvem/Projeto_IA/.agents/teamwork/teamwork_explorer_survey_3/handoff.md
- /home/brenno/Downloads/Nuvem/Projeto_IA/AGENTS.md

Domain Skills to consult:
- /home/brenno/Downloads/Nuvem/Projeto_IA/.agents/skills/backend-api-specialist/SKILL.md
- /home/brenno/Downloads/Nuvem/Projeto_IA/.agents/skills/software-architect-planner/SKILL.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

File Ownership:
You own exclusively:
- `autotutor_cp/api_server.py`
- `autotutor_cp/core/problem_bank.py`
- `autotutor_cp/core/library.py`
- `autotutor_cp/core/knowledge.py`
- `.ai-memory/handoffs/spec-atual.md`
- `.ai-memory/handoffs/pipeline_state.json`

Implementation Objectives:
1. Optimize `/api/progress` in `autotutor_cp/api_server.py`:
   - By default, do NOT serialize and return the full content body of all 46 saved materials in `/api/progress`.
   - Return `materials_count` and a lightweight list of materials with only `{ "id": ..., "title": ..., "created_at": ... }`.
   - Remove the duplicate payload fields (`data` and `payload` containing the same dict).
   - Support `include_materials=true` query param or create `/api/progress/materials` if full body is requested.
   - Verify payload drops from 834 KB to <2 KB.
2. In-memory caching for static JSON files:
   - In `autotutor_cp/core/problem_bank.py`: Add `@functools.lru_cache()` to `load_problems()`. Add a `clear_cache()` helper if ever mutated.
   - In `autotutor_cp/core/library.py`: Add `@functools.lru_cache()` to `resources()` and `deep_guides()`.
3. In `autotutor_cp/core/knowledge.py`:
   - Add caching to `stats()` with TTL (or timestamp-based in-memory cache) so it doesn't run 5 SQLite queries with full table scan over 7,187 docs on every search.
4. Offload heavy synchronous blocking operations in `async def` endpoints:
   - In `api_server.py`, use `from starlette.concurrency import run_in_threadpool` for synchronous disk I/O, heavy judge calls or subprocesses where appropriate.
5. Verification:
   - Run the backend test suite: `python3 -m pytest autotutor_cp/tests/ -v`. Ensure 100% pass rate.
   - Measure `/api/progress` response time and size using curl or python benchmark to confirm latency reduction.
6. Protocol & Spec:
   - Write the technical specification for full-stack navigation optimization in `.ai-memory/handoffs/spec-atual.md`.
   - Update `.ai-memory/handoffs/pipeline_state.json` with active_stage="FRONTEND", last_output_by="Back_End & Planner", modified_files, test_status.
7. Write your handoff report to:
   /home/brenno/Downloads/Nuvem/Projeto_IA/.agents/teamwork/teamwork_worker_backend/handoff.md
   When complete, send a message to your parent with summary and test results.
