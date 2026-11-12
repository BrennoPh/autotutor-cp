"""Full 20-slide decks for competitive programming fundamentals."""
import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "learning_content.json"

ALL_SLIDES = {
    "fundamentals": [
        {"title": "O Modelo de Computação em Maratona", "points": [
            "Em competições de programação (ICPC, OBI, Codeforces), seu código roda contra testes secretos sob limites estritos de tempo e memória.",
            "Um limite típico de tempo é 1.0 a 2.0 segundos; o limite de memória padrão é 256 MB a 512 MB.",
            "A primeira tarefa do competidor ao ler um problema é calcular o orçamento de operações viável."
        ], "notes": "Compreender os limites da máquina evita submeter soluções ingênuas que receberão Time Limit Exceeded (TLE)."},
        {"title": "A Regra de Ouro: 10^8 Operações por Segundo", "points": [
            "Um processador moderno em juiz online executa aproximadamente 10^8 operações aritméticas/lógicas elementares por segundo em C++.",
            "Se o tempo limite é de 1.0s, seu algoritmo deve realizar no máximo ~10^8 passos no pior caso.",
            "Operações com constantes pesadas (divisão, módulo, alocação de memória) reduzem esse limite para ~2 * 10^7.",
            "Operações com bits (bitwise) e vetores contíguos podem ultrapassar 2 * 10^8 operações."
        ], "notes": "Essa regra de bolso permite saber se sua ideia é viável antes mesmo de escrever uma única linha de código."},
        {"title": "Notação Assintótica: Big-O, Ômega e Theta", "points": [
            "Big-O (O): Limite superior assintótico (pior caso ou teto do crescimento).",
            "Big-Ômega (Ω): Limite inferior assintótico (melhor caso ou piso do crescimento).",
            "Big-Theta (Θ): Limite justo (quando O e Ω coincidem).",
            "Em maratona, sempre analisamos o PIOR CASO para evitar que o juiz com casos de teste adversariais cause TLE."
        ], "notes": "Ignoramos constantes aditivas e multiplicativas pequenas para focar no comportamento do algoritmo quando N cresce."},
        {"title": "Mapeando o Limite de N para a Complexidade Alvo", "points": [
            "N <= 10..12: O(N!) ou O(N^2 * 2^N) — permutações, busca completa recursiva.",
            "N <= 20..22: O(2^N) ou O(N * 2^N) — bitmask DP, subconjuntos.",
            "N <= 500: O(N^3) — Floyd-Warshall, multiplicação de matrizes.",
            "N <= 5000: O(N^2) — laços duplos, DP quadrática.",
            "N <= 2 * 10^5: O(N log N) ou O(N) — ordenação, busca binária, árvores, grafos.",
            "N <= 10^9..10^18: O(log N) ou O(1) — busca binária na resposta, matemática, exponenciação modular."
        ], "notes": "Essa tabela de correspondência direta entre o tamanho da entrada e a complexidade esperada é o maior segredo dos maratonistas veteranos."},
        {"title": "Análise de Laços Aninhados e Séries Harmônicas", "points": [
            "Dois laços de 0 a N: N * N = O(N^2).",
            "Laço interno variando até i: N * (N + 1) / 2 = O(N^2).",
            "Laço externo de 1 a N, laço interno com passo i (múltiplos): N/1 + N/2 + N/3 + ... = N * ln(N) = O(N log N).",
            "Identificar séries harmônicas evita descartar algoritmos de crivo achando que são quadráticos."
        ], "notes": "O crivo de Eratóstenes e a contagem de divisores parecem ter custo quadrático à primeira vista, mas sua análise formal revela O(N log N) ou O(N log log N)."},
        {"title": "Entrada e Saída Rápida em C++ (Fast I/O)", "points": [
            "Por padrão, std::cin e std::cout sincronizam com stdio do C (scanf/printf), causando lentidão massiva.",
            "Linhas obrigatórias no início da main: ios_base::sync_with_stdio(false); cin.tie(NULL);",
            "NUNCA use std::endl em laços: ele força o esvaziamento do buffer de saída (flush). Use '\\n'.",
            "Com Fast I/O, cin e cout tornam-se tão ou mais rápidos que scanf e printf."
        ], "notes": "Muitos competidores recebem TLE com soluções O(N) simplesmente porque usaram std::endl para imprimir 200.000 linhas."},
        {"title": "Tipos Numéricos e Integer Overflow", "points": [
            "int (32 bits com sinal): armazena de -2 * 10^9 até +2 * 10^9 (exatamente 2^31 - 1 = 2.147.483.647).",
            "long long (64 bits com sinal): armazena até ~9 * 10^18 (2^63 - 1).",
            "Qualquer soma de prefixos, multiplicação de inteiros até 10^5 ou soma de elementos 10^9 ESTOURA o int.",
            "Cuidado: a expressão 'long long x = a * b;' estoura se a e b forem int, pois a multiplicação ocorre em 32 bits antes da atribuição! Use '1LL * a * b'."
        ], "notes": "O overflow silencioso de inteiros em C++ produz números negativos estranhos e é uma das causas número 1 de Wrong Answer (WA)."},
        {"title": "Aritmética de Ponto Flutuante e Precisão", "points": [
            "double oferece ~15 a 17 dígitos de precisão significativa; long double oferece ~18 a 19 dígitos.",
            "Nunca compare floats com igualdade exata (a == b). Use tolerância epsilon: fabs(a - b) < 1e-9.",
            "Evite divisões prematuras. Sempre que possível, converta comparações de frações a/b < c/d em multiplicações: a * d < c * b.",
            "Para imprimir com casas decimais fixas: cout << fixed << setprecision(9) << ans << '\\n';"
        ], "notes": "Trabalhar com inteiros sempre que possível elimina 100% dos erros sutis de arredondamento em geometria e física."},
        {"title": "Problemas de Simulação: O Método Direto", "points": [
            "Simulação pura: o enunciado descreve um processo passo a passo (um jogo, um robô, uma fila de banco).",
            "Sua tarefa é implementar exatamente o que foi descrito, sem tentar atalhos matemáticos que possam quebrar regras sutis.",
            "Modularize o código em funções pequenas e legíveis (mover(), colidir(), pontuar()).",
            "Fique atento à ordem exata dos eventos: quem joga primeiro? O que acontece em caso de empate?"
        ], "notes": "Problemas de simulação testam sua atenção a detalhes e sua velocidade de codificação sem bugs."},
        {"title": "Navegação em Grids 2D com Vetores de Direção", "points": [
            "Para mover nas 4 direções (Cima, Baixo, Esquerda, Direita), evite encadear 4 blocos de if/else.",
            "Use vetores constantes de deslocamento: const int dr[] = {-1, 1, 0, 0}; const int dc[] = {0, 0, -1, 1};",
            "Para 8 direções (incluindo diagonais), basta expandir para arrays de tamanho 8.",
            "Laço idiomático: for (int d = 0; d < 4; d++) { int nr = r + dr[d], nc = c + dc[d]; if (valido(nr, nc)) ... }"
        ], "notes": "Essa técnica reduz seu código de simulação pela metade e previne erros de digitação nas coordenadas vizinhas."},
        {"title": "Problemas Ad Hoc e Identificação de Invariantes", "points": [
            "Problemas Ad Hoc não se encaixam em algoritmos clássicos prontos (não é Dijkstra nem DP padrão).",
            "Exigem encontrar uma observação-chave ou uma propriedade invariante que simplifica o problema.",
            "Estratégia: simule manualmente os primeiros casos pequenos (N=1, 2, 3, 4, 5) em uma folha de papel.",
            "Procure por padrões: a resposta é sempre par? O maior elemento sempre vence? Há repetição periódica?"
        ], "notes": "Em maratona, a habilidade de resolver problemas Ad Hoc é o que diferencia os competidores medalhistas."},
        {"title": "Análise de Paridade e Simetrias", "points": [
            "Muitos problemas aparentemente complexos dependem apenas da paridade da soma ou de inversões.",
            "Em jogos de tabuleiro ou trocas de moedas, analise se uma operação muda a paridade ou a preserva.",
            "Se o estado inicial e o estado objetivo têm paridades diferentes e a operação preserva paridade, a resposta é impossível.",
            "Exemplo: no jogo dos 15 (15-puzzle), a paridade da permutação mais a linha do espaço vazio é invariante."
        ], "notes": "Identificar se um invariante é conservado permite responder 'NÃO' imediatamente em O(1)."},
        {"title": "O Princípio da Casa dos Pombos (Pigeonhole)", "points": [
            "Se N itens forem colocados em M recipientes e N > M, pelo menos um recipiente conterá mais de um item.",
            "Em competições: se você calcular N+1 somas de prefixos módulo N, pelo menos duas serão congruentes módulo N.",
            "Isso prova instantaneamente que existe um subvetor contíguo cuja soma é divisível por N!",
            "Use o princípio para provar que ciclos devem ocorrer ou que respostas existem sem precisar testar tudo."
        ], "notes": "O princípio dos pombos frequentemente transforma buscas exponenciais em garantias matemáticas determinísticas."},
        {"title": "Construção de Casos de Teste Locais", "points": [
            "Nunca submeta seu código apenas testando os exemplos do enunciado (eles são propositalmente fracos).",
            "Teste o caso mínimo: N = 1, valores zero, valores negativos.",
            "Teste o caso máximo: N = 10^5, valores máximos (10^9) para checar se dá overflow ou estouro de memória.",
            "Teste casos em linha reta, grafos desconexos, árvores degeneradas e matrizes 1x1."
        ], "notes": "Testar casos extremos na sua máquina antes de enviar economiza submissões com penalidade de tempo (+20 minutos por erro)."},
        {"title": "Stress Testing com Scripts Locais", "points": [
            "Técnica profissional de maratona quando você está recebendo Wrong Answer e não sabe por quê.",
            "Escreva uma solução ingênua (força bruta O(N^2) ou O(2^N)) que você tem 100% de certeza que está correta.",
            "Escreva um gerador de testes aleatórios pequenos.",
            "Rode um script bash ou python que compara a saída da sua solução rápida com a da força bruta até encontrar a discordância."
        ], "notes": "O gerador encontra em segundos o caso de 4 números onde sua lógica falhou, permitindo debugar com precisão."},
        {"title": "Diagnóstico do Veredito: Wrong Answer (WA)", "points": [
            "WA significa que sua lógica falhou em pelo menos um caso de teste oficial.",
            "Causas mais frequentes: Integer overflow (usou int em vez de long long), caso N=1 esquecido, ordem de impressão incorreta.",
            "Atenção a espaços e quebras de linha: 'YES' vs 'Yes' ou esquecer de imprimir espaço entre números.",
            "Confira se o problema exige arredondamento específico (piso, teto ou truncamento)."
        ], "notes": "Revise os limites de tipos numéricos antes de tentar reescrever o algoritmo do zero."},
        {"title": "Diagnóstico do Veredito: Time Limit Exceeded (TLE)", "points": [
            "Seu código demorou mais que o tempo permitido (ex: > 1.0s).",
            "Causa 1: A complexidade teórica do seu algoritmo é alta demais para o N (ex: O(N^2) para N=10^5).",
            "Causa 2: Loop infinito (condição de parada de while que nunca é atingida ou busca que revisita nós).",
            "Causa 3: Entrada e saída lentas (não usou Fast I/O ou usou std::endl).",
            "Causa 4: Alocações repetidas de memória dentro de loops (ex: criar vector<int> de tamanho N dentro do for)."
        ], "notes": "Declare estruturas grandes globalmente ou passe referências constantes (&) em vez de copiar vetores por valor."},
        {"title": "Diagnóstico do Veredito: Runtime Error (RTE / RE)", "points": [
            "Seu programa abortou com código de erro diferente de zero durante a execução.",
            "Causa 1: Acesso fora dos limites de um array ou vector (Index Out of Bounds / SIGSEGV).",
            "Causa 2: Divisão por zero ou resto de divisão por zero (x % 0 / SIGFPE).",
            "Causa 3: Estouro de pilha de recursão (Stack Overflow) por recursão profunda sem limite ampliado.",
            "Causa 4: Desreferência de ponteiro nulo ou ponteiro inválido."
        ], "notes": "No Linux, compile com as flags de depuração: -Wall -Wextra -fsanitize=address,undefined para pegar erros de índice na hora."},
        {"title": "Diagnóstico do Veredito: Memory Limit Exceeded (MLE)", "points": [
            "Seu programa consumiu mais memória do que o limite permitido (ex: > 256 MB).",
            "Calcule a memória dos seus arrays: int arr[10000][10000] consome 10^8 * 4 bytes = 400 MB (MLE imediato).",
            "Evite matrizes quando lista de adjacência for suficiente.",
            "Fique atento a recursões com parâmetros copiados por valor em vez de por referência."
        ], "notes": "sizeof(int) = 4 bytes, sizeof(long long) = 8 bytes, sizeof(double) = 8 bytes. Multiplique pelo tamanho do vetor para estimar o uso de RAM."},
        {"title": "Rotina de Maratona: Estratégia em Equipe", "points": [
            "Nos primeiros 15 minutos: divida a leitura de todos os problemas do caderno entre os integrantes.",
            "Identifique imediatamente os problemas mais fáceis para abrir o placar (balão inicial).",
            "Enquanto um integrante codifica no teclado, os outros dois pensam e escrevem código no papel.",
            "Nunca fique mais de 45 minutos travado no teclado sem progresso: imprima o código, libere a máquina e pense no papel."
        ], "notes": "Em maratona da ICPC, a estratégia de equipe e gerenciamento de tempo no teclado é tão importante quanto o conhecimento algorítmico."}
    ],
    "structures": [
        {"title": "O Papel das Estruturas de Dados na Maratona", "points": [
            "Estruturas de dados organizam coleções de valores para permitir consultas e modificações eficientes.",
            "A escolha correta de estrutura frequentemente reduz a complexidade de O(N) para O(log N) ou O(1).",
            "Em C++, a Standard Template Library (STL) fornece implementações otimizadas e testadas.",
            "Dominar os custos assintóticos de cada método da STL é obrigatório para não introduzir TLE invisível."
        ], "notes": "Não reinvente estruturas básicas durante o contest. Use a STL com maestria e conheça a complexidade de cada função."},
        {"title": "Vetores Dinâmicos: std::vector", "points": [
            "Array dinâmico contíguo em memória com redimensionamento automático.",
            "push_back() possui custo O(1) AMORTIZADO: a capacidade dobra quando cheia (1, 2, 4, 8, 16...).",
            "Acesso posicional v[i] é O(1) direto em memória com altíssima taxa de acerto de cache (cache locality).",
            "Dica de performance: se você souber o tamanho final com antecedência, use v.reserve(N) para evitar realocações."
        ], "notes": "Inserir ou remover no início (v.insert(v.begin(), val)) é O(N). Se precisar de inserção rápida em ambas as pontas, use std::deque."},
        {"title": "Pilhas (Stacks): O Princípio LIFO", "points": [
            "LIFO: Last-In, First-Out (O último a entrar é o primeiro a sair).",
            "Métodos principais: push() para empilhar, pop() para desempilhar, top() para consultar o topo.",
            "Todas as operações executam em O(1) estrito.",
            "std::stack em C++ é um container adapter construído por padrão sobre std::deque."
        ], "notes": "Pilhas são a estrutura natural para avaliar expressões matemáticas, rastrear chamadas recursivas e resolver problemas de parênteses."},
        {"title": "Problema Clássico de Pilha: Casamento de Parênteses", "points": [
            "Problema: determinar se uma expressão com '()', '[]' e '{}' está bem formada.",
            "Algoritmo: ao ler caractere de abertura, empilhe. Ao ler caractere de fechamento, verifique se o topo corresponde e desempilhe.",
            "Se tentar desempilhar com pilha vazia, ou se no final a pilha não estiver vazia: expressão inválida.",
            "Complexidade: O(N) tempo e O(N) memória com uma única varredura linear."
        ], "notes": "Esse padrão de empilhar aberturas e comparar no fechamento é a base de compiladores e parsers de linguagens."},
        {"title": "Pilha Monótona (Monotonic Stack): O Próximo Maior em O(N)", "points": [
            "Problema: para cada elemento de um array, encontrar o primeiro elemento maior à sua direita.",
            "Solução ingênua com dois laços: O(N^2).",
            "Solução com Pilha Monótona: mantenha os elementos na pilha em ordem decrescente.",
            "Ao processar um elemento maior que o topo, desempilhe e registre: esse elemento é o 'próximo maior' dos nós desempilhados!",
            "Cada elemento entra e sai da pilha no máximo uma vez, garantindo O(N) total."
        ], "notes": "A pilha monótona é uma das técnicas mais cobradas em maratonas para problemas de histogramas, áreas máximas de retângulos e visibilidade."},
        {"title": "Filas (Queues): O Princípio FIFO", "points": [
            "FIFO: First-In, First-Out (O primeiro a entrar é o primeiro a sair).",
            "Métodos principais: push() para enfileirar, pop() para desenfileirar, front() para consultar a frente.",
            "Todas as operações executam em O(1) estrito.",
            "std::queue é o motor fundamental da Busca em Largura (BFS) em grafos e matrizes."
        ], "notes": "Filas mantêm a ordem cronológica estrita de chegada dos eventos."},
        {"title": "Deques: Double-Ended Queues", "points": [
            "Fila de extremidade dupla com inserção e remoção em O(1) em ambas as pontas.",
            "Métodos: push_front(), push_back(), pop_front(), pop_back(), front(), back().",
            "Permite acesso aleatório por índice d[i] em O(1).",
            "Aplicação clássica na maratona: BFS 0-1 em grafos com arestas de pesos 0 e 1."
        ], "notes": "std::deque consome ligeiramente mais memória que std::vector porque aloca blocos fixos de memória em vez de um único bloco contíguo."},
        {"title": "Fila Monótona (Monotonic Queue) e Janela Deslizante", "points": [
            "Problema: encontrar o menor elemento em cada janela deslizante de tamanho K em um array de tamanho N.",
            "Solução usando std::multiset: O(N log K).",
            "Solução usando Deque Monótono: O(N) linear! Mantém os índices dos elementos em ordem crescente de valor.",
            "Ao avançar a janela: remove do fundo elementos maiores que o novo elemento, e remove da frente índices que saíram da janela."
        ], "notes": "O elemento mínimo da janela está sempre no front() da deque. Cada índice é inserido e removido no máximo uma vez."},
        {"title": "Filas de Prioridade (Priority Queue / Heaps)", "points": [
            "Estrutura que mantém o elemento de maior prioridade (por padrão o maior elemento) no topo.",
            "push() insere em O(log N); pop() remove o elemento de maior prioridade em O(log N); top() consulta em O(1).",
            "Construída internamente sobre uma árvore binária quase completa chamada Binary Heap.",
            "std::priority_queue<int> é um Max-Heap. Para Min-Heap: std::priority_queue<int, vector<int>, greater<int>>."
        ], "notes": "O Min-Heap é a estrutura que garante a complexidade O(E log V) do algoritmo de Dijkstra e de Prim."},
        {"title": "Invariante de Heap e Representação em Vetor", "points": [
            "Um Heap quase completo pode ser armazenado em um vetor simples sem ponteiros!",
            "Para um nó no índice i (1-based): Filho esquerdo = 2*i; Filho direito = 2*i + 1; Pai = i / 2.",
            "Invariante de Max-Heap: para todo nó i diferente da raiz, valor[pai(i)] >= valor[i].",
            "Operações de up-heap (subida) e down-heap (descida) reestabelecem a invariante em O(log N)."
        ], "notes": "Construir um heap a partir de um vetor desordenado leva O(N) usando make_heap / bottom-up heapify, e não O(N log N)."},
        {"title": "Conjuntos Ordenados: std::set e std::multiset", "points": [
            "Armazena elementos ordenados e sem duplicatas (std::set) ou com duplicatas (std::multiset).",
            "Implementado como Árvore Binária de Busca Balanceada (Red-Black Tree).",
            "Inserção, remoção e busca executam em O(log N) no pior caso garantido.",
            "Métodos essenciais: s.lower_bound(x) encontra o primeiro elemento >= x em O(log N)."
        ], "notes": "CUIDADO: Use o método do set 's.lower_bound(x)' e NUNCA a função genérica 'std::lower_bound(s.begin(), s.end(), x)'. A função genérica não tem acesso aleatório e roda em O(N), causando TLE!"},
        {"title": "Dicionários Ordenados: std::map", "points": [
            "Associa uma chave (Key) a um valor (Value) mantendo as chaves sempre ordenadas.",
            "Acesso, inserção e consulta em O(log N) por operação.",
            "Cuidado clássico: acessar map[k] quando a chave k não existe INSERE automaticamente a chave com valor padrão (0 para inteiros)!",
            "Para apenas consultar sem modificar o mapa, use: if (m.count(k)) ou m.find(k) != m.end()."
        ], "notes": "std::map é perfeito para mapear strings para identificadores numéricos ou comprimir coordenadas esparsas."},
        {"title": "Tabelas Hash: std::unordered_map e std::unordered_set", "points": [
            "Estruturas baseadas em tabela hash (Hash Table).",
            "Tempo MÉDIO de inserção, remoção e busca: O(1).",
            "Os elementos NÃO ficam ordenados.",
            "O pior caso teórico pode ser O(N) se houver muitas colisões de hash."
        ], "notes": "Muitos iniciantes usam unordered_map achando que é sempre mais rápido que map, mas o overhead de constantes e colisões pode torná-lo mais lento."},
        {"title": "Defendendo Hash Maps contra Testes Adversariais", "points": [
            "No Codeforces e maratonas com hackeamento, outros competidores podem gerar testes que forçam colisões na função hash padrão do GCC.",
            "Resultado de colisões em massa: sua complexidade salta de O(1) para O(N^2), gerando TLE imediato.",
            "Solução profissional: use uma função de hash personalizada com número aleatório baseado em chrono::steady_clock.",
            "Custom hash idiomático: struct custom_hash { size_t operator()(uint64_t x) const { ... } };"
        ], "notes": "Essa defesa com custom_hash é padrão obrigatório para competidores na plataforma Codeforces."},
        {"title": "Disjoint Set Union (DSU / Union-Find)", "points": [
            "Estrutura para gerenciar uma partição de N elementos em subconjuntos disjuntos.",
            "Operações fundamentais: find(u) retorna o representante do conjunto de u; unite(u, v) une os conjuntos de u e v.",
            "Inicialização: cada elemento é seu próprio pai: parent[i] = i; size[i] = 1.",
            "Sem otimizações, a árvore de pais pode se degenerar em uma linha, levando a O(N) por operação."
        ], "notes": "O DSU é a espinha dorsal de algoritmos de conectividade dinâmica e do algoritmo de Kruskal para Árvores Geradoras Mínimas."},
        {"title": "Otimização 1 do DSU: Compressão de Caminhos (Path Compression)", "points": [
            "Ao chamar find(u), conectamos todos os nós visitados diretamente à raiz do conjunto.",
            "Implementação em uma linha: int find(int u) { return parent[u] == u ? u : parent[u] = find(parent[u]); }",
            "Essa otimização achata a árvore dinamicamente a cada consulta.",
            "Com apenas path compression, o custo amortizado por operação já cai para O(log N)."
        ], "notes": "A atribuição parent[u] = find(parent[u]) atualiza o ponteiro durante o retorno da recursão sem custo extra."},
        {"title": "Otimização 2 do DSU: União por Tamanho ou Rank", "points": [
            "Ao unir dois conjuntos com raízes r1 e r2, sempre penduramos a árvore MENOR sob a raiz da árvore MAIOR.",
            "Isso garante que a profundidade da árvore nunca ultrapasse O(log N).",
            "Código: if (sz[r1] < sz[r2]) swap(r1, r2); parent[r2] = r1; sz[r1] += sz[r2];",
            "Combinando Path Compression + Union by Size, o custo por operação torna-se praticamente constante!"
        ], "notes": "As duas otimizações juntas produzem uma das estruturas mais rápidas de toda a ciência da computação."},
        {"title": "A Função Inversa de Ackermann no DSU", "points": [
            "A complexidade teórica amortizada de cada operação de DSU é O(α(N)), onde α é a função inversa de Ackermann.",
            "A função de Ackermann cresce astronomicamente rápido; sua inversa α(N) cresce astronomicamente devagar.",
            "Para qualquer número de átomos no universo visível (N <= 10^80), α(N) <= 4.",
            "Portanto, na prática, as operações de DSU executam em tempo O(1) estritamente constante."
        ], "notes": "Robert Tarjan demonstrou essa complexidade formal em 1975, um dos marcos clássicos da análise de algoritmos."},
        {"title": "Bitset em C++: Operações com 64x de Aceleração", "points": [
            "std::bitset<N> armazena um vetor de booleanos comprimido em nível de bits (1 bit por booleano em vez de 1 byte).",
            "Operações lógicas bit a bit (E, OU, XOR, deslocamentos) processam 64 bits em uma única instrução da CPU.",
            "Reduz a complexidade prática de algoritmos de O(N^2) ou O(N^3) por um fator de 64.",
            "Ideal para fechamento transitivo de grafos, problemas de mochila com valores booleanos e casamento de padrões."
        ], "notes": "Um algoritmo O(N^3 / 64) com N = 2000 executa ~1.2 * 10^8 operações, rodando com folga em menos de 0.2 segundos."},
        {"title": "Resumo de Escolha de Estruturas na Maratona", "points": [
            "Consultas de mínimo/máximo com inserções contínuas? -> std::priority_queue.",
            "Saber se elemento já foi visto? -> std::vector<bool> se chaves forem pequenas, std::set / unordered_set se esparsas.",
            "Conectividade de componentes e fusão de grupos? -> DSU com Path Compression.",
            "Processamento LIFO / avaliação de parênteses? -> std::stack.",
            "Processamento FIFO / BFS em camadas? -> std::queue."
        ], "notes": "A estrutura correta torna a solução do problema intuitiva e o código enxuto."}
    ]
}

def main():
    print("Atualizando learning_content.json com decks completos de 20 slides...")
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    
    for topic in data["topics"]:
        tid = topic["id"]
        if tid in ALL_SLIDES:
            topic["slides"] = ALL_SLIDES[tid]
            print(f"  ✓ {tid}: atualizado para {len(topic['slides'])} slides.")
        else:
            print(f"  - {tid}: mantido com {len(topic.get('slides', []))} slides.")
            
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Concluído!")

if __name__ == "__main__":
    main()
