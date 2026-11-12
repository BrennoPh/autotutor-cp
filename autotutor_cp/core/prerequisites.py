"""Pedagogical scaffolding and prerequisite detection for competitive programming topics."""
import re
from html import escape


PREREQUISITES_MAP = {
    'bfs_dfs': {
        'id': 'queue_stack',
        'title': 'Fila (Queue) e Pilha (Stack)',
        'description': (
            'Estruturas lineares fundamentais para navegar em estados e grafos. '
            'A Fila (FIFO) governa a Busca em Largura (BFS) para exploração em camadas de distância mínima. '
            'A Pilha (LIFO / recursão) governa a Busca em Profundidade (DFS) para rastrear caminhos e componentes.'
        ),
        'keywords': ['bfs', 'dfs', 'busca em largura', 'busca em profundidade', 'fila', 'pilha', 'breadth', 'depth', 'ordem topologica', 'topological', 'grafo', 'graph', 'componente'],
        'items': [
            {
                'name': 'Fila (Queue - FIFO: First-In, First-Out)',
                'summary': 'O primeiro elemento a entrar é o primeiro a sair (como uma fila de banco). Ao visitar um nó na BFS, enfileiramos seus vizinhos. Isso garante que todos os nós de distância 1 sejam processados antes dos de distância 2.',
                'operations': 'push(x) insere no fim; pop() remove do início; front() consulta o início. Todas em O(1).',
                'cpp_snippet': 'std::queue<int> q;\nq.push(origem);\nwhile(!q.empty()) {\n    int u = q.front(); q.pop();\n    // visita vizinhos de u\n}'
            },
            {
                'name': 'Pilha (Stack - LIFO: Last-In, First-Out) e Recursão',
                'summary': 'O último elemento a entrar é o primeiro a sair (como uma pilha de pratos). Na DFS recursiva, a pilha de execução (call stack) do sistema guarda os vértices ancestrais. Para desempilhar, a função precisa terminar a exploração dos filhos.',
                'operations': 'push(x) insere no topo; pop() remove do topo; top() consulta o topo. Todas em O(1).',
                'cpp_snippet': 'void dfs(int u) {\n    visitado[u] = true;\n    for (int v : adj[u])\n        if (!visitado[v]) dfs(v);\n}'
            }
        ],
        'diagram': (
            'graph TD\n'
            '  subgraph Fila_FIFO ["Fila (FIFO) na BFS: Primeiro a entrar, primeiro a sair"]\n'
            '    F1["Frente: Sai 1"] --> F2["2"] --> F3["Fundo: Entra 3"]\n'
            '  end\n'
            '  subgraph Pilha_LIFO ["Pilha (LIFO) na DFS: Último a entrar, primeiro a sair"]\n'
            '    P3["Topo: Entra e Sai 3"] --> P2["2"] --> P1["Base: 1"]\n'
            '  end'
        )
    },
    'dijkstra': {
        'id': 'priority_queue',
        'title': 'Fila de Prioridade (Heap) e Grafos Ponderados',
        'description': (
            'Para encontrar o menor caminho com pesos arbitrários não-negativos, a BFS simples falha. '
            'É indispensável dominar a Fila de Prioridade (Min-Heap) para extrair o próximo vértice ótimo em O(log V).'
        ),
        'keywords': ['dijkstra', 'caminho minimo ponderado', 'shortest path', 'heap', 'priority queue', 'fila de prioridade', 'peso'],
        'items': [
            {
                'name': 'Fila de Prioridade (Min-Heap)',
                'summary': 'Estrutura que mantém os elementos ordenados por custo. Em vez de FIFO comum, sai sempre o par {distancia, vertice} com menor valor acumulado.',
                'operations': 'push() insere em O(log N); pop() remove o topo em O(log N); top() consulta o menor em O(1).',
                'cpp_snippet': 'priority_queue<pair<int,int>, vector<pair<int,int>>, greater<pair<int,int>>> pq;\npq.push({0, origem});'
            }
        ],
        'diagram': (
            'graph TD\n'
            '  R["Topo: Menor Distância {d=2, u=A}"] --> H1["{d=5, u=B}"]\n'
            '  R --> H2["{d=8, u=C}"]\n'
            '  classDef heap fill:#fef3c7,stroke:#f59e0b,stroke-width:2px,color:#78350f;\n'
            '  class R,H1,H2 heap;'
        )
    },
    'dp': {
        'id': 'recursion_memo',
        'title': 'Recursão, Subproblemas e Memorização',
        'description': (
            'Programação Dinâmica é a otimização de uma recursão que calcula os mesmos estados várias vezes. '
            'Os pré-requisitos essenciais são definir os estados claramente e armazenar respostas parciais em um vetor ou matriz (memoization/tabulation).'
        ),
        'keywords': ['dp', 'programacao dinamica', 'dinamica', 'knapsack', 'mochila', 'memorizacao', 'memoization', 'subestrutura'],
        'items': [
            {
                'name': 'Subproblemas Sobrepostos e Tabela de Estados',
                'summary': 'Se uma função f(n) chama f(n-1) e f(n-2), a árvore cresce exponencialmente O(2^N). Ao guardar memo[n], cada subproblema é resolvido apenas 1 vez, reduzindo para O(N).',
                'operations': 'Consultar memo[n]: se já calculado (diferente de -1), retorne instantaneamente em O(1).',
                'cpp_snippet': 'int memo[MAXN];\nint solve(int n) {\n    if (n <= 1) return n;\n    if (memo[n] != -1) return memo[n];\n    return memo[n] = solve(n-1) + solve(n-2);\n}'
            }
        ],
        'diagram': (
            'graph TD\n'
            '  F4["fib(4)"] --> F3["fib(3)"]\n'
            '  F4 -.->|Subproblema repetido!| F2a["fib(2)"]\n'
            '  F3 --> F2b["fib(2) [calculado uma vez]"]\n'
            '  F3 --> F1["fib(1)"]\n'
            '  classDef rep fill:#fee2e2,stroke:#ef4444,stroke-width:2px,color:#7f1d1d;\n'
            '  class F2a rep;'
        )
    },
    'segtree': {
        'id': 'binary_tree_dac',
        'title': 'Árvore Binária e Divisão e Conquista',
        'description': (
            'A Segment Tree organiza um vetor em uma árvore binária onde cada nó representa um intervalo [L, R]. '
            'O pré-requisito é entender como dividir intervalos pela metade e combinar as respostas dos filhos esquerdo e direito.'
        ),
        'keywords': ['segment tree', 'segtree', 'arvore de segmentos', 'fenwick', 'bit'],
        'items': [
            {
                'name': 'Divisão e Conquista em Intervalos',
                'summary': 'O nó raiz cobre [1, N]. Seu filho esquerdo cobre [1, N/2] e o direito [N/2 + 1, N]. Consultas e atualizações descem pela árvore em O(log N).',
                'operations': 'mid = (L + R) / 2; no_esq = 2 * no; no_dir = 2 * no + 1;',
                'cpp_snippet': 'void update(int no, int l, int r, int idx, int val) {\n    if (l == r) { tree[no] = val; return; }\n    int mid = (l + r) / 2;\n    if (idx <= mid) update(2*no, l, mid, idx, val);\n    else update(2*no+1, mid+1, r, idx, val);\n    tree[no] = tree[2*no] + tree[2*no+1];\n}'
            }
        ],
        'diagram': (
            'graph TD\n'
            '  R["[1, 4]"] --> L["[1, 2]"]\n'
            '  R --> D["[3, 4]"]\n'
            '  L --> L1["[1, 1]"]\n'
            '  L --> L2["[2, 2]"]\n'
            '  D --> D1["[3, 3]"]\n'
            '  D --> D2["[4, 4]"]'
        )
    }
}


