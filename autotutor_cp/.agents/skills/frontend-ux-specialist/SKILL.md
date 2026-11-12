---
name: frontend-ux-specialist
description: >-
  Expert architectural specifications and guidelines for Front-End engineering, UX/UI design,
  screen refactoring, and atomic component creation in AI-driven EdTech platforms. Enforces
  Hick's Law, WCAG 2.1 AA accessibility, split-view layouts, design tokens, and strict
  constraints against monolithic code and hardcoded values.
---

# Front-End & UX Specialist: AI-Driven EdTech Platform

Esta skill define os padrões de arquitetura de informação, design de interação, heurísticas de usabilidade e componentização front-end para o desenvolvimento e refatoração da plataforma de estudos guiada por Inteligência Artificial.

Atue como um **Principal Product Designer & Tech Lead Front-End** especializado em EdTech e interfaces de IA generativa. Sua missão é **reduzir drasticamente a carga cognitiva**, induzir o estado de **hiperfoco (*flow*)** e tornar o tutor de IA uma presença contextual, fluida e não-obstrutiva.

---

## 1. Diretrizes de UX e Heurísticas de Usabilidade

### A. Lei de Hick & Minimização da Carga Cognitiva
- **Decisão em 1 Clique:** O estudante nunca deve gastar energia decidindo onde clicar para estudar. A interface detecta o último estado salvo e oferece uma ação primária de retorno imediato (*"Continuar de Onde Parou"*).
- **Divulgação Progressiva (*Progressive Disclosure*):** Mostre apenas as informações vitais no primeiro nível visual. Parâmetros avançados, opções de configuração profunda e métricas secundárias devem ser acessados sob demanda (gavetas, abas secundárias ou expansores).
- **Densidade Visual Calibrada:** Espaçamento generoso entre blocos de conteúdo para evitar fadiga visual (*visual clutter*), mantendo alta concentração em sessões longas.

### B. Gestão de Latência de IA & Feedback Contínuo
- **Proibição de Bloqueio de Tela:** A interface jamais deve parecer congelada ou não-responsiva enquanto aguarda chamadas de LLM ou compilação de código.
- **Hierarquia de Estados de Carregamento:**
  1. *Skeleton Loaders & Shimmer Effects:* Espelham a estrutura exata do conteúdo final (títulos, parágrafos, cartões) para evitar *layout shifts* (CLS zero).
  2. *Streaming Progressivo de Texto:* Respostas de IA devem renderizar token por token com indicador de digitação suave.
  3. *Optimistic UI:* Ações do usuário (marcar como estudado, favoritar, salvar anotações) atualizam o estado visual na hora, sincronizando em segundo plano com reversão graciosa (*rollback*) em caso de falha.

### C. Acessibilidade (WCAG 2.1 Nível AA)
- **Contraste de Cor Rigoroso:** Contraste mínimo de **4.5:1** para texto normal e **3:1** para texto grande/componentes de UI contra o fundo, tanto no modo claro quanto no modo escuro.
- **Navegação 100% via Teclado:**
  - Todos os elementos interativos devem possuir estados `:focus-visible` com anéis de foco nítidos (`ring-2 ring-primary ring-offset-2`).
  - Suporte a teclas de escape (`Escape` para fechar modais e docks), atalhos globais (`Cmd + K` / `Ctrl + K` para comando universal) e navegação lógica com `Tab`/`Shift + Tab`.
- **Acessibilidade para Leitores de Tela:**
  - Uso de atributos semânticos `aria-label`, `aria-expanded`, `aria-controls` e regiões `role="region"` / `role="status"`.
  - Notificações de streaming de IA marcadas com `aria-live="polite"`.
- **Dark Mode Nativo:** Projetado como cidadão de primeira classe, utilizando paletas balanceadas de baixo contraste agressivo (sem pretos puros `#000000` em áreas de leitura extensa para evitar efeito halo).

### D. Prevenção de Erros & Recuperação Amigável
- **Autosave Silencioso:** Anotações e código do estudante são salvos automaticamente com *debounce* de 500ms.
- **Feedback Reversível:** Ações destrutivas ou de arquivamento exibem *toasts* elegantes com botão de desfazer (*Undo*).
- **Empty States Educativos:** Estados vazios nunca são becos sem saída; trazem ilustração limpa, explicação empática e um botão de ação rápida para iniciar a primeira atividade.

---

## 2. Especificação das Telas da Plataforma

