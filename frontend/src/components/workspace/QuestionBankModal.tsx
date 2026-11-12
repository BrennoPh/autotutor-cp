"use client";

import React, { useState, useMemo } from "react";
import { ProblemSummary } from "@/services/problemService";
import { Badge } from "@/components/ui/Badge";
import {
  X,
  Search,
  Database,
  Code2,
  Clock,
  Gauge,
  Sparkles,
  ArrowRight,
  Filter,
} from "lucide-react";

interface QuestionBankModalProps {
  isOpen: boolean;
  onClose: () => void;
  problems: ProblemSummary[];
  selectedProblemId?: string;
  onSelectProblem: (id: string) => void;
}

const TOPIC_FILTERS = [
  { id: "all", label: "Todos" },
  { id: "grafos", label: "Grafos" },
  { id: "dp", label: "Prog. Dinâmica" },
  { id: "binary", label: "Busca Binária" },
  { id: "tree", label: "Árvores" },
  { id: "segment_tree", label: "Segment Tree" },
  { id: "greedy", label: "Gulosos" },
  { id: "prefix", label: "Prefix Sum" },
  { id: "inedito", label: "Inéditos IA" },
];

export function QuestionBankModal({
  isOpen,
  onClose,
  problems,
  selectedProblemId,
  onSelectProblem,
}: QuestionBankModalProps) {
  const [search, setSearch] = useState("");
  const [topicFilter, setTopicFilter] = useState("all");
  const [diffFilter, setDiffFilter] = useState<string>("all");

  const filteredProblems = useMemo(() => {
    return problems.filter((p) => {
      // Search filter
      const textMatch =
        !search.trim() ||
        p.title.toLowerCase().includes(search.toLowerCase()) ||
        p.topic.toLowerCase().includes(search.toLowerCase()) ||
        (p.tags || []).some((t) => t.toLowerCase().includes(search.toLowerCase()));

      if (!textMatch) return false;

      // Difficulty filter
      if (diffFilter !== "all" && p.difficulty !== diffFilter) return false;

      // Topic filter
      if (topicFilter === "all") return true;
      if (topicFilter === "inedito") {
        return (p.tags || []).some((t) => t.toLowerCase().includes("inédito"));
      }
      if (topicFilter === "dp") {
        const t = `${p.topic} ${(p.tags || []).join(" ")}`.toLowerCase();
        return t.includes("dp") || t.includes("dinâmica") || t.includes("dinamica");
      }
      if (topicFilter === "binary") {
        const t = `${p.topic} ${(p.tags || []).join(" ")}`.toLowerCase();
        return t.includes("binária") || t.includes("binaria") || p.id === "binary";
      }
      if (topicFilter === "tree") {
        const t = `${p.topic} ${(p.tags || []).join(" ")}`.toLowerCase();
        return t.includes("árvore") || t.includes("arvore") || p.id === "tree";
      }
      if (topicFilter === "segment_tree") {
        const t = `${p.topic} ${(p.tags || []).join(" ")}`.toLowerCase();
        return t.includes("segment") || p.id === "segment_tree";
      }
      if (topicFilter === "greedy") {
        const t = `${p.topic} ${(p.tags || []).join(" ")}`.toLowerCase();
        return t.includes("guloso") || t.includes("greedy") || p.id === "greedy";
      }
      if (topicFilter === "prefix") {
        const t = `${p.topic} ${(p.tags || []).join(" ")}`.toLowerCase();
        return t.includes("prefix") || p.id === "prefix";
      }
      if (topicFilter === "grafos") {
        const t = `${p.topic} ${(p.tags || []).join(" ")}`.toLowerCase();
        return t.includes("grafo") || t.includes("bfs") || t.includes("dfs") || p.id === "graph";
      }

      return p.topic.toLowerCase().includes(topicFilter.toLowerCase());
    });
  }, [problems, search, topicFilter, diffFilter]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="bg-card border border-border rounded-3xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-border flex items-center justify-between shrink-0 bg-card/60">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
              <Database className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-foreground flex items-center gap-2">
                <span>Banco de Questões da Maratona</span>
                <span className="text-[11px] font-mono text-primary font-normal bg-primary/10 px-2 py-0.5 rounded-full">
                  {filteredProblems.length} de {problems.length} disponíveis
                </span>
              </h2>
              <p className="text-[11px] text-muted-foreground">
                Explore livremente o catálogo de problemas sem restrição de trilhas ativas.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Search and Filters Bar */}
        <div className="p-4 border-b border-border bg-secondary/20 space-y-3 shrink-0">
          <div className="flex items-center gap-3">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Buscar por título, tag, técnica ou conceito..."
                className="w-full bg-secondary/80 border border-border rounded-xl pl-9 pr-4 py-2 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary font-medium"
              />
            </div>

            <select
              value={diffFilter}
              onChange={(e) => setDiffFilter(e.target.value)}
              className="bg-secondary/90 border border-border rounded-xl px-3 py-2 text-xs text-foreground font-semibold focus:outline-none w-36 shrink-0"
            >
              <option value="all">Dificuldade (Todas)</option>
              <option value="Iniciante">Iniciante</option>
              <option value="Intermediário">Intermediário</option>
              <option value="Avançado">Avançado</option>
            </select>
          </div>

          {/* Topic Pills */}
          <div className="flex flex-wrap gap-1.5 pt-1">
            {TOPIC_FILTERS.map((f) => (
              <button
                key={f.id}
                type="button"
                onClick={() => setTopicFilter(f.id)}
                className={`text-[11px] font-semibold px-3 py-1 rounded-lg border transition-all ${
                  topicFilter === f.id
                    ? "bg-primary text-primary-foreground border-primary shadow-xs"
                    : "bg-secondary/70 hover:bg-accent text-muted-foreground hover:text-foreground border-border/70"
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>

        {/* Problems List / Cards */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-2.5">
          {filteredProblems.length === 0 ? (
            <div className="py-12 text-center text-muted-foreground text-xs space-y-2">
              <Code2 className="w-8 h-8 mx-auto opacity-40 text-primary" />
              <p>Nenhum problema encontrado com os filtros atuais.</p>
              <button
                type="button"
                onClick={() => {
                  setSearch("");
                  setTopicFilter("all");
                  setDiffFilter("all");
                }}
                className="text-primary hover:underline font-semibold"
              >
                Limpar todos os filtros
              </button>
            </div>
          ) : (
            filteredProblems.map((prob) => {
              const isSelected = prob.id === selectedProblemId;
              const isAiGenerated = (prob.tags || []).some((t) => t.toLowerCase().includes("inédito"));

              return (
                <div
                  key={prob.id}
                  onClick={() => onSelectProblem(prob.id)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      onSelectProblem(prob.id);
                    }
                  }}
                  className={`p-4 rounded-2xl border transition-all cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-3 group ${
                    isSelected
                      ? "border-primary bg-primary/10 shadow-sm"
                      : "border-border bg-card/40 hover:bg-card/80 hover:border-border/80"
                  }`}
                >
                  <div className="space-y-1.5 flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-[10px] font-mono uppercase font-bold text-primary tracking-wider">
                        {prob.topic}
                      </span>
                      <Badge variant={prob.difficulty === "Iniciante" ? "secondary" : "primary"}>
                        {prob.difficulty}
                      </Badge>
                      {isAiGenerated && (
                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-400 font-semibold border border-purple-500/20 flex items-center gap-1">
                          <Sparkles className="w-3 h-3" />
                          Inédito IA
                        </span>
                      )}
                      {isSelected && (
                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/20">
                          Selecionado na Arena
                        </span>
                      )}
                    </div>

                    <h3 className="text-sm font-bold text-foreground group-hover:text-primary transition-colors truncate">
                      {prob.title}
                    </h3>

                    {prob.approach_summary && (
                      <p className="text-xs text-muted-foreground line-clamp-1">
                        {prob.approach_summary}
                      </p>
                    )}

                    <div className="flex items-center gap-3 text-[11px] text-muted-foreground font-mono pt-0.5">
                      <span className="flex items-center gap-1">
                        <Gauge className="w-3 h-3" />
                        {prob.complexity}
                      </span>
                      <span>•</span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {prob.time_limit_sec}s
                      </span>
                      {prob.tags && prob.tags.length > 0 && (
                        <>
                          <span>•</span>
                          <span className="truncate max-w-xs">{prob.tags.join(", ")}</span>
                        </>
                      )}
                    </div>
                  </div>

                  <button
                    type="button"
                    className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold shrink-0 transition-all ${
                      isSelected
                        ? "bg-primary text-primary-foreground shadow-sm"
                        : "bg-secondary text-foreground group-hover:bg-primary group-hover:text-primary-foreground"
                    }`}
                  >
                    <span>{isSelected ? "Em Prática" : "Resolver"}</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
