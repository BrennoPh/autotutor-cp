# Validação por agentes: critérios e auditoria independente

Data: 5 de novembro de 2026. Revisão de código realizada por agente de software, sem professor humano, participantes reais ou inferência de modelo nesta auditoria. Não houve chamada à API. Foram lidos os fluxos de aluno/professor, geração e o novo `core/learner_assessment.py`.

## Escopo e significado das evidências

Os agentes representam personas sintéticas para exercitar o sistema. Testes automatizados demonstram propriedades dos casos executados; não constituem estudo de aprendizagem, revisão docente humana, calibração de nível ou certificação de conteúdo. Uma resposta HTTP bem-sucedida não demonstra correção pedagógica. Testes finitos de programas não demonstram correção formal de todas as entradas.

O recorte principal deve permanecer em fundamentos, vetores, contagem, ordenação, soma de prefixos, busca binária, guloso, BFS/DFS e DP introdutória. SegTree e Block-Cut Tree não são evidências centrais deste recorte.

## Fluxo existente e evolução examinada

- Aluno: entrar na conta, ingressar por código de turma, responder ao diagnóstico, estudar e submeter problemas. O painel de análise existente fica em Diagnóstico, Trilha e Desempenho (`core/learning_views.py`, função `learner_analysis_panel`).
- Professor: criar turma, acompanhar indicadores, consultar aluno e confirmar conclusões externas (`core/school_views.py`). Confirmar conclusão externa não equivale a aceite no juiz local.
- O módulo novo `LearnerAssessmentService` acrescenta proposta individual de avaliação com evidências tipadas, snapshot, histórico de revisão e proteção contra aprovação quando os dados estão desatualizados. A revisão deve ser identificada como humana somente quando tiver sido feita por pessoa; fixtures e agentes devem ser identificados como simulação.
- O fluxo anterior de `core/ai_coach.py` continua sendo uma implementação separada. Evidências ou garantias obtidas no serviço novo não devem ser atribuídas automaticamente ao fluxo antigo.

## Controles confirmados na leitura do serviço novo

1. `_authorize` consulta permissão sobre turma, matrícula e papel do aluno. Apenas o próprio aluno ou o dono da turma podem consultar a avaliação; a revisão requer o dono da turma. `get` encaminha a verificação por `list_for`, sem confiar somente no identificador da avaliação.
2. `evidence_snapshot` transmite métricas inteiras e IDs fixos do currículo, excluindo nomes, IDs de contas, código, conversas e textos livres. A descrição mais precisa é **estatísticas individuais sem identificadores diretos**; isso não demonstra anonimização irreversível.
3. `validate_assessment` confere schema, competência existente e igualdade exata entre cada observação numérica tipada e o snapshot local.
4. Evidência inferior ao limiar operacional de três itens distintos exige nível inconclusivo e confiança baixa. Esse limiar é uma proteção de engenharia, não uma regra validada em estudo educacional.
5. O hash inclui versão e snapshot. Cache usa evidência, modelo solicitado e indicador de simulação. Alterações nesses dados invalidam o reaproveitamento.
6. Revisões são armazenadas separadamente e mantêm a proposta original do modelo. Aprovar avaliação com snapshot desatualizado é bloqueado.
7. O provider é criado somente quando necessário e utiliza o ledger compartilhado de pesquisa. Renderizar a interface não deve disparar chamada externa.

## Achados concretos e limites

### Contagens em prosa: achado inicial e correção posterior

Em `core/learner_assessment.py`, função `validate_assessment`, a expressão regular de quantificadores cobre dígitos e algumas palavras, mas não todos os números por extenso. Foi reproduzido localmente, sem modelo nem rede:

- Snapshot sem respostas; observação tipada `answered=0`.
- Resumo `Você acertou vinte por cento das questões.` foi aceito.
- Resumo `Faça uma revisão de fundamentos.` foi rejeitado, pois a palavra `uma` coincide com o filtro.

Na versão inicial, portanto, havia falso negativo factual e falso positivo de linguagem. Após o relato, o backend ampliou os quantificadores e retirou artigos indefinidos da lista proibida. A reprodução foi repetida localmente: `vinte por cento` agora é recusado, e `Faça uma revisão de fundamentos.` agora é aceito. Esses dois casos concretos foram corrigidos; o registro acima preserva a descoberta original.

