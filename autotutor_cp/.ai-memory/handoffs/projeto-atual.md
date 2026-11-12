# Memória de projeto — AutoTutor Online Judge

> Handoff portátil consolidado da conversa de evolução do projeto. Não contém
> chaves de API, senhas, tokens, código privado de aluno nem soluções de
> referência. Atualizado em 2026-11-05.

## 1. Propósito e público

O AutoTutor é uma plataforma educacional de programação competitiva em
português. O objetivo é ensinar e praticar fundamentos com um juiz local:
simulação e Ad Hoc, soma de prefixos, BFS/DFS, grafos, árvores, programação
dinâmica, estruturas básicas e análise de complexidade.

O usuário pediu uma experiência de juiz online em tema escuro, minimalista,
com estudos salvos, trilhas, biblioteca, diagnóstico de nível, monitoramento
por turma, professores e formação de trios baseada em evidências.

## 2. Decisões de produto confirmadas

- Cada material de IA recebe página própria em **Meus estudos**, pode ser
  anotado, marcado como estudado e usado para criar um problema relacionado.
- A biblioteca guarda materiais, planos, problemas, orientações, feedbacks e
  referências. Conteúdo gerado não inventa referências: links vêm do acervo
  recuperado ou recebem rótulo explícito.
- Problemas externos entram no juiz local apenas com contrato, oráculo e testes
  válidos. Soluções de referência não são expostas.
- O foco atual são fundamentos; Segment Tree e Block-Cut Tree não são o centro
  dos experimentos.
- Diagnóstico, trilhas e avaliações são formativos. Ler ou gerar conteúdo não
  prova domínio.

## 3. Provedores e custo

- Gemini 3.1 Flash-Lite é o padrão experimental. A conta do usuário é gratuita
  e o projeto não seleciona fallback pago nem inicia cobrança.
- Ollama/Llama local é suportado; Qwen, DeepSeek, OpenAI e Gemini possuem
  conectores de API. Incompatibilidades de endpoint são diagnosticadas.
- Não existe teto diário local de chamadas ou tokens. O projeto continua dentro
  da quota gratuita e interrompe tentativas automáticas após 429, 402, chave
  inválida ou indisponibilidade.
- Foram tratados: instrução de desenvolvedor não suportada, modelos exclusivos
  da Interactions API, quota 429, sobrecarga 503 e credencial/saldo DeepSeek.

## 4. RAG, materiais e problemas

- O acervo inclui CSES, USACO Guide, Neps Academy, Maratona UFMG, YouKnowWho
  Academy e TLE Eliminators, com atribuição e metadados.
- RAG recupera trechos e referências; links recomendados não são confundidos
  com evidência textual. Fonte recuperada é tratada como dado, nunca instrução.
- Material aceita pedido livre, tamanho, profundidade, exemplos, exercícios e
  meta de caracteres. O pedido explícito do aluno vence o assunto anterior.
- Estudos verificáveis têm contratos para prefixos, BFS, DP e simulação. Só o
  exemplo automaticamente conferido é publicado; teoria exige revisão humana.
- A geração de problemas exige assunto e competências antes da execução. Há
  testes pequenos, aleatórios, extremos e de custo quando aplicável.

## 5. Avaliação individual, professor e agentes

- Há contas de aluno/professor, turmas e acompanhamento de turma.
- Parecer individual usa estatísticas minimizadas, produz evidência rastreável
  e não é nota automática. Professor aprova, pede revisão ou rejeita com
  comentário qualitativo.
- Simulação local de agentes de estudantes executou 58 verificações e a suíte
  `tests/test_student_agents.py` passou com 9 testes. Ela valida fluxo, não
  substitui avaliação humana da qualidade pedagógica.
- Validação Gemini: prefixos passou; um problema BFS contraditório foi
  corretamente bloqueado; DP e simulação inicialmente falharam por formato e,
  após contrato explícito, retornaram `[5]` e `[4]` no reteste.
