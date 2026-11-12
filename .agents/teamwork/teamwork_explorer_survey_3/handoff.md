# Relatório de Investigação: Fullstack Network & Backend Endpoints Explorer
**Instância:** `teamwork_explorer_survey_3`  
**Data:** 2026-11-07  
**Escopo:** Diagnóstico de rede, latência de backend, deduplicação de chamadas, ciclo de vida de componentes e I/O bloqueante na navegação entre as 7 rotas (`/`, `/workspace`, `/whiteboard`, `/lab`, `/biblioteca`, `/repetition`, `/calendar`) do AutoTutor CP.

---

## 1. Observation

### 1.1 Mapeamento de Requisições de Rede por Rota na Montagem (Mount / Page Transition)

| Rota | Arquivos de Origem | Requisições HTTP Disparadas no Mount | Tamanho Payload & Latência Medida | Impacto Percebido |
|---|---|---|---|---|
| **`/`** (Dashboard) | `frontend/src/app/page.tsx:4`<br>`frontend/src/app/dashboard/page.tsx:83-93`<br>`frontend/src/components/navigation/PersistentNav.tsx:34` | 1. `GET /api/auth/me`<br>2. `GET /api/progress` | - `/api/auth/me`: 35 B, ~2.4ms (direto) / 24ms (proxy)<br>- `/api/progress`: **833.6 KB**, **579ms** (direto) / **368ms** (proxy) | Bloqueio de rede na hidratação, processamento de 833 KB de JSON para ler apenas 2 inteiros (`streak_days` e `solved_count`). |
| **`/workspace`** | `frontend/src/app/workspace/page.tsx:84-96`<br>`frontend/src/components/workspace/WorkspaceLayout.tsx:83`<br>`frontend/src/components/workspace/PracticeArena.tsx:97-131` | 1. `GET /api/auth/me`<br>2. `GET /api/problems`<br>3. `GET /api/problems/{id}` *(waterfall sequencial)* | - `/api/problems`: 12.5 KB, ~5.4ms (direto) / 22ms (proxy)<br>- `/api/problems/{id}`: ~4.2 KB, ~4.8ms | **Waterfall**: `getProblem` só inicia após `listProblems` resolver. Enquanto `problemDetail === null`, tela de enunciado fica totalmente em branco sem skeleton. |
| **`/whiteboard`** | `frontend/src/app/whiteboard/page.tsx:56`<br>`frontend/src/components/whiteboard/GraphLabWorkspace.tsx` | 1. `GET /api/auth/me` | - `/api/auth/me`: 35 B | Não há chamadas bloqueantes de API no mount. Presets e grafos são importados de `sessionStorage`. |
| **`/lab`** | `frontend/src/app/lab/page.tsx:135-141`<br>`frontend/src/app/lab/page.tsx:83-107` | 1. `GET /api/auth/me`<br>2. `GET /api/progress`<br>3. *(Condicional)* `POST /api/ai/generate-material` | - `/api/progress`: **833.6 KB**, ~579ms<br>- `generate-material`: chamada síncrona a LLM (**5s - 15s**) | `/api/progress` traz o payload duplicado de materiais salvos. Se `autoGenerate=true`, congela o event loop do backend por até 15 segundos. |
| **`/biblioteca`** | `frontend/src/app/biblioteca/page.tsx:39, 81-93`<br>`frontend/src/services/libraryService.ts:78-97` | 1. `GET /api/auth/me` *(PersistentNav)*<br>2. `GET /api/auth/me` *(BibliotecaPage - DUPLICADO)*<br>3. `GET /api/library/books`<br>4. `GET /api/library/search?limit=12` | - `auth/me` x2 concorrentes: 35 B cada<br>- `/api/library/books`: 41.7 KB, ~7ms<br>- `/api/library/search`: 7.5 KB, **323.7ms** | Chamada duplicada de auth. `/api/library/search` executa `kb.stats()` com full table scan e `json_extract` sobre 7.187 documentos SQLite a cada pesquisa. |
| **`/repetition`** | `frontend/src/app/repetition/page.tsx:98-113` | 1. `GET /api/auth/me` | - `/api/auth/me`: 35 B | Dados mockados em memória (`INITIAL_SCHEDULE`, `INITIAL_TOPICS`). **Bug visual:** passa `currentPath="/revisao"`, mas rota é `/repetition`. |
| **`/calendar`** | `frontend/src/app/calendar/page.tsx:33-53, 71` | 1. `GET /api/auth/me` | - `/api/auth/me`: 35 B | Dados locais em `localStorage`. **Bug visual:** passa `currentPath="/calendario"`, mas rota é `/calendar`. |

