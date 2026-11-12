"use client";

import React, { useState } from "react";
import { Check, Copy } from "lucide-react";

export interface CodeBlockProps {
  language?: string;
  code: string;
}

export const CodeBlock: React.FC<CodeBlockProps> = ({ language, code }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback
    }
  };

  const displayLang = language ? language.toUpperCase() : "CODE";

  return (
    <div className="my-4 overflow-hidden rounded-xl border border-slate-800 bg-slate-950/90 shadow-sm backdrop-blur-sm">
      <div className="flex items-center justify-between border-b border-slate-800/80 bg-slate-900/60 px-4 py-2">
        <span className="text-[11px] font-mono font-semibold tracking-wider text-indigo-400">
          {displayLang}
        </span>
        <button
          type="button"
          onClick={handleCopy}
          aria-label="Copiar bloco de código"
          className="flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-medium text-slate-400 hover:bg-slate-800 hover:text-slate-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 transition-colors"
        >
          {copied ? (
            <>
              <Check className="h-3.5 w-3.5 text-emerald-400" />
              <span className="text-emerald-400">Copiado!</span>
            </>
          ) : (
            <>
              <Copy className="h-3.5 w-3.5" />
              <span>Copiar</span>
            </>
          )}
        </button>
      </div>

      <div className="overflow-x-auto p-4 text-xs font-mono leading-relaxed text-slate-200">
        <pre className="m-0 p-0 bg-transparent">
          <code>{code}</code>
        </pre>
      </div>
    </div>
  );
};
