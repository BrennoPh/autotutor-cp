# Project: Otimização de Alta Performance e Latência de Navegação no AutoTutor CP

## Architecture
- **Frontend**: Next.js 14 App Router, TypeScript, Tailwind CSS, Lucide icons.
  - Core navigation: `frontend/src/app/layout.tsx` (Shared Root Layout), `AppShell.tsx`, `PersistentNav.tsx`, `Breadcrumbs.tsx`, `TopProgressBar.tsx`.
  - 7 Canonical Routes: `/` (Dashboard), `/workspace`, `/whiteboard`, `/lab`, `/biblioteca`, `/repetition`, `/calendar`.
- **Backend**: Starlette/FastAPI (`autotutor_cp/api_server.py`), Uvicorn on port 8000.
  - Endpoints called during navigation: `/api/auth/me`, `/api/progress`, `/api/problems`, `/api/library/books`, `/api/library/search`.
- **Data Flow & State Bus**:
  - State bus: `.ai-memory/handoffs/pipeline_state.json` and `.ai-memory/handoffs/spec-atual.md`.
  - History & Long-term memory: `.ai-memory/handoffs/projeto-atual.md`.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Otimização do `/api/progress` | Reduzir payload de 834 KB para <2 KB, remover duplicação `data`/`payload`, desacoplar materiais completos para query sob demanda | M1 (DONE) | Survey Explorer 3 |
| 2 | Cache em Memória de Catálogos JSON | Implementar `lru_cache` para `load_problems`, `resources` e `deep_guides` eliminando leituras repetidas de disco | M1 (DONE) | Survey Explorer 3 |
| 3 | Cache de Estatísticas do Acervo | Cachear `kb.stats()` com TTL evitando full table scan SQLite sobre 7.187 docs a cada busca | M1 (DONE) | Survey Explorer 3 |
| 4 | Desacoplamento de Tarefas Bloqueantes | Executar I/O síncrono e subprocessos pesados em threadpool para não travar o event loop da Starlette | M1 (DONE) | Survey Explorer 3 |
| 5 | Elevação do `PersistentNav` para o Layout | Mover a barra para `frontend/src/app/layout.tsx` via AppShell, mantendo DOM persistente | M2 (DONE) | Survey Explorer 1, 2 |
| 6 | Sessão Compartilhada AuthContext | Evitar tempestade de chamadas a `/api/auth/me` a cada clique de rota montando sessão no topo do app | M2 (DONE) | Survey Explorer 1, 2, 3 |
| 7 | Feedback Visual Instantâneo (<100ms) | Estado otimista (`pendingPath` <10ms), spinner e indicador imediato de clique em `PersistentNav` | M2 (DONE) | Survey Explorer 1, 2 |
| 8 | Barra de Progresso Global de Transição | Barra de progresso discreta no topo da janela acionada imediatamente nas transições de rota | M2 (DONE) | Survey Explorer 1, 2 |
| 9 | Criação de `loading.tsx` e Skeletons | Adicionar `loading.tsx` e skeletons de carregamento para eliminar congelamento de tela | M2 (DONE) | Survey Explorer 1, 2 |
| 10 | Eliminação de `window.location.href` | Substituir todos os hard reloads em Dashboard, Calendar, Trilhas e Onboarding por `router.push()` | M2 (DONE) | Survey Explorer 1, 2, 3 |
| 11 | Conversão de tags `<a>` em Breadcrumbs | Substituir tags `<a href>` em `Breadcrumbs.tsx` por `<Link href>` do Next.js | M2 (DONE) | Survey Explorer 1 |
| 12 | Correção de Mismatches de Rota | Corrigir `currentPath` para `/repetition` e `/calendar`, garantindo destaque ativo consistente | M2 (DONE) | Survey Explorer 1, 2, 3 |
| 13 | Code Splitting via `next/dynamic` | Carregar sob demanda componentes pesados (`GraphLabWorkspace`, KaTeX, MarkdownRenderer) reduzindo chunks | M2 (DONE) | Survey Explorer 2 |
| 14 | Resolução de Waterfall no `/workspace` | Paralelizar `listProblems` e `getProblem` e exibir skeleton animado durante carregamento inicial | M2 (DONE) | Survey Explorer 3 |
| 15 | Medição Programática & Benchmarks | Medir TTFB e tempo de resposta antes e depois em todas as 7 rotas e endpoints de backend | M3 (DONE) | Requirement R3 & AC |
| 16 | Verificação de Integridade e Testes E2E | Rodar suíte de testes unitários, testes de integração e auditoria forense de integridade | M3 (DONE) | Audit & AC |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Backend Performance & Unblocking | Features 1-4 (`api_server.py`, `problem_bank.py`, `library.py`, `knowledge.py`) | none | DONE |
| 2 | Frontend Navigation & Layout Optimization | Features 5-14 (`app/layout.tsx`, `PersistentNav.tsx`, `Breadcrumbs.tsx`, `loading.tsx`, `WorkspaceLayout.tsx`, `page.tsx`) | M1 | DONE |
| 3 | Benchmarking, Testing & Forensic Audit | Features 15, 16 (medir latências antes/depois, 2 reviewers, 2 challengers, 1 auditor) | M1, M2 | DONE |

## Gate Verdict
- `GATE_STATUS.md`: **PASS** (100% dos critérios satisfeitos).
  - Reviewer 1 (Frontend): APPROVE
  - Reviewer 2 (Backend): APPROVE
  - Challenger 1 (Latency Benchmarks): CONFIRM
  - Challenger 2 (Stress Integrity): CONFIRM / APPROVE
  - Auditor 1 (Forensic Integrity): CLEAN (Zero Violações)
