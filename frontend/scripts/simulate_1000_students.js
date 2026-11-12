/**
 * Multi-Agent Synthetic Student Journey Simulation Engine
 * Simula 1.000 estudantes sintéticos no AutoTutor CP:
 * - Diagnóstico e Calibração
 * - Geração de Trilha Customizada e Tarefas
 * - Navegação e Resolução de Lições (Dashboard -> Workspace, Calendário -> Workspace, Trilhas -> Workspace)
 * - Auditoria de Redirecionamento Correto, Modo (Reader vs Arena) e Queda em Fallbacks
 */
const path = require("path");
const fs = require("fs");
const createJITI = require("jiti");

const jiti = createJITI(__filename, {
  alias: {
    "@": path.resolve(__dirname, "../src"),
  },
});

const {
  evaluateDiagnostic,
  generateCustomTrack,
  generateStudySchedule,
  resolveTaskActionUrl,
  DIAGNOSTIC_QUESTIONS,
} = jiti("../src/core/adaptiveRoadmapEngine.ts");

const { CURRICULUM_LESSONS } = jiti("../src/data/curriculumLessons.ts");

// Funções de resolução do Workspace e Trilhas
function parseCustomTrackLessons(track) {
  if (!track || !track.id) return [];

  const mainLesson = {
    id: track.id,
    category: `Personalizada: ${track.subject || track.targetGoal || "Algoritmos"}`,
    topicId: track.id,
    topicTitle: track.title,
    title: track.title,
    subtitle: track.description,
    summary: track.description,
    estimatedReadingMinutes: 30,
    totalCharacters: 3500,
    sections: (track.modules || track.milestones || []).map((m, idx) => ({
      id: m.id || m.topicId || `mod-${idx}`,
      title: m.title,
      content: `### ${m.title}`,
    })),
  };

  const moduleLessons = (track.modules || track.milestones || []).map((m, idx) => {
    const modId = m.id || m.topicId || `${track.id}-mod-${idx}`;
    return {
      id: modId,
      category: `${track.title} • Módulo ${idx + 1}`,
      topicId: track.id,
      topicTitle: track.title,
      title: m.title,
      subtitle: m.description || `Módulo focado de ${track.title}`,
      summary: m.description || m.title,
      estimatedReadingMinutes: 30,
      totalCharacters: 2200,
      sections: [
        {
          id: `${modId}-sec-1`,
          title: `Fundamentos: ${m.title}`,
          content: `### ${m.title}`,
        },
      ],
    };
  });

  return [mainLesson, ...moduleLessons];
}

function resolveLessonFromParams(lessonParam, topicParam, allLessons) {
  if (lessonParam) {
    const exactMatch = allLessons.find(
      (l) => l.id === lessonParam || l.id.toLowerCase() === lessonParam.toLowerCase()
    );
    if (exactMatch) return exactMatch.id;

    const sectionMatch = allLessons.find((l) =>
      l.sections.some((s) => s.id === lessonParam || s.id.toLowerCase() === lessonParam.toLowerCase())
    );
    if (sectionMatch) return sectionMatch.id;
  }

  if (topicParam) {
    const t = topicParam.toLowerCase().trim();

    if (
      t.includes("árvore") ||
      t.includes("arvore") ||
      t.includes("tree") ||
      t.includes("lca") ||
      t.includes("bst") ||
      t.includes("avl")
    ) {
      return "tree_foundations";
    }
    if (
      t.includes("busca bin") ||
      t.includes("binary search") ||
      (t.includes("binária") && !t.includes("arvor")) ||
      (t.includes("binaria") && !t.includes("arvor"))
    ) {
      return "binary_search_foundations";
    }
    if (t === "dp" || t.includes("dinâmica") || t.includes("dinamica") || t.includes("mochila")) {
      return "dp_knapsack_foundations";
    }
    if (t === "greedy" || t.includes("guloso")) {
      return "greedy_foundations";
    }
    if (t === "prefix" || t.includes("prefix")) {
      return "prefix_sum_foundations";
    }
    if (t === "dsu" || t === "segtree" || t.includes("segment")) {
      return "dsu_kruskal_mst";
    }
    if (t === "dijkstra" || t.includes("caminho")) {
      return "dijkstra_shortest_path";
    }
    if (t === "grafos" || t === "grafo" || t.includes("bfs") || t.includes("dfs")) {
      return "bfs_dfs_foundations";
    }

    const match = allLessons.find(
      (l) =>
        l.topicId.toLowerCase() === t ||
        l.id.toLowerCase() === t ||
        l.category.toLowerCase().includes(t) ||
        l.topicTitle.toLowerCase().includes(t) ||
        l.title.toLowerCase().includes(t)
    );
    if (match) return match.id;
  }

  if (lessonParam) {
    const lp = lessonParam.toLowerCase();
    if (lp.includes("árvor") || lp.includes("arvor") || lp.includes("tree")) return "tree_foundations";
    if (lp.includes("binar") || lp.includes("binary")) return "binary_search_foundations";
    if (lp.includes("dp") || lp.includes("dinam")) return "dp_knapsack_foundations";
  }

  return allLessons[0]?.id || "bfs_dfs_foundations";
}

