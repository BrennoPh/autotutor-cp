import {
  GraphNode,
  GraphEdge,
  ExecutionStep,
  NodeVisualState,
  EdgeVisualState,
  CallStackFrame,
} from "@/types/graphLab";

export const BST_CODE_SNIPPET = [
  "bool searchBST(int u, int target) {",
  "    if (u == 0) return false;      // Caso base: nó nulo",
  "    if (u == target) return true;  // Caso base: alvo encontrado!",
  "    ",
  "    if (target < u) {",
  "        // Alvo < nó: buscar na subárvore esquerda",
  "        return searchBST(left_child[u], target);",
  "    } else {",
  "        // Alvo > nó: buscar na subárvore direita",
  "        return searchBST(right_child[u], target);",
  "    }",
  "}",
];

export const DFS_CODE_SNIPPET = [
  "void dfs(int u) {",
  "    visited[u] = true;",
  "    in_stack[u] = true;",
  "    for (int v : adj[u]) {",
  "        if (!visited[v]) {",
  "            dfs(v);",
  "        } else if (in_stack[v]) {",
  "            // Ciclo detectado: Back Edge (u -> v)",
  "        }",
  "    }",
  "    in_stack[u] = false; // Backtrack",
  "}",
];

export const BFS_CODE_SNIPPET = [
  "void bfs(int origem) {",
  "    visited[origem] = true;",
  "    dist[origem] = 0;",
  "    queue<int> q;",
  "    q.push(origem);",
  "    while (!q.empty()) {",
  "        int u = q.front(); q.pop();",
  "        for (int v : adj[u]) {",
  "            if (!visited[v]) {",
  "                visited[v] = true;",
  "                dist[v] = dist[u] + 1;",
  "                q.push(v);",
  "            }",
  "        }",
  "    }",
  "}",
];

export const DIJKSTRA_CODE_SNIPPET = [
  "void dijkstra(int s) {",
  "    fill(dist.begin(), dist.end(), 1e9);",
  "    dist[s] = 0;",
  "    priority_queue<pair<int,int>, vector<pair<int,int>>, greater<>> pq;",
  "    pq.push({0, s});",
  "    while (!pq.empty()) {",
  "        auto [d, u] = pq.top(); pq.pop();",
  "        if (d > dist[u]) continue;",
  "        for (auto [v, w] : adj[u]) {",
  "            if (dist[u] + w < dist[v]) {",
  "                dist[v] = dist[u] + w;",
  "                pq.push({dist[v], v});",
  "            }",
  "        }",
  "    }",
  "}",
];

const MAX_SAFETY_STEPS = 1000;

/**
 * Generates an event-tape of deterministic snapshots for Depth-First Search.
 * Pure function: runs in microseconds and yields full time-travel capability.
 */
