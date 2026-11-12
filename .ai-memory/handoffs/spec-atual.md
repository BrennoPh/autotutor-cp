# RFC & Especificação Técnica: Roteamento 100% Dinâmico de Trilhas, Isolamento de Conclusão e Navegação Intra-Trilha

## 1. Contexto e Motivação
O usuário relatou três anomalias críticas no fluxo de aprendizagem:
1. **Roteamento Estático Rígido:** Ao criar ou navegar por trilhas (onboarding, IA ou manuais), caminhos fixos (`if (text.includes("grafo")) return "/workspace?topic=grafos&lesson=bfs_dfs_foundations"`) forçavam o aluno sempre para a mesma aula de Grafos (`bfs_dfs_foundations`) e para o mesmo problema na prática (`graph` - "Rotas entre cidades"), ignorando os módulos gerados.
2. **Conclusão Indiscriminada em Cascata:** Ao marcar a primeira aula de Teoria como concluída, `lessonProgressService.ts` comparava `t.topicId === lessonId` sem distinguir `taskType`. Como as tarefas de teoria, prática e revisão compartilhavam o mesmo `topicId`, um clique marcava a teoria, o desafio prático e o flashcard simultaneamente como concluídos, além de marcar o módulo inteiro da trilha.
3. **Quebra de Contexto ao Avançar ("Avançar para Próxima Aula"):** O botão "Avançar" consumia a lista canônica global (`CURRICULUM_LESSONS`), avançando linearmente de Grafos para Dijkstra para SegTree para DP, em vez de avançar para o Módulo 2 e Módulo 3 da *mesma trilha*.

## 2. Decisões Arquiteturais

### 2.1 Eliminação Absoluta de Mapeamentos Estáticos por Keyword
- Remover todas as funções heurísticas do tipo `if (text.includes("grafo")) ...` em `trilhas/[slug]/page.tsx`, `adaptiveRoadmapEngine.ts`, `workspace/page.tsx` e `PracticeArena.tsx`.
- Toda navegação utilizará identificadores de entidade dinâmicos:
  `URL: /workspace?topic=${encodeURIComponent(trackId)}&lesson=${encodeURIComponent(moduleId)}&mode=reader`
  `URL: /workspace?topic=${encodeURIComponent(trackId)}&problem=${encodeURIComponent(moduleId)}&mode=arena`

### 2.2 Isolamento Estrito de Conclusão de Tarefas por Tipo
- A conclusão de uma aula de teoria (`mode=reader`) altera **apenas** tarefas com `t.taskType === "theory"`.
- Tarefas do tipo `"problem"` só são concluídas através da submissão/aprovação na Arena ou ação explícita de prática.
- Tarefas do tipo `"review"` só são concluídas via sessão de flashcards.
- Na trilha do usuário, apenas o módulo cujo `id` corresponda ao `lessonId` é marcado como concluído.

### 2.3 Navegação Intra-Trilha Sequencial
- O serviço `lessonProgressService.getNextStepForLesson` deve receber ou consultar os módulos da trilha ativa (`currentTopicId` / `trackLessons`).
- Se houver próximo módulo na trilha atual ($i+1$), o botão "Próxima Aula" avança para `$trackLessons[i+1]`.
- Se o aluno estiver no último módulo teórico da trilha atual, a CTA de avanço convida o aluno a praticar o desafio no Juiz Online (`mode=arena`) dentro do tema da trilha.

## 3. Matriz de Mudanças
1. `frontend/src/services/lessonProgressService.ts`:
   - Filtrar por `t.taskType === "theory"` em `toggleLessonCompletion`.
   - Ajustar `getNextStepForLesson` para sequenciamento intra-trilha baseado nos módulos do `trackId`.
2. `frontend/src/core/adaptiveRoadmapEngine.ts`:
   - `resolveTaskActionUrl`: gerar URLs dinâmicas baseadas no `track.id` e `milestone.topicId` sem keywords estáticas.
   - `generateStudySchedule`: gerar IDs únicos e desvinculados para theory, problem e review.
3. `frontend/src/app/trilhas/[slug]/page.tsx`:
   - Remover `resolveWorkspaceUrl` baseado em keywords.
   - Utilizar resolução dinâmica `track.id` + `mod.id`.
4. `frontend/src/app/workspace/page.tsx`:
   - Em `resolveLessonFromParams`, priorizar busca exata em `allLessons` antes de qualquer fallback.
   - Fornecer lista ordenada de lições da trilha ativa para `StudyReader` / `WorkspaceLayout`.
5. Testes automatizados:
   - Script de teste de ponta a ponta (`simulate_dynamic_tracks_and_isolation.js`) cobrindo:
     a) Geração dinâmica de trilha e ausência de hardcodes.
     b) Isolamento: marcar teoria NÃO marca prática nem flashcards.
     c) Avanço: clicar em avançar no módulo 1 leva ao módulo 2 da mesma trilha.
