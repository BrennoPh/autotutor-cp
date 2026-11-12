/**
 * Rigorous Full-System Student Audit Engine
 * AutoTutor CP: Auditoria Completa de Integridade Pedagógica, Roteamento e Progresso
 */
const path = require("path");
const fs = require("fs");
const createJITI = require("jiti");

// Mock isomórfico para execução em Node.js
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
  location: { origin: "http://127.0.0.1:8000" },
};
global.localStorage = mockStorage;

const jiti = createJITI(__filename, {
  alias: {
    "@": path.resolve(__dirname, "../src"),
  },
});

const { CURRICULUM_LESSONS } = jiti("../src/data/curriculumLessons.ts");
const { lessonProgressService } = jiti("../src/services/lessonProgressService.ts");
const {
  evaluateDiagnostic,
  generateCustomTrack,
  generateStudySchedule,
  resolveTaskActionUrl,
  DIAGNOSTIC_QUESTIONS,
} = jiti("../src/core/adaptiveRoadmapEngine.ts");

console.log("==================================================================");
console.log("🔍 AUDITORIA RIGOROSA DO SISTEMA & SIMULAÇÃO MULTI-PERSONA");
console.log("==================================================================\n");

let passedChecks = 0;
let totalChecks = 0;

function check(condition, desc) {
  totalChecks++;
  if (!condition) {
    console.error(`❌ FALHA: ${desc}`);
    process.exit(1);
  }
  passedChecks++;
}

// -------------------------------------------------------------
// 1. AUDITORIA ESTRUTURAL DAS LIÇÕES CANÔNICAS
// -------------------------------------------------------------
console.log("1. Auditando Catálogo de Lições Canônicas (curriculumLessons.ts)...");
check(Array.isArray(CURRICULUM_LESSONS) && CURRICULUM_LESSONS.length >= 7, "Catálogo possui lições canônicas suficientes");

const lessonIds = new Set();
for (const lesson of CURRICULUM_LESSONS) {
  check(typeof lesson.id === "string" && lesson.id.trim().length > 0, `Lição possui ID válido: ${lesson.id}`);
  check(!lessonIds.has(lesson.id), `ID de lição é único: ${lesson.id}`);
  lessonIds.add(lesson.id);

  check(typeof lesson.title === "string" && lesson.title.length > 3, `Título válido em: ${lesson.id}`);
  check(typeof lesson.topicId === "string" && lesson.topicId.length > 0, `TopicId válido em: ${lesson.id}`);
  check(Array.isArray(lesson.sections) && lesson.sections.length > 0, `Lição possui seções: ${lesson.id}`);

  // Checa se o próximo passo é determinístico e não quebra
  const nextStep = lessonProgressService.getNextStepForLesson(lesson.id, lesson.topicId, CURRICULUM_LESSONS);
  check(nextStep !== null && typeof nextStep.url === "string", `Próximo passo resolvido para: ${lesson.id}`);
}
console.log(`✓ ${CURRICULUM_LESSONS.length} lições canônicas 100% íntegras.\n`);

// -------------------------------------------------------------
// 2. AUDITORIA DE REGRAS DE AVALIAÇÃO DIAGNÓSTICA & COMBINATÓRIA
// -------------------------------------------------------------
console.log("2. Auditando Motor Diagnóstico Combinatório (evaluateDiagnostic)...");
const totalCombinations = Math.pow(4, 5); // 1024 combinações de respostas
let noviceCount = 0;
let intermediateCount = 0;
let advancedCount = 0;

for (let bitPattern = 0; bitPattern < totalCombinations; bitPattern++) {
  const answers = {};
  let temp = bitPattern;
  DIAGNOSTIC_QUESTIONS.forEach((q) => {
    const optIndex = temp % 4;
    temp = Math.floor(temp / 4);
    answers[q.id] = q.options[optIndex].id;
  });

  const res = evaluateDiagnostic(answers);
  const correctCount = res.strongTopics.length;
  check(res.score >= 0 && res.score <= 100, "Score no intervalo 0..100");
  check(correctCount >= 0 && correctCount <= 5, "Acertos no intervalo 0..5");
  check(res.strongTopics.length + res.gapTopics.length === 5, "Soma de fortes + gaps sempre igual a 5");

  if (res.entryLevel === "Iniciante") noviceCount++;
  else if (res.entryLevel === "Intermediário") intermediateCount++;
  else if (res.entryLevel === "Avançado") advancedCount++;
}
check(noviceCount > 0 && intermediateCount > 0 && advancedCount > 0, "Distribuição diagnóstica balanceada");
console.log(`✓ 1.024 combinações diagnósticas testadas com invariantes perfeitos (Iniciantes: ${noviceCount}, Intermediários: ${intermediateCount}, Avançados: ${advancedCount}).\n`);

