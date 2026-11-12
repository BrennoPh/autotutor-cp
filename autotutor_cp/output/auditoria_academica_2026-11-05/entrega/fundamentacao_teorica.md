# Fundamentação teórica para a defesa do AutoTutor-CP

Data da auditoria: 05/11/2026. O texto distingue conceitos científicos, mecanismos implementados e propostas. As referências R1–R16 estão em `referencias.md`. Não houve treinamento ou alteração do código durante esta auditoria.

## 1. Problema científico e unidades de análise

Há pelo menos quatro objetos diferentes: o programa do aluno, o enunciado gerado, a explicação pedagógica e a trajetória de aprendizagem. Cada um exige um critério. Executar um programa mede comportamento em entradas determinadas. Analisar um enunciado exige conferir consistência de objetivo, restrições, exemplos e soluções. Avaliar uma explicação exige relevância, verdade e utilidade. Demonstrar aprendizagem exige observar mudança de desempenho e transferência, com desenho que controle explicações alternativas.

O objetivo inicial documentado era estender a geração de problemas do AutoCode com avaliação local e tutoria por dificuldades. A pergunta “evidências executáveis melhoram a tutoria?” é uma reconstrução pertinente, não uma hipótese causal previamente registrada. A aplicação atual possibilita conduzir esse estudo, mas seus testes ainda não o substituem.

## 2. Modelos de linguagem, treinamento e inferência

Um modelo autorregressivo representa pθ(y|x)=∏t pθ(yt|x,y<t). Os parâmetros θ resultam de treinamento. A inferência usa os parâmetros já aprendidos, selecionando tokens em sequência. Tokens são unidades do tokenizador, não palavras necessariamente. Em código, um identificador pode ocupar várias unidades e erros em uma unidade podem alterar completamente o programa.

O pré-treinamento aprende regularidades gerais de dados. Instruction tuning usa exemplos de instruções e respostas para adaptar comportamento. Fine-tuning local exigiria dados, otimização, versionamento e avaliação fora do treinamento. O AutoTutor não realiza nenhuma dessas etapas de ajuste de pesos. Enviar histórico ou trechos ao prompt é condicionamento durante inferência. Persistir respostas no SQLite cria memória recuperável, sem aprendizado paramétrico automático.

O Transformer utiliza atenção para relacionar posições: Attention(Q,K,V)=softmax(QKᵀ/√dk)V. Q contém consultas, K chaves e V valores; produtos internos geram escores, a divisão estabiliza escala e softmax normaliza pesos. Modelos geradores usam máscara causal. O projeto acessa arquiteturas prontas por adaptadores, sem implementar o Transformer. [R4]

Few-shot prompting acrescenta exemplos da tarefa ao contexto. O prompt do tutor possui exemplos de WA, TLE e CE para induzir orientação socrática. Isso é diferente de treinar com esses exemplos. Prompts podem restringir formato e estilo, mas não garantem observância. Filtros de expressões regulares detectam alguns padrões de código e não toda entrega indevida de solução.

Temperatura modifica a distribuição de seleção de tokens. Temperatura zero reduz variabilidade de amostragem, sem certificar verdade. O sistema pode produzir uma resposta errada de forma repetível. Alucinações incluem fontes inventadas, afirmações sem apoio e interpretações incorretas; erros numéricos e JSON truncado são problemas diferentes que merecem diagnósticos separados.

### Quantização e recursos

Quantização reduz a precisão de representação dos pesos. A aproximação P×b/8 calcula apenas bytes dos pesos para P parâmetros e b bits. Cache de atenção, ativações, buffers e processos do sistema acrescentam memória. Tamanho do arquivo, número de parâmetros e pico de RAM não são equivalentes. Contexto maior também exige recursos. A configuração observada usa Llama 3.2 1B, duas threads e descarregamento após resposta. O registro pontual de cerca de 1,47 bilhão de bytes é um smoke test, não avaliação completa. Qwen2.5-Coder 1.5B permanece uma alternativa para experimento, sem superioridade comprovada. [R15–R16]

## 3. Recuperação de informação e RAG

Recuperação seleciona evidências em uma coleção; geração produz uma resposta condicionada ao que recebeu. O modelo pode errar mesmo quando a fonte correta aparece. São falhas distintas: cobertura insuficiente, recuperação inadequada, truncamento e interpretação errada.

O artigo de Lewis e colaboradores combina memória paramétrica e não paramétrica em uma arquitetura treinada. Uma expressão conceitual é p(y|x)≈Σz∈TopK(x) pη(z|x)pθ(y|x,z). A implementação local não calcula essa marginalização nem treina recuperador e gerador conjuntamente. Seu RAG recupera trechos e os incorpora ao prompt. [R5]

### Indexação e chunking reais

