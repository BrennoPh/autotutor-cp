"use client";

import React, { useState, useEffect, useRef, useMemo } from "react";
import {
  Play,
  Pause,
  SkipForward,
  SkipBack,
  RotateCcw,
  Table2,
  Code2,
  BrainCircuit,
  Terminal,
  Send,
  Lightbulb,
  Coins,
  Backpack,
  Binary,
  Footprints,
} from "lucide-react";

export type DpProblemType = "knapsack" | "coin_change" | "lcs" | "fibonacci";

interface DpStep {
  i: number;
  w: number;
  val: number;
  line: number;
  decision: string;
  fromCells: Array<{ i: number; w: number }>;
}

interface DpProblemConfig {
  id: DpProblemType;
  title: string;
  subtitle: string;
  bellmanEquation: string;
  bellmanExplanation: string;
  rowLabels: string[];
  colLabels: string[];
  cppCode: string[];
  generateTape: () => DpStep[];
  rowCount: number;
  colCount: number;
}

// 1. Mochila 0/1
const KNAPSACK_ITEMS = [
  { name: "Item 1", weight: 2, value: 3 },
  { name: "Item 2", weight: 3, value: 4 },
  { name: "Item 3", weight: 4, value: 5 },
  { name: "Item 4", weight: 5, value: 8 },
];
const KNAPSACK_CAPACITY = 7;

function generateKnapsackTape(): DpStep[] {
  const steps: DpStep[] = [];
  const dp: number[][] = Array.from({ length: KNAPSACK_ITEMS.length + 1 }, () =>
    Array(KNAPSACK_CAPACITY + 1).fill(0)
  );

  for (let i = 1; i <= KNAPSACK_ITEMS.length; i++) {
    const item = KNAPSACK_ITEMS[i - 1];
    for (let w = 0; w <= KNAPSACK_CAPACITY; w++) {
      const notPick = dp[i - 1][w];
      let pick = -1;
      const from: Array<{ i: number; w: number }> = [{ i: i - 1, w }];

      if (w >= item.weight) {
        pick = dp[i - 1][w - item.weight] + item.value;
        from.push({ i: i - 1, w: w - item.weight });
      }

      const best = Math.max(notPick, pick);
      dp[i][w] = best;

      const decision =
        pick > notPick
          ? `Pegar ${item.name} (+${item.value}) superou não pegar. dp[${i}][${w}] = ${best}`
          : `Melhor NÃO pegar ${item.name}. Mantém dp[${i - 1}][${w}] = ${best}`;

      steps.push({
        i,
        w,
        val: best,
        line: pick > notPick ? 7 : 5,
        decision,
        fromCells: from,
      });
    }
  }
  return steps;
}

// 2. Troco de Moedas (Coin Change)
const COINS = [1, 3, 4];
const COIN_TARGET = 6;

function generateCoinChangeTape(): DpStep[] {
  const steps: DpStep[] = [];
  const dp: number[][] = Array.from({ length: COINS.length + 1 }, () =>
    Array(COIN_TARGET + 1).fill(99)
  );

  for (let i = 0; i <= COINS.length; i++) {
    dp[i][0] = 0;
  }

  for (let i = 1; i <= COINS.length; i++) {
    const coin = COINS[i - 1];
    for (let v = 0; v <= COIN_TARGET; v++) {
      if (v === 0) {
        steps.push({
          i,
          w: 0,
          val: 0,
          line: 4,
          decision: `Valor zero requer 0 moedas. dp[${i}][0] = 0`,
          fromCells: [],
        });
        continue;
      }

      const notUse = dp[i - 1][v];
      let use = 99;
      const from: Array<{ i: number; w: number }> = [{ i: i - 1, w: v }];

      if (v >= coin && dp[i][v - coin] !== 99) {
        use = dp[i][v - coin] + 1;
        from.push({ i, w: v - coin });
      }

      const best = Math.min(notUse, use);
      dp[i][v] = best;

      const decision =
        use < notUse
          ? `Usar moeda ${coin} resulta em ${best} moedas (otimização encontrada!).`
          : `Não usar moeda ${coin}. Mantém melhor anterior: ${best === 99 ? "∞" : best} moedas.`;

      steps.push({
        i,
        w: v,
        val: best,
        line: use < notUse ? 7 : 5,
        decision,
        fromCells: from,
      });
    }
  }
  return steps;
}

// 3. Maior Subsequência Comum (LCS)
const S1 = "ABCB";
const S2 = "BDCB";

