"use client";

import React, { useState } from "react";
import { Terminal, Loader2, Send, Lightbulb } from "lucide-react";
import { whiteboardService, WhiteboardPromptResult } from "@/services/whiteboardService";

interface WhiteboardPromptBarProps {
  onGenerated: (result: WhiteboardPromptResult) => void;
  className?: string;
}

const PRESET_PROMPTS = [
  { label: "BST (Busca Binária)", text: "Gere uma árvore binária de busca BST com 7 nós e código C++ de busca binária do valor 25" },
  { label: "Árvore Binária (7 nós)", text: "Gere uma árvore binária balanceada com 7 nós e código C++ DFS" },
  { label: "Grafo Bipartido K3,3", text: "Crie um grafo bipartido completo K3,3 com 6 nós e algoritmo BFS em C++" },
  { label: "Grafo Dijkstra Ponderado", text: "Gere um grafo orientado com pesos para simulação de Dijkstra em C++" },
  { label: "Ciclo com Ponte", text: "Crie um grafo com um ciclo e uma aresta de ponte para teste de conectividade C++" },
  { label: "Desconexo (2 componentes)", text: "Gere um grafo desconexo com 2 componentes independentes em C++" },
];

export function WhiteboardPromptBar({ onGenerated, className = "" }: WhiteboardPromptBarProps) {
  const [prompt, setPrompt] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const abortControllerRef = React.useRef<AbortController | null>(null);

  const handleSubmit = async (e?: React.FormEvent, customPrompt?: string) => {
    if (e) e.preventDefault();
    const targetPrompt = (customPrompt || prompt).trim();
    if (!targetPrompt) return;

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    setIsLoading(true);
    setStatusMessage(`Processando topologia: "${targetPrompt}"...`);

    try {
      const res = await whiteboardService.generateFromPrompt(targetPrompt);
      if (res && res.nodes && res.nodes.length > 0) {
        onGenerated(res);
        setStatusMessage(`Grafo gerado: ${res.topic || res.title || "Personalizado"} (${res.nodes.length} nós)`);
      } else {
        setStatusMessage("Não foi possível gerar a topologia. Tente outro prompt.");
      }
    } catch (err: any) {
      if (err.name !== "AbortError") {
        console.error("Falha ao gerar grafo via prompt:", err);
        setStatusMessage("Erro ao consultar motor de IA. Verifique a conexão.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickPreset = (presetText: string) => {
    setPrompt(presetText);
    handleSubmit(undefined, presetText);
  };

  return (
    <div className={`p-3 bg-slate-900 border border-slate-800 rounded-lg shadow-sm space-y-2.5 ${className}`}>
      {/* Form de Input */}
      <form onSubmit={handleSubmit} className="flex items-center gap-2">
        <div className="relative flex-1">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
            <Terminal className="w-4 h-4" />
          </div>
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={isLoading}
            placeholder="Descreva a estrutura desejada (ex: 'Árvore binária 7 nós', 'Grafo bipartido K3,3', 'Dijkstra ponderado')..."
            className="w-full pl-9 pr-3 py-2 bg-slate-950/70 border border-slate-800 rounded-md text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-slate-700 transition-colors disabled:opacity-50 font-normal"
          />
        </div>

        <button
          type="submit"
          disabled={isLoading || !prompt.trim()}
          className="flex items-center gap-1.5 px-3.5 py-2 bg-blue-600 text-white rounded-md text-xs font-medium hover:bg-blue-500 transition-colors shadow-sm disabled:opacity-40 shrink-0"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              <span>Gerando...</span>
            </>
          ) : (
            <>
              <Send className="w-3 h-3" />
              <span>Gerar no Quadro</span>
            </>
          )}
        </button>
      </form>

      {/* Quick Presets Pills */}
      <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
        <span className="flex items-center gap-1 text-slate-400 font-medium pr-1">
          <Lightbulb className="w-3 h-3 text-amber-400" />
          Presets:
        </span>
        {PRESET_PROMPTS.map((p, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => handleQuickPreset(p.text)}
            disabled={isLoading}
            className="px-2 py-0.5 bg-slate-800/80 hover:bg-slate-800 text-slate-300 hover:text-slate-100 border border-slate-700/50 rounded text-[11px] transition-colors disabled:opacity-40"
          >
            {p.label}
          </button>
        ))}
      </div>

      {/* Status Feedback */}
      {statusMessage && (
        <div className="text-[11px] font-mono text-slate-400 px-1 flex items-center justify-between border-t border-slate-800/60 pt-1.5">
          <span>{statusMessage}</span>
          <button
            type="button"
            onClick={() => setStatusMessage(null)}
            className="text-slate-500 hover:text-slate-300 text-[10px]"
          >
            limpar
          </button>
        </div>
      )}
    </div>
  );
}