O corpo do documento permanece comprimido no SQLite, acompanhado de URL, revisão, licença e checksum. O índice FTS5 permite localizar termos nos trechos. Chunking usa até aproximadamente 1.800 caracteres e prefere fronteiras textuais. O tamanho é em caracteres, não tokens. Não há overlap explícito. Cortar trechos pode separar definição, hipótese e exemplo; uma evolução deve comparar segmentação por seção e vizinhos, mantendo igual orçamento de contexto.

O contexto de materiais usa somente texto externo elegível, com exclusão de metadados e material autoral local. O filtro identifica tipo e origem; isso não avalia verdade de cada afirmação. O sistema mostra fontes recuperadas separadas dos links recomendados. Uma URL exibida não comprova leitura integral da página nem uso correto de seu conteúdo.

### TF-IDF e cosseno

TF pondera frequência de termo, enquanto IDF dá maior peso a termos menos comuns. No código, TF=1+log(contagem), quando positiva, e IDF=log((1+N)/(1+df))+1. Os vetores são normalizados. O cosseno é sim(a,b)=(a·b)/(‖a‖‖b‖), em que o numerador soma produtos coordenada a coordenada e as normas normalizam magnitude. Para vetores unitários, basta a·b.

O recuperador de problemas mantém três espaços: enunciado, conceitos/essência e estratégia. O escore combina 0,25, 0,45 e 0,30 desses espaços e um LLM reranqueia candidatos. Esses pesos não têm ablação local documentada. TF-IDF é uma representação vetorial lexical; usar NumPy não a transforma em embedding neural. O OI-Assistant original usa embeddings de API e FAISS, logo a implementação é uma adaptação. [R2]

### BM25, embeddings e fusão

BM25 soma contribuições de termos, com saturação de frequência e normalização por comprimento. Uma forma é Σt IDF(t)×f(t,d)(k1+1)/(f(t,d)+k1(1−b+b|d|/avgdl)). O projeto usa a função do SQLite com pesos de título, tags e corpo 6:3:1, aliases bilíngues e bônus de título e fundamentos. O sinal de BM25 no SQLite exige ordenar corretamente; o código combina o negativo do rank com bônus. [R7, R14]

Embeddings neurais aprendem coordenadas densas para representar relações entre textos. Sentence-BERT oferece a base conceitual de codificar sentenças e comparar vetores, mas all-minilm não deve ser identificado como uma reprodução integral de todos os experimentos de SBERT. Na comparação local, all-minilm:22m representa título e primeiros 1.200 caracteres dos documentos. O uso de cosseno mede proximidade, sem garantir equivalência de algoritmo. [R6, R15]

RRF combina posições de listas: score(d)=Σr 1/(k+posr(d)). O script usa k=60 e posições a partir de zero. Esse deslocamento precisa ser preservado para reproduzir o resultado. A fusão pode reunir sinais complementares, mas não corrige automaticamente documentos irrelevantes. O resultado local 7/12 contra 6/12 é exploratório, sem conjunto independente amplo. [R8]

FAISS é uma biblioteca para busca vetorial exata ou aproximada, não um modelo de embeddings. Não aparece na aplicação instalada. Com 302 vetores, o produto matricial exato em NumPy é simples; uma migração só se justifica por medição. Re-ranking neural pode melhorar ordenação a custo de latência, e não foi comparado localmente de forma isolada.

## 4. Geração algorítmica e validade

Um problema inclui enunciado, domínio de entrada, objetivo, limites, critério de saída e exemplos. Uma solução que compila possui validade sintática, mas pode falhar semanticamente. Um enunciado plausível pode contradizer a solução ou admitir um atalho incompatível com a competência pretendida.

AutoCode gera testes com validadores, geradores e checkers em múltiplas rodadas, além de variantes de problemas e validação dupla. O protótipo limita a geração a 39 contratos e não reproduz esse processo completo. O LLM escolhe o contrato em um catálogo dentro do prompt. Não existe recuperação RAG de candidatos nesse caminho. Alterar o cenário mantendo o contrato é uma adaptação útil para prática, sem demonstrar inovação algorítmica. [R1]

### Testes e oráculos

Casos pequenos enumerados permitem comparação com brute force. Casos extremos exploram overflow, índices e configurações adversariais. Entradas grandes procuram expor custos excessivos, mas um caso grande não garante reprovar todo algoritmo subótimo em qualquer máquina. Os limites locais são 2 s e 256 MB.

Nas sete sementes originais, std e brute concordam nos casos pequenos e std produz saídas nos grandes. Nas 32 tarefas acrescentadas, o oráculo Python verifica saídas da referência. Em intervalos, blocos constituem caminho independente da Segment Tree; em grafos, DSU, enumeração e caminhos mínimos ajudam a variar o mecanismo. Independência não é absoluta: implementações podem compartilhar uma hipótese equivocada.