function generateLcsTape(): DpStep[] {
  const steps: DpStep[] = [];
  const dp: number[][] = Array.from({ length: S1.length + 1 }, () =>
    Array(S2.length + 1).fill(0)
  );

  for (let i = 1; i <= S1.length; i++) {
    for (let j = 1; j <= S2.length; j++) {
      const match = S1[i - 1] === S2[j - 1];
      let best = 0;
      let from: Array<{ i: number; w: number }> = [];

      if (match) {
        best = dp[i - 1][j - 1] + 1;
        from = [{ i: i - 1, w: j - 1 }];
      } else {
        best = Math.max(dp[i - 1][j], dp[i][j - 1]);
        from = [{ i: i - 1, w: j }, { i, w: j - 1 }];
      }
      dp[i][j] = best;

      const decision = match
        ? `Caracteres iguais ('${S1[i - 1]}'): estende LCS da diagonal + 1 = ${best}.`
        : `Caracteres distintos ('${S1[i - 1]}' != '${S2[j - 1]}'): pega max(cima, esquerda) = ${best}.`;

      steps.push({
        i,
        w: j,
        val: best,
        line: match ? 6 : 8,
        decision,
        fromCells: from,
      });
    }
  }
  return steps;
}

// 4. Fibonacci / Subida de Degraus
const FIB_N = 6;

function generateFibTape(): DpStep[] {
  const steps: DpStep[] = [];
  const dp = [1, 1, 0, 0, 0, 0, 0];

  steps.push({
    i: 0,
    w: 0,
    val: 1,
    line: 2,
    decision: "Caso base: dp[0] = 1 (1 forma de ficar no chão)",
    fromCells: [],
  });
  steps.push({
    i: 0,
    w: 1,
    val: 1,
    line: 3,
    decision: "Caso base: dp[1] = 1 (1 forma de subir 1 degrau)",
    fromCells: [],
  });

  for (let i = 2; i <= FIB_N; i++) {
    dp[i] = dp[i - 1] + dp[i - 2];
    steps.push({
      i: 0,
      w: i,
      val: dp[i],
      line: 6,
      decision: `Degrau ${i}: soma dp[${i - 1}] (${dp[i - 1]}) + dp[${i - 2}] (${dp[i - 2]}) = ${dp[i]} formas.`,
      fromCells: [{ i: 0, w: i - 1 }, { i: 0, w: i - 2 }],
    });
  }
  return steps;
}

