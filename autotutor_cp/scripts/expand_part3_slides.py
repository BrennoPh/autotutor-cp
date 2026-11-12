"""Part 3: 20-slide decks for math, greedy, dp, tree and binary completion."""
import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "learning_content.json"

PART3_SLIDES = {
    "binary_extra": {
        "title": "Aplicações Avançadas de Busca Binária", "points": [
            "Binary Search sobre o grafo de fluxo máximo: encontrando a capacidade de corte gargalo.",
            "Combinando Busca Binária com 2-Pointers: fixando uma variável e buscando a outra.",
            "Busca Binária sobre estruturas de dados: Segment Trees com busca binária interna (Walk on SegTree) em O(log N).",
            "A técnica se aplica a qualquer problema onde uma propriedade é preservada unidirecionalmente."
        ], "notes": "A busca binária é um paradigma universal que transcende arrays simples e opera sobre qualquer estrutura com invariante monótono."
    },
    "math": [
        {"title": "Matemática na Programação Competitiva", "points": [
            "A matemática discreta é uma das áreas mais frequentes e decisivas em maratonas da SBC e ICPC.",
            "Tópicos essenciais: Teoria dos Números, Primalidade, Crivos, Aritmética Modular, Exponenciação Rápida e Combinatória.",
            "Objetivo: evitar computação de força bruta através de identidades e propriedades algébricas.",
            "Complexidade típica: transformar laços de O(N) em O(sqrt(N)), O(log N) ou O(1)."
        ], "notes": "Compreender a matemática subjacente simplifica o código e previne Time Limit Exceeded."},
        {"title": "Divisibilidade e Números Primos", "points": [
            "Um número inteiro p > 1 é primo se possui exatamente dois divisores positivos distintos: 1 e p.",
            "Se um número N for composto, ele possui obrigatoriamente pelo menos um divisor d tal que 2 <= d <= sqrt(N).",
            "Por que? Se todos os divisores fossem maiores que sqrt(N), o produto de dois divisores seria > sqrt(N) * sqrt(N) = N, uma contradição!",
            "Teste de primalidade ingênuo: testar divisores até sqrt(N) em tempo O(sqrt(N))."
        ], "notes": "Verificar até sqrt(N) é a base de testes elementares de primalidade para N até 10^12."},
        {"title": "Otimizando o Teste de Primalidade Simples", "points": [
            "Casos especiais: se N <= 1 retorna false; se N <= 3 retorna true; se N % 2 == 0 ou N % 3 == 0 retorna false.",
            "Todos os primos maiores que 3 são da forma 6k ± 1 (6k + 1 ou 6k + 5).",
            "Laço com passo 6: for (long long i = 5; i * i <= N; i += 6) if (N % i == 0 || N % (i + 2) == 0) return false;",
            "Reduz o número de iterações por um fator de 3 em relação ao teste comum."
        ], "notes": "Para testar se um único número até 10^12 é primo durante a leitura, essa função roda em menos de 1 milissegundo."},
        {"title": "O Crivo de Eratóstenes: Primos em Massa", "points": [
            "Problema: encontrar todos os números primos até N (onde N = 10^7).",
            "Algoritmo: comece assumindo todos primos; para cada primo p, marque todos os seus múltiplos 2p, 3p, 4p... como compostos.",
            "Otimização 1: comece a marcar múltiplos a partir de p * p (múltiplos menores já foram marcados por primos anteriores).",
            "Complexidade: O(N * (1/2 + 1/3 + 1/5 + 1/7 + ...)) = O(N log(log N)) — assintoticamente quase linear!"
        ], "notes": "Com N = 10^7, o crivo roda em cerca de 0.08 segundos em C++ moderno."},
        {"title": "Crivo Linear e Fatoração em Tempo O(log N)", "points": [
            "O crivo tradicional marca o mesmo número composto múltiplas vezes (ex: 12 é marcado por 2 e por 3).",
            "O Crivo Linear (Euler Sieve) marca cada número composto exatamente uma vez pelo seu Menor Fator Primo (SPF - Smallest Prime Factor).",
            "Mantém o array spf[x] contendo o menor primo que divide x.",
            "Fatoração instantânea: para fatorar qualquer número N <= 10^7, basta fazer N /= spf[N] repetidamente em tempo O(log N)!"
        ], "notes": "Fatorar em O(log N) permite decompor 100.000 números em menos de 0.05 segundos em um contest."},
        {"title": "Fatoração de Inteiros Únicos até 10^12", "points": [
            "Para fatorar um número N até 10^12 sem pré-calcular crivo:",
            "Itere d de 2 até d * d <= N. Enquanto d dividir N, incremente o expoente de d e divida N por d.",
            "Ao final, se N > 1, o que sobrou é obrigatoriamente um número primo!",
            "Resultado: decomposição canônica N = p1^a1 * p2^a2 * ... * pk^ak em tempo O(sqrt(N))."
        ], "notes": "Essa decomposição em fatores primos é o ponto de partida para calcular divisores, função totiente e somatórios."},
        {"title": "Contagem e Soma de Divisores", "points": [
            "Dada a fatoração prima N = p1^a1 * p2^a2 * ... * pk^ak:",
            "Número de divisores: d(N) = (a1 + 1) * (a2 + 1) * ... * (ak + 1).",
            "Soma dos divisores: sigma(N) = (p1^(a1+1) - 1)/(p1 - 1) * ... * (pk^(ak+1) - 1)/(pk - 1).",
            "Um número com muitos divisores (número altamente composto) até 10^9 possui no máximo 1344 divisores."
        ], "notes": "Saber que o número de divisores até 10^9 é pequeno permite iterar sobre todos os divisores sem estourar o tempo."},
        {"title": "Máximo Divisor Comum (MDC / GCD)", "points": [
            "O maior inteiro positivo que divide simultaneamente A e B.",
            "Algoritmo de Euclides: gcd(A, B) = gcd(B, A % B) com base gcd(A, 0) = A.",
            "A cada dois passos, o resto pelo menos se reduz pela metade: A % B < A / 2.",
            "Complexidade: O(log(min(A, B))). Com números de 64 bits, executa em no máximo ~70 passos!",
            "Em C++17+: std::gcd(a, b) está disponível nativamente em <numeric>."
        ], "notes": "O algoritmo de Euclides é um dos algoritmos mais antigos da humanidade (300 a.C.) e continua sendo insuperável em eficiência."},
        {"title": "Mínimo Múltiplo Comum (MMC / LCM)", "points": [
            "Identidade fundamental: A * B = gcd(A, B) * lcm(A, B).",
            "Fórmula de cálculo: lcm(A, B) = (A / gcd(A, B)) * B.",
            "ATENÇÃO COM OVERFLOW: Divida primeiro e multiplique depois! Se fizer (A * B) / gcd, a multiplicação pode estourar 64 bits antes da divisão.",
            "Em C++17+: std::lcm(a, b) em <numeric>."
        ], "notes": "A ordem das operações 'dividir antes de multiplicar' evita overflow em cálculos de MMC com números grandes."},
        {"title": "Algoritmo Estendido de Euclides", "points": [
            "Teorema de Bézout: para quaisquer inteiros A e B, existem inteiros x e y tais que: A * x + B * y = gcd(A, B).",
            "O Algoritmo Estendido de Euclides calcula simultaneamente gcd(A, B) e os coeficientes x e y.",
            "Recorrência: d = extgcd(B, A % B, x1, y1); x = y1; y = x1 - y1 * (A / B);",
            "Aplicações: resolver Equações Diofantinas Lineares e encontrar o Inverso Modular quando o módulo não for primo."
        ], "notes": "Essencial para criptografia RSA e problemas de congruências lineares."},
        {"title": "Aritmética Modular: Adição e Multiplicação", "points": [
            "Módulos comuns em competições: 10^9 + 7 e 998244353 (ambos são números primos grandes).",
            "Propriedades fundamentais:",
            "(A + B) % M = ((A % M) + (B % M)) % M",
            "(A * B) % M = ((A % M) * (B % M)) % M",
            "Em C++: ao multiplicar dois inteiros de 32 bits módulo 10^9+7, converta para long long para evitar overflow no produto intermediário (1LL * a * b) % M."
        ], "notes": "O módulo 10^9+7 cabe em um inteiro de 32 bits, mas seu produto pode chegar a 10^18, exigindo 64 bits."},
        {"title": "Aritmética Modular: Subtração Segura", "points": [
            "Em C++, o operador % com números negativos retorna resultado negativo! Ex: (-5) % 3 = -2.",
            "Isso gera respostas incorretas em contagens e probabilidades modulares.",
            "FÓRMULA SEGURA DE SUBTRAÇÃO: ((A - B) % M + M) % M;",
            "Somar M antes do segundo módulo garante que o resultado seja estritamente não negativo no intervalo [0, M-1]."
        ], "notes": "Essa fórmula de subtração segura é indispensável para evitar valores negativos em problemas de Programação Dinâmica com módulo."},
        {"title": "Exponenciação Modular Rápida (Binary Exponentiation)", "points": [
            "Problema: calcular (A^B) % M onde B pode ser até 10^18.",
            "Multiplicação sequencial ingênua: B passos -> O(B) -> TLE absoluto.",
            "Ideia: se B for par, A^B = (A^(B/2))^2; se B for ímpar, A^B = A * A^(B-1).",
            "Complexidade: O(log B). Para B = 10^18, calcula a potência em apenas 60 multiplicações!"
        ], "notes": "A exponenciação rápida é a chave para calcular potências astronômicas em menos de um microssegundo."},
        {"title": "O Pequeno Teorema de Fermat e Divisão Modular", "points": [
            "Na aritmética modular, a divisão comum (A / B) % M NÃO É IGUAL a ((A % M) / (B % M)) % M!",
            "Para dividir por B, devemos multiplicar pelo INVERSO MODULAR de B: A * B^(-1) % M.",
            "Pequeno Teorema de Fermat: se M for um número primo e B não for múltiplo de M, então: B^(M - 1) ≡ 1 (mod M).",
            "Multiplicando ambos os lados por B^(-1): B^(M - 2) ≡ B^(-1) (mod M)!",
            "Portanto, o inverso modular de B é simplesmente: binpow(B, M - 2, M)!"
        ], "notes": "Essa elegância matemática permite calcular divisões modulares em O(log M) usando a mesma função de exponenciação rápida."},
        {"title": "Análise Combinatória: Coeficientes Binomiais", "points": [
            "Número de maneiras de escolher K itens entre N itens sem repetição: C(N, K) = N! / (K! * (N - K)!).",
            "Módulo M: C(N, K) ≡ fact[N] * invFact[K] * invFact[N - K] (mod M).",
            "Pré-cálculo de fatoriais em O(N): fact[i] = (fact[i-1] * i) % M.",
            "Pré-cálculo de inversos fatoriais em O(N): invFact[N] = inv(fact[N]); invFact[i-1] = (invFact[i] * i) % M.",
            "Após o pré-cálculo O(N), QUALQUER consulta C(N, K) é respondida em tempo O(1) puro!"
        ], "notes": "Com N até 10^6, você pré-calcula os fatoriais no início do programa e responde 10^5 consultas instantaneamente."},
        {"title": "O Triângulo de Pascal para N Pequeno", "points": [
            "Se N for pequeno (N <= 2000) e o módulo M NÃO for primo (ou não permitir inverso modular):",
            "Use a relação fundamental de Stifel: C(N, K) = C(N-1, K-1) + C(N-1, K).",
            "Construa uma matriz bidimensional C[2005][2005] com dois laços for aninhados.",
            "Não utiliza nenhuma divisão, funcionando para QUALQUER módulo, mesmo composto!"
        ], "notes": "O Triângulo de Pascal é a alternativa perfeita quando o módulo M do problema não for um número primo."},
        {"title": "Princípio de Inclusão-Exclusão (PIE) em Contagem", "points": [
            "Para calcular o tamanho da união de múltiplos conjuntos: |A U B U C| = soma(|A|) - soma(|A inter B|) + |A inter B inter C|.",
            "Em geral: somamos as interseções de tamanho ímpar e subtraímos as interseções de tamanho par.",
            "Implementação em maratona: itere sobre todas as 2^K máscaras de bits de subconjuntos de restrições.",
            "Aplicações: contar números coprimos com um conjunto de fatores, desarranjos (derangements) e problemas de coloração."
        ], "notes": "O PIE é a ferramenta que resolve problemas de 'quantos elementos satisfazem pelo menos uma das condições'."},
        {"title": "Multiplicação e Exponenciação de Matrizes", "points": [
            "Multiplicação de duas matrizes K x K: leva tempo O(K^3).",
            "Exponenciação de Matrizes: calcula M^N em tempo O(K^3 * log N) usando o mesmo princípio da exponenciação binária.",
            "Permite resolver qualquer Recorrência Linear homogênea com coeficientes constantes em tempo logarítmico!",
            "Se K <= 5 e N = 10^18, calcula o N-ésimo termo da sequência em menos de 0.01 segundo."
        ], "notes": "Essa técnica transforma problemas de DP linear que levariam O(N) em soluções quase instantâneas O(K^3 log N)."},
        {"title": "Fibonacci em O(log N) via Matrizes", "points": [
            "A recorrência F(n) = F(n-1) + F(n-2) pode ser expressa como vetor de estados: [F(n), F(n-1)] = [[1, 1], [1, 0]] * [F(n-1), F(n-2)].",
            "Aplicando repetidamente: [F(n+1), F(n)] = [[1, 1], [1, 0]]^n * [F(1), F(0)].",
            "Para encontrar o 10^18-ésimo número de Fibonacci módulo 10^9+7, elevamos a matriz 2x2 à potência 10^18 em ~60 multiplicações!",
            "Complexidade: O(8 * log N) tempo e O(1) memória."
        ], "notes": "Um dos problemas clássicos mais recorrentes em seleções de empresas e maratonas de programação."},
        {"title": "Checklist de Matemática para Maratona", "points": [
            "1. Declarou todas as variáveis de multiplicação e acumulação como long long?",
            "2. Aplicou a fórmula de subtração segura com + MOD antes do segundo resto?",
            "3. Garantiu que o módulo M é primo antes de usar o Pequeno Teorema de Fermat para inverso modular?",
            "4. Verificou se a base N=0 ou expoente B=0 são tratados corretamente na exponenciação rápida?"
        ], "notes": "A precisão matemática aliada a tipos de 64 bits garante Accepted limpo em problemas numéricos."}
    ],
    "greedy": [
        {"title": "O Paradigma dos Algoritmos Gulosos (Greedy)", "points": [
            "Um algoritmo guloso constrói a solução passo a passo, sempre fazendo a escolha que parece MELHOR NO MOMENTO (ótimo local).",
            "Diferença da Programação Dinâmica: o guloso NUNCA volta atrás e nunca reconsidera escolhas passadas (não há backtracking).",
            "Vantagem: algoritmos gulosos costumam ser extremamente rápidos (O(N) ou O(N log N)) e simples de codificar.",
            "Perigo: uma escolha local atraente pode levar a um beco sem saída ou a um resultado subótimo global."
        ], "notes": "A maior dificuldade de problemas gulosos não é a implementação, mas provar que a intuição gulosa está matematicamente correta."},
        {"title": "As Duas Condições de Ouro da Estratégia Gulosa", "points": [
            "1. Propriedade da Escolha Gulosa: uma solução ótima global pode ser alcançada fazendo uma escolha ótima local.",
            "2. Subestrutura Ótima: a solução ótima para o problema contém em si as soluções ótimas para os subproblemas restantes.",
            "Se qualquer uma dessas duas propriedades falhar, a abordagem gulosa está condenada ao fracasso e o problema exige DP ou Fluxo.",
            "Sempre tente criar contraexemplos manuais antes de começar a codificar uma ideia gulosa."
        ], "notes": "Tentar 'enganar' sua própria ideia com casos pequenos adversariais é o melhor teste de fogo durante a competição."},
        {"title": "A Técnica do Argumento de Troca (Exchange Argument)", "points": [
            "O método de prova formal mais usado em competições para demonstrar a corretude de um algoritmo guloso.",
            "Suponha que exista uma solução ótima hipotética OPT que difere da solução GULOSA (G).",
            "Mostre que podemos TROCAR um elemento de OPT pelo elemento escolhido por G sem piorar o valor da resposta.",
            "Repetindo a troca indutivamente, transformamos OPT em G sem perda de qualidade, provando que G é tão bom quanto o melhor ótimo possível!"
        ], "notes": "Dominar o argumento de troca permite validar ordenações gulosas com certeza matemática absoluta."},
        {"title": "Problema Clássico 1: Agendamento de Intervalos (Interval Scheduling)", "points": [
            "Problema: dadas N tarefas com início s[i] e fim e[i], selecione o maior número de tarefas compatíveis sem sobreposição.",
            "Tentativa 1: Escolher menor duração? Falha (pode bloquear duas tarefas longas).",
            "Tentativa 2: Escolher menor início? Falha (uma tarefa longa no início bloqueia todas as outras).",
            "ESTRATÉGIA GULOSA CORRETA: Ordene as tarefas pelo TEMPO DE TÉRMINO (e[i]) em ordem crescente!",
            "Sempre pegue a tarefa que termina mais cedo e que não colide com a anterior."
        ], "notes": "Terminar mais cedo é ótimo porque libera o recurso o mais rápido possível para acomodar futuras tarefas."},
        {"title": "Prova do Agendamento de Intervalos por Argumento de Troca", "points": [
            "Seja g1 a primeira tarefa escolhida pelo guloso (menor fim) e o1 a primeira tarefa de uma solução ótima OPT.",
            "Como g1 termina antes ou junto com o1, podemos substituir o1 por g1 em OPT.",
            "Todas as tarefas restantes de OPT continuam compatíveis porque g1 termina antes de o1 começar a liberar tempo!",
            "Portanto, a solução gulosa tem pelo menos tantas tarefas quanto qualquer solução ótima."
        ], "notes": "Uma das demonstrações mais elegantes e didáticas de toda a teoria da computação."},
        {"title": "Problema Clássico 2: Particionamento de Intervalos", "points": [
            "Problema: qual o número mínimo de salas necessárias para acomodar N palestras com horários [inicio, fim]?",
            "Abordagem: ordene todos os eventos de início e fim cronologicamente.",
            "Ao iniciar uma palestra: salas_ativas++ (se salas_ativas > max_salas, max_salas = salas_ativas).",
            "Ao terminar uma palestra: salas_ativas--.",
            "Equivalente a encontrar a sobreposição máxima em qualquer ponto da linha do tempo (resolvido em O(N log N))."
        ], "notes": "Também pode ser resolvido com std::priority_queue armazenando os tempos de liberação das salas ativas."},
        {"title": "Problema Clássico 3: Mochila Fracionária (Fractional Knapsack)", "points": [
            "Problema: itens com valor v[i] e peso w[i]; podemos levar frações de itens. Capacidade máxima W.",
            "Estratégia gulosa: ordene os itens pela densidade de valor por quilo: densidade = v[i] / w[i].",
            "Coloque o máximo que puder do item de maior densidade até encher a mochila.",
            "Complexidade: O(N log N) para ordenar.",
            "CUIDADO: Se os itens forem inteiros (Mochila 0-1, onde só pode levar 0% ou 100%), o guloso FALHA e exige Programação Dinâmica!"
        ], "notes": "A distinção entre mochila fracionária (guloso) e mochila 0-1 (DP) é a clássica questão conceitual de entrevistas e maratonas."},
        {"title": "Problema Clássico 4: Codificação de Huffman", "points": [
            "Problema: comprimir dados atribuindo códigos binários de tamanho variável para caracteres de acordo com sua frequência.",
            "Caracteres mais frequentes devem receber códigos mais curtos; nenhum código pode ser prefixo de outro (Prefix-Free Code).",
            "Algoritmo Guloso: coloque todas as frequências em um Min-Heap (priority_queue).",
            "Retire os dois menores nós, crie um nó pai com a soma das frequências e reinsira no heap até sobrar uma única árvore.",
            "Complexidade: O(N log N). Produz a compressão prefixada comprovadamente ótima."
        ], "notes": "David Huffman inventou esse algoritmo enquanto era estudante de doutorado no MIT em 1952 para um trabalho de disciplina."},
        {"title": "Guloso em Grafos: Algoritmo de Kruskal (MST)", "points": [
            "Objetivo: encontrar a Árvore Geradora Mínima (Minimum Spanning Tree) de um grafo ponderado conectado.",
            "Estratégia gulosa pura: ordene todas as arestas em ordem crescente de peso.",
            "Para cada aresta (u, v): se u e v já estiverem conectados no mesmo conjunto, descarte; senão, adicione a aresta à MST e una os conjuntos com DSU!",
            "Complexidade: O(E log E) para ordenar as arestas + O(E * α(V)) para as operações de DSU."
        ], "notes": "A simplicidade de Kruskal combinada com DSU faz dele a implementação favorita de MST em maratonas."},
        {"title": "Guloso em Grafos: Algoritmo de Prim (MST)", "points": [
            "Constrói a MST crescendo a partir de um vértice inicial.",
            "Mantém um Min-Heap com todas as arestas que conectam a árvore atual a vértices ainda não visitados.",
            "A cada passo: retira a aresta mais leve que conecta a um vértice novo e marca como visitado.",
            "Complexidade: O(E log V) usando std::priority_queue.",
            "Mais rápido que Kruskal em grafos muito densos onde E aproxima-se de V^2."
        ], "notes": "Prim e Dijkstra compartilham exatamente a mesma estrutura algorítmica, diferindo apenas na função de relaxamento da prioridade."},
        {"title": "Guloso em Grafos: O Algoritmo de Dijkstra", "points": [
            "Dijkstra é fundamentalmente um algoritmo GULOSO!",
            "Invariante: no momento em que um vértice u é retirado do Min-Heap com menor distância temporária, sua distância real está DEFINITIVAMENTE CONSOLIDADA.",
            "Por que falha com arestas negativas? Porque arestas negativas violam a invariante gulosa de que avançar no caminho só pode aumentar a distância!",
            "Para arestas negativas, a abordagem gulosa deve ser substituída por Programação Dinâmica (Bellman-Ford / SPFA)."
        ], "notes": "Compreender por que Dijkstra é guloso esclarece de uma vez por todas por que pesos negativos quebram o algoritmo."},
        {"title": "Minimizando Somas de Distâncias: A Mediana", "points": [
            "Problema: escolher um ponto X que minimize a soma das distâncias |x[i] - X| para N pontos em uma reta.",
            "Tentativa errada: escolher a média aritmética (a média minimiza a soma dos quadrados das distâncias, não o valor absoluto!).",
            "ESCOLHA GULOSA CORRETA: A MEDIANA dos pontos!",
            "Ordene o array; se N for ímpar, X = arr[N / 2]. Mover X para a esquerda ou direita a partir da mediana sempre aumenta mais distâncias do que diminui."
        ], "notes": "Problema extremamente frequente em maratona disfarçado de 'ponto de encontro ideal' ou 'depósito central'."},
        {"title": "O Truque do Guloso com Reembolso (Regret Greedy)", "points": [
            "Problema avançado: tomamos uma decisão gulosa agora, mas guardamos a opção de DESFAZER a decisão mais tarde se surgir algo melhor.",
            "Implementação: use uma std::priority_queue para rastrear as escolhas anteriores.",
            "Se encontrarmos um elemento no futuro que oferece benefício superior ao pior elemento escolhido anteriormente, trocamos!",
            "Mantém a complexidade O(N log N) e resolve problemas que pareciam exigir DP com limites grandes."
        ], "notes": "Técnica favorita do Codeforces Div. 1 para problemas de compra e venda de ações ou consumo de poções de vida."},
        {"title": "O Problema do Troco: Canônico vs Não-Canônico", "points": [
            "Para sistemas de moedas canônicos (como o Real brasileiro: 100, 50, 20, 10, 5, 2, 1), o algoritmo guloso sempre dá o menor número de moedas.",
            "MAS para sistemas arbitrários, o guloso pode falhar espetacularmente!",
            "Exemplo: moedas de {1, 3, 4} e troco 6. Guloso escolhe 4 + 1 + 1 = 3 moedas. A solução ótima real é 3 + 3 = 2 moedas!",
            "Moral da história: em sistemas de moedas arbitrários, SEMPRE use Programação Dinâmica."
        ], "notes": "Sempre verifique se o sistema de moedas do problema tem garantia canônica antes de aplicar a estratégia gulosa."},
        {"title": "Problema de Minimizar o Maior Atraso (Lateness)", "points": [
            "Tarefas com duração p[i] e prazo limite d[i]. Queremos minimizar o atraso máximo: max(0, conclusao[i] - d[i]).",
            "Regra de Jackson: ordene as tarefas por PRAZO LIMITE (Earliest Deadline First - EDF) em ordem crescente.",
            "Demonstração por troca: se duas tarefas adjacentes estiverem fora da ordem de prazo, trocá-las nunca aumenta o atraso máximo entre elas.",
            "Complexidade: O(N log N) para ordenar e O(N) para simular."
        ], "notes": "A regra EDF é aplicada em sistemas operacionais de tempo real para escalonamento ótimo de tarefas."},
        {"title": "Gulosos em Strings e Rearranjos", "points": [
            "Problema: reorganizar caracteres de uma string para que nenhum caractere adjacente seja repetido.",
            "Estratégia gulosa: use um Max-Heap com a contagem de cada caractere.",
            "A cada passo: retire o caractere mais frequente, coloque na string, e mantenha-o em espera até o próximo caractere ser colocado para não repetir.",
            "Se em algum momento o caractere mais frequente tiver frequência > (N + 1) / 2, é matematicamente impossível."
        ], "notes": "Acompanhar a frequência máxima com priority queue resolve problemas de intercalação em tempo O(N log(alfabeto))."},
        {"title": "Quando Desconfiar de uma Abordagem Gulosa", "points": [
            "Desconfie imediatamente se: você precisa fazer uma escolha sem saber o que vem pela frente, e escolhas passadas limitam opções futuras.",
            "Desconfie se o problema tem restrições de 'capacidade exata' (como a Mochila 0-1).",
            "Desconfie se você não consegue articular um argumento de troca sólido no papel.",
            "Se você criar um caso de teste pequeno de 4 números onde a lógica falha, pare imediatamente e pense em DP."
        ], "notes": "Saber quando NÃO usar guloso economiza horas preciosas de contest evitando implementar heurísticas furadas."},
        {"title": "Como Validar o Guloso com Stress Testing", "points": [
            "Em caso de dúvida durante o contest:",
            "1. Escreva uma solução de força bruta com busca recursiva em 10 linhas.",
            "2. Escreva sua solução gulosa candidata.",
            "3. Gere 10.000 testes aleatórios pequenos (N=5 a 10) e compare as duas respostas.",
            "Se as respostas baterem em 10.000 testes aleatórios, sua intuição gulosa tem 99.9% de chance de estar correta. Submeta com confiança!"
        ], "notes": "Stress testing é a rede de segurança dos maratonistas veteranos para submeter soluções gulosas sem medo de WA."},
        {"title": "Resumo de Padrões Gulosos Mais Frequentes", "points": [
            "1. Interval Scheduling: ordenar pelo fim do intervalo.",
            "2. Interval Partitioning: ordenar pelo início e usar priority_queue para recursos livres.",
            "3. Minimização de atraso: ordenar pelo prazo limite (EDF).",
            "4. Huffman / Agrupamento de menores: Min-Heap para fundir os 2 menores recursivamente.",
            "5. Mediana: minimizar soma de distâncias absolutas em uma dimensão."
        ], "notes": "Decorar esses 5 padrões clássicos permite reconhecer soluções gulosas em segundos durante a leitura do caderno."}
    ],
    "dp": [
        {"title": "O que é Programação Dinâmica (DP)?", "points": [
            "Programação Dinâmica é uma técnica que resolve problemas complexos quebrando-os em subproblemas sobrepostos e memorizando seus resultados.",
            "O nome 'Programação' vem do termo matemático original (planejamento de tabelas), não de programação de computadores.",
            "A regra de ouro: NUNCA RESOLVA O MESMO SUBPROBLEMA DUAS VEZES!",
            "Transforma algoritmos de tempo exponencial O(2^N) em algoritmos polinomiais O(N), O(N^2) ou O(N * W)."
        ], "notes": "Richard Bellman cunhou o termo na década de 1950 enquanto trabalhava na RAND Corporation."},
        {"title": "As Duas Propriedades Obrigatórias de DP", "points": [
            "1. Subestrutura Ótima: a solução ótima para o problema pode ser construída a partir das soluções ótimas de seus subproblemas.",
            "2. Subproblemas Sobrepostos (Overlapping Subproblems): a recursão ingênua visita os mesmos estados repetidas vezes.",
            "Exemplo de Fibonacci ingênuo: fib(5) chama fib(4) e fib(3); fib(4) chama fib(3) e fib(2). fib(3) é recalculado do zero!",
            "Com DP, armazenamos o valor de fib(3) na primeira vez que ele é calculado e o reutilizamos em O(1)."
        ], "notes": "Se os subproblemas não se sobrepuserem (como no Merge Sort), trata-se de Divisão e Conquista simples, não de DP."},
        {"title": "Abordagem 1: Top-Down (Recursão com Memorização)", "points": [
            "Escreva a solução recursiva natural baseada na definição matemática do problema.",
            "Crie uma tabela de memória (ex: int memo[N][M]) inicializada com -1 (indicando 'não calculado').",
            "No início da função: if (memo[estado] != -1) return memo[estado];",
            "Antes de retornar: return memo[estado] = calculo_recursivo;",
            "Vantagem: só calcula os estados que são estritamente necessários para alcançar a resposta."
        ], "notes": "A abordagem Top-Down é muito intuitiva para começar a pensar porque segue diretamente a intuição recursiva."},
        {"title": "Abordagem 2: Bottom-Up (Tabulação Iterativa)", "points": [
            "Preencha a tabela de DP iterativamente usando laços for, começando dos casos base até o estado final.",
            "Não utiliza recursão nem consome memória de pilha de chamadas.",
            "Vantagens: mais rápida (sem overhead de chamadas de função), melhor localidade de cache e imune a Stack Overflow.",
            "Permite otimizações fáceis de memória (como descartar linhas antigas)."
        ], "notes": "Em maratona, a abordagem Bottom-Up é frequentemente preferida por sua velocidade e segurança de memória."},
        {"title": "As Quatro Etapas de Ouro para Modelar Qualquer DP", "points": [
            "1. Definição do Estado: O que dp[i][j] significa em português claro? (Ex: 'o menor custo usando os primeiros i itens com peso j').",
            "2. Transição: Como calcular dp[i][j] usando estados menores já resolvidos?",
            "3. Casos Base: Quais são as respostas triviais iniciais? (Ex: dp[0] = 0).",
            "4. Ordem de Avaliação: Em qual ordem os laços devem rodar para que os estados menores já estejam prontos ao calcular os maiores?"
        ], "notes": "Se você não conseguir definir o significado do estado em uma frase clara de português, você ainda não entendeu a DP."},
        {"title": "O DAG dos Estados de Programação Dinâmica", "points": [
            "Toda Programação Dinâmica é matematicamente equivalente a encontrar o menor ou maior caminho em um DAG (Grafo Acíclico Dirigido)!",
            "Cada estado da DP é um vértice do DAG.",
            "Cada transição é uma aresta direcionada conectando o estado dependente ao estado menor.",
            "A ordem de avaliação dos laços no Bottom-Up nada mais é do que uma Ordenação Topológica desse DAG!"
        ], "notes": "Essa equivalência entre DP e caminhos em DAGs é uma das conexões mais profundas da ciência da computação."},
        {"title": "Problema Clássico 1: 0-1 Knapsack (Mochila 0-1)", "points": [
            "Problema: N itens com peso w[i] e valor v[i]. Mochila com capacidade máxima W. Cada item pode ser levado 0 ou 1 vez.",
            "Estado: dp[i][c] = valor máximo usando um subconjunto dos primeiros i itens com peso total <= c.",
            "Transição: para o item i, temos duas opções:",
            "- Não levar o item: dp[i-1][c]",
            "- Levar o item (se w[i] <= c): dp[i-1][c - w[i]] + v[i]",
            "dp[i][c] = max(dp[i-1][c], dp[i-1][c - w[i]] + v[i])."
        ], "notes": "Complexidade: O(N * W) tempo e O(N * W) memória. Trata-se de um problema pseudo-polinomial (NP-completo no tamanho dos bits)."},
        {"title": "Otimização de Espaço da Mochila para O(W)", "points": [
            "Observe que a linha dp[i] só depende diretamente da linha imediatamente anterior dp[i-1]!",
            "Podemos usar um único vetor unidimensional dp[c] de tamanho W + 1.",
            "PONTO CRÍTICO: Itere a capacidade c DE TRÁS PARA FRENTE (de W descendo até w[i])!",
            "for (int c = W; c >= w[i]; c--) dp[c] = max(dp[c], dp[c - w[i]] + v[i]);",
            "Por que de trás para frente? Para que dp[c - w[i]] ainda represente o valor da iteração anterior, impedindo que o mesmo item seja reutilizado!"
        ], "notes": "Se você iterar de frente para trás (c de w[i] até W), você resolve a Mochila Ilimitada (Unbounded Knapsack), onde itens podem ser repetidos infinitamente."},
        {"title": "Problema Clássico 2: Problema do Troco (Coin Change)", "points": [
            "Problema: moedas com valores {c1, c2, ..., ck}. Qual o MENOR número de moedas para somar o valor X?",
            "Estado: dp[s] = menor número de moedas para formar a soma s.",
            "Base: dp[0] = 0; todos os outros inicializados com infinito.",
            "Transição: dp[s] = min_{c in moedas} (dp[s - c] + 1) para todo c <= s.",
            "Complexidade: O(K * X) tempo e O(X) memória."
        ], "notes": "Para contar o número de MANEIRAS distintas de dar o troco: dp[s] = soma(dp[s - c])."},
        {"title": "A Ordem dos Laços Muda a Contagem de Maneiras!", "points": [
            "Se o laço de moedas estiver FORA e o de valores DENTRO: conta COMBINAÇÕES (ordem das moedas não importa: 1+2 é o mesmo que 2+1).",
            "for (int c : coins) for (int s = c; s <= X; s++) dp[s] = (dp[s] + dp[s - c]) % MOD;",
            "Se o laço de valores estiver FORA e o de moedas DENTRO: conta PERMUTAÇÕES (ordem importa: 1+2 é diferente de 2+1)!",
            "for (int s = 1; s <= X; s++) for (int c : coins) if (s >= c) dp[s] = (dp[s] + dp[s - c]) % MOD;"
        ], "notes": "Esse é um dos testes conceituais mais famosos de maratona: a simples inversão de dois laços altera a semântica de combinações para permutações."},
        {"title": "Problema Clássico 3: Longest Increasing Subsequence (LIS)", "points": [
            "Problema: encontrar o comprimento da maior subsequência estritamente crescente de um array A.",
            "Abordagem O(N^2): dp[i] = comprimento da maior LIS que termina no elemento A[i].",
            "Transição: dp[i] = 1 + max_{j < i e A[j] < A[i]} (dp[j]).",
            "Base: dp[i] = 1 para todo i.",
            "Resposta global: max(dp[1], dp[2], ..., dp[N])."
        ], "notes": "A abordagem O(N^2) é intuitiva e aceita até N = 5000."},
        {"title": "Otimizando LIS para O(N log N) com Busca Binária", "points": [
            "Para N = 2 * 10^5, O(N^2) dá TLE! Precisamos de O(N log N).",
            "Mantenha um vetor tails[], onde tails[len] guarda o MENOR elemento final de todas as subsequências crescentes de tamanho len vistas até agora.",
            "Invariante crucial: o vetor tails[] é estritamente crescente!",
            "Para cada elemento x de A: use std::lower_bound para encontrar a primeira posição em tails com valor >= x e substitua-o por x (ou insira no fim se x for maior que todos).",
            "Tamanho final de tails é o comprimento exato da LIS!"
        ], "notes": "A substituição com lower_bound torna a subsequência futura mais promissora para aceitar novos elementos menores."},
        {"title": "Problema Clássico 4: Caminhos em Grid 2D", "points": [
            "Problema: em uma matriz N x M, você começa em (1, 1) e só pode mover para a Direita ou para Baixo. Quantos caminhos levam a (N, M)?",
            "Estado: dp[r][c] = número de caminhos de (1, 1) até (r, c).",
            "Transição: dp[r][c] = dp[r - 1][c] + dp[r][c - 1] (se a célula não for obstáculo).",
            "Base: dp[1][1] = 1.",
            "Se cada célula tiver um custo: dp[r][c] = min(dp[r - 1][c], dp[r][c - 1]) + custo[r][c]."
        ], "notes": "Caminhos em grids são a porta de entrada visual para compreender DP bidimensional."},
        {"title": "Problema Clássico 5: Distância de Edição (Edit Distance)", "points": [
            "Problema: menor número de operações (inserir, deletar, substituir) para transformar a string A de tamanho N na string B de tamanho M.",
            "Estado: dp[i][j] = menor custo para converter o prefixo A[1..i] no prefixo B[1..j].",
            "Se A[i] == B[j]: dp[i][j] = dp[i-1][j-1] (sem custo adicional).",
            "Se A[i] != B[j]: dp[i][j] = 1 + min({dp[i-1][j] (deletar), dp[i][j-1] (inserir), dp[i-1][j-1] (substituir)}).",
            "Complexidade: O(N * M) tempo e memória."
        ], "notes": "Esse algoritmo de Levenshtein (1965) é usado até hoje em corretores ortográficos e ferramentas como git diff."},
        {"title": "Reconstrução da Resposta (Backtracking na DP)", "points": [
            "Muitas vezes o problema não quer apenas o valor máximo (ex: lucro 42), mas QUUAIS ITENS foram escolhidos.",
            "Método 1: tabela de pais parent[i][j] que guarda qual transição produziu o ótimo.",
            "Método 2 (sem memória extra): após preencher a tabela de DP, comece do estado final e compare com os estados anteriores:",
            "Se dp[i][c] == dp[i-1][c - w[i]] + v[i], o item i com certeza foi incluído! Recue para dp[i-1][c - w[i]].",
            "Senão, o item i foi ignorado: recue para dp[i-1][c]."
        ], "notes": "Reconstruir a resposta comparando com a tabela dispensa armazenar matrizes extras de ponteiros."},
        {"title": "Introdução a Bitmask DP (DP com Máscaras de Bits)", "points": [
            "Quando o tamanho N for pequeno (N <= 20), podemos representar subconjuntos usando inteiros de 32 bits!",
            "Se o i-ésimo bit estiver ligado ((mask >> i) & 1), o elemento i pertence ao subconjunto.",
            "Estado típico: dp[mask][u] = menor custo visitando o conjunto de vértices representado por mask terminando no nó u.",
            "Problema do Caixeiro Viajante (TSP): resolvido em O(N^2 * 2^N) em vez do fatorial O(N!)."
        ], "notes": "Com N = 20, 2^20 é cerca de 10^6, permitindo resolver o problema NP-difícil do caixeiro viajante em menos de 0.2 segundos."},
        {"title": "Otimizações de Memória em DP: A Técnica de Rolagem", "points": [
            "Se a linha dp[i] só depende da linha dp[i-1], não precisamos manter todas as N linhas na memória!",
            "Use apenas duas linhas: dp[2][M] com indexação modular dp[i % 2][j].",
            "Reduz o consumo de memória de O(N * M) para O(M).",
            "Essencial quando N = 10^5 e M = 10^4, onde a matriz completa consumiria 4 GB de RAM (MLE)."
        ], "notes": "O operador de módulo binário i & 1 é ainda mais rápido que i % 2 para alternar entre as linhas 0 e 1."},
        {"title": "Digit DP (DP em Dígitos)", "points": [
            "Problema: contar quantos números entre A e B satisfazem uma certa propriedade (ex: soma dos dígitos é prima).",
            "Abordagem: resolva para [0, B] e subtraia o resultado para [0, A - 1].",
            "Estado: dp[pos][soma][tight][leading_zeros].",
            "tight = 1 significa que os dígitos anteriores coincidem com o prefixo de B (o próximo dígito não pode passar do dígito de B).",
            "tight = 0 significa que o número já é estritamente menor que B e podemos colocar qualquer dígito de 0 a 9."
        ], "notes": "Digit DP resolve problemas com limites de números até 10^18 em menos de 18 passos de recursão."},
        {"title": "Erros Fatais de DP em Maratonas", "points": [
            "1. Ordem incorreta de avaliação: usar um estado antes dele ter sido computado (gera lixo ou 0).",
            "2. Não inicializar com -1 no Top-Down (faz a função recalcular estados que retornam 0 repetidamente, dando TLE).",
            "3. Esquecer os casos base (gera chamadas recursivas com índices negativos e RTE).",
            "4. Não usar long long quando as somas ou contagens de DP podem crescer até 10^18."
        ], "notes": "Sempre certifique-se de que a tabela de memorização é inicializada com memset(memo, -1, sizeof(memo)) antes de cada caso de teste."},
        {"title": "Checklist Definitivo de Programação Dinâmica", "points": [
            "1. Definiu com clareza em português o significado de dp[i][j]?",
            "2. Identificou todas as transições possíveis com custo/ganho?",
            "3. Escreveu os casos base antes de qualquer laço?",
            "4. A ordem dos laços garante que subproblemas menores são processados primeiro?",
            "5. Se o problema pede resposta módulo M, aplicou o módulo em todas as adições de estados?"
        ], "notes": "Com esse checklist rigoroso, DP deixa de ser um mistério e se torna um método determinístico de resolução."}
    ],
    "tree": [
        {"title": "Árvores na Teoria dos Grafos", "points": [
            "Uma árvore é um grafo conexo e acíclico.",
            "Propriedades equivalentes fundamentais para um grafo de V vértices:",
            "- G é conexo e possui exatamente V - 1 arestas.",
            "- G é acíclico e possui exatamente V - 1 arestas.",
            "- Existe exatamente UM caminho simples entre qualquer par de vértices u e v.",
            "- Adicionar qualquer aresta nova cria exatamente um ciclo."
        ], "notes": "Essa unicidade do caminho entre quaisquer dois nós torna algoritmos em árvores muito mais simples e eficientes que em grafos gerais."},
        {"title": "Árvores com Raiz (Rooted Trees)", "points": [
            "Fixar um vértice como RAIZ estabelece uma hierarquia orientada natural sobre toda a árvore.",
            "Relações familiares: Pai (parent), Filhos (children), Ancestrais e Descendentes.",
            "Vértices sem filhos são chamados de FOLHAS (leaves).",
            "Subárvore de u: o subgrafo composto por u e todos os seus descendentes."
        ], "notes": "A maioria dos algoritmos de programação competitiva trata árvores como enraizadas em um nó conveniente (geralmente o nó 1)."},
        {"title": "Representação de Árvores em C++", "points": [
            "Armazene a árvore como uma lista de adjacência não-direcionada: vector<int> adj[N];",
            "A GRANDE VANTAGEM: em árvores, NÃO precisamos de array de visitados (visited[])!",
            "Basta passar o PAI como parâmetro na recursão: void dfs(int u, int p) { for (int v : adj[u]) if (v != p) dfs(v, u); }",
            "A condição 'v != p' impede que a busca retorne pelo caminho de onde veio, garantindo visita linear O(V)."
        ], "notes": "Eliminar o array visited passando o pai economiza memória e deixa o código extremamente conciso."},
        {"title": "Travessias Clássicas em Árvores", "points": [
            "Pré-Ordem (Pre-Order): visita a raiz antes dos filhos (u -> filhos).",
            "Pós-Ordem (Post-Order): visita todos os filhos antes da raiz (filhos -> u). Ideal para calcular propriedades de subárvores de baixo para cima.",
            "Em-Ordem (In-Order): aplicável a árvores binárias (filho esquerdo -> raiz -> filho direito). Produz elementos em ordem crescente em BSTs.",
            "Todas as travessias executam em tempo O(V) estritamente linear."
        ], "notes": "A pós-ordem é o coração da Tree DP: você resolve os filhos primeiro e combina seus resultados para resolver o pai."},
        {"title": "Cálculo de Tamanhos e Alturas de Subárvores", "points": [
            "sz[u]: número de nós na subárvore de u. Inicializa sz[u] = 1; para cada filho v, sz[u] += sz[v].",
            "depth[u]: distância da raiz até o nó u. depth[u] = depth[p] + 1 com depth[raiz] = 0.",
            "height[u]: maior distância de u até uma folha de sua subárvore. height[u] = 1 + max(height[v]).",
            "Todas essas grandezas fundamentais são calculadas em uma única passada de DFS em O(V)."
        ], "notes": "Saber o tamanho de cada subárvore é o pré-requisito para decomposições pesadas (Centroid Decomposition e HLD)."},
        {"title": "O Euler Tour (Achatamento de Árvores)", "points": [
            "Técnica genial que mapeia uma árvore hierárquica em um array unidimensional simples!",
            "Registre o tempo de entrada tin[u] e de saída tout[u] com um contador global durante a DFS.",
            "PROPRIEDADE MÁGICA: Todos os nós da subárvore de u caem exatamente no intervalo contíguo [tin[u], tout[u]] do Euler Tour!",
            "Isso transforma qualquer consulta ou atualização em subárvores em uma consulta de intervalo 1D (usando Prefix Sums ou SegTree)!"
        ], "notes": "Achatamento de árvores com Euler Tour é um dos tópicos favoritos das etapas nacionais da Maratona e OBI."},
        {"title": "Diâmetro de uma Árvore: Definição", "points": [
            "O diâmetro de uma árvore é o comprimento do MAIOR caminho simples entre quaisquer dois vértices da árvore.",
            "É a maior distância entre dois nós na árvore inteira.",
            "Aplicações: encontrar a rede de menor latência máxima, balanceamento de servidores e raio de cobertura."
        ], "notes": "Em árvores ponderadas, o diâmetro considera a soma dos pesos das arestas."},
        {"title": "O Algoritmo dos Dois BFS/DFS para Diâmetro", "points": [
            "Algoritmo extremamente simples e elegante em O(V):",
            "Passo 1: Escolha um nó inicial arbitrário qualquer (ex: nó 1). Execute uma BFS/DFS e encontre o nó 'A' mais distante de 1.",
            "Passo 2: Execute uma segunda BFS/DFS a partir do nó 'A' e encontre o nó 'B' mais distante de A.",
            "A distância entre A e B é GARANTIDAMENTE o diâmetro da árvore, e o caminho entre eles é o caminho diametral!"
        ], "notes": "Funciona para qualquer árvore com pesos de arestas não negativos em tempo linear O(V + E)."},
        {"title": "Por que o Algoritmo dos Dois BFS Funciona? (Demonstração)", "points": [
            "Teorema: A partir de qualquer nó inicial x, o nó mais distante y pertence a uma das extremidades de algum diâmetro da árvore.",
            "Intuição geométrica: o caminho de x até o diâmetro intercepta o diâmetro em algum nó intermediário.",
            "Para maximizar a distância a partir de x, o caminho mais longo é forçado a seguir até uma das pontas do diâmetro.",
            "Portanto, a segunda busca partindo da ponta A necessariamente alcança a ponta oposta B."
        ], "notes": "Essa prova é um clássico de teoria dos grafos e garante a corretude do método."},
        {"title": "O Centro de uma Árvore", "points": [
            "O centro de uma árvore é o vértice que MINIMIZA a maior distância até qualquer outro nó (o nó mais 'central' da rede).",
            "Toda árvore possui exatamente UM ou DOIS centros.",
            "Como encontrar: o(s) centro(s) é(são) exatamente o(s) nó(s) no MEIO do caminho diametral!",
            "Se o diâmetro tiver comprimento par D = 2k, o centro é único a k passos de A. Se for ímpar D = 2k + 1, existem dois centros adjacentes."
        ], "notes": "Enraizar uma árvore em seu centro produz a menor altura possível da árvore (altura = ceil(D / 2))."},
        {"title": "Tree DP: Programação Dinâmica em Árvores", "points": [
            "Problema clássico: Maior Conjunto Independente em Árvore (Maximum Independent Set).",
            "Conjunto de nós sem arestas entre si. Cada nó tem peso. Queremos a maior soma de pesos.",
            "Estado para cada nó u: dp[u][0] (u NÃO é incluído) e dp[u][1] (u É incluído).",
            "Transições: se u não é incluído, os filhos podem ou não ser incluídos: dp[u][0] = soma(max(dp[v][0], dp[v][1])).",
            "Se u é incluído, NENHUM filho pode ser incluído: dp[u][1] = peso[u] + soma(dp[v][0])."
        ], "notes": "Tree DP é resolvida em O(V) com uma simples DFS em pós-ordem que combina os valores dos filhos."},
        {"title": "Re-enraizamento em Árvores (Rerooting DP)", "points": [
            "Problema: para CADA vértice u da árvore, calcular a soma das distâncias de u para todos os outros nós.",
            "Abordagem ingênua: rodar uma BFS para cada nó -> O(V^2) -> TLE para V = 2 * 10^5.",
            "Abordagem de Rerooting em O(V):",
            "Passo 1: Calcule a resposta para a raiz arbitrária 1 com uma DFS subindo.",
            "Passo 2: Com uma segunda DFS descendo, transfira a raiz de pai para filho em O(1): ao descer para o filho v, nós na subárvore de v ficam 1 passo mais perto, e nós fora da subárvore ficam 1 passo mais longe!",
            "Fórmula de transição: ans[v] = ans[u] - sz[v] + (N - sz[v])."
        ], "notes": "O padrão de Rerooting em duas passadas é um dos tópicos de nível avançado mais bonitos de maratonas internacionais."},
        {"title": "O Problema do Menor Ancestral Comum (LCA)", "points": [
            "LCA(u, v): o nó mais profundo na árvore que é ancestral simultaneamente de u e de v.",
            "É o ponto onde os caminhos da raiz até u e da raiz até v divergem.",
            "Fundamental para calcular distâncias entre nós em O(log N): dist(u, v) = depth[u] + depth[v] - 2 * depth[LCA(u, v)].",
            "Aplicações: consultas em caminhos, menor caminho em redes, genealogia."
        ], "notes": "Quase qualquer problema de consultas em caminhos de árvore se reduz a encontrar o LCA dos nós."},
        {"title": "Abordagem Ingênua de LCA e seus Limites", "points": [
            "Abordagem 1: suba o nó mais profundo até que u e v estejam na mesma profundidade. Depois, suba ambos nó a nó até que se encontrem.",
            "No melhor caso (árvore perfeitamente balanceada): O(log N).",
            "No pior caso (árvore degenerada em linha reta): a profundidade é O(N). Para Q consultas, o tempo total é O(Q * N) -> TLE!",
            "Precisamos de uma técnica que responda cada consulta em tempo O(log N) independente do formato da árvore."
        ], "notes": "Em maratona, juízes com testes adversariais sempre incluem árvores em linha para derrubar o LCA ingênuo."},
        {"title": "Subida Binária (Binary Lifting para LCA)", "points": [
            "A técnica padrão absoluta para responder consultas de LCA em O(log N).",
            "Pré-cálculo: matriz up[N][20], onde up[u][i] é o 2^i-ésimo ancestral do nó u.",
            "Recorrência: up[u][0] = pai[u]; up[u][i] = up[up[u][i-1]][i-1] (saltar 2^i passos é o mesmo que saltar 2^(i-1) passos duas vezes!).",
            "Tempo de pré-cálculo: O(N log N) com uma DFS inicial."
        ], "notes": "Como 2^19 > 5 * 10^5, uma tabela com 20 colunas é suficiente para qualquer árvore com até 500.000 nós."},
        {"title": "Como Responder a Consulta de LCA em O(log N)", "points": [
            "Passo 1: Suponha depth[u] >= depth[v]. Se u for mais profundo, use potências de 2 decrescentes para subir u até que depth[u] == depth[v].",
            "Passo 2: Se após nivelar u == v, o próprio v era ancestral de u, retorne v imediatamente!",
            "Passo 3: Se u != v, tente saltar potências 2^19, 2^18, ..., 2^0 com ambos u e v simulaneamente. Se up[u][i] != up[v][i], dê o salto!",
            "No final, u e v estarão imediatamente abaixo do LCA. Retorne up[u][0] (o pai de u)."
        ], "notes": "Cada consulta faz no máximo 20 iterações em C++, respondendo em menos de 1 microssegundo."},
        {"title": "Consultas de Mínimo/Máximo em Caminhos com Binary Lifting", "points": [
            "Podemos estender a tabela up[u][i] para carregar grandezas ao longo do caminho!",
            "max_edge[u][i]: maior peso de aresta nos 2^i saltos acima de u.",
            "Recorrência: max_edge[u][i] = max(max_edge[u][i-1], max_edge[up[u][i-1]][i-1]).",
            "Permite responder: 'qual a aresta mais pesada no caminho entre u e v?' em O(log N) consultas!"
        ], "notes": "Combina o conceito de Sparse Table com a estrutura de árvore de forma unificada."},
        {"title": "Somas de Prefixos em Árvores", "points": [
            "Problema: somar valores em caminhos de árvore de u até v.",
            "Seja pref[u] a soma acumulada dos valores dos nós desde a raiz até o nó u.",
            "Fórmula da soma no caminho entre u e v:",
            "Soma(u, v) = pref[u] + pref[v] - pref[LCA(u, v)] - pref[pai(LCA(u, v))].",
            "Responde a soma de qualquer caminho em tempo O(log N) (tempo para achar o LCA)!"
        ], "notes": "Exatamente o análogo em árvore da fórmula de inclusão-exclusão de prefix sums unidimensional."},
        {"title": "Armadilhas de Maratona em Árvores", "points": [
            "1. Árvores em linha: nunca use recursões sem garantir que a pilha do sistema suporte profundidade N.",
            "2. Árvores com pesos negativos: o diâmetro pode não coincidir com o método de 2 BFS (exige DP).",
            "3. Nó raiz especial: acessar pai da raiz no cálculo de LCA pode acessar índice 0 com lixo de memória se não inicializado com 0.",
            "4. Esquecer que N nós em uma árvore implicam exatamente N - 1 arestas."
        ], "notes": "Sempre aponte up[raiz][i] = raiz para que saltos além da raiz permaneçam na própria raiz de forma segura."},
        {"title": "Checklist de Árvores para Competições", "points": [
            "1. Implementou a DFS passando o nó pai (u, p) para evitar array de visitados?",
            "2. O tamanho da matriz de binary lifting tem colunas suficientes (log2(N) + 1)?",
            "3. Tratou o caso de consultas onde u == v ou onde um nó é ancestral direto do outro?",
            "4. Verificou se a árvore é 1-indexed para evitar conflito com nó 0?"
        ], "notes": "Com este checklist, qualquer problema clássico de árvores na OBI ou ICPC é resolvido com código limpo e seguro."}
    ]
}

def main():
    print("Atualizando learning_content.json com Parte 3 (math, greedy, dp, tree e binary)...")
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    
    # Adiciona o 20º slide para binary
    for topic in data["topics"]:
        if topic["id"] == "binary" and len(topic["slides"]) == 19:
            topic["slides"].append(PART3_SLIDES["binary_extra"])
            print("  ✓ binary: completado para 20 slides.")

    for topic in data["topics"]:
        tid = topic["id"]
        if tid in PART3_SLIDES and tid != "binary_extra":
            topic["slides"] = PART3_SLIDES[tid]
            print(f"  ✓ {tid}: atualizado para {len(topic['slides'])} slides.")
            
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Concluído Parte 3!")

if __name__ == "__main__":
    main()