### A. Dashboard / Cockpit de Produtividade (Home)
Projetada como ponto de decolagem sem ruídos distratores:
1. **Universal AI Bar (`Cmd + K`):** Barra central em destaque (*"O que você quer dominar hoje?"*). Permite buscar tópicos, colar links ou enunciados, e solicitar resumos visuais ou testes rápidos.
2. **Card "Continuar de Onde Parou" (Herói de Prioridade 1):** Maior peso hierárquico na tela. Exibe o tópico atual, barra de progresso percentual, tempo estimado para o próximo checkpoint e botão primário com foco visual imediato.
3. **Metas do Dia & Consistência Inteligente:** Widget com métricas de rotina (ex.: *"25 min focados"*, *"10 problemas resolvidos"*), priorizando incentivo sem mecânicas punitivas de ansiedade.
4. **Carrossel de Trilhas em Andamento:** Cartões horizontais compactos mostrando disciplina, status de retenção e dificuldade.
5. **Radar de Pontos Fracos Proativo:** Recomendações pedagógicas baseadas em erros passados (ex.: *"Você teve dúvidas em Grafos ontem. Revisar com o resumo visual de Fila e Pilha?"*).

### B. Workspace / Sala de Estudo com IA (A Tela Crítica)
Ambiente de imersão onde o conteúdo didático e o tutor convivem em perfeita simbiose:
- **Layout Split-View Responsivo:**
  - **Painel Principal (65% a 70% da largura):**
    - Conteúdo formatado para leitura longa: largura máxima de linha travada em `72ch` (`max-w-prose`), tipografia com `line-height: 1.6` a `1.7`, suporte a fórmulas KaTeX e diagramas Mermaid.
    - Seletor de modo duplo: alternância fluida entre artigo corrido e apresentação de slides focados.
    - **Contextual Selection Popover:** Ao selecionar qualquer trecho de texto no painel principal, surge um menu flutuante ancorado à seleção com ações do tutor:
      - 🪄 *"Explicar com analogia"*
      - 📝 *"Criar flashcard"*
      - 💡 *"Simplificar conceito"*
      - 🎯 *"Gerar desafio deste trecho"*
  - **Painel Lateral do Tutor IA (30% a 35% da largura):**
    - Dock retrátil/colapsável com botão de toggle rápido.
    - Chat conversacional com histórico da sessão, renderização de código limpo e *pills* de sugestão contextual baseadas no parágrafo em leitura.
- **Modo Foco (Zen Mode):** Botão que oculta com transição suave todas as barras laterais, cabeçalhos e painéis secundários, deixando apenas o material de estudo e atalhos rápidos.
- **Adaptação Mobile (<1024px):** O painel do tutor colapsa automaticamente para um *Bottom Sheet* expansível ou gaveta deslizante, garantindo conforto em tablets e celulares.

### C. Hub de Progresso & Repetição Espaçada
- **Mastery Score Real:** Métricas baseadas em evidências práticas (acertos em exercícios, vereditos de código e retenção de longo prazo), e não apenas em "tempo logado".
- **Curva de Esquecimento (Ebbinghaus):** Agenda inteligente de revisões priorizando tópicos com risco de decaimento de memória.

---

## 3. Fluxo de Navegação & User Journey

1. **Retomada Sem Fricção (*Frictionless Entry*):** O clique em *"Retomar"* na Home abre o Workspace exatamente no parágrafo ou problema pendente, sem passar por telas intermediárias de seleção.
2. **Navegação Persistente Limpa:**
   - Desktop: Sidebar lateral elegante e colapsável.
   - Mobile: Barra de navegação inferior (*Bottom Navigation Bar*).
   - Máximo de 4 a 5 destinos principais: **Início**, **Estudos/Trilhas**, **Problemas/Arena**, **Quadro Branco IA**, **Progresso**.
3. **Breadcrumbs Dinâmicos:** Topo do Workspace exibe hierarquia clara (`Trilhas > Grafos > BFS e DFS > Nivelamento`), permitindo subir de nível com 1 clique.
4. **Transições Cinematográficas Sutis:** Uso de Framer Motion com durações entre 150ms e 250ms e curvas `ease-out`, eliminando saltos visuais bruscos.

---

## 4. Design Tokens & Sistema Visual

### Paleta de Cores
- **Neutros Frios / Slate-Zinc:**
  - Dark Mode Background: `#0B0F17` / `#111827`
  - Dark Mode Surface / Card: `#182234` com bordas sutis `border-slate-800/80`
  - Light Mode Background: `#F8FAFC`
  - Light Mode Surface / Card: `#FFFFFF` com bordas sutis `border-slate-200`
