import React from "react";
import { MemorySnapshot } from "@/types/graphLab";
import { Layers, Database, Terminal, ListOrdered } from "lucide-react";

interface MemoryPanelProps {
  memoryState?: MemorySnapshot;
  logMessage?: string;
}

export function MemoryPanel({ memoryState, logMessage }: MemoryPanelProps) {
  const stack = memoryState?.stack || [];
  const visited = memoryState?.visited || {};
  const queue = memoryState?.queue;
  const dist = memoryState?.currentDist;
  const localVars = memoryState?.localVars;

  return (
    <div className="flex flex-col h-full bg-[#1e293b]/90 border border-slate-700/60 rounded-2xl overflow-hidden backdrop-blur-md text-slate-200">
      {/* Header */}
      <div className="px-4 py-2.5 border-b border-slate-700/60 flex items-center justify-between bg-slate-900/40">
        <div className="flex items-center gap-2">
          <Database className="w-4 h-4 text-emerald-400" />
          <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
            Painel de Memória Viva (Call Stack & Arrays)
          </span>
        </div>
      </div>

      <div className="p-3.5 space-y-4 overflow-y-auto flex-1 font-mono text-xs">
        {/* Call Stack Section */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-[11px] text-slate-400 font-sans">
            <span className="flex items-center gap-1.5 font-bold uppercase tracking-wide">
              <Layers className="w-3.5 h-3.5 text-amber-400" />
              Call Stack ({stack.length} frames)
            </span>
            <span className="text-[10px] text-slate-500">Topo da Pilha ↑</span>
          </div>

          <div className="space-y-1.5 min-h-[70px] max-h-[140px] overflow-y-auto p-2 bg-slate-950/60 rounded-xl border border-slate-800/80">
            {stack.length === 0 ? (
              <span className="text-slate-500 text-[11px] italic">Pilha vazia (nenhuma função em execução)</span>
            ) : (
              [...stack].reverse().map((frame, index) => {
                const isTop = index === 0;
                return (
                  <div
                    key={`${frame.functionName}-${frame.callDepth}-${index}`}
                    className={`p-2 rounded-lg border text-xs flex items-center justify-between transition-all ${
                      isTop
                        ? "bg-amber-500/15 border-amber-500/50 text-amber-200 font-semibold shadow-sm"
                        : "bg-slate-900/60 border-slate-800 text-slate-300"
                    }`}
                  >
                    <span>
                      {frame.functionName}({Object.entries(frame.args).map(([k, v]) => `${k}=${v}`).join(", ")})
                    </span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800/80 text-slate-400">
                      depth: {frame.callDepth}
                    </span>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Queue Section (if BFS) */}
        {queue && (
          <div className="space-y-1.5">
            <div className="flex items-center gap-1.5 text-[11px] text-slate-400 font-sans font-bold uppercase tracking-wide">
              <ListOrdered className="w-3.5 h-3.5 text-sky-400" />
              Fila FIFO [Início → Fim]
            </div>
            <div className="flex items-center gap-1.5 p-2 bg-slate-950/60 rounded-xl border border-slate-800/80 overflow-x-auto min-h-[38px]">
              {queue.length === 0 ? (
                <span className="text-slate-500 text-[11px] italic">Fila vazia</span>
              ) : (
                queue.map((item, idx) => (
                  <div
                    key={idx}
                    className="px-2.5 py-1 rounded-md bg-sky-500/20 border border-sky-500/40 text-sky-300 text-[11px] font-bold"
                  >
                    {item}
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* Visited Array */}
        <div className="space-y-1.5">
          <div className="text-[11px] text-slate-400 font-sans font-bold uppercase tracking-wide">
            visited[] Array
          </div>
          <div className="grid grid-cols-4 sm:grid-cols-6 gap-1.5">
            {Object.entries(visited).map(([nodeId, isVisited]) => (
              <div
                key={nodeId}
                className={`p-1.5 rounded-lg border text-center transition-colors ${
                  isVisited
                    ? "bg-emerald-500/15 border-emerald-500/50 text-emerald-300 font-bold"
                    : "bg-slate-950/40 border-slate-800/60 text-slate-500"
                }`}
              >
                <div className="text-[10px] text-slate-400">Nó {nodeId}</div>
                <div className="text-xs">{isVisited ? "T" : "F"}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Distance Array (if present) */}
        {dist && Object.keys(dist).length > 0 && (
          <div className="space-y-1.5">
            <div className="text-[11px] text-slate-400 font-sans font-bold uppercase tracking-wide">
              dist[] (Origem → Vértice)
            </div>
            <div className="grid grid-cols-4 sm:grid-cols-6 gap-1.5">
              {Object.entries(dist).map(([nodeId, d]) => (
                <div
                  key={nodeId}
                  className="p-1.5 rounded-lg border bg-slate-950/40 border-slate-800/60 text-center"
                >
                  <div className="text-[10px] text-slate-400">Nó {nodeId}</div>
                  <div className="text-xs font-bold text-sky-300">{d >= 0 ? d : "∞"}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Local Variables */}
        {localVars && Object.keys(localVars).length > 0 && (
          <div className="space-y-1.5">
            <div className="text-[11px] text-slate-400 font-sans font-bold uppercase tracking-wide">
              Variáveis Locais do Escopo
            </div>
            <div className="flex flex-wrap gap-2 p-2 bg-slate-950/60 rounded-xl border border-slate-800/80">
              {Object.entries(localVars).map(([key, val]) => (
                <span key={key} className="text-[11px] text-slate-300">
                  <span className="text-indigo-400">{key}</span> ={" "}
                  <span className="text-emerald-300 font-bold">{String(val)}</span>
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Step Log Message */}
        {logMessage && (
          <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-700/60 flex items-start gap-2 text-[11px] text-slate-300 font-sans">
            <Terminal className="w-3.5 h-3.5 text-primary shrink-0 mt-0.5" />
            <p className="leading-snug">{logMessage}</p>
          </div>
        )}
      </div>
    </div>
  );
}
