"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { UniversalBar } from "@/components/dashboard/UniversalBar";
import { ResumeCard } from "@/components/dashboard/ResumeCard";
import { DailyStreakWidget } from "@/components/dashboard/DailyStreakWidget";
import { TracksCarousel } from "@/components/dashboard/TracksCarousel";
import { WeakPointsRadar } from "@/components/dashboard/WeakPointsRadar";
import { FirstDayHeroCard } from "@/components/dashboard/FirstDayHeroCard";
import { ResumeSession, DailyGoalStreak, ActiveTrack, WeakPointSuggestion } from "@/types/dashboard";
import { CustomTrack } from "@/types/onboarding";
import { useOnboardingGuard } from "@/hooks/useOnboardingGuard";
import { progressService, ProgressData } from "@/services/progressService";
import { resolveTaskActionUrl } from "@/core/adaptiveRoadmapEngine";
import { lessonProgressService } from "@/services/lessonProgressService";

const defaultSession: ResumeSession = {
  trackId: "onboarding",
  trackName: "Comece Aqui: Diagnóstico de Nivelamento",
  moduleTitle: "Calibração de Nível",
  lessonId: "onboarding",
  lessonTitle: "Teste Diagnóstico Rápido",
  progressPercent: 0,
  estimatedMinutesToFinish: 5,
  lastCheckpointLabel: "Novo Aluno",
  nextActionType: "theory",
  actionUrl: "/onboarding",
};

const initialStreak: DailyGoalStreak = {
  streakDays: 1,
  targetMinutesToday: 30,
  completedMinutesToday: 0,
  flashcardsGoal: 10,
  flashcardsDoneToday: 0,
  consistencyScore: 60,
};

