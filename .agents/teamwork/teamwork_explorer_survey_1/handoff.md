# Relatório de Investigação: Arquitetura de Navegação Frontend & PersistentNav

## 1. Observation (Observações Diretas)

### 1.1 `PersistentNav` Não é Persistente (Ausência de Layout Compartilhado)
- **Arquivo de Layout Raiz**: `frontend/src/app/layout.tsx` (linhas 9-20).
  ```tsx
  export default function RootLayout({ children }: { children: React.ReactNode }) {
    return (
      <html lang="pt-BR" className="dark">
        <body className="min-h-screen bg-background text-foreground antialiased font-sans selection:bg-primary/20 selection:text-primary">
          {children}
        </body>
      </html>
    );
  }
  ```
  `PersistentNav` **NÃO está presente** no layout raiz nem em nenhum layout aninhado (não existe nenhum outro arquivo `layout.tsx` em `frontend/src/app/`).
- **Instanciações Repetidas**: `PersistentNav` é importado e renderizado manualmente dentro de cada página individual, totalizando 11 instâncias:
  1. `frontend/src/components/workspace/WorkspaceLayout.tsx:83`: `{!isZenMode && <PersistentNav currentPath="/workspace" />}`
  2. `frontend/src/app/dashboard/page.tsx:103`: `<PersistentNav currentPath="/" onNavigate={(path) => console.log("Nav to", path)} />`
  3. `frontend/src/app/calendar/page.tsx:71`: `<PersistentNav currentPath="/calendario" />`
  4. `frontend/src/app/biblioteca/page.tsx:173`: `<PersistentNav currentPath="/biblioteca" />`
  5. `frontend/src/app/trilhas/page.tsx:48`: `<PersistentNav currentPath="/trilhas" />`
  6. `frontend/src/app/trilhas/[slug]/page.tsx:158`: `<PersistentNav currentPath="/trilhas" />`
  7. `frontend/src/app/whiteboard/page.tsx:56`: `<PersistentNav currentPath="/whiteboard" />`
  8. `frontend/src/app/whiteboard/page.tsx:140`: `<PersistentNav currentPath="/whiteboard" />` (dentro de `Suspense fallback`)
  9. `frontend/src/app/repetition/page.tsx:113`: `<PersistentNav currentPath="/revisao" />`
  10. `frontend/src/app/lab/page.tsx:188`: `<PersistentNav currentPath="/lab" />`
  11. `frontend/src/app/lab/page.tsx:530`: `<PersistentNav currentPath="/lab" />` (dentro de `Suspense fallback`)

