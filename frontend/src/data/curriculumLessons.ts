import { StudyLesson } from "@/types/workspace";

export interface ExtendedLesson extends StudyLesson {
  category: string;
  whiteboardPreset?: {
    topic: string;
    algorithm: "dfs" | "bfs" | "dijkstra";
    cpp_code: string;
    nodes: Array<{ id: string; label: string; x: number; y: number; color?: string }>;
    edges: Array<{ id: string; from: string; to: string; directed: boolean; weight?: number; label?: string }>;
  };
}

export const CURRICULUM_LESSONS: ExtendedLesson[] = [
  {
    id: "bfs_dfs_foundations",
    category: "Grafos & Busca",
    topicId: "grafos",
    topicTitle: "Busca em Grafos",
    title: "Busca em Largura (BFS) e Busca em Profundidade (DFS) em C++",
    subtitle: "Navegação em estados, árvores de busca e estruturas STL (std::queue e recursão).",
    summary: "Entenda a mecânica da Fila FIFO e da Pilha de Recursão, classificação de arestas e invariantes em C++17.",
    estimatedReadingMinutes: 8,
    totalCharacters: 4200,
    whiteboardPreset: {
      topic: "Busca em Grafos",
      algorithm: "bfs",
      cpp_code: `#include <iostream>
#include <vector>
#include <queue>
using namespace std;

void bfs(int start, int n, const vector<vector<int>>& adj) {
    vector<bool> visited(n + 1, false);
    vector<int> dist(n + 1, -1);
    queue<int> q;

    visited[start] = true;
    dist[start] = 0;
    q.push(start);

    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int v : adj[u]) {
            if (!visited[v]) {
                visited[v] = true;
                dist[v] = dist[u] + 1;
                q.push(v);
            }
        }
    }
}`,
      nodes: [
        { id: "1", label: "Raiz (1)", x: 260, y: 70, color: "#10b981" },
        { id: "2", label: "2", x: 140, y: 160, color: "#4f46e5" },
        { id: "3", label: "3", x: 380, y: 160, color: "#4f46e5" },
        { id: "4", label: "4", x: 100, y: 260, color: "#06b6d4" },
        { id: "5", label: "5", x: 200, y: 260, color: "#06b6d4" },
        { id: "6", label: "6", x: 380, y: 260, color: "#06b6d4" }
      ],
      edges: [
        { id: "e1-2", from: "1", to: "2", directed: true },
        { id: "e1-3", from: "1", to: "3", directed: true },
        { id: "e2-4", from: "2", to: "4", directed: true },
        { id: "e2-5", from: "2", to: "5", directed: true },
        { id: "e3-6", from: "3", to: "6", directed: true }
      ]
    },
    sections: [
      {
        id: "sec-0",
        title: "0. Invariantes Lineares em C++: std::queue vs Call Stack",
        content: `Em C++, o controle de busca é estritamente tipado:
- **std::queue<int> (FIFO):** O primeiro nó inserido é o primeiro a ser expandido, garantindo caminhos mínimos em grafos não ponderados.
- **Pilha de Execução (Recursão DFS):** As chamadas recursivas empilham os estados na memória, aprofundando o caminho até o ponto cego antes do retrocesso (backtracking).`
      },
      {
        id: "sec-1",
        title: "1. Implementação C++ da Busca em Largura (BFS)",
        content: `A armadilha mais comum em maratonas de programação é marcar o vértice como visitado apenas ao retirá-lo da fila (pop), o que gera **Time Limit Exceeded (TLE)** ou **Memory Limit Exceeded (MLE)**.

\`\`\`cpp
// SEMPRE marque como visitado imediatamente ao enfileirar (push)!
visited[v] = true;
dist[v] = dist[u] + 1;
q.push(v);
\`\`\``
      }
    ]
  },
  {
    id: "dijkstra_shortest_path",
    category: "Caminhos Mínimos",
    topicId: "dijkstra",
    topicTitle: "Algoritmo de Dijkstra",
    title: "Caminho Mínimo com Algoritmo de Dijkstra em C++",
    subtitle: "Relaxamento guloso de arestas com std::priority_queue de complexidade O((V + E) log V).",
    summary: "Aprenda a encontrar o menor custo em grafos com pesos positivos utilizando fila de prioridade inversa em C++.",
    estimatedReadingMinutes: 10,
    totalCharacters: 4800,
    whiteboardPreset: {
      topic: "Caminho Mínimo (Dijkstra)",
      algorithm: "dijkstra",
      cpp_code: `#include <iostream>
#include <vector>
#include <queue>
using namespace std;

const int INF = 1e9;

void dijkstra(int s, int n, const vector<vector<pair<int, int>>>& adj) {
    vector<int> dist(n + 1, INF);
    dist[s] = 0;
    priority_queue<pair<int, int>, vector<pair<int, int>>, greater<pair<int, int>>> pq;
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
}`,
      nodes: [
        { id: "1", label: "Origem (1)", x: 100, y: 170, color: "#10b981" },
        { id: "2", label: "2", x: 260, y: 80, color: "#4f46e5" },
        { id: "3", label: "3", x: 260, y: 260, color: "#4f46e5" },
        { id: "4", label: "4", x: 420, y: 80, color: "#06b6d4" },
        { id: "5", label: "Destino (5)", x: 520, y: 170, color: "#f59e0b" }
      ],
      edges: [
        { id: "e1-2", from: "1", to: "2", directed: true, weight: 4, label: "4" },
        { id: "e1-3", from: "1", to: "3", directed: true, weight: 2, label: "2" },
        { id: "e3-2", from: "3", to: "2", directed: true, weight: 1, label: "1" },
        { id: "e2-4", from: "2", to: "4", directed: true, weight: 5, label: "5" },
        { id: "e3-5", from: "3", to: "5", directed: true, weight: 8, label: "8" },
        { id: "e4-5", from: "4", to: "5", directed: true, weight: 2, label: "2" }
      ]
    },
    sections: [
      {
        id: "dijk-0",
        title: "0. O Princípio da Otimização Gulosa",
        content: `O Algoritmo de Dijkstra seleciona repetidamente o vértice não finalizado com a menor distância estimada.
Em C++, implementamos um Min-Heap utilizando:

\`\`\`cpp
priority_queue<pair<int, int>, vector<pair<int, int>>, greater<pair<int, int>>> pq;
\`\`\`

Onde o primeiro elemento do par é a **distância acumulada** e o segundo é o **identificador do vértice**.`
      },
      {
        id: "dijk-1",
        title: "1. A Invariante de Relaxamento",
        content: `A aresta $(u, v)$ de peso $w$ é relaxada se:
$$\\text{dist}[v] > \\text{dist}[u] + w$$

**Atenção Crítica:** Dijkstra **não funciona com pesos negativos**. Para grafos com arestas negativas, utilize o Algoritmo de Bellman-Ford ou SPFA.`
      }
    ]
  },
  {
    id: "dsu_kruskal_mst",
    category: "Árvores & Grafos Avançados",
    topicId: "dsu",
    topicTitle: "Disjoint Set Union (DSU) & Kruskal",
    title: "Conjuntos Disjuntos (DSU) e Árvore Geradora Mínima (Kruskal)",
    subtitle: "Union-Find com compressão de caminho e união por rank em tempo quase linear O(α(N)).",
    summary: "Domine a estrutura de dados mais elegante de maratonas para agrupar componentes conexas e encontrar a AGM.",
    estimatedReadingMinutes: 9,
    totalCharacters: 4100,
    whiteboardPreset: {
      topic: "DSU & Kruskal",
      algorithm: "dfs",
      cpp_code: `#include <iostream>
#include <vector>
#include <numeric>
using namespace std;

struct DSU {
    vector<int> parent, rank;
    DSU(int n) : parent(n + 1), rank(n + 1, 0) {
        iota(parent.begin(), parent.end(), 0);
    }
    int find(int i) {
        if (parent[i] == i) return i;
        return parent[i] = find(parent[i]); // Compressao de caminho
    }
    bool unite(int i, int j) {
        int root_i = find(i), root_j = find(j);
        if (root_i != root_j) {
            if (rank[root_i] < rank[root_j]) swap(root_i, root_j);
            parent[root_j] = root_i;
            if (rank[root_i] == rank[root_j]) rank[root_i]++;
            return true;
        }
        return false;
    }
};`,
      nodes: [
        { id: "1", label: "1", x: 120, y: 100, color: "#3b82f6" },
        { id: "2", label: "2", x: 260, y: 100, color: "#3b82f6" },
        { id: "3", label: "3", x: 400, y: 100, color: "#ec4899" },
        { id: "4", label: "4", x: 120, y: 240, color: "#3b82f6" },
        { id: "5", label: "5", x: 260, y: 240, color: "#ec4899" }
      ],
      edges: [
        { id: "e1-2", from: "1", to: "2", directed: false, weight: 1, label: "1" },
        { id: "e1-4", from: "1", to: "4", directed: false, weight: 2, label: "2" },
        { id: "e3-5", from: "3", to: "5", directed: false, weight: 3, label: "3" },
        { id: "e2-5", from: "2", to: "5", directed: false, weight: 5, label: "5" }
      ]
    },
    sections: [
      {
        id: "dsu-0",
        title: "0. As Duas Operações Fundamentais",
        content: `O DSU mantém uma partição de um conjunto em componentes disjuntas:
1. **find(i):** Encontra o representante canônico do conjunto contendo $i$.
2. **unite(i, j):** Une os conjuntos de $i$ e $j$. Com compressão de caminho e união por rank, a complexidade amortizada por operação é $O(\\alpha(N))$, onde $\\alpha$ é a inversa da função de Ackermann (menor que 5 para qualquer entrada no universo).`
      }
    ]
  },
  {
    id: "dp_knapsack_foundations",
    category: "Programação Dinâmica",
    topicId: "dp",
    topicTitle: "Programação Dinâmica",
    title: "Programação Dinâmica: Problema da Mochila (0/1 Knapsack) em C++",
    subtitle: "Subproblemas sobrepostos, memoização, espaço O(W) e recuperação de escolhas.",
    summary: "Construa o raciocínio de transição de estados e elimine cálculos redundantes exponenciais.",
    estimatedReadingMinutes: 12,
    totalCharacters: 4600,
    whiteboardPreset: {
      topic: "Programação Dinâmica",
      algorithm: "dfs",
      cpp_code: `#include <iostream>
#include <vector>
using namespace std;

int knapsack(int W, const vector<int>& wt, const vector<int>& val, int n) {
    vector<int> dp(W + 1, 0);
    for (int i = 0; i < n; i++) {
        // Itera de tras para frente para nao usar o mesmo item multiplas vezes
        for (int w = W; w >= wt[i]; w--) {
            dp[w] = max(dp[w], dp[w - wt[i]] + val[i]);
        }
    }
    return dp[W];
}`,
      nodes: [
        { id: "1", label: "dp[0]", x: 80, y: 150, color: "#10b981" },
        { id: "2", label: "dp[w - wt[i]]", x: 240, y: 100, color: "#4f46e5" },
        { id: "3", label: "dp[w] anterior", x: 240, y: 200, color: "#06b6d4" },
        { id: "4", label: "dp[w] novo", x: 420, y: 150, color: "#f59e0b" }
      ],
      edges: [
        { id: "e2-4", from: "2", to: "4", directed: true, label: "+ val[i]" },
        { id: "e3-4", from: "3", to: "4", directed: true, label: "ignora" }
      ]
    },
    sections: [
      {
        id: "dp-0",
        title: "0. Subestrutura Ótima e Invariante de Decisão",
        content: `Para cada item $i$ com peso $w_i$ e valor $v_i$, tomamos a decisão binária de escolha:
- **Não colocar o item $i$:** O valor acumulado é $\\text{dp}[i-1][w]$.
- **Colocar o item $i$ (se $w \\ge w_i$):** O valor acumulado é $\\text{dp}[i-1][w - w_i] + v_i$.

A transição de estado canônica da Equação de Bellman é:
$$\\text{dp}[i][w] = \\max(\\text{dp}[i-1][w], \\text{dp}[i-1][w - w_i] + v_i)$$`
      },
      {
        id: "dp-1",
        title: "1. Tabela 2D vs Otimização de Espaço 1D em C++",
        content: `Em competições com limite estrito de memória (ex: 256MB), a matriz 2D $O(N \\times W)$ pode ser condensada em um único vetor de tamanho $W+1$.

**O Segredo da Iteração Reversa:**
Para evitar que o mesmo item seja reutilizado no mesmo estágio (o que transformaria o problema em Mochila Ilimitada), iteramos o laço de capacidades de trás para frente ($W \\to w_i$):

\`\`\`cpp
vector<int> dp(W + 1, 0);
for (int i = 0; i < n; i++) {
    for (int w = W; w >= wt[i]; w--) {
        dp[w] = max(dp[w], dp[w - wt[i]] + val[i]);
    }
}
\`\`\``
      },
      {
        id: "dp-2",
        title: "2. Variações Clássicas: Troco de Moedas e LCS",
        content: `A mesma intuição de subproblemas sobrepostos se aplica a:
- **Troco de Moedas (Coin Change):** $\\text{dp}[v] = \\min(\\text{dp}[v], \\text{dp}[v - c] + 1)$. Aqui iteramos para a frente ($c \\to V$) porque podemos usar moedas ilimitadas.
- **Maior Subsequência Comum (LCS):** Se $S_1[i] == S_2[j]$, estende a diagonal $+1$. Caso contrário, herda $\\max(\\text{dp}[i-1][j], \\text{dp}[i][j-1])$.`
      }
    ]
  },
  {
    id: "binary_search_foundations",
    category: "Busca & Otimização",
    topicId: "binary",
    topicTitle: "Busca Binária",
    title: "Busca Binária na Resposta e Predicados Monótonos em C++",
    subtitle: "Espaço de busca monótono, invariantes de ponteiros low/high e complexidade O(log N).",
    summary: "Aprenda a aplicar busca binária além de vetores ordenados: encontre a resposta ótima minimizando o máximo.",
    estimatedReadingMinutes: 8,
    totalCharacters: 3900,
    sections: [
      {
        id: "bin-0",
        title: "0. O Princípio do Predicado Monótono",
        content: `A busca binária clássica procura um valor em um vetor ordenado. Em maratona de programação, aplicamos **Busca Binária na Resposta**:
Se uma função booleana $\\text{check}(X)$ é monótona (por exemplo, $\\text{FF...FTT...T}$), podemos encontrar o primeiro valor verdadeiro em $O(\\log(\\text{high} - \\text{low}))$.

\`\`\`cpp
long long low = 1, high = 1e18, ans = -1;
while (low <= high) {
    long long mid = low + (high - low) / 2;
    if (check(mid)) {
        ans = mid;
        high = mid - 1; // Tenta encontrar valor ainda menor
    } else {
        low = mid + 1;
    }
}
\`\`\``
      },
      {
        id: "bin-1",
        title: "1. Aplicação Clássica: Divisão de Cargas e Capacidade Mínima",
        content: `No problema de particionamento contíguo (como *Carga das Naves*), a função $\\text{check}(C)$ testa se é possível alocar os elementos em até $K$ grupos onde nenhum grupo excede a capacidade $C$.
A verificação é gulosa em tempo linear $O(N)$, totalizando complexidade $O(N \\log(\\sum A_i))$.`
      }
    ]
  },
  {
    id: "greedy_foundations",
    category: "Algoritmos Gulosos",
    topicId: "greedy",
    topicTitle: "Algoritmos Gulosos",
    title: "Algoritmos Gulosos e Escalonamento de Intervalos em C++",
    subtitle: "Propriedade da escolha gulosa e subestrutura ótima sem backtracking.",
    summary: "Domine a ordenação estratégica por término de intervalos e provas de troca gulosa.",
    estimatedReadingMinutes: 7,
    totalCharacters: 3600,
    sections: [
      {
        id: "grd-0",
        title: "0. A Propriedade da Escolha Gulosa",
        content: `Um algoritmo guloso constrói uma solução passo a passo, escolhendo a melhor opção local sem nunca voltar atrás.
Para que funcione, o problema deve satisfazer o **Argumento de Troca (Exchange Argument)**: qualquer solução ótima pode ser transformada na solução gulosa sem perda de valor.`
      },
      {
        id: "grd-1",
        title: "1. Interval Scheduling (Agendamento de Eventos)",
        content: `Dados $N$ eventos com início $s_i$ e término $e_i$, maximize a quantidade de eventos compatíveis:
**Estratégia Ótima:** Ordene pelo **tempo de término** ($e_i$) crescente. Sempre selecione o evento que termina mais cedo e não colide com o anterior.

\`\`\`cpp
sort(events.begin(), events.end(), [](const auto& a, const auto& b) {
    return a.second < b.second; // Ordena por end_time
});
\`\`\``
      }
    ]
  },
  {
    id: "tree_foundations",
    category: "Árvores & Grafos",
    topicId: "tree",
    topicTitle: "Árvores",
    title: "Propriedades de Árvores, Travessias e Diâmetro em C++",
    subtitle: "Grafos conexos acíclicos com N-1 arestas, nós folhas e cálculo de diâmetro via dupla BFS.",
    summary: "Aprenda a encontrar a maior distância entre dois nós em uma árvore com duas travessias em O(N).",
    estimatedReadingMinutes: 8,
    totalCharacters: 3800,
    sections: [
      {
        id: "tree-0",
        title: "0. Invariantes de Árvores em Computação",
        content: `Uma árvore com $N$ vértices possui exatamente $N-1$ arestas e não tem ciclos. Entre quaisquer dois vértices existe um único caminho simples.
Para calcular o **Diâmetro** (maior caminho entre quaisquer dois nós):
1. Execute uma BFS a partir de qualquer vértice arbitrário (ex: vértice 1) e encontre o vértice mais distante $U$.
2. Execute uma segunda BFS a partir de $U$ e encontre o vértice mais distante $V$.
A distância entre $U$ e $V$ é o diâmetro da árvore!`
      }
    ]
  },
  {
    id: "prefix_sum_foundations",
    category: "Estruturas de Dados",
    topicId: "prefix",
    topicTitle: "Prefix Sum",
    title: "Somas de Prefixo 1D e 2D com Consultas em Tempo O(1)",
    subtitle: "Pré-computação cumulativa para responder consultas de soma em intervalos instantaneamente.",
    summary: "Elimine laços repetitivos O(N) por consulta pré-computando vetores de prefixo.",
    estimatedReadingMinutes: 6,
    totalCharacters: 3200,
    sections: [
      {
        id: "pfx-0",
        title: "0. Invariante da Soma Acumulada",
        content: `Definimos $\\text{pref}[i] = \\sum_{j=1}^{i} A[j]$. A soma de qualquer subvetor de $L$ a $R$ é calculada em tempo $O(1)$:
$$\\text{soma}(L, R) = \\text{pref}[R] - \\text{pref}[L - 1]$$

\`\`\`cpp
vector<long long> pref(n + 1, 0);
for (int i = 1; i <= n; i++) {
    pref[i] = pref[i - 1] + a[i - 1];
}
long long range_sum = pref[R] - pref[L - 1];
\`\`\``
      }
    ]
  },
  {
    id: "recursion_foundations",
    category: "Fundamentos & Estruturas",
    topicId: "recursion",
    topicTitle: "Recursão & Pilha de Execução",
    title: "Fundamentos Críticos: Pilha de Recursão & Análise O(N)",
    subtitle: "Call Stack do Sistema Operacional, Prevenção de Stack Overflow e Técnicas de Desdobramento Linear",
    summary: "Domine a mecânica de frames de ativação da Call Stack, limites de profundidade do SO e análise assintótica formal em chamadas recursivas.",
    estimatedReadingMinutes: 10,
    totalCharacters: 4200,
    whiteboardPreset: {
      topic: "Pilha de Recursão e Call Stack",
      algorithm: "dfs",
      cpp_code: `#include <iostream>
#include <vector>
using namespace std;

void dfs(int u, int p, const vector<vector<int>>& adj) {
    // Aloca novo stack frame na Call Stack
    for (int v : adj[u]) {
        if (v != p) {
            dfs(v, u, adj); // PUSH call
        }
    }
    // POP return frame
}

int main() {
    int n = 4;
    vector<vector<int>> adj = {{}, {2}, {1, 3}, {2, 4}, {3}};
    dfs(1, 0, adj);
    return 0;
}`,
      nodes: [
        { id: "1", label: "main() [Frame 0]", x: 260, y: 50, color: "#10b981" },
        { id: "2", label: "dfs(1) [Frame 1]", x: 260, y: 140, color: "#4f46e5" },
        { id: "3", label: "dfs(2) [Frame 2]", x: 260, y: 230, color: "#06b6d4" },
        { id: "4", label: "dfs(3) [Frame 3]", x: 260, y: 320, color: "#f59e0b" },
      ],
      edges: [
        { id: "e1-2", from: "1", to: "2", directed: true, label: "PUSH call" },
        { id: "e2-3", from: "2", to: "3", directed: true, label: "PUSH call" },
        { id: "e3-4", from: "3", to: "4", directed: true, label: "PUSH call" },
      ],
    },
    sections: [
      {
        id: "rec-0",
        title: "0. A Anatomia da Call Stack e Frames de Ativação",
        content: `Toda chamada de função em C++ aloca um **Stack Frame** (quadro de ativação) na memória de pilha (*Call Stack*). Cada quadro armazena:
- **Parâmetros da função** (passados por valor ou ponteiro).
- **Variáveis locais** declaradas no escopo interno.
- **Endereço de retorno (Return Pointer)** para instrução assembly seguinte.
- **Ponteiro de base (Base Pointer - RBP/EBP)** que demarca o escopo do quadro anterior.

### O Risco de Stack Overflow
Em sistemas Linux e em juízes de maratona (como Codeforces, AtCoder, beecrowd), o limite padrão da pilha do sistema operacional é tipicamente de **8MB**.
- Se cada chamada consome 64 bytes e a profundidade de recursão atinge $N = 200.000$, a memória total exigida é $\\approx 12.8\\text{ MB}$, excedendo os 8MB e disparando imediatamente um **Segmentation Fault (SIGSEGV)**.

\`\`\`cpp
// PERIGO: Em grafos lineares ou ziguezague de 200.000 nós, esta DFS estoura a Call Stack:
void dfs_perigosa(int u, int p) {
    for (int v : adj[u]) {
        if (v != p) {
            dfs_perigosa(v, u); // profundidade O(N) = 200.000 quadros na pilha!
        }
    }
}
\`\`\``
      },
      {
        id: "rec-1",
        title: "1. Prevenção de Stack Overflow e Técnicas de Refatoração",
        content: `Existem duas estratégias principais para lidar com recursão profunda em maratonas de programação:

### Estratégia 1: Desdobramento Iterativo com std::stack ou std::vector
Substituir a pilha do sistema operacional pela memória Heap (que suporta centenas de Megabytes):

\`\`\`cpp
void dfs_iterativa(int raiz, int n) {
    vector<bool> visitado(n + 1, false);
    stack<int> st;
    st.push(raiz);
    visitado[raiz] = true;

    while (!st.empty()) {
        int u = st.top();
        st.pop();
        for (int v : adj[u]) {
            if (!visitado[v]) {
                visitado[v] = true;
                st.push(v);
            }
        }
    }
}
\`\`\`

### Estratégia 2: Passagem Estrita por Referência (const &)
Nunca passe vetores, matrizes ou estruturas pesadas por valor dentro de funções recursivas. Passar por valor copia todo o conteúdo para cada novo frame, acelerando o esgotamento da pilha e gerando TLE/MLE.`
      },
      {
        id: "rec-2",
        title: "2. Análise Assintótica Formal e Árvores de Recorrência",
        content: `Para analisar a complexidade de uma função recursiva:
1. **Trabalho por Chamada ($W$):** O custo computacional do corpo da função excluindo as subchamadas.
2. **Fator de Ramificação ($b$):** Quantas chamadas recursivas são disparadas a cada invocação.
3. **Profundidade Máxima ($d$):** O comprimento do maior caminho da raiz até uma condição base.

- **DFS em Grafos e Árvores:** Cada vértice é visitado 1 vez e cada aresta percorrida 2 vezes $\\implies O(V + E)$.
- **Busca Binária:** Ramificação 1, profundidade $\\log_2 N \\implies O(\\log N)$ chamadas.
- **Backtracking Exaustivo (ex: N-Rainhas):** Ramificação $N$, profundidade $N \\implies O(N!)$.`
      }
    ]
  }
];
