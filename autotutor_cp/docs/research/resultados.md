# Resultados efetivamente observados

Data: 2026-11-05. Gemini 3.1 Flash-Lite, temperatura 0,3, até 4096 tokens de saída, pensamento mínimo. Orçamento financeiro autorizado zero; quatro chamadas reais à cota gratuita declarada, sem ativar faturamento. Consumo retornado pelo provedor: **5744 tokens** no total, incluindo 25 no teste de conexão. Reservas conservadoras do ledger não representam consumo real.

## Piloto de geração

Uma geração por estratégia, mesmo contrato de Segment Tree (`extended_range_sum`), seed de validação 42. Cada saída passou em 43 casos independentes. Tempo inclui geração e validação.

| Estratégia | Tokens entrada | Tokens saída | Tokens total | Segundos | Casos | Resultado técnico |
|---|---:|---:|---:|---:|---:|---|
| direct | 386 | 1132 | 1518 | 9.266 | 43 | aprovado |
| rag | 958 | 1110 | 2068 | 9.104 | 43 | aprovado |
| structured | 1029 | 1104 | 2133 | 11.289 | 43 | aprovado |

As três saídas foram estruturalmente válidas, compilaram e tiveram exemplos consistentes. Portanto, a observação é **3/3 neste piloto**, não estimativa de acurácia de 100% da plataforma. Três tarefas sob um único contrato não sustentam comparação estatística. Não houve falha a reparar nas chamadas reais. As estratégias `examples`, `iterative`, `free_direct` e o baseline local atual estão disponíveis, mas não foram avaliadas por novas chamadas neste piloto.

## Recuperação local

Máximo de três documentos e 2200 caracteres; mesma consulta Segment Tree. O tempo semântico inclui construção inicial do índice. Jaccard mede sobreposição lexical, sem julgamento humano de relevância.

| Método | Segundos observados | Caracteres de contexto | Redundância Jaccard |
|---|---:|---:|---:|
| bm25 | 0.0209 | 2144 | 0.0512 |
| semantic | 90.7014 | 2144 | 0.0747 |
| hybrid | 0.3001 | 2144 | 0.067 |
| hybrid_rerank | 0.4278 | 2198 | 0.067 |
| hybrid_mmr | 0.4194 | 2144 | 0.067 |
| competencies | 0.05 | 2198 | 0.0448 |

Todos os seis métodos retornaram contexto externo. BM25 trouxe Segment Tree (CP-Algorithms), More Applications of Segment Tree e Sparse Segment Trees (USACO). O híbrido e sua diversificação mantiveram os mesmos três documentos nesta consulta. O índice denso compactado ocupou cerca de 2,2 MB; não foi medido pico de memória. Precision@k, Recall@k, MRR, nDCG e relevância pedagógica **não foram calculados**, por ausência de julgamentos revisados.

## Antes e depois

Antes, a seleção de contratos recebia o catálogo inteiro sem RAG; o estudo usava principalmente FTS/BM25. Agora há um caminho experimental com recuperação externa na geração, especificação pedagógica explícita e validação por oráculo do contrato. O juiz da aplicação passou a usar isolamento de filesystem/rede, além dos limites de recursos existentes. Isso é melhoria verificável da infraestrutura, sem demonstrar superioridade científica dos métodos.

O resultado local antigo 0/5 pertence a outra tarefa/configuração; não é grupo de controle deste piloto. Os 98,7% de GPT-5-High na avaliação específica do AutoCode também não são diretamente comparáveis. Não houve avaliação com estudantes nem comprovação de aprendizagem, originalidade ou dificuldade.

## Evidências

- [Resumo e ledger exportado](../../data/research/results/2026-11-05/pilot/summary.json).
- [Recuperação: fontes, scores e latências](../../data/research/results/2026-11-05/retrieval/retrieval.json).
- [Conexão](../../data/research/results/2026-11-05/connection.json).
- [Estado BKT exclusivamente sintético](../../data/research/results/2026-11-05/synthetic_knowledge.json).

Cada pasta de geração contém prompt, resposta integral, consumo, validação, problema compactado e manifesto do código. Revisão humana e repetições estocásticas permanecem pendentes.

## Verificação do software

Suíte completa: **222 testes aprovados**, em 310,16 segundos. Após adicionar a verificação de reparo iterativo limitado, a suíte focada passou com **16 testes**, em 10,23 segundos (15 deles já incluídos na suíte completa). Total de casos distintos verificados: 223. Nenhum desses testes enviou chamadas externas reais. O transporte é simulado e as execuções de C++ usam o isolamento local. Evidência da suíte completa em `data/research/results/2026-11-05/all-tests.log`.
