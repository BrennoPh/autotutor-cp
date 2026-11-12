"use client";

import React, { useState } from "react";
import { RotateCw, ChevronLeft, ChevronRight, CheckCircle2, Brain, ArrowRight } from "lucide-react";

export interface FlashcardItem {
  id: string;
  topic: string;
  question: string;
  codeSnippet?: string;
  answer: string;
  conceptDetail: string;
  tag: string;
}

const DEFAULT_DECK: FlashcardItem[] = [
  {
    id: "fc-1",
    topic: "Busca em Grafos (BFS)",
    question: "Por que marcar um vértice como visitado no momento do PUSH na fila da BFS e NUNCA no POP?",
    codeSnippet: "// Invariante correta:\nq.push(v);\nvisited[v] = true;",
    answer: "Evita que caminhos concorrentes alcancem o mesmo nó vizinho e o reinsiram múltiplas vezes na fila.",
    conceptDetail: "Se a marcação ocorrer apenas no POP, o mesmo vértice pode ser inserido dezenas de vezes, explodindo a memória (MLE) e o tempo de execução (TLE) para O(V²).",
    tag: "Invariante de Maratona",
  },
  {
    id: "fc-2",
    topic: "Busca em Profundidade (DFS)",
    question: "Qual tipo de aresta da árvore de recursão DFS prova categoricamente a existência de ciclos em grafos direcionados?",
    codeSnippet: "if (state[v] == VISITING) {\n    // Back Edge detectada!\n}",
    answer: "Arestas de Retorno (Back Edges) que apontam para um vértice ancestral atualmente ativo na call stack.",
    conceptDetail: "Um nó no estado 'cinza' (em processamento na pilha) que é reencontrado fecha um ciclo orientado no grafo.",
    tag: "Teorema Fundamental",
  },
  {
    id: "fc-3",
    topic: "Caminhos Mínimos (Dijkstra)",
    question: "Por que o Algoritmo de Dijkstra falha em grafos contendo arestas com pesos negativos?",
    codeSnippet: "if (d > dist[u]) continue;\n// Suposição gulosa violada com pesos < 0",
    answer: "A escolha gulosa assume que a menor distância da priority_queue é final e nunca poderá ser reduzida.",
    conceptDetail: "Uma aresta negativa posterior pode oferecer um caminho mais curto para um nó já marcado como ótimo, quebrando a prova de corretude. Nesses casos, usa-se Bellman-Ford ou SPFA.",
    tag: "Algoritmos Gulosos",
  },
  {
    id: "fc-4",
    topic: "Programação Dinâmica (DP)",
    question: "Qual a diferença de complexidade entre a busca ingênua e a Programação Dinâmica na Mochila 0/1?",
    codeSnippet: "// Ingênuo: O(2^N)\n// DP: O(N * W)",
    answer: "A busca ingênua explora todas as 2^N combinações, enquanto a DP memoriza os subproblemas em O(N * W).",
    conceptDetail: "A DP é pseudo-polinomial: o tempo depende linearmente da capacidade W da mochila e do número N de itens.",
    tag: "Complexidade Assintótica",
  },
  {
    id: "fc-5",
    topic: "Estruturas de Dados (DSU / Kruskal)",
    question: "Qual a complexidade de tempo quase-linear da DSU com Union by Rank e Path Compression?",
    codeSnippet: "int find(int i) {\n    if (parent[i] == i) return i;\n    return parent[i] = find(parent[i]); // Path compression\n}",
    answer: "O(α(N)) por operação, onde α(N) é a função inversa de Ackermann.",
    conceptDetail: "Para todos os valores de N até 10⁸⁰ (número de átomos no universo), α(N) ≤ 4, tornando as operações praticamente O(1) no juiz.",
    tag: "Estrutura Quase O(1)",
  },
];

interface FlashcardStudySessionProps {
  deck?: FlashcardItem[];
  onComplete?: () => void;
  onClose?: () => void;
}

