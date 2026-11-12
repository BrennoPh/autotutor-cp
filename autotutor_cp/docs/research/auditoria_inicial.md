# Diagnóstico anterior às alterações experimentais

A auditoria de 05/11/2026 foi concluída antes desta evolução. Estado inicial: 39 contratos, RAG de materiais lexical separado da geração, sem modelagem BKT e sem orçamento persistente de chamadas.

# Auditoria técnico-científica do AutoTutor-CP

Data: **05/11/2026**, America/Maceio. Escopo: código e evidências existentes em `/home/brenno/Downloads/Nuvem/Projeto_IA/autotutor_cp` e documentos fornecidos no diretório pai. Auditoria de leitura, com novos artefatos somente na pasta de saída. Os hashes do código antes/depois constam nas evidências. Não foram extraídos dados privados, senhas, conversas ou chaves do banco de progresso. Não houve chamada paga nem nova inferência de modelo nesta auditoria.

## 1. Método e limitações de acesso

Foram examinados os módulos Python de produção, configurações, scripts de importação e avaliação, testes, README, plano de evolução, artigo local, corpus público e relatórios. O inventário acompanha a entrega. A suíte foi executada com bancos temporários e transporte de IA simulado onde definido nos testes. As compilações e programas de teste são locais, conhecidos, com limites existentes no juiz. Essa execução não mede qualidade de um provedor real.

Não há repositório Git utilizável no diretório inspecionado ou nos pais consultados. Consequentemente, commits, autoria por mudança e ordem exata não são verificáveis. Não foram inventados diffs ou datas de implementação. A cronologia combina documentos, histórico fornecido e registros preservados; timestamps de arquivos são auxiliares.

Os três artigos fornecidos foram lidos em texto integral extraído. As identidades foram confrontadas com páginas primárias e identificadores. Algumas páginas de DOI/editoras não responderam, mas os PDFs locais e registros de conferências permitiram confirmar os artigos centrais. Não foram contornados controles de acesso. Os documentos de propostas usam algumas expressões mais fortes do que as evidências sustentam; abaixo elas são corrigidas sem alterar os originais.

## 2. Evidências e proposta original

- **E01:** `../Plano de Trabalho - IA e Programação Competitiva.pdf`: AutoCode como base e extensão por mini-juiz e tutoria dirigida a dificuldades.
- **E02:** `../Apresentação Final Pitch - IA e Programação Competitiva.pdf` e `../apresentacao_FIA.pdf`, além das versões PPTX: identificação, problema e extensão proposta.
- **E03:** `../Trabalho.pdf`: extensão em até três meses, fidelidade ao objetivo e apresentação de resultados em 5–9 minutos, PDF para envio. A apresentação completa de 24 slides atende ao pedido atual; o roteiro fornece rota curta.
- **E04:** instrução original anexada em `178aeaab-28d3-4d42-b2d2-1dbe69e40642/Pasted text.txt`: requisitos de AutoCode, OI-Assistant e Codigen e fallback inicialmente permitido.
- **E05:** `README.md` e `docs/PLANO_EVOLUCAO.md`: documentação atual, interpretações e próximos passos.
- **E06:** `core/autocode_engine.py`, `problem_bank.py`, `classic_judge.py`, `extended_judge.py`, `segment_tree.py`: geração e verificação.
- **E07:** `core/rag_retriever.py`, `knowledge.py`, `codigen_tutor.py`: recuperação e materiais.
- **E08:** `core/llm_client.py`, `cloud_providers.py`, `ai_connection.py`, `ollama_client.py`: inferência e diagnóstico.
- **E09:** `core/progress_store.py`, `accounts.py`, `classrooms.py`, `library.py`, `study_pages.py`, `practice_context.py`: persistência e continuidade.
- **E10:** `core/ai_coach.py`, `learning_engine.py`, `topic_plans.py`, `school_views.py`, `team_builder.py`: análise, trilhas e trios.
- **E11:** `data/knowledge.sqlite3` (somente leitura), JSONs de problemas, currículo, fontes e cobertura.
- **E12:** `scripts/evaluate_semantic.py` e `.runtime/semantic-comparison.json`.
- **E13:** `scripts/evaluate_learning_quality.py` e `.runtime/learning-quality.json`.
- **E14:** `.runtime/qwen-evaluation.json`, `llama-return.json`, `llama-light-smoke.json`, relatórios de importação.
- **E15:** `tests/`, log da suíte atual e manifesto de hashes nesta entrega.
- **E16:** três PDFs científicos locais e seus identificadores R1–R3.