export function generateDfsExecutionTape(
  nodes: GraphNode[],
  edges: GraphEdge[],
  startNodeId: string
): ExecutionStep[] {
  const steps: ExecutionStep[] = [];
  const nodeStates: Record<string, NodeVisualState> = {};
  const edgeStates: Record<string, EdgeVisualState> = {};
  const visited: Record<string, boolean> = {};
  const inStack: Record<string, boolean> = {};
  const callStack: CallStackFrame[] = [];

  nodes.forEach((n) => {
    nodeStates[n.id] = "unvisited";
    visited[n.id] = false;
    inStack[n.id] = false;
  });

  edges.forEach((e) => {
    edgeStates[e.id] = "normal";
  });

  // Adjacency map
  const adj: Record<string, { to: string; edgeId: string }[]> = {};
  nodes.forEach((n) => (adj[n.id] = []));
  edges.forEach((e) => {
    adj[e.from]?.push({ to: e.to, edgeId: e.id });
    if (!e.directed) {
      adj[e.to]?.push({ to: e.from, edgeId: e.id });
    }
  });

  function cloneVisited() {
    return { ...visited };
  }
  function cloneCallStack() {
    return callStack.map((f) => ({ ...f, localVars: { ...f.localVars } }));
  }

  function emitStep(
    line: number,
    activeNode: string | null,
    activeEdge: string | null,
    log: string,
    currentLocalVars?: Record<string, string | number | boolean>
  ) {
    if (steps.length >= MAX_SAFETY_STEPS) {
      return;
    }
    const stackSnapshot = cloneCallStack();
    if (currentLocalVars && stackSnapshot.length > 0) {
      stackSnapshot[stackSnapshot.length - 1].localVars = { ...currentLocalVars };
    }

    steps.push({
      stepIndex: steps.length,
      lineHighlighted: line,
      memoryState: {
        visited: cloneVisited(),
        stack: stackSnapshot,
        localVars: currentLocalVars ? { ...currentLocalVars } : undefined,
      },
      activeNodeId: activeNode,
      activeEdgeId: activeEdge,
      nodeStates: { ...nodeStates },
      edgeStates: { ...edgeStates },
      logMessage: log,
    });
  }

  function dfs(u: string, depth: number) {
    if (steps.length >= MAX_SAFETY_STEPS) return;

    // Line 1: def dfs(u)
    callStack.push({
      functionName: "dfs",
      args: { u },
      callDepth: depth,
      localVars: { u, v: "-" },
    });
    nodeStates[u] = "visiting";
    emitStep(1, u, null, `Chamada dfs(${u}) adicionada à Call Stack.`, { u, depth });

    // Line 2: visited[u] = True
    visited[u] = true;
    emitStep(2, u, null, `Nó ${u} marcado como visitado (visited[${u}] = True).`, { u, visited: true });

    // Line 3: in_stack[u] = True
    inStack[u] = true;
    emitStep(3, u, null, `Nó ${u} empilhado na cadeia de recursão ativa (in_stack[${u}] = True).`, { u, inStack: true });

    const neighbors = adj[u] || [];
    for (const neighbor of neighbors) {
      if (steps.length >= MAX_SAFETY_STEPS) break;
      const v = neighbor.to;
      const edgeId = neighbor.edgeId;

      // Line 4: for v in adj[u]
      emitStep(4, u, edgeId, `Avaliando aresta (${u} -> ${v}) no loop de vizinhos.`, { u, v });

      if (!visited[v]) {
        // Line 5: if not visited[v]
        edgeStates[edgeId] = "traversed";
        emitStep(5, v, edgeId, `Vizinho ${v} não foi visitado ainda. Seguindo pela aresta de árvore (${u} -> ${v}).`, { u, v });

        // Line 6: dfs(v)
        dfs(v, depth + 1);

        // Retorno da recursão para o nó u
        nodeStates[u] = "visiting";
        emitStep(6, u, null, `Retorno da chamada dfs(${v}) para o nó ancestral ${u}.`, { u, v });
      } else if (inStack[v]) {
        // Line 7: elif in_stack[v] -> Ciclo detectado (Back Edge)
        edgeStates[edgeId] = "back_edge";
        emitStep(7, v, edgeId, `ALERTA: Vizinho ${v} já está ativo na Pilha! Ciclo detectado via Back-Edge (${u} -> ${v}).`, { u, v, ciclo: true });
        emitStep(8, v, edgeId, `Ignorando expansão do ciclo.`, { u, v });
      }
    }

    // Line 10: in_stack[u] = False; backtrack
    inStack[u] = false;
    nodeStates[u] = "visited";
    callStack.pop();
    emitStep(10, u, null, `Desempilhando dfs(${u}). Todos os vizinhos processados. Nó ${u} marcado como finalizado.`, { u, finished: true });
  }

  // Se o nó inicial existir, inicia a DFS
  if (nodes.some((n) => n.id === startNodeId)) {
    dfs(startNodeId, 0);
  }

  return steps;
}

