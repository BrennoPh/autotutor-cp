# Relatório de Investigação Técnica: Renderização de Páginas, Hidratação e Bundle Overhead das 7 Rotas

**Autor:** teamwork_explorer instance 2 (Page-Level Rendering & 7 Routes Explorer)  
**Data:** 2026-11-07  
**Status:** Concluído  
**Escopo de Rotas Analisadas:** `/` (Dashboard), `/workspace`, `/whiteboard`, `/lab`, `/biblioteca`, `/repetition`, `/calendar`  

---

## 1. Observações (Evidence-Backed Direct Observations)

### 1.1 Classificação Server vs Client Components ("use client")
Todas as 7 rotas inspecionadas são declaradas como **Client Components** puros (`"use client"`), sem uso de Server Components (RSC) para carregamento inicial de dados ou isolamento estrutural:

| Rota | Arquivo Fonte | Diretiva / Linha | Arquitetura |
|---|---|---|---|
| `/` | `frontend/src/app/page.tsx:1-5` delega para `frontend/src/app/dashboard/page.tsx:1` | `"use client"` (L1) | 100% Client Component |
| `/workspace` | `frontend/src/app/workspace/page.tsx:1` | `"use client"` (L1) | 100% Client Component |
| `/whiteboard` | `frontend/src/app/whiteboard/page.tsx:1` | `"use client"` (L1) | 100% Client Component |
| `/lab` | `frontend/src/app/lab/page.tsx:1` | `"use client"` (L1) | 100% Client Component (548 linhas em arquivo único) |
| `/biblioteca` | `frontend/src/app/biblioteca/page.tsx:1` | `"use client"` (L1) | 100% Client Component (814 linhas em arquivo único) |
| `/repetition` | `frontend/src/app/repetition/page.tsx:1` | `"use client"` (L1) | 100% Client Component |
| `/calendar` | `frontend/src/app/calendar/page.tsx:1` | `"use client"` (L1) | 100% Client Component |

### 1.2 Layout Raiz Desprovido de Navegação Compartilhada (Layout Thrashing)
- `frontend/src/app/layout.tsx:9-21`: O `RootLayout` renderiza apenas `<html><body className="...">{children}</body></html>`. Não há renderização de shell, sidebar ou navegação global no layout compartilhado.
- `<PersistentNav />` é importado e instanciado **manualmente dentro de cada página individual**:
  - `frontend/src/app/dashboard/page.tsx:103`: `<PersistentNav currentPath="/" ... />`
  - `frontend/src/components/workspace/WorkspaceLayout.tsx:83`: `<PersistentNav currentPath="/workspace" />`
  - `frontend/src/app/whiteboard/page.tsx:56, 140`: `<PersistentNav currentPath="/whiteboard" />`
  - `frontend/src/app/lab/page.tsx:188, 530`: `<PersistentNav currentPath="/lab" />`
  - `frontend/src/app/biblioteca/page.tsx:173`: `<PersistentNav currentPath="/biblioteca" />`
  - `frontend/src/app/repetition/page.tsx:113`: `<PersistentNav currentPath="/revisao" />`
  - `frontend/src/app/calendar/page.tsx:71`: `<PersistentNav currentPath="/calendario" />`
- **Impacto Direto:** A cada navegação de rota, o componente `PersistentNav` é completamente desmontado do DOM e remontado do zero. O Next.js não consegue preservar a árvore de layout nem o estado do sidebar.

### 1.3 Ausência Total de `loading.tsx` e Feedback Instantâneo (<100ms)
- `find frontend/src/app -name "loading.tsx"` retornou **0 arquivos**. Não existe `loading.tsx` nem na raiz `frontend/src/app/` nem em nenhuma das 7 sub-rotas.
- No componente `frontend/src/components/navigation/PersistentNav.tsx:74-88`:
  - Os links de navegação utilizam `<Link href={item.path} onClick={() => onNavigate?.(item.path)} className="...">`.
  - Não há estado de pending (`useTransition`), indicador de carregamento, spinner ou barra de progresso (ex: nprogress).
  - Quando o usuário clica em um link do menu lateral, **nenhum feedback visual imediato (<100ms) é renderizado**. O navegador permanece estático na página anterior até que o bundle da rota de destino seja baixado, parseado e executado.