A motivação documentada é usar a precisão da avaliação de programas para orientar aprendizagem. O plano espera feedback dirigido e exercício imediato sem entregar a resposta. Não define um ensaio controlado nem hipótese estatística. A hipótese reconstruída nesta auditoria é que evidências executáveis e recuperação orientada por competências podem melhorar especificidade e alinhamento. Ela continua por testar.

O plano descreve o resultado AutoCode como “atesta validade matemática” e atribui eficácia ampla a Codigen. As fontes sustentam concordância experimental e resultados em contextos particulares, não prova universal nem eficácia do nosso sistema. É necessário manter essa correção na defesa.

## 3. Matriz de rastreabilidade

Categorias: **P0** proposto inicialmente; **F** implementado e funcional nos cenários verificados; **P** implementado parcialmente; **E** experimentado sem evidência suficiente para adoção; **N** planejado, não implementado; **V** não verificável. A proposta original é registrada em coluna própria para não confundir origem e estado atual.

| Elemento | Origem | Implementação e evidência | Estado e limite |
|---|---|---|---|
| Compilação e vereditos C++ | P0, E01/E04 | MiniJudge e testes E06/E15 | F: AC/WA/TLE/RE/CE nos casos testados |
| Isolamento seguro completo | P0, linguagem do plano | runner aplica recursos POSIX | P: sem isolamento de arquivos/rede |
| Validação std/brute | P0 | sete sementes, casos pequenos | F no protocolo delimitado; sem prova universal |
| Oráculos independentes | extensão de engenharia | 24 tarefas clássicas e oito novas | F em testes; independência não absoluta |
| Problemas estruturalmente inéditos | P0 | adapt_seed preserva objetivo e gramática | P: narrativa e limites, não novidade demonstrada |
| Geradores/checkers por LLM | AutoCode original | verificadores escritos previamente | N para arquitetura completa do artigo |
| Interatividade e múltiplas respostas | artigo de base | comparação textual normalizada | N para checkers especializados |
| Recomendação multivetor | P0 | três espaços TF-IDF e reranker | F como adaptação lexical |
| Embeddings/FAISS na recomendação | P0, alternativa inicial | NumPy/TF-IDF na aplicação | P para intenção; FAISS ausente |
| RAG de materiais | expansão | FTS5/BM25, texto externo | F, qualidade semântica limitada |
| RAG na seleção do problema | integração desejada | catálogo de 39 no prompt | P: geração sem recuperador de candidatos |
| Busca densa/híbrida do acervo | evolução | experimento all-minilm/RRF | E: 4/12 e 7/12, padrão lexical mantido |
| Conteúdo integral dos seis sites | expansão | 302 textos e 5.230 links | P: cobertura integral não existe |
| Vídeos e transcrições | expansão | 27 referências de vídeos | P: sem transcrições |
| Catálogo TLE | expansão | relatório HTTP 403 | P: referência inicial, lista não importada |
| Feedback pós-falha | P0 | prompt com caso e código | F na integração; eficácia e veracidade não medidas |
| Guardrails pedagógicos | P0 | instruções e regex | P: não prova de não revelação |
| Fluxograma | P0 | Mermaid gerado e validação sintática limitada | F na interface; correção de algoritmo não certificada |
| Materiais e páginas próprias | expansão | biblioteca e study_pages | F em testes de integração |
| Problema do estudo/busca atual | expansão | practice_context e UI | F em testes com modelo controlado |
| Persistência e perfis | expansão | SQLite e consultas por proprietário | F em cenários de teste |
| Ajuste de pesos com o banco | expectativa histórica | não há treino ou otimizador | N; RAG não é treinamento contínuo |
| Diagnóstico e trilha por IA | expansão | ai_coach e topic_plans | F na integração, sem calibração de domínio |
| Segment Tree nas estatísticas | suporte ampliado | ausente entre nove tópicos | P: histórico existe, agregação omite o tópico |
| Turmas e professor | expansão | contas, turmas, tarefas, permissões | F em testes; sem estudo com turma real |
| Melhor trio garantido | expansão | propose_teams com LLM e schema | P: proposta válida, sem garantia ótima |
| Algoritmo heurístico de trios | versão legada | team_builder presente, interface usa LLM | F em módulo legado, sem uso atual nesse fluxo |
| Bloom, ZDP e mastery learning | pedido de aprofundamento | relações conceituais possíveis | N como modelos pedagógicos formais |
| Ontologia/grafo de competências | pesquisa futura | currículo com pré-requisitos apenas | N para recuperação estruturada |
| Efeito educacional local | objetivo amplo | sem participantes ou pré/pós | V para conclusão causal |
| Histórico por commits | desejável | Git indisponível | V |

