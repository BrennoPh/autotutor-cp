"use client";

import React, { useState } from "react";
import { ScheduledTask } from "@/types/onboarding";
import { TaskDetailModal } from "./TaskDetailModal";
import { MonthViewGrid } from "./MonthViewGrid";
import { lessonProgressService } from "@/services/lessonProgressService";
import {
  ChevronLeft,
  ChevronRight,
  Calendar as CalendarIcon,
  CheckCircle2,
  Clock,
  Coffee,
} from "lucide-react";

interface StudyCalendarProps {
  tasks: ScheduledTask[];
  onTasksChange: (tasks: ScheduledTask[]) => void;
  onNavigateAction?: (url: string) => void;
}

function toLocalDateString(d: Date): string {
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export function StudyCalendar({ tasks, onTasksChange, onNavigateAction }: StudyCalendarProps) {
  const [viewMode, setViewMode] = useState<"week" | "month">("month");
  const [selectedTask, setSelectedTask] = useState<ScheduledTask | null>(null);
  const [currentDate, setCurrentDate] = useState<Date>(new Date());

  // Group tasks by date string (YYYY-MM-DD)
  const tasksByDate = tasks.reduce<Record<string, ScheduledTask[]>>((acc, task) => {
    acc[task.date] = acc[task.date] || [];
    acc[task.date].push(task);
    return acc;
  }, {});

  // Compute 7 days for current week view
  const dayOfWeek = currentDate.getDay();
  const weekStart = new Date(currentDate);
  weekStart.setDate(currentDate.getDate() - dayOfWeek);

  const weekDays = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(weekStart);
    d.setDate(weekStart.getDate() + i);
    return {
      dateObj: d,
      dateStr: toLocalDateString(d),
      dayName: ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"][d.getDay()],
      dayNum: d.getDate(),
      isToday: d.toDateString() === new Date().toDateString(),
    };
  });

  // Navigation handlers
  const handlePrev = () => {
    if (viewMode === "month") {
      setCurrentDate((prev) => new Date(prev.getFullYear(), prev.getMonth() - 1, 1));
    } else {
      setCurrentDate((prev) => new Date(prev.getFullYear(), prev.getMonth(), prev.getDate() - 7));
    }
  };

  const handleNext = () => {
    if (viewMode === "month") {
      setCurrentDate((prev) => new Date(prev.getFullYear(), prev.getMonth() + 1, 1));
    } else {
      setCurrentDate((prev) => new Date(prev.getFullYear(), prev.getMonth(), prev.getDate() + 7));
    }
  };

  const handleToday = () => {
    setCurrentDate(new Date());
  };

  // Task Actions
  const handleToggleComplete = (taskId: string) => {
    const targetTask = tasks.find((t) => t.id === taskId);
    if (targetTask) {
      const willBeCompleted = targetTask.status !== "completed";
      // Apenas tarefas de teoria sincronizam com lições de leitura
      if (targetTask.taskType === "theory") {
        let lessonId = "";
        if (targetTask.actionUrl) {
          const match = targetTask.actionUrl.match(/[?&]lesson=([^&]+)/);
          if (match) lessonId = decodeURIComponent(match[1]);
        }
        if (!lessonId && targetTask.topicId) {
          lessonId = targetTask.topicId;
        }
        if (lessonId) {
          lessonProgressService.toggleLessonCompletion(lessonId, willBeCompleted, "theory");
        }
      }
    }

    onTasksChange(
      tasks.map((t) =>
        t.id === taskId
          ? {
              ...t,
              status: t.status === "completed" ? "pending" : "completed",
              completedAt: t.status === "completed" ? undefined : new Date().toISOString(),
            }
          : t
      )
    );
    if (selectedTask?.id === taskId) {
      setSelectedTask((prev) =>
        prev
          ? {
              ...prev,
              status: prev.status === "completed" ? "pending" : "completed",
            }
          : null
      );
    }
  };

  const handlePostponeTask = (taskId: string) => {
    onTasksChange(
      tasks.map((t) => {
        if (t.id !== taskId) return t;
        const curr = new Date(t.date);
        curr.setDate(curr.getDate() + 1);
        return {
          ...t,
          date: toLocalDateString(curr),
          rescheduledFrom: t.date,
        };
      })
    );
    setSelectedTask(null);
  };

  const rawTitle =
    viewMode === "month"
      ? currentDate.toLocaleDateString("pt-BR", { month: "long", year: "numeric" })
      : `${weekDays[0].dateObj.toLocaleDateString("pt-BR", { day: "numeric", month: "short" })} - ${weekDays[6].dateObj.toLocaleDateString("pt-BR", { day: "numeric", month: "short", year: "numeric" })}`;

  const formattedTitle = rawTitle.charAt(0).toUpperCase() + rawTitle.slice(1);

  return (
    <div className="space-y-4">
      {/* Calendar Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-4 bg-card border border-border rounded-2xl shadow-sm">
        <div className="flex items-center gap-3">
          <CalendarIcon className="w-5 h-5 text-primary" />
          <h2 className="text-base font-bold text-foreground capitalize">
            {formattedTitle}
          </h2>
          <button
            type="button"
            onClick={handleToday}
            className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-secondary hover:bg-accent text-foreground transition-colors"
          >
            Hoje
          </button>
        </div>

        <div className="flex items-center gap-2">
          {/* View Mode Toggle */}
          <div className="flex items-center gap-1 bg-secondary/80 p-1 rounded-xl border border-border">
            <button
              type="button"
              onClick={() => setViewMode("week")}
              className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                viewMode === "week"
                  ? "bg-card text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Semana
            </button>
            <button
              type="button"
              onClick={() => setViewMode("month")}
              className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                viewMode === "month"
                  ? "bg-card text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Mês
            </button>
          </div>

          {/* Period Pagination */}
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={handlePrev}
              className="p-1.5 rounded-lg border border-border hover:bg-secondary text-muted-foreground hover:text-foreground transition-colors"
              title={viewMode === "month" ? "Mês anterior" : "Semana anterior"}
              aria-label={viewMode === "month" ? "Mês anterior" : "Semana anterior"}
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={handleNext}
              className="p-1.5 rounded-lg border border-border hover:bg-secondary text-muted-foreground hover:text-foreground transition-colors"
              title={viewMode === "month" ? "Próximo mês" : "Próxima semana"}
              aria-label={viewMode === "month" ? "Próximo mês" : "Próxima semana"}
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Calendar View: Month or Week */}
      {viewMode === "month" ? (
        <MonthViewGrid
          currentDate={currentDate}
          tasksByDate={tasksByDate}
          onSelectTask={setSelectedTask}
          onToggleComplete={handleToggleComplete}
        />
      ) : (
        /* Week View Grid */
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-7 gap-3">
          {weekDays.map((day) => {
            const dayTasks = tasksByDate[day.dateStr] || [];

            return (
              <div
                key={day.dateStr}
                className={`flex flex-col rounded-2xl border p-3 min-h-[220px] transition-all ${
                  day.isToday
                    ? "border-primary/60 bg-primary/5 shadow-sm"
                    : "border-border bg-card/60"
                }`}
              >
                {/* Day Header */}
                <div className="flex items-center justify-between pb-2 mb-2 border-b border-border/60">
                  <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                    {day.dayName}
                  </span>
                  <span
                    className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-mono font-bold ${
                      day.isToday ? "bg-primary text-primary-foreground" : "text-foreground"
                    }`}
                  >
                    {day.dayNum}
                  </span>
                </div>

                {/* Tasks List */}
                <div className="space-y-2 flex-1">
                  {dayTasks.length === 0 ? (
                    <div className="h-full flex items-center justify-center text-[11px] text-muted-foreground/60 italic">
                      Sem tarefas
                    </div>
                  ) : (
                    dayTasks.map((t) => {
                      const isRest = t.taskType === "rest";
                      const isCompleted = t.status === "completed";

                      return (
                        <div
                          key={t.id}
                          onClick={() => setSelectedTask(t)}
                          className={`p-2.5 rounded-xl border text-left cursor-pointer transition-all hover:scale-[1.02] ${
                            isRest
                              ? "bg-secondary/40 border-border/40 text-muted-foreground"
                              : isCompleted
                              ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
                              : "bg-card border-border hover:border-primary/50 text-foreground shadow-sm"
                          }`}
                        >
                          <div className="flex items-center justify-between gap-1 mb-1">
                            <span className="text-[10px] font-bold uppercase tracking-wider">
                              {isRest ? (
                                <span className="flex items-center gap-1">
                                  <Coffee className="w-3 h-3 text-muted-foreground" />
                                  Descanso
                                </span>
                              ) : (
                                t.taskType
                              )}
                            </span>
                            {!isRest && (
                              <button
                                type="button"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleToggleComplete(t.id);
                                }}
                                className={`transition-colors ${
                                  isCompleted ? "text-emerald-500" : "text-muted-foreground hover:text-emerald-500"
                                }`}
                              >
                                <CheckCircle2 className="w-3.5 h-3.5" />
                              </button>
                            )}
                          </div>

                          <div className={`text-xs font-semibold leading-tight line-clamp-2 ${isCompleted ? "line-through opacity-70" : ""}`}>
                            {t.title}
                          </div>

                          {!isRest && (
                            <div className="flex items-center gap-1 text-[10px] text-muted-foreground mt-1.5 font-mono">
                              <Clock className="w-3 h-3 text-primary" />
                              <span>{t.estimatedMinutes}m</span>
                            </div>
                          )}
                        </div>
                      );
                    })
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Detail Modal */}
      <TaskDetailModal
        task={selectedTask}
        onClose={() => setSelectedTask(null)}
        onToggleComplete={handleToggleComplete}
        onPostponeTask={handlePostponeTask}
        onNavigateAction={onNavigateAction}
      />
    </div>
  );
}
