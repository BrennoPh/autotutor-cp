"use client";

import React, { useState } from "react";
import {
  X,
  Gauge,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  HelpCircle,
  Clock,
  Database,
  Cpu,
} from "lucide-react";
import { tutorService } from "@/services/tutorService";
import { PreFlightResponse } from "@/types/tutor";

interface PreFlightModalProps {
  problemId: string;
  problemTitle: string;
  isOpen: boolean;
  onClose: () => void;
}

const COMPLEXITY_PRESETS = ["O(V + E)", "O(N log N)", "O(N)", "O(N^2)", "O(2^N)"];
const STRUCTURE_PRESETS = [
  "Lista de Adjacência",
  "Matriz de Adjacência",
  "Segment Tree",
  "Vetor Auxiliar",
  "Fila / Fila de Prioridade",
];

export function PreFlightModal({
  problemId,
  problemTitle,
  isOpen,
  onClose,
}: PreFlightModalProps) {
  const [complexity, setComplexity] = useState("O(V + E)");
  const [structure, setStructure] = useState("Lista de Adjacência");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<PreFlightResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleEvaluate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    try {
      const res = await tutorService.evaluatePreflight({
        problem_id: problemId,
        proposed_complexity: complexity,
        chosen_structure: structure,
      });
      setResult(res);
    } catch (err: any) {
      setError(err?.message || "Falha ao avaliar complexidade.");
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="preflight-title"
        className="w-full max-w-xl max-h-[85vh] bg-slate-900 border border-slate-800 rounded-xl shadow-2xl flex flex-col overflow-hidden text-slate-100"
      >
        {/* Header */}
        <div className="px-5 py-3.5 border-b border-slate-800 bg-slate-950/80 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-indigo-950/80 border border-indigo-800/60 flex items-center justify-center text-indigo-400">
              <Gauge className="w-4 h-4" />
            </div>
            <div>
              <h3 id="preflight-title" className="text-sm font-semibold text-slate-100">
                Pre-Flight Check: Intuição & Complexidade
              </h3>
              <p className="text-[11px] text-slate-400">{problemTitle}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            aria-label="Fechar pre-flight check"
            className="p-1 rounded-md text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4 text-xs">
          <form onSubmit={handleEvaluate} className="space-y-4">
            {/* Complexity Selection */}
            <div className="space-y-1.5">
              <label className="text-[11px] font-semibold text-slate-300 block">
                Complexidade Assintótica Prevista de Tempo:
              </label>
              <div className="flex flex-wrap gap-1.5 mb-2">
                {COMPLEXITY_PRESETS.map((p) => (
                  <button
                    key={p}
                    type="button"
                    onClick={() => setComplexity(p)}
                    className={`px-2.5 py-1 rounded-md border text-[11px] font-mono transition-colors ${
                      complexity === p
                        ? "bg-indigo-600 text-white border-indigo-500 font-semibold"
                        : "bg-slate-950/70 border-slate-800 text-slate-300 hover:bg-slate-800"
                    }`}
                  >
                    {p}
                  </button>
                ))}
              </div>
              <input
                type="text"
                value={complexity}
                onChange={(e) => setComplexity(e.target.value)}
                placeholder="Ex: O(N log N) ou O(V + E)"
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 font-mono text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-hidden"
              />
            </div>

            {/* Structure Selection */}
            <div className="space-y-1.5">
              <label className="text-[11px] font-semibold text-slate-300 block">
                Estrutura de Dados / Modelagem Escolhida:
              </label>
              <div className="flex flex-wrap gap-1.5 mb-2">
                {STRUCTURE_PRESETS.map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => setStructure(s)}
                    className={`px-2.5 py-1 rounded-md border text-[11px] transition-colors ${
                      structure === s
                        ? "bg-indigo-600 text-white border-indigo-500 font-semibold"
                        : "bg-slate-950/70 border-slate-800 text-slate-300 hover:bg-slate-800"
                    }`}
                  >
                    {s}
                  </button>
                ))}
              </div>
              <input
                type="text"
                value={structure}
                onChange={(e) => setStructure(e.target.value)}
                placeholder="Ex: Lista de Adjacência vector<int> adj[N]"
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-hidden"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Cpu className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
              <span>{isLoading ? "Avaliando Limites..." : "Simular Viabilidade Assintótica"}</span>
            </button>
          </form>

          {/* Results Feedback Card */}
          {error && (
            <div className="p-3 bg-red-950/40 border border-red-800/60 rounded-lg text-red-300">
              <p>{error}</p>
            </div>
          )}

          {result && (
            <div className="space-y-3 pt-2">
              <div
                className={`p-3.5 rounded-xl border flex items-center justify-between ${
                  result.verdict_preview === "VIABLE"
                    ? "bg-emerald-950/30 border-emerald-800/50 text-emerald-300"
                    : result.verdict_preview === "MLE_RISK"
                    ? "bg-amber-950/30 border-amber-800/50 text-amber-300"
                    : "bg-red-950/30 border-red-800/50 text-red-300"
                }`}
              >
                <div className="flex items-center gap-2.5">
                  {result.verdict_preview === "VIABLE" ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  ) : result.verdict_preview === "MLE_RISK" ? (
                    <Database className="w-5 h-5 text-amber-400" />
                  ) : (
                    <AlertTriangle className="w-5 h-5 text-red-400" />
                  )}
                  <div>
                    <span className="font-bold text-xs uppercase tracking-wide">
                      Veredito Prévio: {result.verdict_preview}
                    </span>
                    <p className="text-[11px] opacity-90">
                      Status da Hipótese: {result.status}
                    </p>
                  </div>
                </div>
                <div className="text-right text-[10px] font-mono opacity-80">
                  <div>~{result.estimated_operations.toLocaleString()} ops</div>
                  <div>Limite: {result.time_limit_sec}s</div>
                </div>
              </div>

              <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-lg text-slate-300 leading-relaxed text-[11px]">
                {result.feedback}
              </div>

              {/* Edge Cases Checklist */}
              {result.edge_cases_to_watch && result.edge_cases_to_watch.length > 0 && (
                <div className="space-y-2 pt-1">
                  <div className="text-[11px] font-semibold text-slate-300 flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-indigo-400" />
                    <span>Casos de Borda para Revisar Antes de Submeter:</span>
                  </div>
                  <div className="space-y-1">
                    {result.edge_cases_to_watch.map((ec, idx) => (
                      <div
                        key={idx}
                        className="px-2.5 py-1.5 bg-slate-950/40 border border-slate-800/80 rounded flex items-center gap-2 text-[11px] text-slate-300"
                      >
                        <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 shrink-0" />
                        <span>{ec}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
