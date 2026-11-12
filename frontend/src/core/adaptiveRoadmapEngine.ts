import {
  DiagnosticQuestion,
  DiagnosticResult,
  UserAssessmentProfile,
  CustomTrack,
  TrackMilestone,
  ScheduledTask,
  EntryLevel,
} from "@/types/onboarding";

export const DIAGNOSTIC_QUESTIONS: DiagnosticQuestion[] = [
  {
    id: "q1_complexity",
    topic: "Análise Assintótica e Complexidade",
    difficulty: "basic",
    question: "Qual é a complexidade de tempo no pior caso para o trecho de código abaixo?",
    codeSnippet: `int count = 0;
for (int i = 1; i <= N; i *= 2) {
    for (int j = 0; j < N; j++) {
        count++;
    }
}`,
    options: [
      { id: "a", text: "O(N²)", isCorrect: false },
      { id: "b", text: "O(N log N)", isCorrect: true },
      { id: "c", text: "O(N)", isCorrect: false },
      { id: "d", text: "O(log N)", isCorrect: false },
    ],
    explanation:
      "O laço externo dobra o valor de i a cada iteração, executando log₂(N) vezes. O laço interno roda N vezes fixas. Portanto, a complexidade total é O(N log N).",
  },
  {
    id: "q2_recursion_stack",
    topic: "Recursão e Pilha de Execução",
    difficulty: "intermediate",
    question:
      "Ao executar uma busca em profundidade recursiva sem memoization em uma grade 1000x1000, o programa sofre um travamento por 'Segmentation Fault / Stack Overflow'. Qual é a causa raiz?",
    codeSnippet: `void dfs(int r, int c) {
    visited[r][c] = true;
    for (auto [dr, dc] : dirs)
        if (valid(r+dr, c+dc) && !visited[r+dr][c+dc])
            dfs(r+dr, c+dc);
}`,
    options: [
      { id: "a", text: "Tempo limite excedido (TLE) devido ao laço for.", isCorrect: false },
      { id: "b", text: "A matriz visited consome mais de 2GB de memória heap.", isCorrect: false },
      {
        id: "c",
        text: "O limite de profundidade da Call Stack do sistema operacional foi excedido.",
        isCorrect: true,
      },
      { id: "d", text: "Recursões em C++ só suportam no máximo 100 chamadas aninhadas.", isCorrect: false },
    ],
    explanation:
      "A pilha de execução (Call Stack) do processo possui um tamanho finito (geralmente 8MB). Em caminhos longos de até 10⁶ passos, a profundidade de recursão esgota a pilha do sistema operacional antes do término da DFS.",
  },
  {
    id: "q3_bfs_queue",
    topic: "Fila (Queue) e Invariante de Camadas da BFS",
    difficulty: "intermediate",
    question:
      "Em uma Busca em Largura (BFS) para menor caminho em grafos não-ponderados, por que é essencial marcar o nó como visitado no momento do PUSH na fila em vez do POP?",
    codeSnippet: `// Abordagem A: visited no PUSH
queue.push(vizinho);
visited[vizinho] = true;

// Abordagem B: visited no POP
int u = queue.pop();
visited[u] = true;`,
    options: [
      { id: "a", text: "Não há diferença: ambas possuem a mesma complexidade de tempo e memória.", isCorrect: false },
      {
        id: "b",
        text: "Marcar no POP permite que múltiplos nós alcancem o mesmo vizinho e o reinsiram várias vezes, causando TLE e estouro de memória (MLE).",
        isCorrect: true,
      },
      { id: "c", text: "Marcar no PUSH inverte a ordem topológica dos nós explorados.", isCorrect: false },
      { id: "d", text: "A fila FIFO só aceita valores booleanos como chave.", isCorrect: false },
    ],
    explanation:
      "Se você marcar no POP, qualquer outro nó da mesma camada que também conecte a esse vizinho irá enfileirá-lo novamente antes que ele seja processado, gerando explosão combinatória de nós duplicados na fila.",
  },
  {
    id: "q4_dfs_cycles",
    topic: "Detecção de Ciclos e Arestas de Retorno (DFS)",
    difficulty: "advanced",
    question:
      "Em um Grafo Dirigido, como diferenciamos uma aresta que indica um ciclo real de uma aresta que simplesmente aponta para um nó já visitado em outro ramo (aresta de cruzamento)?",
    options: [
      { id: "a", text: "Basta verificar se visited[v] == true.", isCorrect: false },
      {
        id: "b",
        text: "O ciclo só existe se o nó destino estiver ativo no conjunto de recursão atual (in_stack[v] == true), caracterizando uma Back-Edge.",
        isCorrect: true,
      },
      { id: "c", text: "Grafos dirigidos não possuem arestas de cruzamento, apenas ciclos.", isCorrect: false },
      { id: "d", text: "Calculando a distância euclidiana entre os vértices.", isCorrect: false },
    ],
    explanation:
      "Em grafos dirigidos, apontar para um nó visitado não implica ciclo a menos que esse nó seja um ancestral na pilha ativa de recursão (`in_stack`).",
  },
  {
    id: "q5_dp_memo",
    topic: "Programação Dinâmica e Subestrutura Ótima",
    difficulty: "advanced",
    question:
      "Qual é a condição primária que torna viável a aplicação de Programação Dinâmica em vez de uma Busca Exaustiva ingênua?",
    options: [
      { id: "a", text: "O grafo ou problema possuir apenas números primos como pesos.", isCorrect: false },
      {
        id: "b",
        text: "Presença de Subproblemas Sobrepostos e Subestrutura Ótima.",
        isCorrect: true,
      },
      { id: "c", text: "O algoritmo rodar obrigatoriamente com recursão em cauda.", isCorrect: false },
      { id: "d", text: "A entrada estar previamente ordenada em ordem decrescente.", isCorrect: false },
    ],
    explanation:
      "A Programação Dinâmica aproveita o fato de que os mesmos subproblemas são resolvidos repetidas vezes (sobreposição) e a solução ótima global é composta por soluções ótimas locais.",
  },
];