### 1.4 Ausência de `next/dynamic` e Tamanho Excessivo dos Chunks de Rota
- `grep -rn "next/dynamic" frontend/src/` retornou **0 ocorrências**. Não há um único dynamic import (`next/dynamic({ ssr: false })`) em todo o projeto.
- Tamanho real dos chunks de página gerados em `frontend/.next/static/chunks/app/`:
  - `app/workspace/page.js`: **6.3 MB**
  - `app/lab/page.js`: **6.0 MB**
  - `app/biblioteca/page.js`: **5.6 MB**
  - `app/whiteboard/page.js`: **1.3 MB**
  - `app/repetition/page.js`: **894 KB**
  - `app/calendar/page.js`: **852 KB**
  - `app/page.js`: **849 KB**
- Bibliotecas pesadas importadas estaticamente no topo dos componentes:
  - `MarkdownRenderer` (`frontend/src/components/ui/MarkdownRenderer.tsx:5-10`): importa estaticamente `react-markdown`, `remark-gfm`, `remark-math`, `rehype-katex`, `rehype-sanitize`, pacote completo do KaTeX e `MermaidDiagram`.
  - `GraphLabWorkspace` (`frontend/src/components/whiteboard/GraphLabWorkspace.tsx`, 28.3 KB de código):
    - Importado estaticamente em `frontend/src/app/whiteboard/page.tsx:7`.
    - Importado estaticamente em `frontend/src/app/lab/page.tsx:9` e em `StudyCanvasWorkspace.tsx:5`.
    - Importado estaticamente em `frontend/src/components/workspace/StudyReader.tsx:6` — fazendo com que `/workspace` carregue o motor visual de grafos completo mesmo quando o usuário abre apenas a Arena de Exercícios (`PracticeArena`).
  - `AiConfigModal` (`frontend/src/components/config/AiConfigModal.tsx`): importado estaticamente no topo de `PersistentNav.tsx:22`. Como `PersistentNav` está em todas as páginas, esse modal está embutido em todos os chunks.

### 1.5 Custo de Montagem de `useEffect` e Chamadas Redundantes de Autenticação/Storage
- Em `frontend/src/components/navigation/PersistentNav.tsx:34`:
  - Chama `const { user, isAuthenticated, logout } = useAuth();`.
  - Como `PersistentNav` é remontado a cada troca de rota, `useAuth` (`frontend/src/hooks/useAuth.ts:15-45`) executa seu `useEffect` em cada transição de rota:
    - Linhas 17-18: lê `localStorage.getItem("autotutor_auth_token")` e `localStorage.getItem("autotutor_auth_user")`.
    - Linha 22: executa `JSON.parse(storedUser)`.
    - Linhas 25-36: dispara a requisição de rede assíncrona `authService.me(storedToken)` sem cache.
- Em `frontend/src/app/dashboard/page.tsx`:
  - Linha 79: `useOnboardingGuard` faz `localStorage.getItem("autotutor_user_profile")` e `JSON.parse`.
  - Linha 84: `useEffect` dispara `progressService.getProgress()`.
- Em `frontend/src/app/workspace/page.tsx` (`PracticeArena.tsx`):
  - Linha 98: dispara `problemService.listProblems()`.
  - Linha 126: dispara `problemService.getProblem(selectedProblemId)`.
- Em `frontend/src/app/biblioteca/page.tsx`:
  - Linhas 83-92: dispara duas requisições paralelas no mount: `libraryService.getBooksAndGuides()` e `libraryService.searchKnowledge("", undefined, 12)`.
- Em `frontend/src/app/calendar/page.tsx`:
  - Linhas 34-52: faz parse síncrono de `localStorage.getItem("autotutor_user_profile")` e `autotutor_scheduled_tasks`. Em caso de fallback, executa geração síncrona pesada (`generateCustomTrack` e `generateStudySchedule`) na main thread do navegador.

