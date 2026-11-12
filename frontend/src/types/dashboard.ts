export interface DailyStep {
  id: string;
  type: "theory" | "problem" | "review";
  title: string;
  durationMinutes: number;
  completed: boolean;
  url: string;
}

export interface ResumeSession {
  trackId: string;
  trackName: string;
  moduleTitle: string;
  lessonId: string;
  lessonTitle: string;
  progressPercent: number;
  estimatedMinutesToFinish: number;
  lastCheckpointLabel: string;
  nextActionType?: "theory" | "problem" | "review";
  actionUrl?: string;
  dailySequence?: DailyStep[];
}

export interface DailyGoalStreak {
  streakDays: number;
  targetMinutesToday: number;
  completedMinutesToday: number;
  flashcardsGoal: number;
  flashcardsDoneToday: number;
  consistencyScore: number;
}

export interface ActiveTrack {
  id: string;
  title: string;
  subject: string;
  retentionRate: number;
  difficultyTag: "Iniciante" | "Intermediário" | "Avançado";
  completedModules: number;
  totalModules: number;
}

export interface WeakPointSuggestion {
  id: string;
  topicId: string;
  topicTitle: string;
  accuracyRate: number;
  insight: string;
  suggestedActionLabel: string;
}
