/**
 * Student Journey Simulator: Validação de Conclusão de Aulas e Avanço na Trilha
 * 
 * Simula as 4 personas canônicas do ecossistema AutoTutor CP:
 * 1. 🟢 Novice Artur (Iniciante)
 * 2. 🔵 Veteran Beatriz (Maratonista Sênior)
 * 3. 🟡 Confused Caio (Intermediário com Gaps)
 * 4. 🔴 Pentester Diana (Adversarial / Estresse)
 */

const path = require("path");
const fs = require("fs");
const createJITI = require("jiti");

// Mock de localStorage e Window CustomEvent para execução isomórfica em Node.js
class MockLocalStorage {
  constructor() {
    this.store = {};
  }
  getItem(key) {
    return this.store[key] || null;
  }
  setItem(key, value) {
    this.store[key] = String(value);
  }
  removeItem(key) {
    delete this.store[key];
  }
  clear() {
    this.store = {};
  }
}

const mockStorage = new MockLocalStorage();
global.window = {
  dispatchEvent: (event) => {},
  location: {
    origin: "http://127.0.0.1:8000",
  },
};
global.localStorage = mockStorage;

const jiti = createJITI(__filename, {
  alias: {
    "@": path.resolve(__dirname, "../src"),
  },
});

const { CURRICULUM_LESSONS } = jiti("../src/data/curriculumLessons.ts");
const { lessonProgressService, COMPLETED_LESSONS_STORAGE_KEY } = jiti("../src/services/lessonProgressService.ts");

function logSection(title) {
  console.log("\n" + "=".repeat(70));
  console.log(`📌 ${title}`);
  console.log("=".repeat(70));
}

function assert(condition, message) {
  if (!condition) {
    console.error(`❌ FALHA: ${message}`);
    process.exit(1);
  }
  console.log(`  ✓ ${message}`);
}