### 1.6 Anti-padrão de Navegação com `window.location.href` (Hard Reloads)
Foram identificados múltiplos botões e callbacks de navegação interna que utilizam `window.location.href` em vez do roteador do Next.js (`router.push` ou `<Link>`):
- `frontend/src/app/dashboard/page.tsx:97`: `window.location.href = "/workspace";` (botão de retomar estudo)
- `frontend/src/app/dashboard/page.tsx:123`: `window.location.href = "/onboarding";` (alerta de diagnóstico)
- `frontend/src/app/dashboard/page.tsx:158`: `window.location.href = "/trilhas/${id}";` (carrossel de trilhas)
- `frontend/src/app/calendar/page.tsx:109`: `onNavigateAction={(url) => (window.location.href = url)}` (clique em tarefas do calendário)
- `frontend/src/hooks/useAuth.ts:93`: `window.location.href = "/login";`
- **Impacto Direto:** O uso de `window.location.href` descarta a memória SPA, recarrega o documento HTML inteiro do servidor, força o navegador a parsear novamente 6+ MB de scripts e destrói o estado global.

### 1.7 Mismatch de Nomes de Rota em `PersistentNav`
- `frontend/src/components/navigation/PersistentNav.tsx:42-43`:
  - Rota de Calendário no navItems: `{ label: "Calendário", path: "/calendar", icon: Calendar }`
  - Rota de Repetição no navItems: `{ label: "Repetição & Memória", path: "/repetition", icon: Brain }`
- No entanto:
  - `frontend/src/app/calendar/page.tsx:71` passa: `<PersistentNav currentPath="/calendario" />` (o que faz a verificação `activePath.startsWith(item.path)` falhar para `/calendar`).
  - `frontend/src/app/repetition/page.tsx:113` passa: `<PersistentNav currentPath="/revisao" />` (o que faz a verificação falhar para `/repetition`).
  - Existem pastas de redirecionamento legadas `frontend/src/app/calendario/page.tsx` e `frontend/src/app/revisao/page.tsx` que executam `redirect("/calendar")` e `redirect("/repetition")`, gerando saltos desnecessários caso URLs antigas sejam acionadas.

---

## 2. Cadeia Lógica (Logic Chain)

1. **A percepção de travamento (unresponsiveness) tem como causa primária a inexistência de feedback de navegação instantâneo (<100ms):**
   - *Observação 1.3:* Ao clicar em `<Link href="...">` em `PersistentNav`, nada se altera na tela até que a próxima rota complete sua carga.
   - *Consequência:* O usuário não recebe feedback visual imediato (sem barra de progresso, sem spinner no botão, sem `loading.tsx`). Diante de um delay de 400ms a 2.500ms, o usuário tem a sensação de que o clique falhou ou a página congelou.

2. **O tempo de transição entre rotas é agravado pelo tamanho descomunal dos chunks de rota (5.6 MB a 6.3 MB):**
   - *Observação 1.4:* As rotas `/workspace`, `/lab` e `/biblioteca` possuem bundles gigantescos gerados pelo empacotamento estático de KaTeX, parsers de Markdown (`micromark`, `mdast`, `unist`), diagramas Mermaid e o canvas de grafos (`GraphLabWorkspace`).
   - *Observação 1.4:* Como `next/dynamic` não é utilizado, nenhum componente pesado é postergado; todo o código precisa ser baixado e avaliado pelo runtime JavaScript da V8 antes da montagem da tela.

3. **A destruição do layout compartilhado invalida a eficiência do App Router:**
   - *Observação 1.2:* Por não estar em `frontend/src/app/layout.tsx`, o componente `PersistentNav` sofre desmontagem e remontagem completas a cada transição de tela.
   - *Observação 1.5:* Cada montagem de `PersistentNav` re-executa `useAuth`, acionando leituras síncronas de `localStorage` e chamadas de rede para `/auth/me`.
   - *Consequência:* A árvore DOM é destruída e reconstruída por completo, descartando as otimizações de layout caching do Next.js App Router e causando layout thrashing.