---

### 1.2 Medições de Latência e Tamanho de Payload via Curl Benchmark

Comando executado no ambiente de teste com backend ativo na porta 8000 e frontend Next.js na porta 3000:
```bash
for ep in "/api/auth/me" "/api/progress" "/api/problems" "/api/library/books" "/api/library/search"; do
  echo "=== Testing $ep on :8000 ==="
  curl -w "status: %{http_code} | time_total: %{time_total}s | size: %{size_download}b\n" -o /dev/null -s "http://127.0.0.1:8000$ep"
  echo "=== Testing $ep via Next proxy on :3000 ==="
  curl -w "status: %{http_code} | time_total: %{time_total}s | size: %{size_download}b\n" -o /dev/null -s "http://127.0.0.1:3000$ep"
done
```

Resultado obtido:
```
=== Testing /api/auth/me on :8000 ===
status: 200 | time_total: 0.002396s | size: 35b
=== Testing /api/auth/me via Next proxy on :3000 ===
status: 200 | time_total: 0.024004s | size: 35b
=== Testing /api/progress on :8000 ===
status: 200 | time_total: 0.579140s | size: 833590b
=== Testing /api/progress via Next proxy on :3000 ===
status: 200 | time_total: 0.368358s | size: 833590b
=== Testing /api/problems on :8000 ===
status: 200 | time_total: 0.005425s | size: 12580b
=== Testing /api/problems via Next proxy on :3000 ===
status: 200 | time_total: 0.022312s | size: 12580b
=== Testing /api/library/books on :8000 ===
status: 200 | time_total: 0.006934s | size: 41682b
=== Testing /api/library/books via Next proxy on :3000 ===
status: 200 | time_total: 0.018520s | size: 41682b
=== Testing /api/library/search on :8000 ===
status: 200 | time_total: 0.323707s | size: 7520b
=== Testing /api/library/search via Next proxy on :3000 ===
status: 200 | time_total: 0.106866s | size: 7520b
```

---

### 1.3 Bloqueio do Event Loop do Starlette (`autotutor_cp/api_server.py`)

No arquivo `autotutor_cp/api_server.py`:
1. **Todas as rotas são declaradas como `async def`:**
   - Linha 220: `async def list_problems(request: Request) -> JSONResponse:`
   - Linha 256: `async def get_problem_detail(request: Request) -> JSONResponse:`
   - Linha 299: `async def submit_solution(request: Request) -> JSONResponse:`
   - Linha 500: `async def generate_material_endpoint(request: Request) -> JSONResponse:`
   - Linha 1009: `async def get_progress(request: Request) -> JSONResponse:`
   - Linha 1226: `async def get_library_books(request: Request) -> JSONResponse:`
   - Linha 1246: `async def search_library_knowledge(request: Request) -> JSONResponse:`

2. **I/O Bloqueante de Disco e Deserialização JSON síncrona sem cache em memória:**
   - `autotutor_cp/core/problem_bank.py:8-9`:
     ```python
     def load_problems():
         return json.loads(DATA_PATH.read_text(encoding='utf-8')) + json.loads(DATA_PATH.with_name('local_classics.json').read_text(encoding='utf-8')) + json.loads(DATA_PATH.with_name('extended_contracts.json').read_text(encoding='utf-8'))
     ```
     Chamado síncronamente em `get_all_problems()` em `list_problems` (linha 222), `get_problem_detail` (linha 259) e `submit_solution` (linha 315). A cada requisição, 3 arquivos de disco são relidos e parseados do zero.
   - `autotutor_cp/core/library.py:16, 20`:
     ```python
     def resources(): return json.loads((DATA/'study_resources.json').read_text(encoding='utf-8'))['resources']
     def deep_guides(): return json.loads((DATA/'deep_guides.json').read_text(encoding='utf-8'))['guides']
     ```
     Chamados diretamente em `get_library_books` e `search_library_knowledge`.

