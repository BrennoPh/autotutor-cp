> Recorte atualizado: priorizar os nove objetivos básicos em [foco_fundamentos.md](foco_fundamentos.md). Pilotos avançados anteriores permanecem arquivados e não integram a avaliação principal de iniciantes.

# Roadmap técnico e científico

## Entregue nesta etapa

Auditoria antes das mudanças, adaptador Gemini e interface de provedor, baseline local opcional, orçamento gratuito com ledger persistente, schema, geração controlada e revisão limitada, busca BM25/densa/híbrida, re-ranking leve, diversificação, expansão por competências, juiz isolado, testes diferenciais, grafo de 15 competências, BKT sintético, piloto de três gerações e seis recuperadores. Evidências e configurações foram registradas. Nenhum faturamento foi ativado.

## Próxima prioridade: qualidade de avaliação, sem ampliar requisições automaticamente

1. Revisar manualmente os três enunciados e preencher a rubrica com dois avaliadores; verificar estratégias alternativas que contornem a competência-alvo.
2. Anotar relevância nas sete consultas propostas, ampliar cobertura conceitual e manter conjunto de teste separado. Só então calcular métricas e decidir se re-ranking neural merece custo computacional.
3. Padronizar parâmetros local/API e medir recursos; executar tarefas pareadas de vários contratos com repetições registradas, sempre dentro da cota gratuita e sem fallback pago. Se não houver cota, usar somente testes locais.
4. Comparar uma variável por vez: exemplos, recuperação, especificação e revisão; depois investigar ordem enunciado/solução. Pré-registrar tamanho amostral e incerteza antes de alegar superioridade.
5. Validar grafo e associações problema–competência com professores; corrigir mapeamento dos tópicos legados. Integrar o protótipo ao diagnóstico real somente após revisão, consentimento e avaliação de privacidade.
6. Estimar parâmetros BKT com dados adequados, avaliar calibração e previsão fora da amostra; investigar IRT antes de DKT. Não usar probabilidade experimental como nota ou diagnóstico definitivo.
7. Planejar estudo de aprendizagem com pré/pós-teste e autorização institucional; separar satisfação, desempenho e retenção.
8. Endurecer sandbox e revisar isolamento para qualquer publicação multiusuário; travar dependências e empacotar snapshots completos do ambiente.

GraphRAG completo, fine-tuning, DKT e benchmark oficial em larga escala permanecem hipóteses futuras, sem justificativa empírica para infraestrutura adicional neste momento.