function resolveWorkspaceUrl(slug, subject, title, parentTrackId) {
  const isCustomTrack =
    slug.startsWith("custom-") ||
    (parentTrackId && parentTrackId.startsWith("custom-")) ||
    slug.startsWith("track-") ||
    (parentTrackId && parentTrackId.startsWith("track-"));

  if (isCustomTrack) {
    const topicId = parentTrackId || slug;
    return `/workspace?topic=${encodeURIComponent(topicId)}&lesson=${encodeURIComponent(slug)}`;
  }

  const text = `${slug} ${subject} ${title}`.toLowerCase();

  if (
    text.includes("árvore") ||
    text.includes("arvore") ||
    text.includes("lca") ||
    text.includes("tree") ||
    text.includes("bst") ||
    text.includes("avl")
  ) {
    return "/workspace?topic=trees&lesson=tree_foundations&problem=binary_tree_lca";
  }
  if (
    text.includes("busca bin") ||
    text.includes("binary search") ||
    (text.includes("binária") && !text.includes("arvor")) ||
    (text.includes("binaria") && !text.includes("arvor"))
  ) {
    return "/workspace?topic=binary_search&lesson=binary_search_foundations&problem=binary_search";
  }
  if (text.includes("dp") || text.includes("dinâmica") || text.includes("dinamica") || text.includes("mochila")) {
    return "/workspace?topic=dp&lesson=dp_knapsack_foundations&problem=dp";
  }
  if (text.includes("guloso") || text.includes("greedy")) {
    return "/workspace?topic=greedy&lesson=greedy_foundations&problem=greedy_interval_scheduling";
  }
  if (text.includes("prefix") || text.includes("soma de prefixo")) {
    return "/workspace?topic=prefix_sum&lesson=prefix_sum_foundations&problem=prefix_sum_ranges";
  }
  if (text.includes("segtree") || text.includes("segment") || text.includes("dsu")) {
    return "/workspace?topic=segtree&lesson=dsu_kruskal_mst&problem=segment_tree";
  }
  if (text.includes("dijkstra") || text.includes("caminho mínimo") || text.includes("caminho minimo") || text.includes("caminho")) {
    return "/workspace?topic=dijkstra&lesson=dijkstra_shortest_path&problem=graph";
  }
  if (text.includes("grafo") || text.includes("bfs") || text.includes("dfs") || text.includes("busca em largura") || text.includes("busca em profundidade")) {
    return "/workspace?topic=grafos&lesson=bfs_dfs_foundations&problem=graph";
  }
  if (text.includes("recursão") || text.includes("recursao") || text.includes("backtracking")) {
    return "/workspace?topic=recursion&lesson=bfs_dfs_foundations&problem=graph";
  }

  const topicId = parentTrackId || slug;
  return `/workspace?topic=${encodeURIComponent(topicId)}&lesson=${encodeURIComponent(slug)}`;
}

// ==========================================
// CONFIGURAÇÃO DOS 1.000 AGENTES SINTÉTICOS
// ==========================================
const GOALS = ["foundations", "graphs", "dp", "obi", "icpc", "interviews"];
const LANGUAGES = ["cpp", "python", "java"];
const HOURS = [0.5, 1, 2, 3];

function createSyntheticAgent(i) {
  const goal = GOALS[i % GOALS.length];
  const lang = LANGUAGES[i % LANGUAGES.length];
  const hours = HOURS[i % HOURS.length];

  // Simulação de acertos no diagnóstico (probabilidades variadas de acordo com o perfil)
  // Iniciantes (i % 3 === 0), Intermediários (i % 3 === 1), Avançados (i % 3 === 2)
  const answers = {};
  DIAGNOSTIC_QUESTIONS.forEach((q, idx) => {
    const isNovice = i % 3 === 0;
    const isVeteran = i % 3 === 2;
    let chooseCorrect = false;

    if (isVeteran) {
      chooseCorrect = Math.random() < 0.95;
    } else if (isNovice) {
      chooseCorrect = Math.random() < 0.25;
    } else {
      chooseCorrect = Math.random() < 0.60;
    }

    const correctOpt = q.options.find((o) => o.isCorrect);
    const wrongOpt = q.options.find((o) => !o.isCorrect);
    answers[q.id] = chooseCorrect ? correctOpt.id : wrongOpt.id;
  });

  const diagnosticResult = evaluateDiagnostic(answers);

  const profile = {
    userId: `agent-${i + 1}`,
    hasCompletedOnboarding: true,
    targetGoal: goal,
    availableHoursPerDay: hours,
    activeDaysOfWeek: [1, 2, 3, 4, 5],
    preferredLanguage: lang,
    diagnosticResult,
  };

  return profile;
}

