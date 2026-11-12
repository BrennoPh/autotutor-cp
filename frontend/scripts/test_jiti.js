const createJITI = require("jiti");
const jiti = createJITI(__filename, {
  alias: {
    "@": require("path").resolve(__dirname, "../src"),
  },
});

const { evaluateDiagnostic, generateCustomTrack, generateStudySchedule, resolveTaskActionUrl } = jiti("../src/core/adaptiveRoadmapEngine.ts");
console.log("JITI loaded adaptiveRoadmapEngine successfully!");

const sampleProfile = {
  userId: "student-1",
  hasCompletedOnboarding: true,
  targetGoal: "graphs",
  availableHoursPerDay: 1,
  activeDaysOfWeek: [1, 2, 3, 4, 5],
  preferredLanguage: "cpp",
  diagnosticResult: {
    score: 60,
    entryLevel: "Intermediário",
    confidence: "alta",
    strongTopics: ["Análise Assintótica e Complexidade"],
    gapTopics: ["Recursão e Pilha de Execução", "Fila (Queue) e Invariante de Camadas da BFS"],
    evaluatedAt: new Date().toISOString(),
    answers: {},
  },
};

const track = generateCustomTrack(sampleProfile);
console.log("Track generated:", track.title, "Milestones:", track.milestones.length);

const schedule = generateStudySchedule(track, sampleProfile, new Date());
console.log("Schedule generated:", schedule.length, "tasks");
console.log("Sample task URL:", resolveTaskActionUrl(schedule[0]));
