export type UrgencyLevel = "urgent" | "due-today" | "upcoming" | "mastered";

export interface RepetitionItem {
  id: string;
  topicId: string;
  topicTitle: string;
  category: string;
  retentionRate: number; // 0 to 100
  lastReviewedAt: string;
  nextReviewDue: string;
  intervalDays: number;
  repetitionsCount: number;
  urgency: UrgencyLevel;
  flashcardsCount: number;
}

export interface TopicMastery {
  topicId: string;
  topicName: string;
  category: string;
  masteryScore: number; // 0 - 100
  questionsSolved: number;
  totalQuestions: number;
  lastPracticed: string;
  trend: "up" | "stable" | "down";
}

export interface EbbinghausCurvePoint {
  day: number;
  withoutReviewRetention: number; // %
  withReviewRetention: number; // %
}
