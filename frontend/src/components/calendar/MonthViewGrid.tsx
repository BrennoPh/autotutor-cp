"use client";

import React from "react";
import { ScheduledTask } from "@/types/onboarding";
import { CheckCircle2, Clock, Coffee } from "lucide-react";

interface MonthViewGridProps {
  currentDate: Date;
  tasksByDate: Record<string, ScheduledTask[]>;
  onSelectTask: (task: ScheduledTask) => void;
  onToggleComplete: (taskId: string) => void;
}

function toLocalDateString(d: Date): string {
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

const WEEKDAY_NAMES = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];

export function MonthViewGrid({
  currentDate,
  tasksByDate,
  onSelectTask,
  onToggleComplete,
}: MonthViewGridProps) {
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const firstDay = new Date(year, month, 1);
  const startingDayOfWeek = firstDay.getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const daysInPrevMonth = new Date(year, month, 0).getDate();

  const cells: Array<{
    dateObj: Date;
    dateStr: string;
    dayNum: number;
    isCurrentMonth: boolean;
    isToday: boolean;
  }> = [];

  // Trailing days from previous month
  for (let i = startingDayOfWeek - 1; i >= 0; i--) {
    const dayNum = daysInPrevMonth - i;
    const d = new Date(year, month - 1, dayNum);
    cells.push({
      dateObj: d,
      dateStr: toLocalDateString(d),
      dayNum,
      isCurrentMonth: false,
      isToday: d.toDateString() === new Date().toDateString(),
    });
  }

  // Days of current month
  for (let dayNum = 1; dayNum <= daysInMonth; dayNum++) {
    const d = new Date(year, month, dayNum);
    cells.push({
      dateObj: d,
      dateStr: toLocalDateString(d),
      dayNum,
      isCurrentMonth: true,
      isToday: d.toDateString() === new Date().toDateString(),
    });
  }

  // Leading days from next month
  const totalCells = cells.length <= 35 ? 35 : 42;
  let nextMonthDay = 1;
  while (cells.length < totalCells) {
    const d = new Date(year, month + 1, nextMonthDay);
    cells.push({
      dateObj: d,
      dateStr: toLocalDateString(d),
      dayNum: nextMonthDay,
      isCurrentMonth: false,
      isToday: d.toDateString() === new Date().toDateString(),
    });
    nextMonthDay++;
  }

  return (
    <div className="space-y-2">
      {/* Weekday Column Headers */}
      <div className="grid grid-cols-7 gap-2 px-1">
        {WEEKDAY_NAMES.map((name) => (
          <div
            key={name}
            className="text-center text-xs font-bold uppercase tracking-wider text-muted-foreground py-1.5"
          >
            {name}
          </div>
        ))}
      </div>

      {/* 7x5 or 7x6 Month Grid */}
      <div className="grid grid-cols-7 gap-2">
        {cells.map((cell, idx) => {
          const dayTasks = tasksByDate[cell.dateStr] || [];
          const visibleTasks = dayTasks.slice(0, 2);
          const extraCount = dayTasks.length - visibleTasks.length;

          return (
            <div
              key={`${cell.dateStr}-${idx}`}
              className={`flex flex-col rounded-xl border p-2 min-h-[95px] sm:min-h-[110px] transition-all text-xs ${
                !cell.isCurrentMonth
                  ? "bg-card/25 border-border/40 text-muted-foreground/40 opacity-50"
                  : cell.isToday
                  ? "border-primary/60 bg-primary/5 shadow-xs"
                  : "border-border bg-card/60 hover:bg-card/80"
              }`}
            >
              {/* Day Header */}
              <div className="flex items-center justify-between pb-1 mb-1 border-b border-border/40">
                <span
                  className={`w-5 h-5 rounded-full flex items-center justify-center text-[11px] font-mono font-bold ${
                    cell.isToday
                      ? "bg-primary text-primary-foreground"
                      : cell.isCurrentMonth
                      ? "text-foreground"
                      : "text-muted-foreground/60"
                  }`}
                >
                  {cell.dayNum}
                </span>

                {dayTasks.length > 0 && (
                  <span className="text-[10px] text-muted-foreground font-mono">
                    {dayTasks.length} {dayTasks.length === 1 ? "meta" : "metas"}
                  </span>
                )}
              </div>

              {/* Tasks preview in cell */}
              <div className="space-y-1 flex-1 overflow-hidden">
                {visibleTasks.map((t) => {
                  const isRest = t.taskType === "rest";
                  const isCompleted = t.status === "completed";

                  return (
                    <div
                      key={t.id}
                      onClick={() => onSelectTask(t)}
                      className={`px-1.5 py-1 rounded text-left cursor-pointer transition-all truncate text-[10px] font-medium border flex items-center justify-between gap-1 ${
                        isRest
                          ? "bg-secondary/40 border-border/40 text-muted-foreground"
                          : isCompleted
                          ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400 line-through opacity-80"
                          : "bg-card border-border hover:border-primary/50 text-foreground shadow-xs"
                      }`}
                      title={t.title}
                    >
                      <span className="truncate flex-1">
                        {isRest ? "☕ Descanso" : t.title}
                      </span>

                      {!isRest && (
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            onToggleComplete(t.id);
                          }}
                          className={`shrink-0 ${
                            isCompleted
                              ? "text-emerald-400"
                              : "text-muted-foreground hover:text-emerald-400"
                          }`}
                        >
                          <CheckCircle2 className="w-3 h-3" />
                        </button>
                      )}
                    </div>
                  );
                })}

                {extraCount > 0 && (
                  <div className="text-[9px] font-bold text-primary pl-1">
                    +{extraCount} mais
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
