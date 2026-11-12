"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import rehypeSanitize, { defaultSchema } from "rehype-sanitize";
import { MermaidDiagram } from "@/components/common/MermaidDiagram";
import { extractGraphFromMermaid } from "@/utils/graphExtractor";
import { Check, Copy, Code2, Network, ArrowUpRight } from "lucide-react";

// Safe schema that allows MathML and KaTeX tags along with standard Markdown tags
const mathSanitizeSchema = {
  ...defaultSchema,
  attributes: {
    ...defaultSchema.attributes,
    div: [
      ...(defaultSchema.attributes?.div || []),
      ["className", "math", "math-display"],
    ],
    span: [
      ...(defaultSchema.attributes?.span || []),
      ["className", "math", "math-inline", /^katex/],
    ],
    code: [
      ...(defaultSchema.attributes?.code || []),
      ["className", /^language-/],
    ],
  },
  tagNames: [
    ...(defaultSchema.tagNames || []),
    "math",
    "semantics",
    "mrow",
    "mi",
    "mo",
    "mn",
    "annotation",
    "mspace",
    "mtext",
    "msub",
    "msup",
    "msubsup",
    "mfrac",
    "msqrt",
    "mroot",
  ],
};

interface CodeSnippetProps {
  language: string;
  code: string;
}

function CodeSnippet({ language, code }: CodeSnippetProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formattedLang = language ? language.toUpperCase() : "CÓDIGO";

  return (
    <div className="my-3.5 rounded-xl border border-border bg-[#0B0F17]/95 overflow-hidden shadow-sm">
      <div className="flex items-center justify-between px-3.5 py-1.5 bg-secondary/50 border-b border-border/80 text-[11px] font-mono">
        <span className="flex items-center gap-1.5 text-primary font-bold">
          <Code2 className="w-3.5 h-3.5 text-primary" />
          <span>{formattedLang}</span>
        </span>
        <button
          type="button"
          onClick={handleCopy}
          className="flex items-center gap-1 px-2.5 py-0.5 rounded-lg bg-card/60 hover:bg-card text-muted-foreground hover:text-foreground border border-border transition-colors text-[10px]"
          title="Copiar código"
        >
          {copied ? (
            <>
              <Check className="w-3 h-3 text-emerald-400" />
              <span className="text-emerald-400 font-semibold">Copiado</span>
            </>
          ) : (
            <>
              <Copy className="w-3 h-3" />
              <span>Copiar</span>
            </>
          )}
        </button>
      </div>
      <pre className="p-4 text-xs font-mono leading-relaxed overflow-x-auto text-foreground/95 bg-card/10">
        <code>{code}</code>
      </pre>
    </div>
  );
}

export interface MarkdownRendererProps {
  content: string;
  className?: string;
  onOpenInWhiteboard?: (graphData: { mermaid: string; nodes: any[]; edges: any[] }) => void;
}

