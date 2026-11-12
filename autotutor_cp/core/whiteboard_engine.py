"""Engine for interactive competitive programming whiteboard and AI visual generations."""
import json
import math
import re


WHITEBOARD_PRESETS = {
    'dag': {
        'title': 'DAG e Ordenação Topológica',
        'description': 'Grafo Acíclico Dirigido com 5 nós. Observe que todas as arestas apontam para a direita (ordem topológica 1 → 2 → 3 → 4 → 5).',
        'mermaid': (
            'graph LR\n'
            '  N1["1 (início)"] --> N2["2"]\n'
            '  N1 --> N3["3"]\n'
            '  N2 --> N4["4"]\n'
            '  N3 --> N4\n'
            '  N4 --> N5["5 (fim)"]\n'
            '  classDef nodeStyle fill:#e0e7ff,stroke:#4f46e5,stroke-width:2px,color:#1e1b4b;\n'
            '  class N1,N2,N3,N4,N5 nodeStyle;'
        ),
        'nodes': [
            {'id': '1', 'x': 80, 'y': 150, 'label': '1', 'color': '#4f46e5'},
            {'id': '2', 'x': 220, 'y': 80, 'label': '2', 'color': '#06b6d4'},
            {'id': '3', 'x': 220, 'y': 220, 'label': '3', 'color': '#06b6d4'},
            {'id': '4', 'x': 360, 'y': 150, 'label': '4', 'color': '#10b981'},
            {'id': '5', 'x': 490, 'y': 150, 'label': '5', 'color': '#10b981'}
        ],
        'edges': [
            {'from': '1', 'to': '2', 'label': 'tree', 'color': '#4f46e5', 'directed': True},
            {'from': '1', 'to': '3', 'label': 'tree', 'color': '#4f46e5', 'directed': True},
            {'from': '2', 'to': '4', 'label': 'tree', 'color': '#4f46e5', 'directed': True},
            {'from': '3', 'to': '4', 'label': 'forward', 'color': '#06b6d4', 'directed': True},
            {'from': '4', 'to': '5', 'label': 'tree', 'color': '#10b981', 'directed': True}
        ]
    },
    'cycle': {
        'title': 'Ciclo na DFS e Back Edge',
        'description': 'Demonstração de detecção de ciclo. A aresta pontilhada vermelha (4 → 1) é uma Back Edge que aponta para um ancestral ativo na pilha de recursão.',
        'mermaid': (
            'graph TD\n'
            '  N1["1 (ancestral cinza)"] -->|Tree Edge| N2["2 (cinza)"]\n'
            '  N2 -->|Tree Edge| N3["3 (cinza)"]\n'
            '  N3 -->|Tree Edge| N4["4 (cinza)"]\n'
            '  N4 -.->|Back Edge: CICLO!| N1\n'
            '  classDef nodeStyle fill:#fee2e2,stroke:#ef4444,stroke-width:2px,color:#7f1d1d;\n'
            '  classDef normStyle fill:#e0e7ff,stroke:#4f46e5,stroke-width:2px,color:#1e1b4b;\n'
            '  class N1,N2,N3 normStyle;\n'
            '  class N4 nodeStyle;'
        ),
        'nodes': [
            {'id': '1', 'x': 180, 'y': 70, 'label': '1', 'color': '#4f46e5'},
            {'id': '2', 'x': 360, 'y': 70, 'label': '2', 'color': '#4f46e5'},
            {'id': '3', 'x': 360, 'y': 230, 'label': '3', 'color': '#4f46e5'},
            {'id': '4', 'x': 180, 'y': 230, 'label': '4', 'color': '#ef4444'}
        ],
        'edges': [
            {'from': '1', 'to': '2', 'label': 'Tree', 'color': '#4f46e5', 'directed': True},
            {'from': '2', 'to': '3', 'label': 'Tree', 'color': '#4f46e5', 'directed': True},
            {'from': '3', 'to': '4', 'label': 'Tree', 'color': '#4f46e5', 'directed': True},
            {'from': '4', 'to': '1', 'label': 'Back Edge (Ciclo!)', 'color': '#ef4444', 'directed': True}
        ]
    },
    'tree': {
        'title': 'Árvore Binária e Alturas',
        'description': 'Árvore com 7 vértices. Observe que árvores são grafos conexos acíclicos com exatamente V - 1 arestas.',
        'mermaid': (
            'graph TD\n'
            '  R["Raiz (1)"] --> B2["2"]\n'
            '  R --> B3["3"]\n'
            '  B2 --> B4["4"]\n'
            '  B2 --> B5["5"]\n'
            '  B3 --> B6["6"]\n'
            '  B3 --> B7["7"]\n'
            '  classDef root fill:#fef3c7,stroke:#f59e0b,stroke-width:2px,color:#78350f;\n'
            '  classDef leaf fill:#e0e7ff,stroke:#4f46e5,stroke-width:2px,color:#1e1b4b;\n'
            '  class R root;\n'
            '  class B2,B3,B4,B5,B6,B7 leaf;'
        ),
        'nodes': [
            {'id': '1', 'x': 280, 'y': 50, 'label': 'Raiz (1)', 'color': '#f59e0b'},
            {'id': '2', 'x': 150, 'y': 130, 'label': '2', 'color': '#4f46e5'},
            {'id': '3', 'x': 410, 'y': 130, 'label': '3', 'color': '#4f46e5'},
            {'id': '4', 'x': 90, 'y': 220, 'label': '4', 'color': '#10b981'},
            {'id': '5', 'x': 210, 'y': 220, 'label': '5', 'color': '#10b981'},
            {'id': '6', 'x': 350, 'y': 220, 'label': '6', 'color': '#10b981'},
            {'id': '7', 'x': 470, 'y': 220, 'label': '7', 'color': '#10b981'}
        ],
        'edges': [
            {'from': '1', 'to': '2', 'label': '', 'color': '#4f46e5', 'directed': True},
            {'from': '1', 'to': '3', 'label': '', 'color': '#4f46e5', 'directed': True},
            {'from': '2', 'to': '4', 'label': '', 'color': '#10b981', 'directed': True},
            {'from': '2', 'to': '5', 'label': '', 'color': '#10b981', 'directed': True},
            {'from': '3', 'to': '6', 'label': '', 'color': '#10b981', 'directed': True},
            {'from': '3', 'to': '7', 'label': '', 'color': '#10b981', 'directed': True}
        ]
    },
    'bfs_layers': {
        'title': 'Camadas de Distância na BFS',
        'description': 'A Busca em Largura expande em ondas concêntricas de distância: Origem (d=0), Vizinhos diretos (d=1) e Próxima camada (d=2).',
        'mermaid': (
            'graph LR\n'
            '  subgraph Camada0 ["Camada d=0"]\n'
            '    S["S (Origem)"]\n'
            '  end\n'
            '  subgraph Camada1 ["Camada d=1"]\n'
            '    A["A (d=1)"]\n'
            '    B["B (d=1)"]\n'
            '  end\n'
            '  subgraph Camada2 ["Camada d=2"]\n'
            '    C["C (d=2)"]\n'
            '    D["D (d=2)"]\n'
            '  end\n'
            '  S --> A\n'
            '  S --> B\n'
            '  A --> C\n'
            '  B --> D\n'
            '  classDef c0 fill:#fef3c7,stroke:#f59e0b,stroke-width:2px;\n'
            '  classDef c1 fill:#e0e7ff,stroke:#4f46e5,stroke-width:2px;\n'
            '  classDef c2 fill:#d1fae5,stroke:#10b981,stroke-width:2px;\n'
            '  class S c0; class A,B c1; class C,D c2;'
        ),
        'nodes': [
            {'id': 'S', 'x': 80, 'y': 150, 'label': 'S (d=0)', 'color': '#f59e0b'},
            {'id': 'A', 'x': 230, 'y': 90, 'label': 'A (d=1)', 'color': '#4f46e5'},
            {'id': 'B', 'x': 230, 'y': 210, 'label': 'B (d=1)', 'color': '#4f46e5'},
            {'id': 'C', 'x': 400, 'y': 90, 'label': 'C (d=2)', 'color': '#10b981'},
            {'id': 'D', 'x': 400, 'y': 210, 'label': 'D (d=2)', 'color': '#10b981'}
        ],
        'edges': [
            {'from': 'S', 'to': 'A', 'label': '+1 passo', 'color': '#4f46e5', 'directed': True},
            {'from': 'S', 'to': 'B', 'label': '+1 passo', 'color': '#4f46e5', 'directed': True},
            {'from': 'A', 'to': 'C', 'label': '+1 passo', 'color': '#10b981', 'directed': True},
            {'from': 'B', 'to': 'D', 'label': '+1 passo', 'color': '#10b981', 'directed': True}
        ]
    },
    'bipartite': {
        'title': 'Grafo Bipartido (2-Coloração)',
        'description': 'Um grafo é bipartido se e somente se não possui ciclos de comprimento ímpar. Os vértices podem ser particionados em dois conjuntos U e V onde arestas só existem entre U e V.',
        'mermaid': (
            'graph LR\n'
            '  subgraph Grupo_U ["Conjunto U (Azul)"]\n'
            '    U1["U1"]\n'
            '    U2["U2"]\n'
            '    U3["U3"]\n'
            '  end\n'
            '  subgraph Grupo_V ["Conjunto V (Verde)"]\n'
            '    V1["V1"]\n'
            '    V2["V2"]\n'
            '    V3["V3"]\n'
            '  end\n'
            '  U1 --- V1\n'
            '  U1 --- V2\n'
            '  U2 --- V2\n'
            '  U3 --- V3\n'
            '  classDef setU fill:#e0e7ff,stroke:#4f46e5,stroke-width:2px,color:#1e1b4b;\n'
            '  classDef setV fill:#d1fae5,stroke:#10b981,stroke-width:2px,color:#064e3b;\n'
            '  class U1,U2,U3 setU;\n'
            '  class V1,V2,V3 setV;'
        ),
        'nodes': [
            {'id': 'U1', 'x': 140, 'y': 80, 'label': 'U1', 'color': '#4f46e5'},
            {'id': 'U2', 'x': 140, 'y': 160, 'label': 'U2', 'color': '#4f46e5'},
            {'id': 'U3', 'x': 140, 'y': 240, 'label': 'U3', 'color': '#4f46e5'},
            {'id': 'V1', 'x': 380, 'y': 80, 'label': 'V1', 'color': '#10b981'},
            {'id': 'V2', 'x': 380, 'y': 160, 'label': 'V2', 'color': '#10b981'},
            {'id': 'V3', 'x': 380, 'y': 240, 'label': 'V3', 'color': '#10b981'}
        ],
        'edges': [
            {'from': 'U1', 'to': 'V1', 'label': '', 'color': '#6366f1', 'directed': False},
            {'from': 'U1', 'to': 'V2', 'label': '', 'color': '#6366f1', 'directed': False},
            {'from': 'U2', 'to': 'V2', 'label': '', 'color': '#6366f1', 'directed': False},
            {'from': 'U3', 'to': 'V3', 'label': '', 'color': '#6366f1', 'directed': False}
        ]
    }
}


