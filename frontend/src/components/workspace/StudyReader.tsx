import React, { useState, useMemo, useEffect } from "react";
import { StudyLesson, ReaderViewMode } from "@/types/workspace";
import {
  BookOpen,
  MonitorPlay,
  ChevronLeft,
  ChevronRight,
  Network,
  Wand2,
  Terminal,
  Brain,
  ArrowRight,
  CheckCircle2,
} from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { MarkdownRenderer } from "@/components/ui/MarkdownRenderer";
import { GraphLabWorkspace } from "@/components/whiteboard/GraphLabWorkspace";
import { extractGraphFromMermaid } from "@/utils/graphExtractor";
import { lessonProgressService, NextStepAction } from "@/services/lessonProgressService";

interface StudyReaderProps {
  lesson: StudyLesson;
  containerRef: React.RefObject<HTMLDivElement>;
  initialMode?: ReaderViewMode;
  onPracticeChallenge?: () => void;
  onAdvanceNextStep?: () => void;
  allLessons?: Array<{ id: string; title: string; topicId?: string }>;
}

export function StudyReader({
  lesson,
  containerRef,
  initialMode = "article",
  onPracticeChallenge,
  onAdvanceNextStep,
  allLessons,
}: StudyReaderProps) {
  const [viewMode, setViewMode] = useState<ReaderViewMode>(initialMode);
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);

  const [isCompleted, setIsCompleted] = useState<boolean>(() =>
    lessonProgressService.isLessonCompleted(lesson.id)
  );

  useEffect(() => {
    setIsCompleted(lessonProgressService.isLessonCompleted(lesson.id));
    const handleSync = (e: any) => {
      if (!e?.detail?.lessonId || e.detail.lessonId === lesson.id) {
        setIsCompleted(lessonProgressService.isLessonCompleted(lesson.id));
      }
    };
    window.addEventListener("lesson-completion-changed", handleSync);
    return () => window.removeEventListener("lesson-completion-changed", handleSync);
  }, [lesson.id]);

  const handleToggleCompleted = async () => {
    const res = await lessonProgressService.toggleLessonCompletion(lesson.id);
    setIsCompleted(res.completed);
  };

  const nextStep: NextStepAction | null = useMemo(() => {
    return lessonProgressService.getNextStepForLesson(lesson.id, lesson.topicId, allLessons);
  }, [lesson.id, lesson.topicId, allLessons]);

  const handleTriggerAdvance = () => {
    if (onAdvanceNextStep) {
      onAdvanceNextStep();
    } else if (nextStep?.url) {
      window.location.href = nextStep.url;
    } else if (onPracticeChallenge) {
      onPracticeChallenge();
    }
  };

  const sections = lesson.sections;
  const currentSection = sections[currentSlideIndex] || sections[0];

  // Extract graph topology from lesson sections if available
  const lessonGraph = useMemo(() => {
    const fullText = sections.map((s) => s.content).join("\n\n");
    return extractGraphFromMermaid(fullText);
  }, [sections]);

  const handleOpenGraphOnWhiteboard = () => {
    setViewMode("whiteboard");
  };

  return (
    <article
      ref={containerRef}
      className="w-full flex flex-col items-center py-6 px-4 sm:px-8 select-text"
      aria-label={`Leitura da aula: ${lesson.title}`}
    >
      {/* Header and Mode Selector */}
      <div className="w-full max-w-prose mb-8 flex flex-col gap-4 border-b border-border pb-6">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-2">
            <Badge variant="primary">{lesson.topicTitle}</Badge>
            <button
              type="button"
              onClick={handleToggleCompleted}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-xl text-xs font-semibold transition-all shadow-xs ${
                isCompleted
                  ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/25"
                  : "bg-secondary text-muted-foreground border border-border hover:text-foreground hover:border-primary/50"
              }`}
              title={isCompleted ? "Clique para marcar como pendente" : "Marcar esta aula como concluída"}
            >
              <CheckCircle2
                className={`w-3.5 h-3.5 ${
                  isCompleted ? "text-emerald-400 fill-emerald-500/20" : "text-muted-foreground"
                }`}
              />
              <span>{isCompleted ? "Concluída ✓" : "Concluir Aula"}</span>
            </button>
          </div>

          <div className="flex items-center gap-1 bg-secondary/80 p-1 rounded-xl border border-border">
            <button
              onClick={() => setViewMode("article")}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                viewMode === "article" ? "bg-card text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"
              }`}
              aria-pressed={viewMode === "article"}
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span>Artigo</span>
            </button>
            <button
              onClick={() => setViewMode("slides")}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                viewMode === "slides" ? "bg-card text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"
              }`}
              aria-pressed={viewMode === "slides"}
            >
              <MonitorPlay className="w-3.5 h-3.5" />
              <span>Slides</span>
            </button>
            <button
              onClick={() => setViewMode("whiteboard")}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                viewMode === "whiteboard"
                  ? "bg-card text-primary shadow-sm font-semibold"
                  : "text-muted-foreground hover:text-foreground"
              }`}
              aria-pressed={viewMode === "whiteboard"}
              title="Abrir simulação visual e quadro branco do estudo"
            >
              <Network className="w-3.5 h-3.5 text-primary" />
              <span>Quadro Branco</span>
            </button>
          </div>

          {onPracticeChallenge && (
            <button
              type="button"
              onClick={onPracticeChallenge}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold bg-primary text-primary-foreground hover:bg-primary-hover shadow-sm transition-all"
              title="Gera uma questão de maratona baseada especificamente neste conteúdo"
            >
              <Wand2 className="w-3.5 h-3.5" />
              <span>Gerar Questão deste conteúdo</span>
            </button>
          )}
        </div>

        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground mb-2">
            {lesson.title}
          </h1>
          {lesson.subtitle && (
            <p className="text-sm text-muted-foreground leading-relaxed">{lesson.subtitle}</p>
          )}
        </div>
      </div>

      {/* Reader Content - Article View */}
      {viewMode === "article" && (
        <div className="w-full max-w-prose space-y-8 text-foreground/90 leading-[1.7] text-[15px]">
          {sections.map((section, idx) => (
            <section key={section.id || idx} className="space-y-4">
              <h2 className="text-lg font-bold text-foreground tracking-tight pt-2 border-t border-border/40">
                {section.title}
              </h2>
              <MarkdownRenderer
                content={section.content}
                onOpenInWhiteboard={handleOpenGraphOnWhiteboard}
              />
            </section>
          ))}

          {/* Roteiro Guiado: Próximo Passo do Aprendizado */}
          <div className="w-full p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-blue-950/30 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mt-8 shadow-sm">
            <div className="space-y-1">
              <span className={`text-xs font-bold flex items-center gap-1.5 uppercase tracking-wider ${isCompleted ? "text-emerald-400" : "text-primary"}`}>
                {isCompleted ? (
                  <>
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    Aula Concluída!
                  </>
                ) : (
                  <>
                    <Terminal className="w-4 h-4 text-primary" />
                    Leitura em Andamento
                  </>
                )}
              </span>
              <p className="text-xs text-slate-300">
                {isCompleted
                  ? "Excelente! Prossiga diretamente para o próximo passo da sua trilha com 1 clique."
                  : `Marque a aula como concluída para registrar seu progresso em ${lesson.title}.`}
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2.5 w-full md:w-auto shrink-0">
              <button
                type="button"
                onClick={handleToggleCompleted}
                className={`flex-1 md:flex-none flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                  isCompleted
                    ? "bg-secondary text-muted-foreground hover:bg-secondary/80 border border-border"
                    : "bg-emerald-600 hover:bg-emerald-500 text-white font-bold shadow-sm"
                }`}
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>{isCompleted ? "Marcar como Pendente" : "Marcar como Concluída"}</span>
              </button>

              <button
                type="button"
                onClick={handleTriggerAdvance}
                className="flex-1 md:flex-none flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl bg-primary text-primary-foreground text-xs font-bold hover:bg-primary-hover transition-all shadow-md"
              >
                <span>{nextStep?.type === "lesson" ? "Avançar para a Próxima Aula" : "Praticar Desafio no Juiz"}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>

              <button
                type="button"
                onClick={() => {
                  window.location.href = `/repetition?topic=${encodeURIComponent(lesson.topicId)}&autoStart=true`;
                }}
                className="flex-1 md:flex-none flex items-center justify-center gap-1.5 px-3 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold transition-all"
                title="Fixar conceitos com repetição espaçada"
              >
                <Brain className="w-3.5 h-3.5 text-purple-400" />
                <span>Flashcards</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Reader Content - Slide View */}
      {viewMode === "slides" && (
        <div className="w-full max-w-prose space-y-6">
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>
              Slide {currentSlideIndex + 1} de {sections.length}
            </span>
            <div className="w-36 h-1.5 bg-secondary rounded-full overflow-hidden">
              <div
                className="h-full bg-primary transition-all duration-300"
                style={{ width: `${((currentSlideIndex + 1) / sections.length) * 100}%` }}
              />
            </div>
          </div>

          <div className="p-6 rounded-2xl border border-border bg-card shadow-sm space-y-4 min-h-[300px]">
            <h2 className="text-xl font-bold text-foreground">{currentSection.title}</h2>
            <MarkdownRenderer
              content={currentSection.content}
              onOpenInWhiteboard={handleOpenGraphOnWhiteboard}
            />
          </div>

          <div className="flex items-center justify-between pt-2">
            <button
              onClick={() => setCurrentSlideIndex((prev) => Math.max(0, prev - 1))}
              disabled={currentSlideIndex === 0}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-secondary hover:bg-accent disabled:opacity-40 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
              <span>Anterior</span>
            </button>
            <button
              onClick={() => setCurrentSlideIndex((prev) => Math.min(sections.length - 1, prev + 1))}
              disabled={currentSlideIndex >= sections.length - 1}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-primary text-primary-foreground hover:bg-primary-hover disabled:opacity-40 transition-colors"
            >
              <span>Próximo</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          {currentSlideIndex === sections.length - 1 && (
            <div className="p-4 rounded-2xl bg-card border border-border flex flex-wrap items-center justify-between gap-3 animate-fade-in mt-4">
              <button
                type="button"
                onClick={handleToggleCompleted}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                  isCompleted
                    ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                    : "bg-secondary text-foreground border border-border hover:border-primary/50"
                }`}
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>{isCompleted ? "Aula Concluída ✓" : "Concluir Aula"}</span>
              </button>

              <button
                type="button"
                onClick={handleTriggerAdvance}
                className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-primary text-primary-foreground text-xs font-bold hover:bg-primary-hover shadow-sm transition-all"
              >
                <span>{nextStep?.type === "lesson" ? "Próxima Aula" : "Praticar Desafio"}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          )}
        </div>
      )}

      {/* Reader Content - Whiteboard Obsidian Split View */}
      {viewMode === "whiteboard" && (
        <div className="w-full max-w-6xl space-y-6">
          <div className="p-4 rounded-2xl border border-primary/20 bg-primary/5 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Network className="w-5 h-5 text-primary" />
              <div>
                <h3 className="text-sm font-bold text-foreground">
                  Quadro Branco Interativo & Simulação Sincronizada
                </h3>
                <p className="text-xs text-muted-foreground">
                  Simulação de execução visual com os nós e arestas referenciados na aula.
                </p>
              </div>
            </div>
            <button
              onClick={() => setViewMode("article")}
              className="text-xs font-semibold px-3 py-1.5 rounded-xl bg-secondary hover:bg-accent border border-border transition-colors"
            >
              Voltar ao Artigo
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            {/* Left Column: Summary and Reading (4 cols) */}
            <div className="lg:col-span-5 space-y-4 max-h-[680px] overflow-y-auto p-4 rounded-2xl border border-border bg-card/60">
              <h3 className="text-sm font-bold text-foreground border-b border-border pb-2">
                Referência Teórica do Tópico
              </h3>
              <MarkdownRenderer content={currentSection.content} />
            </div>

            {/* Right Column: Interactive Whiteboard Canvas & Execution Engine (7 cols) */}
            <div className="lg:col-span-7">
              <GraphLabWorkspace
                initialNodes={lessonGraph?.nodes}
                initialEdges={lessonGraph?.edges}
                compact
              />
            </div>
          </div>
        </div>
      )}
    </article>
  );
}
