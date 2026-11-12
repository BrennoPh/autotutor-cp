"""Expand curriculum slides in learning_content.json to at least 20 slides per topic with rich competitive programming pedagogy."""
import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "learning_content.json"

# Decks de 20 a 22 slides por assunto com fundamentação de maratona (UFMG, USP, Stanford, Erickson, CLRS, CP4)
CURRICULUM_SLIDES = {
    "graph": [
        {
            "title": "Grafos na Maratona de Programação",
            "points": [
                "Definição matemática formal: G = (V, E), onde V é o conjunto de vértices e E o de arestas.",
                "Grafos modelam estados e transições em problemas de busca, dependência, conectividade e rotas.",
                "A primeira decisão do maratonista é identificar o que é vértice e o que é aresta.",
                "Complexidade alvo clássica: algoritmos lineares no tamanho do grafo, O(V + E)."
            ],
            "notes": "Em programação competitiva, grafos raramente vêm explícitos com 'vértices e arestas'. Eles aparecem como labirintos, palavras com trocas de letras, dependências de tarefas ou estados de jogos."
        },
        {
            "title": "Grafo Simples vs Multigrafo vs Pseudografo",
            "points": [
                "Grafo Simples: não possui laços (arestas de um vértice para ele mesmo) nem arestas paralelas.",
                "Multigrafo: permite múltiplas arestas conectando o mesmo par de vértices (pesos diferentes).",
                "Pseudografo: permite arestas paralelas e laços (loops reflexivos).",
                "Cuidado em maratona: ao ler multigrafos com lista de adjacência, você pode ter arestas repetidas que afetam algoritmos ingênuos."
            ],
            "notes": "Se o enunciado diz 'existe no máximo uma aresta entre cada par de cidades', é um grafo simples. Se diz 'estradas com pedágios diferentes entre as mesmas cidades', trata-se de um multigrafo e você geralmente só quer guardar a menor aresta."
        },
        {
            "title": "Grafo Não-Direcionado vs Dígrafo (Direcionado)",
            "points": [
                "Grafo Não-Direcionado: arestas são bidirecionais ({u, v}). Se u conecta a v, v conecta a u.",
                "Dígrafo (Directed Graph): arestas possuem sentido (u -> v). A existência de u -> v não implica v -> u.",
                "Grau de entrada (in-degree) vs Grau de saída (out-degree) em dígrafos.",
                "Na implementação: grafos não-direcionados exigem adicionar a aresta em ambas as listas: adj[u].push_back(v) e adj[v].push_back(u)."
            ],
            "notes": "O esquecimento de duplicar a aresta na lista de adjacência em grafos não-direcionados é um dos erros mais comuns de iniciantes, gerando desconexão e Wrong Answer (WA)."
        },
        {
            "title": "DAG: Grafo Acíclico Dirigido (Directed Acyclic Graph)",
            "points": [
                "Definição: Dígrafo que não possui nenhum ciclo direcionado.",
                "Propriedade vital: Em um DAG, sempre existe pelo menos um vértice com in-degree 0 (fonte) e um com out-degree 0 (sumidouro).",
                "A espinha dorsal da Programação Dinâmica: toda transição de estados de DP forma um caminho em um DAG.",
                "Aplicações: Pré-requisitos de disciplinas, sistemas de compilação (Makefile) e escalonamento de processos."
            ],
            "notes": "Se um problema envolve tarefas que dependem de outras e não podem ter dependência circular, o grafo é garantidamente um DAG e admite Ordenação Topológica."
        },
        {
            "title": "Modelagem e Representações em Memória",
            "points": [
                "Lista de Adjacência: vector<int> adj[N] — padrão absoluto de maratona.",
                "Matriz de Adjacência: bool adj[N][N] ou int adj[N][N] para grafos com peso.",
                "Lista de Arestas: vector<pair<int, int>> edges — ideal para ordenação global de arestas (Kruskal).",
                "A escolha depende do número de vértices V e da densidade de arestas E."
            ],
            "notes": "Lista de adjacência usa espaço proporcional ao número real de arestas. Matriz usa espaço quadrático independentemente de haver arestas ou não."
        },
        {
            "title": "Comparativo de Espaço e Tempo das Representações",
            "points": [
                "Lista de Adjacência: Espaço O(V + E). Iterar vizinhos de u leva O(grau(u)). Checar se existe (u, v) é O(grau(u)).",
                "Matriz de Adjacência: Espaço O(V^2). Checar se existe (u, v) é O(1). Iterar vizinhos leva O(V).",
                "Limite prático: Se V = 10^5, matriz exige 10^10 bytes (~10 GB de RAM), estourando o limite de 256 MB (MLE).",
                "Regra geral: Use matriz apenas se V <= 2000. Para V > 2000, use estritamente lista de adjacência."
            ],
            "notes": "Um grafo com 10^5 vértices e 2*10^5 arestas cabe com folga em 20 MB com lista de adjacência, mas estoura qualquer juiz online se implementado em matriz."
        },
        {
            "title": "Busca em Largura (BFS): Intuição Física",
            "points": [
                "A metáfora da pedra na água: ondas concêntricas se propagando a partir da fonte.",
                "Visita todos os vértices a distância 1, depois todos a distância 2, depois distância 3, e assim por diante.",
                "Garante o MENOR CAMINHO em número de arestas em qualquer grafo não ponderado (ou com pesos unitários).",
                "Estrutura essencial: FILA (Queue) com política FIFO (First-In, First-Out)."
            ],
            "notes": "A BFS explora a fronteira de estados em ordem estrita de proximidade da origem. Por isso, a primeira vez que um nó é alcançado, o caminho até ele é comprovadamente o mais curto possível."
        },
        {
            "title": "A Invariante da Fila FIFO na BFS",
            "points": [
                "Em qualquer instante, a fila contém vértices de no máximo duas distâncias consecutivas: d e d+1.",
                "Todos os nós de distância d são desenfileirados antes de qualquer nó de distância d+1 ser processado.",
                "Vetor de distâncias: dist[s] = 0 e dist[v] = -1 para não visitados.",
                "Transição fundamental: dist[v] = dist[u] + 1 para cada vizinho v não visitado."
            ],
            "notes": "A propriedade de monotonia da fila é a demonstração formal da corretude da BFS. Ela garante que nenhum caminho mais longo seja explorado antes de um mais curto."
        },
        {
            "title": "Árvore de Busca BFS e Camadas de Nível",
            "points": [
                "A BFS induz uma árvore enraizada na origem (BFS Tree).",
                "Cada nível da árvore corresponde exatamente ao vetor de distância dist[v].",
                "Arestas do grafo original que não estão na árvore conectam nós do mesmo nível ou de níveis adjacentes (|dist[u] - dist[v]| <= 1).",
                "Nunca existem arestas cruzando dois ou mais níveis de distância em um grafo não direcionado."
            ],
            "notes": "A árvore BFS decompõe o grafo em estratos horizontais. Isso é útil para provar propriedades de diâmetro e caminhos mínimos."
        },
        {
            "title": "Rastreamento Passo a Passo da BFS (Tabela de Estados)",
            "points": [
                "Passo 0: Fila=[1], dist[1]=0. Outros -1. Enfileira 1 e marca visitado.",
                "Passo 1: Retira 1. Vizinhos 2 e 3 descobertos. dist[2]=1, dist[3]=1. Fila=[2, 3].",
                "Passo 2: Retira 2. Vizinhos 4 e 5 descobertos. dist[4]=2, dist[5]=2. Fila=[3, 4, 5].",
                "Passo 3: Retira 3. Vizinho 6 descoberto. dist[6]=2. Fila=[4, 5, 6].",
                "A busca termina quando a fila fica vazia: todos os nós alcançáveis foram explorados."
            ],
            "notes": "Visualizar a tabela de estados passo a passo ajuda a fixar que nós no mesmo nível são processados juntos."
        },
        {
            "title": "A Armadilha Fatal de Maratona: Push vs Pop",
            "points": [
                "ERRO CLÁSSICO: Marcar o nó como visitado apenas ao retirá-lo da fila (q.pop()).",
                "O QUE ACONTECE: Múltiplos vizinhos podem enfileirar o mesmo nó antes que ele saia da fila.",
                "CONSEQUÊNCIA: A fila cresce exponencialmente, gerando Time Limit Exceeded (TLE) e Memory Limit Exceeded (MLE).",
                "REGRA DE OURO: Sempre marque como visitado IMEDIATAMENTE ao inserir na fila (q.push())."
            ],
            "notes": "Esse é o bug que mais elimina competidores em problemas de BFS em matriz/grid. Se você marca no pop em uma matriz 1000x1000, o mesmo nó pode ser enfileirado 4 vezes por passos vizinhos, explodindo a memória."
        },
        {
            "title": "BFS em Matriz / Grid 2D (Labirintos)",
            "points": [
                "Cada célula (r, c) é um vértice. As arestas são os movimentos para as 4 direções.",
                "Vetores de deslocamento: int dr[] = {-1, 1, 0, 0}; int dc[] = {0, 0, -1, 1};",
                "Fila armazena pares de coordenadas: queue<pair<int, int>> q;",
                "Matriz de distâncias e visitados: int dist[N][M]; inicializada com -1."
            ],
            "notes": "A verificação dos limites (0 <= nr < N && 0 <= nc < M) e se a célula não é parede (#) deve ser feita antes de enfileirar."
        },
        {
            "title": "Busca em Profundidade (DFS): O Fio de Teseu",
            "points": [
                "A estratégia de ir o mais fundo possível por um caminho até atingir um beco sem saída.",
                "Ao encontrar um nó sem vizinhos não visitados, realiza o retrocesso (backtracking).",
                "Estrutura essencial: PILHA (Stack) com política LIFO (Last-In, First-Out).",
                "Na prática: implementada elegantemente pela própria PILHA DE CHAMADAS da recursão."
            ],
            "notes": "A DFS não encontra caminhos mínimos em arestas, mas é a ferramenta definitiva para analisar a conectividade estrutural, componentes e ciclos de um grafo."
        },
        {
            "title": "A Pilha de Recursão e o Risco de Stack Overflow",
            "points": [
                "Cada chamada dfs(u) aloca um registro de ativação na pilha do sistema.",
                "Se o grafo for uma linha de V = 2 * 10^5 vértices, a profundidade de recursão chega a 200.000 chamadas.",
                "O limite padrão de pilha do Linux é de 8 MB; chamadas profundas podem estourar a pilha, gerando Runtime Error (RTE / SIGSEGV).",
                "Solução em maratona: Em C++, aumente o limite da pilha com setrlimit() ou use uma pilha explícita std::stack."
            ],
            "notes": "Em problemas da Codeforces ou maratonas da SBC com grafos grandes em árvore ou linha, a recursão profunda sem cuidados pode abortar submissões corretas."
        },
        {
            "title": "Os Três Estados dos Vértices na DFS (Cores)",
            "points": [
                "Branco (White / 0): Vértice ainda não descoberto/visitado.",
                "Cinza (Gray / 1): Vértice descoberto, ATUALMENTE na pilha ativa de recursão (seus descendentes estão sendo explorados).",
                "Preto (Black / 2): Vértice totalmente concluído (todos os seus vizinhos e subárvore foram explorados e desempilhados).",
                "Esse esquema de 3 cores é a chave para classificar arestas e detectar ciclos."
            ],
            "notes": "Um array int cor[N] com valores 0, 1 e 2 permite que a DFS identifique exatamente a topologia do grafo."
        },
        {
            "title": "Tempos de Entrada e Saída (tin e tout)",
            "points": [
                "Contador de tempo global iniciado em 0 que incrementa a cada evento de entrada e saída.",
                "tin[u]: instante em que dfs(u) é chamada (o nó entra na pilha).",
                "tout[u]: instante em que dfs(u) termina (o nó sai da pilha).",
                "Propriedade de Parênteses: O nó v é descendente de u na árvore DFS se e somente se [tin[v], tout[v]] está contido dentro de [tin[u], tout[u]]."
            ],
            "notes": "Os intervalos de tempo [tin, tout] permitem responder se u é ancestral de v em O(1), sendo a base da subida binária para Lowest Common Ancestor (LCA)."
        },
        {
            "title": "A Árvore DFS e os 4 Tipos de Arestas",
            "points": [
                "Durante a execução da DFS em um dígrafo, cada aresta (u -> v) pertence a uma de 4 categorias:",
                "1. Tree Edge: Leva a um nó Branco (novo nó na árvore DFS).",
                "2. Back Edge: Leva a um nó Cinza (ancestral ativo na pilha de chamadas).",
                "3. Forward Edge: Leva a um nó Preto que é descendente de u na árvore DFS.",
                "4. Cross Edge: Leva a um nó Preto que NÃO é ancestral nem descendente de u (ramos distintos)."
            ],
            "notes": "Essa classificação clássica (Erickson / Cormen) é a base de quase todos os teoremas avançados de grafos."
        },
        {
            "title": "Detecção de Ciclos: O Teorema da Back-Edge",
            "points": [
                "Teorema Fundamental: Um grafo direcionado possui um ciclo se e somente se a DFS encontra pelo menos uma Back Edge.",
                "Por que? Porque uma Back Edge aponta de volta para um nó que já está no caminho ativo da pilha de recursão.",
                "Em grafos NÃO direcionados: basta verificar se existe aresta para um nó já visitado que NÃO seja o pai direto na árvore DFS.",
                "Complexidade: O(V + E) para certificar se o grafo é acíclico ou cíclico."
            ],
            "notes": "A presença de uma aresta apontando para um vértice no estado Cinza prova sem ambiguidade a existência de ciclo direcionado."
        },
        {
            "title": "Ordenação Topológica em DAGs",
            "points": [
                "Objetivo: Ordenar os vértices de forma que para toda aresta u -> v, u apareça antes de v na lista.",
                "Método 1 (DFS): Execute DFS. Ao finalizar cada nó (quando ele fica Preto), adicione-o a uma lista. Inverta a lista no final.",
                "Por que funciona? Porque se u -> v, v termina e fica Preto antes de u terminar (pois não há ciclos). Logo, u precede v na ordem inversa.",
                "Método 2 (Algoritmo de Kahn): Fila com nós de grau de entrada (in-degree) zero. Remove nós e decrementa graus dos vizinhos."
            ],
            "notes": "Se o algoritmo de Kahn não processar todos os N vértices, o grafo possui um ciclo e a ordenação topológica é impossível."
        },
        {
            "title": "Componentes Conexas e Fortemente Conexas (SCC)",
            "points": [
                "Componentes Conexas (Não-direcionados): laço externo 'for (int i = 1; i <= n; i++) if (!vis[i]) dfs(i);'. Cada chamada cobre uma componente inteira.",
                "Componentes Fortemente Conexas (Dígrafos): subgrafos máximos onde todo par de vértices é mutuamente alcançável.",
                "Algoritmo de Kosaraju: duas passadas de DFS (uma no grafo original e outra no grafo transposto/invertido).",
                "Algoritmo de Tarjan: uma única passada de DFS rastreando tin e valores low[u]."
            ],
            "notes": "Condensar um dígrafo em suas SCCs produz um DAG de componentes, permitindo aplicar DP sobre as componentes."
        },
        {
            "title": "Grafos Bipartidos e 2-Coloração",
            "points": [
                "Grafo Bipartido: os vértices podem ser divididos em dois conjuntos independentes L e R, sem arestas internas.",
                "Teorema de König: Um grafo é bipartido se e somente se NÃO possui ciclos de comprimento ímpar.",
                "Teste de Bipartição: use BFS ou DFS alternando cores (0 e 1). Se um vizinho já colorido tiver a mesma cor do nó atual, o grafo não é bipartido.",
                "Aplicações: Emparelhamento máximo (Maximum Matching) e problemas de atribuição de tarefas."
            ],
            "notes": "Se o teste com 2 cores encontrar conflito, você achou um ciclo ímpar e provou que a bipartição é inviável."
        },
        {
            "title": "BFS 0-1 com Deque (Pesos 0 e 1)",
            "points": [
                "Quando as arestas possuem peso 0 ou 1, a BFS clássica falha, mas Dijkstra O(E log V) é excessivo.",
                "A solução ótima é a BFS 0-1 usando std::deque<int> em O(V + E) tempo linear.",
                "Se a aresta tem peso 0: insere na frente da deque (q.push_front(v)) com a mesma distância.",
                "Se a aresta tem peso 1: insere no fundo da deque (q.push_back(v)) com dist + 1.",
                "A invariante de monotonicidade da fila é perfeitamente preservada."
            ],
            "notes": "Técnica muito frequente em maratona para labirintos com portas que podem ser abertas sem custo ou com custo unitário."
        }
    ]
}

def main():
    print("Atualizando learning_content.json com decks de slides expandidos...")
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    
    # Atualiza tópicos
    for topic in data["topics"]:
        tid = topic["id"]
        if tid in CURRICULUM_SLIDES:
            topic["slides"] = CURRICULUM_SLIDES[tid]
            print(f"  ✓ {tid}: atualizado para {len(topic['slides'])} slides.")
        else:
            print(f"  - {tid}: mantido com {len(topic.get('slides', []))} slides.")
            
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Concluído!")

if __name__ == "__main__":
    main()