export default function DashboardPage() {
  const router = useRouter();
  const { profile, isLoading, shouldRedirectToOnboarding } = useOnboardingGuard();
  const [streak, setStreak] = useState<DailyGoalStreak>(initialStreak);
  const [dashboardTracks, setDashboardTracks] = useState<ActiveTrack[]>([]);
  const [session, setSession] = useState<ResumeSession>(defaultSession);
  const [weakPoints, setWeakPoints] = useState<WeakPointSuggestion[]>([]);

  // Sync session and weak points with profile and custom tracks
  const syncSession = () => {
    try {
      // 1. Prioridade máxima: meta de hoje do plano de estudos adaptativo
      const scheduledTasksStored = localStorage.getItem("autotutor_scheduled_tasks");
      let todayTask: any = null;
      let dailySequence: any[] = [];

      if (scheduledTasksStored) {
        try {
          const tasks: any[] = JSON.parse(scheduledTasksStored);
          const todayStr = new Date().toISOString().split("T")[0];
          const activeTasksPool = tasks.filter((t) => t.taskType !== "rest");
          const pendingTasks = activeTasksPool.filter((t) => t.status !== "completed");
          const todayPending = pendingTasks.filter((t) => t.date === todayStr);
          const chosenTasks = todayPending.length > 0 ? todayPending : pendingTasks;

          if (chosenTasks.length > 0) {
            todayTask = chosenTasks[0];
            dailySequence = chosenTasks.slice(0, 3).map((t, i) => ({
              id: t.id || `step-${i}`,
              type: t.taskType || "theory",
              title: t.title,
              durationMinutes: t.estimatedMinutes || 25,
              completed: t.status === "completed",
              url: resolveTaskActionUrl(t),
            }));
          }
        } catch {
          // ignore
        }
      }

      if (todayTask) {
        const actionType = (todayTask.taskType || "theory").toLowerCase();
        setSession({
          trackId: todayTask.topicId || "grafos",
          trackName: todayTask.category || "Plano Adaptativo",
          moduleTitle: actionType === "theory" ? "Aula Teórica de Hoje" : actionType === "problem" ? "Desafio no Juiz de Hoje" : "Revisão e Fixação",
          lessonId: todayTask.topicId || "bfs_dfs_foundations",
          lessonTitle: todayTask.title,
          progressPercent: todayTask.status === "completed" ? 100 : 0,
          estimatedMinutesToFinish: todayTask.estimatedMinutes || 30,
          lastCheckpointLabel: actionType === "theory" ? "Compreensão de Conceitos & Invariantes" : actionType === "problem" ? "Submeter Solução Accepted (AC)" : "Fixação Curva de Ebbinghaus",
          nextActionType: actionType,
          actionUrl: resolveTaskActionUrl(todayTask),
          dailySequence,
        });
      } else {
        // 2. Prioridade secundária: o último conteúdo que o usuário efetivamente estudou
        const lastStudied = localStorage.getItem("autotutor_last_studied");
        if (lastStudied) {
          const parsed = JSON.parse(lastStudied);
          if (parsed?.lessonId) {
            setSession({
              trackId: parsed.trackId || "grafos",
              trackName: parsed.trackName || "Trilha Ativa",
              moduleTitle: "Retomar de onde parou",
              lessonId: parsed.lessonId,
              lessonTitle: parsed.lessonTitle || "Conteúdo em Andamento",
              progressPercent: 35,
              estimatedMinutesToFinish: 20,
              lastCheckpointLabel: "Último Tópico Estudado",
              nextActionType: "theory",
            });
          }
        } else {
          // 3. Trilha customizada do onboarding
          const storedTrack = localStorage.getItem("autotutor_user_track");
          if (storedTrack) {
            const parsedTrack: CustomTrack = JSON.parse(storedTrack);
            const milestones = parsedTrack?.milestones || [];
            if (milestones.length > 0) {
              const completedCount = milestones.filter(
                (m: any) =>
                  lessonProgressService.isLessonCompleted(m.topicId) ||
                  lessonProgressService.isLessonCompleted(m.id) ||
                  m.completed
              ).length;
              const progressPct = Math.round((completedCount / milestones.length) * 100);

              const uncompletedIndex = milestones.findIndex(
                (m: any) =>
                  !lessonProgressService.isLessonCompleted(m.topicId) &&
                  !lessonProgressService.isLessonCompleted(m.id) &&
                  !m.completed
              );

              const isAllDone = uncompletedIndex === -1;
              const activeIndex = isAllDone ? milestones.length - 1 : uncompletedIndex;
              const activeMilestone = milestones[activeIndex];

              setSession({
                trackId: parsedTrack.id,
                trackName: parsedTrack.title,
                moduleTitle: isAllDone ? "Trilha Concluída! Desafio Final na Arena" : activeMilestone.title,
                lessonId: activeMilestone.topicId || activeMilestone.id || "pilha",
                lessonTitle: isAllDone ? "Praticar Desafio Final no Juiz de Código" : (activeMilestone.keyConcepts?.[0] || activeMilestone.title),
                progressPercent: progressPct,
                estimatedMinutesToFinish: isAllDone ? 30 : ((activeMilestone.estimatedHours || 1) * 60),
                lastCheckpointLabel: isAllDone ? "Parabéns! Trilha 100% Concluída" : `Semana ${activeMilestone.weekNumber || activeIndex + 1}: Em Andamento`,
                nextActionType: isAllDone ? "problem" : "theory",
              });
            }
          } else {
            // 4. Trilha personalizada criada com IA
            const customTracksStored = localStorage.getItem("autotutor_custom_tracks");
            if (customTracksStored) {
              const parsedCustom = JSON.parse(customTracksStored);
              if (parsedCustom?.length > 0 && parsedCustom[0]?.modules?.length > 0) {
                const latestTrack = parsedCustom[0];
                const mods = latestTrack.modules || [];
                const completedCount = mods.filter(
                  (m: any) => lessonProgressService.isLessonCompleted(m.id) || m.completed
                ).length;
                const uncompletedMod = mods.find(
                  (m: any) => !lessonProgressService.isLessonCompleted(m.id) && !m.completed
                ) || mods[0];

                setSession({
                  trackId: latestTrack.id,
                  trackName: latestTrack.title,
                  moduleTitle: uncompletedMod.title,
                  lessonId: uncompletedMod.id || latestTrack.id,
                  lessonTitle: uncompletedMod.title,
                  progressPercent: Math.round((completedCount / Math.max(1, mods.length)) * 100),
                  estimatedMinutesToFinish: uncompletedMod.estimatedMinutes || 30,
                  lastCheckpointLabel: "Módulo em Andamento",
                  nextActionType: "theory",
                });
              }
            }
          }
        }
      }

      if (profile?.diagnosticResult?.gapTopics && profile.diagnosticResult.gapTopics.length > 0) {
        const mappedGaps: WeakPointSuggestion[] = profile.diagnosticResult.gapTopics.map((gap, i) => ({
          id: `wp-${i}`,
          topicId: gap,
          topicTitle: gap,
          accuracyRate: 0,
          insight: "Identificado como lacuna conceitual na avaliação diagnóstica inicial.",
          suggestedActionLabel: "Revisar conceitos e exercitar",
        }));
        setWeakPoints(mappedGaps);
      }
    } catch (e) {
      console.error("Falha ao sincronizar dados do perfil no dashboard:", e);
    }
  };

  // Sync session and weak points with profile and custom tracks, plus live lesson completion listener
  useEffect(() => {
    syncSession();
    window.addEventListener("lesson-completion-changed", syncSession);
    return () => window.removeEventListener("lesson-completion-changed", syncSession);
  }, [profile]);

  // Sync with custom tracks in localStorage and lesson completions
  useEffect(() => {
    const syncDashboardTracks = () => {
      try {
        const activeTracksList: ActiveTrack[] = [];

        // 1. Trilha personalizada do Onboarding
        const storedUserTrack = localStorage.getItem("autotutor_user_track");
        if (storedUserTrack) {
          const userTrack = JSON.parse(storedUserTrack);
          const milestones = userTrack.milestones || [];
          const completedCount = milestones.filter(
            (m: any) =>
              lessonProgressService.isLessonCompleted(m.topicId) ||
              lessonProgressService.isLessonCompleted(m.id) ||
              m.completed
          ).length;
          const userActive: ActiveTrack = {
            id: userTrack.id,
            title: userTrack.title,
            subject: userTrack.targetGoal
              ? `Trilha do Aluno: ${userTrack.targetGoal.toUpperCase()}`
              : "Sua Trilha Ativa",
            retentionRate: 88,
            difficultyTag: userTrack.entryLevel || "Iniciante",
            completedModules: completedCount,
            totalModules: milestones.length || 3,
          };
          activeTracksList.push(userActive);
        }

        // 2. Trilhas customizadas geradas via modal IA
        const stored = localStorage.getItem("autotutor_custom_tracks");
        if (stored) {
          const parsed = JSON.parse(stored);
          const customActive: ActiveTrack[] = parsed.map((t: any) => ({
            id: t.id,
            title: t.title,
            subject: t.subject,
            retentionRate: t.retentionRate || 80,
            difficultyTag: t.difficulty,
            completedModules: (t.modules || []).filter(
              (m: any) => lessonProgressService.isLessonCompleted(m.id) || m.completed
            ).length,
            totalModules: (t.modules || []).length || 3,
          }));
          activeTracksList.push(...customActive);
        }

        setDashboardTracks(activeTracksList);
      } catch (e) {
        console.error(e);
      }
    };

    syncDashboardTracks();
    window.addEventListener("lesson-completion-changed", syncDashboardTracks);
    return () => window.removeEventListener("lesson-completion-changed", syncDashboardTracks);
  }, []);

  // Sync with headless API progress
  useEffect(() => {
    progressService
      .getProgress()
      .then((data: ProgressData) => {
        if (data) {
          setStreak((prev) => ({
            ...prev,
            streakDays: data.streak_days || prev.streakDays,
            consistencyScore: Math.min(100, (data.solved_count * 15) + 60),
          }));
        }
      })
      .catch(console.warn);
  }, []);

  const handleResume = (targetMode?: "reader" | "arena", customUrl?: string) => {
    if (customUrl) {
      router.push(customUrl);
      return;
    }
    const mode = targetMode || (session.nextActionType === "problem" ? "arena" : "reader");
    const topic = session.trackId || "grafos";
    const lesson = session.lessonId || "bfs_dfs_foundations";
    const problemParam = mode === "arena" ? `&problem=${encodeURIComponent(lesson)}` : "";
    router.push(`/workspace?topic=${encodeURIComponent(topic)}&lesson=${encodeURIComponent(lesson)}&mode=${mode}${problemParam}`);
  };

  if (isLoading) {
    return (
      <main className="flex-1 p-4 sm:p-8 lg:p-10 space-y-8 max-w-6xl mx-auto w-full pb-20 lg:pb-10">
        <div className="h-10 w-full bg-slate-800/40 animate-pulse rounded-lg" />
        <div className="h-44 w-full bg-slate-800/40 animate-pulse rounded-xl" />
      </main>
    );
  }

  return (
    <main className="flex-1 p-4 sm:p-8 lg:p-10 space-y-8 max-w-6xl mx-auto w-full pb-20 lg:pb-10">
      {/* Universal AI Command Bar */}
      <section aria-label="Comando universal de estudo">
        <UniversalBar
          onSearchSubmit={(q) =>
            router.push(`/lab?q=${encodeURIComponent(q)}&autoGenerate=true`)
          }
        />
      </section>

      {/* Conditionally render First-Day Welcome Hero or Veteran Dashboard Cockpit */}
      {shouldRedirectToOnboarding ? (
        <FirstDayHeroCard onStart={() => router.push("/onboarding")} />
      ) : (
        <>
          {/* Priority 1 Cockpit Hero: Continue from where you left off */}
          <section aria-label="Sessão ativa prioritária">
            <ResumeCard session={session} onResume={handleResume} />
          </section>

          {/* Middle Grid: Streak Widget & Weak Points Radar */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <DailyStreakWidget streak={streak} />
            <WeakPointsRadar
              suggestions={
                weakPoints.length > 0
                  ? weakPoints
                  : [
                      {
                        id: "wp-init",
                        topicId: "foundations",
                        topicTitle: "Fundamentos e Complexidade",
                        accuracyRate: 50,
                        insight: "Complete seus primeiros exercícios práticos para calibrar o radar de lacunas.",
                        suggestedActionLabel: "Abrir laboratório de código",
                      },
                    ]
              }
              onReviewTopic={(id) => router.push(`/lab?q=${encodeURIComponent(id)}`)}
            />
          </div>

          {/* Tracks Carousel */}
          <TracksCarousel
            tracks={dashboardTracks}
            onSelectTrack={(id) => router.push(`/trilhas/${id}`)}
          />
        </>
      )}
    </main>
  );
}