## 4. Artigos e comparação científica

**AutoCode (R1).** Shang Zhou e colaboradores, preprint 2025 e ICLR 2026, arXiv:2510.12803. Pesquisa autoria de problemas e confiabilidade dos testes. Usa múltiplas rodadas de validadores, geradores, checkers e, quando necessário, interactors. Resultados: Tabela 1, 91,1% em 7.538 problemas/195.988 submissões com o3; Tabela 2, 98,7% em outro conjunto de 720 e GPT-5-High. O protocolo de geração também relata melhoria de referência de 86% para 94% após filtragem. Esses números não são intercambiáveis nem resultados locais. O texto e a figura de avaliação humana utilizam denominadores distintos; evitar misturar percentuais dessa parte sem explicitar o universo. O protótipo aproveita estratégias de testes e cruzamento, preservando contratos em vez de gerar estrutura aberta.

**OI-Assistant (R2).** Yuhua Su, Ping Nie e Xin Meng, 2025, DOI:10.15388/ioi.2025.09. Recupera problemas semelhantes sob narrativas distintas. Usa três representações, embeddings de API, FAISS e reranker. Avalia 900 entradas em três configurações, relata recall acima de 80% no top-50 e experiência com 36 estudantes. Avaliação percebida não estabelece ganho causal. O custo do reranker e corpus Luogu limitam generalização. O protótipo adapta a separação em três espaços TF-IDF, sem reproduzir índices, amostras e métricas do artigo.

**Codigen (R3).** Mohamed Ez-zaouia e Yazid Boumarafi, VL/HCC 2025, DOI:10.1109/VL-HCC65237.2025.00038. Trata autoria visual e ajuda in situ. O título IEEE usa “LLMs”, enquanto a página do evento expande “Large Language Models”. Não confundir com CodeGen. A avaliação tem 29 participantes no total, 23 na atividade e seis entrevistas, com medidas pré/pós em JavaScript. Efeitos favoráveis para iniciantes não se repetem integralmente em intermediários; SUS 70,95 não é significativamente superior ao referencial 68 reportado. Não há base para dizer que o trabalho prova eficácia do nosso mapeamento de fraquezas. O protótipo adota prompter e helpers, sem reproduzir o ambiente visual ou o estudo.

## 5. Arquitetura e decisões

Python/Streamlit organiza a interação e o estado. NumPy implementa TF-IDF e produto matricial. SQLite guarda perfis e artefatos em um banco e corpus comprimido/FTS5 em outro. requests fornece transporte Ollama local; SDKs google-genai e openai dão acesso aos provedores configuráveis. g++/subprocess e runner POSIX fazem avaliação determinística. pytest e AppTest verificam lógica e interface. Não há FAISS, PostgreSQL, serviço de treinamento ou índice denso ativo na aplicação.

A escolha de SQLite reduz dependências e permite persistência local; limita concorrência de escrita e não substitui políticas operacionais. Streamlit acelera prototipação, com dependência de reruns e estado de sessão. NumPy é suficiente para a dimensão atual, mas não avalia equivalência algorítmica. APIs permitem modelos maiores, ao custo de latência, cota e credenciais. Ollama evita envio externo, mas a máquina limitada e o modelo leve restringem desempenho e qualidade. As razões são inferências de engenharia coerentes com código e pedidos; não há registro de uma seleção formal de todas as alternativas.

A arquitetura futura deve aparecer separada: catálogo de competências, recuperador estruturado, avaliador de alinhamento, mutantes e benchmark independente. Nada disso deve ser desenhado como se estivesse ativo.

## 6. Resultados e falhas confirmadas

Inventário atual: 39 contratos, cinco Segment Tree, seis grafos, nove DP. Corpus: 302 textos externos, 19 autorais, 5.230 referências, total 5.551 documentos e 6.837 trechos. O banco público tem cerca de 14,74 MiB na consulta; tamanho de arquivo não é RAM. Atualização de 138 tutoriais não ampliou a contagem de textos.

Recuperação: lexical 6/12, semântica 4/12, RRF 7/12 no indicador tópico por título top-3. Tempo registrado 21,28 s para a execução do experimento, não por consulta. Vetores: 463.872 bytes, sem incluir modelo e processo. O índice denso usa apenas começo do documento. Não há avaliação independente ampla nem conclusão estatística de superioridade.

