"use client";

import React, { useState, useEffect, useId } from "react";
import { AlertTriangle, Check, Copy, Code2, RefreshCw } from "lucide-react";

export interface MermaidDiagramProps {
  chart: string;
  className?: string;
  caption?: string;
}

export const MermaidDiagram: React.FC<MermaidDiagramProps> = ({
  chart,
  className = "",
  caption,
}) => {
  const reactId = useId().replace(/[^a-zA-Z0-9]/g, "");
  const [svgHtml, setSvgHtml] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [showRaw, setShowRaw] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    setError(null);

    const renderChart = async () => {
      try {
        const mermaid = (await import("mermaid")).default;
        mermaid.initialize({
          startOnLoad: false,
          theme: "dark",
          securityLevel: "loose",
          darkMode: true,
          themeVariables: {
            darkMode: true,
            background: "#0b0f17",
            primaryColor: "#4f46e5",
            primaryTextColor: "#f8fafc",
            primaryBorderColor: "#6366f1",
            lineColor: "#94a3b8",
            secondaryColor: "#1e293b",
            tertiaryColor: "#0f172a",
            mainBkg: "#0f172a",
            nodeBorder: "#334155",
            clusterBkg: "#1e293b",
            titleColor: "#f8fafc",
            edgeLabelBackground: "#0b0f17",
          },
          fontFamily: "ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        });

        const elementId = `mermaid_${reactId}_${Math.random().toString(36).substring(2, 7)}`;
        const cleanChart = chart.trim();

        const { svg } = await mermaid.render(elementId, cleanChart);
        if (isMounted) {
          setSvgHtml(svg);
          setIsLoading(false);
        }
      } catch (err: unknown) {
        if (isMounted) {
          const message = err instanceof Error ? err.message : "Erro de sintaxe no diagrama";
          setError(message);
          setIsLoading(false);

          // Limpa possíveis elementos temporários criados pelo Mermaid em caso de falha
          const tempElements = document.querySelectorAll(`[id^="dmermaid_"]`);
          tempElements.forEach((el) => el.remove());
        }
      }
    };

    if (chart) {
      renderChart();
    }

    return () => {
      isMounted = false;
    };
  }, [chart, reactId]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(chart);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback silencioso
    }
  };

  return (
    <figure
      role="figure"
      aria-label={caption || "Diagrama estrutural"}
      className={`my-5 overflow-hidden rounded-xl border border-slate-800 bg-slate-900/60 shadow-sm backdrop-blur-sm transition-all duration-150 ${className}`}
    >
      {/* Header com Metadados e Controles */}
      <div className="flex items-center justify-between border-b border-slate-800/80 px-4 py-2.5 bg-slate-950/40">
        <div className="flex items-center gap-2">
          <span className="flex h-2 w-2 rounded-full bg-indigo-500 animate-pulse" />
          <span className="text-xs font-semibold tracking-wide text-slate-300">
            {caption || "Diagrama Arquitetural / Grafo"}
          </span>
        </div>

        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={() => setShowRaw(!showRaw)}
            aria-label={showRaw ? "Ocultar código fonte" : "Ver código fonte"}
            className="flex items-center gap-1 rounded-lg px-2 py-1 text-[11px] font-medium text-slate-400 hover:bg-slate-800 hover:text-slate-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 transition-colors"
          >
            <Code2 className="h-3.5 w-3.5" />
            <span>{showRaw ? "Diagrama" : "Fonte"}</span>
          </button>

          <button
            type="button"
            onClick={handleCopy}
            aria-label="Copiar código do diagrama"
            className="flex items-center gap-1 rounded-lg px-2 py-1 text-[11px] font-medium text-slate-400 hover:bg-slate-800 hover:text-slate-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 transition-colors"
          >
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5 text-emerald-400" />
                <span className="text-emerald-400">Copiado</span>
              </>
            ) : (
              <>
                <Copy className="h-3.5 w-3.5" />
                <span>Copiar</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Exibição Alternada: Código Fonte */}
      {showRaw ? (
        <div className="p-4 bg-slate-950/80">
          <pre className="overflow-x-auto text-xs font-mono text-slate-300 leading-relaxed selection:bg-indigo-500/30">
            <code>{chart}</code>
          </pre>
        </div>
      ) : (
        /* Área de Renderização Visual */
        <div className="relative min-h-[160px] p-4 flex items-center justify-center overflow-x-auto">
          {isLoading && (
            <div className="flex flex-col items-center justify-center gap-2 py-8 text-slate-400">
              <RefreshCw className="h-5 w-5 animate-spin text-indigo-400" />
              <span className="text-xs">Compilando diagrama vetorial...</span>
            </div>
          )}

          {!isLoading && error && (
            <div className="flex flex-col items-center justify-center gap-2 py-6 px-4 text-center max-w-md">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-amber-500/10 text-amber-400">
                <AlertTriangle className="h-5 w-5" />
              </div>
              <p className="text-xs font-semibold text-slate-200">
                Sintaxe do diagrama não reconhecida pela engine
              </p>
              <p className="text-[11px] text-slate-400 line-clamp-2">
                {error}
              </p>
              <button
                type="button"
                onClick={() => setShowRaw(true)}
                className="mt-1 text-xs text-indigo-400 hover:text-indigo-300 underline font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
              >
                Visualizar código bruto
              </button>
            </div>
          )}

          {!isLoading && !error && svgHtml && (
            <div
              className="w-full overflow-x-auto py-2 flex items-center justify-center [&>svg]:max-w-full [&>svg]:h-auto [&>svg]:drop-shadow-sm"
              dangerouslySetInnerHTML={{ __html: svgHtml }}
            />
          )}
        </div>
      )}
    </figure>
  );
};
