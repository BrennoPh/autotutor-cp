/**
 * Multi-Agent Synthetic Student Journey Simulation Engine - 1,000,000 AGENTS
 * AutoTutor CP: Stress Test em Hiper-Escala (3.000.000 de Jornadas de Navegação)
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
  const cleanLesson = (lessonParam && lessonParam !== "undefined" && lessonParam !== "null") ? lessonParam.trim() : null;
  const cleanTopic = (topicParam && topicParam !== "undefined" && topicParam !== "null") ? topicParam.trim() : null;

  if (cleanLesson) {
    const exactMatch = allLessons.find(
      (l) => l.id === cleanLesson || l.id.toLowerCase() === cleanLesson.toLowerCase()
    );
    if (exactMatch) return exactMatch.id;

    const sectionMatch = allLessons.find((l) =>
      l.sections.some((s) => s.id === cleanLesson || s.id.toLowerCase() === cleanLesson.toLowerCase())
    );
    if (sectionMatch) return sectionMatch.id;
  }

  if (cleanTopic) {
    const t = cleanTopic.toLowerCase().trim();

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
    if (t === "recursion" || t.includes("recurs") || t.includes("pilha") || t.includes("stack") || t.includes("fundamentos") || t.includes("foundations")) {
      const match = allLessons.find((l) => l.id.includes("foundations_stack") || l.topicId.includes("foundations"));
      if (match) return match.id;
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

  if (cleanLesson) {
    const lp = cleanLesson.toLowerCase();
    if (lp.includes("árvor") || lp.includes("arvor") || lp.includes("tree")) return "tree_foundations";
    if (lp.includes("binar") || lp.includes("binary")) return "binary_search_foundations";
    if (lp.includes("dp") || lp.includes("dinam")) return "dp_knapsack_foundations";
    if (lp.includes("recurs") || lp.includes("pilha") || lp.includes("stack") || lp.includes("foundations")) {
      const match = allLessons.find((l) => l.id.includes("foundations_stack") || l.topicId.includes("foundations"));
      if (match) return match.id;
    }
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
// CONFIGURAÇÃO DOS 1.000.000 DE AGENTES SINTÉTICOS
// ==========================================
const GOALS = ["foundations", "graphs", "dp", "obi", "icpc", "interviews"];
const LANGUAGES = ["cpp", "python", "java"];
const HOURS = [0.5, 1, 2, 3];
const ACTIVE_DAYS_PRESETS = [
  [1, 2, 3, 4, 5],       // Seg a Sex (Padrão)
  [0, 1, 2, 3, 4, 5, 6], // Todos os dias
  [1, 3, 5],             // Seg, Qua, Sex
  [6, 0],                // Fins de semana
  [],                    // Borda: array vazio (deve cair no fallback sem loop)
  [2, 4],                // Ter, Qui
  [1],                   // Apenas Segunda
];

console.log("==================================================================");
console.log("🚀 SIMULAÇÃO MASSIVA DE 1.000.000 DE ESTUDANTES SINTÉTICOS (AutoTutor CP)");
console.log("==================================================================\n");

const TOTAL_AGENTS = 1_000_000;
const BATCH_SIZE = 50_000;
const t_start = Date.now();

let totalJourneysTested = 0;
let successfulJourneys = 0;
let fallbackDetections = 0;
let restRedirectionAnomalies = 0;
let singleStepDirectAccessCount = 0;

const levelDistribution = { Iniciante: 0, Intermediário: 0, Avançado: 0 };
const distributionByGoal = { foundations: 0, graphs: 0, dp: 0, obi: 0, icpc: 0, interviews: 0 };
const errorsByTopic = {};

for (let batch = 0; batch < TOTAL_AGENTS / BATCH_SIZE; batch++) {
  const batchStart = batch * BATCH_SIZE;
  const batchEnd = batchStart + BATCH_SIZE;

  for (let i = batchStart; i < batchEnd; i++) {
    const goal = GOALS[i % GOALS.length];
    const lang = LANGUAGES[i % LANGUAGES.length];
    const hours = HOURS[i % HOURS.length];
    const daysPreset = ACTIVE_DAYS_PRESETS[i % ACTIVE_DAYS_PRESETS.length];

    // Simulação determinística de respostas cobrindo todo o espaço de estados
    const answers = {};
    const pattern = i % 1024;
    DIAGNOSTIC_QUESTIONS.forEach((q, qIdx) => {
      const bit = (pattern >> qIdx) & 1;
      const opt = bit ? q.options.find((o) => o.isCorrect) : q.options.find((o) => !o.isCorrect);
      answers[q.id] = opt ? opt.id : "a";
    });

    const diagnosticResult = evaluateDiagnostic(answers);
    levelDistribution[diagnosticResult.entryLevel]++;
    distributionByGoal[goal]++;

    const profile = {
      userId: `agent-${i + 1}`,
      hasCompletedOnboarding: true,
      targetGoal: goal,
      availableHoursPerDay: hours,
      activeDaysOfWeek: daysPreset,
      preferredLanguage: lang,
      diagnosticResult,
    };

    // 1. Geração da Trilha Adaptativa
    const track = generateCustomTrack(profile);
    const customLessons = parseCustomTrackLessons(track);
    const allLessons = [...CURRICULUM_LESSONS, ...customLessons];

    // 2. Geração do Cronograma Preditivo
    const tasks = generateStudySchedule(track, profile, new Date());

    // -------------------------------------------------------------
    // Jornada 1: Dashboard -> Card Principal de Retomada
    // -------------------------------------------------------------
    totalJourneysTested++;
    const activeTasks = tasks.filter((t) => t.taskType !== "rest");
    const todayTask = activeTasks[0] || tasks[0];
    const dashboardUrl = resolveTaskActionUrl(todayTask);

    const parsedDashUrl = new URL(dashboardUrl, "http://localhost:3000");
    const topicParam = parsedDashUrl.searchParams.get("topic");
    const lessonParam = parsedDashUrl.searchParams.get("lesson");

    const resolvedLessonId = resolveLessonFromParams(lessonParam, topicParam, allLessons);

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

    if (dashboardUrl.startsWith("/workspace?") || dashboardUrl.startsWith("/revisao") || dashboardUrl.startsWith("/calendar")) {
      singleStepDirectAccessCount++;
    }

    // -------------------------------------------------------------
    // Jornada 2: Calendário -> Tarefa de Teoria (Leitor)
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
    // Jornada 3: Trilhas -> Módulo da Trilha Customizada
    // -------------------------------------------------------------
    totalJourneysTested++;
    if (track.milestones.length > 0) {
      const selectedMilestone = track.milestones[i % track.milestones.length];
      const trackModuleUrl = resolveWorkspaceUrl(
        selectedMilestone.topicId,
        selectedMilestone.category,
        selectedMilestone.title,
        track.id
      );

      const parsedModUrl = new URL(trackModuleUrl, "http://localhost:3000");
      const modTopic = parsedModUrl.searchParams.get("topic");
      const modLesson = parsedModUrl.searchParams.get("lesson");

      const resolvedModLesson = resolveLessonFromParams(modLesson, modTopic, allLessons);

      if (resolvedModLesson === selectedMilestone.topicId || resolvedModLesson === track.id) {
        successfulJourneys++;
        singleStepDirectAccessCount++;
      } else {
        fallbackDetections++;
      }
    }

    // Checagem de Anomalia de Descanso
    const restTask = tasks.find((t) => t.taskType === "rest");
    if (restTask) {
      const restUrl = resolveTaskActionUrl(restTask);
      if (restUrl.includes("/workspace?topic=rest")) {
        restRedirectionAnomalies++;
      }
    }
  }

  const elapsedSec = ((Date.now() - t_start) / 1000).toFixed(1);
  const percentDone = (((batch + 1) * BATCH_SIZE / TOTAL_AGENTS) * 100).toFixed(0);
  process.stdout.write(`⚡ Processado Lote ${batch + 1}/${TOTAL_AGENTS / BATCH_SIZE} (${percentDone}%) — ${batchEnd.toLocaleString()} agentes (${elapsedSec}s)\r`);
}

const totalSec = ((Date.now() - t_start) / 1000).toFixed(2);
console.log(`\n\n✓ SIMULAÇÃO DE 1.000.000 CONCLUÍDA EM ${totalSec} SEGUNDOS!`);
console.log("------------------------------------------------------------------");
console.log(`Total de Agentes Avaliados: ${TOTAL_AGENTS.toLocaleString()}`);
console.log(`Total de Jornadas de Navegação Testadas: ${totalJourneysTested.toLocaleString()}`);
console.log(`Jornadas Aprovadas com Sucesso: ${successfulJourneys.toLocaleString()} (${((successfulJourneys / totalJourneysTested) * 100).toFixed(2)}%)`);
console.log(`Acesso Direto em 1 Passo (Zero Atrito): ${singleStepDirectAccessCount.toLocaleString()} (${((singleStepDirectAccessCount / totalJourneysTested) * 100).toFixed(2)}%)`);
console.log(`Quedas em Fallback Indesejado (Travamento BFS/DFS): ${fallbackDetections}`);
console.log(`Anomalias de Descanso (task=rest no Workspace): ${restRedirectionAnomalies}`);
console.log("------------------------------------------------------------------");

console.log("\nDistribuição Cognitiva Real dos 1.000.000 de Alunos:");
console.table(levelDistribution);

console.log("Distribuição por Meta dos 1.000.000 de Alunos:");
console.table(distributionByGoal);

if (Object.keys(errorsByTopic).length > 0) {
  console.log("\nTópicos que sofreram fallback:");
  console.table(errorsByTopic);
}

// Salva relatório executivo
const reportPath = path.resolve(__dirname, "../../.runtime/simulation_1m_students_report.json");
fs.writeFileSync(
  reportPath,
  JSON.stringify(
    {
      totalAgents: TOTAL_AGENTS,
      totalJourneysTested,
      successfulJourneys,
      successRate: ((successfulJourneys / totalJourneysTested) * 100).toFixed(2) + "%",
      singleStepDirectAccessRate: ((singleStepDirectAccessCount / totalJourneysTested) * 100).toFixed(2) + "%",
      fallbackDetections,
      restRedirectionAnomalies,
      executionTimeSeconds: totalSec,
      throughputJourneysPerSecond: Math.round(totalJourneysTested / parseFloat(totalSec)),
      levelDistribution,
      distributionByGoal,
    },
    null,
    2
  ),
  "utf-8"
);
console.log(`\n✓ Relatório consolidado de 1 Milhão de Agentes salvo em: ${reportPath}`);