// ==========================================
// MOTOR DE EXECUÇÃO MULTI-AGENTE (1.000 AGENTES)
// ==========================================
console.log("===============================================================");
console.log("🚀 INICIANDO SIMULAÇÃO MULTI-AGENTE COM 1.000 ALUNOS SINTÉTICOS");
console.log("===============================================================\n");

const TOTAL_AGENTS = 1000;
let totalJourneysTested = 0;
let successfulJourneys = 0;
let fallbackDetections = 0;
let restRedirectionAnomalies = 0;
let singleStepDirectAccessCount = 0;

const distributionByGoal = {};
const levelDistribution = { Iniciante: 0, Intermediário: 0, Avançado: 0 };
const errorsByTopic = {};

const sampleAudits = [];

for (let i = 0; i < TOTAL_AGENTS; i++) {
  const profile = createSyntheticAgent(i);
  levelDistribution[profile.diagnosticResult.entryLevel]++;
  distributionByGoal[profile.targetGoal] = (distributionByGoal[profile.targetGoal] || 0) + 1;

  // 1. Geração da Trilha
  const track = generateCustomTrack(profile);
  const customLessons = parseCustomTrackLessons(track);
  const allLessons = [...CURRICULUM_LESSONS, ...customLessons];

  // 2. Geração do Cronograma
  const tasks = generateStudySchedule(track, profile, new Date());

  // Testar 3 Jornadas de Navegação por Aluno:
  
  // -------------------------------------------------------------
  // Jornada A: Dashboard -> Estudar Tarefa de Hoje
  // -------------------------------------------------------------
  totalJourneysTested++;
  const activeTasks = tasks.filter((t) => t.taskType !== "rest");
  const todayTask = activeTasks[0] || tasks[0];
  const dashboardUrl = resolveTaskActionUrl(todayTask);

  // Parse da URL
  const parsedDashUrl = new URL(dashboardUrl, "http://localhost:3000");
  const topicParam = parsedDashUrl.searchParams.get("topic");
  const lessonParam = parsedDashUrl.searchParams.get("lesson");
  const problemParam = parsedDashUrl.searchParams.get("problem");
  const modeParam = parsedDashUrl.searchParams.get("mode");

  const resolvedLessonId = resolveLessonFromParams(lessonParam, topicParam, allLessons);

  // Verificações da Jornada A:
  // Se o tópico da tarefa não é grafos, caiu em bfs_dfs_foundations?
  const isGraphRelated =
    (todayTask.topicId && todayTask.topicId.includes("graph")) ||
    (todayTask.title && todayTask.title.toLowerCase().includes("grafo")) ||
    (todayTask.title && todayTask.title.toLowerCase().includes("bfs"));

  if (!isGraphRelated && resolvedLessonId === "bfs_dfs_foundations") {
    fallbackDetections++;
    errorsByTopic[todayTask.topicId || "desconhecido"] =
      (errorsByTopic[todayTask.topicId || "desconhecido"] || 0) + 1;
  } else {
    successfulJourneys++;
  }

  // Verifica se é 1 clique direto
  if (dashboardUrl.startsWith("/workspace?") || dashboardUrl.startsWith("/revisao")) {
    singleStepDirectAccessCount++;
  }

  // -------------------------------------------------------------
  // Jornada B: Calendário -> Tarefa de Teoria vs Tarefa de Prática
  // -------------------------------------------------------------
  totalJourneysTested++;
  const theoryTask = tasks.find((t) => t.taskType === "theory");
  if (theoryTask) {
    const theoryUrl = resolveTaskActionUrl(theoryTask);
    const parsedTheoryUrl = new URL(theoryUrl, "http://localhost:3000");
    const theoryTopic = parsedTheoryUrl.searchParams.get("topic");
    const theoryLesson = parsedTheoryUrl.searchParams.get("lesson");
    const theoryMode = parsedTheoryUrl.searchParams.get("mode");

    const resolvedTheoryLesson = resolveLessonFromParams(theoryLesson, theoryTopic, allLessons);

    const isTheoryGraph =
      (theoryTask.topicId && theoryTask.topicId.includes("graph")) ||
      (theoryTask.title && theoryTask.title.toLowerCase().includes("grafo"));

    if (!isTheoryGraph && resolvedTheoryLesson === "bfs_dfs_foundations") {
      fallbackDetections++;
    } else if (theoryMode === "reader") {
      successfulJourneys++;
      singleStepDirectAccessCount++;
    }
  }

  // -------------------------------------------------------------
  // Jornada C: Trilhas -> Módulo da Trilha Customizada
  // -------------------------------------------------------------
  totalJourneysTested++;
  if (track.milestones.length > 0) {
    const randomMilestone = track.milestones[i % track.milestones.length];
    const trackModuleUrl = resolveWorkspaceUrl(
      randomMilestone.topicId,
      randomMilestone.category,
      randomMilestone.title,
      track.id
    );

    const parsedModUrl = new URL(trackModuleUrl, "http://localhost:3000");
    const modTopic = parsedModUrl.searchParams.get("topic");
    const modLesson = parsedModUrl.searchParams.get("lesson");

    const resolvedModLesson = resolveLessonFromParams(modLesson, modTopic, allLessons);

    // O módulo deve resolver no ID do módulo ou na lição customizada
    if (resolvedModLesson === randomMilestone.topicId || resolvedModLesson === track.id) {
      successfulJourneys++;
      singleStepDirectAccessCount++;
    } else {
      fallbackDetections++;
    }
  }

  // Verificar anomalia de descanso
  const restTask = tasks.find((t) => t.taskType === "rest");
  if (restTask) {
    const restUrl = resolveTaskActionUrl(restTask);
    if (restUrl.includes("/workspace?topic=rest")) {
      restRedirectionAnomalies++;
    }
  }

  // Coleta amostra para o relatório
  if (i === 0 || i === 250 || i === 500 || i === 750) {
    sampleAudits.push({
      agentIndex: i + 1,
      goal: profile.targetGoal,
      level: profile.diagnosticResult.entryLevel,
      milestonesCount: track.milestones.length,
      firstTask: todayTask.title,
      resolvedUrl: dashboardUrl,
      resolvedLessonId,
    });
  }
}