def detect_prerequisites(request_text='', concept=''):
    """Identifica quais pré-requisitos fundamentais são relevantes para o pedido."""
    combined = (str(request_text) + ' ' + str(concept)).lower()
    matches = []
    for key, spec in PREREQUISITES_MAP.items():
        if any(re.search(r'\b' + re.escape(kw) + r'\b', combined) for kw in spec['keywords']):
            matches.append(spec)
    return matches


def build_prerequisite_primer_markdown(prereq_spec):
    """Gera uma seção didática completa explicando os pré-requisitos antes do tópico principal."""
    parts = [
        f"## 0. Nivelamento Obrigatório de Pré-Requisitos: {prereq_spec['title']}",
        prereq_spec['description'],
        "\n### Estrutura Visual dos Conceitos Base",
        f"```mermaid\n{prereq_spec['diagram']}\n```\n"
    ]

    for item in prereq_spec['items']:
        parts.append(f"### {item['name']}")
        parts.append(item['summary'])
        parts.append(f"**Operações principais:** {item['operations']}")
        parts.append("```cpp\n" + item['cpp_snippet'] + "\n```")

    parts.append(
        "\n> **Transição para o Tópico Avançado:** Agora que as estruturas fundamentais e suas invariantes operacionais "
        "estão fixadas, podemos avançar com segurança para a aplicação completa abaixo.\n"
    )
    return '\n\n'.join(parts)


def format_prerequisite_instructions_for_ai(prereq_spec, user_decision='explain'):
    """Cria a diretriz explícita para o modelo de IA sobre como lidar com pré-requisitos."""
    if user_decision == 'explain':
        items_str = ', '.join(i['name'] for i in prereq_spec['items'])
        return (
            f"\nNIVELAMENTO PEDAGÓGICO DE PRÉ-REQUISITOS (SOLICITADO PELO ALUNO):\n"
            f"- O aluno informou explicitamente que PRECISA REVISAR os pré-requisitos fundamentais: {items_str}.\n"
            f"- É MANDATÓRIO iniciar o material gerado com uma seção de nivelamento intitulada "
            f"'# Fundamentos e Pré-Requisitos: {prereq_spec['title']}'.\n"
            f"- Explique o que é cada uma dessas estruturas básicas do zero, com intuição visual, "
            f"a diferença crucial entre as operações (ex.: LIFO vs FIFO) e pequenos trechos em C++.\n"
            f"- Somente após essa fundamentação clara e completa, faça a transição para o assunto principal "
            f"(explicando exatamente como o algoritmo de busca ou técnica se apoia sobre essas estruturas).\n"
        )
    else:
        return (
            f"\nNIVELAMENTO PEDAGÓGICO (ALUNO CONFIRMOU DOMÍNIO):\n"
            f"- O aluno confirmou que já domina os pré-requisitos fundamentais ({prereq_spec['title']}).\n"
            f"- NÃO perca tempo definindo conceitos básicos ou operações triviais de pilha/fila isoladas.\n"
            f"- Vá DIRETAMENTE para a mecânica do algoritmo avançado, suas invariantes, análise de corretude, "
            f"árvore de busca e casos de borda de competição.\n"
        )