// -------------------------------------------------------------
// 3. AUDITORIA DE CALENDÁRIO COM CONDIÇÕES DE BORDA
// -------------------------------------------------------------
console.log("3. Auditando Agendador de Cronograma com Entradas Limítrofes...");
const edgeProfiles = [
  { userId: "u1", activeDaysOfWeek: [], availableHoursPerDay: 1, targetGoal: "graphs" },
  { userId: "u2", activeDaysOfWeek: [0, 1, 2, 3, 4, 5, 6], availableHoursPerDay: 0.5, targetGoal: "dp" },
  { userId: "u3", activeDaysOfWeek: [1], availableHoursPerDay: 4, targetGoal: "foundations" },
  { userId: "u4", activeDaysOfWeek: [6, 0], availableHoursPerDay: 2, targetGoal: "icpc" },
];

for (const prof of edgeProfiles) {
  const track = generateCustomTrack(prof);
  check(track && track.milestones && track.milestones.length > 0, `Trilha gerada para perfil extremo: ${prof.userId}`);

  const schedule = generateStudySchedule(track, prof, new Date());
  check(Array.isArray(schedule) && schedule.length > 0, `Cronograma gerado sem laço infinito: ${prof.userId}`);

  // Garante que nenhuma URL de tarefa contenha undefined ou anomalias
  for (const task of schedule) {
    const url = resolveTaskActionUrl(task);
    check(!url.includes("undefined") && !url.includes("null"), `URL limpa gerada: ${url}`);
    if (task.taskType === "rest") {
      check(url === "/calendar", `Tarefa de descanso redireciona para /calendar: ${url}`);
    }
  }
}
console.log("✓ Todos os perfis limítrofes agendados sem exceções ou loops infinitos.\n");

// -------------------------------------------------------------
// 4. SIMULAÇÃO DE PROGRESSÃO DE 10.000 ALUNOS COMPLETOS
// -------------------------------------------------------------
console.log("4. Executando Simulação Massiva de Progressão (10.000 Estudantes)...");
const t0 = Date.now();
for (let s = 0; s < 10000; s++) {
  mockStorage.clear();
  const studentTrack = CURRICULUM_LESSONS.slice(0, 4);

  // Estudante conclui lição por lição
  for (let idx = 0; idx < studentTrack.length; idx++) {
    const currentLesson = studentTrack[idx];
    lessonProgressService.toggleLessonCompletion(currentLesson.id, true);
    check(lessonProgressService.isLessonCompleted(currentLesson.id), `Lição concluída pelo estudante ${s}`);

    const next = lessonProgressService.getNextStepForLesson(currentLesson.id, currentLesson.topicId, studentTrack);
    if (idx < studentTrack.length - 1) {
      check(next.type === "lesson" && next.id === studentTrack[idx + 1].id, `Próximo passo é a próxima aula (${next.id})`);
    } else {
      check(next.type === "problem", "Ao término da trilha, próximo passo é o desafio na Arena");
    }
  }

  // Verifica cálculo de porcentagem
  const comp = lessonProgressService.getCompletedLessons();
  const pct = Math.round((comp.filter((id) => studentTrack.some((l) => l.id === id)).length / studentTrack.length) * 100);
  check(pct === 100, `Estudante ${s} atingiu 100% de conclusão`);
}
const elapsed = ((Date.now() - t0) / 1000).toFixed(2);
console.log(`✓ 10.000 estudantes progrediram por todas as lições em ${elapsed}s com 100% de acerto.\n`);

console.log("==================================================================");
console.log(`🎉 AUDITORIA CONCLUÍDA COM SUCESSO!`);
console.log(`Total de Asserções Verificadas: ${totalChecks}`);
console.log(`Total de Falhas: 0`);
console.log("==================================================================");
