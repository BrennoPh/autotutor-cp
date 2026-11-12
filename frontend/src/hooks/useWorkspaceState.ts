import { useState, useCallback } from "react";
import { TutorMessage, TutorActionType } from "@/types/tutor";
import { ComponentStatus } from "@/types/workspace";
import { tutorService } from "@/services/tutorService";

export function useWorkspaceState() {
  const [isZenMode, setIsZenMode] = useState(false);
  const [isDockOpen, setIsDockOpen] = useState(true);
  const [tutorStatus, setTutorStatus] = useState<ComponentStatus>("active");
  const [messages, setMessages] = useState<TutorMessage[]>([
    {
      id: "initial-tutor-msg",
      sender: "tutor",
      content: "Olá! Sou o Tutor Colaborativo integrado ao LangGraph e à Memória Akita. Qualquer dúvida ou erro no juiz é compartilhado entre nossa equipe de agentes para guiar você.",
      timestamp: "Agora",
      agentTrail: ["ai_memory_recall", "socratic_tutor_agent", "ai_memory_consolidate"],
    },
  ]);

  const toggleZenMode = useCallback(() => {
    setIsZenMode((prev) => !prev);
  }, []);

  const toggleDock = useCallback(() => {
    setIsDockOpen((prev) => !prev);
  }, []);

  const triggerContextualAction = useCallback(async (
    action: TutorActionType,
    snippet: string,
    context?: { problem_id?: string; code?: string; judge_result?: any }
  ) => {
    setIsDockOpen(true);
    const userPromptMap: Record<TutorActionType, string> = {
      hint: snippet || "Me dê uma dica socrática sem me entregar a resposta pronta.",
      scaffolding: snippet || "Forneça um esqueleto de código com lacunas (scaffolding) e comentários para eu completar em C++.",
      minimal_example: snippet || "Mostre um exemplo mínimo de caso de teste com rastreamento das variáveis.",
      review_code: snippet || "Analise o código C++ que escrevi até agora, procurando possíveis bugs, TLE ou violação de invariantes.",
      explain_analogy: `Pode me explicar este trecho usando uma analogia do cotidiano? "${snippet}"`,
      make_flashcard: `Transforme este trecho em um flashcard de pergunta e resposta: "${snippet}"`,
      simplify: `Simplifique a explicação deste trecho de forma direta: "${snippet}"`,
      generate_quiz: `Gere uma questão de múltipla escolha com pegadinha sobre: "${snippet}"`,
    };

    const userPrompt = userPromptMap[action] || snippet;
    const userMsg: TutorMessage = {
      id: `user-${Date.now()}`,
      sender: "user",
      content: userPrompt,
      timestamp: "Agora",
      actionContext: { actionType: action, snippet },
    };

    setMessages((prev) => [...prev, userMsg]);
    setTutorStatus("streaming");

    try {
      const response = await tutorService.sendMessage({
        message: userPrompt,
        action: action === "explain_analogy" ? "explain" : "hint",
        problem_id: context?.problem_id,
        code: context?.code,
        judge_result: context?.judge_result,
        collaborative: true,
      });

      setMessages((prev) => [
        ...prev,
        {
          id: `bot-${Date.now()}`,
          sender: "tutor",
          content: response.reply,
          timestamp: "Agora",
          agentTrail: response.agent_trail,
        },
      ]);
      setTutorStatus("active");
    } catch {
      const botResponseMap: Record<TutorActionType, string> = {
        hint: `💡 **Dica Socrática:**\nPense na invariante do algoritmo: quais dados precisam estar garantidos antes de avançar para o próximo nó ou subproblema? Observe os limites assintóticos do laço principal.`,
        scaffolding: `🧩 **Estrutura com Lacunas (C++17):**\n\`\`\`cpp\n// TODO [LACUNA 1]: Defina o caso base ou condição de parada\nif (/* condição */) return;\n\n// TODO [LACUNA 2]: Atualize o estado de visitação ou transição DP\nvisited[u] = true;\n\n// TODO [LACUNA 3]: Itere sobre os vizinhos ou subproblemas\nfor (int v : adj[u]) {\n    // recursão / fila\n}\n\`\`\``,
        minimal_example: `🔍 **Exemplo Mínimo Comentado:**\nConsidere uma entrada simples de 3 vértices: 1 -> 2 e 1 -> 3.\n- Raiz: 1 (distância 0)\n- Nível 1: [2, 3] (distância 1)\nA fila garante ordem estrita por camada.`,
        review_code: `📝 **Comentários do Código:**\nSeu scaffold C++ está estruturado. Verifique se o vetor de visitados é reinicializado entre casos de teste e se a complexidade respeita o limite de 2.0s no juiz.`,
        explain_analogy: `💡 **Analogia Prática:**\nPense na Fila (FIFO) da BFS como uma fila de padaria: quem chega primeiro recebe o pão primeiro. Já a Pilha (LIFO) da DFS é como uma pilha de pratos: para alcançar o prato do fundo, você é obrigado a tirar os pratos de cima antes.`,
        make_flashcard: `🗂️ **Flashcard Gerado:**\n\n**Pergunta:** Por que a BFS garante o menor caminho em grafos não-ponderados?\n**Resposta:** Porque a Fila (FIFO) explora os vértices em camadas concêntricas de distância.`,
        simplify: `🎯 **Em resumo direto:**\n- **BFS:** Exploração em largura/níveis usando Fila (Queue).\n- **DFS:** Exploração em profundidade usando Pilha (Recursão).`,
        generate_quiz: `🧪 **Desafio Rápido:**\nSe você esquecer de marcar o vértice como visitado no momento do \`push\` na BFS, o que acontecerá em um grafo com ciclos?\n\nA) O código funciona normalmente em O(V+E)\nB) TLE / MLE por reinserção redundante de vértices\nC) Resposta errada (WA) apenas`,
      };

      setMessages((prev) => [
        ...prev,
        {
          id: `bot-${Date.now()}`,
          sender: "tutor",
          content: botResponseMap[action] || "Verifique as condições de contorno e invariantes do algoritmo.",
          timestamp: "Agora",
          agentTrail: ["ai_memory_recall", "socratic_tutor_agent"],
        },
      ]);
      setTutorStatus("active");
    }
  }, []);

  return {
    isZenMode,
    isDockOpen,
    tutorStatus,
    messages,
    toggleZenMode,
    toggleDock,
    triggerContextualAction,
    setIsDockOpen,
  };
}
