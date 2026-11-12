import React from "react";
import { Flame, Target, CheckCircle2 } from "lucide-react";
import { DailyGoalStreak } from "@/types/dashboard";

interface DailyStreakWidgetProps {
  streak: DailyGoalStreak;
}

export function DailyStreakWidget({ streak }: DailyStreakWidgetProps) {
  const percentMinutes = Math.min(100, Math.round((streak.completedMinutesToday / streak.targetMinutesToday) * 100));

  return (
    <div className="p-4 rounded-lg border border-slate-800 bg-slate-900/90 shadow-sm space-y-3">
      <div className="flex items-center justify-between pb-2 border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded bg-amber-950/60 text-amber-500 border border-amber-800/40 flex items-center justify-center">
            <Flame className="w-3.5 h-3.5 fill-current" />
          </div>
          <div>
            <span className="font-semibold text-xs text-slate-200 block">Foco & Consistência</span>
            <span className="text-[10px] text-slate-400 font-mono">{streak.streakDays} dias consecutivos</span>
          </div>
        </div>
        <span className="text-[11px] font-mono font-medium text-amber-400 bg-amber-950/60 border border-amber-800/40 px-2 py-0.5 rounded">
          {streak.streakDays}x Streak
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2.5 pt-0.5">
        <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800">
          <div className="flex items-center gap-1.5 text-[11px] text-slate-400 mb-1">
            <Target className="w-3.5 h-3.5 text-slate-500" />
            <span>Tempo focado</span>
          </div>
          <p className="text-xs font-semibold font-mono text-slate-200">
            {streak.completedMinutesToday} / {streak.targetMinutesToday} min
          </p>
          <div className="w-full h-1 bg-slate-800 rounded-full mt-2 overflow-hidden">
            <div className="h-full bg-blue-500 rounded-full" style={{ width: `${percentMinutes}%` }} />
          </div>
        </div>

        <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800">
          <div className="flex items-center gap-1.5 text-[11px] text-slate-400 mb-1">
            <CheckCircle2 className="w-3.5 h-3.5 text-slate-500" />
            <span>Exercícios</span>
          </div>
          <p className="text-xs font-semibold font-mono text-slate-200">
            {streak.flashcardsDoneToday} / {streak.flashcardsGoal} itens
          </p>
          <div className="w-full h-1 bg-slate-800 rounded-full mt-2 overflow-hidden">
            <div
              className="h-full bg-blue-500 rounded-full"
              style={{ width: `${Math.min(100, (streak.flashcardsDoneToday / streak.flashcardsGoal) * 100)}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
