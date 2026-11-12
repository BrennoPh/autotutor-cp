"use client";

import React, { useState } from "react";
import {
  DataStructureTab,
  StackElement,
  QueueElement,
  VectorElement,
} from "@/types/whiteboard";
import {
  Layers,
  ArrowDownToLine,
  ArrowUpFromLine,
  Trash2,
  Plus,
  Minus,
  Sparkles,
  ArrowRight,
  ListOrdered,
} from "lucide-react";

export function DataStructuresPanel() {
  const [activeTab, setActiveTab] = useState<DataStructureTab>("stack");

  // Stack State
  const [stack, setStack] = useState<StackElement[]>([
    { id: "s1", value: "10" },
    { id: "s2", value: "25" },
    { id: "s3", value: "42" },
  ]);
  const [stackInput, setStackInput] = useState("");
  const [lastPopped, setLastPopped] = useState<string | null>(null);

  // Queue State
  const [queue, setQueue] = useState<QueueElement[]>([
    { id: "q1", value: "A" },
    { id: "q2", value: "B" },
    { id: "q3", value: "C" },
  ]);
  const [queueInput, setQueueInput] = useState("");
  const [lastDequeued, setLastDequeued] = useState<string | null>(null);

  // Vector / Array State
  const [vector, setVector] = useState<VectorElement[]>([
    { id: "v1", value: "7" },
    { id: "v2", value: "14" },
    { id: "v3", value: "21" },
    { id: "v4", value: "28" },
  ]);
  const [vectorInput, setVectorInput] = useState("");

  // Stack Handlers
  const handlePushStack = () => {
    const val = stackInput.trim() || Math.floor(Math.random() * 90 + 10).toString();
    setStack((prev) => [...prev, { id: `s_${Date.now()}`, value: val }]);
    setStackInput("");
    setLastPopped(null);
  };

  const handlePopStack = () => {
    if (stack.length === 0) return;
    const popped = stack[stack.length - 1];
    setLastPopped(popped.value);
    setStack((prev) => prev.slice(0, -1));
  };

  // Queue Handlers
  const handleEnqueue = () => {
    const val = queueInput.trim() || String.fromCharCode(65 + (queue.length % 26));
    setQueue((prev) => [...prev, { id: `q_${Date.now()}`, value: val }]);
    setQueueInput("");
    setLastDequeued(null);
  };

  const handleDequeue = () => {
    if (queue.length === 0) return;
    const dequeued = queue[0];
    setLastDequeued(dequeued.value);
    setQueue((prev) => prev.slice(1));
  };

  // Vector Handlers
  const handleAppendVector = () => {
    const val = vectorInput.trim() || Math.floor(Math.random() * 50 + 1).toString();
    setVector((prev) => [...prev, { id: `v_${Date.now()}`, value: val }]);
    setVectorInput("");
  };

  const handlePopVector = () => {
    if (vector.length === 0) return;
    setVector((prev) => prev.slice(0, -1));
  };

  return (
    <div className="bg-card/90 backdrop-blur-md border border-border rounded-2xl p-4 flex flex-col gap-4 text-xs select-none">
      {/* Header and Switcher */}
      <div className="flex items-center justify-between border-b border-border pb-3">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-primary" />
          <span className="font-bold text-foreground text-sm">Estruturas Interativas</span>
        </div>
        <div className="flex items-center gap-1 bg-secondary/80 p-0.5 rounded-lg border border-border">
          <button
            type="button"
            onClick={() => setActiveTab("stack")}
            className={`px-2.5 py-1 rounded-md font-semibold transition-all ${
              activeTab === "stack"
                ? "bg-primary text-primary-foreground shadow-xs"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Pilha (LIFO)
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("queue")}
            className={`px-2.5 py-1 rounded-md font-semibold transition-all ${
              activeTab === "queue"
                ? "bg-primary text-primary-foreground shadow-xs"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Fila (FIFO)
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("vector")}
            className={`px-2.5 py-1 rounded-md font-semibold transition-all ${
              activeTab === "vector"
                ? "bg-primary text-primary-foreground shadow-xs"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Vetor / Array
          </button>
        </div>
      </div>

      {/* Tab: Pilha (Stack LIFO) */}
      {activeTab === "stack" && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={stackInput}
              onChange={(e) => setStackInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handlePushStack()}
              placeholder="Valor (ex: 42)"
              className="bg-secondary text-foreground px-3 py-1.5 rounded-xl border border-border w-28 text-xs focus:outline-none focus:ring-1 focus:ring-primary"
            />
            <button
              type="button"
              onClick={handlePushStack}
              className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-primary text-primary-foreground font-semibold hover:opacity-90 transition-opacity"
            >
              <ArrowDownToLine className="w-3.5 h-3.5" />
              <span>Push</span>
            </button>
            <button
              type="button"
              onClick={handlePopStack}
              disabled={stack.length === 0}
              className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-destructive/10 text-destructive border border-destructive/20 font-semibold hover:bg-destructive/20 transition-all disabled:opacity-40"
            >
              <ArrowUpFromLine className="w-3.5 h-3.5" />
              <span>Pop</span>
            </button>
            <button
              type="button"
              onClick={() => {
                setStack([]);
                setLastPopped(null);
              }}
              title="Limpar pilha"
              className="p-1.5 rounded-xl text-muted-foreground hover:text-destructive hover:bg-secondary transition-colors ml-auto"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>

          {lastPopped && (
            <div className="text-[11px] text-amber-400 font-medium">
              Elemento desempilhado: <strong>{lastPopped}</strong>
            </div>
          )}

          {/* Visual Stack Representation */}
          <div className="min-h-[140px] max-h-[220px] overflow-y-auto p-3 rounded-xl bg-background/60 border border-border flex flex-col-reverse items-center gap-1.5">
            {stack.length === 0 ? (
              <div className="text-muted-foreground text-center py-8">
                Pilha vazia (Stack Underflow)
              </div>
            ) : (
              stack.map((item, idx) => {
                const isTop = idx === stack.length - 1;
                return (
                  <div
                    key={item.id}
                    className={`w-full max-w-[200px] py-1.5 px-3 rounded-lg border flex items-center justify-between text-xs font-mono font-bold transition-all ${
                      isTop
                        ? "bg-amber-500/20 border-amber-500/60 text-amber-300 ring-2 ring-amber-500/20"
                        : "bg-secondary/70 border-border text-foreground"
                    }`}
                  >
                    <span>{item.value}</span>
                    <span className="text-[10px] text-muted-foreground font-normal">
                      {isTop ? "← TOPO" : `[${idx}]`}
                    </span>
                  </div>
                );
              })
            )}
          </div>
          <div className="text-[10px] text-muted-foreground text-center">
            Ordem LIFO: O último elemento inserido no topo é o primeiro a ser retirado.
          </div>
        </div>
      )}

      {/* Tab: Fila (Queue FIFO) */}
      {activeTab === "queue" && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={queueInput}
              onChange={(e) => setQueueInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleEnqueue()}
              placeholder="Valor (ex: X)"
              className="bg-secondary text-foreground px-3 py-1.5 rounded-xl border border-border w-28 text-xs focus:outline-none focus:ring-1 focus:ring-primary"
            />
            <button
              type="button"
              onClick={handleEnqueue}
              className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-primary text-primary-foreground font-semibold hover:opacity-90 transition-opacity"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Enqueue</span>
            </button>
            <button
              type="button"
              onClick={handleDequeue}
              disabled={queue.length === 0}
              className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-destructive/10 text-destructive border border-destructive/20 font-semibold hover:bg-destructive/20 transition-all disabled:opacity-40"
            >
              <Minus className="w-3.5 h-3.5" />
              <span>Dequeue</span>
            </button>
            <button
              type="button"
              onClick={() => {
                setQueue([]);
                setLastDequeued(null);
              }}
              title="Limpar fila"
              className="p-1.5 rounded-xl text-muted-foreground hover:text-destructive hover:bg-secondary transition-colors ml-auto"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>

          {lastDequeued && (
            <div className="text-[11px] text-cyan-400 font-medium">
              Elemento desenfileirado: <strong>{lastDequeued}</strong>
            </div>
          )}

          {/* Visual Queue Representation */}
          <div className="min-h-[100px] overflow-x-auto p-4 rounded-xl bg-background/60 border border-border flex items-center gap-2">
            {queue.length === 0 ? (
              <div className="text-muted-foreground text-center w-full py-4">
                Fila vazia (Queue Underflow)
              </div>
            ) : (
              queue.map((item, idx) => {
                const isFront = idx === 0;
                const isBack = idx === queue.length - 1;
                return (
                  <React.Fragment key={item.id}>
                    <div
                      className={`min-w-[56px] py-2 px-3 rounded-xl border text-center font-mono font-bold text-xs shrink-0 flex flex-col items-center gap-0.5 ${
                        isFront
                          ? "bg-cyan-500/20 border-cyan-500/60 text-cyan-300 ring-2 ring-cyan-500/20"
                          : isBack
                          ? "bg-indigo-500/20 border-indigo-500/60 text-indigo-300"
                          : "bg-secondary/70 border-border text-foreground"
                      }`}
                    >
                      <span>{item.value}</span>
                      <span className="text-[9px] text-muted-foreground font-normal">
                        {isFront ? "FRENTE" : isBack ? "FIM" : `[${idx}]`}
                      </span>
                    </div>
                    {idx < queue.length - 1 && (
                      <ArrowRight className="w-3.5 h-3.5 text-muted-foreground shrink-0" />
                    )}
                  </React.Fragment>
                );
              })
            )}
          </div>
          <div className="text-[10px] text-muted-foreground text-center">
            Ordem FIFO: Entra pelo Fim (Back) e sai pela Frente (Front).
          </div>
        </div>
      )}

      {/* Tab: Vetor / Array */}
      {activeTab === "vector" && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={vectorInput}
              onChange={(e) => setVectorInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAppendVector()}
              placeholder="Valor"
              className="bg-secondary text-foreground px-3 py-1.5 rounded-xl border border-border w-28 text-xs focus:outline-none focus:ring-1 focus:ring-primary"
            />
            <button
              type="button"
              onClick={handleAppendVector}
              className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-primary text-primary-foreground font-semibold hover:opacity-90 transition-opacity"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Inserir</span>
            </button>
            <button
              type="button"
              onClick={handlePopVector}
              disabled={vector.length === 0}
              className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-secondary hover:bg-secondary/80 text-foreground border border-border font-semibold transition-all disabled:opacity-40"
            >
              <Minus className="w-3.5 h-3.5" />
              <span>Remover Fim</span>
            </button>
            <button
              type="button"
              onClick={() => setVector([])}
              title="Limpar vetor"
              className="p-1.5 rounded-xl text-muted-foreground hover:text-destructive hover:bg-secondary transition-colors ml-auto"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Visual Array Grid */}
          <div className="min-h-[100px] overflow-x-auto p-4 rounded-xl bg-background/60 border border-border flex items-center gap-1">
            {vector.length === 0 ? (
              <div className="text-muted-foreground text-center w-full py-4">
                Vetor vazio (tamanho 0)
              </div>
            ) : (
              vector.map((item, idx) => (
                <div key={item.id} className="flex flex-col items-center gap-1 shrink-0">
                  <div className="w-12 h-12 rounded-lg border border-border bg-secondary/80 flex items-center justify-center font-mono font-bold text-sm text-foreground shadow-xs">
                    {item.value}
                  </div>
                  <span className="text-[10px] text-muted-foreground font-mono">
                    [{idx}]
                  </span>
                </div>
              ))
            )}
          </div>
          <div className="text-[10px] text-muted-foreground text-center">
            Acesso O(1) indexado por ponteiro de memória contígua `vector[i]`.
          </div>
        </div>
      )}
    </div>
  );
}
