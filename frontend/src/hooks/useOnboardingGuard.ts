import { useState, useEffect } from "react";
import { UserAssessmentProfile } from "@/types/onboarding";
import { progressService } from "@/services/progressService";
import { apiRequest } from "@/services/apiClient";

const STORAGE_KEY = "autotutor_user_profile";

export function purgeAllClientStudyData() {
  if (typeof window === "undefined") return;
  try {
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem("autotutor_user_track");
    localStorage.removeItem("autotutor_custom_tracks");
    localStorage.removeItem("autotutor_scheduled_tasks");
    localStorage.removeItem("autotutor_completed_lessons");
    localStorage.removeItem("autotutor_last_session");
    localStorage.removeItem("autotutor_active_topic");
    window.dispatchEvent(new CustomEvent("lesson-completion-changed"));
  } catch (e) {
    console.warn("Falha ao purgar armazenamento local:", e);
  }
}

export function useOnboardingGuard() {
  const [profile, setProfile] = useState<UserAssessmentProfile | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [shouldRedirectToOnboarding, setShouldRedirectToOnboarding] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true;

    async function checkState() {
      try {
        // Validação com o backend para assegurar que se o backend foi zerado, o cache do navegador também seja limpo
        const remote = await progressService.getProgress().catch(() => null);

        if (remote && (remote.onboarding_completed === false || (!remote.diagnostic_score && remote.total_submissions === 0))) {
          purgeAllClientStudyData();
          if (isMounted) {
            setProfile(null);
            setShouldRedirectToOnboarding(true);
            setIsLoading(false);
          }
          return;
        }

        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
          const parsed: UserAssessmentProfile = JSON.parse(stored);
          if (isMounted) {
            setProfile(parsed);
            if (!parsed.hasCompletedOnboarding) {
              setShouldRedirectToOnboarding(true);
            }
          }
        } else {
          if (isMounted) {
            setShouldRedirectToOnboarding(true);
          }
        }
      } catch {
        if (isMounted) {
          setShouldRedirectToOnboarding(true);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    checkState();

    return () => {
      isMounted = false;
    };
  }, []);

  const saveProfile = (newProfile: UserAssessmentProfile) => {
    setProfile(newProfile);
    setShouldRedirectToOnboarding(false);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(newProfile));
    } catch (e) {
      console.error("Falha ao persistir perfil de onboarding:", e);
    }
  };

  const resetAllData = async () => {
    try {
      await apiRequest("/api/progress/reset", { method: "POST" });
    } catch (e) {
      console.warn("Erro ao chamar reset no backend:", e);
    }
    purgeAllClientStudyData();
    setProfile(null);
    setShouldRedirectToOnboarding(true);
    if (typeof window !== "undefined") {
      window.location.href = "/onboarding";
    }
  };

  return {
    profile,
    isLoading,
    shouldRedirectToOnboarding,
    saveProfile,
    resetAllData,
  };
}
