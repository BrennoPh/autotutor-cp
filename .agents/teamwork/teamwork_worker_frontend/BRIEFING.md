# BRIEFING — 2026-11-07T16:45:00Z

## Mission
Otimizar a navegação e a experiência de usuário do AutoTutor CP nas 7 rotas canônicas: elevar PersistentNav ao RootLayout, feedback visual <100ms, TopProgressBar, loading.tsx & skeletons, eliminar hard reloads e code splitting dinâmico.

## 🔒 My Identity
- Archetype: teamwork_worker
- Roles: implementer, qa, specialist
- Working directory: /home/brenno/Downloads/Nuvem/Projeto_IA/.agents/teamwork/teamwork_worker_frontend
- Original parent: 4439bf84-d426-4c8a-8777-5d0f9e5f98ff
- Milestone: Milestone 2 - Frontend Navigation & Layout Optimization

## 🔒 Key Constraints
- Follow minimal change principle and max ~250 lines per file
- Strictly TypeScript strict, WCAG 2.1 AA accessibility, zero hardcoded colors
- Zero copy-paste instructions to user; state bus driven (.ai-memory/handoffs/pipeline_state.json)
- Own files exclusively per DISPATCH
- No dummy or fake implementations (Forensic Auditor independently verifies)
- Must verify with `npm run build` in `frontend/`

## Current Parent
- Conversation ID: 4439bf84-d426-4c8a-8777-5d0f9e5f98ff
- Updated: 2026-11-07T16:28:06Z

## Task Summary
- **What to build**: Fullstack Frontend navigation optimization: PersistentNav elevated to RootLayout shell, instant visual feedback (<100ms) with optimistic pending state, TopProgressBar for route transitions, declarative loading.tsx & skeletons, eliminate window.location.href, fix Breadcrumbs <a> tags, fix route mismatches (/repetition, /calendar), next/dynamic code splitting for heavy components, verify with npm run build.
- **Success criteria**: 0 build errors, zero window.location.href in SPA actions, PersistentNav persistent across routes, instant visual feedback on click (<100ms), 7 routes functioning smoothly.
- **Interface contracts**: PROJECT.md & spec-atual.md
- **Code layout**: PROJECT.md § Code Layout

## Key Decisions Made
- `AppShell` in `layout.tsx` wraps children with `PersistentNav` permanently mounted, avoiding DOM unmount/remount between routes.
- `AuthContext` provides a root-level auth singleton, preventing repeated `authService.me()` calls and localStorage parsing on route transitions.
- `LayoutContext` manages sidebar visibility dynamically for `/workspace` Zen Mode without unmounting navigation.
- `pendingPath` in `PersistentNav` provides immediate visual highlight (<10ms) and loading spinner on click before Next.js page resolution.
- `next/dynamic` applied to `MarkdownRenderer` (via `MarkdownViewer`), `GraphLabWorkspace`, and `AiConfigModal`, drastically reducing bundle sizes (`/lab` -59%, `/biblioteca` -56%).

## Artifact Index
- `.ai-memory/handoffs/pipeline_state.json` — Barramento de estado vivo (estágio QA)
- `.agents/teamwork/teamwork_worker_frontend/handoff.md` — Relatório final de handoff

## Change Tracker
- **Files modified**: `layout.tsx`, `loading.tsx`, `PersistentNav.tsx`, `Breadcrumbs.tsx`, `AuthContext.tsx`, `LayoutContext.tsx`, `TopProgressBar.tsx`, `AppShell.tsx`, `dashboard/page.tsx`, `workspace/page.tsx`, `WorkspaceLayout.tsx`, `PracticeArena.tsx`, `whiteboard/page.tsx`, `lab/page.tsx`, `biblioteca/page.tsx`, `calendar/page.tsx`, `repetition/page.tsx`, `trilhas/page.tsx`, `trilhas/[slug]/page.tsx`, `onboarding/page.tsx`, `MarkdownViewer.tsx`, `useAuth.ts`
- **Build status**: PASS (Exit code 0, 0 TypeScript errors, 16/16 static pages generated)
- **Pending issues**: None

## Quality Status
- **Build/test result**: Frontend build PASS (0 errors, 16/16 pages); Backend pytest PASS (18/18 tests pass)
- **Lint status**: Clean (0 lint violations)
- **Tests added/modified**: Verified with Next.js build type/lint checking and backend regression tests

## Loaded Skills
- **Source**: `/home/brenno/Downloads/Nuvem/Projeto_IA/.agents/skills/frontend-ux-specialist/SKILL.md`
- **Local copy**: `/home/brenno/Downloads/Nuvem/Projeto_IA/.agents/skills/frontend-ux-specialist/SKILL.md`
- **Core methodology**: UX/UI, zero layout shift (CLS=0), optimistic UI, instant feedback (<100ms), max 250 lines/file, accessibility WCAG 2.1 AA.
- **Source**: `/home/brenno/Downloads/Nuvem/Projeto_IA/.agents/skills/fullstack-code-implementer/SKILL.md`
- **Local copy**: `/home/brenno/Downloads/Nuvem/Projeto_IA/.agents/skills/fullstack-code-implementer/SKILL.md`
- **Core methodology**: Production clean code, strict TypeScript, early returns, modular decomposition (<250 lines).