Geração local: Llama 1B não acertou campo e valor exigidos nas cinco questões. Há formato inválido e erros conceituais, incluindo DFS e Segment Tree. A pergunta de prefixos tem número esperado em chave diferente com justificativa incorreta. O escore mistura conformidade e valor: não significa simplesmente zero operações matemáticas corretas.

| Problema | Evidência | Causa demonstrada ou provável | Consequência | Próxima ação |
|---|---|---|---|---|
| Lentidão Qwen 3B | E14: timeout 300,11 s | Custo local elevado é hipótese sem perfil causal completo | Interação interrompida | Medir RSS/swap/latência e comparar 1.5B |
| Conteúdo numérico inconsistente | E13: cinco saídas brutas | Modelo/configuração falham; causa exata não isolada | Tutor exige revisão humana | Separar formato, valor e fundamentação |
| SegTree fora das métricas | E10/E11 e consulta sintética | Agregação percorre nove títulos sem Segment Tree | Evidência incompleta para personalização | Taxonomia única por ID |
| Geração sem busca RAG de candidatos | E06 | Arquitetura envia catálogo ao LLM | Integração de pesquisa parcial | Comparar seleção estruturada e lexical |
| Diversidade restrita | E06, prompt preserva objetivo | Contratos fixos | Novidade estrutural não demonstrada | Rubrica estrutural e deduplicação |
| TLE parcial | E11/E14: 403 | Origem não verificada segundo resposta registrada | Lista não importada | Acesso autorizado/exportação |
| Caminho legado de lacunas SegTree | E07: tupla com três valores e unpack em dois | Inconsistência no fallback não ativo | ValueError em chamada legada | Reproduzir em sandbox e corrigir depois |

O último caso foi identificado por leitura, sem alterar a aplicação e sem afirmar ocorrência no fluxo normal: app.py usa require_model=True e não percorre aquele fallback. Métodos legados de estimate_level/build_roadmap também contêm regras fixas, mas o fluxo atual de orientação chama ai_coach. É incorreto afirmar que todo arquivo com regra determina a experiência atual.

Erros Gemini 400 e 503, DeepSeek 402 e quota 429 foram relatados pelo usuário no histórico. O adaptador atual tem tratamento e testes para essas classes. Não se reproduziu acesso real a essas contas na auditoria, logo a solução operacional externa permanece condicionada ao provedor.

## 7. Por que os 98,7% do AutoCode não foram reproduzidos

Não existe uma medida local equivalente para concluir que passamos de 98,7% a outro percentual. O artigo mede concordância de vereditos; a avaliação de cinco perguntas mede valor no campo esperado e formato. A implementação é uma adaptação deliberadamente restrita, sem as múltiplas rodadas e seleção de verificadores do pipeline completo. O modelo local é menor e o protocolo é diferente. Portanto, o resultado do artigo não foi transferido nem reproduzido.

Isso não demonstra impossibilidade de alcançar resultado semelhante. Exige um estudo em conjunto comum de submissões e vereditos oficiais, com pipeline fiel e ablações. A escolha por viabilidade em CPU não justifica atribuir a essa versão a confiabilidade medida por outra implementação. A principal lacuna científica é justamente a ausência de reprodução comparável. O roadmap inclui essa etapa antes da comparação de percentuais.

## 8. Maturidade, lacunas e conclusões

Contribuição principal: integração funcional, adaptação de métodos existentes e verificadores de contratos. Contribuição experimental: avaliações exploratórias pequenas e transparentes. Não há novo algoritmo de IA validado, calibração de dificuldade, prova de optimalidade de trios, ganho de aprendizagem ou superioridade geral entre modelos.

A proposta original de tutoria por dificuldades possui implementação, porém sua eficácia continua aberta. É possível demonstrar conexão entre veredito e prompt e persistência de resultados. Não é possível concluir que o feedback corrige a compreensão ou que uma trilha estima o tempo real de domínio.

As prioridades são unificar competências, medir alinhamento e correção com benchmark independente, reforçar testes com mutantes e comparar recuperação estruturada. Estudos com especialistas e depois estudantes devem distinguir implementação, relevância, desempenho e aprendizagem. O roadmap detalha hipóteses e métricas sem apresentá-las como resultados já obtidos.

## 9. Relação de arquivos examinados

O arquivo `evidencias/manifesto_codigo_antes.json` lista os arquivos de produção, scripts e testes com hash SHA-256. Os principais documentos e relatórios estão identificados em E01–E16. Todos os módulos de produção foram inventariados; a inspeção profunda priorizou os fluxos de IA, recuperação, geração, juiz, persistência, análise e interface. Não se reivindica prova formal ou auditoria de segurança completa de cada linha.
