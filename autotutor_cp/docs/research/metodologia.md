# Metodologia e reprodução

## Ambiente e protocolo

Executar na raiz do projeto com Python 3.12 e dependências de requirements.txt. Linux requer bubblewrap, prlimit, g++ e user namespaces habilitados. O juiz falha de forma fechada se o isolamento não funcionar. Não há instalação automática de serviços pagos. Ollama e all-minilm:22m são necessários somente para recuperação densa; carregar o modelo pode consumir tempo e memória. Os testes de fixture não medem inteligência.

Copiar `.env.example` para `.env`, preencher a chave localmente e restringir permissões a 0600. Não publicar esse arquivo. O experimento aceita apenas o endpoint oficial e gemini-3.1-flash-lite com a política gratuita. Não habilita faturamento, não compra créditos, não troca para modelo pago e não faz fallback de provedor. O usuário declarou que a chave utiliza cota gratuita; a resposta de geração não informa a modalidade de faturamento da conta. Orçamento financeiro autorizado: **zero**.

O limite local é de seis tentativas externas por dia UTC, 150000 tokens reservados conservadoramente e intervalo mínimo de 15 segundos. Falhas contam e reservas não são devolvidas. Padrão: uma tentativa; nenhuma repetição oculta. Erros 400/401/403/429 bloqueiam novas tentativas no dia. O controle não substitui as cotas gratuitas do Google. A reserva é um teto técnico calculado a partir do tamanho do payload, não consumo ou cobrança observada. O ledger fica em `.runtime/research/budget.sqlite3`; não apagá-lo para contornar limites.

## Comandos

```sh
# Integração offline com solução conhecida; nenhuma chamada externa
.venv/bin/python scripts/run_research_pilot.py --target 'Segment Tree' --strategies direct
# Comparação local da recuperação; embeddings locais podem criar índice
.venv/bin/python scripts/run_research_pilot.py --retrieval-only --output .runtime/research/retrieval
# Baseline local explícito, executado separadamente para limitar memória
.venv/bin/python scripts/run_research_pilot.py --local --strategies direct
# Chamadas reais: executar apenas dentro da cota gratuita e dos limites locais
.venv/bin/python scripts/run_research_pilot.py --live --strategies direct rag structured
# Testes, com transporte de API simulado
.venv/bin/python -m pytest tests -q
```

O Laboratório IA tem um painel recolhido de experimento. A renderização não chama a API; o botão executa uma geração estruturada e só libera o artefato para prática após validação. As configurações desse painel vêm do `.env`; os controles legados dos outros provedores continuam separados.

## Baselines

`free_direct` recebe só o tópico, mas não possui oráculo independente e não é publicado como problema tecnicamente validado. `direct`, `examples`, `rag`, `structured` e `iterative` compartilham o contrato de entrada/saída, para permitir comparação verificável. Portanto, o `direct` deste piloto é uma variação de contrato sem recuperação, não a geração livre A descrita na proposta. `examples` acrescenta exemplos do contrato; `rag` acrescenta contexto; `structured` acrescenta competências, dificuldade e objetivo. `iterative` permite no máximo uma correção a partir do diagnóstico. Não se comparou a ordem de geração enunciado/solução.

A API usa temperatura 0,3, máximo de 4096 tokens de saída, pensamento mínimo e schema JSON; não aceita seed de geração neste adaptador. Seed 42 controla os testes locais. O baseline local atual tem parâmetros distintos do cliente Ollama legado e não constitui comparação controlada com a API sem padronização adicional.

## Recuperação e corpus

Corpus público existente: 5551 registros e 6837 chunks; 302 documentos externos integrais (164 CP-Algorithms, 138 USACO), 19 conteúdos autorais e 5230 referências. A recuperação experimental exclui referências sem texto e documentos autorais, preservando origem e licença. Isso não significa que todos os sites enviados anteriormente foram importados integralmente.

No piloto, no máximo três documentos distintos e 2200 caracteres de contexto, candidatos lexicais/semânticos de até 18 posições, RRF k=60. Denso: all-minilm:22m, textos truncados a 1600 caracteres mais título e seção; cache compactado com checksum do corpus. Alterações do corpus invalidam o cache. A primeira medição semântica inclui indexação; medições seguintes reutilizam o índice. Não comparar essas latências como desempenho estabilizado.

## Validação e evidências

Schema → compilação isolada → exemplos gerados → validação das entradas do contrato → testes diferenciais e comparação com solução confiável original. O contrato Segment Tree soma em intervalos com atualização pontual gerou 43 casos em cada execução. O enunciado, dicas e dificuldade não passaram por revisão humana. Dificuldade e tipo pedagógico são instruções, sem certificação automática.

Cada pasta de execução guarda prompt, resposta, versão retornada, consumo, fontes/scores, tempos, seed e manifesto de hashes de cinco módulos centrais. O manifesto não é snapshot completo do ambiente; dependências não estão travadas. Resultados exportados: `data/research/results/2026-11-05/`. `.runtime/` guarda originais e cache. O segredo não integra os relatórios. Não enviar histórico real de alunos: o protótipo só aceita perfis marcados como sintéticos.

`queries.json` é modelo para anotação, sem rótulos prontos. Precision, Recall, MRR e nDCG não são calculados sem julgamentos revisados e universo relevante completo. `human_rubric.json` define revisão independente; `synthetic_profiles.json` contém eventos inventados. Tempo, dicas e tipo de erro ficam disponíveis como campos, mas o BKT atual só usa acerto/erro por item e competência.