4. **O uso de `window.location.href` degrada ações pontuais para recarregamentos completos (Full Page Reloads):**
   - *Observação 1.6:* Nos pontos críticos de conversão (ex: botão "Continuar Estudo" no Cockpit do Dashboard e clique no Calendário), o código força `window.location.href`.
   - *Consequência:* Todo o benefício da navegação SPA do Next.js é abortado, gerando latência de carregamento de documento novo e recarregamento integral dos 6 MB de JavaScript.

5. **A ausência de Server Components e Suspense Boundaries sobrecarrega a main thread do cliente:**
   - *Observação 1.1 e 1.5:* Todas as 7 rotas executam fetching de dados via `useEffect` no cliente, acionando montagens e cascatas de renderização sem suspensão assíncrona granular.

---

## 3. Ressalvas e Limitações (Caveats)

1. **Ambiente de Desenvolvimento vs Produção:**
   - Em modo de desenvolvimento (`next dev`), as rotas são compiladas on-demand (just-in-time) na primeira vez que são acessadas, o que adiciona 1 a 3 segundos extras à navegação inicial de cada rota.
   - No entanto, a análise do `.next` e dos imports estáticos comprovou que mesmo após a compilação, o chunk de cada rota individual permanece entre 850 KB e 6.3 MB devido ao empacotamento indiscriminado de dependências client-side.
2. **Backend Network Round-Trip:**
   - Este relatório concentrou-se especificamente na camada de front-end (renderização, hidratação, bundles e navegação). Latências adicionais originadas nas respostas do backend Starlette/FastAPI (ex: endpoints `/api/problems`, `/api/library/search`, `/api/auth/me`) atuam em cascata após a montagem do componente.
3. **Restrição de Leitura (Read-Only Investigation):**
   - Nenhuma alteração foi aplicada no código-fonte do projeto durante esta investigação, em estrita conformidade com as regras do papel de Explorer.

---

## 4. Conclusão e Recomendações de Remediação

A percepção de lentidão na navegação do AutoTutor CP decorre de **quatro gargalos arquiteturais fundamentais no front-end**:
1. **Falta de layout persistente:** `PersistentNav` precisa ser movido para `frontend/src/app/layout.tsx` (ou um layout aninhado de rota interna), eliminando a remontagem e o layout shift a cada clique.
2. **Ausência de estado de transição imediato:** Falta de indicador visual de carregamento (<100ms) no `PersistentNav` (usando `useTransition` ou barra de carregamento top-level) e inexistência de `loading.tsx` com skeletons nas rotas.
3. **Bundles monolíticos sem `next/dynamic`:** Componentes de alto peso (`GraphLabWorkspace`, `MarkdownRenderer` com KaTeX, `AiConfigModal`, `AiTutorDock`) devem ser carregados dinamicamente via `next/dynamic({ ssr: false, loading: () => <Skeleton /> })`.
4. **Hard Reloads acidentais:** Substituição de todos os `window.location.href` por `router.push()` ou `<Link>` do Next.js.

### Plano de Remediação Concreto (Proposta para Planejador / Front_End):

#### R1. Mover `PersistentNav` para o Layout Compartilhado
- **Alvo:** `frontend/src/app/layout.tsx` e `frontend/src/components/navigation/PersistentNav.tsx`.
- **Ação:**
  - Extrair o layout shell (desktop sidebar + mobile bottom bar + content container) para um layout wrapper unificado (ex: `AppLayout` ou dentro do próprio `RootLayout`).
  - Remover as instâncias manuais de `<PersistentNav>` dos 7 arquivos de página (`dashboard`, `workspace`, `whiteboard`, `lab`, `biblioteca`, `repetition`, `calendar`).
  - Centralizar a sessão de autenticação em um `AuthProvider` de contexto no topo do layout, eliminando requisições repetidas a `authService.me()` a cada troca de rota.