export function FlashcardStudySession({
  deck = DEFAULT_DECK,
  onComplete,
  onClose,
}: FlashcardStudySessionProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [ratings, setRatings] = useState<Record<string, "hard" | "good" | "easy">>({});
  const [isFinished, setIsFinished] = useState(false);

  const currentCard = deck[currentIndex];
  const progressPercent = Math.round(((currentIndex + 1) / deck.length) * 100);

  const handleFlip = () => {
    setIsFlipped((prev) => !prev);
  };

  const handleNext = () => {
    setIsFlipped(false);
    if (currentIndex < deck.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    } else {
      setIsFinished(true);
    }
  };

  const handlePrev = () => {
    setIsFlipped(false);
    setCurrentIndex((prev) => Math.max(0, prev - 1));
  };

  const handleRate = (rating: "hard" | "good" | "easy") => {
    setRatings((prev) => ({ ...prev, [currentCard.id]: rating }));
    handleNext();
  };

  if (isFinished) {
    return (
      <div className="w-full max-w-lg bg-card border border-border rounded-2xl p-6 shadow-2xl text-center space-y-5 animate-fade-in">
        <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 text-emerald-400 mx-auto flex items-center justify-center border border-emerald-500/20">
          <CheckCircle2 className="w-6 h-6" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-foreground">Sessão Concluída com Sucesso!</h3>
          <p className="text-xs text-muted-foreground mt-1">
            Você revisou todos os {deck.length} flashcards deste ciclo de repetição intervalada.
          </p>
        </div>
        <div className="grid grid-cols-3 gap-2 p-3 bg-secondary/50 rounded-xl border border-border text-center text-xs">
          <div>
            <span className="text-[10px] text-muted-foreground block">Difíceis</span>
            <span className="font-bold text-rose-400">
              {Object.values(ratings).filter((r) => r === "hard").length}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-muted-foreground block">Bons</span>
            <span className="font-bold text-amber-400">
              {Object.values(ratings).filter((r) => r === "good").length}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-muted-foreground block">Fáceis</span>
            <span className="font-bold text-emerald-400">
              {Object.values(ratings).filter((r) => r === "easy").length}
            </span>
          </div>
        </div>
        <div className="flex justify-center gap-3">
          <button
            type="button"
            onClick={() => {
              setCurrentIndex(0);
              setIsFlipped(false);
              setIsFinished(false);
              setRatings({});
            }}
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-secondary hover:bg-accent text-foreground transition-colors"
          >
            Revisar Novamente
          </button>
          <button
            type="button"
            onClick={() => {
              onComplete?.();
              onClose?.();
            }}
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            Concluir & Voltar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-lg bg-card border border-border rounded-2xl p-6 shadow-2xl space-y-4 animate-fade-in select-none">
      {/* Header & Progress */}
      <div className="flex items-center justify-between border-b border-border pb-3">
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-primary" />
          <span className="text-xs font-bold text-foreground">{currentCard.topic}</span>
        </div>
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span>
            {currentIndex + 1} de {deck.length}
          </span>
          {onClose && (
            <button
              onClick={onClose}
              className="text-muted-foreground hover:text-foreground text-xs"
            >
              ✕ Fechar
            </button>
          )}
        </div>
      </div>

      <div className="w-full h-1 bg-secondary rounded-full overflow-hidden">
        <div
          className="h-full bg-primary transition-all duration-300"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {/* Interactive Card Body with Flip */}
      <div
        onClick={handleFlip}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === " " || e.key === "Enter") {
            e.preventDefault();
            handleFlip();
          }
        }}
        className={`w-full min-h-[220px] p-6 rounded-2xl border transition-all duration-300 cursor-pointer flex flex-col justify-between text-left ${
          isFlipped
            ? "bg-gradient-to-br from-indigo-950/40 via-card to-secondary/70 border-indigo-500/40 shadow-indigo-500/10 shadow-lg"
            : "bg-gradient-to-br from-slate-900 via-card to-secondary/50 border-border hover:border-primary/40 shadow-md"
        }`}
      >
        <div>
          <div className="flex items-center justify-between text-[11px] mb-3">
            <span className="px-2 py-0.5 rounded-full bg-primary/10 text-primary border border-primary/20 font-medium">
              {currentCard.tag}
            </span>
            <span className="text-muted-foreground flex items-center gap-1 font-semibold">
              <RotateCw className="w-3 h-3 text-primary animate-spin-slow" />
              {isFlipped ? "Verso (Resposta)" : "Frente (Pergunta) · Clique para virar"}
            </span>
          </div>

          {!isFlipped ? (
            <div className="space-y-3">
              <p className="text-sm font-bold text-foreground leading-relaxed">
                {currentCard.question}
              </p>
              {currentCard.codeSnippet && (
                <pre className="p-3 bg-black/40 rounded-xl font-mono text-[11px] text-sky-300 border border-slate-800">
                  {currentCard.codeSnippet}
                </pre>
              )}
            </div>
          ) : (
            <div className="space-y-3">
              <div className="p-3 bg-emerald-500/10 border border-emerald-500/25 rounded-xl">
                <p className="text-xs font-bold text-emerald-300 leading-relaxed">
                  ✓ {currentCard.answer}
                </p>
              </div>
              <p className="text-xs text-muted-foreground leading-relaxed">
                {currentCard.conceptDetail}
              </p>
            </div>
          )}
        </div>

        <div className="pt-4 border-t border-border/40 flex items-center justify-between text-[11px] text-muted-foreground">
          <span>Pressione Espaço para virar</span>
          <span className="text-primary font-semibold flex items-center gap-1">
            Girar Cartão <RotateCw className="w-3 h-3" />
          </span>
        </div>
      </div>

      {/* Action Controls & Navigation */}
      <div className="space-y-3 pt-1">
        {/* Flip Button & Spaced Repetition Ratings */}
        {isFlipped ? (
          <div className="space-y-2 animate-fade-in">
            <span className="text-[11px] text-muted-foreground block text-center">
              Como você avalia a retenção deste conceito?
            </span>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => handleRate("hard")}
                className="py-2 px-3 rounded-xl bg-rose-500/15 hover:bg-rose-500/25 text-rose-300 border border-rose-500/30 text-xs font-bold transition-all"
              >
                🔴 Difícil
              </button>
              <button
                type="button"
                onClick={() => handleRate("good")}
                className="py-2 px-3 rounded-xl bg-amber-500/15 hover:bg-amber-500/25 text-amber-300 border border-amber-500/30 text-xs font-bold transition-all"
              >
                🟡 Bom
              </button>
              <button
                type="button"
                onClick={() => handleRate("easy")}
                className="py-2 px-3 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/25 text-emerald-300 border border-emerald-500/30 text-xs font-bold transition-all"
              >
                🟢 Fácil
              </button>
            </div>
          </div>
        ) : (
          <button
            type="button"
            onClick={handleFlip}
            className="w-full py-2.5 rounded-xl bg-primary text-primary-foreground font-bold text-xs flex items-center justify-center gap-1.5 hover:bg-primary/90 shadow-sm transition-all"
          >
            <RotateCw className="w-3.5 h-3.5" />
            <span>Virar Cartão & Ver Resposta</span>
          </button>
        )}

        {/* Step Forward / Backward Footer */}
        <div className="flex items-center justify-between pt-1">
          <button
            type="button"
            onClick={handlePrev}
            disabled={currentIndex === 0}
            className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-secondary hover:bg-accent text-xs font-semibold disabled:opacity-40 transition-colors"
          >
            <ChevronLeft className="w-3.5 h-3.5" />
            <span>Anterior</span>
          </button>

          <button
            type="button"
            onClick={handleNext}
            className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-secondary hover:bg-accent text-xs font-semibold transition-colors"
          >
            <span>{currentIndex < deck.length - 1 ? "Próximo" : "Finalizar"}</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