console.log("--- RESULTADOS DA SIMULAÇÃO COM 1.000 ESTUDANTES ---");
console.log(`Total de Agentes Avaliados: ${TOTAL_AGENTS}`);
console.log(`Total de Jornadas de Navegação Testadas: ${totalJourneysTested}`);
console.log(`Jornadas Aprovadas com Sucesso: ${successfulJourneys} (${((successfulJourneys / totalJourneysTested) * 100).toFixed(1)}%)`);
console.log(`Jornadas de 1 Passo Direto (Mínimo de Cliques): ${singleStepDirectAccessCount} (${((singleStepDirectAccessCount / totalJourneysTested) * 100).toFixed(1)}%)`);
console.log(`Detecções de Queda em Fallback (Travamento em BFS/DFS): ${fallbackDetections}`);
console.log(`Anomalias em Tarefas de Descanso (URL com topic=rest): ${restRedirectionAnomalies} de ${TOTAL_AGENTS}`);
console.log("\nDistribuição de Nível dos Alunos:");
console.table(levelDistribution);
console.log("Distribuição por Meta de Estudo:");
console.table(distributionByGoal);

if (Object.keys(errorsByTopic).length > 0) {
  console.log("\nTópicos que sofreram fallback para BFS/DFS:");
  console.table(errorsByTopic);
}

// Salva relatório estruturado em .runtime
const reportPath = path.resolve(__dirname, "../../.runtime/simulation_1000_students_report.json");
fs.writeFileSync(
  reportPath,
  JSON.stringify(
    {
      totalAgents: TOTAL_AGENTS,
      totalJourneysTested,
      successfulJourneys,
      successRate: ((successfulJourneys / totalJourneysTested) * 100).toFixed(1) + "%",
      singleStepDirectAccessRate: ((singleStepDirectAccessCount / totalJourneysTested) * 100).toFixed(1) + "%",
      fallbackDetections,
      restRedirectionAnomalies,
      levelDistribution,
      distributionByGoal,
      errorsByTopic,
      sampleAudits,
    },
    null,
    2
  ),
  "utf-8"
);

console.log(`\n✓ Relatório de auditoria persistido em: ${reportPath}`);