/**
 * Avalia o questionário diagnóstico e gera pontuações e lacunas de conhecimento.
 */
export function evaluateDiagnostic(answers: Record<string, string>): DiagnosticResult {
  let correctCount = 0;
  const strongTopics: string[] = [];
  const gapTopics: string[] = [];

  DIAGNOSTIC_QUESTIONS.forEach((q) => {
    const selectedOptionId = answers[q.id];
    const correctOption = q.options.find((opt) => opt.isCorrect);

    if (selectedOptionId && correctOption && selectedOptionId === correctOption.id) {
      correctCount++;
      strongTopics.push(q.topic);
    } else {
      gapTopics.push(q.topic);
    }
  });

  const score = Math.round((correctCount / DIAGNOSTIC_QUESTIONS.length) * 100);

  let entryLevel: EntryLevel = "Iniciante";
  if (score >= 80) entryLevel = "Avançado";
  else if (score >= 50) entryLevel = "Intermediário";

  return {
    score,
    entryLevel,
    confidence: "alta",
    strongTopics,
    gapTopics,
    evaluatedAt: new Date().toISOString(),
    answers,
  };
}

/**
 * Gera a trilha dinâmica personalizada considerando objetivos declarados e lacunas reais.
 */
export function generateCustomTrack(profile: UserAssessmentProfile): CustomTrack {
  const result = profile.diagnosticResult;
  const milestones: TrackMilestone[] = [];
  let week = 1;

  // 1. Scaffolding: Se o aluno tem lacunas em recursão, pilha ou complexidade, adiciona semana de nivelamento
  const hasStackOrRecursionGap = result?.gapTopics.some((t) =>
    t.includes("Recursão") || t.includes("Complexidade")
  );

  if (hasStackOrRecursionGap || profile.targetGoal === "foundations") {
    milestones.push({
      weekNumber: week++,
      topicId: "recursion_foundations",
      title: "Fundamentos Críticos: Pilha de Recursão & Análise O(N)",
      category: "Estruturas de Dados Lineares",
      isPrerequisiteRefinement: true,
      estimatedHours: 6,
      keyConcepts: [
        "Call Stack e profundidade de recursão",
        "Prevenção de Stack Overflow",
        "Análise assintótica formal",
      ],
    });

    if (profile.targetGoal === "foundations") {
      milestones.push({
        weekNumber: week++,
        topicId: "bfs_dfs_foundations",
        title: "Estruturas Lineares: Vetores Dinâmicos, Pilhas e Filas FIFO",
        category: "Estruturas de Dados Fundamentais",
        isPrerequisiteRefinement: false,
        estimatedHours: 6,
        keyConcepts: [
          "std::vector e realocação dinâmica",
          "std::queue e std::stack",
          "Consultas por índice e invariantes",
        ],
      });
      milestones.push({
        weekNumber: week++,
        topicId: "binary_search_foundations",
        title: "Busca Binária & Invariantes de Ordenação",
        category: "Algoritmos Fundamentais",
        isPrerequisiteRefinement: false,
        estimatedHours: 8,
        keyConcepts: [
          "Busca Binária no vetor ordenado",
          "lower_bound e upper_bound",
          "Complexidade O(log N)",
        ],
      });
    }
  }

  // 2. Se a meta envolver Grafos, OBI ou ICPC
  if (["graphs", "obi", "icpc", "interviews"].includes(profile.targetGoal)) {
    // Lacuna de BFS/Fila?
    const hasBfsGap = result?.gapTopics.some((t) => t.includes("Fila"));
    if (hasBfsGap) {
      milestones.push({
        weekNumber: week++,
        topicId: "graph_bfs_queue",
        title: "Busca em Largura (BFS) & Invariante de Fila",
        category: "Grafos Básicos",
        isPrerequisiteRefinement: true,
        estimatedHours: 8,
        keyConcepts: [
          "Fila FIFO e caminhos mínimos não-ponderados",
          "Regra do PUSH vs POP para visitados",
          "BFS Multi-Source",
        ],
      });
    }

    milestones.push({
      weekNumber: week++,
      topicId: "graph_dfs_cycles",
      title: "DFS Profunda, Detecção de Ciclos & DAGs",
      category: "Grafos e Árvores",
      isPrerequisiteRefinement: false,
      estimatedHours: 8,
      keyConcepts: [
        "Classificação de arestas (Tree, Back, Forward, Cross)",
        "Conjunto in_stack e aciclicidade",
        "Ordenação Topológica (Kahn e DFS)",
      ],
    });

    milestones.push({
      weekNumber: week++,
      topicId: "graph_dijkstra_scc",
      title: "Caminhos Mínimos Ponderados & Componentes Conexos",
      category: "Grafos Avançados",
      isPrerequisiteRefinement: false,
      estimatedHours: 10,
      keyConcepts: [
        "Dijkstra com Min-Heap",
        "Algoritmo de Tarjan para SCCs",
        "Pontes e Pontos de Articulação",
      ],
    });
  }

  // 3. Se a meta envolver Programação Dinâmica
  if (["dp", "icpc", "interviews"].includes(profile.targetGoal)) {
    milestones.push({
      weekNumber: week++,
      topicId: "dynamic_programming_intro",
      title: "Programação Dinâmica 1D: Memoization & Tabulação",
      category: "Paradigmas Algorítmicos",
      isPrerequisiteRefinement: false,
      estimatedHours: 8,
      keyConcepts: [
        "Subproblemas sobrepostos",
        "Top-down vs Bottom-up",
        "Problema da Mochila (Knapsack 0/1)",
      ],
    });
  }

  return {
    id: `track-${profile.userId}-${profile.targetGoal}`,
    title: `Trilha Adaptativa: Rumo ao Domínio em ${profile.targetGoal.toUpperCase()}`,
    description: `Plano customizado calibrado para nível ${result?.entryLevel || "Iniciante"}, com foco prioritário em sanar as lacunas identificadas no diagnóstico.`,
    totalWeeks: milestones.length,
    targetGoal: profile.targetGoal,
    entryLevel: result?.entryLevel || "Iniciante",
    milestones,
  };
}

