# Projeto de evolução do AutoTutor

Revisão: 4 de novembro de 2026.

## Resultado esperado

O pedido específico do aluno deve determinar o conteúdo, as fontes e o exercício. O sistema deve conseguir explicar de onde veio a evidência e reconhecer quando não tem outro exercício compatível. A coleção pessoal continua privada e persistida no SQLite.

## Diagnóstico e alterações implementadas

1. **Referências repetidas.** A bibliografia era uma seleção fixa por assunto do menu. Agora a consulta usa o pedido escrito; as recomendações são pesquisadas no catálogo e os vídeos podem apontar para aulas específicas. Os trechos enviados à IA aparecem separados dos links para continuar estudando. Links desconhecidos produzidos pela IA são identificados como não confirmados.
2. **RAG baseado nas próprias aulas.** O contexto de RAG passa a excluir por padrão URLs internas e registros que contêm apenas metadados. Aulas autorais continuam disponíveis na biblioteca, mas não são apresentadas como evidência externa. Na ausência de trechos, o material informa que a explicação veio do conhecimento do modelo.
3. **Baixa precisão da busca.** A busca SQLite FTS5/BM25 combina correspondência de títulos, vocabulário português/inglês e preferência por fundamentos para iniciantes. O orçamento de contexto é distribuído entre fontes. O texto escolhido, e não a página inteira, entra no pedido da IA.
4. **Exercícios repetidos.** A escolha foi ampliada de sete para 39 contratos locais. A seleção prioriza contratos fora dos oito últimos gerados; se o assunto só tiver um contrato compatível, a interface permite uma revisão explicitamente identificada. A IA continua responsável pela escolha e adaptação; validação e testes objetivos impedem a publicação de exercícios inconsistentes. Os testes aleatórios mudam a cada geração e registram a semente para reprodução.
5. **Origem pouco visível.** Biblioteca → Acervo RAG mostra a cobertura de cada fonte e distingue texto disponível de referência. Cada material novo salva as referências efetivamente recuperadas e as recomendações específicas do pedido.

## Organização dos dados

- `data/progress.sqlite3`: perfis, estudos, histórico e atividades privadas. Não é substituído durante a importação pública.
- `data/knowledge.sqlite3`: documentos externos e índice lexical, com corpos comprimidos, URLs, versão, licença e atribuição. Aulas autorais permanecem identificadas separadamente.
- `data/knowledge.json.gz`: exportação portátil do acervo, incluindo metadados de origem.
- `data/study_sources_report.json`: cobertura, contagens e limitações das seis fontes solicitadas.
- `.runtime/study-source-cache`: respostas públicas consultadas, para repetição da importação sem baixar novamente.

A importação deduplica URLs e não substitui um artigo completo por uma referência. Metadados de problemas não são enunciados nem testes oficiais. Recuperação não modifica os pesos do modelo: isto é RAG, não treinamento ou fine-tuning.

## Cobertura e limites

- USACO Guide: módulos de tutoriais com licença já importados, versão fixada; MDX limpo, sem soluções de problemas e sem trechos de terceiros.
- CP-Algorithms: artigos externos licenciados preservados como fonte complementar.
- Maratona UFMG: títulos e URLs dos vídeos expostos publicamente na página do canal; sem mídia ou transcrições.
- CSES: catálogo público de títulos e seções. Exercícios corrigíveis localmente continuam sujeitos aos contratos próprios de juiz.
- Neps: referências públicas de cursos, blogs e vídeos em português; títulos derivados das URLs são marcados. Endereços que só contêm IDs numéricos não são tratados como títulos reais.
- YouKn0wWho: metadados públicos de problemas e seus tópicos, extraídos sem executar JavaScript. O conteúdo dos destinos não foi copiado.
- TLE: link público indexado; a consulta do catálogo devolveu HTTP 403 por origem não verificada. A lista completa não foi importada.

As contagens exatas e atualizadas estão no relatório JSON. Não se afirma que todos os textos, cursos, vídeos ou enunciados das seis plataformas estejam disponíveis localmente.

## Próximas entregas propostas

