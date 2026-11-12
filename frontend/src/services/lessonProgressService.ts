import { apiRequest } from "./apiClient";

export const COMPLETED_LESSONS_STORAGE_KEY = "autotutor_completed_lessons";

export interface NextStepAction {
  type: "lesson" | "problem";
  id: string;
  title: string;
  url: string;
}

export const lessonProgressService = {
  getCompletedLessons(): string[] {
    if (typeof window === "undefined") return [];
    try {
      const stored = localStorage.getItem(COMPLETED_LESSONS_STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        return Array.isArray(parsed) ? parsed : [];
      }
      return [];
    } catch {
      return [];
    }
  },

  isLessonCompleted(lessonId: string): boolean {
    if (!lessonId) return false;
    const completed = this.getCompletedLessons();
    return completed.includes(lessonId) || completed.includes(lessonId.toLowerCase());
  },

  async toggleLessonCompletion(
    lessonId: string,
    forceState?: boolean,
    targetTaskType?: "theory" | "problem" | "review"
  ): Promise<{ completed: boolean; completedLessons: string[] }> {
    if (!lessonId || typeof window === "undefined") {
      return { completed: false, completedLessons: [] };
    }

    const currentList = this.getCompletedLessons();
    const alreadyCompleted = currentList.includes(lessonId) || currentList.includes(lessonId.toLowerCase());
    const nextState = forceState !== undefined ? forceState : !alreadyCompleted;

    let updatedList: string[];
    if (nextState) {
      updatedList = Array.from(new Set([...currentList, lessonId]));
    } else {
      updatedList = currentList.filter(
        (id) => id !== lessonId && id.toLowerCase() !== lessonId.toLowerCase()
      );
    }

    // 1. Salva no localStorage com resposta instantânea
    try {
      localStorage.setItem(COMPLETED_LESSONS_STORAGE_KEY, JSON.stringify(updatedList));
    } catch (e) {
      console.warn("Falha ao salvar lições concluídas no localStorage:", e);
    }

    // 2. Sincroniza tarefas do calendário com isolamento estrito por tipo
    try {
      const storedTasks = localStorage.getItem("autotutor_scheduled_tasks");
      if (storedTasks) {
        const tasks = JSON.parse(storedTasks);
        let taskModified = false;
        const desiredType = targetTaskType || "theory";

        const updatedTasks = tasks.map((t: any) => {
          const actionUrl = t.actionUrl || "";
          const taskType = t.taskType || "theory";

          // Isolamento: Se estamos completando uma lição de teoria, JAMAIS marcar
          // tarefas de prática (problem) ou de revisão de flashcards (review) em cascata!
          if (desiredType === "theory" && (taskType === "problem" || taskType === "review")) {
            return t;
          }

          const matchesLessonUrl =
            actionUrl.includes(`lesson=${lessonId}`) ||
            actionUrl.includes(`lesson=${encodeURIComponent(lessonId)}`);
          const matchesProblemUrl =
            actionUrl.includes(`problem=${lessonId}`) ||
            actionUrl.includes(`problem=${encodeURIComponent(lessonId)}`);

          const isDirectMatch = t.id === lessonId;
          const isTopicMatch = t.topicId === lessonId && taskType === desiredType;
          const isUrlMatch =
            (taskType === "theory" && matchesLessonUrl) ||
            (taskType === "problem" && matchesProblemUrl);

          if (isDirectMatch || isTopicMatch || isUrlMatch) {
            taskModified = true;
            return {
              ...t,
              status: nextState ? "completed" : "pending",
              completedAt: nextState ? new Date().toISOString() : undefined,
            };
          }
          return t;
        });

        if (taskModified) {
          localStorage.setItem("autotutor_scheduled_tasks", JSON.stringify(updatedTasks));
        }
      }
    } catch (e) {
      console.warn("Falha ao sincronizar tarefas agendadas com a lição:", e);
    }

    // 3. Sincroniza módulos específicos da trilha do usuário (sem marcar outros módulos)
    try {
      const storedTrack = localStorage.getItem("autotutor_user_track");
      if (storedTrack) {
        const track = JSON.parse(storedTrack);
        let modModified = false;
        const list = track.milestones || track.modules;
        if (Array.isArray(list)) {
          list.forEach((m: any) => {
            const matchesId = m.id === lessonId || m.id?.toLowerCase() === lessonId.toLowerCase();
            const matchesTopic = (m.topicId === lessonId || m.topicId?.toLowerCase() === lessonId.toLowerCase()) && !m.id;
            if (matchesId || matchesTopic) {
              m.completed = nextState;
              modModified = true;
            }
          });
          if (modModified) {
            localStorage.setItem("autotutor_user_track", JSON.stringify(track));
          }
        }
      }

      // Sincroniza também trilhas customizadas
      const storedCustom = localStorage.getItem("autotutor_custom_tracks");
      if (storedCustom) {
        const customTracks = JSON.parse(storedCustom);
        let anyModified = false;
        if (Array.isArray(customTracks)) {
          customTracks.forEach((ct: any) => {
            const modList = ct.modules || ct.milestones;
            if (Array.isArray(modList)) {
              modList.forEach((m: any) => {
                if (m.id === lessonId || m.id?.toLowerCase() === lessonId.toLowerCase()) {
                  m.completed = nextState;
                  anyModified = true;
                }
              });
            }
          });
          if (anyModified) {
            localStorage.setItem("autotutor_custom_tracks", JSON.stringify(customTracks));
          }
        }
      }
    } catch (e) {
      console.warn("Falha ao sincronizar módulos da trilha do usuário:", e);
    }

    // 4. Dispara evento customizado para reatividade em tempo real em todas as telas
    window.dispatchEvent(
      new CustomEvent("lesson-completion-changed", {
        detail: {
          lessonId,
          completed: nextState,
          completedLessons: updatedList,
          taskType: targetTaskType || "theory",
        },
      })
    );

    // 5. Persiste assincronamente no backend SQLite
    apiRequest("/api/progress/lessons/complete", {
      method: "POST",
      body: JSON.stringify({
        lesson_id: lessonId,
        completed: nextState,
      }),
    }).catch((err) => {
      if (typeof window !== "undefined" && (window as any).__DEBUG_API__) {
        console.warn("Sincronização com backend:", err);
      }
    });

    return { completed: nextState, completedLessons: updatedList };
  },

  getNextStepForLesson(
    currentLessonId: string,
    currentTopicId?: string,
    allLessons?: Array<{ id: string; title: string; topicId?: string }>,
    trackLessons?: Array<{ id: string; title: string; topicId?: string }>
  ): NextStepAction | null {
    // 1. Se trackLessons explícitas forem fornecidas, usamos a ordem estrita dessa trilha
    let targetList = trackLessons;

    // 2. Se não fornecidas, tentamos isolar as lições pertencentes à trilha ativa (currentTopicId)
    if ((!targetList || targetList.length === 0) && allLessons && allLessons.length > 0 && currentTopicId) {
      const topicMatches = allLessons.filter(
        (l) => l.topicId === currentTopicId || l.topicId?.toLowerCase() === currentTopicId.toLowerCase()
      );
      if (topicMatches.length > 0) {
        targetList = topicMatches;
      }
    }

    // 3. Se ainda não temos lista específica, verificamos se a trilha ativa no localStorage possui módulos
    if (!targetList || targetList.length === 0) {
      if (typeof window !== "undefined") {
        try {
          const userTrackStr = localStorage.getItem("autotutor_user_track");
          if (userTrackStr) {
            const userTrack = JSON.parse(userTrackStr);
            const mList = userTrack.milestones || userTrack.modules;
            if (Array.isArray(mList) && mList.length > 0) {
              const matched = mList.some(
                (m: any) => m.id === currentLessonId || m.topicId === currentLessonId
              );
              if (matched) {
                targetList = mList.map((m: any, idx: number) => ({
                  id: m.id || m.topicId || `mod-${idx}`,
                  title: m.title,
                  topicId: userTrack.id,
                }));
              }
            }
          }
        } catch {
          // ignore
        }
      }
    }

    // Se temos uma lista de lições da trilha:
    if (targetList && targetList.length > 0) {
      const currentIndex = targetList.findIndex(
        (l) => l.id === currentLessonId || l.id.toLowerCase() === currentLessonId.toLowerCase()
      );

      // Se houver próximo módulo dentro da mesma trilha, avança para ele
      if (currentIndex >= 0 && currentIndex + 1 < targetList.length) {
        const nextLesson = targetList[currentIndex + 1];
        const effectiveTopic = currentTopicId || nextLesson.topicId || "geral";
        return {
          type: "lesson",
          id: nextLesson.id,
          title: nextLesson.title,
          url: `/workspace?topic=${encodeURIComponent(effectiveTopic)}&lesson=${encodeURIComponent(nextLesson.id)}&mode=reader`,
        };
      }

      // Se for a última aula da trilha, avança para o desafio prático na Arena
      const arenaTopic = currentTopicId || targetList[0]?.topicId || "grafos";
      return {
        type: "problem",
        id: "practice",
        title: "Praticar Desafio no Juiz de Código",
        url: `/workspace?topic=${encodeURIComponent(arenaTopic)}&problem=${encodeURIComponent(currentLessonId)}&mode=arena`,
      };
    }

    // 4. Fallback resiliente usando allLessons (mas mantendo a trava para não pular de trilha)
    if (allLessons && allLessons.length > 0) {
      const currentIndex = allLessons.findIndex(
        (l) => l.id === currentLessonId || l.id.toLowerCase() === currentLessonId.toLowerCase()
      );

      if (currentIndex >= 0 && currentIndex + 1 < allLessons.length) {
        const current = allLessons[currentIndex];
        const next = allLessons[currentIndex + 1];

        // Só avança para a próxima se for do MESMO tópico/trilha
        if (current.topicId && next.topicId && current.topicId === next.topicId) {
          return {
            type: "lesson",
            id: next.id,
            title: next.title,
            url: `/workspace?topic=${encodeURIComponent(next.topicId)}&lesson=${encodeURIComponent(next.id)}&mode=reader`,
          };
        }
      }
    }

    // Último recurso: Desafio de Prática na Arena para o tópico atual
    return {
      type: "problem",
      id: "practice",
      title: "Praticar Desafio no Juiz de Código",
      url: `/workspace?topic=${encodeURIComponent(currentTopicId || "grafos")}&problem=${encodeURIComponent(currentLessonId)}&mode=arena`,
    };
  },
};