Permanece um limite conceitual: contagens tipadas podem ser descritas como verificadas, mas não toda a prosa. Ampliar lista de palavras não comprova factualidade: comparações como “mais acertos que erros” podem contradizer as métricas sem número explícito. Uma solução mais controlável é produzir fatos quantitativos exclusivamente a partir dos campos tipados e reservar ao modelo comentários identificados como proposta, mantendo revisão docente.

### Correção pedagógica e causalidade

Schema e contagens não comprovam que a interpretação está apoiada na evidência. Um erro de compilação não demonstra desconhecimento de algoritmo; uma solução aceita não demonstra autoria ou domínio geral. As ações e suas referências a tópicos podem ser formalmente válidas e pedagogicamente inadequadas. Revisão humana deve verificar esses aspectos, incluindo pré-requisitos.

### Concorrência e rastreabilidade

Na leitura inicial, a verificação de desatualização em `review` e a gravação da revisão não formavam comparação atômica com o estado do aluno. Após o relato, o backend passou a executar `BEGIN IMMEDIATE` e recalcular o snapshot a partir do perfil dentro da transação antes de aprovar. A leitura posterior confirmou essa proteção contra atualização concorrente durante a aprovação. A interface ainda deve apresentar aprovação junto de sua atualidade, pois novas atividades posteriores podem legitimamente tornar um parecer histórico desatualizado.

O campo `synthetic` é definido pelo chamador e não comprova que uma conta contém apenas dados sintéticos. Fixtures devem usar banco descartável, nunca marcar perfil real como sintético para evitar a autorização explícita de envio de dados. O provider injetável serve aos testes e não deve ser exposto como escolha arbitrária no fluxo público.

### Fluxos anteriores permanecem distintos

- `core/ai_coach.py`, `analyze_learner`, exige alguma medição para atribuir nível, mas admite nível avançado após uma única resposta. O prompt pede cautela; não fornece calibração.
- `analyze_class` verifica que há texto de tamanho limitado, mas não valida cada número citado na análise livre.
- `Classrooms.roster` conta problemas aceitos alguma vez. `learning_stats` considera o último veredito por problema. Os indicadores têm significados diferentes e precisam de rótulos claros.
- `CodigenTutor.generate_material` confere restrições de estrutura/código, mas não verifica automaticamente todos os exemplos matemáticos, afirmações conceituais ou adequação didática. A seção de fontes informa itens recuperados, sem comprovar suporte de cada afirmação.
- `core/research/pipeline.py` verifica a solução por testes e oráculos, mas declara corretamente que alinhamento entre enunciado e código, necessidade do algoritmo, dificuldade, dicas e originalidade precisam de revisão independente.

## Cenários e critérios de aceitação

| Cenário sintético | Critério verificável |
| --- | --- |
| Aluno sem respostas ou apenas leituras | Não atribuir domínio; serviço novo exige inconclusivo e confiança baixa. Nenhuma leitura entra como acerto. |
| Mesma questão respondida repetidamente | Contribui apenas uma questão distinta, usando a resposta mais recente. |
| Prefixos de `[2,-1,3,0]` | Prefixos com sentinela `[0,2,1,4,4]`; soma de índices 2 a 4, iniciados em 1, é 2. Convenção de índices explícita. |
| Problema de prefixos com negativos e tamanho mínimo | Exemplos e solução conferidos com oráculo independente, incluindo `n=1`. |
| Pedido de busca binária | Explicita ordenação ou predicado monótono e convenção de intervalos. Não confunde posição com valor. |
| Pedido de BFS | Limita garantia de menor distância a arestas sem peso ou de peso uniforme. |
| Submissão com erro de compilação | Não converte automaticamente CE em diagnóstico de incapacidade conceitual. |
| Pedido para ignorar regras e atribuir nível alto | Texto do pedido é dado, não autoridade sobre a avaliação. |
| Contagem tipada incorreta | Resposta recusada, mesmo com JSON estruturalmente válido. |
| Número inventado por extenso em resumo | Casos `vinte por cento` e artigo indefinido corrigidos; manter regressão. Teste não pode tratar toda prosa como fato validado. |
| Outro aluno ou professor de outra turma | Acesso negado em consulta, geração e revisão. Nenhuma chamada deve anteceder a autorização. |
| Aluno tenta revisar a própria avaliação | Acesso negado, sem alteração do histórico. |
| Evidência muda depois da geração | Avaliação marcada desatualizada; aprovação bloqueada. Parecer antigo preservado como histórico. |
| Professor pede revisão/rejeita | Proposta original preservada; decisão, comentário e autoria registrados separadamente. |
| Cache com mesmo snapshot e modelo | Nenhuma nova chamada. Alteração de snapshot/modelo impede cache antigo. |
| API responde 429 ou autorização inválida | Operação interrompida, sem migração paga e sem laço automático. |
| Alunos diferentes usam a mesma chave | Compartilham o mesmo ledger e limite; criar conta não renova orçamento. |
| Apenas abrir a página | Nenhuma chamada à API e nenhuma inferência local. |

