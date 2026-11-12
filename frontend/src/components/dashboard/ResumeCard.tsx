import React from "react";
import { BookOpen, Code2, Clock, Brain, ArrowRight, CheckCircle2, Sparkles } from "lucide-react";
import { ResumeSession } from "@/types/dashboard";
import { Badge } from "@/components/ui/Badge";

interface ResumeCardProps {
  session: ResumeSession;
  onResume: (mode?: "reader" | "arena", customUrl?: string) => void;
}

export function ResumeCard({ session, onResume }: ResumeCardProps) {
  const isTheory = session.nextActionType === "theory" || !session.nextActionType;
  const isProblem = session.nextActionType === "problem";
  const isReview = session.nextActionType === "review";

  return (
    <div className="relative p-6 rounded-2xl border border-slate-800 bg-gradient-to-br from-slate-900/95 via-slate-900/90 to-blue-950/20 shadow-lg transition-all duration-200 hover:border-slate-700/80 group">
      {/* Top Banner: Meta Prioritária Imediata */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          <span className="flex h-2 w-2 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">
            Sua Próxima Ação Recomendada Hoje
          </span>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="primary">{session.trackName}</Badge>
          <span className="text-xs text-slate-400 flex items-center gap-1 font-mono">
            <Clock className="w-3.5 h-3.5 text-slate-500" /> ~{session.estimatedMinutesToFinish} min
          </span>
        </div>
      </div>

      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 pt-4">
        <div className="space-y-3 max-w-2xl">
          <div>
            <div className="flex items-center gap-2 mb-1">
              {isTheory ? (
                <span className="text-[11px] font-semibold text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded-md border border-blue-500/20 flex items-center gap-1">
                  <BookOpen className="w-3 h-3" /> Aula Didática
                </span>
              ) : isProblem ? (
                <span className="text-[11px] font-semibold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-md border border-amber-500/20 flex items-center gap-1">
                  <Code2 className="w-3 h-3" /> Desafio de Código no Juiz
                </span>
              ) : (
                <span className="text-[11px] font-semibold text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded-md border border-purple-500/20 flex items-center gap-1">
                  <Brain className="w-3 h-3" /> Fixação com Flashcards
                </span>
              )}
              <span className="text-xs text-slate-400">• {session.moduleTitle}</span>
            </div>

            <h2 className="text-xl sm:text-2xl font-extrabold tracking-tight text-white group-hover:text-blue-300 transition-colors">
              {session.lessonTitle}
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Próximo marco pedagógico: <strong className="text-slate-300 font-medium">{session.lastCheckpointLabel}</strong>
            </p>
          </div>

          {/* Barra de Progresso Rápida */}
          <div className="space-y-1 pt-1 max-w-md">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-400 text-[11px]">Progresso do objetivo</span>
              <span className="text-blue-400 font-semibold">{session.progressPercent}%</span>
            </div>
            <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full transition-all duration-300"
                style={{ width: `${Math.max(session.progressPercent, 5)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Primary Action Button - 1 Clique sem pensar */}
        <div className="shrink-0 flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          {session.actionUrl ? (
            <button
              onClick={() => onResume(undefined, session.actionUrl)}
              className="flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl font-bold text-sm bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-500 hover:to-indigo-500 shadow-md shadow-blue-900/30 transition-all hover:scale-[1.02] active:scale-[0.98]"
            >
              {isTheory && <BookOpen className="w-4 h-4" />}
              {isProblem && <Code2 className="w-4 h-4" />}
              {isReview && <Brain className="w-4 h-4" />}
              <span>
                {isTheory
                  ? "Começar Aula de Hoje"
                  : isProblem
                  ? "Resolver Questão Agora"
                  : "Fazer Flashcards do Dia"}
              </span>
              <ArrowRight className="w-4 h-4 ml-1" />
            </button>
          ) : (
            <>
              <button
                onClick={() => onResume("reader")}
                className="flex items-center justify-center gap-2 px-5 py-3 rounded-xl font-bold text-xs bg-blue-600 text-white hover:bg-blue-500 shadow-sm transition-all"
              >
                <BookOpen className="w-4 h-4" />
                <span>Estudar Conteúdo</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => onResume("arena")}
                className="flex items-center justify-center gap-2 px-4 py-3 rounded-xl font-bold text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700/80 transition-all"
              >
                <Code2 className="w-4 h-4 text-blue-400" />
                <span>Praticar</span>
              </button>
            </>
          )}
        </div>
      </div>

      {/* Trilha Linear de Ações de Hoje (Sequência Sem Atrito) */}
      {session.dailySequence && session.dailySequence.length > 0 && (
        <div className="mt-5 pt-4 border-t border-slate-800/80">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block mb-2.5">
            Roteiro Guiado de Hoje (1 clique em cada passo):
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
            {session.dailySequence.map((step, idx) => (
              <button
                key={step.id}
                onClick={() => onResume(undefined, step.url)}
                className={`p-3 rounded-xl text-left border transition-all flex items-center justify-between gap-2.5 ${
                  step.completed
                    ? "bg-slate-900/50 border-emerald-500/30 text-slate-400"
                    : "bg-slate-800/60 border-slate-700/70 hover:border-blue-500/50 hover:bg-slate-800 text-slate-200 shadow-xs"
                }`}
              >
                <div className="min-w-0">
                  <span className="text-[10px] font-bold block text-slate-400 uppercase">
                    Passo {idx + 1} • {step.type === "theory" ? "Aula" : step.type === "problem" ? "Questão" : "Revisão"} ({step.durationMinutes}m)
                  </span>
                  <p className="text-xs font-semibold truncate text-white">{step.title}</p>
                </div>
                {step.completed ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                ) : (
                  <ArrowRight className="w-4 h-4 text-blue-400 shrink-0" />
                )}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
