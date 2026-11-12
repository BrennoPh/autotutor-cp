import React from "react";
import { RepetitionItem } from "@/types/repetition";
import { AlertCircle, Clock, CheckCircle2, RotateCw, Layers } from "lucide-react";
import { Badge } from "@/components/ui/Badge";

interface EbbinghausScheduleProps {
  items: RepetitionItem[];
  onStartReview: (itemId?: string) => void;
}

export function EbbinghausSchedule({ items, onStartReview }: EbbinghausScheduleProps) {
  const urgentCount = items.filter((i) => i.urgency === "urgent").length;
  const dueTodayCount = items.filter((i) => i.urgency === "due-today").length;

  const getUrgencyBadge = (urgency: RepetitionItem["urgency"]) => {
    switch (urgency) {
      case "urgent":
        return <Badge variant="danger">Crítico (&lt; 50%)</Badge>;
      case "due-today":
        return <Badge variant="warning">Hoje</Badge>;
      case "upcoming":
        return <Badge variant="secondary">Em 3 dias</Badge>;
      case "mastered":
        return <Badge variant="success">Consolidado</Badge>;
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-base font-bold text-foreground">Ciclos de Revisão (Ebbinghaus)</h2>
          <p className="text-xs text-muted-foreground">
            Revisões intervaladas calculadas com base na curva de esquecimento para retenção de longo prazo.
          </p>
        </div>
        <button
          onClick={() => onStartReview()}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground text-xs font-semibold rounded-xl hover:bg-primary-hover shadow-sm transition-all focus:ring-2 focus:ring-ring"
        >
          <Layers className="w-3.5 h-3.5" />
          <span>Revisar Tudo ({urgentCount + dueTodayCount} pendentes)</span>
        </button>
      </div>

      <div className="space-y-2.5">
        {items.map((item) => (
          <div
            key={item.id}
            className="p-3.5 rounded-xl border border-border bg-card flex items-center justify-between gap-4 hover:border-border/80 transition-colors"
          >
            <div className="flex items-center gap-3 min-w-0">
              <div
                className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${
                  item.urgency === "urgent"
                    ? "bg-rose-500/10 text-rose-500"
                    : item.urgency === "due-today"
                    ? "bg-amber-500/10 text-amber-500"
                    : "bg-primary/10 text-primary"
                }`}
              >
                {item.urgency === "urgent" ? (
                  <AlertCircle className="w-4 h-4" />
                ) : item.urgency === "due-today" ? (
                  <Clock className="w-4 h-4" />
                ) : (
                  <CheckCircle2 className="w-4 h-4" />
                )}
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <h4 className="text-xs font-bold text-foreground truncate">{item.topicTitle}</h4>
                  {getUrgencyBadge(item.urgency)}
                </div>
                <div className="flex items-center gap-3 text-[11px] text-muted-foreground mt-0.5">
                  <span>{item.category}</span>
                  <span>•</span>
                  <span>{item.flashcardsCount} flashcards</span>
                  <span>•</span>
                  <span>Ciclo #{item.repetitionsCount} ({item.intervalDays}d)</span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-4 shrink-0">
              <div className="text-right hidden sm:block">
                <span className="text-xs font-mono font-bold text-foreground block">
                  {item.retentionRate}% retenção
                </span>
                <span className="text-[10px] text-muted-foreground">Previsão Ebbinghaus</span>
              </div>
              <button
                onClick={() => onStartReview(item.id)}
                className="px-3 py-1.5 rounded-lg border border-border text-xs font-semibold hover:bg-secondary text-foreground transition-colors"
              >
                Revisar
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
