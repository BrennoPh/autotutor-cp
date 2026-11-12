"use client";

import React, { useState, useEffect, useMemo } from "react";
import { useParams, useRouter } from "next/navigation";
import { Breadcrumbs } from "@/components/navigation/Breadcrumbs";
import {
  Compass,
  ArrowRight,
  BookOpen,
  Code2,
  CheckCircle2,
  Clock,
  Network,
  ChevronRight,
  Layers,
} from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { TrackMetadata, TrackModule } from "@/types/tracks";
import { lessonProgressService } from "@/services/lessonProgressService";

const PRESET_TRACKS_METADATA: Record<string, TrackMetadata> = {
  pilha: {
    id: "pilha",
    title: "Recursão, Pilhas & Estruturas Lineares",
    subject: "Fundamentos de Computação",
    difficulty: "Iniciante",
    retentionRate: 86,
    description:
      "Domine a mecânica da Pilha de Execução (Call Stack), alocação de frames em memória, prevenção de Stack Overflow e a transição entre estruturas lineares (vetores, pilhas LIFO e filas FIFO).",
    modules: [
      {
        id: "recursion_foundations",
        title: "Módulo 1: Call Stack, Recursão e Prevenção de Estouro de Pilha",
        description: "Mecânica de empilhamento de frames, caso base, retorno e rastreamento assintótico formal.",
        estimatedMinutes: 30,
        completed: false,
        lessons: ["Pilha de Execução em C++", "Prevenção de Stack Overflow", "Passagem por Valor vs Referência"],
      },
      {
        id: "bfs_dfs_foundations",
        title: "Módulo 2: Pilhas LIFO (DFS) vs Filas FIFO (BFS)",
        description: "Comparação prática entre estruturas de pilha na DFS e filas de processamento em camadas.",
        estimatedMinutes: 35,
        completed: false,
        lessons: ["std::stack e std::queue", "Invariantes de travessia linear e flood fill"],
      },
      {
        id: "binary_search_foundations",
        title: "Módulo 3: Invariantes em Vetores Lineares e Busca Binária",
        description: "Divisão do espaço de busca em O(log N) em vetores ordenados contíguos.",
        estimatedMinutes: 35,
        completed: false,
        lessons: ["lower_bound e upper_bound", "Invariantes de vetores contíguos"],
      },
    ],
  },
  grafos: {
    id: "grafos",
    title: "Busca em Grafos (BFS/DFS)",
    subject: "Algoritmos e Estruturas de Dados",
    difficulty: "Iniciante",
    retentionRate: 88,
    description:
      "Domine as duas travessias fundamentais da maratona de programação. Aprenda a invariante de camadas na Fila da BFS e a classificação das quatro arestas na recursão da DFS.",
    modules: [
      {
        id: "bfs_dfs_foundations",
        title: "Módulo 1: Modelagem e Matrizes vs Listas de Adjacência",
        description: "Representação eficiente de vértices e arestas em memória e tempo O(V+E).",
        estimatedMinutes: 20,
        completed: false,
        lessons: ["Listas de Adjacência em C++ e Python", "Grafos Direcionados vs Não-Direcionados"],
      },
      {
        id: "dijkstra_shortest_path",
        title: "Módulo 2: Busca em Largura & Menor Caminho (Dijkstra)",
        description: "Exploração concêntrica, filas de prioridade (heap) e cálculo de distâncias mínimas.",
        estimatedMinutes: 35,
        completed: false,
        lessons: ["Dijkstra em O(E log V)", "Fila de Prioridade em C++"],
      },
    ],
  },
  dp: {
    id: "dp",
    title: "Programação Dinâmica Clássica",
    subject: "Otimização e Subestrutura Ótima",
    difficulty: "Intermediário",
    retentionRate: 72,
    description:
      "Aprenda a definir estados mínimos, transições sem dependência cíclica e técnicas de memoization e tabela iterativa (bottom-up).",
    modules: [
      {
        id: "dp_knapsack_foundations",
        title: "Módulo 1: Memoization e Mochila 0/1",
        description: "Transformando soluções exponenciais O(2^N) em polinomiais O(N*W).",
        estimatedMinutes: 30,
        completed: false,
        lessons: ["Fibonacci e Escadas", "Problema da Mochila 0/1"],
      },
    ],
  },
  binary_search: {
    id: "binary_search",
    title: "Busca Binária & Invariantes de Vetor",
    subject: "Divisão e Conquista",
    difficulty: "Iniciante",
    retentionRate: 84,
    description: "Pesquisa logarítmica em vetores ordenados, invariantes de ponteiros e busca binária na resposta.",
    modules: [
      {
        id: "binary_search_foundations",
        title: "Módulo 1: Fundamentos de Busca Binária O(log N)",
        description: "Ponteiros low/high, meio sem overflow e condições de parada estritas.",
        estimatedMinutes: 30,
        completed: false,
        lessons: ["Busca Binária Clássica", "std::lower_bound e std::upper_bound"],
      },
    ],
  },
  trees: {
    id: "trees",
    title: "Árvores Binárias & Árvores de Busca (BST)",
    subject: "Estruturas Hierárquicas",
    difficulty: "Intermediário",
    retentionRate: 80,
    description: "Propriedades de árvores, travessias em profundidade, menor ancestral comum (LCA) e diâmetro.",
    modules: [
      {
        id: "tree_foundations",
        title: "Módulo 1: Travessias e Propriedades de Árvores",
        description: "Preorder, Inorder, Postorder e cálculo de altura e diâmetro.",
        estimatedMinutes: 35,
        completed: false,
        lessons: ["Travessias Recursivas", "Árvore Binária de Busca"],
      },
    ],
  },
  prefix_sum: {
    id: "prefix_sum",
    title: "Somas de Prefixos & Consultas Estáticas",
    subject: "Técnicas de Vetores",
    difficulty: "Iniciante",
    retentionRate: 92,
    description: "Pré-computação O(N) e consultas de intervalo em tempo constante O(1).",
    modules: [
      {
        id: "prefix_sum_foundations",
        title: "Módulo 1: Vetor de Prefixos 1D & Range Sum Query",
        description: "Invariante de fronteira pref[R] - pref[L-1] e extensões 2D.",
        estimatedMinutes: 25,
        completed: false,
        lessons: ["Somas de Prefixo 1D", "Vetor de Diferenças"],
      },
    ],
  },
  greedy: {
    id: "greedy",
    title: "Algoritmos Gulosos (Greedy)",
    subject: "Estratégias Construtivas",
    difficulty: "Iniciante",
    retentionRate: 82,
    description: "Escolha gulosa, subestrutura ótima e problemas clássicos de ordenação de intervalos.",
    modules: [
      {
        id: "greedy_foundations",
        title: "Módulo 1: Interval Scheduling & Escolha Local",
        description: "Critério de ordenação pelo término e prova por contradição.",
        estimatedMinutes: 30,
        completed: false,
        lessons: ["Interval Scheduling", "Troco Guloso"],
      },
    ],
  },
  segtree: {
    id: "segtree",
    title: "Segment Tree & Consultas em Intervalos",
    subject: "Estruturas de Dados Avançadas",
    difficulty: "Avançado",
    retentionRate: 91,
    description:
      "Consultas associativas de soma, mínimo e máximo em tempo O(log N) com atualizações pontuais e DSU.",
    modules: [
      {
        id: "dsu_kruskal_mst",
        title: "Módulo 1: Disjoint Set Union (DSU) & Árvore Geradora Mínima",
        description: "Union-Find com compressão de caminhos e heurística de rank.",
        estimatedMinutes: 45,
        completed: false,
        lessons: ["Find e Union com Heurística", "Algoritmo de Kruskal"],
      },
    ],
  },
};