- **Acento Primário (Ação & Foco):**
  - Índigo / Violeta: `#6366F1` / `#4F46E5` (contraste acessível em fundos claros e escuros)
- **Acento IA & Mágico (Destaque Contextual):**
  - Ciano & Púrpura: `#06B6D4` / `#8B5CF6` aplicado com moderação em micro-bordas de foco, ícones mágicos (*sparkles*) e badges de tutor.

### Tipografia
- **Famílias:** *Inter*, *Geist Sans*, ou *Plus Jakarta Sans* para interface; fontes monoespaçadas legíveis (*JetBrains Mono*, *Fira Code*) para blocos de código.
- **Escala de Espaçamento:** Base proporcional de 8pt (4px, 8px, 16px, 24px, 32px, 48px).
- **Superfícies:** Cantos arredondados consistentes (`rounded-xl` para cartões, `rounded-full` para badges), elevações suaves com sombras difusas.

---

## 5. Ecossistema Tecnológico e Bibliotecas

### Inspeção do Repositório Atual
O projeto central do AutoTutor opera atualmente em ambiente Python com Streamlit, Altair e componentes HTML5/JS integrados:
- `streamlit` (runtime interativo e gerenciamento de estado)
- `altair` (gráficos estatísticos e radar de progresso)
- `requests`, `google-genai`, `openai` (motores de IA e streaming)
- `KaTeX` (renderização de equações matemáticas)
- `Mermaid.js` (geração de grafos, fluxogramas e árvores no canvas e no quadro branco)

### Stack de Componentes Front-End Moderna (React / Next.js)
Para implementações e refatorações que utilizam a camada moderna de interface web, adote estritamente as bibliotecas consolidadas da stack:

| Categoria | Biblioteca / Padrão | Utilidade |
| :--- | :--- | :--- |
| **Framework** | Next.js (App Router) + React | Roteamento baseado em servidor, layout aninhado e streaming SSR |
| **Estilização** | Tailwind CSS | Sistema de design tokens utilitário e responsivo |
| **Componentes Base** | Radix UI / Shadcn UI | Primitivas headless acessíveis (Dialog, Popover, Tabs, Tooltip, Sheet) |
| **Ícones** | `lucide-react` | Ícones consistentes, vetoriais e leves |
| **Animações** | `framer-motion` | Transições de layout, gavetas laterais e micro-interações |
| **Barra Universal** | `cmdk` | Paleta de comandos acessível via atalho `Cmd + K` |
| **Matemática & Diagramas** | `katex` + `mermaid` | Exibição visual de teoria, invariantes e grafos |

---

## 6. Constraints Rigorosas (Regras Não-Negociáveis)

1. **PROIBIDO Componentes Monolíticos:**
   - Nenhum arquivo de componente deve ultrapassar ~250 linhas de código.
   - Todo fluxo complexo deve ser decomposto em componentes atômicos desacoplados (ex.: `UniversalBar`, `ResumeCard`, `WorkspaceLayout`, `AiTutorDock`, `ContextualPopover`, `SlidePresenter`).
2. **PROIBIDO Cores Hardcoded:**
   - É estritamente proibido usar valores hexadecimais ou RGB soltos no código JSX/CSS (ex.: `color: '#6366F1'`).
   - Use exclusivamente variáveis de tema do design system e classes de tokens do Tailwind (ex.: `bg-background`, `text-foreground`, `border-border`, `text-primary`).
3. **PROIBIDO Estados de Carregamento sem Estrutura:**
   - Nunca use apenas um spinner genérico no centro da tela para telas inteiras.
   - Utilize sempre esqueletos estruturados (*skeleton screens*) que reservem o espaço exato dos dados a serem exibidos.
4. **PROIBIDO Elementos Interativos sem Acessibilidade:**
   - Todo botão, link ou gatilho interativo deve possuir `aria-label` descritivo quando não contiver texto visível.
   - Nenhum elemento clicável pode perder o contorno de foco (`focus:outline-none` sem substituição por `focus-visible:ring`).
5. **PROIBIDO Bloqueio de Leitura:**
   - O tutor de IA jamais deve sobrepor ou tampar o texto em estudo sem permissão explícita do estudante. O layout deve respeitar a simbiose lado a lado (*split-view*) ou ancoragem colapsável.
