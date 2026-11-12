"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Breadcrumbs } from "@/components/navigation/Breadcrumbs";
import { ActiveTrack } from "@/types/dashboard";
import { TrackMetadata } from "@/types/tracks";
import { CreateTrackModal } from "@/components/tracks/CreateTrackModal";
import { Badge } from "@/components/ui/Badge";
import { Compass, Plus, Sparkles, BookOpen, Trash2, ArrowRight, Wand2, RotateCcw } from "lucide-react";
import { lessonProgressService } from "@/services/lessonProgressService";
import { apiRequest } from "@/services/apiClient";
import { purgeAllClientStudyData } from "@/hooks/useOnboardingGuard";

interface CanonicalTrackDefinition {
  id: string;
  title: string;
  subject: string;
  retentionRate: number;
  difficultyTag: "Iniciante" | "Intermediário" | "Avançado";
  moduleLessonIds: string[];
}

const CANONICAL_PRESET_TRACKS: CanonicalTrackDefinition[] = [
  {
    id: "pilha",
    title: "Recursão, Pilhas & Estruturas Lineares",
    subject: "Fundamentos de Computação",
    retentionRate: 86,
    difficultyTag: "Iniciante",
    moduleLessonIds: ["recursion_foundations", "bfs_dfs_foundations", "binary_search_foundations"],
  },
  {
    id: "grafos",
    title: "Busca em Grafos (BFS/DFS & Menor Caminho)",
    subject: "Algoritmos em Grafos",
    retentionRate: 88,
    difficultyTag: "Iniciante",
    moduleLessonIds: ["bfs_dfs_foundations", "dijkstra_shortest_path"],
  },
  {
    id: "dp",
    title: "Programação Dinâmica Clássica",
    subject: "Otimização & Subestrutura",
    retentionRate: 72,
    difficultyTag: "Intermediário",
    moduleLessonIds: ["dp_knapsack_foundations"],
  },
  {
    id: "binary_search",
    title: "Busca Binária & Invariantes de Vetor",
    subject: "Divisão e Conquista",
    retentionRate: 84,
    difficultyTag: "Iniciante",
    moduleLessonIds: ["binary_search_foundations"],
  },
  {
    id: "trees",
    title: "Árvores Binárias & Árvores de Busca (BST)",
    subject: "Estruturas Hierárquicas",
    retentionRate: 80,
    difficultyTag: "Intermediário",
    moduleLessonIds: ["tree_foundations"],
  },
  {
    id: "prefix_sum",
    title: "Somas de Prefixos & Consultas Estáticas",
    subject: "Técnicas de Vetores",
    retentionRate: 92,
    difficultyTag: "Iniciante",
    moduleLessonIds: ["prefix_sum_foundations"],
  },
  {
    id: "greedy",
    title: "Algoritmos Gulosos (Greedy)",
    subject: "Estratégias Construtivas",
    retentionRate: 82,
    difficultyTag: "Iniciante",
    moduleLessonIds: ["greedy_foundations"],
  },
  {
    id: "segtree",
    title: "Segment Tree, DSU & Consultas em Intervalos",
    subject: "Estruturas Avançadas",
    retentionRate: 91,
    difficultyTag: "Avançado",
    moduleLessonIds: ["dsu_kruskal_mst"],
  },
];

const INITIAL_MOCK_TRACKS: ActiveTrack[] = [];

