import { apiRequest } from "./apiClient";

export interface CanonicalBook {
  id: string;
  title: string;
  authors: string[];
  edition: string;
  publisher: string;
  open_access: boolean;
  url: string;
  overview: string;
  topics: Record<string, string>;
}

export interface DeepGuideSection {
  title: string;
  body: string;
}

export interface DeepGuideExercise {
  prompt: string;
  answer: string;
}

export interface DeepGuide {
  id: string;
  title: string;
  topic_id: string;
  author: string;
  minutes: number;
  prerequisites: string;
  sections: DeepGuideSection[];
  exercises: DeepGuideExercise[];
}

export interface KnowledgeSearchResult {
  id: string;
  title: string;
  heading: string;
  source: string;
  url: string;
  excerpt?: string;
  context_excerpt?: string;
  score?: number;
  tags?: string[];
  topics?: string[];
  track?: string;
}

export interface CuratedResource {
  id?: string;
  title: string;
  publisher?: string;
  summary?: string;
  url: string;
  kind?: string;
  language?: string;
  topics?: string[];
  verification?: string;
}

export interface CollectionItem {
  id: string;
  kind: string;
  title: string;
  payload: any;
  time: string;
  status: "Quero estudar" | "Estudando" | "Estudado";
  note: string;
}

export interface CollectionResponse {
  total: number;
  items: CollectionItem[];
}

export const libraryService = {
  async getBooksAndGuides(): Promise<{ books: CanonicalBook[]; guides: DeepGuide[] }> {
    return apiRequest<{ books: CanonicalBook[]; guides: DeepGuide[] }>("/api/library/books");
  },

  async searchKnowledge(
    query: string,
    topic?: string,
    limit: number = 12
  ): Promise<{
    query: string;
    results: KnowledgeSearchResult[];
    curated_resources: CuratedResource[];
    stats: any;
  }> {
    const params = new URLSearchParams();
    if (query) params.append("q", query);
    if (topic) params.append("topic", topic);
    params.append("limit", limit.toString());
    return apiRequest(`/api/library/search?${params.toString()}`);
  },

  async getDocument(id: string): Promise<{ type: "document" | "guide"; data: any }> {
    return apiRequest(`/api/library/document/${id}`);
  },

  async getCollection(params: {
    profile_id?: string;
    search?: string;
    kind?: string;
    status?: string;
    page?: number;
  }): Promise<CollectionResponse> {
    const searchParams = new URLSearchParams();
    if (params.profile_id) searchParams.append("profile_id", params.profile_id);
    if (params.search) searchParams.append("search", params.search);
    if (params.kind) searchParams.append("kind", params.kind);
    if (params.status) searchParams.append("status", params.status);
    if (params.page) searchParams.append("page", params.page.toString());

    return apiRequest(`/api/library/collection?${searchParams.toString()}`);
  },

  async saveState(payload: {
    profile_id?: string;
    item_id: string;
    status: "Quero estudar" | "Estudando" | "Estudado";
    note?: string;
  }): Promise<{ ok: boolean; message: string }> {
    return apiRequest("/api/library/state", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async saveResource(payload: {
    profile_id?: string;
    resource: {
      title: string;
      url: string;
      summary?: string;
      kind?: string;
    };
  }): Promise<{ ok: boolean; id: string; message: string }> {
    return apiRequest("/api/library/save-resource", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
};