async function runSimulation() {
  logSection("INICIANDO SIMULAÇÃO DE JORNADA DE ESTUDANTES SINTÉTICOS");
  const startTime = Date.now();

  // -------------------------------------------------------------
  // 1. NOVICE ARTUR (Iniciante)
  // -------------------------------------------------------------
  logSection("1. 🟢 NOVICE ARTUR - Estudo Inicial e Avanço de Lição");
  mockStorage.clear();

  const arturLessonId = "bfs_dfs_foundations";
  const arturTopicId = "grafos";

  assert(!lessonProgressService.isLessonCompleted(arturLessonId), "Artur inicia com lição BFS como Pendente");

  console.log("  → Artur estuda a teoria de BFS e clica em [Concluir Aula]");
  const arturResult1 = await lessonProgressService.toggleLessonCompletion(arturLessonId, true);
  assert(arturResult1.completed === true, "toggleLessonCompletion retornou completed = true");
  assert(lessonProgressService.isLessonCompleted(arturLessonId), "Artur agora possui BFS marcada como Concluída");

  // Artur consulta o próximo passo
  const arturNextStep = lessonProgressService.getNextStepForLesson(arturLessonId, arturTopicId, CURRICULUM_LESSONS);
  assert(arturNextStep !== null, "Artur recebe sugestão automática do próximo passo na trilha");
  assert(arturNextStep.type === "lesson", "Próximo passo é a lição teórica subsequente de Grafos");
  assert(arturNextStep.id === "dijkstra_shortest_path", `Próxima lição calculada com precisão: ${arturNextStep.id}`);
  assert(arturNextStep.url.includes("lesson=dijkstra_shortest_path"), `URL de avanço direta gerada: ${arturNextStep.url}`);
  console.log(`  → Artur avança com 1 clique para: ${arturNextStep.title} (${arturNextStep.url})`);

  // -------------------------------------------------------------
  // 2. VETERAN BEATRIZ (Maratonista Sênior)
  // -------------------------------------------------------------
  logSection("2. 🔵 VETERAN BEATRIZ - Conclusão Completa de Trilha e Desafio na Arena");
  mockStorage.clear();

  // Beatriz estuda trilha de Programação Dinâmica
  const beatrizLessons = [
    { id: "dp_knapsack_foundations", title: "Mochila 0/1", topicId: "dp" },
    { id: "dp_lis", title: "Maior Subsequência Crescente (LIS)", topicId: "dp" },
    { id: "dp_bitmask", title: "DP com Máscaras de Bits", topicId: "dp" },
  ];

  console.log("  → Beatriz conclui Módulo 1 (Mochila 0/1)");
  await lessonProgressService.toggleLessonCompletion("dp_knapsack_foundations", true);
  let comp1 = lessonProgressService.getCompletedLessons();
  let pct1 = Math.round((comp1.filter(id => beatrizLessons.some(l => l.id === id)).length / beatrizLessons.length) * 100);
  assert(pct1 === 33, `Progresso da trilha recalculado dinamicamente: ${pct1}%`);

  const beatrizStep1 = lessonProgressService.getNextStepForLesson("dp_knapsack_foundations", "dp", beatrizLessons);
  assert(beatrizStep1.id === "dp_lis", "Beatriz é direcionada para o Módulo 2 (LIS)");

  console.log("  → Beatriz conclui Módulo 2 (LIS)");
  await lessonProgressService.toggleLessonCompletion("dp_lis", true);
  let comp2 = lessonProgressService.getCompletedLessons();
  let pct2 = Math.round((comp2.filter(id => beatrizLessons.some(l => l.id === id)).length / beatrizLessons.length) * 100);
  assert(pct2 === 67, `Progresso da trilha recalculado dinamicamente: ${pct2}%`);

  console.log("  → Beatriz conclui Módulo 3 Final (DP com Máscaras de Bits)");
  await lessonProgressService.toggleLessonCompletion("dp_bitmask", true);
  let comp3 = lessonProgressService.getCompletedLessons();
  let pct3 = Math.round((comp3.filter(id => beatrizLessons.some(l => l.id === id)).length / beatrizLessons.length) * 100);
  assert(pct3 === 100, `Trilha concluída em 100%: ${pct3}%`);

  const beatrizFinalStep = lessonProgressService.getNextStepForLesson("dp_bitmask", "dp", beatrizLessons);
  assert(beatrizFinalStep.type === "problem", "Ao concluir o último módulo teórico, CTA muda para Desafio Prático na Arena");
  assert(beatrizFinalStep.url.includes("mode=arena"), `URL redireciona diretamente para Arena com juiz: ${beatrizFinalStep.url}`);
  console.log(`  → Beatriz é guiada para a Arena: ${beatrizFinalStep.title} (${beatrizFinalStep.url})`);

  // -------------------------------------------------------------
  // 3. CONFUSED CAIO (Intermediário com Gaps)
  // -------------------------------------------------------------
  logSection("3. 🟡 CONFUSED CAIO - Toggle Bidirecional, Idempotência e Zero Duplicações");
  mockStorage.clear();

  const caioLessonId = "recursion_foundations";

  console.log("  → Caio marca 'recursion_foundations' como Concluída");
  await lessonProgressService.toggleLessonCompletion(caioLessonId, true);
  assert(lessonProgressService.isLessonCompleted(caioLessonId), "Status = Concluída");

  console.log("  → Caio clica acidentalmente e desmarca para Pendente");
  await lessonProgressService.toggleLessonCompletion(caioLessonId, false);
  assert(!lessonProgressService.isLessonCompleted(caioLessonId), "Status = Pendente");

  console.log("  → Caio clica novamente em Concluir");
  await lessonProgressService.toggleLessonCompletion(caioLessonId, true);
  assert(lessonProgressService.isLessonCompleted(caioLessonId), "Status = Concluída novamente");

  console.log("  → Caio chama toggle sem forceState (modo alternância direta)");
  await lessonProgressService.toggleLessonCompletion(caioLessonId);
  assert(!lessonProgressService.isLessonCompleted(caioLessonId), "Alternou para Pendente");
  await lessonProgressService.toggleLessonCompletion(caioLessonId);
  assert(lessonProgressService.isLessonCompleted(caioLessonId), "Alternou para Concluída");

  const caioList = lessonProgressService.getCompletedLessons();
  const occurrences = caioList.filter(id => id === caioLessonId).length;
  assert(occurrences === 1, `Idempotência comprovada: ID aparece exatamente 1 vez na lista (${occurrences})`);

  // -------------------------------------------------------------
  // 4. PENTESTER DIANA (Adversarial / Teste de Estresse)
  // -------------------------------------------------------------
  logSection("4. 🔴 PENTESTER DIANA - Resiliência a Payloads Inválidos e Concorrência");
  
  console.log("  → Diana testa entradas nulas, vazias e corrompidas");
  const rEmpty = await lessonProgressService.toggleLessonCompletion("");
  assert(rEmpty.completed === false, "String vazia tratada com segurança (completed: false)");

  const rNull = await lessonProgressService.toggleLessonCompletion(null);
  assert(rNull.completed === false, "Valor null tratado com segurança sem quebra de runtime");

  const rUndefined = await lessonProgressService.toggleLessonCompletion(undefined);
  assert(rUndefined.completed === false, "Valor undefined tratado com segurança sem quebra de runtime");

  console.log("  → Diana dispara 100 requisições simultâneas de toggle para estressar o armazenamento local");
  const stressPromises = [];
  for (let i = 0; i < 100; i++) {
    stressPromises.push(lessonProgressService.toggleLessonCompletion(`stress_lesson_${i % 10}`));
  }
  await Promise.all(stressPromises);
  const stressList = lessonProgressService.getCompletedLessons();
  assert(Array.isArray(stressList), "Lista de lições completas permanece íntegra como Array");
  const uniqueCount = new Set(stressList).size;
  assert(uniqueCount === stressList.length, `Nenhuma duplicação em alta concorrência: ${uniqueCount} IDs únicos`);

  // -------------------------------------------------------------
  // RELATÓRIO FINAL
  // -------------------------------------------------------------
  const duration = Date.now() - startTime;
  logSection(`RESULTADO DA SIMULAÇÃO: 100% SUCESSO (${duration}ms)`);
  console.log("✨ Todas as personas sintéticas completaram suas jornadas com conformidade pedagógica total:");
  console.log("   - Artur: Conclusão de aula e transição guiada para a próxima aula");
  console.log("   - Beatriz: Recalibração de porcentagem da trilha e avanço para desafio na Arena");
  console.log("   - Caio: Idempotência garantida em alternância de status");
  console.log("   - Diana: Tratamento seguro de exceções e resiliência em rajada concorrente");
}

runSimulation().catch(err => {
  console.error("Erro fatal na simulação:", err);
  process.exit(1);
});