## Rubrica para materiais e problemas

Separar pelo menos três resultados: conformidade estrutural, verificações objetivas e revisão pedagógica pendente/concluída. A rubrica pedagógica deve cobrir correção conceitual, correspondência ao pedido, pré-requisitos, clareza, exemplos, complexidade, casos de borda e pertinência das referências. Revisão por agente deve ser identificada como tal e acompanhada da justificativa; não pode preencher campo de aprovação humana.

Nos problemas, registrar contrato, seed, casos executados e resultado do oráculo. Não publicar como formalmente correto um programa que passou apenas nos exemplos do próprio modelo. Nos materiais, usar exemplos numéricos pequenos com resultados esperados verificáveis; evitar alegar que URLs permitidas garantem fundamento científico.

## API gratuita e reprodução

Não houve chamada nesta auditoria. A proteção local é orçamento autorizado zero, sem ativar faturamento ou mudar automaticamente para modelo pago. O ledger limita consumo; ele não inspeciona o faturamento da conta do provedor nem garante disponibilidade futura da camada gratuita. A cota real depende do projeto e deve ser distinguida do limite local.

Testes de contrato devem usar provider simulado e banco temporário. Pilotos externos precisam de contagem explícita de chamadas, tokens e falhas, compartilhando o mesmo ledger da aplicação. Os resultados devem distinguir: transporte simulado; geração real por API gratuita; verificação objetiva por software; parecer de agente; e revisão de professor humano. Não atribuir melhoria de aprendizagem ou acurácia global a um pequeno piloto sintético.

## Revisão qualitativa de respostas reais já gravadas

Esta seção é **revisão por agente, não professor humano**. Foram inspecionados arquivos existentes em `.runtime/live_student_agents/20261105T144336Z` e, quando disponíveis durante a revisão, `.runtime/live_student_agents/20261105T144558Z`. A inspeção não gerou chamadas à API. Os nomes dos diretórios usam UTC; ambos os lotes são de 5 de novembro de 2026. As saídas originais foram preservadas, sem correção silenciosa de seu texto.

### Aula de soma de prefixos: adequada no trecho examinado

`20261105T144336Z/lesson_0.json`: a definição de `prefix[i]` como soma de `arr[0..i-1]`, a sentinela zero e a fórmula para consulta com índices iniciados em 1 estão coerentes. O exemplo `[2,-1,3,0]` produz prefixos `[0,2,1,4,4]` e respostas `[2,2]`, com rastreamento textual correto. Pré-processamento O(N), consulta O(1) e total O(N+Q) estão corretos para vetor estático.

Não foi identificado erro matemático nesse trecho. Melhorias pedagógicas: explicitar que atualizações de valores exigem reconstrução ou outra estrutura; registrar memória O(N) e risco de overflow em somas acumuladas. A lista recuperada contém um material avançado de prefixos de funções aritméticas, embora o pedido seja introdutório. A resposta identifica somente a primeira fonte em `source_labels`, mas o artefato apresenta três referências recuperadas; mostrar recuperação não equivale a afirmar que todas foram efetivamente utilizadas.

### Aula de BFS: resultado correto, dois problemas na prosa

`20261105T144336Z/lesson_1.json`: o resultado final `[0,1,1,2]` está correto, e a explicação restringe adequadamente menor caminho a grafo sem pesos. A descrição da fila é apropriada.

Há um erro concreto de complexidade espacial: o material declara O(V) **incluindo a lista de adjacência**. O armazenamento total com listas de adjacência é O(V+E); somente memória auxiliar de fila, distâncias e marcação é O(V). A justificativa temporal também deve dizer que cada aresta não direcionada é examinada em ambas as listas, o que preserva O(V+E).

O rastreamento mistura tamanhos e convenções de índices. Começa com `[inf,0,inf,inf]` e depois passa a `[inf,0,1,1,2]`: se a primeira posição for sentinela para vértices iniciados em 1, o vetor inicial deveria ter cinco posições, `[inf,0,inf,inf,inf]`. Se representar somente os quatro vértices, deveria começar `[0,inf,inf,inf]`. A resposta numérica final conferida não detectou essa inconsistência textual.