const DP_CONFIGS: Record<DpProblemType, DpProblemConfig> = {
  knapsack: {
    id: "knapsack",
    title: "Mochila 0/1 (0-1 Knapsack)",
    subtitle: `Capacidade máxima W = ${KNAPSACK_CAPACITY} · 4 itens disponíveis`,
    bellmanEquation: "dp[i][w] = max(dp[i-1][w], dp[i-1][w - peso[i]] + valor[i])",
    bellmanExplanation:
      "Cada célula representa o valor ótimo considerando apenas os primeiros i itens com capacidade w.",
    rowLabels: ["0 (Base)", ...KNAPSACK_ITEMS.map((item) => `${item.name} (p=${item.weight}, v=${item.value})`)],
    colLabels: Array.from({ length: KNAPSACK_CAPACITY + 1 }, (_, w) => `w=${w}`),
    cppCode: [
      "// Programação Dinâmica C++: Mochila 0/1",
      "vector<vector<int>> dp(n + 1, vector<int>(W + 1, 0));",
      "for (int i = 1; i <= n; i++) {",
      "    for (int w = 0; w <= W; w++) {",
      "        dp[i][w] = dp[i - 1][w]; // Não pegar o item i",
      "        if (w >= weights[i - 1]) {",
      "            dp[i][w] = max(dp[i][w], dp[i - 1][w - weights[i - 1]] + values[i - 1]);",
      "        }",
      "    }",
      "}",
      "cout << \"Valor máximo: \" << dp[n][W] << endl;",
    ],
    generateTape: generateKnapsackTape,
    rowCount: KNAPSACK_ITEMS.length + 1,
    colCount: KNAPSACK_CAPACITY + 1,
  },
  coin_change: {
    id: "coin_change",
    title: "Troco de Moedas (Coin Change)",
    subtitle: `Moedas disponíveis: [${COINS.join(", ")}] · Alvo = ${COIN_TARGET}`,
    bellmanEquation: "dp[i][v] = min(dp[i-1][v], dp[i][v - moeda[i]] + 1)",
    bellmanExplanation:
      "Calcula o menor número de moedas para atingir cada valor v. ∞ indica valor inalcançável.",
    rowLabels: ["0 (Sem moedas)", ...COINS.map((c) => `Moeda de ${c}`)],
    colLabels: Array.from({ length: COIN_TARGET + 1 }, (_, v) => `v=${v}`),
    cppCode: [
      "// Programação Dinâmica C++: Menor Número de Moedas",
      "vector<vector<int>> dp(n + 1, vector<int>(V + 1, 1e9));",
      "for (int i = 0; i <= n; i++) dp[i][0] = 0;",
      "for (int i = 1; i <= n; i++) {",
      "    for (int v = 0; v <= V; v++) {",
      "        dp[i][v] = dp[i - 1][v]; // Não usar moeda atual",
      "        if (v >= coins[i - 1] && dp[i][v - coins[i - 1]] != 1e9) {",
      "            dp[i][v] = min(dp[i][v], dp[i][v - coins[i - 1]] + 1);",
      "        }",
      "    }",
      "}",
      "cout << \"Menor número de moedas: \" << dp[n][V] << endl;",
    ],
    generateTape: generateCoinChangeTape,
    rowCount: COINS.length + 1,
    colCount: COIN_TARGET + 1,
  },
  lcs: {
    id: "lcs",
    title: "Maior Subsequência Comum (LCS)",
    subtitle: `Comparando cadeias S1="${S1}" e S2="${S2}"`,
    bellmanEquation: "dp[i][j] = (S1[i] == S2[j]) ? dp[i-1][j-1] + 1 : max(dp[i-1][j], dp[i][j-1])",
    bellmanExplanation:
      "Se os caracteres coincidem, estende a diagonal. Se forem diferentes, herda o melhor entre cima e esquerda.",
    rowLabels: ["Ø", ...S1.split("").map((c, idx) => `S1[${idx}]='${c}'`)],
    colLabels: ["Ø", ...S2.split("").map((c, idx) => `S2[${idx}]='${c}'`)],
    cppCode: [
      "// Programação Dinâmica C++: Maior Subsequência Comum (LCS)",
      "vector<vector<int>> dp(m + 1, vector<int>(n + 1, 0));",
      "for (int i = 1; i <= m; i++) {",
      "    for (int j = 1; j <= n; j++) {",
      "        if (s1[i - 1] == s2[j - 1]) {",
      "            dp[i][j] = dp[i - 1][j - 1] + 1;",
      "        } else {",
      "            dp[i][j] = max(dp[i - 1][j], dp[i][j - 1]);",
      "        }",
      "    }",
      "}",
      "cout << \"Comprimento LCS: \" << dp[m][n] << endl;",
    ],
    generateTape: generateLcsTape,
    rowCount: S1.length + 1,
    colCount: S2.length + 1,
  },
  fibonacci: {
    id: "fibonacci",
    title: "Subida de Degraus / Fibonacci",
    subtitle: `Formas de subir até o degrau N = ${FIB_N} dando passos de 1 ou 2 degraus`,
    bellmanEquation: "dp[i] = dp[i - 1] + dp[i - 2]",
    bellmanExplanation:
      "Para alcançar o degrau i, você só pode ter vindo do degrau i-1 (passo de 1) ou do degrau i-2 (passo de 2).",
    rowLabels: ["dp[i]"],
    colLabels: Array.from({ length: FIB_N + 1 }, (_, i) => `i=${i}`),
    cppCode: [
      "// Programação Dinâmica C++: Subida de Degraus (O(N) tempo, O(N) espaço)",
      "vector<int> dp(n + 1, 0);",
      "dp[0] = 1; // 1 forma de ficar no chão",
      "dp[1] = 1; // 1 forma de subir 1 degrau",
      "for (int i = 2; i <= n; i++) {",
      "    dp[i] = dp[i - 1] + dp[i - 2];",
      "}",
      "cout << \"Total de caminhos: \" << dp[n] << endl;",
    ],
    generateTape: generateFibTape,
    rowCount: 1,
    colCount: FIB_N + 1,
  },
};