export function generateBstExecutionTape(
  nodes: GraphNode[],
  edges: GraphEdge[],
  targetVal = 25
): ExecutionStep[] {
  const steps: ExecutionStep[] = [];
  const visited: Record<string, boolean> = {};
  const nodeStates: Record<string, NodeVisualState> = {};
  const edgeStates: Record<string, EdgeVisualState> = {};
  const callStack: CallStackFrame[] = [];

  nodes.forEach((n) => {
    nodeStates[n.id] = "unvisited";
  });
  edges.forEach((e) => {
    edgeStates[e.id] = "normal";
  });

  const emitStep = (
    lineHighlighted: number,
    activeNodeId: string | null,
    activeEdgeId: string | null,
    logMessage: string,
    localVars: Record<string, any> = {}
  ) => {
    steps.push({
      stepIndex: steps.length,
      lineHighlighted,
      memoryState: {
        visited: { ...visited },
        stack: [...callStack],
        localVars,
      },
      activeNodeId,
      activeEdgeId,
      nodeStates: { ...nodeStates },
      edgeStates: { ...edgeStates },
      logMessage,
    });
  };

  // Find root (node with no incoming edges or id '20')
  const incoming = new Set(edges.map((e) => e.to));
  let rootNode = nodes.find((n) => !incoming.has(n.id)) || nodes[0];
  if (!rootNode) return steps;

  // Build children lookup from edges
  const childrenMap: Record<string, { left?: string; right?: string }> = {};
  edges.forEach((e) => {
    if (!childrenMap[e.from]) childrenMap[e.from] = {};
    const fromVal = parseInt(e.from, 10);
    const toVal = parseInt(e.to, 10);
    if (!isNaN(fromVal) && !isNaN(toVal)) {
      if (toVal < fromVal) childrenMap[e.from].left = e.to;
      else childrenMap[e.from].right = e.to;
    } else {
      if (e.label?.includes("<") || e.label?.includes("esq")) {
        childrenMap[e.from].left = e.to;
      } else {
        childrenMap[e.from].right = e.to;
      }
    }
  });

  function search(uId: string, depth: number): boolean {
    if (!uId) {
      emitStep(2, null, null, `Nó nulo alcançado. Alvo ${targetVal} não encontrado.`);
      return false;
    }

    const uVal = parseInt(uId, 10);
    callStack.push({
      functionName: `searchBST(${uId}, ${targetVal})`,
      args: { u: uId, target: targetVal },
      callDepth: depth,
      localVars: { u: uVal, target: targetVal },
    });

    nodeStates[uId] = "visiting";
    visited[uId] = true;
    emitStep(1, uId, null, `Iniciando searchBST no nó ${uId}.`, { u: uVal, target: targetVal });
    emitStep(3, uId, null, `Comparando nó ${uId} com alvo ${targetVal}.`, { u: uVal, target: targetVal });

    if (uVal === targetVal) {
      nodeStates[uId] = "visited";
      emitStep(3, uId, null, `✓ SUCESSO! Nó ${uId} coincide com o alvo ${targetVal}. Busca concluída!`, {
        u: uVal,
        target: targetVal,
        found: true,
      });
      callStack.pop();
      return true;
    }

    if (targetVal < uVal) {
      emitStep(5, uId, null, `Alvo ${targetVal} < ${uVal}: descendo pela subárvore ESQUERDA.`);
      const leftChild = childrenMap[uId]?.left;
      const edge = edges.find((e) => e.from === uId && e.to === leftChild);
      if (edge) edgeStates[edge.id] = "traversed";
      emitStep(7, uId, edge?.id || null, `Chamando searchBST(${leftChild}, ${targetVal}).`);
      
      const found = leftChild ? search(leftChild, depth + 1) : false;
      callStack.pop();
      return found;
    } else {
      emitStep(8, uId, null, `Alvo ${targetVal} > ${uVal}: descendo pela subárvore DIREITA.`);
      const rightChild = childrenMap[uId]?.right;
      const edge = edges.find((e) => e.from === uId && e.to === rightChild);
      if (edge) edgeStates[edge.id] = "traversed";
      emitStep(10, uId, edge?.id || null, `Chamando searchBST(${rightChild}, ${targetVal}).`);

      const found = rightChild ? search(rightChild, depth + 1) : false;
      callStack.pop();
      return found;
    }
  }

  search(rootNode.id, 0);
  return steps;
}