A condição ∀x∈X: valid(x) e fref(x)=foráculo(x) vale para o conjunto finito X. Ela não é uma prova universal. A comparação posterior com a referência original também não verifica automaticamente a correspondência entre linguagem natural do enunciado e código. Respostas múltiplas, interatividade e tolerância numérica exigiriam checkers específicos.

### Competência, dificuldade e novidade

A técnica de uma referência não demonstra que ela é necessária para resolver o problema. Para conferir competência, devem-se comparar soluções alternativas e limites. Dificuldade depende de conhecimentos prévios, reconhecimento e implementação, não apenas de N. Os rótulos iniciante/intermediário/avançado não foram calibrados empiricamente. Originalidade deve ser medida por estrutura de operações, estados, invariantes e dependências, além de similaridade textual.

## 5. Fundamentos pedagógicos aplicáveis

A taxonomia revisada de Bloom distingue processos cognitivos e tipos de conhecimento. Uma atividade pode pedir execução de BFS, explicação de seu invariante ou avaliação de uma solução; são objetivos distintos, mesmo com o mesmo grafo. O protótipo não possui classificação Bloom validada. Uma evolução deve anotar objetivos e usar rubrica independente. [R9]

A Zona de Desenvolvimento Proximal descreve a distância entre desempenho independente e com assistência. O sistema observa acertos e erros, mas não estima formalmente essa zona. Uma avaliação precisaria comparar tarefas sem ajuda, com níveis de ajuda e após sua retirada. [R10]

Scaffolding envolve apoio contingente e retirada progressiva. Dicas socráticas e lacunas aproximam essa ideia, sem política de fading implementada. Deve-se avaliar se a ajuda facilita compreensão ou apenas fornece pista para o próximo aceite. [R11]

Mastery learning exige objetivos definidos, evidência formativa, intervenções corretivas e nova demonstração de domínio. O protótipo calcula estatísticas, mas não possui limiares de domínio empiricamente validados. Uma leitura concluída é um evento de uso e um AC finito é desempenho em uma tarefa. [R12]

Feedback formativo utiliza informações da atividade para orientar o passo seguinte. O caso que falha pode tornar o feedback específico, mas não identifica sozinho a causa cognitiva. A avaliação deve distinguir correção, especificidade, ação possível e revelação excessiva da solução. [R13]

Aprendizagem baseada em problemas pode organizar investigação de situações e reflexão, enquanto simplesmente resolver listas não demonstra uma aplicação integral dessa metodologia. Preferências declaradas podem orientar formato e calendário, sem presumir a existência de estilos fixos com eficácia já estabelecida.

## 6. Representação do conhecimento e personalização

O currículo possui IDs, objetivos e pré-requisitos. A validação da trilha impõe precedência desses pré-requisitos, mas não há ontologia, linguagem de consulta semântica nem grafo de conhecimento usado como recuperador. Um esquema futuro pode representar Competência, Conceito, Operação, Problema, Recurso e Evidência, com relações exige, pressupõe, exemplifica e avalia. É preciso distinguir relações editoriais de relações inferidas pela IA.

A personalização atual fornece ao modelo contagens por tópico e vereditos recentes. Não usa Bayesian Knowledge Tracing, teoria de resposta ao item nem aprendizado por reforço. Um problema de taxonomia confirmado é a ausência de Segment Tree entre os nove tópicos de learning_stats: acertos nesse assunto ficam fora da agregação. Essa lacuna deve ser corrigida em trabalho de implementação posterior, não silenciosamente durante a auditoria.

Propostas de trios seguem instruções ao modelo com evidências resumidas e validação de participantes. O texto “melhor trio” define o modo de saída, sem prova de otimização. O módulo heurístico legado existe, mas a interface atual chama a proposta por LLM. Confundir código disponível com caminho ativo produziria uma descrição incorreta.

## 7. Avaliação e ameaças à validade

Testes do software medem cenários e invariantes conhecidos. Hit@3 por título esperado mede uma aproximação de relevância, não cobertura de todas as competências. O escore numérico de cinco respostas depende de campo e formato, além do valor. Não há participantes locais nem evidência de ganho educacional.

Validade interna exige controlar modelo, tokens, temperatura, recuperação, seleção e validação. Validade de construto exige que a métrica represente correção, novidade ou alinhamento que pretende medir. Validade externa exige diversidade de tópicos, modelos e alunos. Reprodutibilidade exige versões, hashes, prompts, sementes e registro de falhas e rejeições. Exemplos não devem ser escolhidos apenas por sucesso.

O próximo estudo deve separar avaliação do recuperador, do gerador e do efeito educativo, usando critérios independentes e protocolos comuns. Um resultado negativo é útil quando informa exatamente a amostra, a configuração e o que falhou.