- Uma revisão encontrou texto BFS numericamente correto, mas com complexidade
  de memória errada e índices confusos. Checagem numérica não basta para validar
  explicação. Ver `docs/research/validacao_agentes_criterios.md`.

## 6. Memória de longo prazo adicionada nesta conversa

Inspirada em `akitaonrails/ai-memory`, usa `captura → consolidação →
recuperação → handoff`:

1. Atividades, questionários, submissões e diagnósticos pedagógicos produzem
   observações sanitizadas em tempo real. Vereditos (AC, WA, TLE), métricas de
   tempo e diagnósticos são indexados; códigos e soluções são excluídos.
2. Observações geram deterministamente quatro tipos de documentos Markdown por
   perfil em `data/memory/<profile_id>/`:
   - `memoria.md`: diário cronológico de eventos e atividades;
   - `topicos/<slug>.md`: notas de retenção por assunto (materiais, vereditos e
     diagnósticos de dificuldades observadas);
   - `progresso.md`: síntese de competências práticas e retenção global;
   - `handoff.md`: contexto portátil para passagem entre sessões e agentes.
3. SQLite/FTS atua como índice derivado para busca lexical e ranqueamento;
   Markdown é a fonte de verdade legível, exportável e auditável.
4. Recuperação integrada ao RAG: antes de uma geração de material ou problema,
   o RAG funde trechos teóricos com o briefing da AI Memory, instruindo o modelo
   a sanar dificuldades anteriores sem repetir o que já foi assimilado e sem
   atribuir domínio prematuro.
5. Configurações exporta pacote JSON e Markdown com trilha de auditoria.
6. A consolidação e o recall são 100% locais e determinísticos, sem chamadas
   de IA em segundo plano e com custo financeiro zero.

## 7. Atualização de 2026-11-06 — Implementação e avaliação experimental

- **Decisão tomada:** Conectar formalmente a AI Memory de Akita ao pipeline RAG
  e incorporar scaffolding pedagógico com nivelamento prévio de pré-requisitos:
  - *Guia Pedagógico de Pré-Requisitos:* Ao gerar estudos ou problemas sobre tópicos
    avançados (como BFS/DFS, Dijkstra, Programação Dinâmica, Segment Tree), o sistema
    detecta automaticamente as estruturas e conceitos fundamentais necessários (ex.:
    Fila FIFO e Pilha LIFO para BFS/DFS; Min-Heap para Dijkstra; recursão e tabela de
    estados para DP; divisão e conquista em intervalos para SegTree). O usuário é
    perguntado interativamente se já domina esses conceitos prévios:
    * Se "Sim, já domino!": o gerador avança diretamente para o algoritmo avançado,
      invariantes, árvore de busca e armadilhas de maratona, sem gastar tempo com definições
      triviais;
    * Se "Não / Quero revisar": o gerador inclui obrigatoriamente uma seção de nivelamento
      (`# 0. Fundamentos e Pré-Requisitos`) com intuição visual, diagramas Mermaid
      (comparando FIFO vs LIFO), operações principais em O(1) e sintaxe C++, fazendo
      uma transição suave para o tópico principal.
    * No juiz e Arena de problemas, um componente expansor permite consultar o resumo
      didático desses pré-requisitos a qualquer momento durante a resolução.
  - *Quadro Branco IA (Whiteboard Interativo):* Módulo completo implementado em
    `core/whiteboard_engine.py` e `core/whiteboard_views.py`, permitindo desenhar grafos,
    árvores, tabelas de DP e somas de prefixos com canvas HTML5 interativo, geração de
    diagramas conceituais via IA/Mermaid, presets didáticos prontos, análise estrutural
    e salvamento como artefatos no acervo pessoal.
  - *Modo Duplo de Estudos (Artigo Contínuo vs Slides):* Adicionado alternador em
    `core/study_pages.py` para visualizar materiais tanto no formato clássico de artigo
    quanto no formato de apresentação de slides passo a passo, acompanhado de expansão
    curricular de 183 slides estruturados em `data/learning_content.json` cobrindo todos os
    9 tópicos de maratona com pelo menos 20 slides cada.
  - *Blindagem Anti-Spoilers em Questões Adaptativas:* O enunciado de exercícios (`statement`)
    foi estritamente blindado contra vazamento de respostas, técnicas, nomes de algoritmos
    (ex.: BFS, DFS, Dijkstra, DP), estruturas de dados e seções indevidas geradas por modelos
    (como "Teoria", "Dica" ou "Como resolver"). Foi implementada a função `sanitize_statement()`
    em `core/autocode_engine.py` e em `app.py` que expurga sistematicamente quaisquer seções
    de spoiler, garantindo que o enunciado contenha exclusivamente narrativa, Entrada, Saída
    e Restrições. Recursos didáticos e pré-requisitos foram movidos para a aba `Tutor & dicas`.
  - *Persistência e Desaparecimento de Nivelamento Inicial:* Atendendo à solicitação do usuário,
    os mecanismos de nivelamento inicial servem apenas de diagnóstico no primeiro contato e
    desaparecem da visualização principal após o registro do nível do aluno:
    (1) O teste de diagnóstico inicial de 18 questões (`Diagnóstico`) deixa de ocupar as abas
    principais de estudo (`Área de estudo`) e o card da página inicial assim que o perfil conclui
    a avaliação ou já tem histórico/nível registrado, permanecendo disponível como recurso opcional
    em "Refazer diagnóstico inicial" dentro de Progresso e Minha Trilha.
    (2) O card de pré-requisitos no Laboratório IA (Fila e Pilha para BFS/DFS, etc.) desaparece
    após a primeira resposta do aluno ("Sim, já domino!" ou "Não / Quero revisar"), guardando sua
    preferência e exibindo apenas uma etiqueta discreta com botão de "Alterar", sem interromper as
    gerações subsequentes de materiais ou problemas.
