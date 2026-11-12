export type TargetGoal =
  | "foundations"
  | "graphs"
  | "dp"
  | "obi"
  | "icpc"
  | "interviews";

export type PreferredLanguage = "cpp" | "python" | "java";

export type EntryLevel = "Iniciante" | "Intermediário" | "Avançado" | "Expert";

export interface DiagnosticQuestion {
  id: string;
  topic: string;
  difficulty: "basic" | "intermediate" | "advanced";
  question: string;
  codeSnippet?: string;
  options: {
    id: string;
    text: string;
    isCorrect: boolean;
  }[];
  explanation: string;
}

export interface DiagnosticResult {
  score: number; // 0 a 100
  entryLevel: EntryLevel;
  confidence: "baixa" | "média" | "alta";
  strongTopics: string[];
  gapTopics: string[];
  evaluatedAt: string;
  answers: Record<string, string>; // questionId -> optionId
}

export interface UserAssessmentProfile {
  userId: string;
  hasCompletedOnboarding: boolean;
  targetGoal: TargetGoal;
  targetExamDate?: string;
  availableHoursPerDay: number;
  activeDaysOfWeek: number[]; // 0: Dom, 1: Seg, 2: Ter, 3: Qua, 4: Qui, 5: Sex, 6: Sab
  preferredLanguage: PreferredLanguage;
  diagnosticResult?: DiagnosticResult;
}

export interface TrackMilestone {
  weekNumber: number;
  topicId: string;
  title: string;
  category: string;
  isPrerequisiteRefinement: boolean;
  estimatedHours: number;
  keyConcepts: string[];
  id?: string;
  completed?: boolean;
}

export interface CustomTrack {
  id: string;
  title: string;
  description: string;
  totalWeeks: number;
  targetGoal: TargetGoal;
  entryLevel: EntryLevel;
  milestones: TrackMilestone[];
}

export type TaskType = "theory" | "problem" | "review" | "rest";
export type TaskStatus = "pending" | "completed" | "overdue" | "rest";

export interface ScheduledTask {
  id: string;
  date: string; // YYYY-MM-DD
  topicId: string;
  title: string;
  description: string;
  taskType: TaskType;
  status: TaskStatus;
  estimatedMinutes: number;
  completedAt?: string;
  rescheduledFrom?: string;
  actionUrl?: string;
}