export default function TrilhasPage() {
  const router = useRouter();
  const [tracks, setTracks] = useState<ActiveTrack[]>(INITIAL_MOCK_TRACKS);
  const [customTracks, setCustomTracks] = useState<TrackMetadata[]>([]);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [quickPrompt, setQuickPrompt] = useState("");

  // Load custom tracks from localStorage and sync completion
  useEffect(() => {
    const loadTracks = () => {
      try {
        const activeList: ActiveTrack[] = [];

        // 1. Prioridade máxima: Trilha ativa personalizada do aluno (Onboarding / Diagnóstico)
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
          activeList.push(userActive);
        }

        // 2. Trilhas personalizadas geradas com IA
        const storedCustom = localStorage.getItem("autotutor_custom_tracks");
        if (storedCustom) {
          const parsed: TrackMetadata[] = JSON.parse(storedCustom);
          setCustomTracks(parsed);

          const customActive: ActiveTrack[] = parsed.map((t) => ({
            id: t.id,
            title: t.title,
            subject: t.subject,
            retentionRate: t.retentionRate || 80,
            difficultyTag: t.difficulty,
            completedModules: (t.modules || []).filter(
              (m) => lessonProgressService.isLessonCompleted(m.id) || m.completed
            ).length,
            totalModules: (t.modules || []).length || 3,
          }));

          activeList.push(...customActive);
        }

        setTracks(activeList);
      } catch (e) {
        console.error("Falha ao carregar trilhas personalizadas:", e);
      }
    };

    loadTracks();
    window.addEventListener("lesson-completion-changed", loadTracks);
    return () => window.removeEventListener("lesson-completion-changed", loadTracks);
  }, []);

  const handleTrackCreated = (newTrack: TrackMetadata) => {
    const updated = [newTrack, ...customTracks];
    setCustomTracks(updated);
    try {
      localStorage.setItem("autotutor_custom_tracks", JSON.stringify(updated));
    } catch (e) {
      console.error("Erro ao salvar trilha no localStorage:", e);
    }

    const newActive: ActiveTrack = {
      id: newTrack.id,
      title: newTrack.title,
      subject: newTrack.subject,
      retentionRate: newTrack.retentionRate,
      difficultyTag: newTrack.difficulty,
      completedModules: 0,
      totalModules: newTrack.modules.length,
    };

    setTracks([newActive, ...tracks.filter((t) => t.id !== newTrack.id)]);
  };

  const handleDeleteCustomTrack = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    const filteredCustom = customTracks.filter((t) => t.id !== id);
    setCustomTracks(filteredCustom);
    try {
      localStorage.setItem("autotutor_custom_tracks", JSON.stringify(filteredCustom));
    } catch (e) {
      console.error("Erro ao salvar trilha no localStorage:", e);
    }
    setTracks(tracks.filter((t) => t.id !== id));
  };

  const handleResetAll = async () => {
    if (confirm("Deseja realmente zerar todas as trilhas, histórico e reiniciar sua conta do zero?")) {
      try {
        await apiRequest("/api/progress/reset", { method: "POST" });
      } catch (e) {
        console.warn("Erro ao resetar no backend:", e);
      }
      purgeAllClientStudyData();
      router.push("/onboarding");
    }
  };

  const breadcrumbs = [
    { label: "Início", href: "/" },
    { label: "Trilhas de Aprendizado" },
  ];

  return (
    <main className="flex-1 flex flex-col min-w-0 pb-20 lg:pb-8">
      <header className="px-6 py-4 border-b border-border bg-card/40 backdrop-blur-sm sticky top-0 z-30">
        <Breadcrumbs items={breadcrumbs} />
      </header>

      <div className="max-w-6xl w-full mx-auto px-4 sm:px-6 py-8 space-y-6">
        {/* Top Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-primary/10 flex items-center justify-center text-primary shrink-0">
              <Compass className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-2xl font-extrabold tracking-tight text-foreground">
                Trilhas de Especialização
              </h1>
              <p className="text-xs text-muted-foreground mt-0.5">
                Roteiros estruturados do básico ao avançado com verificação prática no juiz C++.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-auto shrink-0">
            <button
              type="button"
              onClick={handleResetAll}
              className="flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl text-xs font-semibold text-muted-foreground hover:text-rose-400 hover:bg-rose-500/10 border border-border transition-colors cursor-pointer"
              title="Zera todas as trilhas, histórico e recomeça a conta do zero"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Zerar Tudo</span>
            </button>

            <button
              type="button"
              onClick={() => {
                setQuickPrompt("");
                setIsCreateModalOpen(true);
              }}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold bg-secondary hover:bg-accent text-foreground border border-border shadow-sm transition-all"
            >
              <Plus className="w-4 h-4 text-primary" />
              <span>Criar Manualmente</span>
            </button>
          </div>
        </div>

        {/* AI Track Generator Hero Bar */}
        <div className="p-5 sm:p-6 rounded-3xl border border-primary/25 bg-gradient-to-r from-primary/10 via-card/70 to-card/40 backdrop-blur-md shadow-sm space-y-3">
          <div className="flex items-center gap-2 text-xs font-bold text-primary">
            <Sparkles className="w-4 h-4" />
            <span>Criador Inteligente de Trilhas com IA</span>
          </div>
          <p className="text-xs text-muted-foreground max-w-2xl leading-relaxed">
            Diga o que você deseja estudar e a IA pedagógica estruturará uma trilha com módulos progressivos, tempos estimados e conteúdos práticos para você treinar no Juiz.
          </p>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              setIsCreateModalOpen(true);
            }}
            className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 pt-1"
          >
            <div className="relative flex-1">
              <input
                type="text"
                value={quickPrompt}
                onChange={(e) => setQuickPrompt(e.target.value)}
                placeholder="Ex: Quero uma trilha sobre estrutura de dados com Árvore Binária e Árvore Balanceada..."
                className="w-full bg-secondary/90 border border-border rounded-xl px-4 py-2.5 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary font-medium pr-10"
              />
              <Sparkles className="w-4 h-4 text-primary absolute right-3.5 top-1/2 -translate-y-1/2 pointer-events-none opacity-60" />
            </div>
            <button
              type="submit"
              className="flex items-center justify-center gap-1.5 px-5 py-2.5 rounded-xl text-xs font-bold bg-primary text-primary-foreground hover:bg-primary-hover shadow-sm transition-all shrink-0"
            >
              <Wand2 className="w-3.5 h-3.5" />
              <span>Gerar Trilha com IA</span>
            </button>
          </form>
        </div>

        {/* Tracks Grid or Empty State */}
        {tracks.length === 0 ? (
          <div className="p-8 sm:p-12 text-center rounded-3xl border border-dashed border-border bg-card/40 backdrop-blur-sm space-y-4">
            <div className="w-14 h-14 mx-auto rounded-2xl bg-primary/10 flex items-center justify-center text-primary">
              <Compass className="w-7 h-7" />
            </div>
            <div className="max-w-md mx-auto space-y-1.5">
              <h3 className="text-base font-bold text-foreground">Nenhuma Trilha Ativa</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Você não possui trilhas ativas no momento. Faça o teste diagnóstico inicial para calibrar seu nível e gerar seu plano adaptativo, ou crie uma trilha sob medida usando IA.
              </p>
            </div>
            <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
              <button
                type="button"
                onClick={() => router.push("/onboarding")}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold bg-primary text-primary-foreground hover:bg-primary-hover shadow-sm transition-all"
              >
                <span>Fazer Diagnóstico de Nivelamento</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                onClick={() => setIsCreateModalOpen(true)}
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold bg-secondary hover:bg-secondary/80 text-foreground border border-border transition-all"
              >
                <Sparkles className="w-3.5 h-3.5 text-primary" />
                <span>Criar com IA</span>
              </button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {tracks.map((track) => {
              const isCustom = customTracks.some((c) => c.id === track.id);
              return (
                <div
                  key={track.id}
                  onClick={() => router.push(`/trilhas/${track.id}`)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      router.push(`/trilhas/${track.id}`);
                    }
                  }}
                  className="p-5 rounded-2xl border border-border bg-card/60 backdrop-blur-sm hover:border-primary/50 hover:bg-card/90 transition-all cursor-pointer flex flex-col justify-between space-y-4 group relative"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-[10px] text-primary uppercase font-bold tracking-wider font-mono">
                        {track.subject}
                      </span>
                      <div className="flex items-center gap-1.5">
                        {isCustom && (
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 font-semibold border border-blue-500/20">
                            Personalizada
                          </span>
                        )}
                        <Badge variant={track.difficultyTag === "Iniciante" ? "secondary" : "primary"}>
                          {track.difficultyTag}
                        </Badge>
                        {isCustom && (
                          <button
                            type="button"
                            onClick={(e) => handleDeleteCustomTrack(e, track.id)}
                            title="Excluir trilha personalizada"
                            className="p-1 rounded text-muted-foreground hover:text-rose-400 hover:bg-rose-500/10 transition-colors ml-1"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </div>
                    </div>

                    <h3 className="font-bold text-sm text-foreground group-hover:text-primary transition-colors leading-snug">
                      {track.title}
                    </h3>
                  </div>

                  <div className="space-y-2 pt-2 border-t border-border">
                    <div className="flex justify-between text-[11px] text-muted-foreground font-mono">
                      <span>
                        {track.completedModules} de {track.totalModules} módulos
                      </span>
                      <span className="text-emerald-400 font-medium">{track.retentionRate}% retenção</span>
                    </div>
                    <div className="w-full h-1.5 bg-secondary rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary rounded-full transition-all"
                        style={{
                          width: `${Math.min(
                            100,
                            Math.max(10, (track.completedModules / Math.max(1, track.totalModules)) * 100)
                          )}%`,
                        }}
                      />
                    </div>
                    <div className="flex items-center justify-end text-[11px] text-primary font-semibold pt-1 group-hover:translate-x-1 transition-transform">
                      <span>Acessar Trilha</span>
                      <ArrowRight className="w-3.5 h-3.5 ml-1" />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Catálogo de Sugestões Opcionais */}
        <details className="group pt-4 border-t border-border/80">
          <summary className="flex items-center justify-between cursor-pointer text-xs font-bold text-muted-foreground hover:text-foreground py-2 select-none">
            <span className="flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-primary" />
              <span>Explorar Modelos Sugeridos do Catálogo (Opcional)</span>
            </span>
            <span className="text-[10px] text-muted-foreground group-open:rotate-180 transition-transform">▼</span>
          </summary>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-3">
            {CANONICAL_PRESET_TRACKS.map((t) => (
              <div
                key={t.id}
                onClick={() => router.push(`/trilhas/${t.id}`)}
                className="p-3.5 rounded-xl border border-border/70 bg-card/40 hover:bg-card hover:border-primary/40 transition-all cursor-pointer space-y-2 group"
              >
                <div className="flex items-center justify-between text-[10px] text-muted-foreground">
                  <span className="uppercase font-mono">{t.subject}</span>
                  <Badge variant="secondary">{t.difficultyTag}</Badge>
                </div>
                <h4 className="text-xs font-bold text-foreground group-hover:text-primary transition-colors leading-snug">
                  {t.title}
                </h4>
                <div className="flex items-center justify-between text-[10px] text-muted-foreground pt-1 border-t border-border/50">
                  <span>{t.moduleLessonIds.length} módulos</span>
                  <span className="text-primary font-semibold flex items-center gap-0.5">
                    Ver modelo <ArrowRight className="w-2.5 h-2.5" />
                  </span>
                </div>
              </div>
            ))}
          </div>
        </details>
      </div>

      <CreateTrackModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onTrackCreated={handleTrackCreated}
        initialPrompt={quickPrompt}
      />
    </main>
  );
}
