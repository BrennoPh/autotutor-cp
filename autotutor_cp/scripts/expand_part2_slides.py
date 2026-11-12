"""Part 2: 20-slide decks for prefix, binary, math, greedy, dp, and tree."""
import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "learning_content.json"

PART2_SLIDES = {
    "prefix": [
        {"title": "O Desafio das Consultas Repetidas", "points": [
            "Problema: dado um array de tamanho N, responda a Q consultas perguntando a soma dos elementos entre os índices L e R.",
            "Abordagem ingênua: iterar de L a R para cada consulta. Custo: O(N) por consulta, total O(Q * N).",
            "Com N = 2 * 10^5 e Q = 2 * 10^5, Q * N = 4 * 10^10 operações -> TLE certo (demoraria ~400 segundos!).",
            "A técnica de Soma de Prefixos pré-calcula a resposta para responder qualquer consulta em O(1) estrito."
        ], "notes": "Soma de prefixos é a primeira otimização de complexidade que todo competidor deve dominar."},
        {"title": "A Invariante Matemática da Soma de Prefixos", "points": [
            "Definição: P[k] é a soma de todos os elementos desde o início até o índice k.",
            "Recorrência: P[0] = 0 e P[k] = P[k-1] + A[k] para k >= 1.",
            "Pré-processamento: um único laço de 1 a N preenche todo o vetor P em tempo O(N) linear.",
            "Espaço de memória auxiliar: O(N) para armazenar o vetor P."
        ], "notes": "A propriedade fundamental é que o prefixo até R contém o prefixo até L-1 acrescido dos elementos entre L e R."},
        {"title": "A Fórmula Mágica de Consulta em O(1)", "points": [
            "Fórmula: Soma(L, R) = P[R] - P[L - 1].",
            "Por que funciona? P[R] = (A[1] + ... + A[L-1]) + (A[L] + ... + A[R]). Ao subtrair P[L-1], sobra exatamente A[L] + ... + A[R].",
            "Tempo de consulta: exatamente 1 subtração aritmética -> O(1) tempo constante!",
            "Com isso, Q = 2 * 10^5 consultas executam em menos de 0.01 segundo."
        ], "notes": "Uma economia de complexidade de O(Q * N) para O(N + Q), viabilizando problemas com centenas de milhares de consultas."},
        {"title": "A Importância da Base P[0] = 0 e Indexação 1-Based", "points": [
            "Em C++, usar arrays 1-based (índices de 1 a N) torna o código de prefix sums imune a falhas de índice.",
            "Com 1-based: se L = 1, a fórmula calcula P[R] - P[0] = P[R] - 0 = P[R], sem precisar de if especial para a borda!",
            "Com 0-based: quando L = 0, acessar P[L - 1] acessaria P[-1], gerando lixo de memória ou Runtime Error (RTE).",
            "Adote como padrão: declare 'long long p[N + 1];' e leia a entrada de 1 a N."
        ], "notes": "Evitar casos especiais na borda elimina a causa número 1 de bugs em somas de prefixos."},
        {"title": "Integer Overflow: Por que Usar long long", "points": [
            "Se cada elemento A[i] puder ser até 10^9 e N = 10^5, a soma acumulada atinge 10^14.",
            "O tipo int de 32 bits só armazena até ~2 * 10^9.",
            "Portanto, o vetor de prefix sums DEVE ser declarado como 'long long p[N + 1];'.",
            "Ignorar isso gera overflow silencioso e números negativos bizarros (WA)."
        ], "notes": "Sempre confira os valores máximos do enunciado antes de decidir entre int e long long."},
        {"title": "Contagem de Frequência em Faixas (Prefix Frequencies)", "points": [
            "A técnica não se limita a somas de valores; aplica-se a contagem de ocorrências de qualquer propriedade.",
            "Exemplo: contar quantas vezes o caractere 'c' aparece na substring de L a R.",
            "Crie uma matriz: pref[26][N + 1], onde pref[ch][i] conta quantas vezes o caractere ch apareceu até a posição i.",
            "Consulta: pref[ch][R] - pref[ch][L - 1] responde a frequência em O(1)."
        ], "notes": "Muito comum em problemas de palíndromos, anagramas e permutações de strings."},
        {"title": "Prefix XOR: Consultas de Paridade em O(1)", "points": [
            "A operação XOR possui a propriedade de autocancelamento: X ^ X = 0 e X ^ 0 = X.",
            "Defina P[k] = P[k-1] ^ A[k].",
            "O XOR do subvetor de L a R é simplesmente: P[R] ^ P[L - 1].",
            "Aplicação: um subvetor pode formar um palíndromo se no máximo um caractere tiver frequência ímpar (máscara de bits com XOR)."
        ], "notes": "O XOR de prefixos transforma verificações de paridade de intervalos em operações binárias instantâneas."},
        {"title": "Subvetor com Soma Igual a K em O(N)", "points": [
            "Problema: contar quantos subvetores contíguos somam exatamente K.",
            "Abordagem ingênua: testar todos os pares (L, R) com prefix sums em O(N^2).",
            "Abordagem ótima O(N): Queremos P[R] - P[L - 1] = K, o que equivale a P[L - 1] = P[R] - K.",
            "Ao iterar R de 1 a N, consultamos em uma tabela hash (ou mapa) quantas vezes o valor (P[R] - K) já apareceu anteriormente como prefixo."
        ], "notes": "Essa combinação de Prefix Sums com Hash Map resolve um dos problemas mais clássicos de entrevistas e competições."},
        {"title": "Subvetor com Soma Múltipla de K (Lema dos Pombos)", "points": [
            "Queremos que (P[R] - P[L - 1]) seja divisível por K, ou seja, P[R] % K == P[L - 1] % K.",
            "Armazene a contagem dos restos da divisão de P[i] por K.",
            "Atenção com números negativos em C++: se o resto for negativo, normalize com: (resto % K + K) % K.",
            "Complexidade: O(N) com um único vetor de frequências de restos de tamanho K."
        ], "notes": "O Princípio dos Pombos garante que se o tamanho do array for maior que K, sempre existe pelo menos um subvetor múltiplo de K."},
        {"title": "Soma de Prefixos em 2D: Definição em Matrizes", "points": [
            "Problema: responder a soma de qualquer subretângulo com cantos opostos (r1, c1) e (r2, c2) em O(1).",
            "Definição: P[i][j] é a soma de todos os elementos na submatriz do topo esquerdo (1, 1) até (i, j).",
            "Tamanho da matriz: (N + 1) x (M + 1), com linha 0 e coluna 0 preenchidas com zeros."
        ], "notes": "Essencial para matrizes de notas, mapas de densidade e problemas de visão computacional em maratonas."},
        {"title": "A Fórmula de Construção 2D (Inclusão-Exclusão)", "points": [
            "Recorrência: P[i][j] = P[i-1][j] + P[i][j-1] - P[i-1][j-1] + A[i][j].",
            "Por que subtrair P[i-1][j-1]? Porque ao somar o retângulo de cima e o retângulo da esquerda, a região superior esquerda foi somada duas vezes!",
            "Construção completa em tempo O(N * M) com dois laços for aninhados."
        ], "notes": "Visualizar os retângulos geométricos sobrepostos torna a dedução da fórmula de inclusão-exclusão intuitiva."},
        {"title": "A Fórmula de Consulta Retangular em O(1)", "points": [
            "Dada a consulta do retângulo de (r1, c1) até (r2, c2):",
            "Soma = P[r2][c2] - P[r1 - 1][c2] - P[r2][c1 - 1] + P[r1 - 1][c1 - 1].",
            "Subtrai a faixa inteira acima de r1, subtrai a faixa inteira à esquerda de c1, e reinsere o canto superior esquerdo que foi subtraído duplamente.",
            "Tempo de resposta: exatamente 4 acessos e 3 operações aritméticas -> O(1) puro!"
        ], "notes": "Uma única linha de código que substitui laços aninhados de somatório."},
        {"title": "O Problema Inverso: Vetor de Diferenças (Difference Array)", "points": [
            "Problema: dado um array inicial de zeros, execute Q operações: 'adicione o valor V a todos os elementos de L até R'. No final, imprima o array.",
            "Abordagem ingênua: laço de L a R para cada operação -> O(Q * N) -> TLE.",
            "Com Vetor de Diferenças: cada operação em faixa executa em tempo O(1)!",
            "No final, uma única soma de prefixos reconstrói o array em O(N)."
        ], "notes": "Soma de prefixos e vetor de diferenças são operações inversas entre si, análogas à integração e derivada no cálculo."},
        {"title": "Como Funciona o Vetor de Diferenças 1D", "points": [
            "Para somar V no intervalo [L, R]:",
            "1. D[L] += V  (marca o início do incremento).",
            "2. D[R + 1] -= V  (cancela o incremento a partir de R + 1).",
            "Complexidade por atualização: exatamente duas operações pontuais -> O(1)!",
            "Reconstrução final: A[i] = A[i-1] + D[i]."
        ], "notes": "Ao calcular os prefixos de D, o valor V é propagado de L até R, e no índice R+1 o -V anula a propagação."},
        {"title": "Vetor de Diferenças em 2D", "points": [
            "Problema: somar V em todo o subretângulo de (r1, c1) até (r2, c2) em O(1).",
            "Operações pontuais na matriz de diferenças D:",
            "1. D[r1][c1] += V",
            "2. D[r1][c2 + 1] -= V",
            "3. D[r2 + 1][c1] -= V",
            "4. D[r2 + 1][c2 + 1] += V",
            "Reconstrução: calcula a soma de prefixos 2D sobre D ao final."
        ], "notes": "Atualizar qualquer retângulo em O(1) sem estruturas complexas de árvores é um dos truques mais elegantes de competição."},
        {"title": "Compressão de Coordenadas com Prefix Sums", "points": [
            "Quando os valores de L e R forem grandes (ex: até 10^9), não podemos criar um array de tamanho 10^9.",
            "Porém, se houver apenas N = 10^5 intervalos, existem no máximo 2 * 10^5 coordenadas relevantes.",
            "Solução: colete todas as coordenadas, ordene e remova duplicatas com std::unique.",
            "Mapeie cada coordenada original para seu índice no array comprimido de 1 a 2N e aplique o vetor de diferenças normalmente."
        ], "notes": "Compressão de coordenadas reduz problemas com coordenadas até 10^9 para o espaço de memória da máquina em O(N log N)."},
        {"title": "Prefix Maxima e Minima: Consultas Não Invertíveis", "points": [
            "Soma e XOR são invertíveis (subtração desfaz soma, XOR desfaz XOR).",
            "Máximo e Mínimo NÃO são invertíveis (saber o máximo de 1 a R e de 1 a L-1 não permite descobrir o máximo de L a R).",
            "Para consultas de máximo/mínimo em faixas arbitrárias sem updates, use Sparse Table em O(1) com O(N log N) pré-cálculo.",
            "Se o intervalo sempre começar no início (1 a R), o Prefix Maxima funciona perfeitamente: M[i] = max(M[i-1], A[i])."
        ], "notes": "Entender quando a operação permite inversão evita tentar aplicar a fórmula de subtração para operações de min/max."},
        {"title": "Algoritmo de Kadane visto via Prefix Sums", "points": [
            "Problema do Subvetor com Maior Soma (Maximum Subarray Sum).",
            "A soma de qualquer subvetor terminado em i é dada por P[i] - P[j] para algum j < i.",
            "Para maximizar P[i] - P[j], devemos MINIMIZAR P[j].",
            "Algoritmo: mantenha o menor prefixo visto até agora (min_prefix). A melhor resposta terminando em i é P[i] - min_prefix.",
            "Complexidade: O(N) com uma única variável de mínimo prefixo."
        ], "notes": "Essa interpretação revela a equivalência matemática profunda entre o algoritmo de Kadane e a soma de prefixos."},
        {"title": "Aplicações em Maratonas e Padrões Frequentes", "points": [
            "Problemas de sobreposição de intervalos: horários de pico em servidores ou salas de aula (Difference Array).",
            "Imagens digitais: detecção de manchas e filtros de desfoque (Blur Filter com Prefix 2D).",
            "Jogos de tabuleiro: pontuações acumuladas de territórios retangulares.",
            "Filtro de paridade de letras para checagem de palíndromos em substrings."
        ], "notes": "Quase todo contest possui pelo menos um problema fácil/médio cuja solução envolve soma de prefixos."},
        {"title": "Checklist de Verificação de Prefix Sums", "points": [
            "1. Declarou o vetor P como long long se a soma puder ultrapassar 2 * 10^9?",
            "2. Usou indexação 1-based com P[0] = 0 para evitar if especial quando L = 1?",
            "3. O tamanho do array P é N + 2 para suportar com folga acessos a R + 1 no vetor de diferenças?",
            "4. Lembrou de calcular a soma de prefixos final após todas as atualizações de diferença?"
        ], "notes": "Seguir esse checklist mental garante submissões com Accepted (AC) de primeira tentativa."}
    ],
    "binary": [
        {"title": "O Princípio da Busca Binária", "points": [
            "Estratégia de divisão e conquista que reduz o espaço de busca pela metade a cada iteração.",
            "Pré-requisito inviolável: o espaço de busca deve ser ORDENADO ou MONÓTONO.",
            "Complexidade: O(log N). Com N = 10^9, são necessárias apenas ~30 comparações; com N = 10^18, apenas ~60!",
            "Um dos algoritmos mais eficientes e fundamentais de toda a ciência da computação."
        ], "notes": "Logaritmo na base 2 cresce tão devagar que torna problemas com números astronômicos tratáveis em milissegundos."},
        {"title": "O Invariante do Intervalo [L, R]", "points": [
            "Mantemos dois ponteiros: L (início do intervalo viável) e R (fim do intervalo viável).",
            "Invariante: se a resposta existir, ela está garantidamente dentro de [L, R].",
            "Calculamos o elemento central M = (L + R) / 2.",
            "Se o elemento em M for menor que o alvo, descartamos a metade esquerda: L = M + 1.",
            "Se o elemento em M for maior que o alvo, descartamos a metade direita: R = M - 1."
        ], "notes": "A clareza sobre o que o intervalo [L, R] representa é o que impede loops infinitos e off-by-one errors."},
        {"title": "Evitando Overflow no Ponto Médio", "points": [
            "Fórmula ingênua: int M = (L + R) / 2;",
            "O BUG: se L e R forem grandes (ex: L = 1.5 * 10^9 e R = 2.0 * 10^9), a soma L + R estoura o limite do int (2.14 * 10^9), tornando-se negativa!",
            "FÓRMULA SEGURA: int M = L + (R - L) / 2;",
            "Essa forma alternativa é matematicamente equivalente e NUNCA estoura os limites de L e R."
        ], "notes": "Esse bug famoso permaneceu na biblioteca padrão do Java por quase uma década antes de ser corrigido."},
        {"title": "Busca Exata vs lower_bound e upper_bound", "points": [
            "lower_bound(x): primeiro elemento que é MAIOR OU IGUAL a x (>= x).",
            "upper_bound(x): primeiro elemento que é ESTRITAMENTE MAIOR que x (> x).",
            "Se x não existir no array, lower_bound aponta para o primeiro elemento maior que x.",
            "Contar quantas vezes x aparece no array ordenado em O(log N): upper_bound(x) - lower_bound(x)."
        ], "notes": "Em C++, use 'std::lower_bound(v.begin(), v.end(), x)' para vetores. Para conjuntos, use 's.lower_bound(x)'."},
        {"title": "Busca Binária na Resposta (BSTA)", "points": [
            "A técnica mais poderosa e frequente de busca binária em competições de programação.",
            "Em vez de buscar um valor dentro de um array pré-existente, buscamos o VALOR DA RESPOSTA ótima no espaço numérico.",
            "Aplica-se a problemas de otimização: 'Qual é o menor tempo para completar as tarefas?' ou 'Qual é a maior distância mínima viável?'",
            "Transforma um problema de otimização em um problema de decisão: 'É possível com valor X?'"
        ], "notes": "Sempre que um problema perguntar 'qual o valor mínimo/máximo tal que...', pense imediatamente em Busca Binária na Resposta."},
        {"title": "A Função de Predicado Monótono: check(x)", "points": [
            "Criamos uma função booleana: bool check(long long x);",
            "Propriedade de Monotonia: se for possível com X, também é possível com qualquer valor maior que X (ou vice-versa).",
            "Comportamento da função: [Falso, Falso, Falso, Falso, Verdadeiro, Verdadeiro, Verdadeiro...]",
            "A busca binária encontra exatamente o PONTO DE TRANSIÇÃO (o primeiro Verdadeiro) em O(log(MAX) * custo(check))."
        ], "notes": "Se a função check(x) não for monótona (se oscilar entre verdadeiro e falso), a busca binária não pode ser aplicada."},
        {"title": "Problema Canônico: Alocação de Máquinas / Fábrica", "points": [
            "Problema: K máquinas produzem itens. A máquina i leva t[i] segundos por item. Qual o tempo mínimo para produzir T itens?",
            "check(tempo): em 'tempo' segundos, a máquina i produz tempo / t[i] itens. Total produzido = soma(tempo / t[i]).",
            "Se total >= T, retorna true; senão false.",
            "A função check() é claramente monótona (mais tempo = mais itens produzidos) e roda em O(K) linear."
        ], "notes": "Com K = 10^5 e tempo até 10^18, a busca binária roda em 60 passos de O(K), totalizando ~6 * 10^6 operações (< 0.05s)."},
        {"title": "Problema Canônico: Alocação de Livros / Empacotamento", "points": [
            "Problema: dividir N livros entre M estudantes contiguamente minimizando o número máximo de páginas lidas por qualquer estudante.",
            "check(max_paginas): simule gulosamente. Aloque livros para o estudante atual enquanto a soma <= max_paginas. Se estourar, passe para o próximo estudante.",
            "Se o número total de estudantes necessários <= M, retorna true; senão false.",
            "A verificação gulosa do predicado check() roda em O(N)."
        ], "notes": "Esse padrão de 'Busca Binária na Resposta + Validação Gulosa no check()' resolve centenas de problemas de maratona."},
        {"title": "Definindo os Limites L e R com Segurança", "points": [
            "L (limite inferior): deve ser o menor valor teoricamente concebível (geralmente 0 ou 1, ou o maior elemento individual).",
            "R (limite superior): deve ser um valor que com certeza é suficiente no pior caso absoluto.",
            "No problema dos livros: L = max(paginas[i]) (um estudante tem que ler pelo menos o maior livro), R = soma_total(paginas) (um estudante lê tudo).",
            "Se R for muito pequeno, você nunca alcançará a resposta (WA). Se L for muito grande, o predicado falha."
        ], "notes": "Em caso de dúvida sobre o teto de R, use 10^18 para valores com long long. O log2 de 10^18 é apenas 60, não custa quase nada a mais."},
        {"title": "Padrão de Código Robusto para BSTA", "points": [
            "long long L = 1, R = 1e18, ans = R;",
            "while (L <= R) { long long M = L + (R - L) / 2; if (check(M)) { ans = M; R = M - 1; } else { L = M + 1; } }",
            "Vantagem dessa estrutura: a variável 'ans' sempre guarda a melhor resposta válida encontrada até agora.",
            "Imune a loops infinitos de fim de intervalo."
        ], "notes": "Salvar a melhor resposta válida e fechar o intervalo (R = M - 1) elimina qualquer ambiguidade sobre qual ponteiro imprimir ao final."},
        {"title": "Busca Binária em Números de Ponto Flutuante (Floats)", "points": [
            "Quando a resposta é um número real (double) em vez de inteiro.",
            "Não usamos L = M + 1 nem R = M - 1, pois entre M e M+1 existem infinitos números reais! Usamos L = M ou R = M.",
            "Critério de parada por tolerância: while (R - L > 1e-9) { ... }",
            "Perigo: erros de precisão do double podem fazer R - L nunca ficar menor que 1e-9 se os números forem grandes, gerando TLE!"
        ], "notes": "Em ponto flutuante, a representação de bits se esgota e comparações diretas de tolerância podem travar em loop infinito."},
        {"title": "O Truque das 100 Iterações em Ponto Flutuante", "points": [
            "Em vez de testar 'while (R - L > EPS)', execute um laço for fixo de 80 a 100 iterações:",
            "for (int iter = 0; iter < 100; iter++) { double M = (L + R) / 2; if (check(M)) R = M; else L = M; }",
            "Por que funciona? (1/2)^100 é aproximadamente 10^-30, uma precisão muito superior aos 53 bits da mantissa do double!",
            "Garante 100% de precisão e 0% de risco de loop infinito."
        ], "notes": "Técnica padrão ensinada pelos melhores técnicos de maratona para qualquer busca binária com doubles."},
        {"title": "Busca Ternária: Otimização de Funções Unimodais", "points": [
            "Quando a função NÃO é monótona, mas possui um único pico (máximo) ou um único vale (mínimo).",
            "Exemplo: parábolas, distâncias euclidianas convexas, custos de transporte unimodais.",
            "Dividimos o intervalo [L, R] em três partes iguais usando dois pontos médios: m1 = L + (R - L) / 3 e m2 = R - (R - L) / 3.",
            "Comparamos f(m1) com f(m2) e descartamos 1/3 do intervalo a cada passo."
        ], "notes": "A busca ternária reduz o intervalo por um fator de 2/3 a cada passo, com complexidade O(log_{1.5} N)."},
        {"title": "Implementação da Busca Ternária para Mínimo", "points": [
            "Se f(m1) < f(m2): o mínimo não pode estar à direita de m2 -> R = m2.",
            "Se f(m1) > f(m2): o mínimo não pode estar à esquerda de m1 -> L = m1.",
            "Se f(m1) == f(m2): podemos descartar as extremidades ou convergir.",
            "Em números reais, use 100 iterações fixas. Em inteiros, pare quando R - L < 3 e teste os valores restantes manualmente."
        ], "notes": "Em inteiros, a divisão inteira de 3 partes pode estagnar se R - L for pequeno, por isso a checagem manual final é essencial."},
        {"title": "Busca Binária Interativa", "points": [
            "Problemas onde o corretor responde a perguntas do seu programa em tempo real via terminal.",
            "Exemplo: 'Pensei em um número de 1 a 10^9. Você pode fazer até 30 perguntas com '>' ou '<'.'",
            "Após imprimir cada pergunta: fflush(stdout); ou cout << endl; (aqui o flush é OBRIGATÓRIO!).",
            "Sem esvaziar o buffer com fflush, seu programa trava aguardando resposta que o juiz não enviou (Idleness Limit Exceeded)."
        ], "notes": "Problemas interativos são comuns no Codeforces e na OBI; o esquecimento do fflush é o erro mais clássico."},
        {"title": "Binary Search em Árvores e Grafos", "points": [
            "Busca binária combinada com caminhos mínimos: 'Qual o menor peso máximo de aresta em um caminho de 1 a N?'",
            "check(max_peso): rode BFS ou Dijkstra ignorando qualquer aresta com peso > max_peso. Se 1 alcançar N, retorna true.",
            "A combinação de busca binária com travessia de grafos resolve problemas complexos em tempo O(log(MAX_PESO) * (V + E))."
        ], "notes": "Transforma problemas de caminho minimax em verificações simples de alcance de BFS."},
        {"title": "O Método de Subida Binária (Binary Lifting)", "points": [
            "Aplicação de busca binária em potências de 2 sobre estruturas de árvore e grafos funcionais.",
            "up[u][i]: armazena o 2^i-ésimo ancestral do nó u.",
            "Permite saltar 2^19, 2^18, ..., 2^0 passos para encontrar ancestrais ou responder consultas de LCA em O(log N).",
            "Em vez de dividir o intervalo, somamos potências de 2 decrescentes que satisfazem o predicado."
        ], "notes": "Essa variante 'aditiva' de busca binária por potências de 2 é a base de estruturas avançadas de árvores."},
        {"title": "Armadilhas de Maratona: Loop Infinito com 2 Elementos", "points": [
            "Quando L = 4 e R = 5: M = (4 + 5) / 2 = 4.",
            "Se sua atualização for 'R = M;', o intervalo vira [4, 4] e para.",
            "Mas se sua atualização for 'L = M;', o novo L continua sendo 4, e o loop while (L < R) NUNCA termina (TLE)!",
            "Regra: se a atualização puder ser L = M, o cálculo do ponto médio DEVE arredondar para cima: M = L + (R - L + 1) / 2."
        ], "notes": "Compreender o sentido do arredondamento do ponto médio evita 100% dos loops infinitos em busca binária inteira."},
        {"title": "Checklist de Busca Binária na Resposta", "points": [
            "1. A função de viabilidade check(x) é estritamente monótona (só muda de estado uma vez)?",
            "2. O limite inferior L é viável e o limite superior R é grande o suficiente?",
            "3. O cálculo do ponto médio usa M = L + (R - L) / 2 para prevenir overflow?",
            "4. A variável 'ans' foi inicializada e atualizada a cada check(M) == true?",
            "5. Se for float, usou laço fixo de 100 iterações em vez de EPS frágil?"
        ], "notes": "Com esse checklist, a chance de errar uma busca binária na resposta em contest é zero."}
    ]
}

def main():
    print("Atualizando learning_content.json com Parte 2 (prefix e binary)...")
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    
    for topic in data["topics"]:
        tid = topic["id"]
        if tid in PART2_SLIDES:
            topic["slides"] = PART2_SLIDES[tid]
            print(f"  ✓ {tid}: atualizado para {len(topic['slides'])} slides.")
            
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Concluído Parte 2!")

if __name__ == "__main__":
    main()
