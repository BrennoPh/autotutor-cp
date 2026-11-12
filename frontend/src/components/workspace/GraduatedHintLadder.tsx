"use client";

import React, { useState, useEffect } from "react";
import {
  X,
  ShieldCheck,
  BookOpen,
  Brain,
  ChevronRight,
  ExternalLink,
  Layers,
  HelpCircle,
  Sparkles,
} from "lucide-react";
import { tutorService } from "@/services/tutorService";
import { GraduatedHintResponse } from "@/types/tutor";
import { MarkdownViewer } from "@/components/common/MarkdownViewer";

interface GraduatedHintLadderProps {
  problemId: string;
  problemTitle: string;
  currentCode?: string;
  isOpen: boolean;
  onClose: () => void;
}

const TIER_LABELS = [
  { tier: 1, label: "T1: Invariante", desc: "Teoremas e Propriedades" },
  { tier: 2, label: "T2: Contraexemplo", desc: "Casos de Borda e Mesa" },
  { tier: 3, label: "T3: Modelagem", desc: "Estados e Estruturas" },
  { tier: 4, label: "T4: Esqueleto", desc: "Decomposição Lógica" },
];

export function GraduatedHintLadder({
  problemId,
  problemTitle,
  currentCode,
  isOpen,
  onClose,
}: GraduatedHintLadderProps) {
  const [activeTier, setActiveTier] = useState<number>(1);
  const [maxUnlockedTier, setMaxUnlockedTier] = useState<number>(1);
  const [hintsCache, setHintsCache] = useState<Record<number, GraduatedHintResponse>>({});
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchHint = async (tier: number) => {
    if (hintsCache[tier]) {
      setActiveTier(tier);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const res = await tutorService.getGraduatedHint({
        problem_id: problemId,
        tier,
        current_code: currentCode,
      });
      setHintsCache((prev) => ({ ...prev, [tier]: res }));
      setActiveTier(tier);
      if (res.next_tier_available && res.next_tier_available > maxUnlockedTier) {
        setMaxUnlockedTier(res.next_tier_available);
      }
    } catch (err: any) {
      setError(err?.message || "Erro ao consultar pista socrática.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen && problemId) {
      if (!hintsCache[1]) {
        fetchHint(1);
      }
    }
  }, [isOpen, problemId]);

  if (!isOpen) return null;

  const currentHint = hintsCache[activeTier];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="ladder-title"
        className="w-full max-w-2xl max-h-[85vh] bg-slate-900 border border-slate-800 rounded-xl shadow-2xl flex flex-col overflow-hidden text-slate-100"
      >
        {/* Header */}
        <div className="px-5 py-3.5 border-b border-slate-800 bg-slate-950/80 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-blue-950/80 border border-blue-800/60 flex items-center justify-center text-blue-400">
              <Layers className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 id="ladder-title" className="text-sm font-semibold text-slate-100">
                  Pistas Socráticas Graduais (4 Tiers)
                </h3>
                <span className="flex items-center gap-1 text-[10px] font-medium px-2 py-0.5 rounded-full bg-emerald-950/80 text-emerald-400 border border-emerald-800/50">
                  <ShieldCheck className="w-3 h-3" />
                  Zero-Leak Verificado
                </span>
              </div>
              <p className="text-[11px] text-slate-400">{problemTitle}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            aria-label="Fechar modal de pistas"
            className="p-1 rounded-md text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Tier Selector Navigation */}
        <div className="grid grid-cols-4 p-2 bg-slate-950/50 border-b border-slate-800 gap-1.5 text-xs">
          {TIER_LABELS.map((item) => {
            const isUnlocked = item.tier <= maxUnlockedTier;
            const isActive = item.tier === activeTier;
            return (
              <button
                key={item.tier}
                disabled={!isUnlocked}
                onClick={() => fetchHint(item.tier)}
                className={`p-2 rounded-lg text-left transition-all ${
                  isActive
                    ? "bg-slate-800 border border-blue-500/60 shadow-xs text-white"
                    : isUnlocked
                    ? "bg-slate-900/60 hover:bg-slate-800/60 border border-slate-800 text-slate-300"
                    : "opacity-40 cursor-not-allowed bg-slate-950 border border-slate-900 text-slate-500"
                }`}
              >
                <div className="font-semibold text-[11px] truncate">{item.label}</div>
                <div className="text-[9px] text-slate-400 truncate">{item.desc}</div>
              </button>
            );
          })}
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4 text-xs leading-relaxed">
          {isLoading ? (
            <div className="space-y-3 py-8 animate-pulse text-center text-slate-400">
              <HelpCircle className="w-8 h-8 mx-auto text-blue-400 animate-spin" />
              <p className="text-xs">Consultando acervo RAG e adaptando à sua memória...</p>
            </div>
          ) : error ? (
            <div className="p-3 bg-red-950/30 border border-red-800/60 rounded-lg text-red-300">
              <p className="font-semibold">Erro ao carregar pista</p>
              <p className="text-[11px] mt-1">{error}</p>
            </div>
          ) : currentHint ? (
            <>
              {/* Cognitive Memory Context Badge */}
              {currentHint.memory_trigger && (
                <div className="p-3 rounded-lg bg-blue-950/30 border border-blue-900/50 flex items-start gap-2.5">
                  <Brain className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                  <div className="text-[11px] text-slate-300">
                    <span className="font-semibold text-blue-300 block">Memória Cognitiva (AI Memory):</span>
                    {currentHint.memory_trigger}
                  </div>
                </div>
              )}

              {/* Main Markdown Socratic Hint */}
              <div className="prose prose-invert prose-xs max-w-none text-slate-200">
                <MarkdownViewer content={currentHint.hint_markdown} />
              </div>

              {/* RAG Canonical Citations */}
              {currentHint.rag_citations && currentHint.rag_citations.length > 0 && (
                <div className="mt-4 pt-3 border-t border-slate-800 space-y-2">
                  <div className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-300">
                    <BookOpen className="w-3.5 h-3.5 text-blue-400" />
                    <span>Literatura Canônica Recuperada (RAG):</span>
                  </div>
                  <div className="space-y-1.5">
                    {currentHint.rag_citations.map((cit, idx) => (
                      <div
                        key={idx}
                        className="p-2 rounded bg-slate-950/60 border border-slate-800/80 flex items-center justify-between text-[11px]"
                      >
                        <div className="truncate pr-2">
                          <span className="font-medium text-slate-200">{cit.title}</span>
                          <span className="text-slate-400 block text-[10px]">{cit.publisher}</span>
                        </div>
                        {cit.url && cit.url.startsWith("http") && (
                          <a
                            href={cit.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-400 hover:text-blue-300 p-1 shrink-0"
                            title="Ver fonte oficial"
                          >
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : null}
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-slate-800 bg-slate-950/80 flex items-center justify-between text-xs">
          <span className="text-[11px] text-slate-400">
            Tier {activeTier} de 4 · Nenhum código completo é fornecido
          </span>
          {activeTier < 4 && (
            <button
              onClick={() => fetchHint(activeTier + 1)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold transition-colors"
            >
              <span>Avançar para Tier {activeTier + 1}</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
