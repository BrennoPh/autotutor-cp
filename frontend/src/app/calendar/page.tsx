"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Breadcrumbs } from "@/components/navigation/Breadcrumbs";
import { StudyCalendar } from "@/components/calendar/StudyCalendar";
import { ScheduledTask, UserAssessmentProfile, CustomTrack } from "@/types/onboarding";
import { generateStudySchedule, generateCustomTrack, resolveTaskActionUrl } from "@/core/adaptiveRoadmapEngine";
import { Calendar, Target, Clock, ArrowRight } from "lucide-react";

const FALLBACK_PROFILE: UserAssessmentProfile = {
  userId: "user-1",
  hasCompletedOnboarding: true,
  targetGoal: "graphs",
  availableHoursPerDay: 1,
  activeDaysOfWeek: [1, 2, 3, 4, 5],
  preferredLanguage: "cpp",
  diagnosticResult: {
    score: 60,
    entryLevel: "Intermediário",
    confidence: "alta",
    strongTopics: ["Análise Assintótica e Complexidade"],
    gapTopics: ["Recursão e Pilha de Execução", "Fila (Queue) e Invariante de Camadas da BFS"],
    evaluatedAt: new Date().toISOString(),
    answers: {},
  },
};

export default function CalendarPage() {
  const router = useRouter();
  const [profile, setProfile] = useState<UserAssessmentProfile>(FALLBACK_PROFILE);
  const [tasks, setTasks] = useState<ScheduledTask[]>([]);

  useEffect(() => {
    try {
      const storedProfile = localStorage.getItem("autotutor_user_profile");
      const storedTasks = localStorage.getItem("autotutor_scheduled_tasks");

      if (storedProfile) {
        setProfile(JSON.parse(storedProfile));
      }
      if (storedTasks) {
        const parsed: ScheduledTask[] = JSON.parse(storedTasks);
        // Auto-migra URLs legadas para que tarefas teóricas abram diretamente em mode=reader e práticas em mode=arena
        const migrated = parsed.map((t) => {
          const typeStr = (t.taskType || "").toLowerCase();
          const titleStr = (t.title || "").toLowerCase();
          const isTheory = typeStr === "theory" || titleStr.startsWith("teoria") || titleStr.includes("leitura");
          const isProblem = typeStr === "problem" || titleStr.startsWith("prática") || titleStr.startsWith("pratica");
          const normalizedType = isTheory ? "theory" : isProblem ? "problem" : (t.taskType || "theory");

          const needsMigration =
            !t.actionUrl ||
            t.actionUrl === "/workspace" ||
            !t.actionUrl.includes("mode=") ||
            (isTheory && !t.actionUrl.includes("mode=reader")) ||
            (isProblem && !t.actionUrl.includes("mode=arena"));

          if (needsMigration) {
            return {
              ...t,
              taskType: normalizedType as any,
              actionUrl: resolveTaskActionUrl({
                ...t,
                taskType: normalizedType,
              }),
            };
          }
          return t;
        });
        setTasks(migrated);
        try {
          localStorage.setItem("autotutor_scheduled_tasks", JSON.stringify(migrated));
        } catch (e) {
          console.warn("Falha ao salvar tarefas migradas:", e);
        }
      } else if (storedProfile) {
        const parsedProfile = JSON.parse(storedProfile);
        if (parsedProfile.hasCompletedOnboarding) {
          const storedTrack = localStorage.getItem("autotutor_user_track");
          const track = storedTrack ? JSON.parse(storedTrack) : generateCustomTrack(parsedProfile);
          const generated = generateStudySchedule(track, parsedProfile, new Date());
          setTasks(generated);
          try {
            localStorage.setItem("autotutor_scheduled_tasks", JSON.stringify(generated));
          } catch {}
        } else {
          setTasks([]);
        }
      } else {
        setTasks([]);
      }
    } catch {
      setTasks([]);
    }
  }, []);

  const handleTasksChange = (newTasks: ScheduledTask[]) => {
    setTasks(newTasks);
    try {
      localStorage.setItem("autotutor_scheduled_tasks", JSON.stringify(newTasks));
    } catch (e) {
      console.error(e);
    }
  };

  const breadcrumbs = [
    { label: "Dashboard", href: "/" },
    { label: "Calendário Interativo de Estudos" },
  ];

  return (
    <main className="flex-1 flex flex-col min-w-0 pb-20 lg:pb-8">
      <header className="px-6 py-4 border-b border-border bg-card/40 backdrop-blur-sm sticky top-0 z-30">
        <Breadcrumbs items={breadcrumbs} />
      </header>

      <div className="max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Calendar className="w-6 h-6 text-primary" />
              <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground">
                Calendário de Estudos & Metas
              </h1>
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              Planejamento diário adaptativo calibrado com base no seu diagnóstico e ritmo de {profile.availableHoursPerDay}h/dia.
            </p>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <span className="px-3 py-1.5 rounded-xl border border-border bg-card flex items-center gap-1.5 font-medium">
              <Target className="w-3.5 h-3.5 text-primary" />
              Meta: {profile.targetGoal.toUpperCase()}
            </span>
            <span className="px-3 py-1.5 rounded-xl border border-border bg-card flex items-center gap-1.5 font-medium">
              <Clock className="w-3.5 h-3.5 text-amber-500" />
              {profile.availableHoursPerDay}h diárias
            </span>
          </div>
        </div>

        {/* Empty State Banner if no tasks */}
        {tasks.length === 0 && (
          <div className="p-6 rounded-2xl border border-dashed border-border bg-card/40 backdrop-blur-sm text-center space-y-3">
            <h3 className="text-sm font-bold text-foreground">Nenhuma Tarefa Agendada</h3>
            <p className="text-xs text-muted-foreground max-w-md mx-auto">
              Seu calendário está limpo. Realize o teste diagnóstico de nivelamento para calibrar suas metas e gerar seu cronograma diário adaptativo.
            </p>
            <button
              type="button"
              onClick={() => router.push("/onboarding")}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold bg-primary text-primary-foreground hover:bg-primary-hover shadow-sm transition-all cursor-pointer"
            >
              <span>Fazer Diagnóstico de Nivelamento</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* Calendar Component */}
        <StudyCalendar
          tasks={tasks}
          onTasksChange={handleTasksChange}
          onNavigateAction={(url) => router.push(url)}
        />
      </div>
    </main>
  );
}
