## 2026-11-07T16:28:06Z
You are teamwork_worker: Frontend UX & Navigation Specialist.
Your working directory is: /home/brenno/Downloads/Nuvem/Projeto_IA/.agents/teamwork/teamwork_worker_frontend
You MUST read /home/brenno/Downloads/Nuvem/Projeto_IA/.agents/teamwork/ORIGINAL_REQUEST.md before starting work.
Also read:
- /home/brenno/Downloads/Nuvem/Projeto_IA/.agents/teamwork/PROJECT.md
- /home/brenno/Downloads/Nuvem/Projeto_IA/.ai-memory/handoffs/spec-atual.md
- /home/brenno/Downloads/Nuvem/Projeto_IA/.agents/teamwork/teamwork_explorer_survey_1/handoff.md
- /home/brenno/Downloads/Nuvem/Projeto_IA/.agents/teamwork/teamwork_explorer_survey_2/handoff.md
- /home/brenno/Downloads/Nuvem/Projeto_IA/AGENTS.md

Domain Skills to consult:
- /home/brenno/Downloads/Nuvem/Projeto_IA/.agents/skills/frontend-ux-specialist/SKILL.md
- /home/brenno/Downloads/Nuvem/Projeto_IA/.agents/skills/fullstack-code-implementer/SKILL.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

File Ownership:
You own exclusively:
- `frontend/src/app/layout.tsx`
- `frontend/src/app/loading.tsx`
- `frontend/src/components/navigation/PersistentNav.tsx`
- `frontend/src/components/navigation/Breadcrumbs.tsx`
- `frontend/src/context/AuthContext.tsx` (or auth provider integration)
- `frontend/src/components/ui/TopProgressBar.tsx` (top transition progress bar)
- `frontend/src/app/dashboard/page.tsx`
- `frontend/src/app/workspace/page.tsx`
- `frontend/src/components/workspace/WorkspaceLayout.tsx`
- `frontend/src/components/workspace/PracticeArena.tsx`
- `frontend/src/app/whiteboard/page.tsx`
- `frontend/src/app/lab/page.tsx`
- `frontend/src/app/biblioteca/page.tsx`
- `frontend/src/app/calendar/page.tsx`
- `frontend/src/app/repetition/page.tsx`
- `frontend/src/app/trilhas/page.tsx`
- `frontend/src/app/onboarding/page.tsx`
- `.ai-memory/handoffs/pipeline_state.json`

Implementation Objectives (Per PROJECT.md and spec-atual.md):
1. **PersistentNav in Layout**:
   - Move or wrap `PersistentNav` so that it persists across page navigations in `frontend/src/app/layout.tsx` (or a persistent client shell). Ensure `PersistentNav` is NOT destroyed and remounted on each route change.
   - For `/workspace` Zen Mode or pages like `/login` or `/onboarding`, support hiding the sidebar via path detection (`usePathname()`) or an app layout context.
   - Remove redundant `<PersistentNav />` calls from the 7 pages so there are no duplicate navbars.
2. **Instant Visual Feedback (<100ms) on PersistentNav**:
   - In `PersistentNav.tsx`: implement optimistic click state (e.g. `pendingPath` with `setPendingPath(item.path)` on click or `useTransition()`).
   - Immediately upon click, highlight the clicked item and/or show a subtle spinner/indicator so the user sees instant feedback in <100ms.
   - Set `prefetch={true}` on all primary navigation `<Link>` components.
3. **Top Transition Progress Bar**:
   - Add a lightweight top progress bar in `layout.tsx` that triggers on route transition (visual progress indicator across the top of the screen).
4. **Declarative `loading.tsx` & Route Skeletons**:
   - Create `frontend/src/app/loading.tsx` with a clean skeleton.
   - Add loading skeleton to `/workspace` (`PracticeArena.tsx`) so there is no empty blank screen while `problemDetail` loads.
5. **Eliminate `window.location.href` Hard Reloads**:
   - In `dashboard/page.tsx`: replace `window.location.href = "/workspace"` with `router.push("/workspace")` or `<Link>`. Same for `/onboarding` and `/trilhas`.
   - In `calendar/page.tsx:109`: replace `window.location.href = url` with `router.push(url)`.
   - In `trilhas/page.tsx:70`: replace with `router.push`.
   - In `onboarding/page.tsx:36`: replace with `router.push("/calendar")`.
6. **Fix Breadcrumbs Native `<a>` Tags**:
   - In `frontend/src/components/navigation/Breadcrumbs.tsx`: replace native `<a href="...">` with Next.js `<Link href="...">`.
7. **Fix Route Mismatches**:
   - Fix `/repetition` (`currentPath="/repetition"`) and `/calendar` (`currentPath="/calendar"`).
8. **Code Splitting via `next/dynamic`**:
   - Dynamically load heavy components (`GraphLabWorkspace`, KaTeX/MarkdownRenderer, `AiConfigModal`) with `{ ssr: false, loading: () => <Skeleton /> }` to reduce initial route chunk size.
9. **Build & Verify**:
   - Run `npm run build` in `frontend/`. Ensure exit code 0, 0 TypeScript errors, and successful static page generation.
   - Test that navigation across all 7 routes (`/`, `/workspace`, `/whiteboard`, `/lab`, `/biblioteca`, `/repetition`, `/calendar`) works seamlessly.
10. Update `.ai-memory/handoffs/pipeline_state.json` to stage `QA` (`last_output_by: Front_End`).
11. Write your handoff report to:
    `/home/brenno/Downloads/Nuvem/Projeto_IA/.agents/teamwork/teamwork_worker_frontend/handoff.md`
    When finished, message parent with summary of changes and build results.
