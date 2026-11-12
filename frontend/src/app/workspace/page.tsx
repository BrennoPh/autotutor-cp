"use client";

import React, { useState, useEffect, useMemo, useRef, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { WorkspaceLayout } from "@/components/workspace/WorkspaceLayout";
import { CURRICULUM_LESSONS, ExtendedLesson } from "@/data/curriculumLessons";
import { BookOpen, Network, Loader2, Sparkles } from "lucide-react";

function parseCustomTrackLessons(track: any): ExtendedLesson[] {
  if (!track || !track.id) return [];

  const mainLesson: ExtendedLesson = {
    id: track.id,
    category: `Personalizada: ${track.subject || track.targetGoal || "Algoritmos"}`,
    topicId: track.id,
    topicTitle: track.title,
    title: track.title,
    subtitle: track.description,
    summary: track.description,
    estimatedReadingMinutes: Math.round(
      ((track.modules || track.milestones || []).reduce(
        (acc: number, m: any) => acc + (m.estimatedMinutes || (m.estimatedHours ? m.estimatedHours * 60 : 30)),
        0
      )) / 2
    ),
    totalCharacters: 3500,
    sections: (track.modules || track.milestones || []).map((m: any, idx: number) => ({
      id: m.id || m.topicId || `mod-${idx}`,
      title: m.title,
      content: `### ${m.title}\n\n${m.description || `Semana ${m.weekNumber || idx + 1}: ${m.category || "Estudo Focado"}`}\n\n**Aulas e Metas Práticas do Módulo:**\n${(m.lessons || m.keyConcepts || []).map((l: string) => `- **${l}**`).join("\n")}\n\n*Tempo estimado sugerido: ${m.estimatedMinutes || (m.estimatedHours ? m.estimatedHours * 60 : 30)} minutos.*`,
    })),
  };

  const moduleLessons: ExtendedLesson[] = (track.modules || track.milestones || []).map((m: any, idx: number) => {
    const modId = m.id || m.topicId || `${track.id}-mod-${idx}`;
    return {
      id: modId,
      category: `${track.title} • Módulo ${idx + 1}`,
      topicId: track.id,
      topicTitle: track.title,
      title: m.title,
      subtitle: m.description || `Módulo focado de ${track.title}`,
      summary: m.description || m.title,
      estimatedReadingMinutes: Math.round(m.estimatedMinutes || (m.estimatedHours ? m.estimatedHours * 60 : 30)),
      totalCharacters: 2200,
      sections: [
        {
          id: `${modId}-sec-1`,
          title: `Fundamentos: ${m.title}`,
          content: `### Conceito Central\n\n${m.description || m.title}\n\n**Tópicos e Conceitos Chave:**\n${(m.lessons || m.keyConcepts || ["Fundamentos do tema", "Aplicações práticas"]).map((c: string) => `- **${c}**`).join("\n")}\n\n*Recomendação pedagógica: Leia os conceitos e resolva os desafios práticos associados no Juiz de Código.*`,
        },
      ],
    };
  });

  return [mainLesson, ...moduleLessons];
}

function resolveLessonFromParams(
  lessonParam: string | null | undefined,
  topicParam: string | null | undefined,
  allLessons: ExtendedLesson[]
): string {
  const cleanLesson = (lessonParam && lessonParam !== "undefined" && lessonParam !== "null") ? lessonParam.trim() : null;
  const cleanTopic = (topicParam && topicParam !== "undefined" && topicParam !== "null") ? topicParam.trim() : null;

  // 1. Tenta correspondência direta por lessonParam (ID exato ou case-insensitive)
  if (cleanLesson) {
    const exactMatch = allLessons.find(
      (l) => l.id === cleanLesson || l.id.toLowerCase() === cleanLesson.toLowerCase()
    );
    if (exactMatch) return exactMatch.id;

    // Tenta encontrar em seções ou títulos
    const sectionMatch = allLessons.find((l) =>
      l.sections.some((s) => s.id === cleanLesson || s.id.toLowerCase() === cleanLesson.toLowerCase())
    );
    if (sectionMatch) return sectionMatch.id;
  }

  // 2. Tenta correspondência direta por topicParam dentro da coleção viva de lições
  if (cleanTopic) {
    const t = cleanTopic.toLowerCase().trim();

    // Prioridade A: Lição com topicId idêntico ou ID de lição igual ao topicParam
    const directTopicMatch = allLessons.find(
      (l) => l.topicId.toLowerCase() === t || l.id.toLowerCase() === t
    );
    if (directTopicMatch) return directTopicMatch.id;

    // Prioridade B: Lição cujo topicTitle ou categoria contenha o tópico
    const textMatch = allLessons.find(
      (l) =>
        l.topicTitle?.toLowerCase().includes(t) ||
        l.category?.toLowerCase().includes(t) ||
        l.title?.toLowerCase().includes(t)
    );
    if (textMatch) return textMatch.id;
  }

  // 3. Se lessonParam foi informado sem correspondência exata, busca por similaridade de título
  if (cleanLesson) {
    const lp = cleanLesson.toLowerCase();
    const partialMatch = allLessons.find(
      (l) => l.title.toLowerCase().includes(lp) || l.subtitle?.toLowerCase().includes(lp)
    );
    if (partialMatch) return partialMatch.id;
  }

  // 4. Fallback final: Primeira aula disponível
  return allLessons[0]?.id || "bfs_dfs_foundations";
}

function loadStoredCustomLessons(): ExtendedLesson[] {
  if (typeof window === "undefined") return [];
  try {
    const allCustom: ExtendedLesson[] = [];
    const stored = localStorage.getItem("autotutor_custom_tracks");
    if (stored) {
      const parsed = JSON.parse(stored);
      parsed.forEach((track: any) => {
        allCustom.push(...parseCustomTrackLessons(track));
      });
    }

    const storedUserTrack = localStorage.getItem("autotutor_user_track");
    if (storedUserTrack) {
      const parsedUserTrack = JSON.parse(storedUserTrack);
      allCustom.push(...parseCustomTrackLessons(parsedUserTrack));
    }

    return allCustom;
  } catch {
    return [];
  }
}

function WorkspaceContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [customLessons, setCustomLessons] = useState<ExtendedLesson[]>(loadStoredCustomLessons);

  useEffect(() => {
    setCustomLessons(loadStoredCustomLessons());
  }, []);

  const allLessons = useMemo(() => {
    return [...CURRICULUM_LESSONS, ...customLessons];
  }, [customLessons]);

  const [selectedLessonId, setSelectedLessonId] = useState<string>(() => {
    const initialLessons = [...CURRICULUM_LESSONS, ...loadStoredCustomLessons()];
    return resolveLessonFromParams(
      searchParams.get("lesson"),
      searchParams.get("topic"),
      initialLessons
    );
  });

  useEffect(() => {
    const lessonParam = searchParams.get("lesson");
    const topicParam = searchParams.get("topic");

    if (lessonParam || topicParam) {
      const resolved = resolveLessonFromParams(lessonParam, topicParam, allLessons);
      if (resolved && resolved !== selectedLessonId) {
        setSelectedLessonId(resolved);
      }
    }
  }, [searchParams, allLessons, selectedLessonId]);

  const activeLesson: ExtendedLesson =
    allLessons.find((l) => l.id === selectedLessonId) || allLessons[0] || CURRICULUM_LESSONS[0];

  useEffect(() => {
    if (activeLesson && typeof window !== "undefined") {
      try {
        localStorage.setItem(
          "autotutor_last_studied",
          JSON.stringify({
            trackId: activeLesson.topicId,
            trackName: activeLesson.topicTitle || activeLesson.category,
            lessonId: activeLesson.id,
            lessonTitle: activeLesson.title,
            timestamp: new Date().toISOString(),
          })
        );
      } catch {
        // ignore
      }
    }
  }, [activeLesson]);

  const handleSelectLesson = (lessonId: string) => {
    setSelectedLessonId(lessonId);
    const topicParam = searchParams.get("topic");
    const problemParam = searchParams.get("problem");
    const modeParam = searchParams.get("mode") || "reader";
    const params = new URLSearchParams();
    params.set("lesson", lessonId);
    if (topicParam) params.set("topic", topicParam);
    if (problemParam) params.set("problem", problemParam);
    params.set("mode", modeParam);
    router.replace(`/workspace?${params.toString()}`);
  };

  const handleProjectToWhiteboard = () => {
    if (activeLesson.whiteboardPreset && typeof window !== "undefined") {
      sessionStorage.setItem("autotutor_active_graph", JSON.stringify(activeLesson.whiteboardPreset));
      router.push("/whiteboard");
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-background">
      {/* Top Curriculum Switcher Bar */}
      <div className="bg-card/70 border-b border-border px-4 py-2 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-primary shrink-0" />
          <span className="font-bold text-foreground shrink-0">Trilha Ativa:</span>
          <select
            value={activeLesson.id}
            onChange={(e) => handleSelectLesson(e.target.value)}
            className="bg-secondary text-foreground font-semibold px-3 py-1.5 rounded-xl border border-border focus:outline-none focus:ring-2 focus:ring-primary/50 text-xs cursor-pointer max-w-xs sm:max-w-md truncate"
          >
            <optgroup label="Trilhas Canônicas de Maratona">
              {CURRICULUM_LESSONS.map((l) => (
                <option key={l.id} value={l.id}>
                  {l.category}: {l.title}
                </option>
              ))}
            </optgroup>
            {customLessons.length > 0 && (
              <optgroup label="Trilhas Personalizadas & Criadas com IA">
                {customLessons.map((l) => (
                  <option key={l.id} value={l.id}>
                    ✨ {l.title}
                  </option>
                ))}
              </optgroup>
            )}
          </select>
        </div>

        {/* Projection Action to Whiteboard */}
        {activeLesson.whiteboardPreset && (
          <button
            type="button"
            onClick={handleProjectToWhiteboard}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700/60 font-medium transition-colors text-xs shrink-0"
            title="Exporta o grafo e exemplo C++ desta lição diretamente para o Quadro Branco Interativo"
          >
            <Network className="w-3.5 h-3.5 text-blue-400" />
            <span>Projetar Exemplo no Quadro Branco</span>
          </button>
        )}
      </div>

      <div className="flex-1">
        <WorkspaceLayout
          lesson={activeLesson}
          allLessons={allLessons}
          onLessonChange={handleSelectLesson}
          initialProblemId={searchParams.get("problem") || undefined}
          onBack={() => {
            if (typeof window !== "undefined") router.push("/");
          }}
        />
      </div>
    </div>
  );
}

export default function WorkspacePage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center min-h-screen bg-background text-muted-foreground text-xs gap-2">
          <Loader2 className="w-4 h-4 animate-spin text-primary" />
          <span>Carregando ambiente de aprendizagem C++...</span>
        </div>
      }
    >
      <WorkspaceContent />
    </Suspense>
  );
}