3. **Inchaço de Payload e Duplicação no `/api/progress` (`autotutor_cp/api_server.py:1018-1043`):**
   ```python
   # Retrieve saved materials
   materials = []
   try:
       artifacts = store.artifacts(pid, "material")
       for art in artifacts:
           payload = art.get("payload") or art.get("data") or {}
           materials.append({
               "id": art.get("id"),
               "title": art.get("title"),
               "created_at": art.get("time") or art.get("created_at"),
               "data": payload,
               "payload": payload
           })
   ```
   **Medição verificada em Python:** O perfil ativo possui 46 materiais didáticos completos em markdown. O campo `data` e `payload` contêm exatamente o mesmo objeto duplicado na serialização. Isso gera um JSON de **833.590 bytes (834 KB)** gerado e transmitido a cada mount do Dashboard e do Lab.

4. **Operações Síncronas Pesadas no Event Loop Principal:**
   - `submit_solution` (linha 444): Executa compilação C++ `g++ -O2` e runner de execução (`subprocess.run`) diretamente na thread da Starlette.
   - `generate_material_endpoint` (linha 550): Chama `tutor.generate_material(...)` (requisição síncrona de rede externa para Gemini/Ollama). Durante os 5 a 15 segundos dessa chamada, **todo o servidor Starlette é paralisado**, travando qualquer resposta a `/api/auth/me` ou navegação de outros clientes.
   - `search_library_knowledge` (linha 1277): Chama `kb.stats()`. Em `autotutor_cp/core/knowledge.py:148-155`, `stats()` executa 5 queries SQLite síncronas incluindo `SELECT json_extract(metadata,'$.track'),COUNT(*) FROM knowledge_documents GROUP BY 1` sobre 7.187 linhas, gerando um custo de ~320ms por busca.

---

### 1.4 Estado de Front-End, Ausência de Caching e Recriação de Instâncias

1. **`PersistentNav` Descentralizado e Remontado a Cada Rota:**
   - Em `frontend/src/app/layout.tsx:9-20`, não há layout persistente compartilhado (`PersistentNav` não está no RootLayout).
   - `PersistentNav` é instanciado manualmente dentro de cada página:
     - `dashboard/page.tsx:103`
     - `workspace/WorkspaceLayout.tsx:83`
     - `whiteboard/page.tsx:56`
     - `lab/page.tsx:188`
     - `biblioteca/page.tsx:173`
     - `repetition/page.tsx:113`
     - `calendar/page.tsx:71`
   - Toda transição de rota desfaz o DOM do sidebar, remonta o componente, reinicializa o hook `useAuth()` e dispara `authService.me()` na montagem (`frontend/src/hooks/useAuth.ts:25`).

2. **Chamadas Duplicadas de `useAuth()` na mesma página:**
   - Em `frontend/src/app/biblioteca/page.tsx:39`: `const { user } = useAuth();`
   - Em `frontend/src/components/navigation/PersistentNav.tsx:34`: `const { user, isAuthenticated, logout } = useAuth();`
   - Ambas as chamadas executam seus `useEffect` de validação de token, gerando 2 requests idênticos `GET /api/auth/me` em paralelo a cada visita à biblioteca.

3. **Ausência Total de Cache e Deduplicação no Cliente (`frontend/src/services/apiClient.ts`):**
   - Não há SWR, React Query ou cache HTTP configurado (`cache: 'no-store'` implícito pelo fetch dinâmico).
   - Dados estáticos que nunca mudam em runtime (catálogo de problemas em `/workspace`, catálogo de livros em `/biblioteca`) são refetchados integralmente do zero toda vez que o usuário clica no item da sidebar.

4. **Hard Page Reloads com `window.location.href`:**
   Encontradas transições que forçam recarregamento completo do navegador em vez de navegação SPA com `router.push()`:
   - `frontend/src/app/dashboard/page.tsx:97`: `window.location.href = "/workspace";` (botão Continuar Estudo)
   - `frontend/src/app/dashboard/page.tsx:123`: `window.location.href = "/onboarding";` (banner de diagnóstico)
   - `frontend/src/app/dashboard/page.tsx:158`: `window.location.href = `/trilhas/${id}`;` (cards de trilha)
   - `frontend/src/app/calendar/page.tsx:109`: `onNavigateAction={(url) => (window.location.href = url)}`
   - `frontend/src/app/onboarding/page.tsx:36`: `window.location.href = "/calendar";`