// Aliases para roteamento resiliente
PRESET_TRACKS_METADATA["recursao"] = PRESET_TRACKS_METADATA["pilha"];
PRESET_TRACKS_METADATA["recursion"] = PRESET_TRACKS_METADATA["pilha"];
PRESET_TRACKS_METADATA["foundations"] = PRESET_TRACKS_METADATA["pilha"];
PRESET_TRACKS_METADATA["stack"] = PRESET_TRACKS_METADATA["pilha"];
PRESET_TRACKS_METADATA["binary"] = PRESET_TRACKS_METADATA["binary_search"];
PRESET_TRACKS_METADATA["tree"] = PRESET_TRACKS_METADATA["trees"];
PRESET_TRACKS_METADATA["prefix"] = PRESET_TRACKS_METADATA["prefix_sum"];

function resolveWorkspaceUrl(
  moduleId: string,
  parentTrackId?: string,
  mode: "reader" | "arena" = "reader"
): string {
  const topicId = parentTrackId || moduleId;
  const isProblem = mode === "arena";
  const paramKey = isProblem ? "problem" : "lesson";
  return `/workspace?topic=${encodeURIComponent(topicId)}&${paramKey}=${encodeURIComponent(moduleId)}&mode=${mode}`;
}

export default function TrackDetailPage() {
  const params = useParams();
  const router = useRouter();
  const rawSlug = (params?.slug as string)?.toLowerCase() || "grafos";

  const [track, setTrack] = useState<TrackMetadata>(() => {
    return (
      PRESET_TRACKS_METADATA[rawSlug] || {
        id: rawSlug,
        title: `Trilha: ${rawSlug.toUpperCase()}`,
        subject: "Ciência da Computação & Algoritmos",
        difficulty: "Intermediário",
        retentionRate: 80,
        description: "Trilha de estudo com problemas práticos e verificação no juiz online.",
        modules: [
          {
            id: "mod-generic-1",
            title: "Módulo 1: Fundamentos e Resolução de Problemas",
            description: "Conceitos centrais com resolução guiada e exercícios de maratona.",
            estimatedMinutes: 30,
            completed: false,
            lessons: ["Fundamentos do Tópico", "Exercícios Práticos"],
          },
        ],
      }
    );
  });

  const [completedLessons, setCompletedLessons] = useState<string[]>(() =>
    lessonProgressService.getCompletedLessons()
  );

  useEffect(() => {
    const sync = () => setCompletedLessons(lessonProgressService.getCompletedLessons());
    window.addEventListener("lesson-completion-changed", sync);
    return () => window.removeEventListener("lesson-completion-changed", sync);
  }, []);

  const isModuleCompleted = (mod: TrackModule) => {
    return (
      completedLessons.includes(mod.id) ||
      completedLessons.includes(mod.id.toLowerCase()) ||
      lessonProgressService.isLessonCompleted(mod.id)
    );
  };

  const handleToggleModule = async (moduleId: string) => {
    const res = await lessonProgressService.toggleLessonCompletion(moduleId);
    setCompletedLessons(res.completedLessons);
  };

  const completedModulesCount = useMemo(() => {
    return track.modules.filter((m) => isModuleCompleted(m)).length;
  }, [track.modules, completedLessons]);

  const progressPercent = useMemo(() => {
    return Math.round((completedModulesCount / Math.max(1, track.modules.length)) * 100);
  }, [completedModulesCount, track.modules.length]);

  // Try loading from localStorage if it's a custom track
  useEffect(() => {
    if (PRESET_TRACKS_METADATA[rawSlug]) {
      setTrack(PRESET_TRACKS_METADATA[rawSlug]);
      return;
    }

    try {
      const stored = localStorage.getItem("autotutor_custom_tracks");
      if (stored) {
        const customList: TrackMetadata[] = JSON.parse(stored);
        const match = customList.find(
          (t) => t.id.toLowerCase() === rawSlug || t.title.toLowerCase().replace(/[^a-z0-9]+/g, "-").includes(rawSlug)
        );
        if (match) {
          setTrack(match);
          return;
        }
      }

      // Check onboarding track
      const onboardingTrack = localStorage.getItem("autotutor_user_track");
      if (onboardingTrack) {
        const parsed = JSON.parse(onboardingTrack);
        const slugNorm = rawSlug.toLowerCase();
        if (
          parsed.id?.toLowerCase() === slugNorm ||
          slugNorm.startsWith("track-") ||
          slugNorm === "minha-trilha" ||
          slugNorm === "personalizada" ||
          (parsed.title && parsed.title.toLowerCase().replace(/[^a-z0-9]+/g, "-").includes(slugNorm))
        ) {
          setTrack({
            id: parsed.id,
            title: parsed.title,
            subject: parsed.targetGoal ? `Trilha Personalizada: ${parsed.targetGoal.toUpperCase()}` : "Algoritmos",
            difficulty: parsed.entryLevel || "Iniciante",
            retentionRate: 85,
            description: parsed.description,
            modules: (parsed.milestones || []).map((m: any, idx: number) => ({
              id: m.topicId || m.id || `mod-${idx}`,
              title: m.title,
              description: `Semana ${m.weekNumber || idx + 1}: ${m.category || "Fundamentos"} (${m.estimatedHours || 1}h sugeridas)`,
              estimatedMinutes: (m.estimatedHours || 1) * 60,
              completed: lessonProgressService.isLessonCompleted(m.topicId || m.id),
              lessons: m.keyConcepts || [],
            })),
          });
          return;
        }
      }
    } catch (e) {
      console.error("Erro ao carregar detalhes da trilha customizada:", e);
    }
  }, [rawSlug]);

  const firstPendingModule = track.modules.find((m) => !isModuleCompleted(m)) || track.modules[0];
  const targetModuleId = firstPendingModule?.id || track.id;
  const targetTheoryUrl = resolveWorkspaceUrl(targetModuleId, track.id, "reader");
  const targetArenaUrl = resolveWorkspaceUrl(targetModuleId, track.id, "arena");

  const isDp =
    rawSlug === "dp" ||
    track.subject.toLowerCase().includes("dinâmica") ||
    track.subject.toLowerCase().includes("dinamica") ||
    track.title.toLowerCase().includes("dinâmica");
  const isGraph =
    rawSlug === "grafos" ||
    track.subject.toLowerCase().includes("grafo") ||
    track.title.toLowerCase().includes("grafo");

  const breadcrumbs = [
    { label: "Dashboard", href: "/" },
    { label: "Trilhas", href: "/trilhas" },
    { label: track.title, active: true },
  ];

  return (
    <main className="flex-1 flex flex-col min-w-0 pb-20 lg:pb-10">
      <header className="px-6 py-4 border-b border-border bg-card/40 backdrop-blur-sm sticky top-0 z-30">
        <Breadcrumbs items={breadcrumbs} />
      </header>

      <div className="max-w-5xl w-full mx-auto px-4 sm:px-6 py-8 space-y-8">
        {/* Track Hero Banner */}
        <div className="p-6 sm:p-8 rounded-3xl border border-border bg-card/60 backdrop-blur-md shadow-sm relative overflow-hidden space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <span className="text-xs uppercase font-bold text-muted-foreground tracking-wider">
                {track.subject}
              </span>
              <span className="text-muted-foreground">•</span>
              <Badge variant={track.difficulty === "Iniciante" ? "secondary" : "primary"}>
                {track.difficulty}
              </Badge>
              {track.isCustom && (
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 font-semibold border border-blue-500/20">
                  Personalizada
                </span>
              )}
            </div>

            <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>{track.retentionRate}% Retenção Média</span>
            </div>
          </div>

          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground">
              {track.title}
            </h1>
            <p className="text-sm text-muted-foreground mt-2 max-w-3xl leading-relaxed">
              {track.description}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3 pt-2">
            <button
              onClick={() => router.push(targetTheoryUrl)}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold bg-primary text-primary-foreground hover:bg-primary-hover shadow-sm transition-all"
            >
              <BookOpen className="w-4 h-4" />
              <span>Estudar Teoria & Conteúdo</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </button>

            <button
              onClick={() => router.push(targetArenaUrl)}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold bg-secondary hover:bg-accent text-foreground border border-border shadow-xs transition-all"
            >
              <Code2 className="w-4 h-4 text-primary" />
              <span>Praticar Desafios no Juiz</span>
            </button>

            {isGraph && (
              <button
                onClick={() => router.push("/whiteboard?mode=graph")}
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold bg-secondary text-foreground hover:bg-accent border border-border transition-colors"
              >
                <Network className="w-4 h-4 text-primary" />
                <span>Abrir no Laboratório de Grafos</span>
              </button>
            )}

            {isDp && (
              <button
                onClick={() => router.push("/whiteboard?mode=dp")}
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold bg-secondary text-foreground hover:bg-accent border border-border transition-colors"
              >
                <Layers className="w-4 h-4 text-primary" />
                <span>Abrir no Estúdio de DP</span>
              </button>
            )}
          </div>

          {/* Track Progress Bar */}
          <div className="pt-3 border-t border-border/60">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
              <span className="text-xs font-bold text-foreground">
                Progresso Geral: {completedModulesCount} de {track.modules.length} módulos concluídos ({progressPercent}%)
              </span>
              {progressPercent === 100 ? (
                <span className="text-[11px] font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20 flex items-center gap-1 self-start sm:self-auto">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Trilha 100% Concluída
                </span>
              ) : (
                <span className="text-[11px] text-muted-foreground font-medium">
                  {track.modules.length - completedModulesCount} módulo{track.modules.length - completedModulesCount > 1 ? "s" : ""} restante{track.modules.length - completedModulesCount > 1 ? "s" : ""}
                </span>
              )}
            </div>
            <div className="w-full h-2 bg-secondary rounded-full overflow-hidden">
              <div
                className="h-full bg-emerald-500 transition-all duration-500 rounded-full"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>
        </div>

        {/* Modules List */}
        <div className="space-y-4">
          <h2 className="text-base font-bold text-foreground flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-primary" />
            <span>Módulos de Aprendizado & Desafios</span>
          </h2>

          <div className="space-y-3">
            {track.modules.map((mod, index) => {
              const isDone = isModuleCompleted(mod);
              const isFirstPending = !isDone && track.modules.slice(0, index).every((m) => isModuleCompleted(m));

              return (
                <div
                  key={mod.id}
                  className={`p-5 rounded-2xl border transition-all flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 group ${
                    isDone
                      ? "bg-card/30 border-border/60 opacity-90"
                      : isFirstPending
                      ? "bg-card/70 border-primary/50 shadow-xs"
                      : "bg-card/40 border-border hover:bg-card/70"
                  }`}
                >
                  <div className="space-y-1.5 flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-xs font-bold text-primary font-mono">
                        {String(index + 1).padStart(2, "0")}.
                      </span>
                      <h3 className="text-sm font-bold text-foreground group-hover:text-primary transition-colors">
                        {mod.title}
                      </h3>

                      <button
                        type="button"
                        onClick={() => handleToggleModule(mod.id)}
                        className={`flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-semibold border transition-all ${
                          isDone
                            ? "bg-emerald-500/15 border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/25"
                            : "bg-secondary border-border text-muted-foreground hover:text-foreground hover:border-primary/50"
                        }`}
                        title={isDone ? "Clique para marcar como pendente" : "Clique para marcar módulo como concluído"}
                      >
                        <CheckCircle2 className={`w-3 h-3 ${isDone ? "text-emerald-400 fill-emerald-500/20" : ""}`} />
                        <span>{isDone ? "Concluído ✓" : "Concluir"}</span>
                      </button>

                      {isFirstPending && (
                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 font-bold border border-blue-500/20 animate-pulse">
                          👉 Próximo Passo
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground leading-relaxed">
                      {mod.description}
                    </p>
                    <div className="flex items-center gap-3 pt-1 text-[11px] text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {mod.estimatedMinutes} min
                      </span>
                      <span>•</span>
                      <span>{mod.lessons.length} aulas práticas</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <button
                      onClick={() => {
                        const modUrl = resolveWorkspaceUrl(mod.id, track.id, "reader");
                        router.push(modUrl);
                      }}
                      className="flex items-center justify-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-primary text-primary-foreground hover:bg-primary-hover transition-all"
                    >
                      <BookOpen className="w-3.5 h-3.5" />
                      <span>Ler Conteúdo</span>
                    </button>

                    <button
                      onClick={() => {
                        const modUrl = resolveWorkspaceUrl(mod.id, track.id, "arena");
                        router.push(modUrl);
                      }}
                      className="flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold bg-secondary text-foreground hover:bg-accent border border-border transition-all"
                    >
                      <Code2 className="w-3.5 h-3.5 text-primary" />
                      <span>Praticar</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </main>
  );
}
