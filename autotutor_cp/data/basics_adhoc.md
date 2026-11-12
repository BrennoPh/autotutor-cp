# Ad hoc e implementação: do enunciado ao algoritmo

Um problema ad hoc pede uma solução construída para suas condições particulares. A palavra não identifica um algoritmo único. Em muitos exercícios iniciais, bastam leitura cuidadosa, condições, contagem e uma ou duas passagens por um vetor. Antes de escolher grafos ou DP, descubra se a pergunta pode ser respondida mantendo poucas informações enquanto percorre os dados.

## Comece pelo contrato

Anote o que entra, o que deve sair, os limites e as operações permitidas. Distinguir “exatamente”, “pelo menos” e “no máximo” costuma ser decisivo. Refaça o exemplo à mão e crie um exemplo menor. Escreva uma frase que descreva a resposta sem usar os personagens da história.

Se uma sequência contém números de 1 a N, exceto um, a pergunta é encontrar o elemento ausente. Uma abordagem inicial é marcar os valores vistos. Outra compara a soma esperada com a observada, cuidando da capacidade do tipo numérico. Não é preciso construir um grafo porque o enunciado menciona cidades ou pessoas.

## Simulação: reproduzir as operações

Na simulação, o estado representa a situação atual, e cada operação do enunciado transforma esse estado. Se um elevador começa no andar 2 e recebe os movimentos +3, -1 e +2, os estados são 2, 5, 4 e 6. A resposta depende da pergunta: andar final, maior andar visitado e distância percorrida são quantidades diferentes.

Defina quais variáveis precisam ser atualizadas, em que ordem e quais limites devem ser respeitados. Atualizar duas variáveis usando um valor que já mudou é um erro comum. Quando as operações devem ser simultâneas, preserve os valores anteriores antes de calcular os novos.

## Uma passagem e um invariante

Para achar a maior sequência de caracteres iguais em “AAABBCCCC”, mantenha o caractere anterior, o comprimento da sequência atual e o melhor comprimento encontrado. Ao ler um caractere igual ao anterior, aumente a sequência atual. Ao mudar, comece uma sequência de comprimento 1. Atualize o melhor em todas as posições. A resposta é 4, para “CCCC”.

Depois de processar cada prefixo, o melhor comprimento deve representar a maior sequência encontrada nesse prefixo. Essa propriedade é um invariante: ajuda a explicar a correção e revela se o último grupo foi esquecido. Cada caractere é processado uma vez, logo o tempo é O(N), com memória adicional O(1).

## Contagem e frequências

Quando a ordem não importa, contar pode simplificar o problema. Para saber se dois grupos têm as mesmas letras, compare frequências. Para verificar se todos os valores são distintos, use um conjunto ou ordene e compare vizinhos. A escolha depende dos limites e do tipo de dado; não existe uma estrutura que seja melhor em todos os casos.

Também distinga contar ocorrências de contar valores distintos. No vetor [2, 2, 5], existem três elementos e dois valores distintos. Em uma pergunta sobre pares, verifique se a ordem importa: (i, j) e (j, i) podem representar o mesmo par ou dois pares diferentes, conforme o contrato.

## Casos extremos antes de submeter

Teste N=1, todos os valores iguais, valores já ordenados, ordem inversa e limites numéricos. Acrescente zeros e negativos somente quando o enunciado permitir. Se há uma divisão, verifique se o divisor pode ser zero. Se usa posições de vetor, confira o primeiro e o último índice válidos.

Um resultado correto no exemplo não demonstra correção geral. Procure um caso que contradiga sua ideia. Se não conseguir justificar a estratégia, descreva o que cada variável significa e confira essa descrição após cada operação em uma entrada pequena.

## Onde entram prefixos, BFS, DFS e DP?

Se várias perguntas repetem somas sobre o mesmo vetor, a simulação direta pode repetir trabalho: soma de prefixos permite reaproveitar uma preparação. Se a resposta depende de conectividade entre elementos, representar um grafo e visitar vértices com BFS ou DFS pode ser adequado. Se escolhas diferentes levam aos mesmos subproblemas, DP pode evitar calcular o mesmo estado repetidamente.

Essas técnicas surgem da estrutura da pergunta, não do tema da história. Começar com uma simulação pequena é útil mesmo quando a solução final usa outra técnica: ela ajuda a construir exemplos e a comparar resultados.

## Pratique sem olhar uma solução

1. Encontre o maior grupo de caracteres consecutivos iguais em uma string. Qual estado precisa ser guardado?
2. Dado um vetor, conte quantos elementos são estritamente maiores que todos os anteriores. O primeiro conta? Declare sua convenção.
3. Simule um placar com operações de adicionar e remover pontos, conforme as regras do enunciado. Quando ocorre uma situação inválida?
4. Em [3, 1, 2, 2], quantos aumentos seriam necessários para tornar a sequência não decrescente se só podemos aumentar valores? Trace os estados e justifique uma decisão por vez.

A proposta é produzir um raciocínio verificável, identificar casos de fronteira e estimar o custo antes de escrever a submissão.

Referência para continuar: [USACO Guide — Ad Hoc Problems](https://usaco.guide/bronze/ad-hoc). Este texto é autoral; os exercícios acima são propostas didáticas, sem garantia de correspondência com testes de um juiz externo.