- **Resultados dos testes:**
  - `tests/test_prerequisites.py`: 13 aprovados (100%).
  - `tests/test_whiteboard.py`: 6 aprovados (100%).
  - `tests/test_study_pages.py`: 7 aprovados (100%).
  - Suíte completa: 288 aprovados, 3 pulados, 0 falhas (100% verde).
  (`core/learner_memory.py`, `core/progress_store.py`, `core/codigen_tutor.py` e
  `app.py`), introduzindo tópicos canônicos unificados, páginas por tópico
  (`topicos/<slug>.md`), priorização de diagnósticos no topo dos arquivos e
  expansão lexical de consultas para recuperação direcionada. Adicionado suporte
  a persistência total dos dados de simulação (`--persist-dir`) a pedido do usuário.
  Adicionado ecossistema de livros canônicos em 3 pilares: (1) Ingestão de capítulos
  de livros abertos (Laaksonen, Erickson, Sannemo) no RAG; (2) Catálogo de 10 livros
  clássicos (`canonical_books.json`) com capítulos e leituras recomendadas por assunto;
  (3) Utilitário CLI (`import_user_books.py`) e pasta `data/meus_livros/` para importação
  local de PDFs privados do usuário.
  Adicionada expansão massiva de slides curriculares baseados em aulas de maratona de
  professores universitários (UFMG, USP, Stanford, CLRS, Erickson, CP4), garantindo
  pelo menos 20 slides por tema em todos os 9 tópicos fundamentais (total de 183 slides).
  Implementado modo duplo de visualização no leitor de estudos (`core/study_pages.py`):
  alternância dinâmica entre "📖 Artigo contínuo" e "🖥️ Apresentação em Slides" com
  navegação passo a passo, seletor de slides e barra de progresso.
  Reforçada a profundidade teórica do tutor em grafos e DFS (`core/codigen_tutor.py` e
  `core/material_writer.py`), tornando mandatória a classificação das 4 arestas (Tree,
  Back, Forward, Cross), a máquina de estados de 3 cores (Branco, Cinza, Preto) e a
  distinção formal entre Grafo Simples, Grafo Direcionado e DAG.
  Implementado o Quadro Branco Inteligente com IA (`core/whiteboard_engine.py` e
  `core/whiteboard_views.py`), adicionando a página "Quadro Branco IA" ao menu principal (`app.py`).
  Inclui canvas interativo HTML5 para desenho livre com caneta touch/mouse, estampagem de nós
  numerados de grafos, arestas direcionadas com setas, caixas de estados (DP/fila/pilha), paleta de
  cores, desfazer e exportação em PNG. Oferece presets de maratona (DAG, Ciclo/Back Edge, Árvore,
  BFS e Bipartição), gerador de diagramas e instâncias com IA em Mermaid, formulário de análise
  pedagógica de modelagem e persistência na biblioteca pessoal (`kind='whiteboard'`).