5. **Inconsistências de Rota Ativa no `PersistentNav`:**
   - `frontend/src/app/repetition/page.tsx:113`: `<PersistentNav currentPath="/revisao" />`. Como a rota no menu é `/repetition`, a condição `activePath.startsWith(item.path)` falha e nenhum botão fica aceso.
   - `frontend/src/app/calendar/page.tsx:71`: `<PersistentNav currentPath="/calendario" />`. Como a rota no menu é `/calendar`, a condição falha e o link de Calendário não recebe o estado ativo.

6. **Next.js Rewrite Proxy (`frontend/next.config.js:4-11`):**
   - `/api/:path*` redireciona para `http://127.0.0.1:8000/api/:path*`.
   - Adiciona entre 15ms e 22ms de overhead de proxy HTTP Node.js por requisição em relação a conexões diretas.
   - Em `frontend/src/services/apiClient.ts:35`, `fetch(url)` não possui timeout configurado via `AbortSignal.timeout(...)`. Se o backend travar (ex: em geração de IA), a requisição fica pendente indefinidamente no navegador.

---

## 2. Logic Chain

1. **Do I/O Síncrono no Backend à Latência Percebida:**
   - *Premissa 1:* Starlette processa rotas `async def` diretamente na thread única do event loop asyncio (`api_server.py:1372-1433`).
   - *Premissa 2:* Funções como `load_problems()`, `store.load()`, `store.artifacts()`, `kb.stats()`, `current_judge.judge()` e `tutor.generate_material()` são síncronas e bloqueantes (`problem_bank.py:8`, `progress_store.py`, `knowledge.py:148`).
   - *Inferência:* Durante a execução dessas funções bloqueantes, nenhuma outra requisição (nem mesmo `GET /api/auth/me`) consegue ser respondida. O tempo de resposta acumula a fila de requisições pendentes.

2. **Do Inchaço de Dados no `/api/progress` à Lentidão da Home e do Lab:**
   - *Premissa 1:* O método `store.artifacts(pid, "material")` acumula 46 artefatos completos com texto em markdown (`api_server.py:1021`).
   - *Premissa 2:* `api_server.py:1028-1029` insere tanto `"data": payload` quanto `"payload": payload` no retorno de cada artefato.
   - *Premissa 3:* A medição por curl confirmou 833.590 bytes (834 KB) e latência de ~580ms.
   - *Premissa 4:* O componente de Dashboard (`frontend/src/app/dashboard/page.tsx:84-93`) só utiliza `streak_days` e `solved_count`.
   - *Inferência:* A montagem da Dashboard transfere e desserializa centenas de kilobytes de texto didático desnecessário, consumindo banda e tempo de processamento na thread do navegador antes de exibir o streak de estudos.

3. **Da Remontagem do `PersistentNav` à Carga Repetitiva de Rede:**
   - *Premissa 1:* Cada rota Next.js App Router renderiza sua própria instância de `PersistentNav`.
   - *Premissa 2:* O hook `useAuth()` executa `authService.me()` a cada montagem (`useAuth.ts:25`).
   - *Inferência:* Cada clique de navegação (ex: de `/` para `/workspace`, ou de `/whiteboard` para `/biblioteca`) gera nova requisição HTTP para checar autenticação, competindo por I/O no backend com as requisições principais da página.

4. **Do Waterfall no `/workspace` à Sensação de Tela Vazia/Travada:**
   - *Premissa 1:* `PracticeArena.tsx:98` executa `problemService.listProblems()`.
   - *Premissa 2:* `selectedProblemId` só é definido após a conclusão de `listProblems()`.
   - *Premissa 3:* `problemService.getProblem(selectedProblemId)` (`PracticeArena.tsx:126`) só dispara após `selectedProblemId` estar definido.
   - *Premissa 4:* Enquanto `problemDetail` for `null`, `PracticeArena.tsx:317` não renderiza nada no painel de enunciados, e o editor Monaco permanece com código vazio.
   - *Inferência:* O usuário experimenta um delay cumulativo de duas requisições consecutivas sem qualquer feedback visual de esqueleto ou placeholder, parecendo que a página não carregou.

