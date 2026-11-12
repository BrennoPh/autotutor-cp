import { GraphNode, GraphEdge } from "@/types/graphLab";

/**
 * Extracts nodes and edges from a Mermaid graph definition (graph TD / LR) or edge text.
 */
export function extractGraphFromMermaid(mermaidText: string): { nodes: GraphNode[]; edges: GraphEdge[] } | null {
  if (!mermaidText) return null;

  const lines = mermaidText.split("\n");
  const edgeList: Array<{ from: string; to: string; label?: string }> = [];
  const nodeLabels: Record<string, string> = {};

  // Regex patterns for arrows: -->, -.->, ==> with optional labels
  const arrowPattern = /([a-zA-Z0-9_-]+)(?:\["?(.*?)"?\])?\s*(?:-->|-.->|==>|->)(?:\|(.*?)\|)?\s*([a-zA-Z0-9_-]+)(?:\["?(.*?)"?\])?/;

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("graph ") || trimmed.startsWith("flowchart ") || trimmed.startsWith("classDef ") || trimmed.startsWith("class ")) {
      continue;
    }

    const match = trimmed.match(arrowPattern);
    if (match) {
      const fromId = match[1].replace(/^N/, "");
      const fromLabel = match[2] || fromId;
      const edgeLabel = match[3] || "";
      const toId = match[4].replace(/^N/, "");
      const toLabel = match[5] || toId;

      nodeLabels[fromId] = fromLabel;
      nodeLabels[toId] = toLabel;

      edgeList.push({
        from: fromId,
        to: toId,
        label: edgeLabel,
      });
    } else {
      // Direct edge line like "1 2" or "1 -> 2"
      const simpleMatch = trimmed.match(/^([a-zA-Z0-9]+)\s+(?:->\s+)?([a-zA-Z0-9]+)/);
      if (simpleMatch) {
        const fromId = simpleMatch[1];
        const toId = simpleMatch[2];
        nodeLabels[fromId] = fromId;
        nodeLabels[toId] = toId;
        edgeList.push({ from: fromId, to: toId });
      }
    }
  }

  const nodeIds = Object.keys(nodeLabels);
  if (nodeIds.length === 0 && edgeList.length === 0) {
    return null;
  }

  // Position nodes nicely on canvas (circular or hierarchical layout)
  const n = nodeIds.length;
  const centerX = 260;
  const centerY = 190;
  const radius = Math.min(160, Math.max(75, 26 * n));

  const nodes: GraphNode[] = nodeIds.map((id, idx) => {
    const angle = (2 * Math.PI * idx) / Math.max(1, n) - Math.PI / 2;
    const x = Math.round(centerX + radius * Math.cos(angle));
    const y = Math.round(centerY + radius * Math.sin(angle));
    return {
      id,
      label: nodeLabels[id] || id,
      x,
      y,
      state: "unvisited",
    };
  });

  const edges: GraphEdge[] = edgeList.map((e, idx) => ({
    id: `e-${e.from}-${e.to}-${idx}`,
    from: e.from,
    to: e.to,
    directed: true,
    state: "normal",
  }));

  return { nodes, edges };
}
