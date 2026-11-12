import React, { useState, useEffect } from "react";
import { Search, Command, Terminal, ChevronRight } from "lucide-react";

interface UniversalBarProps {
  onSearchSubmit?: (query: string) => void;
}

export function UniversalBar({ onSearchSubmit }: UniversalBarProps) {
  const [query, setQuery] = useState("");
  const [isFocused, setIsFocused] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        document.getElementById("universal-command-input")?.focus();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    onSearchSubmit?.(query.trim());
  };

  const suggestions = [
    { label: "BFS e DFS em Grafos", query: "Explicar BFS e DFS com Fila e Pilha em C++" },
    { label: "Dijkstra com Heap", query: "Dijkstra com Priority Queue em C++" },
    { label: "Segment Tree", query: "Segment Tree e Divisão e Conquista em C++" },
  ];

  return (
    <div className="w-full max-w-2xl mx-auto relative">
      <form
        onSubmit={handleSubmit}
        className={`relative flex items-center bg-slate-900/90 rounded-lg border transition-colors duration-150 ${
          isFocused
            ? "border-slate-700 ring-1 ring-slate-700 shadow-sm"
            : "border-slate-800 shadow-sm hover:border-slate-700/80"
        }`}
      >
        <div className="pl-3.5 pr-2 text-slate-400">
          <Search className="w-4 h-4" />
        </div>
        <input
          id="universal-command-input"
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder="Buscar algoritmo, tópico ou estrutura (ex: Dijkstra, SegTree, DP)..."
          className="w-full py-2.5 pr-20 bg-transparent text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none"
        />
        <div className="absolute right-2.5 flex items-center gap-1.5 pointer-events-none">
          <kbd className="hidden sm:inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-400 border border-slate-700/60">
            <Command className="w-2.5 h-2.5" /> K
          </kbd>
        </div>
      </form>

      {/* Quick Prompt Badges */}
      <div className="flex items-center gap-2 mt-2 px-1 text-[11px] text-slate-400 overflow-x-auto no-scrollbar">
        <span className="shrink-0 flex items-center gap-1 text-slate-400 font-medium">
          <Terminal className="w-3 h-3 text-slate-500" /> Tópicos rápidos:
        </span>
        {suggestions.map((item, idx) => (
          <React.Fragment key={item.label}>
            {idx > 0 && <span className="text-slate-600">·</span>}
            <button
              type="button"
              onClick={() => onSearchSubmit?.(item.query)}
              className="whitespace-nowrap px-2 py-0.5 rounded text-slate-300 hover:text-slate-100 hover:bg-slate-800 transition-colors"
            >
              {item.label}
            </button>
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}