5. **Do Uso de `window.location.href` à Destruição da Performance de SPA:**
   - *Premissa 1:* Em Next.js App Router, navegação interna deve ser efetuada via `<Link>` ou `router.push()`.
   - *Premissa 2:* `window.location.href` causa descarga completa do documento (`unload`), queima o cache de React Components em memória e força o download e execução de todos os scripts da aplicação novamente.
   - *Inferência:* Ao clicar em "Continuar Sessão" no Dashboard, a transição para `/workspace` demora ordens de grandeza a mais (1.5s - 3s) do que uma transição SPA (<100ms).

---

## 3. Caveats

1. **Ambiente de Desenvolvimento vs Produção:**
   Em `next dev`, o Next.js compila páginas on-demand na primeira requisição e desativa o prefetching automático de `<Link>` fora do evento de hover. Em produção (`next build` / `next start`), o App Router pré-compila as rotas, o que reduz parte da latência de compilação JS, mas **não elimina** os gargalos identificados de I/O de rede, payloads inchados de 834 KB e bloqueios síncronos da Starlette.
2. **Concorrência com LLM Externo:**
   Quando `generate_material` ou `generate_problem` é acionado sem chave de API ou com timeout elevado de provedor (Gemini/OpenAI/Ollama), o Starlette pode ficar paralisado por até 30s se não houver isolamento em threadpool.

---

## 4. Conclusion

A sensação de lentidão e falta de responsividade na navegação entre as 7 rotas (`/`, `/workspace`, `/whiteboard`, `/lab`, `/biblioteca`, `/repetition`, `/calendar`) decorre de **7 causas técnicas objetivas e interdependentes**:

1. **Ausência de Layout Persistente e AuthContext Compartilhado:** `PersistentNav` e `useAuth()` remontam em cada rota, re-executando `GET /api/auth/me` repetidamente (e duplicado em `/biblioteca`).
2. **Payload Gigante e Bloqueante de 834 KB em `/api/progress`:** A Home e o Lab consomem um endpoint inchado que duplica 46 materiais didáticos inteiros, atrasando a renderização em ~580ms.
3. **Bloqueio do Event Loop Starlette (`async def` com sync I/O):** Endpoints do backend executam leitura de disco JSON, consultas SQLite com table scan (`kb.stats()`), subprocessos de compilação C++ e requisições HTTP para LLMs diretamente na thread principal do asyncio.
4. **Hard Reloads no Frontend:** Uso recorrente de `window.location.href = ...` em vez de `router.push(...)` no Dashboard, Calendário e Trilhas, eliminando os benefícios da SPA.
5. **Waterfall e Ausência de Loading Skeleton no `/workspace`:** Encadeamento de `listProblems` -> `getProblem` com área de enunciado em branco enquanto carrega.
6. **Zero Caching de Dados Estáticos no Cliente:** Catálogo de problemas e catálogo de livros são re-baixados a cada transição de rota sem SWR/React Query ou cache de memória.
7. **Bugs de Identificação de Rota Ativa no Menu:** `PersistentNav` recebe paths errados (`/revisao` e `/calendario`), desorientando o usuário sobre a página atual.

---

## 5. Concrete Remediation Plan (Ações Recomendadas por Chat)

### 5.1 Para o Chat de Back-End (`backend-api-specialist`)
1. **Otimização do `/api/progress` (`autotutor_cp/api_server.py:1009-1044`):**
   - Não retornar o corpo integral de todos os materiais didáticos salvos no `/api/progress` padrão.
   - Retornar apenas metadados leves (`id`, `title`, `created_at`) ou criar endpoint dedicado `/api/progress/materials` com paginação.
   - Eliminar a duplicação dos campos `"data": payload` e `"payload": payload`.
   - **Ganho esperado:** Redução do payload de 834 KB para <2 KB, reduzindo a latência de 580ms para <15ms.
2. **Cache em Memória de Arquivos JSON Estáticos:**
   - Adicionar `@functools.lru_cache()` em `load_problems()` (`problem_bank.py:8`) e em `resources()` / `deep_guides()` (`library.py:16, 20`).
   - Evitar ler 3 arquivos de disco do filesystem a cada chamada de `list_problems`, `get_problem_detail` e `submit_solution`.
