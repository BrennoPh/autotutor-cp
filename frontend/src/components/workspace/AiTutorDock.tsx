import React, { useState } from "react";
import {
  Send,
  X,
  Terminal,
  Bot,
  AlertCircle,
  Lightbulb,
  Puzzle,
  Eye,
  MessageSquareCode,
  Loader2,
} from "lucide-react";
import { TutorMessage, QuickSuggestion } from "@/types/tutor";
import { ComponentStatus } from "@/types/workspace";
import { Skeleton } from "@/components/ui/Skeleton";

export interface AiTutorDockProps {
  isOpen: boolean;
  onClose: () => void;
  status: ComponentStatus;
  messages: TutorMessage[];
  arenaContext?: {
    problem?: any;
    code?: string;
    result?: any;
  };
  onSendMessage?: (content: string) => void;
  onTriggerQuickAction?: (actionType: string, customPrompt?: string) => void;
}

const AGENT_BADGES: Record<string, { label: string; icon: string }> = {
  ai_memory_recall: { label: "Memória", icon: "🧠" },
  diagnostic_agent: { label: "Diagnóstico", icon: "🔍" },
  material_writer_agent: { label: "Teoria", icon: "📚" },
  problem_generator_agent: { label: "Desafio", icon: "🎯" },
  whiteboard_agent: { label: "Quadro", icon: "📊" },
  socratic_tutor_agent: { label: "Tutor", icon: "🤖" },
  ai_memory_consolidate: { label: "Checkpoint", icon: "💾" },
};

