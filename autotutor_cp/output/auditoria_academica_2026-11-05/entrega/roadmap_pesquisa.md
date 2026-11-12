# Roadmap de pesquisa e engenharia

05/11/2026. Todas as comparações abaixo são **propostas**, sem resultados inventados. Ambiente-alvo: i5-12450H, 8 GB, Linux, CPU. A ordem é por dependências; não constitui promessa de prazo de aprendizagem.

## 0. Reprodução do AutoCode antes de comparar percentuais

A pergunta do usuário sobre os 99% exige uma avaliação equivalente, não uma comparação com as cinco questões do Llama. O alvo inicial é **reproduzir o protocolo e medir**, sem prometer o percentual. Separar esta linha da extensão pedagógica.

1. Fixar a versão publicada do AutoCode, código e artefatos oficiais disponíveis, termos de acesso, conjunto e modelos. Se um componente não estiver disponível, declarar reprodução parcial.
2. Obter um conjunto autorizado de problemas, submissões e vereditos oficiais, sem usar respostas dos próprios testes como gabarito. Preservar aceites e rejeições, famílias e dificuldades.
3. Implementar ou executar em ambiente isolado o pipeline fiel, incluindo seleção de validadores/checkers, estratégias e rodadas. Um gerador restrito a contratos não é a mesma intervenção.
4. Comparar nosso protocolo atual e a reprodução em um subconjunto comum, com os mesmos programas e limites. Medir concordância, falsos aceites e falsas rejeições. Controlar versão, custo e modelo, e relatar o denominador e a distribuição de submissões.
5. Fazer ablações do modelo e das rodadas para separar efeito de capacidade, algoritmo e recursos. Uma comparação com modelos distintos sem controle não identifica a causa do desempenho.
6. Somente após essa base, investigar se a tutoria e a recuperação acrescentam benefício. A versão local pode continuar como alternativa econômica, com seus resultados próprios.

A máquina de 8 GB pode coordenar juízes e dados, mas não se presume que execute localmente os modelos usados no artigo. APIs exigem planejamento de custo e credenciais. Esta auditoria não executou uma reprodução paga nem mediu a concordância do nosso juiz com os vereditos oficiais.

## 1. Engenharia antes de novas afirmações científicas

1. **Taxonomia única por ID.** Alinhar contratos, currículo, material e estatísticas, incluindo Segment Tree. Critério: tentativa e aceite em cada assunto aparecem em evidência numérica e exportação, sem depender de grafias de títulos.
2. **Auditar caminhos ativos e legados.** Remover ambiguidade de fallback, regras antigas e formação de trios, após autorização de implementação. Critério: documentar qual chamada a interface usa e cobrir falhas de schema. A auditoria atual não altera esses arquivos.
3. **Proveniência e reprodutibilidade.** Versionar prompts, conjunto de avaliação, modelo/digest, parâmetros, corpus, sementes e hashes. Inicializar controle de versão em etapa própria e preservar o estado atual. Critério: reproduzir decisões e explicar divergências.
4. **Medir recursos.** Coletar wall time, tempo até primeira resposta quando aplicável, RSS do processo inteiro, swap e falhas, em repetidas execuções frias/quentes. Distinguir pesos, vetores e RAM. Manter um modelo por vez, gerar embeddings antes e limitar contexto/saída conforme a tarefa.
5. **Isolamento do juiz.** Se houver implantação pública, implementar ambiente sem acesso a dados do host/rede e políticas de recursos apropriadas. Timeout e RLIMIT não bastam. Avaliar checkers para múltiplas respostas quando a expansão exigir.
6. **Qualidade e cache.** Cachear por pedido, versão de modelo, corpus e evidências do aluno, sem compartilhar conteúdo privado. Não reutilizar resposta defeituosa como referência. Medir acerto e custo do cache.

## 2. Alternativas técnicas viáveis

