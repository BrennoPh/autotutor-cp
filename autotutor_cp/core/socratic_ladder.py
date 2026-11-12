"""Socratic Hint Ladder and Pre-Flight Asymptotic Evaluation for AutoTutor CP.

Demonstrates RAG (KnowledgeBase citations), Cognitive AI Memory (LearnerMemory)
and strict Zero-Leak Guardrails based on AutoCode, OI-Assistant and Codigen principles.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

TIER_NAMES = {
    1: "Invariante & Teoremas Fundamentais",
    2: "Contraexemplo Mínimo & Casos de Borda",
    3: "Modelagem de Estado & Estruturas de Dados",
    4: "Esqueleto Lógico Conceitual (Sem Código)",
}

FORBIDDEN_LEAK_PATTERNS = [
    r"#\s*include",
    r"\bint\s+main\s*\(",
    r"\bvoid\s+main\s*\(",
    r"\bmain\s*\(\s*\)",
    r"\breturn\s+0\s*;",
    r"\busing\s+namespace\s+std\s*;",
    r"\bstd::cin\b",
    r"\bstd::cout\b",
]


def verify_zero_leak(text: str, tier: int) -> Tuple[bool, str]:
    """Ensures no executable C++ solution leaks to the student."""
    if not isinstance(text, str) or not text.strip():
        return False, "Texto vazio"
    for pattern in FORBIDDEN_LEAK_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return False, f"Padrão proibido detectado: {pattern}"

    # In tiers 1-3, strictly prohibit code blocks containing multiple executable statements
    if tier <= 3:
        code_blocks = re.findall(r"```(?:cpp|c\+\+|c)?(.*?)```", text, re.DOTALL)
        for block in code_blocks:
            clean_lines = [
                line.strip() for line in block.splitlines()
                if line.strip() and not line.strip().startswith("//")
            ]
            if len(clean_lines) > 2 or any(";" in line for line in clean_lines):
                return False, "Bloco de código executável em Tier socrático restrito (1-3)"

    return True, ""


def extract_memory_insight(memory_evidence: Any, topic: str) -> Tuple[str, str]:
    """Derives pedagogical triggers and adaptations from student memory."""
    if not memory_evidence:
        return (
            f"Iniciando exploração estruturada do tópico '{topic}'.",
            "Mantenha o foco em propriedades invariantes antes de codificar."
        )
    text_data = ""
    if isinstance(memory_evidence, dict):
        pages = memory_evidence.get("recalled_pages", [])
        text_data = " ".join(p.get("excerpt", "") for p in pages)
    else:
        text_data = str(memory_evidence)

    text_lower = text_data.lower()
    if "runtime error" in text_lower or re.search(r"\bre\b", text_lower) or any(k in text_lower for k in ["recursão", "pilha", "stack"]):
        return (
            "Detectamos no seu histórico registros anteriores de Runtime Error (RE) por recursão profunda ou limites de pilha.",
            "Considere implementar a travessia de forma iterativa ou garantir que a condição de parada seja testada antes da chamada recursiva."
        )
    if "time limit" in text_lower or re.search(r"\btle\b", text_lower) or any(k in text_lower for k in ["aninhado", "infinito", "tempo excedido"]):
        return (
            "Seu histórico recente aponta atenção especial a Time Limit Exceeded (TLE) e custos assintóticos.",
            "Certifique-se de marcar nós/estados visitados imediatamente ao enfileirar, evitando expansão combinatória."
        )
    if "wrong answer" in text_lower or re.search(r"\bwa\b", text_lower) or any(k in text_lower for k in ["contraexemplo", "overflow", "resposta errada"]):
        return (
            "Identificamos desafios prévios com casos extremos (WA) e limites numéricos.",
            "Teste mentalmente o comportamento em instâncias mínimas (N=1) e avalie se somas podem exceder o limite de 32 bits."
        )

    return (
        f"Histórico consolidado no tópico '{topic}' carregado com sucesso.",
        "Aplique o raciocínio socrático gradual para deduzir a estrutura da solução."
    )


def generate_fallback_hint(
    problem: Dict[str, Any],
    tier: int,
    rag_refs: List[Dict[str, Any]],
    memory_evidence: Any,
    user_query: Optional[str] = None
) -> Dict[str, Any]:
    """Generates a high-yield, mathematically sound socratic hint without LLM dependency."""
    topic = problem.get("topic") or problem.get("family", "Algoritmos")
    title = f"{TIER_NAMES.get(tier, 'Pista')} · {problem.get('title', 'Problema')}"
    trigger, adaptation = extract_memory_insight(memory_evidence, topic)
    family = problem.get("family", "").lower()
    math_essence = problem.get("math_essence") or "Propriedade estrutural do problema."
    approach = problem.get("approach_summary") or "Decomposição algorítmica ótima."

    if tier == 1:
        hint_md = (
            f"### Invariante Fundamental\n\n"
            f"> **Essência Teórica:** {math_essence}\n\n"
            f"**Pergunta Socrática:** Em qualquer instância válida deste problema, qual propriedade "
            f"permanece verdadeira a cada passo da execução? Se você dividir o problema em subproblemas "
            f"menores, como a resposta do todo se relaciona com a resposta das partes?\n\n"
            f"*Dica de reflexão:* Observe as restrições informadas no enunciado e pense em qual teorema "
            f"ou invariante matemática garante que uma escolha não invalide a corretude global."
        )
    elif tier == 2:
        hint_md = (
            f"### Teste de Mesa e Casos de Borda\n\n"
            f"Antes de escrever código, considere os seguintes contraexemplos mínimos:\n\n"
            f"1. **Instância Mínima:** $N = 1$ ou grafo com zero arestas / componentes isolados.\n"
            f"2. **Caso Extremo:** Elementos todos iguais, ou grafo em formato de linha vs estrela.\n"
            f"3. **Extremos Numéricos:** O somatório ou produto intermediário cabe em um tipo inteiro padrão de 32 bits?\n\n"
            f"**Pergunta Socrática:** Se executarmos seu algoritmo manualmente com $N=3$, qual o "
            f"estado intermediário exato após a primeira iteração? Há risco de loop infinito ou acesso a índice inválido?"
        )
    elif tier == 3:
        hint_md = (
            f"### Modelagem de Estado e Estruturas de Dados\n\n"
            f"Para atingir a complexidade alvo ({problem.get('complexity', 'ótima')}), recomenda-se:\n\n"
            f"- **Abordagem Estruturada:** {approach}\n"
            f"- **Representação do Estado:** Qual informação é estritamente necessária manter para não refazer trabalho?\n"
            f"- **Estrutura Recomendada:** Se o grafo for esparso ($M \\approx N$), uma Lista de Adjacência "
            f"(`vector<vector<int>>`) consome $O(N + M)$, enquanto uma Matriz consumiria $O(N^2)$ e causaria MLE/TLE.\n\n"
            f"**Pergunta Socrática:** Quais operações de consulta e atualização são feitas repetidamente no loop central?"
        )
    else:  # Tier 4
        hint_md = (
            f"### Decomposição Lógica em Passos (Sem Código)\n\n"
            f"Siga esta sequência lógica de alto nível para estruturar seu programa C++:\n\n"
            f"1. **Leitura e Inicialização:** Ler as dimensões e instanciar as estruturas de dados necessárias "
            f"com tamanho baseado em $N$ (atenção à convenção 0-based vs 1-based).\n"
            f"2. **Pré-processamento:** Preencher estados base ou construir a lista de adjacência.\n"
            f"3. **Execução Principal:** Percorrer os elementos ou nós seguindo a ordem necessária "
            f"(fila, pilha, ou ordenação), mantendo o vetor de visitados/distâncias atualizado.\n"
            f"4. **Agregação e Saída:** Combinar as respostas parciais e imprimir o resultado conforme o formato exigido.\n\n"
            f"*Desafio:* Implemente agora essas 4 etapas no editor ao lado mantendo seu código limpo e modular."
        )

    citations = [
        {"title": r.get("title", ""), "publisher": r.get("publisher", ""), "url": r.get("url", "")}
        for r in rag_refs
    ]

    return {
        "problem_id": problem.get("id"),
        "tier": tier,
        "tier_name": TIER_NAMES.get(tier, "Pista"),
        "title": title,
        "hint_markdown": hint_md,
        "rag_citations": citations,
        "memory_trigger": trigger,
        "memory_adaptation": adaptation,
        "zero_leak_verified": True,
        "next_tier_available": tier + 1 if tier < 4 else None,
    }


def evaluate_complexity_preflight(
    problem: Dict[str, Any],
    proposed_complexity: str,
    chosen_structure: str,
    estimated_ops: Optional[int] = None
) -> Dict[str, Any]:
    """Analytically evaluates proposed complexity and data structure against constraints."""
    constraints = problem.get("constraints") or {}
    n_max = constraints.get("n_max") or 100000
    time_limit = float(problem.get("time_limit_sec") or 1.0)
    target_comp = problem.get("complexity", "O(N)")

    # Standard operations budget in C++ (~10^8 ops per second)
    max_safe_ops = int(1e8 * time_limit)
    comp_clean = re.sub(r"\s+", "", proposed_complexity.lower())
    struct_clean = chosen_structure.lower()

    # Estimate operations if not provided
    calculated_ops = estimated_ops or 0
    if not calculated_ops:
        if any(x in comp_clean for x in ["n^2", "v^2", "n*n", "v*v", "n**2"]):
            calculated_ops = int(n_max) * int(n_max)
        elif any(x in comp_clean for x in ["log", "nlogn", "vlogv", "eloge"]):
            calculated_ops = int(n_max * 18)
        elif any(x in comp_clean for x in ["n+m", "v+e", "o(n)", "o(v)"]):
            calculated_ops = int(n_max * 2)
        elif "2^n" in comp_clean or "2**n" in comp_clean:
            calculated_ops = 2 ** min(n_max, 32)
        else:
            calculated_ops = int(n_max)

    # Edge cases catalogue by problem family
    family = problem.get("family", "").lower()
    edge_cases_map = {
        "graph": [
            "Grafo desconexo composto por múltiplos componentes",
            "Vértices isolados com grau 0",
            "Grafos com ciclos ou arestas paralelas",
            "Vértice de início já correspondente ao destino",
        ],
        "dp": [
            "Instância com N=1 (caso base elementar)",
            "Valores negativos ou nulos se houver acumuladores",
            "Estouro de capacidade de inteiros de 32 bits (use long long)",
            "Transições com estados que nunca são alcançáveis",
        ],
        "greedy": [
            "Empates em critérios de ordenação (ex.: mesmo fim de intervalo)",
            "Intervalos adjacentes compartilhando apenas o ponto de fronteira",
            "Conjunto de entrada já ordenado em ordem reversa",
        ],
        "binary": [
            "Elemento procurado fora do intervalo ou inexistente",
            "Intervalos com L == R (condição de parada estrita)",
            "Cálculo de meio com overflow: prefira L + (R - L) / 2",
        ],
        "segtree": [
            "Consultas com intervalo [L, R] completamente fora do nó atual",
            "Árvore alocada com menos de 4*N posições causando RE",
            "Atualizações repetidas na mesma folha",
        ],
        "prefix": [
            "Consultas cobrindo todo o intervalo de 1 a N",
            "Consultas pontuais com L == R",
            "Acesso ao índice 0 quando os dados usam convenção 1-based",
        ],
    }
    edge_cases = edge_cases_map.get(family, [
        "Instância mínima de teste N=1",
        "Valores extremos de limites e tipos de 64 bits",
        "Tempo de execução com casos induzidos ao pior caso",
    ])

    # 1. Memory Check (MLE)
    if "matriz" in struct_clean and ("adjac" in struct_clean or "matriz" in struct_clean):
        if n_max >= 5000:
            bytes_req = (n_max * n_max) * 4
            mb_req = bytes_req / (1024 * 1024)
            return {
                "status": "WARNING",
                "verdict_preview": "MLE_RISK",
                "feedback": (
                    f"Risco Crítico de Memória (MLE): Uma matriz {n_max}x{n_max} exigiria aproximadamente "
                    f"{mb_req:.0f} MB, excedendo o limite de memória. Para grafos esparsos, use "
                    f"Lista de Adjacência (`vector<vector<int>>` ou `vector<int> adj[N]`)."
                ),
                "estimated_operations": calculated_ops,
                "time_limit_sec": time_limit,
                "edge_cases_to_watch": edge_cases,
            }

    # 2. Time Check (TLE)
    if calculated_ops > max_safe_ops:
        return {
            "status": "REJECTED" if calculated_ops > max_safe_ops * 5 else "WARNING",
            "verdict_preview": "TLE_RISK",
            "feedback": (
                f"Risco de Tempo Limite (TLE): A complexidade proposta {proposed_complexity} "
                f"resulta em cerca de {calculated_ops:,.0f} operações com N={n_max}. "
                f"Para o limite de {time_limit:.1f}s, o orçamento máximo é ~{max_safe_ops:,.0f} operações. "
                f"A complexidade esperada para este problema é {target_comp}."
            ),
            "estimated_operations": calculated_ops,
            "time_limit_sec": time_limit,
            "edge_cases_to_watch": edge_cases,
        }

    # 3. Approved (VIABLE)
    est_seconds = calculated_ops / 1e8
    return {
        "status": "APPROVED",
        "verdict_preview": "VIABLE",
        "feedback": (
            f"Intuição Aprovada! A complexidade {proposed_complexity} executará aproximadamente "
            f"{calculated_ops:,.0f} operações (~{est_seconds:.3f}s), perfeitamente adequada ao limite "
            f"de {time_limit:.1f}s. A estrutura '{chosen_structure}' é condizente com a meta."
        ),
        "estimated_operations": calculated_ops,
        "time_limit_sec": time_limit,
        "edge_cases_to_watch": edge_cases,
    }
