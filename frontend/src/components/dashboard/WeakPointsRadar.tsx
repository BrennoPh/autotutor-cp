import React from "react";
import { Target, ArrowRight } from "lucide-react";
import { WeakPointSuggestion } from "@/types/dashboard";

interface WeakPointsRadarProps {
  suggestions: WeakPointSuggestion[];
  onReviewTopic: (topicId: string) => void;
}

export function WeakPointsRadar({ suggestions, onReviewTopic }: WeakPointsRadarProps) {
  if (!suggestions.length) return null;

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/90 p-4 shadow-sm space-y-3">
      <div className="flex items-center justify-between pb-2.5 border-b border-slate-800/80">
        <div className="flex items-center gap-2 text-slate-100 font-semibold text-xs">
          <Target className="w-4 h-4 text-amber-500" />
          <span>Diagnóstico de Pontos Fracos</span>
        </div>
        <span className="text-[11px] font-mono text-slate-500">
          {suggestions.length} {suggestions.length === 1 ? "tópico pendente" : "tópicos pendentes"}
        </span>
      </div>

      <div className="space-y-2.5">
        {suggestions.map((item) => (
          <div
            key={item.id}
            className="p-3 rounded-md bg-slate-950/60 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
          >
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="font-medium text-xs text-slate-200">{item.topicTitle}</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-950/70 text-amber-400 border border-amber-800/40 font-mono font-medium">
                  {item.accuracyRate}% acerto recente
                </span>
              </div>
              <p className="text-[11px] text-slate-400 leading-relaxed">{item.insight}</p>
            </div>

            <button
              onClick={() => onReviewTopic(item.topicId)}
              className="shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white border border-slate-700/60 transition-colors"
            >
              <span>{item.suggestedActionLabel}</span>
              <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