| Alternativa | Situação atual | Experimento antes de adotar |
|---|---|---|
| SQLite/FTS5 | Implementado | Medir concorrência e tamanho antes de migrar |
| Ollama/Llama 1B | Implementado, qualidade limitada | Amostra independente com mesmo orçamento |
| Qwen2.5-Coder 1.5B | Candidato futuro | Quantização leve, RSS e correção em CPU |
| Qwen2.5-Coder 3B | Candidato futuro distinto do qwen2.5:3b testado | Primeiro viabilidade de memória; não assumir que é o mesmo modelo |
| all-minilm:22m | Experimento separado | Comparar texto completo/trechos e português |
| Embeddings multilíngues leves | Proposta | Benchmark com relevância humana e custo |
| Busca híbrida/RRF | Experimento, sem padrão ativo | Avaliar teste independente e ablação |
| FAISS | Ausente | Comparar NumPy exato, recall e latência no tamanho real |
| Re-ranking dedicado | Proposta | Medir ganho após recuperação fixa e latência |
| PostgreSQL | Ausente | Considerar apenas necessidade multiusuário/operacional |
| Casos adversariais e mutantes | Ampliação proposta | Quantificar falhas que a suíte atual deixa passar |

Não baixar ou ativar modelos maiores apenas por capacidade nominal. O menor modelo que executa pode continuar inadequado para tutoria. Fixar limite de memória e tolerância a falhas antes de comparar; os valores devem vir das necessidades e medições do usuário.

## 3. Direção A — Recuperação orientada por competências

**Pergunta:** representar conceitos, operações e pré-requisitos melhora a recuperação de problemas alinhados ao objetivo?

**Fundamento:** OI-Assistant distingue narrativa e estrutura; representação explícita de relações permite filtrar por competências e condições de uso. O currículo existente é uma base editorial parcial, sem ontologia operacional.

**Hipótese:** recuperação estruturada melhora alinhamento de competência frente à lexical e à semântica simples, sob mesmo número de candidatos e orçamento.

**Método:** definir esquema com conceitos, pré-requisitos, operações, tipos de entrada e objetivo. Dois especialistas anotam problemas sem ver o método. Separar desenvolvimento/teste por família, gerar consultas explícitas e paráfrases, preservar pedidos fora de cobertura. Comparar BM25, TF-IDF multiespaço, embeddings, híbrido e filtros estruturados; ablar pré-requisitos e operações.

**Métricas:** Recall@k com conjunto relevante anotado, MRR para primeiro recurso útil, nDCG para relevância graduada, cobertura de competências, taxa de recusa correta e latência. Relatar concordância e adjudicação entre anotadores.

**Limites:** anotação é custosa, ontologia pode ser rígida, múltiplas técnicas podem resolver a mesma tarefa e filtrar demais reduz recall. **Contribuição esperada:** benchmark e esquema reproduzíveis, além de evidência sobre quando a estrutura ajuda.

## 4. Direção B — Geração pedagogicamente orientada

**Pergunta:** condicionar explicitamente a um objetivo cognitivo e pré-requisitos melhora a adequação do exercício?

**Fundamento:** objetivos de Bloom, scaffolding e feedback formativo fornecem dimensões para planejar e avaliar, sem presumir implementação atual.

**Hipótese:** prompts com objetivo observável e contexto de pré-requisitos aumentam alinhamento e clareza, sem reduzir validade técnica ou revelar solução.

**Método:** preparar pedidos e objetivos, fixar gerador e orçamento, comparar prompt genérico e pedagógico. Especialistas avaliam cegamente exigência cognitiva, clareza, excesso de ajuda e adequação. Depois, conduzir piloto com estudantes, pré/pós e tarefa de transferência; registrar uso de dicas e experiência prévia. Distinguir satisfação e aprendizagem.

**Métricas:** validade, alinhamento, concordância de avaliadores, taxa de conclusão, dependência de ajuda, ganho e retenção quando houver estudo apropriado. Dificuldade prevista deve ser comparada com desempenho real, não assumida pela complexidade.

**Limites:** efeito do professor, prática prévia, teto para avançados e novidade da ferramenta. Preferências de formato não equivalem a estilos fixos comprovados. **Contribuição esperada:** método de condicionamento e rubrica com evidências de adequação; eficácia educacional exige estudo separado.

