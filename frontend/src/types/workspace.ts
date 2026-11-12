export type ReaderViewMode = "article" | "slides" | "whiteboard";

export interface StudySection {
  id: string;
  title: string;
  content: string;
  hasMermaid?: boolean;
  hasLatex?: boolean;
}

export interface StudyLesson {
  id: string;
  topicId: string;
  topicTitle: string;
  title: string;
  subtitle?: string;
  summary: string;
  sections: StudySection[];
  estimatedReadingMinutes: number;
  totalCharacters: number;
  lastReadParagraphId?: string;
}

export interface ContextualSelection {
  text: string;
  rangeRect: DOMRect | null;
  sectionId?: string;
}

export type ComponentStatus = "empty" | "loading" | "streaming" | "active" | "error";
