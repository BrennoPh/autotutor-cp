import React from "react";
import { Code2 } from "lucide-react";

interface CodeTracerPanelProps {
  codeLines: string[];
  activeLineIndex?: number; // 1-indexed
  title?: string;
}

export function CodeTracerPanel({
  codeLines,
  activeLineIndex = 1,
  title = "Algoritmo em Execução (Python)",
}: CodeTracerPanelProps) {
  return (
    <div className="flex flex-col h-full bg-[#1e293b]/90 border border-slate-700/60 rounded-2xl overflow-hidden backdrop-blur-md text-slate-200">
      <div className="px-4 py-2.5 border-b border-slate-700/60 flex items-center justify-between bg-slate-900/40">
        <div className="flex items-center gap-2">
          <Code2 className="w-4 h-4 text-primary" />
          <span className="text-xs font-bold uppercase tracking-wider text-slate-300">{title}</span>
        </div>
        <span className="text-[11px] text-slate-400 font-mono">Linha {activeLineIndex}</span>
      </div>

      <div className="p-3 overflow-y-auto flex-1 font-mono text-xs leading-relaxed space-y-0.5">
        {codeLines.map((line, idx) => {
          const lineNumber = idx + 1;
          const isActive = lineNumber === activeLineIndex;

          return (
            <div
              key={lineNumber}
              className={`flex items-center gap-3 px-2 py-0.5 rounded-md transition-colors ${
                isActive
                  ? "bg-primary/25 border border-primary/50 text-white font-bold shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <span className={`w-5 text-right select-none text-[11px] ${isActive ? "text-primary" : "text-slate-600"}`}>
                {lineNumber}
              </span>
              <pre className="font-mono text-xs whitespace-pre">{line}</pre>
            </div>
          );
        })}
      </div>
    </div>
  );
}
