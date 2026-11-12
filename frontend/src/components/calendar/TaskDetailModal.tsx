import React from "react";
import { ScheduledTask } from "@/types/onboarding";
import { CheckCircle2, Clock, Calendar, ArrowRight, X, RotateCcw, BookOpen, Code2 } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { resolveTaskActionUrl } from "@/core/adaptiveRoadmapEngine";

interface TaskDetailModalProps {
  task: ScheduledTask | null;
  onClose: () => void;
  onToggleComplete: (taskId: string) => void;
  onPostponeTask: (taskId: string) => void;
  onNavigateAction?: (url: string) => void;
}

export function TaskDetailModal({
  task,
  onClose,
  onToggleComplete,
  onPostponeTask,
  onNavigateAction,
}: TaskDetailModalProps) {
  if (!task) return null;

  const isRest = task.taskType === "rest";

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 animate-fade-in"
    >
      <div className="w-full max-w-md bg-card border border-border rounded-3xl p-6 shadow-2xl space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between gap-2 border-b border-border pb-3">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Badge variant={task.status === "completed" ? "success" : "primary"}>
                {task.taskType.toUpperCase()}
              </Badge>
              <span className="text-xs text-muted-foreground flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5" />
                {task.date}
              </span>
            </div>
            <h3 className="text-base font-bold text-foreground">{task.title}</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-secondary text-muted-foreground hover:text-foreground"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <p className="text-xs text-muted-foreground leading-relaxed">{task.description}</p>

        {!isRest && (
          <div className="flex items-center gap-4 text-xs text-muted-foreground py-1">
            <span className="flex items-center gap-1 font-mono">
              <Clock className="w-3.5 h-3.5 text-primary" />
              {task.estimatedMinutes} min estimadas
            </span>
            <span>•</span>
            <span className="font-semibold text-foreground">
              Status: {task.status === "completed" ? "Concluída" : "Pendente"}
            </span>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-between gap-2 pt-3 border-t border-border/80">
          {!isRest && (
            <button
              onClick={() => onPostponeTask(task.id)}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold border border-border hover:bg-secondary text-muted-foreground hover:text-foreground transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Adiar 1 Dia</span>
            </button>
          )}

          <div className="flex items-center gap-2 ml-auto">
            {!isRest && (
              <button
                onClick={() => onToggleComplete(task.id)}
                className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                  task.status === "completed"
                    ? "bg-secondary text-muted-foreground hover:bg-secondary/80"
                    : "bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500/20"
                }`}
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>{task.status === "completed" ? "Marcar Pendente" : "Concluir"}</span>
              </button>
            )}

            {!isRest && (
              <button
                onClick={() => {
                  onClose();
                  const typeStr = (task.taskType || "").toLowerCase();
                  const titleStr = (task.title || "").toLowerCase();
                  const isTheory = typeStr === "theory" || titleStr.startsWith("teoria") || titleStr.includes("leitura");
                  const isProblem = typeStr === "problem" || titleStr.startsWith("prática") || titleStr.startsWith("pratica");
                  const targetUrl = resolveTaskActionUrl({
                    ...task,
                    taskType: isTheory ? "theory" : isProblem ? "problem" : task.taskType,
                  });
                  onNavigateAction?.(targetUrl);
                }}
                className="flex items-center gap-1.5 px-4 py-2 bg-primary text-primary-foreground rounded-xl text-xs font-bold hover:bg-primary-hover shadow-sm transition-all"
              >
                {(task.taskType || "").toLowerCase() === "theory" || (task.title || "").toLowerCase().startsWith("teoria") ? (
                  <>
                    <BookOpen className="w-3.5 h-3.5" />
                    <span>Estudar Teoria</span>
                  </>
                ) : (task.taskType || "").toLowerCase() === "problem" || (task.title || "").toLowerCase().startsWith("prática") || (task.title || "").toLowerCase().startsWith("pratica") ? (
                  <>
                    <Code2 className="w-3.5 h-3.5" />
                    <span>Praticar Desafio</span>
                  </>
                ) : (
                  <>
                    <span>Iniciar Agora</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
