"use client";

import React, { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { problemService, ProblemSummary, ProblemDetail } from "@/services/problemService";
import { judgeService, SubmissionResponse, Verdict } from "@/services/judgeService";
import { aiService } from "@/services/aiService";
import { MarkdownViewer } from "@/components/common/MarkdownViewer";
import {
  Play,
  CheckCircle2,
  XCircle,
  Clock,
  AlertTriangle,
  Code2,
  Terminal,
  Bot,
  ChevronRight,
  RefreshCw,
  FileCode,
  Layers,
  Wand2,
  Filter,
  Gauge,
  HelpCircle,
  Database,
  BookOpen,
  Brain,
} from "lucide-react";
import { GraduatedHintLadder } from "./GraduatedHintLadder";
import { PreFlightModal } from "./PreFlightModal";
import { QuestionBankModal } from "./QuestionBankModal";

export interface PracticeArenaProps {
  initialProblemId?: string;
  topicFilter?: string;
  onAskTutor?: (context: { problem: ProblemDetail | null; code: string; result: SubmissionResponse | null }) => void;
  onContextUpdate?: (context: { problem: ProblemDetail | null; code: string; result: SubmissionResponse | null }) => void;
  onOpenTheory?: (topic: string) => void;
}

export const PROBLEM_ALIAS_MAP: Record<string, string> = {
  binary_search: "binary",
  binary_tree_lca: "tree",
  trees: "tree",
  tree_foundations: "tree",
  greedy_interval_scheduling: "greedy",
  prefix_sum_ranges: "prefix",
  dsu_kruskal_mst: "graph",
  dijkstra: "graph",
  recursion: "tree",
  recursion_foundations: "tree",
  foundations_stack_complexity: "tree",
};

export function normalizeProblemId(id?: string | null): string {
  if (!id) return "";
  const clean = id.trim();
  return PROBLEM_ALIAS_MAP[clean] || clean;
}

function matchesProblemTopic(problem: ProblemSummary, filter?: string): boolean {
  if (!filter || filter === "all") return true;
  const f = filter.toLowerCase().trim();
  const top = (problem.topic || "").toLowerCase();
  const tit = (problem.title || "").toLowerCase();
  const tags = (problem.tags || []).map((t) => t.toLowerCase());
  const fam = ((problem as any).family || "").toLowerCase();
  const id = (problem.id || "").toLowerCase();

  // Direct check
  if (top.includes(f) || f.includes(top)) return true;
  if (tit.includes(f) || fam.includes(f) || id.includes(f)) return true;
  if (tags.some((t) => t.includes(f) || f.includes(t))) return true;

  // Trees / Árvores
  const isFilterTree =
    f.includes("árvore") ||
    f.includes("arvore") ||
    f.includes("tree") ||
    f.includes("lca") ||
    f.includes("bst") ||
    f.includes("avl");
  const isProbTree =
    id === "tree" ||
    fam === "tree" ||
    top.includes("árvor") ||
    top.includes("arvor") ||
    tags.some((t) => t.includes("árvor") || t.includes("tree"));
  if (isFilterTree && isProbTree) return true;

  // Busca Binária / Binary Search
  const isFilterBinary =
    f.includes("busca bin") ||
    f.includes("binary") ||
    f.includes("binária") ||
    f.includes("binaria");
  const isProbBinary =
    id === "binary" ||
    fam === "binary" ||
    top.includes("busca") ||
    top.includes("binár") ||
    top.includes("binar");
  if (isFilterBinary && isProbBinary) return true;

  // Programação Dinâmica / DP
  const isFilterDp =
    f === "dp" ||
    f.includes("dinâmica") ||
    f.includes("dinamica") ||
    f.includes("mochila") ||
    f.includes("knapsack");
  const isProbDp =
    id === "dp" ||
    fam === "dp" ||
    top === "dp" ||
    tags.includes("dp") ||
    tags.some((t) => t.includes("dinâmica") || t.includes("dinamica"));
  if (isFilterDp && isProbDp) return true;

  // Algoritmos Gulosos / Greedy
  const isFilterGreedy =
    f.includes("guloso") ||
    f.includes("greedy") ||
    f.includes("interval") ||
    f.includes("scheduling");
  const isProbGreedy =
    id === "greedy" ||
    fam === "greedy" ||
    top.includes("guloso") ||
    tags.some((t) => t.includes("guloso") || t.includes("greedy"));
  if (isFilterGreedy && isProbGreedy) return true;

  // Prefix Sum / Prefixo
  const isFilterPrefix =
    f.includes("prefix") ||
    f.includes("prefixo") ||
    f.includes("soma acumulada");
  const isProbPrefix =
    id === "prefix" ||
    fam === "prefix" ||
    top.includes("prefix") ||
    tags.some((t) => t.includes("prefix"));
  if (isFilterPrefix && isProbPrefix) return true;

  // Segment Tree / Segtree / DSU
  const isFilterSegtree =
    f.includes("segtree") ||
    f.includes("segment") ||
    f.includes("dsu") ||
    f.includes("fenwick");
  const isProbSegtree =
    id === "segment_tree" ||
    fam === "segtree" ||
    top.includes("segment");
  if (isFilterSegtree && isProbSegtree) return true;

  // Recursão / Pilha de Execução
  const isFilterRecursion =
    f.includes("recurs") ||
    f.includes("pilha") ||
    f.includes("stack");
  const isProbRecursion = id === "tree" || id === "graph";
  if (isFilterRecursion && isProbRecursion) return true;

  // Grafos / BFS / DFS / Dijkstra
  const isFilterGraph =
    f === "grafos" ||
    f === "graph" ||
    f.includes("grafo") ||
    f.includes("bfs") ||
    f.includes("dfs") ||
    f.includes("dijkstra") ||
    f.includes("caminho");
  const isProbGraph =
    id === "graph" ||
    fam === "graph" ||
    top.includes("grafo");
  if (isFilterGraph && isProbGraph) return true;

  return false;
}

export function getBestProblemForTopic(topic: string, problems: ProblemSummary[]): string {
  if (!topic || problems.length === 0) return problems[0]?.id || "graph";
  const t = topic.toLowerCase().trim();

  if (t.includes("árvore") || t.includes("arvore") || t.includes("tree") || t.includes("lca")) {
    const p = problems.find((x) => x.id === "tree" || (x as any).family === "tree");
    if (p) return p.id;
  }
  if (t.includes("busca bin") || t.includes("binary") || t.includes("binária") || t.includes("binaria")) {
    const p = problems.find((x) => x.id === "binary" || (x as any).family === "binary");
    if (p) return p.id;
  }
  if (t === "dp" || t.includes("dinâmica") || t.includes("dinamica") || t.includes("mochila")) {
    const p = problems.find((x) => x.id === "dp" || (x as any).family === "dp");
    if (p) return p.id;
  }
  if (t.includes("guloso") || t.includes("greedy") || t.includes("interval")) {
    const p = problems.find((x) => x.id === "greedy" || (x as any).family === "greedy");
    if (p) return p.id;
  }
  if (t.includes("prefix") || t.includes("prefixo")) {
    const p = problems.find((x) => x.id === "prefix" || (x as any).family === "prefix");
    if (p) return p.id;
  }
  if (t.includes("segtree") || t.includes("segment") || t.includes("dsu")) {
    const p = problems.find((x) => x.id === "segment_tree" || (x as any).family === "segtree");
    if (p) return p.id;
  }
  if (t.includes("recurs") || t.includes("pilha") || t.includes("stack")) {
    const p = problems.find((x) => x.id === "tree" || x.id === "graph");
    if (p) return p.id;
  }
  if (t.includes("grafo") || t.includes("graph") || t.includes("bfs") || t.includes("dfs") || t.includes("dijkstra")) {
    const p = problems.find((x) => x.id === "graph" || (x as any).family === "graph");
    if (p) return p.id;
  }

  const match = problems.find((p) => matchesProblemTopic(p, topic));
  return match?.id || problems[0]?.id || "graph";
}

export function PracticeArena({
  initialProblemId,
  topicFilter,
  onAskTutor,
  onContextUpdate,
  onOpenTheory,
}: PracticeArenaProps) {
  const searchParams = useSearchParams();
  const rawUrlProblem = searchParams.get("problem");
  const urlProblemId = normalizeProblemId(rawUrlProblem);
  const urlTopic = searchParams.get("topic");
  const normalizedInitialId = normalizeProblemId(initialProblemId);

  const [problems, setProblems] = useState<ProblemSummary[]>([]);
  const [selectedTopic, setSelectedTopic] = useState<string>("all");
  const [selectedProblemId, setSelectedProblemId] = useState<string>(
    normalizedInitialId || urlProblemId || ""
  );
  const [isQuestionBankOpen, setIsQuestionBankOpen] = useState<boolean>(false);
  const [problemDetail, setProblemDetail] = useState<ProblemDetail | null>(null);
  const [language] = useState<"cpp">("cpp");
  const [code, setCode] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [submissionResult, setSubmissionResult] = useState<SubmissionResponse | null>(null);
  const [activeTab, setActiveTab] = useState<"statement" | "examples" | "tests">("statement");

  // FIA Socratic & Pre-Flight Modals State
  const [showHintLadder, setShowHintLadder] = useState<boolean>(false);
  const [showPreFlight, setShowPreFlight] = useState<boolean>(false);

  // AI Problem Generator Modal State
  const [showAiModal, setShowAiModal] = useState<boolean>(false);
  const [isGeneratingProblem, setIsGeneratingProblem] = useState<boolean>(false);
  const [aiLevel, setAiLevel] = useState<"Iniciante" | "Intermediário" | "Avançado">("Iniciante");
  const [aiConcept, setAiConcept] = useState<string>("Grafos");
  const [aiTheme, setAiTheme] = useState<string>("Exploração Espacial");
  const [aiLearningRequest, setAiLearningRequest] = useState<string>("");
  const [aiError, setAiError] = useState<string | null>(null);

  const handleCreateAiProblem = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsGeneratingProblem(true);
    setAiError(null);

    try {
      const res = await aiService.generateProblem({
        level: aiLevel,
        concept: aiConcept,
        theme: aiTheme,
        learning_request: aiLearningRequest,
      });

      const newSummary: ProblemSummary = {
        id: res.id,
        title: res.title,
        topic: res.topic,
        difficulty: res.difficulty as any,
        tags: [res.topic, "Inédito IA"],
        time_limit_sec: 2.0,
        memory_limit_mb: 256,
        complexity: res.complexity,
        approach_summary: "Problema adaptativo inédito gerado via AutoCode Engine.",
      };

      setProblems((prev) => [newSummary, ...prev]);
      setSelectedProblemId(res.id);
      setShowAiModal(false);
    } catch (err: any) {
      setAiError(err.message || "Falha ao gerar problema via IA. Verifique sua chave de API.");
    } finally {
      setIsGeneratingProblem(false);
    }
  };

  // Load problem catalog and select target problem (optimized with parallel fetch)
  useEffect(() => {
    const targetId = normalizedInitialId || urlProblemId;
    const activeFilter = urlTopic || topicFilter;

    problemService
      .listProblems()
      .then((res) => {
        setProblems(res.problems);

        let finalId = targetId;
        if (!finalId && activeFilter) {
          finalId = getBestProblemForTopic(activeFilter, res.problems);
        }
        if (!finalId && res.problems.length > 0) {
          finalId = res.problems[0].id;
        }

        if (finalId) {
          setSelectedProblemId(finalId);
          return problemService.getProblem(finalId).then((detail) => {
            setProblemDetail(detail);
            setCode(detail.starter_code.cpp || "");
          });
        }
      })
      .catch(console.error);
  }, [normalizedInitialId, urlProblemId, urlTopic, topicFilter]);

  // Sync external initialProblemId changes
  useEffect(() => {
    if (normalizedInitialId && normalizedInitialId !== selectedProblemId) {
      setSelectedProblemId(normalizedInitialId);
    }
  }, [normalizedInitialId, selectedProblemId]);

  // Load problem detail when selection changes
  useEffect(() => {
    if (!selectedProblemId) return;
    if (problemDetail && problemDetail.id === selectedProblemId) return;
    problemService
      .getProblem(selectedProblemId)
      .then((detail) => {
        setProblemDetail(detail);
        setCode(detail.starter_code.cpp || "");
        setSubmissionResult(null);
      })
      .catch(console.error);
  }, [selectedProblemId, problemDetail]);

  // Notify parent container of active context for AI Tutor (protected against re-render loops)
  const onContextUpdateRef = React.useRef(onContextUpdate);
  React.useEffect(() => {
    onContextUpdateRef.current = onContextUpdate;
  }, [onContextUpdate]);

  const lastReportedContextRef = React.useRef<{ problemId?: string; code?: string; result?: any }>({});

  useEffect(() => {
    const pId = problemDetail?.id;
    if (
      lastReportedContextRef.current.problemId === pId &&
      lastReportedContextRef.current.code === code &&
      lastReportedContextRef.current.result === submissionResult
    ) {
      return;
    }
    lastReportedContextRef.current = { problemId: pId, code, result: submissionResult };
    onContextUpdateRef.current?.({
      problem: problemDetail,
      code,
      result: submissionResult,
    });
  }, [problemDetail, code, submissionResult]);

  const handleSubmit = async () => {
    if (!selectedProblemId || !code.trim()) return;
    setIsSubmitting(true);
    setSubmissionResult(null);

    try {
      const res = await judgeService.submit({
        problem_id: selectedProblemId,
        source_code: code,
        language: language,
      });
      setSubmissionResult(res);
      setActiveTab("tests");
    } catch (err: any) {
      setSubmissionResult({
        verdict: "RE",
        message: err.message || "Erro durante a submissão.",
        execution_time_ms: 0,
        tests_passed: 0,
        total_tests: 0,
        failed_test: null,
        tests: [],
      });
      setActiveTab("tests");
    } finally {
      setIsSubmitting(false);
    }
  };

  const getVerdictBadge = (verdict: Verdict) => {
    switch (verdict) {
      case "AC":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Accepted (AC)
          </span>
        );
      case "WA":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30">
            <XCircle className="w-3.5 h-3.5" />
            Wrong Answer (WA)
          </span>
        );
      case "TLE":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
            <Clock className="w-3.5 h-3.5" />
            Time Limit Exceeded (TLE)
          </span>
        );
      case "MLE":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-600/10 text-amber-500 border border-amber-500/30">
            <AlertTriangle className="w-3.5 h-3.5" />
            Memory Limit Exceeded (MLE)
          </span>
        );
      case "CE":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-blue-500/10 text-blue-400 border border-blue-500/30">
            <AlertTriangle className="w-3.5 h-3.5" />
            Compilation Error (CE)
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-purple-500/10 text-purple-400 border border-purple-500/30">
            <AlertTriangle className="w-3.5 h-3.5" />
            Runtime Error (RE)
          </span>
        );
    }
  };

  const filteredProblems = problems.filter((p) => {
    if (selectedTopic === "all") return true;
    if (selectedTopic === "inedito") {
      return p.tags?.some((t) => t.toLowerCase().includes("inédito"));
    }
    return matchesProblemTopic(p, selectedTopic);
  });

  return (
    <div className="flex flex-col lg:flex-row h-full min-h-[calc(100vh-3.5rem)] bg-background">
      {/* Left Panel: Problem Statement & Context */}
      <div className="w-full lg:w-[48%] border-r border-border flex flex-col bg-card/20 overflow-hidden">
        {/* Top Problem Header */}
        <div className="p-4 border-b border-border bg-card/60 flex flex-wrap items-center justify-between gap-3 shrink-0">
          <div className="flex items-center gap-1.5 flex-1 min-w-[200px]">
            <button
              type="button"
              onClick={() => setIsQuestionBankOpen(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold bg-primary text-primary-foreground hover:bg-primary-hover shadow-sm transition-all shrink-0"
              title="Abrir Banco de Questões completo com busca e filtros"
            >
              <Database className="w-3.5 h-3.5" />
              <span>Banco de Questões</span>
              <span className="text-[10px] font-mono bg-primary-foreground/20 px-1.5 py-0.5 rounded-md">
                {problems.length}
              </span>
            </button>
            <select
              value={selectedTopic}
              onChange={(e) => setSelectedTopic(e.target.value)}
              className="bg-secondary/90 border border-border text-foreground text-[11px] font-semibold rounded-lg px-2 py-1.5 focus:outline-none w-28 shrink-0"
              title="Filtrar problemas por tópico"
            >
              <option value="all">Todos</option>
              <option value="grafo">Grafos</option>
              <option value="dp">Prog. Dinâmica</option>
              <option value="árvore">Árvores</option>
              <option value="inedito">Inéditos IA</option>
            </select>
            <select
              value={selectedProblemId}
              onChange={(e) => setSelectedProblemId(e.target.value)}
              className="bg-secondary/70 border border-border text-foreground text-xs font-semibold rounded-xl px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-primary w-full max-w-xs"
            >
              {filteredProblems.some((p) => p.id === selectedProblemId) || !problemDetail
                ? filteredProblems.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.title} ({p.difficulty} • {p.topic})
                    </option>
                  ))
                : [
                    <option key={problemDetail.id} value={problemDetail.id}>
                      {problemDetail.title} ({problemDetail.difficulty} • {problemDetail.topic})
                    </option>,
                    ...filteredProblems.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.title} ({p.difficulty} • {p.topic})
                      </option>
                    )),
                  ]}
            </select>
            <button
              type="button"
              onClick={() => setShowAiModal(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold bg-primary/15 text-primary border border-primary/30 hover:bg-primary/25 transition-all shrink-0"
              title="Gerar um problema inédito adaptativo via IA"
            >
              <Wand2 className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Criar com IA</span>
            </button>
          </div>

          {problemDetail && (
            <div className="flex items-center gap-2 shrink-0">
              <span className="text-[11px] font-medium px-2.5 py-0.5 rounded-full bg-secondary text-muted-foreground border border-border">
                {problemDetail.topic}
              </span>
              <span className="text-[11px] font-medium px-2.5 py-0.5 rounded-full bg-primary/10 text-primary border border-primary/20">
                {problemDetail.complexity}
              </span>
              {onOpenTheory && (
                <button
                  type="button"
                  onClick={() => onOpenTheory(problemDetail.topic)}
                  className="flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-primary/10 text-primary border border-primary/25 hover:bg-primary/20 transition-all shadow-xs"
                  title={`Abrir teoria e material didático sobre ${problemDetail.topic}`}
                >
                  <BookOpen className="w-3 h-3" />
                  <span>Teoria</span>
                </button>
              )}
            </div>
          )}
        </div>

        {/* Tab Header for Problem */}
        <div className="flex items-center gap-1 px-4 pt-2 border-b border-border bg-card/40 shrink-0">
          <button
            onClick={() => setActiveTab("statement")}
            className={`px-3 py-2 text-xs font-semibold border-b-2 transition-all ${
              activeTab === "statement"
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            Enunciado
          </button>
          <button
            onClick={() => setActiveTab("examples")}
            className={`px-3 py-2 text-xs font-semibold border-b-2 transition-all ${
              activeTab === "examples"
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            Exemplos ({problemDetail?.examples?.length || 0})
          </button>
          <button
            onClick={() => setActiveTab("tests")}
            className={`px-3 py-2 text-xs font-semibold border-b-2 transition-all ${
              activeTab === "tests"
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            Veredito do Juiz {submissionResult && `(${submissionResult.verdict})`}
          </button>
        </div>

        {/* Tab Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4 text-xs leading-relaxed">
          {activeTab === "statement" && !problemDetail && (
            <div className="space-y-4 py-2 animate-pulse" aria-label="Carregando enunciado do problema">
              <div className="h-6 bg-secondary/70 rounded-lg w-3/4" />
              <div className="h-3 bg-secondary/40 rounded w-1/2" />
              <div className="space-y-2 pt-2">
                <div className="h-4 bg-secondary/50 rounded w-full" />
                <div className="h-4 bg-secondary/50 rounded w-5/6" />
                <div className="h-4 bg-secondary/50 rounded w-4/6" />
              </div>
              <div className="h-28 bg-card/60 rounded-xl border border-border" />
            </div>
          )}

          {activeTab === "statement" && problemDetail && (
            <div className="space-y-4">
              <div>
                <h2 className="text-lg font-bold text-foreground">{problemDetail.title}</h2>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Limite de Tempo: {problemDetail.time_limit_sec}s • Memória: {problemDetail.memory_limit_mb}MB
                </p>
              </div>

              <div>
                <MarkdownViewer content={problemDetail.statement} />
              </div>

              {problemDetail.math_essence && (
                <div className="p-3.5 rounded-xl border border-primary/20 bg-primary/5 text-xs text-foreground space-y-1">
                  <span className="font-bold text-primary block">Invariante & Essência Matemática:</span>
                  <p className="text-[11px] text-muted-foreground leading-relaxed">{problemDetail.math_essence}</p>
                </div>
              )}
            </div>
          )}

          {activeTab === "examples" && problemDetail && (
            <div className="space-y-3">
              {problemDetail.examples.map((ex, i) => (
                <div key={i} className="p-3.5 rounded-xl border border-border bg-secondary/30 space-y-2">
                  <span className="font-bold text-foreground text-xs block">Caso de Exemplo #{i + 1}</span>
                  <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
                    <div className="p-2 rounded-lg bg-card border border-border">
                      <span className="text-muted-foreground block text-[10px] mb-1">Entrada:</span>
                      <pre className="whitespace-pre-wrap">{ex.input}</pre>
                    </div>
                    <div className="p-2 rounded-lg bg-card border border-border">
                      <span className="text-muted-foreground block text-[10px] mb-1">Saída Esperada:</span>
                      <pre className="whitespace-pre-wrap">{ex.output}</pre>
                    </div>
                  </div>
                  {ex.explanation && (
                    <p className="text-[11px] text-muted-foreground italic mt-1">{ex.explanation}</p>
                  )}
                </div>
              ))}
            </div>
          )}

          {activeTab === "tests" && (
            <div className="space-y-3">
              {!submissionResult ? (
                <div className="p-8 text-center text-muted-foreground space-y-2">
                  <Terminal className="w-8 h-8 mx-auto opacity-40" />
                  <p>Nenhuma submissão realizada ainda.</p>
                  <p className="text-[11px]">Clique em &quot;Submeter Solução&quot; no editor para executar os testes no juiz.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="p-4 rounded-xl border border-border bg-card/60 flex items-center justify-between">
                    <div>
                      <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider block">
                        Resultado Oficial
                      </span>
                      <div className="mt-1">{getVerdictBadge(submissionResult.verdict)}</div>
                    </div>
                    <div className="text-right text-xs text-muted-foreground">
                      <p>
                        Tempo máx: <strong className="text-foreground">{submissionResult.execution_time_ms} ms</strong>
                      </p>
                      <p>
                        Passaram:{" "}
                        <strong className="text-foreground">
                          {submissionResult.tests_passed} / {submissionResult.total_tests}
                        </strong>
                      </p>
                    </div>
                  </div>

                  {submissionResult.message && (
                    <div className="p-3 rounded-xl border border-border bg-secondary/40 font-mono text-[11px] whitespace-pre-wrap text-muted-foreground">
                      {submissionResult.message}
                    </div>
                  )}

                  {/* Next Step Cockpit on Accepted (AC) */}
                  {submissionResult.verdict === "AC" && (
                    <div className="p-4 rounded-xl border border-emerald-500/30 bg-emerald-500/10 space-y-3 animate-fade-in">
                      <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs">
                        <CheckCircle2 className="w-4 h-4" />
                        <span>Excelente! Problema resolvido com sucesso (Accepted).</span>
                      </div>
                      <p className="text-[11px] text-muted-foreground">
                        Fixe o algoritmo na memória de longo prazo com flashcards do tema ou avance para a próxima etapa.
                      </p>
                      <div className="flex flex-wrap items-center gap-2 pt-1">
                        <button
                          type="button"
                          onClick={() => {
                            const topic = problemDetail?.topic || "grafos";
                            window.location.href = `/repetition?topic=${encodeURIComponent(topic)}&autoStart=true`;
                          }}
                          className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold bg-primary text-primary-foreground hover:bg-primary-hover shadow-sm transition-all"
                        >
                          <Brain className="w-3.5 h-3.5" />
                          <span>Fixar com Flashcards deste Tema →</span>
                        </button>

                        {onOpenTheory && (
                          <button
                            type="button"
                            onClick={() => onOpenTheory(problemDetail?.topic || "")}
                            className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold bg-secondary text-foreground hover:bg-accent border border-border transition-all"
                          >
                            <BookOpen className="w-3.5 h-3.5" />
                            <span>Rever Teoria & Invariantes</span>
                          </button>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Ask AI Tutor about this verdict */}
                  {submissionResult.verdict !== "AC" && (
                    <button
                      type="button"
                      onClick={() =>
                        onAskTutor?.({
                          problem: problemDetail,
                          code,
                          result: submissionResult,
                        })
                      }
                      className="w-full flex items-center justify-center gap-2 p-2.5 rounded-md bg-slate-800 border border-slate-700 text-slate-200 font-medium text-xs hover:bg-slate-700 hover:text-white transition-colors"
                    >
                      <Bot className="w-4 h-4 text-blue-400" />
                      <span>Pedir Diagnóstico ao Assistente</span>
                    </button>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Right Panel: Code Editor & Submission Terminal */}
      <div className="flex-1 flex flex-col bg-card/40">
        {/* Editor Controls Bar */}
        <div className="p-3 border-b border-border bg-card/80 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2">
            <FileCode className="w-4 h-4 text-primary" />
            <span className="text-xs font-bold text-foreground">Editor de Código</span>
            <div className="flex items-center gap-1.5 bg-primary/10 border border-primary/25 px-2.5 py-0.5 rounded-lg ml-2">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="text-[11px] font-bold text-primary font-mono">C++17 (Gnu++17)</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setShowPreFlight(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
              title="Validar intuição e complexidade assintótica antes de codar"
            >
              <Gauge className="w-3.5 h-3.5 text-indigo-400" />
              <span>Pre-Flight</span>
            </button>

            <button
              type="button"
              onClick={() => setShowHintLadder(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
              title="Escada Gradual de Pistas Socráticas (RAG + AI Memory + Zero-Leak)"
            >
              <HelpCircle className="w-3.5 h-3.5 text-blue-400" />
              <span>Pistas (4 Tiers)</span>
            </button>

            <button
              type="button"
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="flex items-center gap-1.5 px-4 py-1.5 rounded-xl text-xs font-bold bg-primary text-primary-foreground hover:opacity-90 transition-opacity shadow-sm disabled:opacity-50"
            >
              <Play className={`w-3.5 h-3.5 ${isSubmitting ? "animate-spin" : ""}`} />
              <span>{isSubmitting ? "Avaliando..." : "Submeter Solução"}</span>
            </button>
          </div>
        </div>

        {/* Code Input Area */}
        <div className="flex-1 relative">
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            spellCheck={false}
            className="w-full h-full p-4 bg-background/90 text-foreground font-mono text-xs focus:outline-none resize-none selection:bg-primary/20 leading-relaxed"
            placeholder="Digite sua solução aqui..."
          />
        </div>
      </div>

      {/* AI Problem Generator Modal */}
      {showAiModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-in fade-in-0">
          <div className="w-full max-w-md bg-card border border-border rounded-2xl p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <div className="flex items-center gap-2">
                <Wand2 className="w-4 h-4 text-primary" />
                <h3 className="text-sm font-bold text-foreground">Gerador de Problemas Competitivos (IA)</h3>
              </div>
              <button
                type="button"
                onClick={() => setShowAiModal(false)}
                className="text-muted-foreground hover:text-foreground text-xs p-1"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateAiProblem} className="space-y-3.5 text-xs">
              <div className="space-y-1">
                <label className="font-semibold text-foreground">Tópico / Estrutura</label>
                <select
                  value={aiConcept}
                  onChange={(e) => setAiConcept(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-secondary/60 border border-border text-foreground font-medium focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="Grafos">Grafos (BFS, DFS, Dijkstra, Ciclos)</option>
                  <option value="Programação Dinâmica">Programação Dinâmica (Mochila, Subsequências)</option>
                  <option value="Busca Binária">Busca Binária em Resposta Monótona</option>
                  <option value="Segment Tree">Segment Tree e Consultas em Intervalos</option>
                  <option value="Prefix Sum">Soma de Prefixos e Invariantes</option>
                  <option value="Guloso">Algoritmos Gulosos (Interval Scheduling)</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-1">
                  <label className="font-semibold text-foreground">Dificuldade</label>
                  <select
                    value={aiLevel}
                    onChange={(e) => setAiLevel(e.target.value as any)}
                    className="w-full px-3 py-2 rounded-xl bg-secondary/60 border border-border text-foreground font-medium focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="Iniciante">Iniciante</option>
                    <option value="Intermediário">Intermediário</option>
                    <option value="Avançado">Avançado</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="font-semibold text-foreground">Tema Narrativo</label>
                  <input
                    type="text"
                    value={aiTheme}
                    onChange={(e) => setAiTheme(e.target.value)}
                    placeholder="ex: Exploração Espacial"
                    className="w-full px-3 py-2 rounded-xl bg-secondary/60 border border-border text-foreground font-medium focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="font-semibold text-foreground">Objetivo Específico ou Regra</label>
                <textarea
                  value={aiLearningRequest}
                  onChange={(e) => setAiLearningRequest(e.target.value)}
                  rows={3}
                  placeholder="ex: Menor caminho com matriz de adjacência e busca em largura..."
                  className="w-full p-2.5 rounded-xl bg-secondary/50 border border-border text-foreground font-mono text-[11px] focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                />
              </div>

              {aiError && (
                <div className="p-2.5 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive text-[11px]">
                  {aiError}
                </div>
              )}

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-border">
                <button
                  type="button"
                  onClick={() => setShowAiModal(false)}
                  className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-secondary text-foreground hover:bg-accent"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={isGeneratingProblem}
                  className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-md text-xs font-medium bg-blue-600 text-white hover:bg-blue-500 shadow-sm disabled:opacity-50 transition-colors"
                >
                  <Wand2 className={`w-3.5 h-3.5 ${isGeneratingProblem ? "animate-spin" : ""}`} />
                  <span>{isGeneratingProblem ? "Gerando Contrato..." : "Gerar e Carregar na Arena"}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Socratic Hint Ladder Modal (4 Tiers, Zero-Leak, RAG + AI Memory) */}
      <GraduatedHintLadder
        isOpen={showHintLadder}
        onClose={() => setShowHintLadder(false)}
        problemId={selectedProblemId}
        problemTitle={problemDetail?.title || "Problema de Programação Competitiva"}
        currentCode={code}
      />

      {/* Pre-Flight Intuition & Asymptotic Complexity Check Modal */}
      <PreFlightModal
        isOpen={showPreFlight}
        onClose={() => setShowPreFlight(false)}
        problemId={selectedProblemId}
        problemTitle={problemDetail?.title || "Problema de Programação Competitiva"}
      />

      {/* Full Catalog Question Bank Modal */}
      <QuestionBankModal
        isOpen={isQuestionBankOpen}
        onClose={() => setIsQuestionBankOpen(false)}
        problems={problems}
        selectedProblemId={selectedProblemId}
        onSelectProblem={(id) => {
          setSelectedProblemId(id);
          setIsQuestionBankOpen(false);
        }}
      />
    </div>
  );
}