## 5. Direção C — Verificação algorítmica

**Pergunta:** mutantes e testes adversariais reduzem aceitação de soluções incorretas sem rejeitar soluções válidas?

**Fundamento:** validação diferencial e análise de erros de julgamento em AutoCode. A concordância entre programas pode esconder hipótese comum equivocada.

**Hipótese:** ampliar cobertura por classes de mutação melhora detecção de erros conhecidos e reduz FPR, mantendo FNR baixo.

**Método:** construir mutantes plausíveis: overflow, fronteira, identidade de agregação, marcação tardia em BFS, lazy propagation incompleta e condição de DP errada. Manter referências corretas alternativas. Avaliar a suíte básica e a ampliada em mutantes reservados; validar toda entrada e medir custo. Não gerar código não confiável sem isolamento adequado.

**Métricas:** mutation score excluindo equivalentes, FPR (solução errada aceita), FNR (solução correta rejeitada), tempo até contraexemplo e custo de validação. Relatar a origem do gabarito e incerteza sobre equivalência de mutantes.

**Limites:** mutantes não representam todos os erros, casos grandes dependem da máquina e testes finitos não provam universalidade. **Contribuição esperada:** benchmark de verificadores e estratégia de seleção de testes com ganho medido.

## 6. Direção D — Diversidade e originalidade

**Pergunta:** alterações guiadas de operações e restrições produzem maior diversidade estrutural que a troca de narrativa?

**Fundamento:** AutoCode modifica condições de sementes, enquanto o protótipo preserva contratos. Similaridade lexical não mede equivalência de solução.

**Hipótese:** condicionamento estrutural aumenta variedade de competências e padrões sem comprometer validade.

**Método:** comparar reescrita de cenário, variação controlada de restrições e geração de novo contrato com verificador. Representar estrutura por operações, recorrência, invariante e complexidade esperada. Especialistas anotam equivalência sem ver o método. Comparar com corpus reservado e registrar reuso semântico. Novos contratos exigem implementação e oráculos antes de publicação.

**Métricas:** famílias estruturais distintas por lote, taxa de duplicatas, cobertura, diversidade entre sementes, validade e originalidade por rubrica. Novidade pode ser relativa ao corpus e não universal.

**Limites:** rótulos dependem de especialistas, dificuldade e novidade se confundem, equivalência geral de programas é problemática. **Contribuição esperada:** definição operacional e protocolo de diversidade, com avaliações auditáveis.

## 7. Desenho integrado proposto

Comparar A: LLM sem recuperação; B: LLM com RAG semântico; C: recuperação estruturada; D: recuperação estruturada e validação. Fixar modelo, prompts-base, orçamento, temperatura e máquina. Avaliar todas as tentativas pela mesma auditoria externa e contar rejeições. Relatar taxa válida por tentativa e por custo total, evitando vantagem artificial por descartar falhas somente em D.

Separar desenvolvimento e teste por família algorítmica, controlar duplicação e permitir pedidos não cobertos. Executar múltiplas gerações, com comparação pareada por pedido. Definir tamanho amostral a partir de piloto e precisão desejada. Especialistas cegos avaliam correção, objetivo e novidade; acordos e desacordos permanecem registrados. Publicar intervalos de incerteza quando o desenho os sustentar.

As métricas incluem taxa de problema válido, correção da solução, aderência do enunciado ao contrato, cobertura, diversidade, alinhamento, tempo e pico de memória. Recuperação usa métricas de ranking com relevância anotada. Educação usa estudo próprio de aprendizagem, sem tratar taxa de AC como ganho causal.

## 8. Sequência de prioridades

**Primeiro:** taxonomia e reprodutibilidade, com benchmark pequeno independente. **Depois:** comparação de recuperação e testes adversariais. **Em seguida:** geração condicionada com avaliação cega por especialistas. **Por último:** estudo com alunos e investigação de aprendizagem. Publicar resultados negativos e limites em cada etapa.