- **Testes executados:**
  - `tests/test_whiteboard.py`: 6 novos testes cobrindo presets, extração e sanitização de Mermaid,
    geração e fallback por IA, análise de modelagem, geração do HTML do canvas e persistência
    de quadros na base SQLite: 100% aprovado.
  - `tests/test_learner_memory.py` ampliado para 5 testes (captura, privacidade,
    consolidação por tópicos, integração RAG e orçamentos de contexto): 100% aprovado.
  - `scripts/evaluate_ai_memory_agents.py` e `tests/test_ai_memory_agents.py`:
    simulação expandida para 6 personas de alunos sintéticos (Clara, Bruno, Diana,
    Eduardo, Fernando e Gabriela) com preservação de banco SQLite e arquivos Markdown
    em `autotutor_cp/.runtime/persisted_simulation/`. Retenção de lacunas: 100%.
  - `tests/test_study_pages.py`: ampliado com 4 novos testes cobrindo renderização e não-rejeição
    de diagramas Mermaid com mais de 25 linhas, sanitização automática de rótulos com parênteses,
    presença mandatória de diretrizes de aula visual, trace de execução e teoria completa de grafos
    (4 arestas da DFS, máquina de 3 cores e DAGs), inclusão de diagramas em modo offline e
    suporte de seções prontas para modo slides. 100% aprovado.
  - `tests/test_learning.py`: atualizado para validar a meta de $\ge 20$ slides por tópico
    em todos os 9 módulos e geração de HTML de apresentação: 100% aprovado.
  - `tests/test_book_catalog_and_importer.py`: 5 novos testes cobrindo o catálogo canônico
    de 10 livros clássicos (`core/book_catalog.py`), limpeza de texto e divisão em chunks
    de livros, simulação dry-run e importação real de PDFs/TXTs locais para o `KnowledgeBase`
    (`scripts/import_user_books.py`), além de recomendações de leitura no tutor. 100% aprovado.
  - *Suite Completa de Regressão:* Execução de todos os 278 testes do projeto (`autotutor_cp/tests/`):
    275 aprovados, 3 pulados, 0 falhas (100% verde).