/**
 * Generates an event-tape for Breadth-First Search (BFS).
 */
export function generateBfsExecutionTape(
  nodes: GraphNode[],
  edges: GraphEdge[],
  startNodeId: string
): ExecutionStep[] {
  const steps: ExecutionStep[] = [];
  const nodeStates: Record<string, NodeVisualState> = {};
  const edgeStates: Record<string, EdgeVisualState> = {};
  const visited: Record<string, boolean> = {};
  const dist: Record<string, number> = {};
  const queue: string[] = [];

  nodes.forEach((n) => {
    nodeStates[n.id] = "unvisited";
    visited[n.id] = false;
    dist[n.id] = -1;
  });
  edges.forEach((e) => (edgeStates[e.id] = "normal"));

  const adj: Record<string, { to: string; edgeId: string }[]> = {};
  nodes.forEach((n) => (adj[n.id] = []));
  edges.forEach((e) => {
    adj[e.from]?.push({ to: e.to, edgeId: e.id });
    if (!e.directed) {
      adj[e.to]?.push({ to: e.from, edgeId: e.id });
    }
  });

  function emitStep(
    line: number,
    activeNode: string | null,
    activeEdge: string | null,
    log: string,
    localVars?: Record<string, string | number | boolean>
  ) {
    if (steps.length >= MAX_SAFETY_STEPS) return;
    steps.push({
      stepIndex: steps.length,
      lineHighlighted: line,
      memoryState: {
        visited: { ...visited },
        stack: [],
        queue: [...queue],
        currentDist: { ...dist },
        localVars: localVars ? { ...localVars } : undefined,
      },
      activeNodeId: activeNode,
      activeEdgeId: activeEdge,
      nodeStates: { ...nodeStates },
      edgeStates: { ...edgeStates },
      logMessage: log,
    });
  }

  if (!nodes.some((n) => n.id === startNodeId)) return steps;

  // 1: def bfs
  emitStep(1, startNodeId, null, `Iniciando BFS a partir da origem ${startNodeId}.`);
  // 2: visited[s] = True
  visited[startNodeId] = true;
  nodeStates[startNodeId] = "visiting";
  emitStep(2, startNodeId, null, `Origem ${startNodeId} marcada como visitada.`);
  // 3: dist[s] = 0
  dist[startNodeId] = 0;
  emitStep(3, startNodeId, null, `Distância da origem ${startNodeId} definida como 0.`);
  // 4: queue.append(s)
  queue.push(startNodeId);
  emitStep(4, startNodeId, null, `Enfileirado nó ${startNodeId} na fila FIFO.`);

  // 5: while queue
  while (queue.length > 0 && steps.length < MAX_SAFETY_STEPS) {
    emitStep(5, null, null, `Verificando se a fila possui elementos (tamanho = ${queue.length}).`);
    // 6: u = queue.pop(0)
    const u = queue.shift()!;
    nodeStates[u] = "visiting";
    emitStep(6, u, null, `Desenfileirado nó ${u} para exploração de camadas.`, { u });

    const neighbors = adj[u] || [];
    for (const neighbor of neighbors) {
      if (steps.length >= MAX_SAFETY_STEPS) break;
      const v = neighbor.to;
      const edgeId = neighbor.edgeId;

      emitStep(7, u, edgeId, `Avaliando vizinho ${v} de ${u}.`, { u, v });
      if (!visited[v]) {
        emitStep(8, v, edgeId, `Vizinho ${v} ainda não visitado.`);
        visited[v] = true;
        nodeStates[v] = "visiting";
        emitStep(9, v, edgeId, `visited[${v}] = True (marcado no push para evitar duplicações).`);
        dist[v] = dist[u] + 1;
        emitStep(10, v, edgeId, `dist[${v}] = dist[${u}] + 1 = ${dist[v]}.`);
        queue.push(v);
        edgeStates[edgeId] = "traversed";
        emitStep(11, v, edgeId, `Nó ${v} adicionado à fila FIFO.`);
      }
    }
    nodeStates[u] = "visited";
  }

  return steps;
}


