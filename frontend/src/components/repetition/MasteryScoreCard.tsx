import React from "react";
import { TopicMastery } from "@/types/repetition";
import { TrendingUp, TrendingDown, Minus, CheckCircle2 } from "lucide-react";
import { Badge } from "@/components/ui/Badge";

interface MasteryScoreCardProps {
  topic: TopicMastery;
  onPracticeClick?: (topicId: string) => void;
}

export function MasteryScoreCard({ topic, onPracticeClick }: MasteryScoreCardProps) {
  const getTrendIcon = () => {
    switch (topic.trend) {
      case "up":
        return <TrendingUp className="w-3.5 h-3.5 text-emerald-500" aria-label="Evoluindo" />;
      case "down":
        return <TrendingDown className="w-3.5 h-3.5 text-rose-500" aria-label="Queda de rendimento" />;
      default:
        return <Minus className="w-3.5 h-3.5 text-muted-foreground" aria-label="Estável" />;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-emerald-500";
    if (score >= 60) return "text-indigo-400";
    if (score >= 40) return "text-amber-500";
    return "text-rose-500";
  };

  const getProgressBarColor = (score: number) => {
    if (score >= 80) return "bg-emerald-500";
    if (score >= 60) return "bg-primary";
    if (score >= 40) return "bg-amber-500";
    return "bg-rose-500";
  };

  return (
    <div className="p-4 rounded-xl border border-border bg-card shadow-sm hover:border-border/80 transition-all flex flex-col justify-between gap-4">
      <div className="flex items-start justify-between gap-2">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-medium text-muted-foreground">{topic.category}</span>
            <div className="flex items-center gap-1 text-xs">{getTrendIcon()}</div>
          </div>
          <h3 className="font-semibold text-foreground text-sm tracking-tight">{topic.topicName}</h3>
        </div>
        <div className="text-right">
          <span className={`text-xl font-bold font-mono tracking-tight ${getScoreColor(topic.masteryScore)}`}>
            {topic.masteryScore}%
          </span>
          <span className="block text-[11px] text-muted-foreground">domínio</span>
        </div>
      </div>

      <div className="space-y-1.5">
        <div className="flex items-center justify-between text-[11px] text-muted-foreground">
          <span>Questões Resolvidas</span>
          <span className="font-medium text-foreground">
            {topic.questionsSolved} / {topic.totalQuestions}
          </span>
        </div>
        <div className="w-full h-1.5 bg-secondary rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${getProgressBarColor(topic.masteryScore)}`}
            style={{ width: `${topic.masteryScore}%` }}
          />
        </div>
      </div>

      <div className="flex items-center justify-between pt-1 border-t border-border/40 text-xs">
        <span className="text-[11px] text-muted-foreground">Último treino: {topic.lastPracticed}</span>
        <button
          onClick={() => onPracticeClick?.(topic.topicId)}
          className="text-xs font-semibold text-primary hover:text-primary-hover transition-colors"
        >
          Praticar agora →
        </button>
      </div>
    </div>
  );
}