- **Falhas observadas e corrigidas durante o desenvolvimento:**
  - *PDFs escaneados sem OCR no importador:* Arquivos em PDF contendo apenas imagens escaneadas
    (como o livro de Callioli de 1990) geravam 0 caracteres de texto no `pdftotext` e
    disparavam exceção não tratada que abortava a importação em lote. Corrigido com a classe
    `ScannedPdfError` e tratamento defensivo, exibindo aviso claro sobre necessidade de OCR
    e prosseguindo normalmente com a importação dos demais livros com texto pesquisável.
  - *Geração superficial de estudos:* Modelos de IA geravam materiais teóricos vagos,
    sem instâncias concretas e sem recursos visuais. Corrigido com reformulação das
    diretrizes para o formato de "Aula Completa e Visual", exigindo diagramas Mermaid
    (`graph TD`/`LR`), rastreamento minucioso passo a passo (trace) de fila/pilha/vetores
    e fundamentação teórica de invariantes.
  - *Falso positivo de segurança em diagramas:* Diagramas Mermaid extensos eram classificados
    como trechos de código C++ pelo filtro de cercas Markdown e descartados quando
    tinham mais de 25 linhas. Corrigido diferenciando blocos de diagramas (`is_diagram`)
    de blocos de código de programação (`code_snippets`).
  - *Fragmentação de tópicos:* Variações como `"Prefix Sum"` e `"Soma de prefixos"`
    inicialmente geravam arquivos separados, impedindo a unificação entre teoria e
    submissões. Corrigido com tabela canônica `_canonical_topic`.
  - *Truncamento precoce no brief:* O disclaimer pedagógico no início da página
    consumia a janela de caracteres antes dos diagnósticos. Corrigido com cabeçalho
    conciso e priorização da seção de dificuldades no topo.
  - *Idempotência em banco persistido:* A reexecução da simulação no mesmo banco
    falhava por colisão de chave única em `users.username`. Corrigido reutilizando
    o registro existente se já cadastrado.
  - *Fallback do juiz sem bubblewrap:* No Ubuntu 24.04 com restrição padrão do
    AppArmor a user namespaces não privilegiados (`apparmor_restrict_unprivileged_userns=1`),
    o `IsolatedMiniJudge` bloqueava qualquer submissão na interface web. Corrigido
    em `app.py` para usar `IsolatedMiniJudge` quando disponível ou fazer fallback
    transparente para o `MiniJudge` local com limites de tempo e memória POSIX.
- **O que ainda falta:**
  - Implementar reranking automático de problemas na Arena com base nas lacunas
    da memória;
  - Validação empírica com alunos e professores reais para medir ganhos de
    aprendizagem pedagógica além da simulação sintética.

## 8. Artefatos e limites

- Artigo LaTeX/SBC e PDF: `output/fundamentos_2026-11-05/entrega/artigo/`.
- Apresentação/PDF: `output/fundamentos_2026-11-05/entrega/`.
- Dados persistidos da simulação de agentes: `autotutor_cp/.runtime/persisted_simulation/`
  (contém `simulation.sqlite3`, `memory/`, `exports/`, `relatorio_simulacao.json` e `relatorio_simulacao.md`).
- Não alegar 99% de acurácia: o resultado AutoCode citado é de outra avaliação,
  com benchmark e protocolo próprios. Trocar somente o modelo não o reproduz.
- Erros 429/503, fontes e textos gerados devem ser expostos e revisados; RAG
  apoia a resposta, mas não treina nem altera pesos do modelo.
- Atualizar esta página com decisões, testes e pendências novas para evitar
  depender do contexto transitório do chat.


### Entrega Automática: Validador e Executor C++ do Quadro Branco
- Data: 2026-11-06 21:11:35
- Suíte de Testes: `tests/test_whiteboard_cpp.py` (100% Aprovado)
- RFC associada: `rfc-1794010292.md`


### Entrega Automática: API de outras IAs funcionando (Gemini, DeepSeek, Qwen, Ollama, OpenAI)
- Data: 2026-11-06 21:13:55
- Suíte de Testes: `tests/test_cloud_providers.py` (100% Aprovado)
- RFC associada: `rfc-1794010434.md`


### Entrega Automática: Conexão e Resiliência das APIs de IA
- Data: 2026-11-06 21:14:03
- Suíte de Testes: `tests/test_ai_connection.py` (100% Aprovado)
- RFC associada: `rfc-1794010442.md`

### Automação AntiGravity
- Quatro agentes de projeto: analista, implementador, revisor e coordenador.
- `scripts/antigravity_development_cycle.py` encadeia chats headless do `agy`;
  cada papel recebe a saída do anterior e o coordenador devolve a próxima tarefa.
- Modo padrão é simulação; `--live` exige AntiGravity instalado/autenticado e
  mantém permissões seguras. Nenhum patch é aplicado automaticamente.


### Entrega Automática: Renderizador Markdown Rico e Canvas Híbrido Obsidian-Whiteboard
- Data: 2026-11-06 23:45:06
- Suíte de Testes: `tests/test_study_pages.py` (100% Aprovado)
- RFC associada: `rfc-1794019503.md`