export function MarkdownRenderer({
  content,
  className = "",
  onOpenInWhiteboard,
}: MarkdownRendererProps) {
  const router = useRouter();

  let displayContent = content || "";
  if (typeof displayContent === "string" && displayContent.trim().startsWith("{") && displayContent.includes('"markdown"')) {
    try {
      const parsed = JSON.parse(displayContent);
      if (parsed && typeof parsed.markdown === "string") {
        displayContent = parsed.markdown;
      }
    } catch {
      // Mantém displayContent inalterado
    }
  }

  if (!displayContent) return null;

  const handleProjectGraph = (chart: string) => {
    const extracted = extractGraphFromMermaid(chart);
    if (onOpenInWhiteboard) {
      onOpenInWhiteboard({
        mermaid: chart,
        nodes: extracted?.nodes || [],
        edges: extracted?.edges || [],
      });
      return;
    }

    // Default fallback: persist to session storage and navigate to whiteboard
    try {
      if (extracted) {
        sessionStorage.setItem("autotutor_active_graph", JSON.stringify(extracted));
      }
      router.push("/whiteboard?source=study");
    } catch (e) {
      console.warn("Could not save graph to sessionStorage:", e);
      router.push("/whiteboard");
    }
  };

  return (
    <div
      className={`prose prose-invert max-w-none text-xs sm:text-sm leading-relaxed text-foreground/90 font-sans selection:bg-primary/20 ${className}`}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[[rehypeSanitize, mathSanitizeSchema], rehypeKatex]}
        components={{
          code({ node, inline, className: codeClassName, children, ...props }: any) {
            const match = /language-(\w+)/.exec(codeClassName || "");
            const lang = match ? match[1].toLowerCase() : "";
            const rawContent = String(children).replace(/\n$/, "");

            if (!inline && lang === "mermaid") {
              const isGraphOrTree =
                rawContent.includes("graph ") ||
                rawContent.includes("flowchart ") ||
                rawContent.includes("-->") ||
                rawContent.includes("->");

              return (
                <div className="space-y-2 my-4">
                  <MermaidDiagram chart={rawContent} />
                  {isGraphOrTree && (
                    <div className="flex justify-end">
                      <button
                        type="button"
                        onClick={() => handleProjectGraph(rawContent)}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-primary/10 hover:bg-primary/20 text-primary border border-primary/30 transition-all shadow-sm group"
                      >
                        <Network className="w-3.5 h-3.5 text-primary group-hover:scale-110 transition-transform" />
                        <span>🔬 Intercalar com Quadro Branco / Simular Grafo</span>
                        <ArrowUpRight className="w-3 h-3 opacity-70" />
                      </button>
                    </div>
                  )}
                </div>
              );
            }

            if (!inline && (lang || rawContent.includes("\n"))) {
              return <CodeSnippet language={lang} code={rawContent} />;
            }

            return (
              <code
                className="px-1.5 py-0.5 rounded-md bg-secondary/80 font-mono text-[11px] text-primary font-semibold border border-border/50"
                {...props}
              >
                {children}
              </code>
            );
          },
          h1({ children }: any) {
            return (
              <h1 className="text-xl sm:text-2xl font-extrabold tracking-tight text-foreground mt-6 mb-3 pb-2 border-b border-border/70 flex items-center gap-2">
                {children}
              </h1>
            );
          },
          h2({ children }: any) {
            return (
              <h2 className="text-lg sm:text-xl font-bold tracking-tight text-foreground mt-5 mb-2.5 flex items-center gap-2">
                <span className="w-1.5 h-4 rounded-full bg-primary shrink-0" />
                <span>{children}</span>
              </h2>
            );
          },
          h3({ children }: any) {
            return (
              <h3 className="text-sm sm:text-base font-bold text-foreground mt-4 mb-2">
                {children}
              </h3>
            );
          },
          h4({ children }: any) {
            return (
              <h4 className="text-xs sm:text-sm font-bold text-foreground/90 mt-3 mb-1">
                {children}
              </h4>
            );
          },
          p({ children }: any) {
            return <p className="mb-3 leading-relaxed text-foreground/90">{children}</p>;
          },
          blockquote({ children }: any) {
            return (
              <blockquote className="my-3 pl-4 py-2.5 border-l-4 border-primary bg-primary/5 rounded-r-xl text-xs sm:text-sm italic text-muted-foreground">
                {children}
              </blockquote>
            );
          },
          ul({ children }: any) {
            return (
              <ul className="my-2.5 space-y-1.5 list-disc list-inside text-foreground/90 pl-1">
                {children}
              </ul>
            );
          },
          ol({ children }: any) {
            return (
              <ol className="my-2.5 space-y-1.5 list-decimal list-inside text-foreground/90 pl-1">
                {children}
              </ol>
            );
          },
          li({ children }: any) {
            return <li className="leading-relaxed">{children}</li>;
          },
          table({ children }: any) {
            return (
              <div className="my-4 w-full overflow-x-auto rounded-xl border border-border shadow-sm">
                <table className="w-full text-xs text-left border-collapse">{children}</table>
              </div>
            );
          },
          thead({ children }: any) {
            return (
              <thead className="bg-secondary/70 text-foreground font-semibold border-b border-border">
                {children}
              </thead>
            );
          },
          th({ children }: any) {
            return (
              <th className="px-3.5 py-2.5 font-bold text-foreground border-r border-border/50 last:border-r-0">
                {children}
              </th>
            );
          },
          td({ children }: any) {
            return (
              <td className="px-3.5 py-2 text-muted-foreground border-t border-border/50 border-r border-border/50 last:border-r-0">
                {children}
              </td>
            );
          },
          tr({ children }: any) {
            return <tr className="hover:bg-secondary/30 transition-colors">{children}</tr>;
          },
          a({ href, children }: any) {
            return (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:text-primary-hover underline font-medium inline-flex items-center gap-0.5"
              >
                {children}
              </a>
            );
          },
          hr() {
            return <hr className="my-6 border-border/60" />;
          },
        }}
      >
        {displayContent}
      </ReactMarkdown>
    </div>
  );
}

export default MarkdownRenderer;