export function AiTutorDock({
  isOpen,
  onClose,
  status,
  messages,
  arenaContext,
  onSendMessage,
  onTriggerQuickAction,
}: AiTutorDockProps) {
  const [inputVal, setInputVal] = useState("");

  const handleAction = (actionType: string, promptText: string) => {
    onTriggerQuickAction?.(actionType, promptText);
  };

  const suggestions: QuickSuggestion[] = [
    { id: "1", label: "Diagnosticar código", prompt: "Analise meu código com o Juiz e oriente de forma socrática." },
    { id: "2", label: "Exercício de fixação", prompt: "Com base no meu histórico e erros, gere um problema de fixação." },
    { id: "3", label: "Analogia simples", prompt: "Pode me dar uma analogia simples sobre este conceito?" },
    { id: "4", label: "Casos de borda", prompt: "Qual é o caso de borda mais comum que causa WA ou TLE?" },
  ];

  if (!isOpen) return null;

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputVal.trim()) return;
    onSendMessage?.(inputVal.trim());
    setInputVal("");
  };

  return (
    <aside
      aria-label="Assistente de Código"
      className="fixed inset-y-0 right-0 z-40 w-full lg:w-[380px] xl:w-[420px] bg-slate-900 border-l border-slate-800 flex flex-col shadow-xl transition-transform duration-150"
    >
      {/* Header Sóbrio e Profissional */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800 bg-slate-900/90">
        <div className="flex items-center gap-2.5">
          <div className="w-6 h-6 rounded bg-slate-800 text-slate-300 flex items-center justify-center border border-slate-700/60">
            <Terminal className="w-3.5 h-3.5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-xs text-slate-100 block">Assistente de Código</span>
              <span className="flex items-center gap-1 text-[10px] text-slate-400 font-mono">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                Online
              </span>
            </div>
            <span className="text-[10px] text-slate-400">Ajuda contextual & Code Review C++</span>
          </div>
        </div>
        <button
          onClick={onClose}
          aria-label="Fechar painel do assistente"
          className="p-1 rounded text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Active Problem Context Bar */}
      {arenaContext?.problem && (
        <div className="px-3 py-1.5 bg-slate-950/60 border-b border-slate-800/80 flex items-center justify-between text-[11px]">
          <span className="truncate text-slate-400">
            Problema: <strong className="text-slate-200 font-medium">{arenaContext.problem.title}</strong>
          </span>
          {arenaContext.result && (
            <span
              className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-medium ${
                arenaContext.result.verdict === "AC"
                  ? "bg-emerald-950/80 text-emerald-400 border border-emerald-800/50"
                  : "bg-red-950/80 text-red-400 border border-red-800/50"
              }`}
            >
              {arenaContext.result.verdict}
            </span>
          )}
        </div>
      )}

      {/* Pedagogical Scaffolding Action Buttons */}
      <div className="p-2 border-b border-slate-800 bg-slate-900/50 grid grid-cols-2 gap-1.5 text-xs">
        <button
          type="button"
          onClick={() =>
            handleAction(
              "hint",
              "Me dê uma dica socrática para guiar o próximo passo sem revelar a resposta pronta."
            )
          }
          className="flex items-center gap-1.5 p-2 rounded-md bg-slate-800/70 hover:bg-slate-800 text-slate-300 hover:text-slate-100 border border-slate-700/50 text-[11px] font-medium transition-colors"
        >
          <Lightbulb className="w-3.5 h-3.5 text-amber-400 shrink-0" />
          <span>Dica Socrática</span>
        </button>

        <button
          type="button"
          onClick={() =>
            handleAction(
              "scaffolding",
              "Forneça um esqueleto de código com lacunas (scaffolding) e comentários para eu completar em C++."
            )
          }
          className="flex items-center gap-1.5 p-2 rounded-md bg-slate-800/70 hover:bg-slate-800 text-slate-300 hover:text-slate-100 border border-slate-700/50 text-[11px] font-medium transition-colors"
        >
          <Puzzle className="w-3.5 h-3.5 text-sky-400 shrink-0" />
          <span>Preencher Lacunas</span>
        </button>

        <button
          type="button"
          onClick={() =>
            handleAction(
              "minimal_example",
              "Mostre um exemplo mínimo de entrada e saída com o rastreamento das variáveis passo a passo."
            )
          }
          className="flex items-center gap-1.5 p-2 rounded-md bg-slate-800/70 hover:bg-slate-800 text-slate-300 hover:text-slate-100 border border-slate-700/50 text-[11px] font-medium transition-colors"
        >
          <Eye className="w-3.5 h-3.5 text-slate-300 shrink-0" />
          <span>Ver Exemplo</span>
        </button>

        <button
          type="button"
          onClick={() =>
            handleAction(
              "review_code",
              "Analise criticamente o código C++ que escrevi: comente as linhas, invariantes e se há risco de TLE ou WA."
            )
          }
          className="flex items-center gap-1.5 p-2 rounded-md bg-slate-800/70 hover:bg-slate-800 text-slate-300 hover:text-slate-100 border border-slate-700/50 text-[11px] font-medium transition-colors"
        >
          <MessageSquareCode className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
          <span>Comentar Código</span>
        </button>
      </div>

      {/* Messages Feed */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3.5 text-xs">
        {status === "loading" ? (
          <div className="space-y-2.5">
            <Skeleton className="h-10 w-3/4 rounded-md" />
            <Skeleton className="h-16 w-full rounded-md" />
          </div>
        ) : status === "error" ? (
          <div className="p-3 rounded-md border border-red-800/50 bg-red-950/30 text-red-300 flex items-start gap-2.5">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-red-400" />
            <div>
              <p className="font-medium text-xs text-red-200">Falha ao processar solicitação</p>
              <p className="text-[11px] text-red-400/90 mt-0.5">Não foi possível obter resposta. Tente reenviar.</p>
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-2.5 ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
            >
              {msg.sender === "tutor" && (
                <div className="w-5 h-5 rounded bg-slate-800 text-slate-400 flex items-center justify-center shrink-0 mt-0.5 border border-slate-700/60">
                  <Bot className="w-3 h-3" />
                </div>
              )}
              <div
                className={`max-w-[85%] rounded-md p-3 leading-relaxed text-xs ${
                  msg.sender === "user"
                    ? "bg-slate-800 text-slate-100 border border-slate-700/60 font-normal"
                    : "bg-slate-900 text-slate-200 border border-slate-800"
                }`}
              >
                <div className="whitespace-pre-line text-slate-200">{msg.content}</div>

                {msg.agentTrail && msg.agentTrail.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-slate-800/70 flex flex-wrap gap-1">
                    {msg.agentTrail.map((node) => {
                      const badge = AGENT_BADGES[node];
                      if (!badge) return null;
                      return (
                        <span
                          key={node}
                          className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] bg-slate-800 text-slate-400 border border-slate-700/50"
                        >
                          <span>{badge.icon}</span>
                          <span>{badge.label}</span>
                        </span>
                      );
                    })}
                  </div>
                )}

                <span className="text-[9px] text-slate-500 block mt-1.5 text-right font-mono">{msg.timestamp}</span>
              </div>
            </div>
          ))
        )}

        {status === "streaming" && (
          <div className="flex items-center gap-2 text-slate-400 text-[11px] px-2 py-1">
            <Loader2 className="w-3.5 h-3.5 animate-spin text-slate-400" />
            <span>Processando resposta...</span>
          </div>
        )}
      </div>

      {/* Suggestion Pills */}
      <div className="px-3 py-2 border-t border-slate-800 flex items-center gap-1.5 overflow-x-auto no-scrollbar bg-slate-900/60">
        {suggestions.map((sug) => (
          <button
            key={sug.id}
            onClick={() => onSendMessage?.(sug.prompt)}
            className="whitespace-nowrap px-2 py-0.5 rounded text-[11px] bg-slate-800/60 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-700/40 transition-colors shrink-0"
          >
            {sug.label}
          </button>
        ))}
      </div>

      {/* Input Form */}
      <form onSubmit={handleSend} className="p-2.5 border-t border-slate-800 bg-slate-900">
        <div className="flex items-center gap-2 bg-slate-950/70 rounded-md px-3 py-1.5 border border-slate-800 focus-within:border-slate-700 transition-colors">
          <input
            type="text"
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            placeholder="Perguntar sobre a lógica ou complexidade..."
            className="w-full bg-transparent text-xs text-slate-200 placeholder:text-slate-500 focus:outline-none"
          />
          <button
            type="submit"
            disabled={!inputVal.trim()}
            aria-label="Enviar mensagem"
            className="p-1 rounded bg-blue-600 text-white disabled:opacity-30 hover:bg-blue-500 transition-colors"
          >
            <Send className="w-3 h-3" />
          </button>
        </div>
      </form>
    </aside>
  );
}
