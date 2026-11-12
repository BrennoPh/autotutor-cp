"use client";

import React, { useState, useEffect } from "react";
import { TrackMetadata, TrackModule } from "@/types/tracks";
import { aiService } from "@/services/aiService";
import {
  X,
  Plus,
  Trash2,
  Compass,
  Sparkles,
  BookOpen,
  Wand2,
  Loader2,
  CheckCircle2,
  Lightbulb,
} from "lucide-react";

interface CreateTrackModalProps {
  isOpen: boolean;
  onClose: () => void;
  onTrackCreated: (track: TrackMetadata) => void;
  initialPrompt?: string;
}

const DEFAULT_MODULE_TEMPLATES: Record<string, TrackModule[]> = {
  "Estruturas de Dados": [
    {
      id: "mod-1",
      title: "Módulo 1: Árvore Binária de Busca (BST) e Travessias",
      description: "Ponteiros, alocação de nós e percursos In-Order, Pre-Order e Post-Order em O(N).",
      estimatedMinutes: 35,
      completed: false,
      lessons: ["Estrutura de Nós em C++", "Inserção e Busca Binária O(log N)", "Remoção com Sucessor In-Order"],
    },
    {
      id: "mod-2",
      title: "Módulo 2: Árvores Balanceadas (AVL & Rotações)",
      description: "Fator de balanceamento e rotações simples e duplas para garantir O(log N).",
      estimatedMinutes: 45,
      completed: false,
      lessons: ["Fator de Balanceamento", "Rotações Simples (LL/RR)", "Rotações Duplas (LR/RL)"],
    },
    {
      id: "mod-3",
      title: "Módulo 3: Árvores Rubro-Negras & STL do C++",
      description: "Propriedades de nós e uso prático de std::set e std::map em competições.",
      estimatedMinutes: 40,
      completed: false,
      lessons: ["Invariantes da Árvore Rubro-Negra", "std::set e std::map", "lower_bound e upper_bound"],
    },
  ],
  "Programação Dinâmica": [
    {
      id: "mod-1",
      title: "Módulo 1: Fundamentos de DP e Memoization",
      description: "Identificando subproblemas sobrepostos e recursão com cache linear.",
      estimatedMinutes: 30,
      completed: false,
      lessons: ["Mochila 0/1", "Recursão vs Iteração"],
    },
    {
      id: "mod-2",
      title: "Módulo 2: Otimização de Espaço 1D e Transições",
      description: "Compressão de memória de O(N*W) para O(W) e iteração reversa.",
      estimatedMinutes: 45,
      completed: false,
      lessons: ["Espaço 1D na Mochila", "Troco de Moedas Ilimitado"],
    },
  ],
};

const PROMPT_SUGGESTIONS = [
  "Quero uma trilha sobre estrutura de dados com Árvore Binária e Árvore Balanceada",
  "Programação Dinâmica de transição 2D e Mochila 0/1",
  "Busca em Grafos, Menor Caminho (Dijkstra) e DSU",
  "Árvores de Segmentos (SegTree) e consultas em intervalos",
  "Algoritmos Gulosos para competições OBI e ICPC",
];