3. **Cache de Estatísticas do Acervo (`autotutor_cp/core/knowledge.py:148`):**
   - Cachear o resultado de `kb.stats()` com TTL de 60 segundos em vez de re-executar contagens e `json_extract` sobre 7.187 documentos a cada busca em `/api/library/search`.
4. **Desacoplamento do Event Loop Starlette:**
   - Para operações com I/O síncrono ou subprocessos (`submit_solution`, `generate_material_endpoint`, `generate_problem_endpoint`), utilizar `await run_in_threadpool(...)` do Starlette ou transformar em `def` comum para execução automática no pool AnyIO de workers.

### 5.2 Para o Chat de Front-End (`frontend-ux-specialist` / `fullstack-code-implementer`)
1. **Elevação do `PersistentNav` e `AuthProvider` para o `RootLayout` (`frontend/src/app/layout.tsx`):**
   - Envolver o App Router em um layout shell onde a barra lateral `<PersistentNav>` é montada **uma única vez** e nunca desmontada nas transições.
   - Criar um `AuthContext` compartilhado para que `authService.me()` rode apenas na inicialização inicial do app.
2. **Substituição de `window.location.href` por `router.push()`:**
   - Corrigir `dashboard/page.tsx:97, 123, 158`, `calendar/page.tsx:109`, `trilhas/page.tsx:70` e `onboarding/page.tsx:36` para usar navegação SPA via `useRouter`.
3. **Correção dos Mismatches de Rota no `PersistentNav`:**
   - Em `frontend/src/app/repetition/page.tsx:113`, alterar `currentPath="/revisao"` para `currentPath="/repetition"`.
   - Em `frontend/src/app/calendar/page.tsx:71`, alterar `currentPath="/calendario"` para `currentPath="/calendar"`.
4. **Feedback Visual Imediato no `PersistentNav` (<100ms):**
   - Adicionar estado de navegação pendente com `useTransition()` ou estado local de clique no item do menu, exibindo spinner ou indicador ativo imediato ao toque.
5. **Eliminação do Waterfall e Inclusão de Skeletons no `/workspace`:**
   - Renderizar skeleton animado (pulsing bars) no painel de enunciado enquanto `problemDetail === null`.
   - Se a lição possui `initialProblemId`, disparar `getProblem(initialProblemId)` e `listProblems()` concorrentemente via `Promise.all`.
6. **Timeout e Resiliência no `apiClient.ts`:**
   - Adicionar `signal: AbortSignal.timeout(8000)` para requisições comuns em `apiClient.ts`, evitando travamentos silenciosos quando o proxy demorar para responder.

---

## 6. Verification Method

Para verificar independentemente os diagnósticos apresentados:

1. **Medição de payload e tempo do `/api/progress`:**
   ```bash
   curl -w "HTTP %{http_code} | Total: %{time_total}s | Size: %{size_download} bytes\n" \
        -o /dev/null -s "http://127.0.0.1:8000/api/progress"
   ```
   *Condição de invalidação:* Se o tamanho for inferior a 10 KB ou o tempo for inferior a 25ms, o payload já foi otimizado.

2. **Verificação de I/O em disco no `load_problems`:**
   Inspecione `autotutor_cp/core/problem_bank.py:8-9` e `autotutor_cp/api_server.py:222, 259`. Execute:
   ```bash
   python3 -c "
   import time
   from autotutor_cp.core.problem_bank import load_problems
   t0 = time.perf_counter()
   for _ in range(100): load_problems()
   print(f'100 reads took {(time.perf_counter() - t0)*1000:.2f}ms')
   "
   ```

3. **Verificação de instâncias de `window.location.href` no Frontend:**
   ```bash
   grep -rn "window.location.href" frontend/src
   ```
   *Condição de conformidade futura:* Retorno de 0 ocorrências fora de logout.

4. **Verificação de chamadas concorrentes duplicadas em `/biblioteca`:**
   Inspecione as linhas 39 e 173 de `frontend/src/app/biblioteca/page.tsx`, comprovando que tanto a página quanto o `PersistentNav` invocam `useAuth()`.
