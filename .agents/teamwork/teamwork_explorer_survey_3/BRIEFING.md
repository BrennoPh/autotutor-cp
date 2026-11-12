# BRIEFING — 2026-11-07T15:57:30Z

## Mission
Investigate network calls, backend endpoints, latency bottlenecks, caching, and data fetching across 7 routes in AutoTutor CP.

## 🔒 My Identity
- Archetype: explorer
- Roles: Fullstack Network & Backend Endpoints Explorer
- Working directory: /home/brenno/Downloads/Nuvem/Projeto_IA/.agents/teamwork/teamwork_explorer_survey_3
- Original parent: 4439bf84-d426-4c8a-8777-5d0f9e5f98ff
- Milestone: Fullstack Performance Survey

## 🔒 Key Constraints
- Read-only investigation — do NOT implement
- Base working directory in `.agents/teamwork/teamwork_explorer_survey_3`
- Cite exact file paths, line numbers, and concrete remediation recommendations

## Current Parent
- Conversation ID: 4439bf84-d426-4c8a-8777-5d0f9e5f98ff
- Updated: 2026-11-07T15:57:30Z

## Investigation State
- **Explored paths**:
  - `frontend/src/app/page.tsx`, `frontend/src/app/dashboard/page.tsx` (Route `/`)
  - `frontend/src/app/workspace/page.tsx`, `frontend/src/components/workspace/WorkspaceLayout.tsx`, `frontend/src/components/workspace/PracticeArena.tsx` (Route `/workspace`)
  - `frontend/src/app/whiteboard/page.tsx`, `frontend/src/components/whiteboard/GraphLabWorkspace.tsx` (Route `/whiteboard`)
  - `frontend/src/app/lab/page.tsx` (Route `/lab`)
  - `frontend/src/app/biblioteca/page.tsx`, `frontend/src/services/libraryService.ts` (Route `/biblioteca`)
  - `frontend/src/app/repetition/page.tsx`, `frontend/src/app/revisao/page.tsx` (Route `/repetition`)
  - `frontend/src/app/calendar/page.tsx`, `frontend/src/app/calendario/page.tsx` (Route `/calendar`)
  - `frontend/src/components/navigation/PersistentNav.tsx`
  - `frontend/src/hooks/useAuth.ts`, `frontend/src/hooks/useWorkspaceState.ts`, `frontend/src/hooks/useOnboardingGuard.ts`
  - `frontend/src/services/apiClient.ts`, `frontend/src/services/progressService.ts`, `frontend/src/services/problemService.ts`, `frontend/src/services/libraryService.ts`, `frontend/src/services/authService.ts`
  - `frontend/next.config.js`, `frontend/src/middleware.ts`
  - `autotutor_cp/api_server.py`, `autotutor_cp/core/problem_bank.py`, `autotutor_cp/core/progress_store.py`, `autotutor_cp/core/knowledge.py`, `autotutor_cp/core/library.py`, `autotutor_cp/core/accounts.py`
- **Key findings**:
  1. No global auth/cache state: `PersistentNav` unmounts/remounts on every page transition, causing `useAuth()` to fire `GET /api/auth/me` on every route switch. On `/biblioteca`, `useAuth()` is called in two components concurrently.
  2. Bloated `/api/progress` response: returns 834 KB payload with 46 full materials duplicated as `data` and `payload`, taking ~580ms backend processing time. Dashboard only needs 2 integers (`streak_days`, `solved_count`).
  3. Starlette event-loop blocking: all endpoints are `async def`, but execute synchronous disk file I/O (`load_problems` reads 3 JSON files on every request), synchronous SQLite table scans (`kb.stats()`), synchronous LLM calls (`CodigenTutor.generate_material`), and synchronous C++ judge execution (`current_judge.judge`). Any long-running call blocks the whole server from serving route requests.
  4. Multiple hard browser page reloads: several links/buttons use `window.location.href = ...` instead of `router.push(...)` (e.g. `dashboard/page.tsx:97`, `dashboard/page.tsx:123`, `dashboard/page.tsx:158`, `calendar/page.tsx:109`), completely destroying the React tree and re-downloading bundles.
  5. Route highlighting bugs: `PersistentNav` receives mismatched paths on `/repetition` (`currentPath="/revisao"`) and `/calendar` (`currentPath="/calendario"`), breaking visual active states.
  6. Workspace waterfall & blank render: `/workspace` runs `listProblems()` then `getProblem(id)` sequentially, during which `problemDetail` is null, rendering an unstyled blank screen with no loading skeleton.
  7. Zero client-side caching: standard fetch in `apiClient.ts` without cache, deduplication, SWR/React Query, or request timeouts.
- **Unexplored areas**: None remaining for the assigned 7 questions.

## Key Decisions Made
- All evidence has been collected, timed, and cross-referenced with exact line numbers.
- Proceed to compile comprehensive handoff.md following 5-component protocol.

## Artifact Index
- DISPATCH.md — incoming task dispatch
- progress.md — liveness heartbeat
- BRIEFING.md — situational awareness
- handoff.md — final comprehensive report