/**
 * Resolve a URL correta com base no tipo da tarefa e nos conceitos abordados.
 * Garante que tarefas teóricas abram diretamente em mode=reader e tarefas práticas em mode=arena.
 */
export function resolveTaskActionUrl(
  task: {
    topicId?: string;
    title?: string;
    description?: string;
    taskType?: "theory" | "problem" | "review" | "rest" | string;
    actionUrl?: string;
  },
  parentTrackId?: string
): string {
  if (task.actionUrl) return task.actionUrl;

  const typeStr = (task.taskType || "").toLowerCase().trim();
  const titleStr = (task.title || "").toLowerCase().trim();

  if (typeStr === "rest" || titleStr.includes("descanso")) {
    return "/calendar";
  }

  const isReview =
    typeStr === "review" ||
    titleStr.includes("revisão") ||
    titleStr.includes("revisao") ||
    titleStr.includes("flashcard");
  if (isReview) {
    return `/revisao?topic=${encodeURIComponent(task.topicId || parentTrackId || "geral")}`;
  }

  const isProblem =
    typeStr === "problem" ||
    titleStr.startsWith("prática") ||
    titleStr.startsWith("pratica") ||
    titleStr.includes("desafio") ||
    titleStr.includes("exercício");

  const effectiveTrack = parentTrackId || task.topicId || "geral";
  const effectiveModule = task.topicId || "inicio";

  if (isProblem) {
    return `/workspace?topic=${encodeURIComponent(effectiveTrack)}&problem=${encodeURIComponent(effectiveModule)}&mode=arena`;
  }

  return `/workspace?topic=${encodeURIComponent(effectiveTrack)}&lesson=${encodeURIComponent(effectiveModule)}&mode=reader`;
}