#### R2. Adicionar Feedback Visual Imediato (<100ms) e `loading.tsx`
- **Alvo:** `PersistentNav.tsx` e `frontend/src/app/**/loading.tsx`.
- **Ação:**
  - Em `PersistentNav.tsx`, usar `useTransition` do React 18:
    ```tsx
    const [isPending, startTransition] = useTransition();
    // Ao clicar em Link:
    onClick={(e) => {
      // ativar feedback de loading imediato no item clicado
    }}
    ```
  - Criar `frontend/src/app/loading.tsx` com um skeleton global de carregamento rápido (<50ms).
  - Criar skeletons específicos para rotas pesadas (`workspace/loading.tsx`, `whiteboard/loading.tsx`, `lab/loading.tsx`, `biblioteca/loading.tsx`).

#### R3. Aplicar Dynamic Imports (`next/dynamic`) nas Bibliotecas Pesadas
- **Alvo:** `WorkspaceLayout.tsx`, `lab/page.tsx`, `whiteboard/page.tsx`, `biblioteca/page.tsx`, `PersistentNav.tsx`.
- **Ação:**
  - Carregar `GraphLabWorkspace` sob demanda:
    ```tsx
    const GraphLabWorkspace = dynamic(
      () => import("@/components/whiteboard/GraphLabWorkspace").then((m) => m.GraphLabWorkspace),
      { ssr: false, loading: () => <GraphLabSkeleton /> }
    );
    ```
  - Carregar `MarkdownViewer` / `MarkdownRenderer` sob demanda:
    ```tsx
    const MarkdownRenderer = dynamic(
      () => import("@/components/ui/MarkdownRenderer").then((m) => m.MarkdownRenderer),
      { ssr: false, loading: () => <div className="h-24 bg-card animate-pulse rounded-xl" /> }
    );
    ```
  - Carregar `AiConfigModal` sob demanda no `PersistentNav`:
    ```tsx
    const AiConfigModal = dynamic(
      () => import("@/components/config/AiConfigModal").then((m) => m.AiConfigModal),
      { ssr: false }
    );
    ```
  - **Redução Esperada:** Reduzir o tamanho dos chunks das páginas `/workspace`, `/lab` e `/biblioteca` de 6 MB para menos de 400 KB no carregamento inicial.

#### R4. Eliminar `window.location.href` e Corrigir Mismatch de Rotas
- **Alvo:** `dashboard/page.tsx`, `calendar/page.tsx`, `repetition/page.tsx`.
- **Ação:**
  - Substituir todas as chamadas de `window.location.href = ...` por `router.push(...)`.
  - Corrigir os parâmetros de rota em `calendar/page.tsx` (`currentPath="/calendar"`) e `repetition/page.tsx` (`currentPath="/repetition"`).

---

## 5. Método de Verificação Independente (Verification Method)

Para validar e auditar de forma independente as constatações deste relatório:

1. **Inspeção de Server vs Client Components:**
   ```bash
   grep -rn '^"use client"' frontend/src/app/
   ```
   *Critério de validação:* Confirmar que todas as 7 rotas retornam `"use client"` na linha 1.

2. **Auditoria de `PersistentNav` Fora do Layout:**
   ```bash
   grep -rn "PersistentNav" frontend/src/app/
   ```
   *Critério de validação:* Confirmar que `layout.tsx` não contém `PersistentNav` e que todas as 7 rotas o instanciam manualmente.

3. **Auditoria de Ausência de `loading.tsx`:**
   ```bash
   find frontend/src/app -name "loading.tsx" -o -name "loading.js"
   ```
   *Critério de validação:* O comando retorna vazio (código de saída 0, 0 linhas).

4. **Auditoria de Ausência de `next/dynamic`:**
   ```bash
   grep -rn "next/dynamic" frontend/src/
   ```
   *Critério de validação:* O comando retorna vazio (código de saída 1).

5. **Auditoria de Hard Reloads via `window.location.href`:**
   ```bash
   grep -rn "window.location.href" frontend/src/app/ frontend/src/components/
   ```
   *Critério de validação:* Confirmar ocorrências em `dashboard/page.tsx`, `calendar/page.tsx` e `StudyCalendar.tsx`.

6. **Auditoria de Tamanho dos Chunks de Rota:**
   ```bash
   ls -lh frontend/.next/static/chunks/app/*/*.js
   ```
   *Critério de validação:* Verificar que os chunks de `workspace`, `lab` e `biblioteca` excedem 5 MB cada.
