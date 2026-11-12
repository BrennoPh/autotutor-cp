# Roteiro da apresentação

## 1. IA nos fundamentos de programação competitiva

Recorte revisado em 5 de novembro de 2026. Público: iniciantes com noções de uma linguagem. Esta apresentação relata infraestrutura e evidências exploratórias. A comparação API/local em fundamentos ainda não foi concluída. SegTree e Block-Cut Tree ficam fora da avaliação principal.

## 2. Problema e pergunta de pesquisa

A contribuição pretendida é integração e avaliação de mecanismos, sem novo modelo fundacional. Não há experimento de aprendizagem com estudantes reais. Fonte: plano_fundamentos.md e artigo revisado.

## 3. Recorte de conteúdo

Nove objetivos básicos estão associados a contratos em basic_curriculum.json. Este recorte pressupõe conhecimentos iniciais de uma linguagem. Árvores simples e matemática básica podem ampliar o currículo depois. Segment Tree, lazy propagation e Block-Cut Tree não entram no conjunto principal de avaliação.

## 4. Mapa do sistema atual

Código: app.py, core/classrooms.py, core/knowledge.py, core/research/, core/isolated_judge.py. A persistência distingue banco público de conteúdo e progresso privado. Nem todo contrato é básico. Os caminhos experimentais coexistem com componentes legados.

## 5. AutoCode: geração e verificação

Fonte primária: Zhou et al., AutoCode: LLMs as Problem Setters for Competitive Programming, ICLR 2026. https://proceedings.iclr.cc/paper_files/paper/2026/hash/1bd78da0966968409e65b5e0b5dbb57e-Abstract-Conference.html . O resultado próximo de 99% do artigo não é do AutoTutor e não mede ganho de aprendizagem.

## 6. OI-Assistant: recuperação para aprender

Fonte: Su, Nie e Meng. OI-Assistant: A Retrieval Augmented System for Similar Problem Discovery and Interactive Learning in Competitive Programming. Olympiads in Informatics 19, 129–144, 2025. DOI 10.15388/ioi.2025.09. https://ioi.te.lv/oi/files/volume19.pdf . A aplicação não reproduz integralmente a arquitetura ou avaliação do artigo.

## 7. Codigen e personalização

Fonte: Mohamed Ez-Zaouia e Yazid Boumarafi. Codigen: Enhancing Personalized Programming Education with Visual Authoring and Large Language Models. VL/HCC 2025. DOI 10.1109/VL-HCC65237.2025.00038. Não se reproduz a interface de autoria visual do artigo, nem se reivindicam seus resultados educacionais.

## 8. Inferência, RAG e evidências

Fontes: Lewis et al. 2020, https://arxiv.org/abs/2005.11401 ; Corbett e Anderson 1994, https://doi.org/10.1007/BF01099821 . O RAG é uma cadeia de recuperação e composição de prompt, sem treinamento conjunto. O BKT atual usa parâmetros hipotéticos e perfis sintéticos, sem diagnóstico validado.

## 9. Fluxo experimental verificável

Mapa técnico editável do caminho experimental. Recuperação retorna no máximo três documentos e 2200 caracteres. A referência é independente da solução gerada. O juiz bloqueia código sem isolamento disponível. Correção do programa em casos finitos não certifica alinhamento pedagógico ou necessidade do algoritmo. Código: core/research/pipeline.py e core/isolated_judge.py.

## 10. Biblioteca e cobertura do RAG

Fonte: auditoria do corpus em 5/11/2026. Há 5551 registros e 6837 chunks no banco completo. Os 302 textos são 164 de CP-Algorithms e 138 de USACO Guide, com atribuição e licença. Não se importou integralmente todo site solicitado. O número de contratos não é o tamanho da biblioteca.

## 11. Falhas locais em quatro tarefas básicas

Fonte: evidencias/recorte_local_basico.json, derivado de learning-quality.json. Llama 3.2 1B, com referências externas. BFS esperava [0,1,1,2], DFS esperava 4. Prefixos contém o valor esperado 5, mas a justificativa diz prefix[5]-prefix[1]=17 e usa chaves fora do esperado. Não chamar todos esses casos de erro aritmético. O item avançado da avaliação original foi excluído.

## 12. Limites locais de memória e fidelidade

Fontes: evidencias/llama-light-smoke.json e qwen-evaluation.json. O Llama respondeu OK em 3,81 s e reportou 1466852966 bytes. A métrica não mede pico de RAM da aplicação. Os testes Qwen usaram tarefas sintéticas distintas e tiveram carga concorrente; não sustentam ranking entre famílias. JSON válido não assegurou fidelidade às estatísticas. Nenhuma nova inferência local foi executada nesta revisão.

## 13. O papel do Gemini 3.1 Flash-Lite

Fonte: data/research/results/2026-11-05/pilot/summary.json. Total anterior retornado pelo provedor: 5744 tokens. O contrato de geração anterior era avançado e não integra o resultado principal de fundamentos. Não houve nova chamada à API nesta revisão. Modelo solicitado pelo usuário, sem evidência de que seja o melhor para educação. Resposta JSON não certifica conteúdo.

## 14. Uso gratuito e orçamento zero

Fontes oficiais, consulta em 5/11/2026: https://ai.google.dev/gemini-api/docs/pricing e https://ai.google.dev/gemini-api/docs/rate-limits . O teto de seis é local e não representa cota oficial Google. O projeto usa recuperação e armazenamento locais, sem depender de grounding ou cache gerenciado. A modalidade de faturamento da conta não é informada pela resposta de geração. O usuário declarou cota gratuita. Termos https://ai.google.dev/gemini-api/terms : nesta fase enviar apenas dados públicos e sintéticos.

## 15. Experimento básico proposto

Planejamento, não resultado executado. Temas: simulação, prefixos, BFS e DP introdutória. Condições: contrato sem RAG, com BM25, com BM25 e especificação pedagógica. Dois e seis dias pressupõem a cota local integral livre e cota do provedor suficiente, sem outras chamadas. Falhas e correções consomem tentativas. Uma ablação posterior manterá contexto idêntico para isolar o efeito da especificação. Comparação local/API requer padronizar saída, prompt e timeout primeiro.

## 16. Avaliação além do formato

Usar a rubrica em data/research/human_rubric.json. Relevância requer julgamentos revisados antes de Precision, Recall, MRR e nDCG. Dois avaliadores devem desconhecer a condição e justificar notas. Aprendizagem exige estudo separado com instrumentos, participantes e autorizações. Registrar denominadores e incerteza, sem transformar contagens de testes de software em acurácia da IA.

## 17. Melhorias com maior utilidade para iniciantes

Auditoria local de nove consultas em evidencias/recuperacao_basica.json: Vetores e contagem não retornava texto antes da correção bilíngue. Outras consultas trouxeram tópicos avançados como Matroids, 0-1 BFS e profile DP. São indícios para curadoria, sem julgamentos de relevância revisados. Cache local de respostas por chave é proposta, não implementação concluída. A persistência de materiais já existe. As estatísticas devem ser calculadas por código e interpretadas pela IA sem inventar valores.

## 18. Contribuição e limites do artigo

O artigo revisado em LaTeX SBC acompanha esta apresentação. O próximo resultado prioritário é um benchmark básico pareado com revisão humana, não aumentar a quantidade de funcionalidades. Manter separados implementação, execução de testes e estudo científico. Não usar os 98,7% do AutoCode como meta já atingida ou número do projeto. Artigos e evidências estão citados nas notas de cada slide.