### 1.2 Ausência de Feedback Visual ao Clique (<100ms) no `PersistentNav`
- **Arquivo**: `frontend/src/components/navigation/PersistentNav.tsx` (linhas 66-89):
  ```tsx
  {navItems.map((item) => {
    const Icon = item.icon;
    const isActive =
      item.path === "/"
        ? activePath === "/" || activePath === "/dashboard"
        : activePath.startsWith(item.path);

    return (
      <Link
        key={item.path}
        href={item.path}
        onClick={() => onNavigate?.(item.path)}
        className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all ${
          isActive
            ? "bg-primary text-primary-foreground shadow-sm"
            : "text-muted-foreground hover:text-foreground hover:bg-secondary"
        }`}
        aria-current={isActive ? "page" : undefined}
      >
        <Icon className="w-4 h-4 shrink-0" aria-hidden="true" />
        <span>{item.label}</span>
      </Link>
    );
  })}
  ```
- **Comportamento observado**:
  - `activePath` é derivado estritamente de `currentPath || pathname || "/"`.
  - Ao clicar no link, não existe estado de `isPending` ou `pendingPath`. O evento `onClick` apenas dispara `onNavigate?.(item.path)`, que na maioria das telas é `undefined` (e no Dashboard é apenas um `console.log`).
  - No Next.js App Router, a rota e o `pathname` só mudam após a conclusão da resolução e montagem da nova página. Durante todo o tempo de carregamento da página destino, o link clicado não altera de cor, não exibe spinner e não dá nenhum sinal visual de clique.
  - Para o usuário, a interface parece inoperante ou travada durante esse intervalo.

### 1.3 Ausência Total de `loading.tsx` e de Indicador de Progresso Global
- O comando `find frontend/src/app -name "loading.*"` retornou **vazio** (zero arquivos). Não há limites de loading declarativos no App Router.
- Não há nenhum componente de barra de progresso no topo da tela (ex: `nextjs-toploader` ou `nprogress`).
- Quando uma transição de página ocorre, o Next.js mantém a visualização anterior parada (freeze) até que o chunk da nova página esteja pronto.

### 1.4 Navegações Destrutivas com Hard Reload via `window.location.href`
Foram identificados múltiplos botões de ação e navegação primária contornando o roteador SPA do Next.js e forçando recarga completa do navegador:
1. `frontend/src/app/dashboard/page.tsx:97` (Hero Card CTA "Continuar Lição"):
   ```tsx
   const handleResume = () => {
     if (typeof window !== "undefined") {
       window.location.href = "/workspace";
     }
   };
   ```
2. `frontend/src/app/dashboard/page.tsx:123` (Banner Diagnóstico):
   ```tsx
   onClick={() => (window.location.href = "/onboarding")}
   ```
3. `frontend/src/app/dashboard/page.tsx:158` (Carrossel de Trilhas):
   ```tsx
   onSelectTrack={(id) => (window.location.href = `/trilhas/${id}`)}
   ```
4. `frontend/src/app/calendar/page.tsx:109` (Modal de Detalhe da Tarefa):
   ```tsx
   onNavigateAction={(url) => (window.location.href = url)}
   ```
5. `frontend/src/app/trilhas/page.tsx:70`:
   ```tsx
   onSelectTrack={(id) => (window.location.href = `/trilhas/${id}`)}
   ```
6. `frontend/src/app/onboarding/page.tsx:36`:
   ```tsx
   window.location.href = "/calendar";
   ```

### 1.5 Links de Breadcrumb Utilizando Tags HTML Nativas `<a>`
- **Arquivo**: `frontend/src/components/navigation/Breadcrumbs.tsx`:
  - Linhas 19-25:
    ```tsx
    <a href="/" aria-label="Ir para a página inicial" className="...">
      <Home className="w-3.5 h-3.5" />
    </a>
    ```
  - Linhas 35-40:
    ```tsx
    <a href={item.href} className="...">
      {item.label}
    </a>
    ```
  - Cada clique no ícone "Home" ou em qualquer nível da navegação estrutural força uma requisição HTTP tradicional de página inteira (`GET /`), destruindo o estado da aplicação e recarregando todos os assets.

### 1.6 Desincronização de Rotas e Quebra do Indicador Ativo no `PersistentNav`
- Em `frontend/src/app/repetition/page.tsx:113`:
  ```tsx
  <PersistentNav currentPath="/revisao" />
  ```
  No `PersistentNav.tsx`, o item de navegação possui `path: "/repetition"`.
  A condição `activePath.startsWith(item.path)` avalia `"/revisao".startsWith("/repetition")`, que retorna **`false`**.
  **Resultado**: Na página de Repetição Espaçada (`/repetition`), nenhum item da navegação fica destacado como ativo.
- Em `frontend/src/app/calendar/page.tsx:71`:
  ```tsx
  <PersistentNav currentPath="/calendario" />
  ```
  Passa a URL legada de redirecionamento (`/calendario`) em vez da rota canônica (`/calendar`).

### 1.7 Requisições Redundantes de Autenticação a Cada Troca de Página
- **Arquivo**: `frontend/src/hooks/useAuth.ts` (linhas 15-45) chamado em `PersistentNav.tsx:34`:
  ```tsx
  const { user, isAuthenticated, logout } = useAuth();
  ```
  No `useAuth.ts`:
  ```tsx
  useEffect(() => {
    ...
    if (storedToken && storedUser) {
      authService.me(storedToken).then((res) => { ... });
    }
  }, []);
  ```
  Como o `PersistentNav` é desmontado e montado do zero a cada navegação de página, o hook `useAuth()` executa seu `useEffect` em **toda e qualquer mudança de rota**, disparando requisições assíncronas repetitivas para `/api/auth/me`.

### 1.8 Tamanhos de Bundle dos Clientes e Execução On-Demand
- Verificação executada via `next build`:
  - Shared First Load JS: **`88.7 kB`**
  - `/workspace`: **`270 kB`** (First Load JS)
  - `/lab`: **`258 kB`** (First Load JS)
  - `/biblioteca`: **`247 kB`** (First Load JS)
  - `/whiteboard`: **`123 kB`** (First Load JS)
  - `/calendar`: **`113 kB`** (First Load JS)
  - `/repetition`: **`112 kB`** (First Load JS)
- No ambiente de desenvolvimento (`next dev`), o prefetch de tags `<Link>` é desativado por especificação do Next.js. Ao clicar em páginas com mais de 250 kB de bundle (`/workspace`, `/lab`, `/biblioteca`), o compilador aciona a compilação de chunks e avaliação de módulos do lado do cliente on-demand (incluindo KaTeX, ReactMarkdown, GraphCanvas, etc.), gerando latência percebida de 1.0 a 3.5 segundos.

---

## 2. Logic Chain (Cadeia de Raciocínio Lógico)

1. **Premissa 1**: Um usuário julga uma interface como lenta, travada ou com botão inoperante quando uma ação de clique leva mais de 100ms para produzir qualquer alteração visual (Princípio de Usabilidade de Nielsen / Human Interface Guidelines).
2. **Premissa 2 (Baseada em 1.2 e 1.3)**: Ao clicar em qualquer link da barra lateral (`PersistentNav`), a aplicação não possui `pendingPath`, não possui `loading.tsx` e não possui barra de progresso no topo. Como o Next.js App Router adia a atualização de `pathname` até que o chunk da nova rota esteja preparado, o botão clicado permanece com a cor e estado idênticos aos de repouso por até vários segundos.
3. **Premissa 3 (Baseada em 1.1 e 1.7)**: Ao invés de o `PersistentNav` persistir na tela via `layout.tsx`, ele é destruído e recriado pelo React a cada troca de rota. Isso impede que qualquer animação contínua ou estado transitório seja preservado, força o navegador a remontar a árvore de 8 ícones SVG e containers do zero, e causa uma nova validação de rede (`authService.me`) a cada salto entre abas.
4. **Premissa 4 (Baseada em 1.4 e 1.5)**: Ações chave de entrada como "Continuar Lição" no Hero Card do Dashboard (`handleResume`), clique em tarefas do calendário e navegações em breadcrumbs executam `window.location.href = ...` ou tags `<a href="...">`. Isso invalida todo o modelo SPA do Next.js, dispara um hard refresh completo do browser com tela branca momentânea e re-download de todo o pacote JavaScript.
5. **Premissa 5 (Baseada em 1.6)**: A desincronização de propriedades (`currentPath="/revisao"` em vez de `"/repetition"`) impede que o usuário veja a aba ativa, aumentando a desorientação e a percepção de instabilidade no sistema.
6. **Premissa 6 (Baseada em 1.8)**: O acoplamento estático de dependências pesadas (`rehype-katex`, `katex`, `react-markdown`, `mermaid`, `GraphLabWorkspace`) eleva o peso dos clientes para até 270 kB por página, maximizando o tempo que o React Concurrent Mode leva para comutar o componente sob transição.
7. **Conclusão Lógica**: A sensação de lentidão e falta de resposta na navegação entre as páginas (`/`, `/workspace`, `/whiteboard`, `/lab`, `/biblioteca`, `/repetition`, `/calendar`) não decorre de problemas de rede do backend nas rotas em si, mas sim de uma arquitetura frontend que:
   - Não utiliza layout compartilhado para navegação;
   - Não fornece feedback otimista instantâneo ao clique (<100ms);
   - Mistura roteamento SPA com `window.location.href` e tags `<a>`;
   - Não implementa `loading.tsx` nem barra de progresso de transição;
   - Passa strings de rotas divergentes que quebram o destaque visual.

---

## 3. Caveats (Ressalvas)

1. **Escopo do Explorer**: Esta investigação focou estritamente na camada frontend e na arquitetura de navegação (`PersistentNav`, roteamento Next.js, layout, bundle sizes e ciclo de vida de componentes).
2. **Ambiente de Desenvolvimento vs Produção**: O comportamento sem prefetching em `next dev` amplifica o problema da ausência de feedback de clique, mas a falta de feedback instantâneo e o uso de `window.location.href` afetam tanto o ambiente de desenvolvimento quanto o de produção.
3. **Exceções de Telas Específicas**: Telas como `/login` e `/onboarding` não devem conter a barra de navegação principal, e o modo `/workspace` possui o estado Zen Mode (`isZenMode`) que esconde a barra. A arquitetura de layout proposta deve respeitar essas condições via contexto ou Route Groups.

---

## 4. Conclusion & Actionable Recommendations (Conclusão e Recomendações)

A raiz do problema de responsividade na navegação está plenamente identificada e detalhada.
Abaixo estão as 7 ações de remediação recomendadas para o plano técnico do `Planejador` e implementação pelo `Front_End`:

### R1. Implementar Layout Compartilhado Real com `PersistentNav`
- **Alvo**: `frontend/src/app/layout.tsx` (ou Route Group `(app)/layout.tsx`).
- **Ação**: Montar o `PersistentNav` no layout compartilhado, envolvendo o container `<main>{children}</main>`.
- **Benefício**: O `PersistentNav` é montado uma única vez. Não é mais destruído e recriado a cada transição de rota. O `useAuth()` valida a sessão uma única vez e elimina as chamadas redundantes a `/api/auth/me`.

### R2. Adicionar Feedback Visual Imediato ao Clique (<50ms) no `PersistentNav`
- **Alvo**: `frontend/src/components/navigation/PersistentNav.tsx`.
- **Ação**:
  1. Introduzir estado otimista `const [pendingPath, setPendingPath] = useState<string | null>(null)`.
  2. Limpar `pendingPath` em um `useEffect` quando o `pathname` mudar.
  3. No clique do `<Link>`, disparar `setPendingPath(item.path)` imediatamente.
  4. Se `pendingPath === item.path`, aplicar imediatamente o estilo ativo ou exibir um indicador de carregamento discreto (`<Loader2 className="w-4 h-4 animate-spin text-primary shrink-0" />`).
  5. Adicionar `prefetch={true}` nos `<Link>` de navegação principal para acelerar rotas em produção.

### R3. Adicionar Barra de Progresso Global de Roteamento
- **Alvo**: `frontend/src/app/layout.tsx`.
- **Ação**: Integrar um componente de barra de progresso no topo da viewport (ex: `nextjs-toploader` ou barra CSS acionada por eventos de transição de rota).
- **Benefício**: Qualquer navegação na aplicação (barra lateral, links internos, botões) gera feedback imediato na borda superior da tela em <50ms.

### R4. Eliminar Todos os `window.location.href` e Substituir por `router.push` / `<Link>`
- **Alvos**:
  - `frontend/src/app/dashboard/page.tsx:97`: Substituir `window.location.href = "/workspace"` por `router.push("/workspace")` ou envolver o botão em `<Link href="/workspace">`.
  - `frontend/src/app/dashboard/page.tsx:123`: Substituir por `router.push("/onboarding")` ou `<Link>`.
  - `frontend/src/app/dashboard/page.tsx:158` e `frontend/src/app/trilhas/page.tsx:70`: Substituir por `router.push(`/trilhas/${id}`)` ou `<Link>`.
  - `frontend/src/app/calendar/page.tsx:109`: Substituir por `router.push(url)` ou `<Link>`.
  - `frontend/src/app/onboarding/page.tsx:36`: Substituir por `router.push("/calendar")`.

### R5. Corrigir Tags `<a>` em `Breadcrumbs.tsx`
- **Alvo**: `frontend/src/components/navigation/Breadcrumbs.tsx`.
- **Ação**: Substituir as tags `<a href="...">` das linhas 19 e 35 pelo componente `<Link href="...">` do `next/link`.

### R6. Corrigir as Rotas Desincronizadas no `PersistentNav`
- **Alvos**:
  - `frontend/src/app/repetition/page.tsx:113`: Corrigir `currentPath="/revisao"` para `"/repetition"` (ou remover a propriedade e deixar o `usePathname()` gerenciar automaticamente).
  - `frontend/src/app/calendar/page.tsx:71`: Corrigir `currentPath="/calendario"` para `"/calendar"`.

### R7. Implementar `loading.tsx` Declarativos no App Router
- **Alvos**: Criar `frontend/src/app/loading.tsx` e skeletons de transição usando o componente existente `frontend/src/components/ui/Skeleton.tsx`.
- **Benefício**: Elimina a tela congelada durante a busca de dados e montagem de componentes complexos.

---

## 5. Verification Method (Método de Verificação Independente)

Para verificar e validar as constatações reportadas de forma autônoma e reproduzível:

1. **Inspeção de Instâncias do PersistentNav**:
   ```bash
   grep -rn "PersistentNav" frontend/src
   ```
   *Condição de falha*: O componente deve constar em 11 locais diferentes, confirmando que não há persistência por layout.

2. **Detecção de Hard Reloads via `window.location.href`**:
   ```bash
   grep -rn "window.location.href" frontend/src
   ```
   *Condição de falha*: Identificar ocorrências no `dashboard`, `calendar`, `trilhas` e `onboarding`.

3. **Detecção de Tags `<a>` Internas em Breadcrumbs**:
   ```bash
   grep -P -rn "<a\b" frontend/src/components/navigation/Breadcrumbs.tsx
   ```
   *Condição de falha*: Linhas 19 e 35 contêm tags `<a href="...">` nativas para rotas internas.

4. **Verificação de Ausência de `loading.tsx`**:
   ```bash
   find frontend/src/app -name "loading.*"
   ```
   *Resultado esperado*: Saída vazia (0 arquivos).

5. **Verificação de Quebra do Indicador Ativo**:
   Inspeção das linhas 113 de `frontend/src/app/repetition/page.tsx` (`currentPath="/revisao"`) vs `frontend/src/components/navigation/PersistentNav.tsx:43` (`path: "/repetition"`).
   Avaliação lógica: `"/revisao".startsWith("/repetition") === false`.

6. **Medição de Bundle e Compilação**:
   ```bash
   cd frontend && npm run build
   ```
   Confirmar que as rotas `/workspace`, `/lab` e `/biblioteca` possuem bundles First Load JS de 247 kB a 270 kB.