export function CreateTrackModal({
  isOpen,
  onClose,
  onTrackCreated,
  initialPrompt = "",
}: CreateTrackModalProps) {
  const [activeTab, setActiveTab] = useState<"ai" | "manual">("ai");
  const [aiPrompt, setAiPrompt] = useState(initialPrompt);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationSuccess, setGenerationSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const [title, setTitle] = useState("");
  const [subject, setSubject] = useState("Estruturas de Dados");
  const [difficulty, setDifficulty] = useState<"Iniciante" | "Intermediário" | "Avançado">("Intermediário");
  const [description, setDescription] = useState("");
  const [modules, setModules] = useState<TrackModule[]>(DEFAULT_MODULE_TEMPLATES["Estruturas de Dados"]);

  useEffect(() => {
    if (initialPrompt) {
      setAiPrompt(initialPrompt);
      setActiveTab("ai");
    }
  }, [initialPrompt]);

  if (!isOpen) return null;

  const handleGenerateWithAi = async (customPrompt?: string) => {
    const textToUse = customPrompt || aiPrompt;
    if (!textToUse.trim()) return;

    setIsGenerating(true);
    setErrorMsg(null);
    setGenerationSuccess(false);

    try {
      const res = await aiService.generateTrack({
        prompt: textToUse.trim(),
        difficulty,
        subject,
      });

      if (res && res.title) {
        setTitle(res.title);
        setSubject(res.subject || "Estruturas de Dados");
        setDifficulty(res.difficulty || "Intermediário");
        setDescription(res.description || "");

        const parsedModules: TrackModule[] = (res.modules || []).map((m, idx) => ({
          id: `mod-ai-${Date.now()}-${idx + 1}`,
          title: m.title || `Módulo ${idx + 1}`,
          description: m.description || "",
          estimatedMinutes: m.estimatedMinutes || 35,
          completed: false,
          lessons: m.lessons || ["Conceitos Fundamentais", "Exercícios Práticos"],
        }));

        setModules(parsedModules.length > 0 ? parsedModules : DEFAULT_MODULE_TEMPLATES["Estruturas de Dados"]);
        setGenerationSuccess(true);
        setActiveTab("manual"); // Move to review/edit
      }
    } catch (err: any) {
      console.error("Falha ao gerar trilha com IA:", err);
      setErrorMsg("Não foi possível conectar à IA no momento. Você pode editar manualmente abaixo.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleAddModule = () => {
    const nextIdx = modules.length + 1;
    const newMod: TrackModule = {
      id: `mod-custom-${Date.now()}-${nextIdx}`,
      title: `Módulo ${nextIdx}: Novo Tópico de Estudo`,
      description: "Conceitos teóricos e prática no juiz.",
      estimatedMinutes: 30,
      completed: false,
      lessons: ["Conceito Principal", "Desafio Prático"],
    };
    setModules([...modules, newMod]);
  };

  const handleRemoveModule = (id: string) => {
    if (modules.length <= 1) return;
    setModules(modules.filter((m) => m.id !== id));
  };

  const handleUpdateModule = (id: string, field: "title" | "description" | "estimatedMinutes", value: any) => {
    setModules(modules.map((m) => (m.id === id ? { ...m, [field]: value } : m)));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    const slug =
      title
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/(^-|-$)/g, "") +
      "-" +
      Math.random().toString(36).substring(2, 6);

    const newTrack: TrackMetadata = {
      id: slug,
      title: title.trim(),
      subject,
      difficulty,
      retentionRate: 85,
      description:
        description.trim() ||
        `Trilha personalizada focada em ${subject} com ${modules.length} módulos práticos e verificação no juiz.`,
      modules,
      isCustom: true,
      createdAt: new Date().toISOString(),
    };

    onTrackCreated(newTrack);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="bg-card border border-border rounded-3xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-border flex items-center justify-between shrink-0 bg-card/60">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
              <Compass className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-foreground">Criar Nova Trilha de Estudo</h2>
              <p className="text-[11px] text-muted-foreground">
                Gere módulos estruturados com Inteligência Artificial ou configure manualmente.
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

        {/* Tab Switcher */}
        <div className="px-6 pt-3 pb-2 flex items-center gap-2 border-b border-border bg-secondary/30">
          <button
            type="button"
            onClick={() => setActiveTab("ai")}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              activeTab === "ai"
                ? "bg-primary text-primary-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground hover:bg-accent/50"
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Gerar com IA</span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("manual")}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              activeTab === "manual"
                ? "bg-primary text-primary-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground hover:bg-accent/50"
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>Edição dos Módulos {title && `(${modules.length})`}</span>
          </button>
          {generationSuccess && (
            <span className="ml-auto inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20">
              <CheckCircle2 className="w-3 h-3" />
              <span>Gerada pela IA</span>
            </span>
          )}
        </div>

        {/* Tab 1: AI Prompt Generator */}
        {activeTab === "ai" && (
          <div className="p-6 space-y-4 overflow-y-auto">
            <div className="p-4 rounded-2xl bg-primary/5 border border-primary/20 space-y-2">
              <div className="flex items-center gap-2 text-xs font-bold text-primary">
                <Wand2 className="w-4 h-4" />
                <span>Arquiteto Pedagógico com IA</span>
              </div>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Descreva em linguagem natural o que deseja aprender. A IA criará uma sequência de módulos com tempos de estudo estimados, conceitos essenciais e exercícios para o Juiz C++.
              </p>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-foreground">
                O que você quer aprender nesta trilha?
              </label>
              <textarea
                rows={3}
                value={aiPrompt}
                onChange={(e) => setAiPrompt(e.target.value)}
                placeholder="Ex: Quero uma trilha sobre estrutura de dados com foco em Árvore Binária e Árvore Balanceada..."
                className="w-full bg-secondary/80 border border-border rounded-xl p-3 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary resize-none font-medium"
              />
            </div>

            {/* Quick Suggestions */}
            <div className="space-y-1.5">
              <span className="text-[11px] font-semibold text-muted-foreground flex items-center gap-1">
                <Lightbulb className="w-3 h-3 text-amber-400" />
                Sugestões rápidas de trilhas:
              </span>
              <div className="flex flex-wrap gap-1.5">
                {PROMPT_SUGGESTIONS.map((s, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => {
                      setAiPrompt(s);
                      handleGenerateWithAi(s);
                    }}
                    className="text-[11px] px-2.5 py-1 rounded-lg bg-secondary/90 hover:bg-primary/20 hover:text-primary text-muted-foreground border border-border/80 transition-all text-left"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 pt-1">
              <div className="space-y-1">
                <label className="text-xs font-semibold text-foreground">Dificuldade desejada</label>
                <select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value as any)}
                  className="w-full bg-secondary/80 border border-border rounded-xl px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-2 focus:ring-primary font-medium"
                >
                  <option value="Iniciante">Iniciante</option>
                  <option value="Intermediário">Intermediário</option>
                  <option value="Avançado">Avançado</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold text-foreground">Área / Assunto</label>
                <select
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  className="w-full bg-secondary/80 border border-border rounded-xl px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-2 focus:ring-primary font-medium"
                >
                  <option value="Estruturas de Dados">Estruturas de Dados</option>
                  <option value="Programação Dinâmica">Programação Dinâmica</option>
                  <option value="Grafos & Travessias">Grafos & Travessias</option>
                  <option value="Algoritmos Gulosos">Algoritmos Gulosos</option>
                  <option value="Geral">Ciência da Computação Geral</option>
                </select>
              </div>
            </div>

            {errorMsg && (
              <p className="text-xs text-rose-400 bg-rose-500/10 p-2.5 rounded-xl border border-rose-500/20">
                {errorMsg}
              </p>
            )}

            <div className="pt-2 flex items-center justify-end gap-2">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
              >
                Cancelar
              </button>
              <button
                type="button"
                disabled={isGenerating || !aiPrompt.trim()}
                onClick={() => handleGenerateWithAi()}
                className="flex items-center gap-1.5 px-5 py-2.5 rounded-xl text-xs font-bold bg-primary text-primary-foreground hover:bg-primary-hover shadow-sm transition-all disabled:opacity-50"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Estruturando Trilha com IA...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Gerar Trilha com IA</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Tab 2: Manual Review & Edit Form */}
        {activeTab === "manual" && (
          <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-foreground">
                Título da Trilha <span className="text-primary">*</span>
              </label>
              <input
                type="text"
                required
                placeholder="ex: Estruturas de Dados Hierárquicas: Árvores Binárias e Balanceadas"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full bg-secondary/80 border border-border rounded-xl px-3.5 py-2 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary font-medium"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="text-xs font-semibold text-foreground">Área / Assunto</label>
                <input
                  type="text"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  className="w-full bg-secondary/80 border border-border rounded-xl px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-2 focus:ring-primary font-medium"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold text-foreground">Dificuldade</label>
                <select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value as any)}
                  className="w-full bg-secondary/80 border border-border rounded-xl px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-2 focus:ring-primary font-medium"
                >
                  <option value="Iniciante">Iniciante</option>
                  <option value="Intermediário">Intermediário</option>
                  <option value="Avançado">Avançado</option>
                </select>
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-foreground">Objetivo / Descrição</label>
              <textarea
                rows={2}
                placeholder="Descrição pedagógica da trilha..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full bg-secondary/80 border border-border rounded-xl px-3 py-2 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary resize-none font-medium"
              />
            </div>

            {/* Modules List */}
            <div className="space-y-3 pt-2 border-t border-border">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-foreground flex items-center gap-1.5">
                  <BookOpen className="w-3.5 h-3.5 text-primary" />
                  Módulos de Aprendizado ({modules.length})
                </span>
                <button
                  type="button"
                  onClick={handleAddModule}
                  className="flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-secondary hover:bg-accent text-foreground border border-border transition-colors"
                >
                  <Plus className="w-3 h-3 text-primary" />
                  <span>Adicionar Módulo</span>
                </button>
              </div>

              <div className="space-y-2.5 max-h-52 overflow-y-auto pr-1">
                {modules.map((m, idx) => (
                  <div
                    key={m.id}
                    className="p-3 rounded-xl border border-border bg-card/40 space-y-1.5 relative group hover:border-slate-700 transition-colors"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-[10px] font-mono text-primary font-bold">
                        {String(idx + 1).padStart(2, "0")}.
                      </span>
                      <input
                        type="text"
                        value={m.title}
                        onChange={(e) => handleUpdateModule(m.id, "title", e.target.value)}
                        className="flex-1 bg-transparent border-b border-border/60 pb-0.5 text-xs font-semibold text-foreground focus:outline-none focus:border-primary"
                      />
                      <div className="flex items-center gap-1">
                        <input
                          type="number"
                          min="5"
                          max="300"
                          value={m.estimatedMinutes}
                          onChange={(e) =>
                            handleUpdateModule(m.id, "estimatedMinutes", parseInt(e.target.value) || 30)
                          }
                          className="w-12 bg-secondary/80 border border-border rounded px-1.5 py-0.5 text-[11px] text-right font-mono text-muted-foreground focus:outline-none"
                        />
                        <span className="text-[10px] text-muted-foreground">min</span>
                        {modules.length > 1 && (
                          <button
                            type="button"
                            onClick={() => handleRemoveModule(m.id)}
                            className="p-1 rounded text-muted-foreground hover:text-rose-400 hover:bg-rose-500/10 transition-colors ml-1"
                          >
                            <Trash2 className="w-3 h-3" />
                          </button>
                        )}
                      </div>
                    </div>
                    <input
                      type="text"
                      value={m.description}
                      onChange={(e) => handleUpdateModule(m.id, "description", e.target.value)}
                      placeholder="Descrição do módulo..."
                      className="w-full bg-transparent text-[11px] text-muted-foreground focus:outline-none placeholder:text-muted-foreground/60"
                    />
                    {m.lessons && m.lessons.length > 0 && (
                      <div className="flex flex-wrap gap-1 pt-1">
                        {m.lessons.map((les, lIdx) => (
                          <span
                            key={lIdx}
                            className="text-[10px] px-2 py-0.5 rounded bg-secondary/70 text-muted-foreground border border-border/60"
                          >
                            {les}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-2 flex items-center justify-between gap-2 shrink-0">
              <button
                type="button"
                onClick={() => setActiveTab("ai")}
                className="flex items-center gap-1 text-xs text-primary font-semibold hover:underline"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Voltar ao Gerador IA</span>
              </button>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="flex items-center gap-1.5 px-5 py-2 rounded-xl text-xs font-bold bg-primary text-primary-foreground hover:bg-primary-hover shadow-sm transition-all"
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Salvar Trilha</span>
                </button>
              </div>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
