"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { OnboardingWizard } from "@/components/onboarding/OnboardingWizard";
import { UserAssessmentProfile, CustomTrack } from "@/types/onboarding";
import { generateStudySchedule } from "@/core/adaptiveRoadmapEngine";
import { assessmentService } from "@/services/assessmentService";

export default function OnboardingPage() {
  const router = useRouter();

  const handleComplete = async (profile: UserAssessmentProfile, track: CustomTrack) => {
    // 1. Gera as tarefas do calendário a partir de hoje
    const initialTasks = generateStudySchedule(track, profile, new Date());

    // 2. Persiste estado no localStorage para carregamento instantâneo
    try {
      localStorage.setItem("autotutor_user_profile", JSON.stringify(profile));
      localStorage.setItem("autotutor_user_track", JSON.stringify(track));
      localStorage.setItem("autotutor_scheduled_tasks", JSON.stringify(initialTasks));
    } catch (e) {
      console.error("Falha ao salvar dados no localStorage:", e);
    }

    // 3. Sincroniza com o backend Python headless (SQLite)
    try {
      await assessmentService.submitAssessment({
        target_goal: profile.targetGoal,
        hours_per_day: profile.availableHoursPerDay,
        language: profile.preferredLanguage,
        answers: profile.diagnosticResult?.answers || {},
      });
    } catch (e) {
      console.warn("Backend offline ou aviso de sincronização:", e);
    }

    // 4. Redireciona para o Calendário de Estudos
    router.push("/calendar");
  };

  return (
    <div className="min-h-screen bg-background flex flex-col justify-center items-center p-4 sm:p-8">
      <div className="w-full max-w-3xl mb-6 text-center space-y-1">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold mb-2">
          <span>AutoTutor AI • Planejamento Inteligente</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground">
          Calibre Seu Ponto de Partida
        </h1>
        <p className="text-xs sm:text-sm text-muted-foreground">
          Diagnóstico rápido em 3 minutos para eliminar lacunas e traçar seu cronograma diário de estudos.
        </p>
      </div>

      <OnboardingWizard onComplete={handleComplete} />
    </div>
  );
}
