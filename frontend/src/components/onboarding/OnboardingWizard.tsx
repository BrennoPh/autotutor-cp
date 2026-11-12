import React, { useState } from "react";
import {
  TargetGoal,
  PreferredLanguage,
  UserAssessmentProfile,
  CustomTrack,
} from "@/types/onboarding";
import {
  DIAGNOSTIC_QUESTIONS,
  evaluateDiagnostic,
  generateCustomTrack,
  generateStudySchedule,
} from "@/core/adaptiveRoadmapEngine";
import {
  Target,
  Clock,
  Code,
  Calendar,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Award,
  Layers,
} from "lucide-react";
import { Badge } from "@/components/ui/Badge";

interface OnboardingWizardProps {
  userId?: string;
  onComplete: (profile: UserAssessmentProfile, track: CustomTrack) => void;
}

export function OnboardingWizard({ userId = "user-1", onComplete }: OnboardingWizardProps) {
  const [step, setStep] = useState<1 | 2 | 3>(1);

  // Form State (Step 1)
  const [targetGoal, setTargetGoal] = useState<TargetGoal>("graphs");
  const [availableHours, setAvailableHours] = useState<number>(1);
  const [activeDays, setActiveDays] = useState<number[]>([1, 2, 3, 4, 5]); // Seg a Sex
  const [preferredLanguage, setPreferredLanguage] = useState<PreferredLanguage>("cpp");

  // Quiz State (Step 2)
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState<number>(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});

  // Generated Result State (Step 3)
  const [finalProfile, setFinalProfile] = useState<UserAssessmentProfile | null>(null);
  const [finalTrack, setFinalTrack] = useState<CustomTrack | null>(null);

  // Toggle active days
  const toggleDay = (dayIndex: number) => {
    setActiveDays((prev) =>
      prev.includes(dayIndex) ? prev.filter((d) => d !== dayIndex) : [...prev, dayIndex].sort()
    );
  };

  const dayLabels = [
    { index: 0, label: "Dom" },
    { index: 1, label: "Seg" },
    { index: 2, label: "Ter" },
    { index: 3, label: "Qua" },
    { index: 4, label: "Qui" },
    { index: 5, label: "Sex" },
    { index: 6, label: "Sáb" },
  ];

  const goalsList: { id: TargetGoal; title: string; desc: string }[] = [
    { id: "graphs", title: "Grafos & Algoritmos de Rede", desc: "BFS, DFS, Dijkstra, Tarjan e Fluxo" },
    { id: "dp", title: "Programação Dinâmica", desc: "Memoization, Tabulação e Otimizações" },
    { id: "obi", title: "OBI (Olimpíada Brasileira)", desc: "Preparação para Nível 1, 2 e Sênior" },
    { id: "icpc", title: "Maratona ICPC / SBC", desc: "Problemas competitivos avançados" },
    { id: "interviews", title: "Entrevistas Tech (Big Techs)", desc: "LeetCode patterns e Clean Code" },
    { id: "foundations", title: "Fundamentos & Estruturas", desc: "Arrays, Recursão, Pilhas e Filas" },
  ];

  // Submit Step 1
  const handleStartQuiz = () => {
    setStep(2);
  };

  // Select Option in Quiz
  const handleSelectOption = (questionId: string, optionId: string) => {
    setAnswers((prev) => ({ ...prev, [questionId]: optionId }));
  };

  // Next Question or Finish Quiz
  const handleNextQuestion = () => {
    if (currentQuestionIndex < DIAGNOSTIC_QUESTIONS.length - 1) {
      setCurrentQuestionIndex((prev) => prev + 1);
    } else {
      // Conclui quiz e processa diagnóstico
      const diagnosticResult = evaluateDiagnostic(answers);
      const profile: UserAssessmentProfile = {
        userId,
        hasCompletedOnboarding: true,
        targetGoal,
        availableHoursPerDay: availableHours,
        activeDaysOfWeek: activeDays.length > 0 ? activeDays : [1, 2, 3, 4, 5],
        preferredLanguage,
        diagnosticResult,
      };

      const track = generateCustomTrack(profile);
      setFinalProfile(profile);
      setFinalTrack(track);
      setStep(3);
    }
  };

  const currentQ = DIAGNOSTIC_QUESTIONS[currentQuestionIndex];
  const isOptionSelected = answers[currentQ?.id] !== undefined;

  return (
    <div className="w-full max-w-3xl mx-auto p-4 sm:p-8 bg-card border border-border rounded-3xl shadow-xl space-y-6">
      {/* Step Indicator */}
      <div className="flex items-center justify-between border-b border-border pb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary/20 text-primary flex items-center justify-center font-bold text-sm">
            {step}
          </div>
          <div>
            <h2 className="text-sm font-bold text-foreground">
              {step === 1 && "1. Intenção & Disponibilidade"}
              {step === 2 && "2. Teste Diagnóstico Fidedigno"}
              {step === 3 && "3. Sua Trilha Adaptativa Personalizada"}
            </h2>
            <span className="text-[11px] text-muted-foreground">
              {step === 1 && "Defina seus objetivos e ritmo de estudo"}
              {step === 2 && `Questão ${currentQuestionIndex + 1} de ${DIAGNOSTIC_QUESTIONS.length}`}
              {step === 3 && "Diagnóstico processado e calendário preditivo gerado"}
            </span>
          </div>
        </div>

        {/* Mini Step Tracker */}
        <div className="flex items-center gap-1.5">
          <div className={`w-3 h-1.5 rounded-full ${step >= 1 ? "bg-primary" : "bg-secondary"}`} />
          <div className={`w-3 h-1.5 rounded-full ${step >= 2 ? "bg-primary" : "bg-secondary"}`} />
          <div className={`w-3 h-1.5 rounded-full ${step >= 3 ? "bg-primary" : "bg-secondary"}`} />
        </div>
      </div>

      {/* ================= STEP 1: OBJETIVOS E RITMO ================= */}
      {step === 1 && (
        <div className="space-y-6 animate-fade-in">
          {/* Metas */}
          <div className="space-y-3">
            <label className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
              <Target className="w-4 h-4 text-primary" />
              O que você quer dominar?
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {goalsList.map((g) => (
                <button
                  key={g.id}
                  onClick={() => setTargetGoal(g.id)}
                  className={`p-3.5 rounded-2xl border text-left transition-all ${
                    targetGoal === g.id
                      ? "border-primary bg-primary/10 shadow-sm"
                      : "border-border hover:bg-secondary/60"
                  }`}
                >
                  <div className="font-bold text-xs text-foreground mb-0.5">{g.title}</div>
                  <div className="text-[11px] text-muted-foreground">{g.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Horas e Dias Ativos */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-2">
            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                <Clock className="w-4 h-4 text-primary" />
                Tempo de Estudo Diário
              </label>
              <div className="grid grid-cols-4 gap-2">
                {[0.5, 1, 2, 3].map((h) => (
                  <button
                    key={h}
                    onClick={() => setAvailableHours(h)}
                    className={`py-2 rounded-xl border text-xs font-semibold transition-colors ${
                      availableHours === h
                        ? "bg-primary text-primary-foreground border-primary"
                        : "border-border hover:bg-secondary text-foreground"
                    }`}
                  >
                    {h}h/dia
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                <Code className="w-4 h-4 text-primary" />
                Linguagem Preferida
              </label>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { id: "cpp", label: "C++ (Padrão)" },
                  { id: "python", label: "Python 3" },
                  { id: "java", label: "Java" },
                ].map((lang) => (
                  <button
                    key={lang.id}
                    onClick={() => setPreferredLanguage(lang.id as PreferredLanguage)}
                    className={`py-2 rounded-xl border text-xs font-semibold transition-colors ${
                      preferredLanguage === lang.id
                        ? "bg-primary text-primary-foreground border-primary"
                        : "border-border hover:bg-secondary text-foreground"
                    }`}
                  >
                    {lang.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Dias da semana */}
          <div className="space-y-2 pt-2">
            <label className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
              <Calendar className="w-4 h-4 text-primary" />
              Dias Ativos na Semana
            </label>
            <div className="flex flex-wrap gap-2">
              {dayLabels.map((d) => {
                const isActive = activeDays.includes(d.index);
                return (
                  <button
                    key={d.index}
                    onClick={() => toggleDay(d.index)}
                    className={`px-3 py-1.5 rounded-xl border text-xs font-medium transition-all ${
                      isActive
                        ? "bg-primary/20 border-primary text-primary font-bold"
                        : "border-border text-muted-foreground hover:bg-secondary"
                    }`}
                  >
                    {d.label}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="pt-4 flex justify-end">
            <button
              onClick={handleStartQuiz}
              className="flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground text-xs font-bold rounded-xl hover:bg-primary-hover shadow-md transition-all"
            >
              <span>Iniciar Teste Diagnóstico Rápido</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* ================= STEP 2: MICRO-QUIZ DIAGNÓSTICO ================= */}
      {step === 2 && currentQ && (
        <div className="space-y-6 animate-fade-in">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Badge variant="primary">{currentQ.topic}</Badge>
              <span className="text-[11px] text-muted-foreground">
                Nível: {currentQ.difficulty}
              </span>
            </div>
            <h3 className="text-base font-bold text-foreground leading-snug">{currentQ.question}</h3>
          </div>

          {currentQ.codeSnippet && (
            <div className="p-3 bg-slate-950/80 rounded-xl border border-slate-800 font-mono text-xs text-slate-200 overflow-x-auto leading-relaxed">
              <pre>{currentQ.codeSnippet}</pre>
            </div>
          )}

          <div className="space-y-2.5">
            {currentQ.options.map((opt) => {
              const isSelected = answers[currentQ.id] === opt.id;
              return (
                <button
                  key={opt.id}
                  onClick={() => handleSelectOption(currentQ.id, opt.id)}
                  className={`w-full p-3.5 rounded-xl border text-left text-xs transition-all flex items-start gap-3 ${
                    isSelected
                      ? "border-primary bg-primary/10 text-foreground font-semibold shadow-sm"
                      : "border-border hover:bg-secondary/60 text-muted-foreground"
                  }`}
                >
                  <span
                    className={`w-5 h-5 rounded-md flex items-center justify-center shrink-0 text-[11px] font-bold ${
                      isSelected ? "bg-primary text-primary-foreground" : "bg-secondary text-muted-foreground"
                    }`}
                  >
                    {opt.id.toUpperCase()}
                  </span>
                  <span className="leading-relaxed">{opt.text}</span>
                </button>
              );
            })}
          </div>

          <div className="pt-4 flex items-center justify-between">
            <span className="text-xs text-muted-foreground">
              {currentQuestionIndex + 1} de {DIAGNOSTIC_QUESTIONS.length} respondidas
            </span>
            <button
              onClick={handleNextQuestion}
              disabled={!isOptionSelected}
              className="flex items-center gap-2 px-6 py-2.5 bg-primary text-primary-foreground text-xs font-bold rounded-xl hover:bg-primary-hover disabled:opacity-40 transition-all"
            >
              <span>
                {currentQuestionIndex === DIAGNOSTIC_QUESTIONS.length - 1 ? "Finalizar Diagnóstico" : "Próxima Questão"}
              </span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* ================= STEP 3: RESULTADO & TRANSIÇÃO ================= */}
      {step === 3 && finalProfile && finalTrack && (
        <div className="space-y-6 animate-fade-in">
          {/* Header do Resultado */}
          <div className="p-6 rounded-2xl bg-gradient-to-r from-primary/10 to-indigo-500/10 border border-primary/30 flex items-center justify-between flex-wrap gap-4">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-primary block mb-1">
                Diagnóstico Concluído
              </span>
              <h3 className="text-xl font-extrabold text-foreground">
                Nível Aferido: {finalProfile.diagnosticResult?.entryLevel} ({finalProfile.diagnosticResult?.score}%)
              </h3>
              <p className="text-xs text-muted-foreground mt-1 max-w-md">
                Sua trilha preditiva foi calibrada priorizando tópicos essenciais para eliminar as lacunas identificadas.
              </p>
            </div>
            <div className="w-16 h-16 rounded-2xl bg-primary/20 flex items-center justify-center text-primary">
              <Award className="w-8 h-8" />
            </div>
          </div>

          {/* Pontos Fortes e Lacunas */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl border border-border bg-card space-y-2">
              <span className="text-xs font-bold text-emerald-500 flex items-center gap-1.5 uppercase tracking-wide">
                <CheckCircle2 className="w-4 h-4" />
                Conceitos Dominados
              </span>
              <ul className="text-xs text-muted-foreground space-y-1">
                {finalProfile.diagnosticResult?.strongTopics.length === 0 ? (
                  <li className="italic">Nenhum tópico dominado com 100% no diagnóstico.</li>
                ) : (
                  finalProfile.diagnosticResult?.strongTopics.map((t, idx) => <li key={idx}>✓ {t}</li>)
                )}
              </ul>
            </div>

            <div className="p-4 rounded-xl border border-border bg-card space-y-2">
              <span className="text-xs font-bold text-amber-500 flex items-center gap-1.5 uppercase tracking-wide">
                <AlertTriangle className="w-4 h-4" />
                Lacunas a Sanar com Prioridade
              </span>
              <ul className="text-xs text-muted-foreground space-y-1">
                {finalProfile.diagnosticResult?.gapTopics.map((t, idx) => (
                  <li key={idx}>• {t} (Priorizado na Trilha)</li>
                ))}
              </ul>
            </div>
          </div>

          {/* Milestones da Trilha */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
              <Layers className="w-4 h-4 text-primary" />
              Marcos da Sua Trilha Personalizada ({finalTrack.totalWeeks} Semanas)
            </h4>
            <div className="space-y-2.5">
              {finalTrack.milestones.map((m) => (
                <div
                  key={m.weekNumber}
                  className="p-3.5 rounded-xl border border-border bg-card flex items-center justify-between gap-4"
                >
                  <div className="flex items-center gap-3">
                    <span className="w-7 h-7 rounded-lg bg-secondary text-foreground text-xs font-bold flex items-center justify-center shrink-0">
                      S{m.weekNumber}
                    </span>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-foreground">{m.title}</span>
                        {m.isPrerequisiteRefinement && (
                          <Badge variant="warning">Reforço de Base</Badge>
                        )}
                      </div>
                      <span className="text-[11px] text-muted-foreground block mt-0.5">
                        {m.keyConcepts.join(" • ")}
                      </span>
                    </div>
                  </div>
                  <span className="text-xs font-mono text-muted-foreground shrink-0">{m.estimatedHours}h estimadas</span>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-4 flex justify-end">
            <button
              onClick={() => onComplete(finalProfile, finalTrack)}
              className="flex items-center gap-2 px-6 py-2.5 bg-blue-600 text-white text-xs font-medium rounded-md hover:bg-blue-500 shadow-sm transition-colors"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>Concluir Onboarding & Abrir Calendário</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