export function DpStudioWorkspace() {
  const [problemType, setProblemType] = useState<DpProblemType>("knapsack");
  const config = DP_CONFIGS[problemType];

  const [userCode, setUserCode] = useState<string>(() => config.cppCode.join("\n"));
  const [rightPanelTab, setRightPanelTab] = useState<"editor" | "tracer">("editor");

  const [promptInput, setPromptInput] = useState("");
  const [tape, setTape] = useState<DpStep[]>(() => config.generateTape());
  const [stepIdx, setStepIdx] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [speedMs, setSpeedMs] = useState(500);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Switch DP problem
  const handleSwitchProblem = (type: DpProblemType) => {
    setProblemType(type);
    const newConf = DP_CONFIGS[type];
    setUserCode(newConf.cppCode.join("\n"));
    const newTape = newConf.generateTape();
    setTape(newTape);
    setStepIdx(0);
    setIsPlaying(false);
  };

  // Re-generate tape if problem changes
  useEffect(() => {
    const newTape = config.generateTape();
    setTape(newTape);
    setStepIdx(0);
    setIsPlaying(false);
  }, [problemType, config]);

  const currentStep = tape[stepIdx];

  // Grid state up to current step
  const gridState = useMemo(() => {
    const table: number[][] = Array.from({ length: config.rowCount }, () =>
      Array(config.colCount).fill(0)
    );
    for (let s = 0; s <= stepIdx && s < tape.length; s++) {
      const step = tape[s];
      if (step.i < config.rowCount && step.w < config.colCount) {
        table[step.i][step.w] = step.val;
      }
    }
    return table;
  }, [tape, stepIdx, config.rowCount, config.colCount]);

  // Playback timer
  useEffect(() => {
    if (isPlaying) {
      timerRef.current = setInterval(() => {
        setStepIdx((prev) => {
          if (prev >= tape.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, speedMs);
    } else if (timerRef.current) {
      clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPlaying, tape.length, speedMs]);

  // Handle Quick Prompt submit
  const handlePromptSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const p = promptInput.toLowerCase();
    if (p.includes("troco") || p.includes("moeda") || p.includes("coin")) {
      handleSwitchProblem("coin_change");
    } else if (p.includes("lcs") || p.includes("subsequência") || p.includes("subsequencia") || p.includes("comum")) {
      handleSwitchProblem("lcs");
    } else if (p.includes("degrau") || p.includes("fibonacci") || p.includes("escada")) {
      handleSwitchProblem("fibonacci");
    } else {
      handleSwitchProblem("knapsack");
    }
    setPromptInput("");
  };

  return (
    <div className="flex flex-col space-y-4 h-full select-none">
      {/* Quick Prompt Bar for DP */}
      <form
        onSubmit={handlePromptSubmit}
        className="p-3 bg-slate-900 border border-slate-800 rounded-2xl shadow-sm flex items-center gap-2"
      >
        <div className="relative flex-1">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
            <Terminal className="w-4 h-4" />
          </div>
          <input
            type="text"
            value={promptInput}
            onChange={(e) => setPromptInput(e.target.value)}
            placeholder="Peça uma DP (ex: 'Troco de moedas', 'Maior subsequência LCS', 'Mochila 0/1', 'Degraus Fibonacci')..."
            className="w-full pl-9 pr-3 py-2 bg-slate-950/70 border border-slate-800 rounded-xl text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-slate-700"
          />
        </div>
        <button
          type="submit"
          className="flex items-center gap-1.5 px-3.5 py-2 bg-primary text-primary-foreground rounded-xl text-xs font-semibold hover:opacity-90 shadow-sm transition-all shrink-0"
        >
          <Send className="w-3 h-3" />
          <span>Carregar DP</span>
        </button>
      </form>

      {/* Top Toolbar: Presets & Playback */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 bg-card border border-border rounded-2xl shadow-sm">
        {/* DP Presets Switcher */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="flex items-center gap-1 text-xs text-muted-foreground font-semibold pr-1">
            <Lightbulb className="w-3.5 h-3.5 text-amber-400" />
            Problemas Clássicos:
          </span>
          <button
            type="button"
            onClick={() => handleSwitchProblem("knapsack")}
            className={`flex items-center gap-1 px-2.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              problemType === "knapsack"
                ? "bg-primary text-primary-foreground shadow-xs"
                : "bg-secondary/70 text-muted-foreground hover:text-foreground"
            }`}
          >
            <Backpack className="w-3.5 h-3.5" />
            <span>Mochila 0/1</span>
          </button>
          <button
            type="button"
            onClick={() => handleSwitchProblem("coin_change")}
            className={`flex items-center gap-1 px-2.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              problemType === "coin_change"
                ? "bg-primary text-primary-foreground shadow-xs"
                : "bg-secondary/70 text-muted-foreground hover:text-foreground"
            }`}
          >
            <Coins className="w-3.5 h-3.5 text-amber-400" />
            <span>Troco de Moedas</span>
          </button>
          <button
            type="button"
            onClick={() => handleSwitchProblem("lcs")}
            className={`flex items-center gap-1 px-2.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              problemType === "lcs"
                ? "bg-primary text-primary-foreground shadow-xs"
                : "bg-secondary/70 text-muted-foreground hover:text-foreground"
            }`}
          >
            <Binary className="w-3.5 h-3.5 text-cyan-400" />
            <span>Subsequência (LCS)</span>
          </button>
          <button
            type="button"
            onClick={() => handleSwitchProblem("fibonacci")}
            className={`flex items-center gap-1 px-2.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              problemType === "fibonacci"
                ? "bg-primary text-primary-foreground shadow-xs"
                : "bg-secondary/70 text-muted-foreground hover:text-foreground"
            }`}
          >
            <Footprints className="w-3.5 h-3.5 text-emerald-400" />
            <span>Degraus / Fibonacci</span>
          </button>
        </div>

        {/* Playback Controls */}
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => {
              setIsPlaying(false);
              setStepIdx(0);
            }}
            className="p-2 rounded-xl border border-border hover:bg-secondary text-muted-foreground hover:text-foreground transition-colors"
            title="Reiniciar Simulação"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
          <button
            type="button"
            onClick={() => {
              setIsPlaying(false);
              setStepIdx((p) => Math.max(0, p - 1));
            }}
            disabled={stepIdx === 0}
            className="p-2 rounded-xl border border-border hover:bg-secondary disabled:opacity-40 transition-colors"
            title="Passo Anterior"
          >
            <SkipBack className="w-4 h-4" />
          </button>
          <button
            type="button"
            onClick={() => setIsPlaying((p) => !p)}
            className="flex items-center gap-1.5 px-4 py-2 bg-primary text-primary-foreground rounded-xl text-xs font-bold shadow-sm hover:opacity-90 transition-opacity"
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            <span>{isPlaying ? "Pausar" : "Executar DP"}</span>
          </button>
          <button
            type="button"
            onClick={() => {
              setIsPlaying(false);
              setStepIdx((p) => Math.min(tape.length - 1, p + 1));
            }}
            disabled={stepIdx >= tape.length - 1}
            className="p-2 rounded-xl border border-border hover:bg-secondary disabled:opacity-40 transition-colors"
            title="Próximo Passo"
          >
            <SkipForward className="w-4 h-4" />
          </button>
          <span className="text-xs text-muted-foreground font-mono ml-2">
            Passo {stepIdx + 1} / {tape.length}
          </span>
        </div>
      </div>

      {/* Main Grid: DP Table (Left) + Code Editor / Tracer (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 flex-1">
        {/* Left: DP Matrix Table (7 cols) */}
        <div className="lg:col-span-7 bg-[#0f172a] border border-border rounded-2xl p-4 flex flex-col justify-between shadow-inner overflow-x-auto">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Table2 className="w-4 h-4 text-primary" />
                <span className="text-xs font-bold text-slate-200">
                  {config.title}
                </span>
                <span className="text-[10px] text-muted-foreground">
                  ({config.subtitle})
                </span>
              </div>
              <div className="flex items-center gap-3 text-[11px]">
                <span className="flex items-center gap-1 text-amber-400">
                  <span className="w-2.5 h-2.5 rounded-sm bg-amber-500/80"></span> Ativo
                </span>
                <span className="flex items-center gap-1 text-cyan-400">
                  <span className="w-2.5 h-2.5 rounded-sm bg-cyan-500/80"></span> Origem
                </span>
              </div>
            </div>

            <table className="w-full text-center text-xs mt-4 border-collapse font-mono">
              <thead>
                <tr className="text-slate-400 border-b border-slate-800">
                  <th className="p-2 text-left text-slate-400 font-semibold">Estado</th>
                  {config.colLabels.map((col, cIdx) => (
                    <th key={cIdx} className="p-2 font-semibold text-slate-300">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {gridState.map((row, i) => (
                  <tr key={i} className="border-b border-slate-800/60">
                    <td className="p-2 text-left font-semibold text-slate-300 whitespace-nowrap">
                      {config.rowLabels[i] || `i=${i}`}
                    </td>
                    {row.map((val, w) => {
                      const isCurrent = currentStep?.i === i && currentStep?.w === w;
                      const isFrom = currentStep?.fromCells?.some((c) => c.i === i && c.w === w);
                      return (
                        <td
                          key={w}
                          className={`p-2 transition-all duration-200 font-bold ${
                            isCurrent
                              ? "bg-amber-500/30 text-amber-300 border-2 border-amber-400 scale-105 shadow-md rounded"
                              : isFrom
                              ? "bg-cyan-500/20 text-cyan-300 border border-cyan-400/80 rounded"
                              : val > 0 && val !== 99
                              ? "text-emerald-400"
                              : "text-slate-600"
                          }`}
                        >
                          {val === 99 ? "∞" : val}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Decision explanation banner */}
          <div className="p-3 mt-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-2 text-xs">
            <BrainCircuit className="w-4 h-4 text-primary shrink-0" />
            <span className="text-slate-200">{currentStep?.decision || "Inicie a simulação"}</span>
          </div>
        </div>

        {/* Right: Editable C++ Code Editor & Tracer (5 cols) */}
        <div className="lg:col-span-5 flex flex-col gap-4">
          {/* Top: Tab switcher between Editor and Line Tracer */}
          <div className="bg-card border border-border rounded-2xl overflow-hidden flex flex-col shadow-sm">
            <div className="p-2 border-b border-border bg-secondary/40 flex items-center justify-between">
              <div className="flex items-center gap-1">
                <button
                  type="button"
                  onClick={() => setRightPanelTab("editor")}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                    rightPanelTab === "editor"
                      ? "bg-primary text-primary-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <Code2 className="w-3.5 h-3.5" />
                  <span>Editor C++</span>
                </button>
                <button
                  type="button"
                  onClick={() => setRightPanelTab("tracer")}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                    rightPanelTab === "tracer"
                      ? "bg-primary text-primary-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <Terminal className="w-3.5 h-3.5" />
                  <span>Rastreador de Linhas</span>
                </button>
              </div>

              <button
                type="button"
                onClick={() => setUserCode(config.cppCode.join("\n"))}
                className="text-[11px] text-muted-foreground hover:text-foreground underline transition-colors px-2"
                title="Restaurar código canônico da DP"
              >
                Restaurar
              </button>
            </div>

            {rightPanelTab === "editor" ? (
              <div className="p-3 space-y-2">
                <textarea
                  value={userCode}
                  onChange={(e) => setUserCode(e.target.value)}
                  rows={9}
                  spellCheck={false}
                  className="w-full p-3 rounded-xl bg-background text-foreground font-mono text-xs focus:outline-none border border-border resize-none leading-relaxed"
                  placeholder="Escreva ou edite seu algoritmo de Programação Dinâmica em C++17..."
                />
                <div className="flex items-center justify-between text-[11px] text-muted-foreground px-1">
                  <span>Edição ao vivo de DP C++17</span>
                  <span>Modo: {config.title.split(" ")[0]}</span>
                </div>
              </div>
            ) : (
              <pre className="font-mono text-[11px] leading-relaxed overflow-x-auto p-3 bg-secondary/50 max-h-64">
                {userCode.split("\n").map((line, idx) => (
                  <div
                    key={idx}
                    className={`px-2 py-0.5 rounded transition-colors ${
                      currentStep?.line === idx + 1
                        ? "bg-primary text-primary-foreground font-bold shadow-xs"
                        : "text-muted-foreground"
                    }`}
                  >
                    <span className="inline-block w-5 opacity-40 select-none">{idx + 1}</span>
                    {line}
                  </div>
                ))}
              </pre>
            )}
          </div>

          {/* Recurrence Equation / Bellman Panel */}
          <div className="flex-1 bg-card border border-border rounded-2xl p-4 shadow-sm space-y-3">
            <div className="flex items-center gap-2 pb-2 border-b border-border">
              <BrainCircuit className="w-4 h-4 text-blue-400" />
              <span className="text-xs font-bold text-foreground">Equação de Bellman / Recorrência</span>
            </div>
            <div className="p-3 bg-secondary/40 rounded-xl border border-border text-xs space-y-2">
              <p className="font-mono text-[11px] text-primary font-bold">
                {config.bellmanEquation}
              </p>
              <p className="text-muted-foreground text-[11px] leading-relaxed">
                {config.bellmanExplanation}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
