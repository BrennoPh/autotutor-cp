# Perguntas e hipóteses

Pergunta central: como recuperação, especificação algorítmica e evidências pedagógicas influenciam problemas gerados, mantendo modelo e critérios de avaliação constantes?

- H1: recuperação híbrida melhora nDCG@3 em relação a BM25. Exige consultas variadas e julgamentos independentes; não testada por este piloto.
- H2: diversificação reduz redundância sem reduzir relevância. Medir Jaccard como aproximação, avaliações humanas e nDCG. A consulta isolada não confirma a hipótese.
- H3: especificação intermediária aumenta alinhamento com competência e clareza. Usar rubrica cega e soluções alternativas; três gerações não permitem concluir.
- H4: revisão com diagnóstico aumenta validação técnica em relação à primeira geração. Comparar primeira tentativa e final, contabilizando tokens e todas as falhas. Caminho de reparo testado com simulação, sem resultado empírico de melhoria por API.
- H5: recuperação por competências aumenta cobertura dos pré-requisitos relevantes. Requer revisar o grafo e os rótulos; expansão lexical não é comprovação.
- H6: adaptação ao estado probabilístico melhora adequação ao perfil. Somente perfis sintéticos nesta fase; nenhuma conclusão de aprendizagem.

Critérios separados: validade estrutural, compilação, exemplos e testes diferenciais; relevância e redundância; rubrica de alinhamento e pedagogia; latência, tokens e memória. Hipóteses nulas, tarefas, número de repetições e análise devem ser registrados antes da ampliação. Manter falhas e saídas truncadas no denominador. Não comparar 0/5 de outra tarefa local com 3/3 deste contrato como ganho causal.
