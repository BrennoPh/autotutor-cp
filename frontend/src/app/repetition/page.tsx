"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Breadcrumbs } from "@/components/navigation/Breadcrumbs";
import { EbbinghausSchedule } from "@/components/repetition/EbbinghausSchedule";
import { MasteryScoreCard } from "@/components/repetition/MasteryScoreCard";
import { FlashcardStudySession } from "@/components/repetition/FlashcardStudySession";
import { RepetitionItem, TopicMastery } from "@/types/repetition";
import { Flame, Brain, Award, Calendar, CheckCircle2 } from "lucide-react";

const INITIAL_SCHEDULE: RepetitionItem[] = [
  {
    id: "rep-1",
    topicId: "bfs-queue",
    topicTitle: "BFS: Invariante da Fila e Ciclo Multi-Source",
    category: "Grafos",
    retentionRate: 42,
    lastReviewedAt: "2026-11-04",
    nextReviewDue: "Hoje",
    intervalDays: 2,
    repetitionsCount: 3,
    urgency: "urgent",
    flashcardsCount: 8,
  },
  {
    id: "rep-2",
    topicId: "dfs-tree",
    topicTitle: "Classificação de Arestas DFS (Árvore, Retorno, Avanço, Cruzamento)",
    category: "Grafos",
    retentionRate: 58,
    lastReviewedAt: "2026-11-05",
    nextReviewDue: "Hoje",
    intervalDays: 3,
    repetitionsCount: 2,
    urgency: "due-today",
    flashcardsCount: 12,
  },
  {
    id: "rep-3",
    topicId: "tarjan-scc",
    topicTitle: "Componentes Fortemente Conexos: Algoritmo de Tarjan",
    category: "Grafos Avançados",
    retentionRate: 74,
    lastReviewedAt: "2026-11-03",
    nextReviewDue: "Em 2 dias",
    intervalDays: 7,
    repetitionsCount: 4,
    urgency: "upcoming",
    flashcardsCount: 15,
  },
];

const INITIAL_TOPICS: TopicMastery[] = [
  {
    topicId: "bfs",
    topicName: "Busca em Largura (BFS)",
    category: "Grafos Básicos",
    masteryScore: 85,
    questionsSolved: 17,
    totalQuestions: 20,
    lastPracticed: "Hoje",
    trend: "up",
  },
  {
    topicId: "dfs",
    topicName: "Busca em Profundidade (DFS) & Ciclos",
    category: "Grafos Básicos",
    masteryScore: 68,
    questionsSolved: 11,
    totalQuestions: 18,
    lastPracticed: "Ontem",
    trend: "stable",
  },
  {
    topicId: "tarjan",
    topicName: "Tarjan & SCCs (Low-link Values)",
    category: "Grafos Avançados",
    masteryScore: 42,
    questionsSolved: 5,
    totalQuestions: 15,
    lastPracticed: "3 dias atrás",
    trend: "down",
  },
  {
    topicId: "dag-topo",
    topicName: "Ordenação Topológica em DAGs (Kahn)",
    category: "Grafos Dirigidos",
    masteryScore: 92,
    questionsSolved: 14,
    totalQuestions: 15,
    lastPracticed: "5 dias atrás",
    trend: "up",
  },
];

function RepetitionHubContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const autoStart = searchParams.get("autoStart") === "true";
  const topicFilter = searchParams.get("topic");

  const [scheduleItems, setScheduleItems] = useState<RepetitionItem[]>(INITIAL_SCHEDULE);
  const [topics, setTopics] = useState<TopicMastery[]>(INITIAL_TOPICS);
  const [activeReviewModal, setActiveReviewModal] = useState<string | null>(() => {
    return autoStart ? (topicFilter || "all") : null;
  });

  useEffect(() => {
    if (autoStart && !activeReviewModal) {
      setActiveReviewModal(topicFilter || "all");
    }
  }, [autoStart, topicFilter, activeReviewModal]);

  const breadcrumbs = [
    { label: "Dashboard", href: "/" },
    { label: "Hub de Progresso & Repetição Espaçada" },
  ];

  const handleStartReview = (itemId?: string) => {
    setActiveReviewModal(itemId || "all");
  };

  const handlePracticeTopic = (topicId: string) => {
    let problem = "graph";
    const t = (topicId || "").toLowerCase();
    if (t.includes("tree") || t.includes("arvor")) problem = "tree";
    else if (t.includes("binar") || t.includes("busca")) problem = "binary";
    else if (t.includes("dp") || t.includes("dinam")) problem = "dp";
    else if (t.includes("greedy") || t.includes("gulos")) problem = "greedy";
    else if (t.includes("prefix")) problem = "prefix";
    else if (t.includes("segtree") || t.includes("segment")) problem = "segment_tree";
    else if (t.includes("recurs")) problem = "tree";
    router.push(`/workspace?topic=${encodeURIComponent(topicId)}&problem=${encodeURIComponent(problem)}&mode=arena`);
  };

  return (
    <>
      <main className="flex-1 flex flex-col min-w-0 pb-20 lg:pb-8">
        <header className="px-6 py-4 border-b border-border bg-card/40 backdrop-blur-sm sticky top-0 z-30">
          <Breadcrumbs items={breadcrumbs} />
        </header>

        <div className="max-w-6xl w-full mx-auto px-4 sm:px-6 py-6 space-y-8">
          {/* Hero Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground">
                Hub de Repetição Espaçada & Retenção
              </h1>
              <p className="text-sm text-muted-foreground mt-1">
                Acompanhe o domínio da sua memória com base no algoritmo de repetição intervalada e na curva de Ebbinghaus.
              </p>
            </div>
          </div>

          {/* Stat Overview Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl border border-border bg-card shadow-sm flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0">
                <Brain className="w-5 h-5" />
              </div>
              <div>
                <span className="text-xs text-muted-foreground block">Retenção Estimada</span>
                <span className="text-xl font-bold font-mono text-foreground">78.4%</span>
              </div>
            </div>

            <div className="p-4 rounded-xl border border-border bg-card shadow-sm flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-amber-500/10 text-amber-500 flex items-center justify-center shrink-0">
                <Calendar className="w-5 h-5" />
              </div>
              <div>
                <span className="text-xs text-muted-foreground block">Revisões para Hoje</span>
                <span className="text-xl font-bold font-mono text-foreground">2 tópicos (20 cards)</span>
              </div>
            </div>

            <div className="p-4 rounded-xl border border-border bg-card shadow-sm flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-emerald-500/10 text-emerald-500 flex items-center justify-center shrink-0">
                <Award className="w-5 h-5" />
              </div>
              <div>
                <span className="text-xs text-muted-foreground block">Tópicos Dominados</span>
                <span className="text-xl font-bold font-mono text-foreground">12 / 16</span>
              </div>
            </div>

            <div className="p-4 rounded-xl border border-border bg-card shadow-sm flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-amber-500/10 text-amber-500 flex items-center justify-center shrink-0">
                <Flame className="w-5 h-5 fill-current" />
              </div>
              <div>
                <span className="text-xs text-muted-foreground block">Streak de Revisão</span>
                <span className="text-xl font-bold font-mono text-foreground">7 dias</span>
              </div>
            </div>
          </div>

          {/* Section 1: Ebbinghaus Schedule */}
          <section className="p-6 rounded-2xl border border-border bg-card shadow-sm space-y-6">
            <EbbinghausSchedule items={scheduleItems} onStartReview={handleStartReview} />
          </section>

          {/* Section 2: Mastery by Topic */}
          <section className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-base font-bold text-foreground">Score de Domínio por Tópico</h2>
                <p className="text-xs text-muted-foreground">
                  Métricas ponderadas por acertos em testes, velocidade de resolução e recência de revisão.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {topics.map((topic) => (
                <MasteryScoreCard
                  key={topic.topicId}
                  topic={topic}
                  onPracticeClick={handlePracticeTopic}
                />
              ))}
            </div>
          </section>
        </div>
      </main>

      {/* Active Interactive Flashcards Review Session */}
      {activeReviewModal && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 animate-fade-in"
        >
          <FlashcardStudySession
            onClose={() => setActiveReviewModal(null)}
            onComplete={() => setActiveReviewModal(null)}
          />
        </div>
      )}
    </>
  );
}

export default function RepetitionHubPage() {
  return (
    <Suspense fallback={<div className="p-10 text-xs text-muted-foreground">Carregando Hub de Repetição...</div>}>
      <RepetitionHubContent />
    </Suspense>
  );
}