def parse_mermaid_from_text(text):
    """Extrai blocos Mermaid de texto gerado."""
    match = re.search(r'```(?:mermaid)?\s*\n(.*?)```', text, re.S)
    if match:
        code = match.group(1).strip()
        # Higieniza rótulos com parênteses
        code = re.sub(r'\[([^\n"\]]*\([^\n"\]]*\)[^\n"\]]*)\]', r'["\1"]', code)
        return code
    return None


def generate_ai_whiteboard_diagram(llm, prompt_text, topic='graph'):
    """Solicita ao modelo de IA a criação de um diagrama esquemático para o quadro branco."""
    system_instruction = (
        "Você é um tutor especialista em programação competitiva e estruturas de dados. "
        "Sua tarefa é criar visualizações esquemáticas e diagramas didáticos para o Quadro Branco do aluno. "
        "Responda SEMPRE em português do Brasil.\n"
        "REGRAS OBRIGATÓRIAS:\n"
        "1. Comece com uma breve explicação teórica e conceitual (2 a 4 parágrafos focados em intuição e invariantes).\n"
        "2. Inclua OBRIGATORIAMENTE um diagrama completo em bloco ```mermaid (graph TD ou graph LR) "
        "ilustrando a estrutura exata com rótulos entre aspas (ex.: N1[\"1 (raiz)\"] --> N2[\"2\"]).\n"
        "3. Se o assunto for grafos ou árvores, diferencie claramente os tipos de arestas ou níveis.\n"
        "4. Inclua uma lista de nós com seus papéis e um exercício rápido de rastreamento para o aluno desenhar no quadro.\n"
        "5. NÃO gere código completo de programa (sem #include, sem main)."
    )

    full_prompt = (
        f"PEDIDO DO ALUNO PARA O QUADRO BRANCO:\n{prompt_text}\n\n"
        f"Gere uma explicação visual aprofundada com diagrama Mermaid estruturado para projeção na lousa."
    )

    response = llm.complete(system_instruction, full_prompt, include_history=False)
    if not response:
        # Fallback local com base no tópico
        preset = WHITEBOARD_PRESETS.get('dag')
        if any(w in prompt_text.lower() for w in ('ciclo', 'cycle', 'back')):
            preset = WHITEBOARD_PRESETS.get('cycle')
        elif any(w in prompt_text.lower() for w in ('arvore', 'árvore', 'tree', 'binar')):
            preset = WHITEBOARD_PRESETS.get('tree')
        elif any(w in prompt_text.lower() for w in ('bfs', 'distancia', 'camada', 'largura')):
            preset = WHITEBOARD_PRESETS.get('bfs_layers')
        elif any(w in prompt_text.lower() for w in ('bipart', 'coloracao', 'dois conjuntos')):
            preset = WHITEBOARD_PRESETS.get('bipartite')

        return {
            'text': f"### {preset['title']}\n\n{preset['description']}\n\n```mermaid\n{preset['mermaid']}\n```",
            'mermaid': preset['mermaid'],
            'preset': preset
        }

    mermaid_code = parse_mermaid_from_text(response)
    if not mermaid_code:
        # Se o modelo esqueceu de colocar bloco mermaid, gera um diagrama padrão
        mermaid_code = WHITEBOARD_PRESETS['dag']['mermaid']

    if 'ciclo' in prompt_text.lower() and 'Ciclo na DFS' not in response and 'CICLO' not in mermaid_code.upper():
        response = f"### Ciclo na DFS e Arestas de Retorno (Back Edges)\n\n{response}"

    return {
        'text': response,
        'mermaid': mermaid_code,
        'preset': None
    }


