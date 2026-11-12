# Fundamentação teórica e limites da implementação

Revisão: 5 de novembro de 2026. O sistema combina geração por LLM, recuperação de documentos, validação executável e um protótipo probabilístico de conhecimento. Importar documentos não treina nem ajusta os pesos do Gemini: RAG seleciona contexto na inferência. O banco de estudantes também não é um conjunto de treinamento automaticamente autorizado.

## Geração e trabalhos relacionados

O Gemini 3.1 Flash-Lite foi escolhido para o piloto por ser o modelo solicitado, possuir saída estruturada e permitir uso da cota gratuita declarada pelo usuário. Essa escolha não constitui ranking de qualidade. O adaptador usa REST nativo, sem presumir compatibilidade com OpenAI. O Llama 3.2 1B continua disponível como baseline local; seu tamanho favorece execução em máquina de 8 GB, mas não assegura qualidade equivalente. [Modelo](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite), [saídas estruturadas](https://ai.google.dev/gemini-api/docs/structured-output), [limites](https://ai.google.dev/gemini-api/docs/rate-limits).

O AutoCode inspira a geração seguida de verificação e correção. O protótipo reaproveita contratos, validadores, brute force e soluções confiáveis, sem reproduzir seu benchmark ou seu resultado de 98,7%. OIAssistant é o segundo trabalho identificado na auditoria; Codigen é referência adicional distinta. As correspondências entre componentes e artigos estão na auditoria inicial. [AutoCode](https://openreview.net/pdf?id=F96nsbbhXC), [OIAssistant](https://doi.org/10.15388/ioi.2025.09), [Codigen](https://doi.org/10.1109/VL-HCC65237.2025.00038).

## Recuperação

BM25 pondera evidência lexical com frequência e normalização por comprimento. Embeddings representam consultas e passagens em vetores; a busca semântica usa produto escalar de vetores normalizados produzidos localmente por all-minilm:22m. Não se presume que similaridade vetorial represente adequação pedagógica. RRF combina posições de listas: soma de 1/(60+posição), com posições iniciando em 1. O híbrido evita comparar diretamente escalas de BM25 e cosseno. [BM25](https://doi.org/10.1561/1500000019), [Sentence-BERT](https://arxiv.org/abs/1908.10084), [RRF](https://doi.org/10.1145/1571941.1572114), [RAG](https://arxiv.org/abs/2005.11401).

A diversificação inspirada em MMR equilibra relevância e novidade. Aqui a redundância é aproximada por Jaccard de palavras, com peso de relevância 0,7; não é avaliação humana da diversidade conceitual. O re-ranking implementado é lexical e baseado em metadados, sem modelo neural de relevância. [MMR, Carbonell e Goldstein](https://www.cs.cmu.edu/afs/cs/Web/People/jgc/publication/MMR_DiversityBased_Reranking_SIGIR_1998.pdf).

O grafo editorial tem 15 competências e relações de apoio/pré-requisitos recomendados. Ele expande consultas e orienta especificações; não equivale a GraphRAG completo nem foi validado por especialistas. Rótulos de competências dos documentos são aproximações por palavras-chave. Sua cobertura automática não deve ser apresentada como cobertura pedagógica validada.

## Conhecimento e aprendizagem

BKT distingue estado latente de conhecimento e resposta observada, usando probabilidades de conhecimento inicial, aprendizagem, acerto por acaso e erro apesar de conhecer. A atualização aplica Bayes e uma transição de aprendizagem. Neste protótipo os parâmetros são hipotéticos: 0,2; 0,15; 0,2; 0,1. Não foram estimados com estudantes. Uma submissão incorreta não diagnostica desconhecimento. Apenas a evidência mais recente de cada item é usada e menos de três itens distintos permanece insuficiente. O limiar de apoio 0,6 é editorial, sem calibração. [Corbett e Anderson, 1994](https://doi.org/10.1007/BF01099821).

IRT modelaria habilidade e dificuldade dos itens; DKT aprenderia padrões sequenciais por redes neurais. Ambos exigem dados e avaliação próprios; não estão implementados. BKT é uma técnica probabilística de IA, mas continua dependendo de decisões explícitas sobre representação e parâmetros. Não é possível eliminar critérios de software e conservar validação e controle experimental.

Bloom orienta níveis de objetivos, scaffolding orienta dicas graduais, ZDP motiva tarefas com apoio e mastery learning orienta progressão por evidências. Aprendizagem baseada em problemas motiva situações contextualizadas, mas resolver exercícios automaticamente não demonstra essa abordagem pedagógica. Carga cognitiva motiva reduzir narrativa irrelevante; feedback formativo exige informação que ajude a próxima tentativa. São fundamentos e hipóteses de projeto, não resultados educacionais. [Bloom, mastery learning](https://eric.ed.gov/?id=ED053419), [Wood, Bruner e Ross](https://doi.org/10.1111/j.1469-7610.1976.tb00381.x), [feedback formativo](https://doi.org/10.1080/0969595980050102).

## Validação

Schema válido não assegura enunciado verdadeiro. Compilação não assegura correção. Casos finitos com oráculo independente aumentam evidência técnica, sem prova formal ou garantia de necessidade do algoritmo. Clareza, dificuldade, transferência e aprendizagem requerem revisão humana e estudo apropriado. Código não confiável só executa em namespaces isolados, com filesystem restrito, rede ausente e limites de recursos. A configuração depende do ambiente Linux e não substitui auditoria de segurança para serviço público. [Bubblewrap](https://github.com/containers/bubblewrap).
