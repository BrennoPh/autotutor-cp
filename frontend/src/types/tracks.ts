export interface TrackModule {
  id: string;
  title: string;
  description: string;
  estimatedMinutes: number;
  completed: boolean;
  lessons: string[];
}

export interface TrackMetadata {
  id: string;
  title: string;
  subject: string;
  difficulty: "Iniciante" | "Intermediário" | "Avançado";
  retentionRate: number;
  description: string;
  modules: TrackModule[];
  isCustom?: boolean;
  createdAt?: string;
}