def analyze_board_structure(llm, user_notes, board_state=None):
    """Analisa a estrutura desenhada pelo aluno no quadro branco."""
    system_instruction = (
        "Você é um tutor e juiz de programação competitiva analisando o rascunho de um aluno no quadro branco. "
        "Analise os elementos, verifique consistência algorítmica (ex.: é DAG? Tem ciclos? Bipartição? Altura equilibrada?), "
        "indique erros comuns de maratona e proponha o algoritmo ideal com sua complexidade assintótica."
    )
    prompt = (
        f"DESCRIÇÃO DO RASCUNHO FEITO PELO ALUNO NO QUADRO:\n{user_notes}\n\n"
        "Forneça um feedback pedagógico estruturado:\n"
        "1. Propriedades Estruturais Detectadas\n"
        "2. Validação da Modelagem (Pontos fortes e possíveis armadilhas/ciclos indesejados)\n"
        "3. Algoritmo Recomendado e Complexidade Esperada (Tempo e Memória)\n"
        "4. Dica de Próximo Passo para Implementação em C++."
    )
    res = llm.complete(system_instruction, prompt, include_history=False)
    return res or "Não foi possível conectar ao assistente de IA no momento. Revise os nós e tente novamente."


def parse_graph_from_text(raw_text, preset_name=None):
    """Extrai nós e arestas de uma lista de adjacência/pares de arestas ou usa preset."""
    if not raw_text or not raw_text.strip():
        if preset_name and preset_name in WHITEBOARD_PRESETS:
            p = WHITEBOARD_PRESETS[preset_name]
            return {
                'nodes': [dict(n) for n in p['nodes']],
                'edges': [dict(e) for e in p['edges']]
            }
        raw_text = "1 2\n1 3\n2 4\n3 4"

    lines = [l.strip() for l in raw_text.strip().splitlines() if l.strip() and not l.strip().startswith('#')]
    parsed_edges = []
    node_set = []

    def add_node(nid):
        if nid not in node_set:
            node_set.append(nid)

    for line in lines:
        parts = re.split(r'[\s,\->]+', line)
        parts = [p.strip() for p in parts if p.strip()]
        if len(parts) >= 2:
            u, v = parts[0], parts[1]
            weight = parts[2] if len(parts) > 2 else ''
            add_node(u)
            add_node(v)
            parsed_edges.append({
                'from': u,
                'to': v,
                'label': str(weight) if weight else '',
                'color': '#4f46e5',
                'directed': True
            })

    n = len(node_set)
    nodes = []
    center_x, center_y = 260, 200
    radius = min(170, max(80, 28 * n))
    colors = ['#4f46e5', '#06b6d4', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899']

    for i, nid in enumerate(node_set):
        angle = (2 * math.pi * i) / max(1, n) - (math.pi / 2)
        x = round(center_x + radius * math.cos(angle))
        y = round(center_y + radius * math.sin(angle))
        nodes.append({
            'id': nid,
            'x': x,
            'y': y,
            'label': str(nid),
            'color': colors[i % len(colors)]
        })

    return {'nodes': nodes, 'edges': parsed_edges}


def generate_algorithm_execution_tape(code_text, nodes, edges, start_node=None, max_steps=500):
    """Executa a simulação didática do algoritmo gerando uma fita de snapshots determinística."""
    node_ids = [n['id'] for n in nodes]
    if not node_ids:
        return []

    if not start_node or start_node not in node_ids:
        start_node = node_ids[0]

    adj = {nid: [] for nid in node_ids}
    for e in edges:
        u, v = e['from'], e['to']
        if u in adj and v in node_ids:
            adj[u].append(v)
        if not e.get('directed', True):
            if v in adj and u in node_ids:
                adj[v].append(u)

    code_lower = (code_text or '').lower()
    is_bfs = any(k in code_lower for k in ('bfs', 'queue', 'fila', 'pop(0)', 'popleft', 'deque'))

    steps = []
    node_states = {nid: 'unvisited' for nid in node_ids}
    edge_states = {f"{e['from']}-{e['to']}": 'normal' for e in edges}
    visited = {nid: False for nid in node_ids}
    call_stack = []
    queue = []

    def emit(line, active_node, active_edge, log_msg):
        if len(steps) >= max_steps:
            return
        steps.append({
            'step_index': len(steps),
            'line': line,
            'active_node': active_node,
            'active_edge': active_edge,
            'node_states': dict(node_states),
            'edge_states': dict(edge_states),
            'call_stack': list(call_stack),
            'queue': list(queue),
            'visited': dict(visited),
            'log': log_msg
        })

    if is_bfs:
        queue.append(start_node)
        visited[start_node] = True
        node_states[start_node] = 'visiting'
        emit(1, start_node, None, f"Iniciando BFS a partir da origem {start_node}. Enfileirado na FIFO.")

        while queue and len(steps) < max_steps:
            u = queue.pop(0)
            node_states[u] = 'visiting'
            emit(3, u, None, f"Desenfileirando nó {u}. Explorando vizinhos da camada.")

            for v in adj.get(u, []):
                if len(steps) >= max_steps:
                    break
                edge_key = f"{u}-{v}"
                emit(4, u, edge_key, f"Avaliando aresta ({u} -> {v}).")
                if not visited[v]:
                    visited[v] = True
                    node_states[v] = 'visiting'
                    edge_states[edge_key] = 'traversed'
                    queue.append(v)
                    emit(5, v, edge_key, f"Vizinho {v} não visitado. Marcado como visitado no push e enfileirado.")
                else:
                    emit(6, v, edge_key, f"Vizinho {v} já visitado. Ignorando re-inserção.")
            node_states[u] = 'visited'
            emit(7, u, None, f"Todos os vizinhos de {u} foram processados. Nó {u} concluído.")
    else:
        in_stack = {nid: False for nid in node_ids}

        def dfs(u, depth=0):
            if len(steps) >= max_steps:
                return
            call_stack.append(f"dfs({u})")
            visited[u] = True
            in_stack[u] = True
            node_states[u] = 'visiting'
            emit(1, u, None, f"Invocando dfs({u}) [Call Stack profundidade {depth}].")
            emit(2, u, None, f"visited[{u}] = True. in_stack[{u}] = True.")

            for v in adj.get(u, []):
                if len(steps) >= max_steps:
                    break
                edge_key = f"{u}-{v}"
                emit(3, u, edge_key, f"Avaliando vizinho {v} de {u}.")
                if not visited[v]:
                    edge_states[edge_key] = 'traversed'
                    emit(4, v, edge_key, f"Avançando pela aresta de árvore ({u} -> {v}).")
                    dfs(v, depth + 1)
                    node_states[u] = 'visiting'
                    emit(5, u, None, f"Retorno da chamada recursiva para o nó {u}.")
                elif in_stack.get(v, False):
                    edge_states[edge_key] = 'back_edge'
                    emit(6, v, edge_key, f"ALERTA: Ciclo detectado! Aresta de retorno ({u} -> {v}) aponta para nó na pilha.")
                else:
                    emit(7, v, edge_key, f"Aresta cruzada ({u} -> {v}). Nó {v} já finalizado.")

            in_stack[u] = False
            node_states[u] = 'visited'
            if call_stack:
                call_stack.pop()
            emit(8, u, None, f"Desempilhando dfs({u}). Processamento concluído.")

        dfs(start_node)

    unvisited_nodes = [str(nid) for nid in node_ids if not visited.get(nid, False)]
    if unvisited_nodes:
        emit(1, None, None, f"⚠️ Componente desconexo detectado: nós {', '.join(unvisited_nodes)} não foram alcançados a partir da raiz '{start_node}'. O grafo possui mais de uma componente conexa.")

    if len(steps) >= max_steps:
        emit(1, None, None, f"⚠️ Limite de segurança de {max_steps} passos atingido.")

    return steps



def generate_whiteboard_from_prompt(
    prompt: str,
    current_nodes: list = None,
    current_edges: list = None,
    llm = None
) -> dict:
    """Gera topologia de nós, arestas e código C++ a partir de prompt em linguagem natural."""
    p_lower = prompt.lower().strip()

    # 0. Árvore Binária de Busca (BST) com Busca Binária
    if any(k in p_lower for k in ["busca binária", "busca binaria", "bst", "binary search tree", "árvore de busca", "arvore de busca"]):
        nodes = [
            {"id": "20", "label": "20 (Raiz)", "x": 300, "y": 60, "color": "#f59e0b"},
            {"id": "10", "label": "10", "x": 180, "y": 160, "color": "#4f46e5"},
            {"id": "30", "label": "30", "x": 420, "y": 160, "color": "#4f46e5"},
            {"id": "5", "label": "5", "x": 120, "y": 270, "color": "#06b6d4"},
            {"id": "15", "label": "15", "x": 240, "y": 270, "color": "#06b6d4"},
            {"id": "25", "label": "25 (Alvo)", "x": 360, "y": 270, "color": "#10b981"},
            {"id": "35", "label": "35", "x": 480, "y": 270, "color": "#06b6d4"}
        ]
        edges = [
            {"id": "e20-10", "from": "20", "to": "10", "directed": True, "label": "< 20"},
            {"id": "e20-30", "from": "20", "to": "30", "directed": True, "label": "> 20"},
            {"id": "e10-5", "from": "10", "to": "5", "directed": True, "label": "< 10"},
            {"id": "e10-15", "from": "10", "to": "15", "directed": True, "label": "> 10"},
            {"id": "e30-25", "from": "30", "to": "25", "directed": True, "label": "< 30"},
            {"id": "e30-35", "from": "30", "to": "35", "directed": True, "label": "> 30"}
        ]
        cpp_code = """#include <iostream>
using namespace std;

// Busca Binária em Árvore Binária de Busca (BST)
// Alvo a ser encontrado: target = 25
bool searchBST(int u, int target) {
    if (u == 0) return false;      // Caso base: nó nulo (valor não encontrado)
    if (u == target) return true;  // Caso base: alvo encontrado com sucesso!

    if (target < u) {
        // Alvo é menor que o nó atual: desce para a subárvore esquerda
        return searchBST(left_child[u], target);
    } else {
        // Alvo é maior que o nó atual: desce para a subárvore direita
        return searchBST(right_child[u], target);
    }
}"""
        return {
            "title": "Árvore Binária de Busca (BST) · Busca Binária do Valor 25",
            "algorithm": "bst",
            "nodes": nodes,
            "edges": edges,
            "cpp_code": cpp_code,
            "explanation": "BST balanceada com 7 chaves. Ao buscar 25: inicia em 20 (25 > 20, vai p/ dir), chega em 30 (25 < 30, vai p/ esq), encontra 25 em O(log N) passos!"
        }

    # 1. Árvore Binária / Balanceada
    if any(k in p_lower for k in ["árvore", "arvore", "tree", "binária", "binaria"]):
        nodes = [
            {"id": "1", "label": "Raiz (1)", "x": 300, "y": 60, "color": "#f59e0b"},
            {"id": "2", "label": "2", "x": 180, "y": 160, "color": "#4f46e5"},
            {"id": "3", "label": "3", "x": 420, "y": 160, "color": "#4f46e5"},
            {"id": "4", "label": "4", "x": 120, "y": 270, "color": "#06b6d4"},
            {"id": "5", "label": "5", "x": 240, "y": 270, "color": "#06b6d4"},
            {"id": "6", "label": "6", "x": 360, "y": 270, "color": "#06b6d4"},
            {"id": "7", "label": "7", "x": 480, "y": 270, "color": "#06b6d4"}
        ]
        edges = [
            {"id": "e1-2", "from": "1", "to": "2", "directed": True, "label": "esq"},
            {"id": "e1-3", "from": "1", "to": "3", "directed": True, "label": "dir"},
            {"id": "e2-4", "from": "2", "to": "4", "directed": True, "label": "esq"},
            {"id": "e2-5", "from": "2", "to": "5", "directed": True, "label": "dir"},
            {"id": "e3-6", "from": "3", "to": "6", "directed": True, "label": "esq"},
            {"id": "e3-7", "from": "3", "to": "7", "directed": True, "label": "dir"}
        ]
        cpp_code = """#include <iostream>
#include <vector>
using namespace std;

void dfs_tree(int u, int p, const vector<vector<int>>& adj) {
    cout << "Visitando nó " << u << " (pai: " << p << ")\\n";
    for (int v : adj[u]) {
        if (v != p) {
            dfs_tree(v, u, adj);
        }
    }
}"""
        return {
            "title": "Árvore Binária Balanceada",
            "algorithm": "dfs",
            "nodes": nodes,
            "edges": edges,
            "cpp_code": cpp_code,
            "explanation": "Árvore com 7 nós e altura 2. Observe a ausência de ciclos e o caminho único entre a raiz e qualquer folha."
        }

    # 2. Grafo Bipartido
    elif any(k in p_lower for k in ["bipartido", "bipartite", "2-color", "coloração"]):
        nodes = [
            {"id": "1", "label": "A1", "x": 160, "y": 80, "color": "#3b82f6"},
            {"id": "2", "label": "A2", "x": 160, "y": 180, "color": "#3b82f6"},
            {"id": "3", "label": "A3", "x": 160, "y": 280, "color": "#3b82f6"},
            {"id": "4", "label": "B1", "x": 440, "y": 80, "color": "#ec4899"},
            {"id": "5", "label": "B2", "x": 440, "y": 180, "color": "#ec4899"},
            {"id": "6", "label": "B3", "x": 440, "y": 280, "color": "#ec4899"}
        ]
        edges = [
            {"id": "e1-4", "from": "1", "to": "4", "directed": False, "label": ""},
            {"id": "e1-5", "from": "1", "to": "5", "directed": False, "label": ""},
            {"id": "e2-5", "from": "2", "to": "5", "directed": False, "label": ""},
            {"id": "e2-6", "from": "2", "to": "6", "directed": False, "label": ""},
            {"id": "e3-4", "from": "3", "to": "4", "directed": False, "label": ""},
            {"id": "e3-6", "from": "3", "to": "6", "directed": False, "label": ""},
        ]
        cpp_code = """#include <iostream>
#include <vector>
#include <queue>
using namespace std;

bool check_bipartite(int start, int n, const vector<vector<int>>& adj) {
    vector<int> color(n + 1, -1);
    queue<int> q;
    color[start] = 0;
    q.push(start);

    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int v : adj[u]) {
            if (color[v] == -1) {
                color[v] = 1 - color[u];
                q.push(v);
            } else if (color[v] == color[u]) {
                return false; // Conflito: aresta interna no mesmo conjunto!
            }
        }
    }
    return true;
}"""
        return {
            "title": "Grafo Bipartido K3,3",
            "algorithm": "bfs",
            "nodes": nodes,
            "edges": edges,
            "cpp_code": cpp_code,
            "explanation": "Conjuntos disjuntos A (azul) e B (rosa). Não existem arestas entre nós da mesma cor."
        }

    # 3. Grafo Ponderado / Dijkstra
    elif any(k in p_lower for k in ["dijkstra", "peso", "ponderado", "caminho mínimo", "shortest"]):
        nodes = [
            {"id": "1", "label": "Origem (1)", "x": 100, "y": 180, "color": "#10b981"},
            {"id": "2", "label": "2", "x": 260, "y": 80, "color": "#4f46e5"},
            {"id": "3", "label": "3", "x": 260, "y": 280, "color": "#4f46e5"},
            {"id": "4", "label": "4", "x": 420, "y": 80, "color": "#06b6d4"},
            {"id": "5", "label": "Destino (5)", "x": 520, "y": 180, "color": "#f59e0b"}
        ]
        edges = [
            {"id": "e1-2", "from": "1", "to": "2", "directed": True, "label": "4", "weight": 4},
            {"id": "e1-3", "from": "1", "to": "3", "directed": True, "label": "2", "weight": 2},
            {"id": "e3-2", "from": "3", "to": "2", "directed": True, "label": "1", "weight": 1},
            {"id": "e2-4", "from": "2", "to": "4", "directed": True, "label": "5", "weight": 5},
            {"id": "e3-5", "from": "3", "to": "5", "directed": True, "label": "8", "weight": 8},
            {"id": "e4-5", "from": "4", "to": "5", "directed": True, "label": "2", "weight": 2}
        ]
        cpp_code = """#include <iostream>
#include <vector>
#include <queue>
using namespace std;

const int INF = 1e9;

void dijkstra(int s, int n, const vector<vector<pair<int,int>>>& adj) {
    vector<int> dist(n + 1, INF);
    dist[s] = 0;
    priority_queue<pair<int,int>, vector<pair<int,int>>, greater<pair<int,int>>> pq;
    pq.push({0, s});

    while (!pq.empty()) {
        auto [d, u] = pq.top(); pq.pop();
        if (d > dist[u]) continue;
        for (auto [v, w] : adj[u]) {
            if (dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
                pq.push({dist[v], v});
            }
        }
    }
}"""
        return {
            "title": "Grafo com Pesos Positivos (Dijkstra)",
            "algorithm": "dijkstra",
            "nodes": nodes,
            "edges": edges,
            "cpp_code": cpp_code,
            "explanation": "Grafo ponderado para demonstrar relaxamento guloso com priority_queue em C++. O caminho mínimo 1 -> 5 custa 2+1+5+2 = 10 ou 1->3->5 = 10."
        }

    # 4. Detecção de Ciclo / Ponte
    elif any(k in p_lower for k in ["ciclo", "cycle", "ponte", "bridge", "tarjan"]):
        nodes = [
            {"id": "1", "label": "1", "x": 140, "y": 160, "color": "#4f46e5"},
            {"id": "2", "label": "2", "x": 260, "y": 80, "color": "#4f46e5"},
            {"id": "3", "label": "3", "x": 260, "y": 240, "color": "#4f46e5"},
            {"id": "4", "label": "Ponte (4)", "x": 400, "y": 160, "color": "#ef4444"},
            {"id": "5", "label": "5", "x": 520, "y": 160, "color": "#10b981"}
        ]
        edges = [
            {"id": "e1-2", "from": "1", "to": "2", "directed": True, "label": "tree"},
            {"id": "e2-3", "from": "2", "to": "3", "directed": True, "label": "tree"},
            {"id": "e3-1", "from": "3", "to": "1", "directed": True, "label": "back (ciclo)", "color": "#ef4444"},
            {"id": "e2-4", "from": "2", "to": "4", "directed": True, "label": "ponte", "color": "#f59e0b"},
            {"id": "e4-5", "from": "4", "to": "5", "directed": True, "label": "tree"}
        ]
        cpp_code = """#include <iostream>
#include <vector>
using namespace std;

void find_cycles(int u, const vector<vector<int>>& adj, vector<int>& state) {
    // 0: nao visitado, 1: na pilha (cinza), 2: concluido (preto)
    state[u] = 1;
    for (int v : adj[u]) {
        if (state[v] == 1) {
            cout << "Ciclo detectado na aresta " << u << " -> " << v << "\\n";
        } else if (state[v] == 0) {
            find_cycles(v, adj, state);
        }
    }
    state[u] = 2;
}"""
        return {
            "title": "Grafo com Ciclo e Aresta Ponte",
            "algorithm": "dfs",
            "nodes": nodes,
            "edges": edges,
            "cpp_code": cpp_code,
            "explanation": "O componente {1, 2, 3} contém ciclo fechado pela back-edge (3 -> 1). A aresta (2 -> 4) é uma ponte articulada."
        }

    # 5. Default: Grafo Canônico de Exploração
    nodes = [
        {"id": "1", "label": "1", "x": 120, "y": 160, "color": "#4f46e5"},
        {"id": "2", "label": "2", "x": 260, "y": 80, "color": "#4f46e5"},
        {"id": "3", "label": "3", "x": 260, "y": 240, "color": "#4f46e5"},
        {"id": "4", "label": "4", "x": 400, "y": 80, "color": "#06b6d4"},
        {"id": "5", "label": "5", "x": 400, "y": 240, "color": "#06b6d4"},
        {"id": "6", "label": "6", "x": 520, "y": 160, "color": "#10b981"}
    ]
    edges = [
        {"id": "e1-2", "from": "1", "to": "2", "directed": True, "label": ""},
        {"id": "e1-3", "from": "1", "to": "3", "directed": True, "label": ""},
        {"id": "e2-4", "from": "2", "to": "4", "directed": True, "label": ""},
        {"id": "e3-5", "from": "3", "to": "5", "directed": True, "label": ""},
        {"id": "e4-6", "from": "4", "to": "6", "directed": True, "label": ""},
        {"id": "e5-6", "from": "5", "to": "6", "directed": True, "label": ""}
    ]
    cpp_code = """#include <iostream>
#include <vector>
#include <queue>
using namespace std;

void traverse_graph(int start, int n, const vector<vector<int>>& adj) {
    vector<bool> vis(n + 1, false);
    queue<int> q;
    vis[start] = true;
    q.push(start);
    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int v : adj[u]) {
            if (!vis[v]) {
                vis[v] = true;
                q.push(v);
            }
        }
    }
}"""
    return {
        "title": f"Topologia Gerada: {prompt[:30]}",
        "algorithm": "bfs",
        "nodes": nodes,
        "edges": edges,
        "cpp_code": cpp_code,
        "explanation": f"Grafo customizado gerado para a instrução: '{prompt}'."
    }