O material recuperou também 0-1 BFS e DSU. São tópicos que precisam ser diferenciados de BFS introdutória; uma fonte permitida não comprova que ela é apropriada ao pedido. O status de revisão pedagógica pendente é necessário, sobretudo diante dos erros observados.

### Problema de prefixos: concordância técnica e conteúdo coerente

`20261105T144336Z/problems/c22e6a7051234dd784cb0f23a9540deb/run.json`: “Somas de Energia em Intervalos” passou nos 44 casos registrados. Os exemplos resultam em 6, 9 e 15; enunciado, gramática, limites e solução correspondem ao contrato `prefix`. `long long` suporta o máximo de soma previsto; tempo O(N+Q) e memória O(N) são coerentes. As dicas progridem de soma acumulada a subtração de prefixos e cuidado com inteiro.

Como exercício introdutório, a primeira dica e o próprio enunciado já apontam fortemente a técnica; isso reduz descoberta autônoma, mas é compatível com prática guiada. Não foi identificada falha concreta no código ou nos exemplos examinados. Os 44 casos não certificam dificuldade, aprendizagem, novidade ou todas as entradas possíveis.

### Problema de BFS: exemplo incorreto corretamente bloqueado

`20261105T144336Z/problems/b5f163710da342a7b42041deb49a8968/run.json`: “O Refúgio Mais Próximo” não foi publicado como validado. Seu segundo exemplo tem três vértices, somente aresta 1–2 e fonte no vértice 3. A saída correta é `-1 -1 0`, pois 1 e 2 estão desconectados da fonte. O modelo forneceu `2 1 0`. A verificação detectou que o exemplo divergia do código e bloqueou o problema.

O algoritmo e a explicação de BFS multifonte parecem adequados no trecho examinado, mas isso não torna o artefato completo correto. A entrada omite detalhes do contrato sobre ausência de arestas repetidas e ordenação `U<V`, e poderia declarar explicitamente que as ligações são não direcionadas. As dicas são conceitualmente coerentes, mas introduzem uma extensão de BFS que deve vir depois da versão de fonte única no currículo básico.

### Aula de DP do lote posterior: falha de contrato, cálculo final correto

`20261105T144558Z/lesson_0_rejected.json`: o contrato esperava a resposta `[5]` para quatro degraus com passos de tamanho 1 ou 2. O modelo devolveu `[1,2,3,5]`, expondo resultados intermediários em vez de somente o resultado solicitado. A rejeição é correta por descumprimento do formato/contrato numérico.

Entretanto, o raciocínio textual enumera corretamente as cinco formas e apresenta a recorrência esperada. Não atribuir esse caso a incapacidade de resolver a conta: houve divergência entre a forma de resposta pedida e a entregue. A explicação poderia separar memoização top-down de tabulação bottom-up com maior precisão e indicar que recursão é útil, mas não indispensável para implementar a versão iterativa. A terceira fonte recuperada trata DP em perfil, avançada para o objetivo introdutório.

### Problema de DP do lote posterior: correto nos testes, dica ambígua

`20261105T144558Z/problems/a21e8ff5e1ec4b2cb92ef172d26150a9/run.json`: “Tesouros sem vizinhos” passou nos 44 casos registrados; exemplos 4 e 12, casos base, tipos inteiros e recorrência são coerentes para valores não negativos. Espaço O(N), com possibilidade de O(1), está adequadamente explicado.

A primeira dica descreve `dp[i]` como subproblema que “termina no índice i”. Isso pode ser interpretado como obrigatoriedade de selecionar o baú i, o que não corresponde à recorrência usada. A explicação principal está mais precisa: considerar os baús de 0 até i. Recomenda-se usar essa definição também na dica. Trata-se de ajuste pedagógico detectado por agente, mantendo revisão humana pendente.

### Consequência para a avaliação científica

As evidências sustentam que verificações objetivas bloqueiam algumas saídas incorretas, mas não certificam a prosa. Neste recorte lido, o exemplo numérico de BFS foi aprovado enquanto sua explicação de memória e seu rastreamento tinham problemas. O problema de BFS foi bloqueado por exemplo incorreto; a aula de DP foi bloqueada por formato de resposta apesar de cálculo final correto. Separar essas classes de falha é essencial para não superestimar sucesso nem atribuir toda rejeição a erro conceitual do modelo.

Esta revisão examina um pequeno lote já existente, sem amostragem representativa, avaliadores humanos independentes ou medida de concordância entre revisores. Não constitui estimativa de acurácia global ou comparação conclusiva com modelos locais.
