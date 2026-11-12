"use client";

import React, { useRef, useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { StudyLesson } from "@/types/workspace";
import { StudyReader } from "./StudyReader";
import { PracticeArena } from "./PracticeArena";
import { AiTutorDock } from "./AiTutorDock";
import { ContextualPopover } from "./ContextualPopover";
import { Breadcrumbs } from "@/components/navigation/Breadcrumbs";
import { useLayoutContext } from "@/context/LayoutContext";
import { useWorkspaceState } from "@/hooks/useWorkspaceState";
import { useTextSelection } from "@/hooks/useTextSelection";
import { Terminal, Maximize2, Minimize2, ArrowLeft, Code2, BookOpen, Loader2, Cpu } from "lucide-react";
import { tutorService } from "@/services/tutorService";
import { aiService } from "@/services/aiService";
import { lessonProgressService } from "@/services/lessonProgressService";

interface WorkspaceLayoutProps {
  lesson: StudyLesson;
  onBack?: () => void;
  onLessonChange?: (lessonId: string) => void;
  initialProblemId?: string;
  allLessons?: any[];
}

function resolveCanonicalProblemForLesson(lessonId?: string, topicId?: string, topicTitle?: string): string {
  const combined = `${lessonId || ""} ${topicId || ""} ${topicTitle || ""}`.toLowerCase();
  if (combined.includes("tree") || combined.includes("árvor") || combined.includes("arvor") || combined.includes("lca")) return "tree";
  if (combined.includes("busca bin") || combined.includes("binary") || combined.includes("binária") || combined.includes("binaria")) return "binary";
  if (combined.includes("dp") || combined.includes("dinâmica") || combined.includes("dinamica") || combined.includes("mochila")) return "dp";
  if (combined.includes("greedy") || combined.includes("guloso") || combined.includes("interval")) return "greedy";
  if (combined.includes("prefix") || combined.includes("prefixo")) return "prefix";
  if (combined.includes("segtree") || combined.includes("segment") || combined.includes("dsu")) return "segment_tree";
  if (combined.includes("recurs") || combined.includes("pilha") || combined.includes("stack")) return "tree";
  if (combined.includes("grafo") || combined.includes("bfs") || combined.includes("dfs") || combined.includes("dijkstra")) return "graph";
  return "graph";
}

export function WorkspaceLayout({
  lesson,
  onBack,
  onLessonChange,
  initialProblemId,
  allLessons,
}: WorkspaceLayoutProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const router = useRouter();
  const searchParams = useSearchParams();
  const urlMode = searchParams.get("mode");
  const [workspaceMode, setWorkspaceMode] = useState<"arena" | "reader">(
    urlMode === "reader" ? "reader" : "arena"
  );

  useEffect(() => {
    if (urlMode === "reader" || urlMode === "arena") {
      setWorkspaceMode(urlMode);
    }
  }, [urlMode]);

  const handleAdvanceNextStep = () => {
    const nextStep = lessonProgressService.getNextStepForLesson(
      lesson.id,
      lesson.topicId,
      allLessons
    );
    if (nextStep) {
      if (nextStep.type === "lesson") {
        onLessonChange?.(nextStep.id);
        const params = new URLSearchParams(searchParams.toString());
        params.set("lesson", nextStep.id);
        params.set("mode", "reader");
        router.replace(`/workspace?${params.toString()}`);
      } else {
        const params = new URLSearchParams(searchParams.toString());
        params.set("mode", "arena");
        if (nextStep.url) {
          const match = nextStep.url.match(/[?&]problem=([^&]+)/);
          if (match) {
            const probId = decodeURIComponent(match[1]);
            params.set("problem", probId);
            setArenaProblemId(probId);
          }
        }
        setWorkspaceMode("arena");
        router.replace(`/workspace?${params.toString()}`);
      }
    } else {
      handleSwitchMode("arena");
    }
  };

  const [arenaProblemId, setArenaProblemId] = useState<string | undefined>(
    initialProblemId || searchParams.get("problem") || undefined
  );

  useEffect(() => {
    const p = searchParams.get("problem");
    if (p) {
      setArenaProblemId(p);
    }
  }, [searchParams]);

  const handleSwitchMode = (newMode: "arena" | "reader") => {
    setWorkspaceMode(newMode);
    const params = new URLSearchParams(searchParams.toString());
    params.set("mode", newMode);
    if (newMode === "arena" && !params.get("problem")) {
      const canonical = resolveCanonicalProblemForLesson(lesson.id, lesson.topicId, lesson.topicTitle);
      params.set("problem", canonical);
      setArenaProblemId(canonical);
    }
    router.replace(`/workspace?${params.toString()}`);
  };

  const [arenaContext, setArenaContext] = useState<any>(null);
  const [isGeneratingChallenge, setIsGeneratingChallenge] = useState(false);

  const handleContextUpdate = React.useCallback(
    (ctx: any) => {
      setArenaContext((prev: any) => {
        if (
          prev?.problem?.id === ctx?.problem?.id &&
          prev?.code === ctx?.code &&
          prev?.result === ctx?.result
        ) {
          return prev;
        }
        return ctx;
      });
      // NOTE: Auto-sync da aula de teoria baseada no problema da Arena foi
      // removido propositalmente: causava override da aula que o usuário havia
      // selecionado ao navegar por um módulo de trilha ou pelo seletor manual.
      // A sincronia de teoria ↔ problema agora é exclusivamente iniciada pelo
      // usuário (via seletor de trilha ou botão "Estudar Teoria" do conteúdo).
    },
    []
  );

  const {
    isZenMode,
    isDockOpen,
    tutorStatus,
    messages,
    toggleZenMode,
    toggleDock,
    triggerContextualAction,
    setIsDockOpen,
  } = useWorkspaceState();

  const { setSidebarHidden } = useLayoutContext();
  React.useEffect(() => {
    setSidebarHidden(isZenMode);
    return () => setSidebarHidden(false);
  }, [isZenMode, setSidebarHidden]);

  const { selection, clearSelection } = useTextSelection(containerRef);

  const handleAskTutorFromArena = React.useCallback(
    async (context: { problem: any; code: string; result: any }) => {
      setIsDockOpen(true);
      triggerContextualAction(
        "explain_analogy",
        `Estou com veredito ${context.result?.verdict || "WA"} no problema ${context.problem?.title}. O que posso revisar?`,
        {
          problem_id: context.problem?.id,
          code: context.code,
          judge_result: context.result,
        }
      );
    },
    [setIsDockOpen, triggerContextualAction]
  );

  const handleGenerateAndPractice = async () => {
    setIsGeneratingChallenge(true);
    const canonical = resolveCanonicalProblemForLesson(lesson.id, lesson.topicId, lesson.topicTitle);
    try {
      const res = await aiService.generateProblem({
        level: "Iniciante",
        concept: lesson.topicTitle,
        theme: lesson.title,
        learning_request: lesson.summary,
      });
      const chosenProblemId = (res && res.id) ? res.id : canonical;
      setArenaProblemId(chosenProblemId);
      const params = new URLSearchParams(searchParams.toString());
      params.set("mode", "arena");
      params.set("problem", chosenProblemId);
      router.replace(`/workspace?${params.toString()}`);
      setWorkspaceMode("arena");
    } catch (e) {
      console.error("Falha ao gerar desafio da lição, direcionando para problema canônico do tema:", e);
      setArenaProblemId(canonical);
      const params = new URLSearchParams(searchParams.toString());
      params.set("mode", "arena");
      params.set("problem", canonical);
      router.replace(`/workspace?${params.toString()}`);
      setWorkspaceMode("arena");
    } finally {
      setIsGeneratingChallenge(false);
    }
  };

  const handleOpenTheoryForTopic = React.useCallback(
    (topicStr: string) => {
      const t = (topicStr || "").toLowerCase().trim();
      let matchedLesson = "bfs_dfs_foundations";

      if (t.includes("dp") || t.includes("dinâmica") || t.includes("dinamica") || t.includes("mochila")) {
        matchedLesson = "dp_knapsack_foundations";
      } else if (t.includes("binária") || t.includes("binaria") || t.includes("busca")) {
        matchedLesson = "binary_search_foundations";
      } else if (t.includes("guloso") || t.includes("greedy")) {
        matchedLesson = "greedy_foundations";
      } else if (t.includes("árvore") || t.includes("arvore") || t.includes("tree")) {
        matchedLesson = "tree_foundations";
      } else if (t.includes("prefix") || t.includes("prefixo")) {
        matchedLesson = "prefix_sum_foundations";
      } else if (t.includes("segtree") || t.includes("segment") || t.includes("dsu")) {
        matchedLesson = "dsu_kruskal_mst";
      } else if (t.includes("dijkstra") || t.includes("caminho")) {
        matchedLesson = "dijkstra_shortest_path";
      } else if (t.includes("grafo") || t.includes("bfs") || t.includes("dfs")) {
        matchedLesson = "bfs_dfs_foundations";
      }

      onLessonChange?.(matchedLesson);
      handleSwitchMode("reader");
    },
    [onLessonChange, handleSwitchMode]
  );

  return (
    <div className={`min-h-screen bg-background flex flex-col ${isZenMode ? "zen-mode" : ""}`}>
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header / Breadcrumb & Mode Bar */}
        {!isZenMode && (
          <header className="sticky top-0 z-30 h-14 border-b border-border bg-card/80 backdrop-blur-md px-4 sm:px-6 flex items-center justify-between shrink-0">
            <div className="flex items-center gap-3">
              {onBack && (
                <button
                  onClick={onBack}
                  aria-label="Voltar para a página anterior"
                  className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
                >
                  <ArrowLeft className="w-4 h-4" />
                </button>
              )}
              <Breadcrumbs
                items={[
                  { label: "Dashboard", href: "/" },
                  { label: lesson.topicTitle, href: `/trilhas/${lesson.topicId}` },
                  { label: workspaceMode === "arena" ? "Arena de Prática & Juiz" : lesson.title, active: true },
                ]}
              />
            </div>

            {/* Mode Switcher */}
            <div className="flex items-center gap-1.5 bg-secondary/80 p-1 rounded-xl border border-border">
              <button
                type="button"
                onClick={() => handleSwitchMode("arena")}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  workspaceMode === "arena"
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                <Code2 className="w-3.5 h-3.5" />
                <span>Arena & Juiz</span>
              </button>
              <button
                type="button"
                onClick={() => handleSwitchMode("reader")}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  workspaceMode === "reader"
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                <BookOpen className="w-3.5 h-3.5" />
                <span>Teoria & Leitura</span>
              </button>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => window.dispatchEvent(new CustomEvent("open-ai-config"))}
                className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800 transition-colors border border-slate-700/60 bg-slate-900/60"
                title="Configurações de Provedores de IA (Gemini, Ollama, Chaves e Modelos)"
              >
                <Cpu className="w-3.5 h-3.5 text-blue-400" />
                <span className="hidden sm:inline">Configurações de API</span>
              </button>

              <button
                onClick={toggleZenMode}
                aria-label={isZenMode ? "Sair do modo foco" : "Ativar modo foco"}
                className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
              >
                <Maximize2 className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Modo Foco</span>
              </button>

              <button
                onClick={toggleDock}
                aria-label={isDockOpen ? "Recolher assistente" : "Abrir assistente"}
                className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium border transition-colors ${
                  isDockOpen
                    ? "bg-slate-800 text-slate-100 border-slate-700 shadow-sm"
                    : "bg-slate-900 text-slate-300 border-slate-800 hover:bg-slate-800"
                }`}
              >
                <Terminal className="w-3.5 h-3.5 text-slate-400" />
                <span>Assistente</span>
              </button>
            </div>
          </header>
        )}

        {/* Floating Exit Zen Button */}
        {isZenMode && (
          <button
            onClick={toggleZenMode}
            aria-label="Sair do modo foco"
            className="fixed top-4 right-4 z-50 flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-card/90 text-foreground border border-border shadow-md text-xs font-medium hover:bg-accent transition-colors"
          >
            <Minimize2 className="w-3.5 h-3.5" />
            <span>Sair do Foco</span>
          </button>
        )}

        {/* Main Split-View Area */}
        <div className="flex-1 flex overflow-hidden relative">
          {/* Overlay de geração de problema a partir do estudo */}
          {isGeneratingChallenge && (
            <div className="absolute inset-0 z-50 bg-background/80 backdrop-blur-sm flex flex-col items-center justify-center gap-3">
              <Loader2 className="w-8 h-8 text-primary animate-spin" />
              <div className="text-center">
                <p className="text-sm font-bold text-foreground">Sintetizando Desafio Adaptativo Inédito...</p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Construindo casos de teste e enunciado C++ sobre {lesson.title}.
                </p>
              </div>
            </div>
          )}

          <main
            className={`flex-1 overflow-y-auto transition-all duration-200 ${
              isDockOpen && !isZenMode ? "lg:mr-[380px] xl:mr-[420px]" : ""
            }`}
          >
            {workspaceMode === "arena" ? (
              <PracticeArena
                initialProblemId={arenaProblemId || initialProblemId}
                topicFilter={lesson.topicTitle}
                onAskTutor={handleAskTutorFromArena}
                onContextUpdate={handleContextUpdate}
                onOpenTheory={handleOpenTheoryForTopic}
              />
            ) : (
              <StudyReader
                lesson={lesson}
                containerRef={containerRef}
                onPracticeChallenge={handleGenerateAndPractice}
                onAdvanceNextStep={handleAdvanceNextStep}
                allLessons={allLessons}
              />
            )}
          </main>

          {/* Floating Contextual Popover on selection (during reader mode) */}
          {workspaceMode === "reader" && (
            <ContextualPopover
              selection={selection}
              onAction={triggerContextualAction}
              onClose={clearSelection}
            />
          )}

          {/* AI Tutor Dock (30-35% split) */}
          {!isZenMode && (
            <AiTutorDock
              isOpen={isDockOpen}
              onClose={toggleDock}
              status={tutorStatus}
              messages={messages}
              arenaContext={arenaContext}
              onSendMessage={(text) =>
                triggerContextualAction("simplify", text, {
                  problem_id: arenaContext?.problem?.id,
                  code: arenaContext?.code,
                  judge_result: arenaContext?.result,
                })
              }
              onTriggerQuickAction={(actionType, customPrompt) => {
                triggerContextualAction(actionType as any, customPrompt || "", {
                  problem_id: arenaContext?.problem?.id,
                  code: arenaContext?.code,
                  judge_result: arenaContext?.result,
                });
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
}