1. **Mais contratos por assunto.** Priorizar Segment Tree (soma, mínimo, máximo, lazy propagation), DFS/BFS e DP com objetivos distintos. Cada contrato precisa de gramática, oráculo independente, exemplos e testes de borda antes da publicação. Critério: permitir cinco exercícios consecutivos do mesmo tópico sem apenas reescrever a narrativa.
2. **Ampliação de texto autorizado.** Acrescentar exportações ou fontes com licença apropriada, transcrições autorizadas e leitura completa de novos módulos. Resolver o acesso público ao catálogo TLE sem contornar autenticação. Critério: relatório de cobertura por fonte e importação repetida sem duplicações.
3. **Avaliação da qualidade.** Conjunto fixo de pedidos em português para BFS, DFS, DP, prefixos e SegTree; avaliar relevância, correção, uso das fontes e extensão. Testes de transporte simulados não comprovam a qualidade pedagógica do Llama 1B.
4. **Busca semântica opcional.** Comparar embeddings leves com a busca lexical antes de adotar outro modelo em memória. Critério: melhorar a recuperação em perguntas parafraseadas sem prejudicar a máquina de 8 GB.
5. **Personalização com evidência.** Usar estatísticas resumidas para ajustar dificuldade e pré-requisitos, preservando a prioridade do pedido atual e evitando que materiais anteriores contaminem o assunto.

## Validação e operação

Os testes cobrem exclusão de fontes internas, separação entre referência e texto, prioridade do pedido sobre o menu, diversidade de contratos, validação por oráculo e fluxos da interface. Nenhuma chave de API foi extraída; testes de integração usam respostas controladas.

Importação reproduzível a partir da raiz do projeto:

```bash
PYTHONPATH=. .venv/bin/python scripts/import_study_links.py \
  --database data/knowledge.sqlite3 \
  --report data/study_sources_report.json \
  --cache .runtime/study-source-cache
```

Para atualizar fontes, use uma nova pasta de cache. Uma execução que falhe em uma fonte preserva os documentos já importados e registra a falha. O modelo local padrão continua Llama 3.2 1B, com limite de dois núcleos e descarregamento após a resposta.


## Etapa executada — novembro de 2026

- **Prática a partir do contexto:** páginas de estudos e buscas da biblioteca possuem ação direta para gerar um problema. O Laboratório também oferece o último assunto. O pedido completo acompanha a geração, com registro da origem; revisão do mesmo contrato fica identificada na Arena.
- **Diversidade:** oito novos contratos com oráculos Python e referências C++17. Agora são 39 contratos, incluindo cinco de Segment Tree, seis de grafos e nove de DP. Cinco objetivos distintos por tópico foram verificados; isso não garante que qualquer modelo selecione corretamente todos eles.
- **Atualização autorizada:** 138 tutoriais USACO atualizados para a revisão `a2a25966a3c8e6cb7e0a87985b0abaac99e2ad40`, após baixar 151 arquivos. Reimportação: 138 inalterados. A quantidade de textos externos permanece 302; não houve ampliação de cobertura integral. TLE continua bloqueado por HTTP 403; vídeos continuam como referências sem transcrições.
- **Busca semântica experimental:** `scripts/evaluate_semantic.py` comparou 12 consultas. Hit@3 por título esperado: lexical 6/12, densa 4/12, fusão 7/12. Modelo de embeddings `all-minilm:22m` de aproximadamente 46 MB; matriz de 302 vetores: 463.872 bytes. A busca lexical permanece padrão. Amostra pequena e somente início dos documentos impedem concluir superioridade geral.
- **Qualidade real:** `scripts/evaluate_learning_quality.py` executou cinco questões no Llama 3.2 1B. Nenhuma satisfez simultaneamente o campo de resultado e valor esperado. Houve também erros conceituais; o resultado não significa simplesmente zero acertos matemáticos. Modelo local permanece experimental, sem troca silenciosa ou comparação não realizada com provedores pagos.
- **Personalização:** geração de material recebe estatísticas do próprio perfil, com questões respondidas, acertos, problemas distintos e aceitos por tópico. Textos antigos gerados não entram nessa evidência; pedido e nível explícitos prevalecem.
- **Artigo:** `docs/artigo_sbc/` contém LaTeX, bibliografia, estilo SBC e PDF, com fundamentos de IA, arquitetura, experimentos e ameaças à validade.

Relatórios reproduzíveis desta execução: `.runtime/semantic-comparison.json`, `.runtime/learning-quality.json` e `.runtime/licensed-update-report.json`. Continuam pendentes avaliação humana de conteúdo, conjunto independente maior, comparação controlada de geradores e ampliação de fontes com acesso autorizado.