/**
 * Gera a grade do calendário distribuindo tarefas apenas nos dias ativos da semana,
 * incluindo intervalos de repetição espaçada calculados.
 */
export function generateStudySchedule(
  track: CustomTrack,
  profile: UserAssessmentProfile,
  startDate: Date = new Date()
): ScheduledTask[] {
  const tasks: ScheduledTask[] = [];
  const rawDays = profile.activeDaysOfWeek && profile.activeDaysOfWeek.length > 0
    ? profile.activeDaysOfWeek.filter((d) => Number.isInteger(d) && d >= 0 && d <= 6)
    : [1, 2, 3, 4, 5];
  const validDays = rawDays.length > 0 ? rawDays : [1, 2, 3, 4, 5];
  const activeDays = new Set(validDays);
  const dailyMinutes = Math.max(15, Math.round((profile.availableHoursPerDay || 1) * 60));

  let currentDate = new Date(startDate);
  // Normaliza para meia-noite
  currentDate.setHours(0, 0, 0, 0);

  let taskCounter = 1;

  track.milestones.forEach((milestone) => {
    const keyConceptsSafe = Array.isArray(milestone.keyConcepts) ? milestone.keyConcepts : [];
    // Para cada milestone, planejamos 3 tipos de sessões com IDs e escopos estritamente desacoplados:
    // 1. Estudo Teórico / Leitura (mode=reader)
    // 2. Resolução de Problemas Práticos (mode=arena)
    // 3. Revisão Espaçada (Ebbinghaus)

    const sessionDefinitions = [
      {
        type: "theory" as const,
        suffix: "theory",
        title: `Teoria: ${milestone.title}`,
        desc: `Conceitos centrais: ${keyConceptsSafe.join(", ")}.`,
        minutes: Math.min(dailyMinutes, 45),
        url: resolveTaskActionUrl(
          {
            topicId: milestone.topicId,
            title: `Teoria: ${milestone.title}`,
            description: keyConceptsSafe.join(", "),
            taskType: "theory",
          },
          track.id
        ),
      },
      {
        type: "problem" as const,
        suffix: "problem",
        title: `Prática: Problemas em ${milestone.title}`,
        desc: "2 problemas competitivos recomendados para fixação.",
        minutes: dailyMinutes,
        url: resolveTaskActionUrl(
          {
            topicId: milestone.topicId,
            title: `Prática: Problemas em ${milestone.title}`,
            description: keyConceptsSafe.join(", "),
            taskType: "problem",
          },
          track.id
        ),
      },
      {
        type: "review" as const,
        suffix: "review",
        title: `Revisão Espaçada: Flashcards de ${milestone.title}`,
        desc: "Ciclo rápido de retenção da curva de Ebbinghaus.",
        minutes: 20,
        url: `/revisao?topic=${encodeURIComponent(milestone.topicId)}`,
      },
    ];

    sessionDefinitions.forEach((session) => {
      // Avança até encontrar um dia ativo com limite de segurança de 30 dias
      let safetyCounter = 30;
      while (!activeDays.has(currentDate.getDay()) && safetyCounter-- > 0) {
        // Registra o dia como descanso programado
        const restDateStr = currentDate.toISOString().split("T")[0];
        tasks.push({
          id: `task-rest-${taskCounter++}`,
          date: restDateStr,
          topicId: "rest",
          title: "Descanso Programado",
          description: "Dia livre sem sessões agendadas para consolidação cognitiva.",
          taskType: "rest",
          status: "rest",
          estimatedMinutes: 0,
        });
        currentDate.setDate(currentDate.getDate() + 1);
      }

      // Agenda a tarefa no dia ativo encontrado com ID tipado único
      const dateStr = currentDate.toISOString().split("T")[0];
      tasks.push({
        id: `task-${session.suffix}-${taskCounter++}`,
        date: dateStr,
        topicId: milestone.topicId,
        title: session.title,
        description: session.desc,
        taskType: session.type,
        status: "pending",
        estimatedMinutes: session.minutes,
        actionUrl: session.url,
      });

      // Passa para o dia seguinte
      currentDate.setDate(currentDate.getDate() + 1);
    });
  });

  return tasks;
}
