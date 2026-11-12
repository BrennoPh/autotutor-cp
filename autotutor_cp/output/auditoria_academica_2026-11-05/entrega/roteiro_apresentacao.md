# Roteiro de apresentação e estudo

Versão completa: 24 slides, aproximadamente 30–40 minutos com explicações. As notas também estão incorporadas no PowerPoint.

## Rota para a apresentação da disciplina

O documento original `Trabalho.pdf` pede 5–9 minutos. Para cerca de oito minutos, use os slides **1, 2, 3, 11, 12, 16, 17, 18 e 23**. Distribuição sugerida: 20, 40, 40, 70, 50, 50, 60, 60 e 50 segundos, respectivamente (440 segundos, cerca de 7 min 20 s). Reserve o restante para transições. Os demais slides servem de apoio e respostas à banca; não é preciso tentar apresentar toda a fundamentação em nove minutos.

No PowerPoint, a visualização do apresentador mostra as notas. Nas notas, as evidências locais identificam módulos e arquivos; as referências científicas têm DOI ou endereço verificável. As sugestões de tempo são planejamento, não uma medição de fala.

## Slide 01 — IA na aprendizagem de programação competitiva

A apresentação examina o AutoTutor-CP, um protótipo que associa geração de materiais e exercícios, recuperação de referências e avaliação local de programas. A identificação do discente consta na apresentação inicial fornecida. A pergunta da capa sintetiza a análise atual; ela não aparece literalmente como uma pergunta formal no planejamento original. O objetivo documentado era estender o AutoCode com avaliação local e tutoria sensível às dificuldades do estudante.

O resultado demonstrável é uma integração funcional com mecanismos de verificação e experimentos exploratórios. Ainda não há estudo que demonstre aprendizagem, transferência para novos problemas ou superioridade sobre outros tutores. Os resultados dos artigos serão identificados como externos e separados dos resultados locais.

Esta versão de 24 slides serve à exposição completa e ao estudo. O arquivo Trabalho.pdf exige 5 a 9 minutos na disciplina: o roteiro oferece uma seleção de nove slides para aproximadamente oito minutos, deixando os demais disponíveis para a banca.

Banca: “Qual é a contribuição?” Responder: integração verificável de métodos existentes e identificação empírica de limites, com um programa experimental proposto. Transição: apresentar a necessidade que motivou o trabalho.

EVIDÊNCIAS LOCAIS: ../Plano de Trabalho - IA e Programação Competitiva.pdf; ../Apresentação Final Pitch - IA e Programação Competitiva.pdf

REFERÊNCIAS:
Zhou, S. et al. AutoCode: LLMs as Problem Setters for Competitive Programming. ICLR 2026. Preprint de 2025, arXiv:2510.12803. https://proceedings.iclr.cc/paper_files/paper/2026/hash/1bd78da0966968409e65b5e0b5dbb57e-Abstract-Conference.html
Su, Y.; Nie, P.; Meng, X. OI-Assistant: A Retrieval Augmented System for Similar Problem Discovery and Interactive Learning in Competitive Programming. Olympiads in Informatics, 19, 129–144, 2025. DOI:10.15388/ioi.2025.09. PDF local fornecido e https://ioi.te.lv/oi/files/volume19.pdf
Ez-zaouia, M.; Boumarafi, Y. Codigen: Enhancing Personalized Programming Education with Visual Authoring and LLMs. IEEE VL/HCC, 2025. DOI:10.1109/VL-HCC65237.2025.00038. https://conf.researchr.org/details/vlhcc-2025/vlhcc-2025-research-papers/29/Codigen-Enhancing-Personalized-Programming-Education-with-Visual-Authoring-and-Large

## Slide 02 — Motivação e hipótese de trabalho

O plano de trabalho identifica o custo de produzir problemas corretos e propõe transformar um gerador em plataforma de tutoria adaptativa. Sua extensão combina um mini-juiz com análise dos erros e exercícios destinados às dificuldades observadas. Essa motivação está documentada, ao contrário de uma hipótese causal formal acompanhada de protocolo experimental.

A formulação apresentada na coluna direita é uma reconstrução analítica: se a IA recebe o veredito e o caso que falhou, pode produzir orientação mais específica do que uma explicação genérica. Recuperar um problema semelhante pode ajudar a contextualizar a técnica. “Pode” expressa uma hipótese, pois a implementação, por si só, não mede ganho educacional.

Vereditos informam efeitos observáveis do programa, mas não identificam automaticamente a causa cognitiva do erro. WA pode decorrer de índice, tipo numérico, interpretação ou algoritmo. TLE não demonstra, isoladamente, complexidade quadrática. A orientação precisa reconhecer essa ambiguidade.

Banca: “Como provar essa hipótese?” Comparar feedback sem evidência e feedback com evidência, controlando tarefa e modelo, e medir transferência e qualidade por especialistas. Transição: confrontar a intenção documentada com os componentes encontrados.

EVIDÊNCIAS LOCAIS: ../Plano de Trabalho - IA e Programação Competitiva.pdf; core/codigen_tutor.py:diagnose_error

REFERÊNCIAS:
Zhou, S. et al. AutoCode: LLMs as Problem Setters for Competitive Programming. ICLR 2026. Preprint de 2025, arXiv:2510.12803. https://proceedings.iclr.cc/paper_files/paper/2026/hash/1bd78da0966968409e65b5e0b5dbb57e-Abstract-Conference.html
Su, Y.; Nie, P.; Meng, X. OI-Assistant: A Retrieval Augmented System for Similar Problem Discovery and Interactive Learning in Competitive Programming. Olympiads in Informatics, 19, 129–144, 2025. DOI:10.15388/ioi.2025.09. PDF local fornecido e https://ioi.te.lv/oi/files/volume19.pdf
Ez-zaouia, M.; Boumarafi, Y. Codigen: Enhancing Personalized Programming Education with Visual Authoring and LLMs. IEEE VL/HCC, 2025. DOI:10.1109/VL-HCC65237.2025.00038. https://conf.researchr.org/details/vlhcc-2025/vlhcc-2025-research-papers/29/Codigen-Enhancing-Personalized-Programming-Education-with-Visual-Authoring-and-Large

## Slide 03 — Proposta e estado verificado

A classificação considera código, testes e registros, não somente o README. “Funcional” significa que existe um caminho executável e que os testes apropriados o exercitam. Não significa que todas as saídas da IA sejam corretas. “Parcial” indica que a implementação atende parte do objetivo, mas não sustenta a afirmação mais forte.

A geração preserva objetivos e gramáticas de contratos conhecidos. Ela pode trocar cenário e apresentação, mas não demonstra originalidade estrutural. A tutoria recebe evidências do aluno, porém faltam validação cognitiva e estudo de aprendizagem. O recuperador de problemas preserva a ideia de separar representação do enunciado, conceitos e estratégia, usando TF-IDF em lugar dos embeddings neurais e FAISS do OI-Assistant.

O acervo de materiais utiliza outro mecanismo: FTS5/BM25. A comparação com embeddings existe como script e relatório, sem ativação na aplicação. As categorias completas da auditoria incluem proposta inicial, funcional, parcial, experimentado sem resultado suficiente, planejado e não verificável. Uma ideia inicialmente proposta pode, portanto, ter implementação parcial hoje.

Banca: “Por que chamar de parcial se funciona?” Porque executar uma adaptação é uma evidência mais fraca que gerar um problema inédito, correto e pedagogicamente calibrado. Transição: situar os artigos sem transferir seus resultados ao protótipo.

EVIDÊNCIAS LOCAIS: core/mini_judge.py; core/autocode_engine.py; core/rag_retriever.py; scripts/evaluate_semantic.py

REFERÊNCIAS:
Zhou, S. et al. AutoCode: LLMs as Problem Setters for Competitive Programming. ICLR 2026. Preprint de 2025, arXiv:2510.12803. https://proceedings.iclr.cc/paper_files/paper/2026/hash/1bd78da0966968409e65b5e0b5dbb57e-Abstract-Conference.html
Su, Y.; Nie, P.; Meng, X. OI-Assistant: A Retrieval Augmented System for Similar Problem Discovery and Interactive Learning in Competitive Programming. Olympiads in Informatics, 19, 129–144, 2025. DOI:10.15388/ioi.2025.09. PDF local fornecido e https://ioi.te.lv/oi/files/volume19.pdf
Ez-zaouia, M.; Boumarafi, Y. Codigen: Enhancing Personalized Programming Education with Visual Authoring and LLMs. IEEE VL/HCC, 2025. DOI:10.1109/VL-HCC65237.2025.00038. https://conf.researchr.org/details/vlhcc-2025/vlhcc-2025-research-papers/29/Codigen-Enhancing-Personalized-Programming-Education-with-Visual-Authoring-and-Large

## Slide 04 — Artigos que fundamentaram a proposta

AutoCode é o título confirmado do artigo de Shang Zhou e colaboradores, com preprint de 2025 e versão ICLR 2026. Não é um artigo chamado “AutoCodeLLM”. Seu protocolo gera e valida testes e problemas usando papéis especializados. A Tabela 1 reporta 91,1% de consistência em 7.538 problemas e 195.988 submissões, com o3; a Tabela 2 reporta 98,7% em 720 problemas e outro desenho experimental, com GPT-5-High. Nenhum desses percentuais representa correção matemática universal.

OI-Assistant, de Yuhua Su, Ping Nie e Xin Meng, usa representações múltiplas e reranking para localizar estruturas semelhantes. O estudo inclui 900 consultas em três configurações e avaliação de uso com 36 estudantes. O texto reporta recall superior a 80% em top-50 para o reranker. Isso não equivale ao nosso Hit@3 nem demonstra transferência de aprendizagem.

Codigen é uma ferramenta de autoria visual com assistência local à atividade. Os 29 participantes incluem 23 na atividade e seis entrevistas; não são 29 pessoas em todas as medidas. Os resultados pré/pós favorecem iniciantes e não mostram o mesmo efeito nos intermediários. Não se deve chamá-lo de “CodeGen”, nome associado a outros trabalhos.

Banca: diferenças de amostra, tarefa e métrica impedem comparação direta. Transição: explicar precisamente quais ideias o projeto adaptou.

EVIDÊNCIAS LOCAIS: PDFs locais: AutoCode §4 Tabelas 1–2; OI-Assistant §4; Codigen §V–VI

REFERÊNCIAS:
Zhou, S. et al. AutoCode: LLMs as Problem Setters for Competitive Programming. ICLR 2026. Preprint de 2025, arXiv:2510.12803. https://proceedings.iclr.cc/paper_files/paper/2026/hash/1bd78da0966968409e65b5e0b5dbb57e-Abstract-Conference.html
Su, Y.; Nie, P.; Meng, X. OI-Assistant: A Retrieval Augmented System for Similar Problem Discovery and Interactive Learning in Competitive Programming. Olympiads in Informatics, 19, 129–144, 2025. DOI:10.15388/ioi.2025.09. PDF local fornecido e https://ioi.te.lv/oi/files/volume19.pdf
Ez-zaouia, M.; Boumarafi, Y. Codigen: Enhancing Personalized Programming Education with Visual Authoring and LLMs. IEEE VL/HCC, 2025. DOI:10.1109/VL-HCC65237.2025.00038. https://conf.researchr.org/details/vlhcc-2025/vlhcc-2025-research-papers/29/Codigen-Enhancing-Personalized-Programming-Education-with-Visual-Authoring-and-Large

## Slide 05 — Adaptação dos métodos científicos

O projeto implementa uma adaptação, não uma reprodução experimental dos três artigos. AutoCode permite modificar condições para criar novos problemas e inclui validadores, geradores e checkers selecionados em ciclos. Aqui os verificadores são escritos previamente para contratos conhecidos. Nas sete sementes originais há cruzamento std/brute em casos pequenos; nas 32 tarefas acrescentadas, o C++ de referência é comparado a oráculos Python. Depois da adaptação, há comparação adicional com a solução confiável do contrato.

O OI-Assistant usa embeddings da API e FAISS. O código local cria três vocabulários TF-IDF e combina escores com pesos 0,25, 0,45 e 0,30, seguidos de reranking por LLM. O nome da classe não transforma esses vetores em embeddings neurais. O Codigen inspira materiais parametrizados e botões de ajuda, enquanto seu ambiente visual de autoria não foi reproduzido.

O artigo original de RAG treina componentes em uma arquitetura probabilística. O AutoTutor usa recuperação textual e composição de contexto com um gerador já existente. Essa adaptação atende ao objetivo de fundamentação externa, mas não implementa o treinamento conjunto do artigo.

Banca: “O que é próprio?” A integração entre contratos verificáveis, persistência, contexto do estudo e evidências resumidas. Transição: explicar como o gerador de linguagem funciona.

EVIDÊNCIAS LOCAIS: core/autocode_engine.py:double_validate; core/rag_retriever.py:TfidfSpace; core/codigen_tutor.py

REFERÊNCIAS:
Zhou, S. et al. AutoCode: LLMs as Problem Setters for Competitive Programming. ICLR 2026. Preprint de 2025, arXiv:2510.12803. https://proceedings.iclr.cc/paper_files/paper/2026/hash/1bd78da0966968409e65b5e0b5dbb57e-Abstract-Conference.html
Su, Y.; Nie, P.; Meng, X. OI-Assistant: A Retrieval Augmented System for Similar Problem Discovery and Interactive Learning in Competitive Programming. Olympiads in Informatics, 19, 129–144, 2025. DOI:10.15388/ioi.2025.09. PDF local fornecido e https://ioi.te.lv/oi/files/volume19.pdf
Ez-zaouia, M.; Boumarafi, Y. Codigen: Enhancing Personalized Programming Education with Visual Authoring and LLMs. IEEE VL/HCC, 2025. DOI:10.1109/VL-HCC65237.2025.00038. https://conf.researchr.org/details/vlhcc-2025/vlhcc-2025-research-papers/29/Codigen-Enhancing-Personalized-Programming-Education-with-Visual-Authoring-and-Large
Lewis, P. et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS, 2020. https://arxiv.org/abs/2005.11401

## Slide 06 — LLMs e geração condicionada

Um modelo de linguagem aprende regularidades para atribuir probabilidade ao próximo token. O produto apresentado decompõe a probabilidade da sequência inteira em decisões condicionais. Token não corresponde necessariamente a uma palavra: o tokenizador pode separar código, números e palavras em subpartes.

No Transformer, consultas Q e chaves K determinam escores de atenção; a normalização softmax produz pesos usados para combinar valores V. A divisão pela raiz da dimensão das chaves controla a escala dos produtos. Em um gerador autorregressivo, uma máscara impede acessar tokens futuros. O protótipo utiliza modelos prontos, sem implementar nem treinar essa arquitetura.

Pré-treinamento fornece regularidades gerais. Instruction tuning adapta o comportamento de modelos a tarefas orientadas por instruções; essa etapa ocorreu no desenvolvimento dos modelos e não no AutoTutor. Prompt engineering organiza o contexto durante a inferência. O prompt GUARDRAILS contém três exemplos de feedback para WA, TLE e CE, caracterizando few-shot.

Uma explicação fluente pode continuar uma premissa falsa ou errar uma operação. Temperatura zero reduz aleatoriedade, mas não produz um verificador de verdade. Banca: “Atenção explica a decisão?” Não fornece, por si só, uma explicação causal confiável. Transição: discutir recursos e os limites do modelo local.

EVIDÊNCIAS LOCAIS: core/codigen_tutor.py:GUARDRAILS; core/llm_client.py:complete; core/ollama_client.py:chat

REFERÊNCIAS:
Vaswani, A. et al. Attention Is All You Need. NeurIPS, 2017. https://arxiv.org/abs/1706.03762

## Slide 07 — Inferência local em uma máquina de 8 GB

A restrição considerada é um Intel Core i5-12450H com 8 GB e Linux, priorizando CPU. O código define llama3.2:1b como padrão local, temperatura zero, duas threads, num_ctx 4096, num_predict 2048 e keep_alive zero. O modelo é descarregado depois da resposta. O timeout do transporte pode chegar a 300 segundos. Essa escolha reduz residência na memória, mas acrescenta custo de carregamento nas próximas chamadas.

Se P parâmetros usam b bits cada, P vezes b dividido por oito aproxima apenas os bytes dos pesos. Uma conta hipotética de um bilhão de parâmetros em quatro bits daria 0,5 GB de pesos, sem metadados, buffers, cache de atenção e demais processos. Isso é uma ilustração teórica, não medição do modelo instalado.

Um registro sintético de smoke test reporta cerca de 1,47 bilhão de bytes, em uma única execução; não é perfil completo de RSS. Outro registro documenta timeout de 300,11 segundos em uma explicação com qwen2.5:3b. A troca para Llama favoreceu a operação, mas a avaliação de cinco questões revelou erros.

Qwen2.5-Coder 1.5B é alternativa a comparar, não vencedor demonstrado. O candidato 3B deve passar primeiro por medição isolada de memória e desempenho. Banca: “O mínimo que roda é suficiente?” Somente se também satisfizer critérios de qualidade previamente definidos.

EVIDÊNCIAS LOCAIS: core/ollama_client.py; .runtime/llama-light-smoke.json; .runtime/qwen-evaluation.json

REFERÊNCIAS:
Ollama. Generate embeddings e biblioteca all-minilm. https://docs.ollama.com/api/embed e https://ollama.com/library/all-minilm. Consulta em 05/11/2026.
Qwen. Qwen2.5-Coder-1.5B-Instruct, model card oficial. https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct. Alternativa futura, sem resultado comparativo local neste trabalho.

## Slide 08 — RAG de materiais: indexação e contexto

O pipeline de materiais começa com importação e limpeza de documentos autorizados. O SQLite guarda o corpo comprimido e metadados de proveniência. A função chunks particiona o texto por limite aproximado de 1.800 caracteres, preferindo quebras de parágrafo, linha ou espaço. Não há sobreposição explícita. Um trecho pode separar uma definição de seu exemplo, razão para investigar chunking por seção e contexto adjacente.

O índice FTS5 pesquisa termos, com BM25 e complementos de ranqueamento. O método context exige fontes externas e conteúdo integral elegível, excluindo registros de simples referência. As aulas autorais continuam disponíveis para leitura, porém não fundamentam por padrão novas gerações como se fossem fonte externa.

O compositor limita o contexto: na geração de materiais, até 2.400 caracteres para Ollama e 6.500 para API. Inclui pedido, preferências e estatísticas resumidas. Salva a resposta com as fontes de fato recuperadas e links recomendados separados. A presença de fontes não assegura que cada afirmação seja sustentada por elas.

Lewis e colaboradores fundamentam a combinação entre memória paramétrica e não paramétrica. Aqui a combinação ocorre no prompt, sem atualização de pesos nem treinamento conjunto. Banca: “O banco treina a IA?” Ele disponibiliza textos para consultas posteriores; pesos permanecem fixos. Transição: distinguir os dois recuperadores reais.

EVIDÊNCIAS LOCAIS: core/knowledge.py:chunks,search,context; core/codigen_tutor.py:generate_material; core/progress_store.py

REFERÊNCIAS:
Lewis, P. et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS, 2020. https://arxiv.org/abs/2005.11401
SQLite. FTS5 Extension, seção bm25(). https://sqlite.org/fts5.html#the_bm25_function. Consulta em 05/11/2026.

## Slide 09 — Recuperação de problemas e de materiais

O produto interno soma o produto das coordenadas de dois vetores. Dividi-lo pelas normas produz o cosseno do ângulo entre eles. Vetores unitários permitem calcular a similaridade somente com produto matricial. No módulo de problemas, as coordenadas representam termos ponderados por frequência e raridade, não características aprendidas por uma rede neural.

Há espaços independentes para enunciado, conceitos mais essência matemática e resumo da estratégia. Cada espaço possui seu vocabulário. O código combina os três escores com os pesos exibidos, seleciona candidatos e solicita reranking e justificativas ao modelo. Esses pesos são escolhas de engenharia, sem otimização experimental documentada. A extração de essência e o reranker também podem falhar.

No acervo de estudos, BM25 satura a contribuição de termos repetidos e normaliza comprimento. A busca complementa o escore com equivalências de vocabulário, títulos e preferência por fundamentos. Essa arquitetura não usa FAISS. O experimento semântico separado compara vetores all-minilm por cosseno e fusão RRF de listas.

Problemas sobre intervalos podem exigir prefixos, Fenwick ou Segment Tree. Identificar palavras parecidas não demonstra a mesma competência nem a necessidade de determinada técnica. Banca: “Por que três espaços?” Para reduzir o domínio da narrativa, hipótese cuja vantagem ainda precisa de ablação local.

EVIDÊNCIAS LOCAIS: core/rag_retriever.py:retrieve; core/knowledge.py:search; scripts/evaluate_semantic.py

REFERÊNCIAS:
Su, Y.; Nie, P.; Meng, X. OI-Assistant: A Retrieval Augmented System for Similar Problem Discovery and Interactive Learning in Competitive Programming. Olympiads in Informatics, 19, 129–144, 2025. DOI:10.15388/ioi.2025.09. PDF local fornecido e https://ioi.te.lv/oi/files/volume19.pdf
Reimers, N.; Gurevych, I. Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. EMNLP-IJCNLP, 2019, 3982–3992. DOI:10.18653/v1/D19-1410. https://arxiv.org/abs/1908.10084
Robertson, S.; Zaragoza, H. The Probabilistic Relevance Framework: BM25 and Beyond. Foundations and Trends in Information Retrieval, 3(4), 333–389, 2009. DOI:10.1561/1500000019. https://www.nowpublishers.com/article/Details/INR-019
Cormack, G. V.; Clarke, C. L. A.; Büttcher, S. Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods. SIGIR, 2009, 758–759. DOI:10.1145/1571941.1572114. https://cormack.uwaterloo.ca/cormack/cormacksigir09-rrf.pdf
SQLite. FTS5 Extension, seção bm25(). https://sqlite.org/fts5.html#the_bm25_function. Consulta em 05/11/2026.

## Slide 10 — Cobertura real do acervo

A leitura somente de consulta ao banco confirmou 5.551 documentos e 6.837 trechos. Os documentos se decompõem em 302 artigos externos, 19 aulas ou guias autorais e 5.230 referências. O total inclui 4.001 referências de problemas, 1.202 referências gerais e 27 vídeos. Não é correto usar a contagem total como se todo o conteúdo tivesse sido lido ou importado.

Os textos externos completos são 164 artigos CP-Algorithms e 138 tutoriais USACO. O relatório registra atualização dos 138 para uma revisão fixada, com reimportação idempotente; isso atualizou a versão e não aumentou o número de artigos. O arquivo comprimido facilita transporte e o SQLite permite consulta, sem modificar pesos do gerador.

Os 39 contratos locais são distintos do catálogo externo de links de problemas. CSES e outros catálogos não fornecem, neste projeto, testes oficiais importados. A integração TLE recebeu HTTP 403 por origem não verificada. Os vídeos do canal UFMG permanecem referências, sem transcrição.

Banca: “O conteúdo de todos os sites está no RAG?” Não. O relatório identifica cobertura por fonte e separa links, textos e materiais autorais. Transição: explicar o que acontece quando o sistema gera um exercício.

EVIDÊNCIAS LOCAIS: data/knowledge.sqlite3, consulta somente leitura; data/study_sources_report.json; core/problem_bank.py:load_problems

REFERÊNCIAS:
Su, Y.; Nie, P.; Meng, X. OI-Assistant: A Retrieval Augmented System for Similar Problem Discovery and Interactive Learning in Competitive Programming. Olympiads in Informatics, 19, 129–144, 2025. DOI:10.15388/ioi.2025.09. PDF local fornecido e https://ioi.te.lv/oi/files/volume19.pdf
Lewis, P. et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS, 2020. https://arxiv.org/abs/2005.11401

## Slide 11 — Geração e verificação de um problema

A geração começa pelo pedido específico, preservado ao sair de uma página de estudo ou busca. O modelo escolhe entre 39 contratos descritos no prompt. Nesse caminho não há chamada a OIAssistantRAG nem recuperação BM25 de candidatos. Portanto, geração de problemas e RAG de materiais estão integrados na plataforma, mas não formam um único pipeline de geração fundamentada por recuperação.

O contrato determina objetivo, gramática e limites. A adaptação solicita enunciado, std_cpp e brute_cpp, preservando a semântica. Testes incluem casos pequenos enumerados, extremos e grandes. Nas sete sementes originais, std e brute são comparados nos pequenos; nas 32 tarefas acrescentadas, oráculos Python verificam as saídas. A adaptação também é comparada com a referência confiável do contrato.

Essas verificações detectam várias implementações erradas, mas não provam que o enunciado gerado descreve fielmente o algoritmo nem que todos os erros possíveis sejam encontrados. A função de comparação normaliza espaços finais, mantendo uma saída determinística única. Não há checker semântico para respostas múltiplas ou problemas interativos.

Banca: “O problema é inédito?” A implementação produz variações verificáveis de contratos, sem medida de originalidade estrutural. A Arena identifica revisão quando reutiliza contrato recente. Transição: localizar os módulos na arquitetura efetiva.

EVIDÊNCIAS LOCAIS: core/autocode_engine.py:generate_problem,adapt_seed,double_validate; core/problem_bank.py; core/classic_judge.py; core/extended_judge.py

REFERÊNCIAS:
Zhou, S. et al. AutoCode: LLMs as Problem Setters for Competitive Programming. ICLR 2026. Preprint de 2025, arXiv:2510.12803. https://proceedings.iclr.cc/paper_files/paper/2026/hash/1bd78da0966968409e65b5e0b5dbb57e-Abstract-Conference.html

## Slide 12 — Arquitetura realmente implementada

A arquitetura usa Streamlit como aplicação e orquestrador. A camada de inferência encaminha pedidos para Ollama local ou Gemini, OpenAI, DeepSeek e Qwen por API. Configurar uma chave não mantém uma conexão permanente: o status representa a última observação. O adaptador distingue falhas de transporte, cota, credencial, saldo e conteúdo recusado.

Existem dois caminhos de conhecimento: os três espaços TF-IDF para recomendação de problemas e o acervo FTS5/BM25 para materiais. A geração seleciona diretamente os contratos. O mini-juiz compila em C++17 e executa com timeout e limites POSIX de CPU, memória e saída. Esses limites não isolam arquivos ou rede como um sandbox completo.

O SQLite público guarda textos comprimidos e proveniência. Outro SQLite guarda contas, sessões, artefatos e progresso privado por perfil. As consultas observadas aplicam vínculo ao proprietário e os testes exercitam privacidade entre perfis. A auditoria não extraiu dados pessoais, senhas ou chaves do banco de progresso.

Cadastros, turmas e propostas de trios existem. A aplicação chama propose_teams, baseado em LLM, e não o otimizador heurístico legado de team_builder. IDs válidos e ausência de repetição garantem integridade da formação, mas não optimalidade esportiva. Banca: “É pronto para internet?” O protótipo requer isolamento de execução e operação específicos antes disso.

EVIDÊNCIAS LOCAIS: app.py; core/llm_client.py; core/mini_judge.py; core/runner.py; core/progress_store.py; core/school_views.py; core/ai_coach.py

REFERÊNCIAS:
SQLite. FTS5 Extension, seção bm25(). https://sqlite.org/fts5.html#the_bm25_function. Consulta em 05/11/2026.
Ollama. Generate embeddings e biblioteca all-minilm. https://docs.ollama.com/api/embed e https://ollama.com/library/all-minilm. Consulta em 05/11/2026.

## Slide 13 — Fundamentos pedagógicos e evidências

O tutor usa exemplos few-shot e orientações socráticas para evitar programas completos depois de uma falha. O filtro rejeita algumas estruturas de código, mas não verifica toda revelação conceitual da solução. Essa é uma estratégia de projeto para feedback formativo, ainda sem avaliação da utilidade do feedback por alunos e especialistas.

Scaffolding envolve ajuda ajustada ao desempenho e retirada progressiva. Oferecer dicas constitui uma aproximação parcial, porque não há política validada de fading. A taxonomia revisada de Bloom distingue lembrar, compreender, aplicar, analisar, avaliar e criar; esses níveis são dimensões cognitivas, não faixas de dificuldade do juiz. Não há anotação ou avaliador Bloom implementado.

A Zona de Desenvolvimento Proximal trata da diferença entre desempenho independente e com ajuda. Estatísticas de acertos não a medem diretamente. Mastery learning organiza objetivos, avaliações formativas, correção e nova oportunidade para demonstrar domínio; um AC isolado ou leitura concluída não satisfaz esse ciclo.

A aprendizagem baseada em problemas pode orientar atividades contextualizadas, mas resolver exercícios de programação não basta para afirmar uma metodologia pedagógica completa. Banca: “Qual teoria o sistema implementa?” Distinguir mecanismos observáveis e interpretações teóricas. Transição: reconstruir a evolução documentada sem inventar histórico de commits.

EVIDÊNCIAS LOCAIS: core/codigen_tutor.py:GUARDRAILS,safe_hint; core/ai_coach.py:analyze_learner; data/learning_content.json

REFERÊNCIAS:
Ez-zaouia, M.; Boumarafi, Y. Codigen: Enhancing Personalized Programming Education with Visual Authoring and LLMs. IEEE VL/HCC, 2025. DOI:10.1109/VL-HCC65237.2025.00038. https://conf.researchr.org/details/vlhcc-2025/vlhcc-2025-research-papers/29/Codigen-Enhancing-Personalized-Programming-Education-with-Visual-Authoring-and-Large
Anderson, L. W.; Krathwohl, D. R. (org.). A Taxonomy for Learning, Teaching, and Assessing: A Revision of Bloom’s Taxonomy of Educational Objectives. Longman, 2001. Registro bibliográfico: https://www.loc.gov/item/00063423/
Vygotsky, L. S. Mind in Society: The Development of Higher Psychological Processes. Harvard University Press, 1978. DOI:10.2307/j.ctvjf9vz4. https://doi.org/10.2307/j.ctvjf9vz4
Wood, D.; Bruner, J. S.; Ross, G. The Role of Tutoring in Problem Solving. Journal of Child Psychology and Psychiatry, 17(2), 89–100, 1976. DOI:10.1111/j.1469-7610.1976.tb00381.x. https://acamh.onlinelibrary.wiley.com/doi/10.1111/j.1469-7610.1976.tb00381.x
Bloom, B. S. Learning for Mastery. Evaluation Comment, 1(2), 1968. ERIC ED053419. https://eric.ed.gov/?id=ED053419
Black, P.; Wiliam, D. Assessment and Classroom Learning. Assessment in Education: Principles, Policy & Practice, 5(1), 7–74, 1998. DOI:10.1080/0969595980050102.

## Slide 14 — Evolução documentada do projeto

A cronologia usa documentos locais, pedidos preservados e relatórios com nomes e datas. O plano e a apresentação inicial registram a extensão: usar erros do mini-juiz como contexto para feedback e prática. Os arquivos da disciplina situam a proposta em setembro e os resultados em novembro. Carimbos de modificação não substituem um histórico de autoria e não provam a data de cada decisão.

O histórico da conversa registra expansão da interface e pedidos de banco local, conteúdos, APIs, turmas e trilhas. Registros de novembro preservam troca do modelo 3B para Llama 1B, timeout, avaliações, revisão das fontes e ampliação dos contratos. A auditoria leu essas evidências sem reconstituir commits inexistentes.

O diretório e seus pais consultados não contêm um repositório Git utilizável. Não se conhecem autores por commit, branches ou diffs históricos. Backups existem, mas não constituem uma sequência completa de versões; não se inferiu causalidade somente pela data dos arquivos.

O principal aprendizado é que a expansão funcional não acompanha automaticamente a maturidade científica. Mais telas e mais conteúdos precisam vir com medidas de correção, fundamentação e adequação pedagógica. Banca: “Quando cada bug foi corrigido?” Responder apenas quando há registro verificável, evitando datas inventadas. Transição: apresentar os protocolos efetivamente executados.

EVIDÊNCIAS LOCAIS: ../Plano de Trabalho - IA e Programação Competitiva.pdf; docs/PLANO_EVOLUCAO.md; .runtime/*evaluation.json; Git indisponível

REFERÊNCIAS:


## Slide 15 — Três níveis de avaliação

O primeiro nível verifica o software: compilação, vereditos, rejeição de referência incorreta, limites, contratos de dados, persistência, perfis, trilhas e navegação. Os testes de IA usam transporte controlado em muitas integrações. Eles confirmam como o programa reage a respostas conhecidas, não a qualidade espontânea do modelo.

O segundo nível usa 12 consultas, seis nomes explícitos e seis paráfrases, em 302 textos externos. O sucesso ocorre quando um padrão de título esperado aparece nos três primeiros resultados. Portanto, é um indicador de recuperação tópica, não anotação de relevância de todos os trechos nem Recall@3 de um conjunto completo de documentos relevantes.

O terceiro nível usa cinco perguntas numéricas com respostas conhecidas, uma de cada tema. Temperatura zero, contexto 2.048 e saída máxima 256 diferem da configuração geral da aplicação. O script confere igualdade do campo result com o gabarito e registra outros campos. A variável numeric_correct mistura valor correto e aderência ao formato: a ausência de result conta como falha.

Os três níveis respondem a perguntas diferentes. Nenhum inclui participantes locais, teste de retenção ou medida de transferência. Banca: “Por que 12 e cinco?” São amostras exploratórias disponíveis, insuficientes para uma estimativa geral.

EVIDÊNCIAS LOCAIS: tests/; scripts/evaluate_semantic.py; scripts/evaluate_learning_quality.py; docs/artigo_sbc/evidencias/

REFERÊNCIAS:


## Slide 16 — Resultados positivos verificáveis

Os números de contratos e corpus foram recalculados a partir do código e do banco público. O conjunto contém cinco contratos de Segment Tree, seis de grafos e nove de DP. Essa cobertura permite diferentes objetivos nesses temas, sem demonstrar que qualquer modelo fará sempre a seleção correta. A referência C++ passa por oráculos, casos pequenos e entradas grandes.

Os testes executados nesta auditoria exercitam a suíte atual em bancos temporários e respostas simuladas para os provedores. O log e o inventário acompanham a entrega. A aprovação significa conformidade aos cenários existentes; não é taxa de acerto de uma IA. A atualização de 138 tutoriais possui relatório de segunda importação com 138 registros inalterados, evidenciando idempotência.

O fluxo direto da página de estudo ou busca leva o pedido até a geração e salva a origem. Quando um contrato reaparece, a interface pode marcá-lo como revisão. Isso corrige perda de contexto entre telas, mas não assegura novidade algorítmica.

Banca: “207 é uma métrica científica?” É evidência de engenharia e reprodutibilidade, não medida pedagógica ou comparação com AutoCode. Os testes têm escopo finito e alguns módulos legados possuem casos não cobertos. Transição: olhar para resultados de recuperação, onde há acertos e perdas.

EVIDÊNCIAS LOCAIS: core/problem_bank.py; tests/test_next_stages.py; tests/test_ui.py; .build/testes_auditoria.log; .runtime/licensed-update-report.json

REFERÊNCIAS:


## Slide 17 — Recuperação: resultado exploratório

O gráfico usa exclusivamente o arquivo semantic-comparison.json: seis acertos lexicais, quatro semânticos e sete com fusão, sobre 12 consultas. A busca lexical combina BM25 e ajustes existentes. A semântica utiliza all-minilm:22m, com títulos e os primeiros 1.200 caracteres de cada documento. As duas listas top-10 entram em Reciprocal Rank Fusion, implementada com denominador 60 mais posição iniciada em zero.

A matriz contém 302 vetores de 384 números float32, ocupando 463.872 bytes. Esse valor é o tamanho dos vetores, não a RAM total do processo. O registro reporta 21,28 segundos para o experimento incluindo construção e consulta. Não é latência por consulta nem medida repetida com intervalo de confiança.

O resultado de sete contra seis representa apenas uma consulta adicional. Não houve teste independente grande, julgamento cego de relevância nem ajuste controlado de todos os parâmetros. O índice denso não representa o documento inteiro nem os mesmos trechos da busca lexical. Língua, truncamento e modelo são fatores de confusão, não causas demonstradas.

Banca: “Por que não ativar o híbrido?” A decisão preserva simplicidade até haver evidência de ganho e custo aceitável. Transição: mostrar que recuperar um tópico também não garante uma resposta correta.

EVIDÊNCIAS LOCAIS: scripts/evaluate_semantic.py; .runtime/semantic-comparison.json

REFERÊNCIAS:
Reimers, N.; Gurevych, I. Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. EMNLP-IJCNLP, 2019, 3982–3992. DOI:10.18653/v1/D19-1410. https://arxiv.org/abs/1908.10084
Cormack, G. V.; Clarke, C. L. A.; Büttcher, S. Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods. SIGIR, 2009, 758–759. DOI:10.1145/1571941.1572114. https://cormack.uwaterloo.ca/cormack/cormacksigir09-rrf.pdf
Ollama. Generate embeddings e biblioteca all-minilm. https://docs.ollama.com/api/embed e https://ollama.com/library/all-minilm. Consulta em 05/11/2026.

## Slide 18 — Modelo local: cinco respostas problemáticas

O relatório learning-quality.json contém as respostas brutas das cinco questões sintéticas. A avaliação exigiu JSON com result, reason e source_labels. O script marcou como falha a ausência do campo result, valor errado ou JSON inválido. Não se pode interpretar 0/5 como ausência absoluta de qualquer conta correta: a resposta de prefixos contém o número esperado em outra chave, mas justifica uma operação errada.

As falhas ultrapassam formato. A resposta de DFS informa um vértice alcançável em uma cadeia com quatro. No caso de Segment Tree, a lista [2,4,1] recebe atribuição da posição dois para sete, e a soma [2,3] é oito; a resposta apresenta cinco, enquanto sua justificativa cita seis. Isso evidencia inconsistência interna em uma tarefa simples.

A saída máxima de 256 tokens e o contexto de 2.048 limitam a generalização para materiais longos e podem influenciar truncamento. Um teste não compara modelos nem separa todos os fatores. A fonte recuperada não forçou o uso correto da definição e o JSON não garantiu semântica.

Banca: “É adequado como tutor?” Os registros sustentam uso experimental supervisionado, sem recomendá-lo como tutor autônomo confiável. A próxima comparação precisa manter contexto, orçamento e perguntas iguais.

EVIDÊNCIAS LOCAIS: scripts/evaluate_learning_quality.py; .runtime/learning-quality.json

REFERÊNCIAS:


## Slide 19 — Falhas confirmadas e causas prováveis

A cadeia causal deve começar pela evidência. O timeout de 300,11 segundos consta no registro qwen2.5:3b; o relato de travamento do usuário reforça o problema operacional. Porém, sem perfis simultâneos de CPU, RSS e swap, não se pode atribuí-lo exclusivamente à quantidade de parâmetros. A ação adequada é medir e comparar sob carga controlada.

A lacuna de Segment Tree possui causa demonstrável: learning_stats percorre nove tópicos do currículo e agrupa por igualdade de título; Segment Tree não aparece entre eles. Uma consulta sintética com AC nesse assunto não produz uma linha correspondente. Isso afeta o resumo numérico enviado à personalização, embora o veredito continue no histórico. A auditoria não alterou o código.

O relatório de importação registra HTTP 403 no catálogo TLE. O conteúdo integral não foi importado e não se contornou o bloqueio. Quanto à diversidade, preservar o objetivo é uma propriedade explícita do prompt de adaptação. A variação é real no texto e nos testes, mas originalidade estrutural continua aberta.

Erros de API 400, 402, 429 e 503 aparecem no histórico fornecido pelo usuário; a implementação possui tratamento e testes, mas a auditoria não reproduziu esses eventos em serviços pagos. Transição: avaliar o alcance científico dessas evidências.

EVIDÊNCIAS LOCAIS: .runtime/qwen-evaluation.json; core/learning_engine.py:learning_stats; data/learning_content.json; data/study_sources_report.json; core/autocode_engine.py

REFERÊNCIAS:


## Slide 20 — Contribuição e maturidade científica

A principal contribuição atual é de engenharia de software e adaptação metodológica. O sistema conecta entradas pedagógicas, geração, recuperação, execução de programas, armazenamento e consulta. Contratos com oráculos e registros de proveniência tornam parte do comportamento verificável, mas não configuram um novo modelo fundacional ou algoritmo de recuperação.

Há uma contribuição experimental preliminar: a comparação de três recuperadores e a observação de erros do modelo leve. O tamanho das amostras e os critérios limitam seu alcance. Ainda não há ensaio educacional, anotação independente de problemas gerados ou comparação com submissões oficiais em larga escala.

A hipótese inicial de tutoria dirigida por fraquezas permanece plausível, porém não confirmada. Os dados de erros alimentam prompts, mas mapear observações para conhecimento do aluno exige validar inferências. Uma diferença do AutoCode é preservar contratos conhecidos; do OI-Assistant, usar busca lexical multiespaço e materiais externos; do Codigen, integrar um juiz C++ e contexto de prática.

Banca: “Isso é apenas integração?” A integração é o resultado sustentado agora. Pode originar contribuição científica ao isolar uma pergunta, controlar fatores e demonstrar efeito replicável com métricas apropriadas. Transição: apresentar quatro direções de pesquisa delimitadas.

EVIDÊNCIAS LOCAIS: docs/PLANO_EVOLUCAO.md; scripts/evaluate_semantic.py; scripts/evaluate_learning_quality.py; core/autocode_engine.py

REFERÊNCIAS:
Zhou, S. et al. AutoCode: LLMs as Problem Setters for Competitive Programming. ICLR 2026. Preprint de 2025, arXiv:2510.12803. https://proceedings.iclr.cc/paper_files/paper/2026/hash/1bd78da0966968409e65b5e0b5dbb57e-Abstract-Conference.html
Su, Y.; Nie, P.; Meng, X. OI-Assistant: A Retrieval Augmented System for Similar Problem Discovery and Interactive Learning in Competitive Programming. Olympiads in Informatics, 19, 129–144, 2025. DOI:10.15388/ioi.2025.09. PDF local fornecido e https://ioi.te.lv/oi/files/volume19.pdf
Ez-zaouia, M.; Boumarafi, Y. Codigen: Enhancing Personalized Programming Education with Visual Authoring and LLMs. IEEE VL/HCC, 2025. DOI:10.1109/VL-HCC65237.2025.00038. https://conf.researchr.org/details/vlhcc-2025/vlhcc-2025-research-papers/29/Codigen-Enhancing-Personalized-Programming-Education-with-Visual-Authoring-and-Large

PERGUNTA DO USUÁRIO: Por que não alcançamos os 99% se já foi feito? Não há medida local comparável de concordância. O protótipo simplificou o pipeline e usa modelo menor, sem reproduzir as rodadas e a seleção de verificadores. O 0/5 de perguntas não é a mesma métrica. É preciso reproduzir o protocolo em submissões com vereditos oficiais e fazer ablações. Essa reprodução é prioridade científica anterior à comparação de percentuais.

## Slide 21 — Quatro direções de pesquisa

A primeira direção representa conceitos, operações e pré-requisitos de forma estruturada. A hipótese é que filtrar e recuperar por essas relações melhora alinhamento sem perder problemas relevantes. O currículo já contém IDs e pré-requisitos, mas isso não constitui uma ontologia nem um grafo de conhecimento operacional para recuperação.

A segunda condiciona a geração a um objetivo cognitivo observável, como justificar um invariante ou aplicar atualização em intervalo. Rubricas independentes precisam distinguir dificuldade, conteúdo e processo cognitivo. Preferir estudar por problemas pode orientar formato, sem assumir que um “estilo de aprendizagem” fixo determine eficácia.

A terceira usa mutações plausíveis de soluções para medir a força dos testes. AC local pode falhar diante de um erro que nunca foi provocado. É preciso medir falsos positivos e negativos em conjuntos de referência e preservar a validade dos casos gerados.

A quarta trata da originalidade. Representar operações, estados e dependências permite comparar estruturas além do texto. Avaliação humana continua necessária para identificar equivalência algorítmica. Nenhuma dessas hipóteses já foi confirmada pelo protótipo.

Banca: “Qual caminho começar?” Competências e validação têm pré-condições concretas e podem produzir um benchmark pequeno e reutilizável. Transição: propor uma comparação controlada que una essas direções.

EVIDÊNCIAS LOCAIS: Proposta desta auditoria; data/learning_content.json como base parcial; roadmap_pesquisa.md

REFERÊNCIAS:
Zhou, S. et al. AutoCode: LLMs as Problem Setters for Competitive Programming. ICLR 2026. Preprint de 2025, arXiv:2510.12803. https://proceedings.iclr.cc/paper_files/paper/2026/hash/1bd78da0966968409e65b5e0b5dbb57e-Abstract-Conference.html
Su, Y.; Nie, P.; Meng, X. OI-Assistant: A Retrieval Augmented System for Similar Problem Discovery and Interactive Learning in Competitive Programming. Olympiads in Informatics, 19, 129–144, 2025. DOI:10.15388/ioi.2025.09. PDF local fornecido e https://ioi.te.lv/oi/files/volume19.pdf
Anderson, L. W.; Krathwohl, D. R. (org.). A Taxonomy for Learning, Teaching, and Assessing: A Revision of Bloom’s Taxonomy of Educational Objectives. Longman, 2001. Registro bibliográfico: https://www.loc.gov/item/00063423/

## Slide 22 — Próximo experimento controlado

O desenho compara quatro condições propostas, ainda sem resultados. A usa apenas o pedido; B fornece recuperação semântica; C fornece recursos selecionados por competência e pré-requisitos; D acrescenta validação automática ao caminho C. Todas as saídas devem passar pela mesma avaliação externa, inclusive rejeições e tentativas, para evitar comparar somente sobreviventes da condição D.

Fixar modelo, quantização, temperatura, orçamento de tokens, pedidos e infraestrutura. Separar desenvolvimento e teste por famílias algorítmicas para reduzir vazamento de variantes semelhantes. Registrar múltiplas gerações por pedido, erros, tempo até sucesso e custo total. Especialistas devem avaliar enunciados sem conhecer a condição.

As métricas incluem problemas válidos por tentativa, correção da referência, cobertura das competências previstas, diversidade estrutural, alinhamento pedagógico, latência e pico de memória. Para comparar recuperação, usar julgamentos independentes e Recall@k, MRR ou nDCG. Para efeito educacional, será necessário outro estudo com pré-teste, pós-teste, transferência e procedimentos éticos adequados.

Na máquina de 8 GB, rodar um modelo por vez e construir embeddings antes da geração. FAISS só se justifica após medir vantagem frente ao NumPy exato no tamanho atual. Banca: “Quantos casos?” A quantidade deve vir de piloto e análise de precisão ou poder, não de um número inventado.

EVIDÊNCIAS LOCAIS: Proposta experimental desta auditoria; roadmap_pesquisa.md

REFERÊNCIAS:
Lewis, P. et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS, 2020. https://arxiv.org/abs/2005.11401
Reimers, N.; Gurevych, I. Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. EMNLP-IJCNLP, 2019, 3982–3992. DOI:10.18653/v1/D19-1410. https://arxiv.org/abs/1908.10084
Anderson, L. W.; Krathwohl, D. R. (org.). A Taxonomy for Learning, Teaching, and Assessing: A Revision of Bloom’s Taxonomy of Educational Objectives. Longman, 2001. Registro bibliográfico: https://www.loc.gov/item/00063423/

## Slide 23 — Conclusões e prioridades

A conclusão retorna à proposta original: usar avaliação local para alimentar tutoria e prática. O projeto construiu essa infraestrutura e ampliou a experiência de estudo. Há geração condicionada a contexto, recomendações, persistência, contratos verificáveis e registros de falhas. Essa é uma base concreta para investigação, mas os resultados de implementação não comprovam a hipótese pedagógica.

As evidências mais fortes são a execução dos testes, a integridade dos contratos e a rastreabilidade do acervo. As limitações mais instrutivas são os erros do modelo leve, a pequena avaliação de recuperação, a falta de taxonomia uniforme para Segment Tree e a diferença entre variar o texto e criar uma nova estrutura algorítmica.

A prioridade de engenharia é alinhar representação dos assuntos, eliminar caminhos legados confusos, medir desempenho e preparar isolamento apropriado se houver implantação pública. A prioridade científica é criar um conjunto independente, comparar condições de geração e avaliar com rubricas cegas. Só depois uma pesquisa com estudantes poderá investigar aprendizagem, retenção e transferência.

Banca: “Se o modelo falhou, o trabalho fracassou?” Não. O resultado negativo local é evidência útil e delimita decisões, desde que apresentado com método, registros e limites. Encerrar reconhecendo que confiabilidade resulta da composição de mecanismos avaliados, não da fluência de uma resposta.

EVIDÊNCIAS LOCAIS: Inventário, testes e relatórios listados em auditoria_projeto.md

REFERÊNCIAS:
Zhou, S. et al. AutoCode: LLMs as Problem Setters for Competitive Programming. ICLR 2026. Preprint de 2025, arXiv:2510.12803. https://proceedings.iclr.cc/paper_files/paper/2026/hash/1bd78da0966968409e65b5e0b5dbb57e-Abstract-Conference.html
Su, Y.; Nie, P.; Meng, X. OI-Assistant: A Retrieval Augmented System for Similar Problem Discovery and Interactive Learning in Competitive Programming. Olympiads in Informatics, 19, 129–144, 2025. DOI:10.15388/ioi.2025.09. PDF local fornecido e https://ioi.te.lv/oi/files/volume19.pdf
Ez-zaouia, M.; Boumarafi, Y. Codigen: Enhancing Personalized Programming Education with Visual Authoring and LLMs. IEEE VL/HCC, 2025. DOI:10.1109/VL-HCC65237.2025.00038. https://conf.researchr.org/details/vlhcc-2025/vlhcc-2025-research-papers/29/Codigen-Enhancing-Personalized-Programming-Education-with-Visual-Authoring-and-Large

## Slide 24 — Referências principais

As referências da tela identificam os trabalhos técnicos centrais. Os documentos complementares contêm a bibliografia ampliada, a comparação dos artigos e os fundamentos pedagógicos. Para AutoCode, citar a versão publicada ICLR 2026 e mencionar o preprint de 2025 quando reconstruir a proposta histórica. Para Codigen, a edição IEEE usa “LLMs” e a página do evento expande “Large Language Models”; ambos apontam para o mesmo DOI e os mesmos autores.

Os percentuais de AutoCode pertencem às tabelas e condições daquele artigo. Os resultados de OI-Assistant pertencem a consultas e usuários daquele estudo. Os dados de Codigen derivam de sua atividade em JavaScript, sem grupo de controle equivalente ao nosso sistema. Manter essas distinções ao responder à banca.

A consulta externa confirmou identidades bibliográficas; os PDFs científicos fornecidos permitiram examinar métodos e resultados. Algumas páginas de editoras não responderam à consulta automática, o que está registrado no relatório. A evidência local permanece nos arquivos e relatórios indicados, sem exportação de dados privados de alunos.

Banca: preparar as respostas sobre a diferença entre recuperação e treinamento, correção finita e prova, relevância e equivalência, bem como observação e causalidade. Se uma informação não está documentada, reconhecer essa lacuna em vez de estimar um resultado.

EVIDÊNCIAS LOCAIS: PDFs científicos locais e referências verificáveis listadas nas notas

REFERÊNCIAS:
Zhou, S. et al. AutoCode: LLMs as Problem Setters for Competitive Programming. ICLR 2026. Preprint de 2025, arXiv:2510.12803. https://proceedings.iclr.cc/paper_files/paper/2026/hash/1bd78da0966968409e65b5e0b5dbb57e-Abstract-Conference.html
Su, Y.; Nie, P.; Meng, X. OI-Assistant: A Retrieval Augmented System for Similar Problem Discovery and Interactive Learning in Competitive Programming. Olympiads in Informatics, 19, 129–144, 2025. DOI:10.15388/ioi.2025.09. PDF local fornecido e https://ioi.te.lv/oi/files/volume19.pdf
Ez-zaouia, M.; Boumarafi, Y. Codigen: Enhancing Personalized Programming Education with Visual Authoring and LLMs. IEEE VL/HCC, 2025. DOI:10.1109/VL-HCC65237.2025.00038. https://conf.researchr.org/details/vlhcc-2025/vlhcc-2025-research-papers/29/Codigen-Enhancing-Personalized-Programming-Education-with-Visual-Authoring-and-Large
Vaswani, A. et al. Attention Is All You Need. NeurIPS, 2017. https://arxiv.org/abs/1706.03762
Lewis, P. et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS, 2020. https://arxiv.org/abs/2005.11401
Reimers, N.; Gurevych, I. Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. EMNLP-IJCNLP, 2019, 3982–3992. DOI:10.18653/v1/D19-1410. https://arxiv.org/abs/1908.10084
Robertson, S.; Zaragoza, H. The Probabilistic Relevance Framework: BM25 and Beyond. Foundations and Trends in Information Retrieval, 3(4), 333–389, 2009. DOI:10.1561/1500000019. https://www.nowpublishers.com/article/Details/INR-019
Cormack, G. V.; Clarke, C. L. A.; Büttcher, S. Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods. SIGIR, 2009, 758–759. DOI:10.1145/1571941.1572114. https://cormack.uwaterloo.ca/cormack/cormacksigir09-rrf.pdf
Anderson, L. W.; Krathwohl, D. R. (org.). A Taxonomy for Learning, Teaching, and Assessing: A Revision of Bloom’s Taxonomy of Educational Objectives. Longman, 2001. Registro bibliográfico: https://www.loc.gov/item/00063423/
Vygotsky, L. S. Mind in Society: The Development of Higher Psychological Processes. Harvard University Press, 1978. DOI:10.2307/j.ctvjf9vz4. https://doi.org/10.2307/j.ctvjf9vz4
Wood, D.; Bruner, J. S.; Ross, G. The Role of Tutoring in Problem Solving. Journal of Child Psychology and Psychiatry, 17(2), 89–100, 1976. DOI:10.1111/j.1469-7610.1976.tb00381.x. https://acamh.onlinelibrary.wiley.com/doi/10.1111/j.1469-7610.1976.tb00381.x
Bloom, B. S. Learning for Mastery. Evaluation Comment, 1(2), 1968. ERIC ED053419. https://eric.ed.gov/?id=ED053419
Black, P.; Wiliam, D. Assessment and Classroom Learning. Assessment in Education: Principles, Policy & Practice, 5(1), 7–74, 1998. DOI:10.1080/0969595980050102.
SQLite. FTS5 Extension, seção bm25(). https://sqlite.org/fts5.html#the_bm25_function. Consulta em 05/11/2026.
Ollama. Generate embeddings e biblioteca all-minilm. https://docs.ollama.com/api/embed e https://ollama.com/library/all-minilm. Consulta em 05/11/2026.
Qwen. Qwen2.5-Coder-1.5B-Instruct, model card oficial. https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct. Alternativa futura, sem resultado comparativo local neste trabalho.

## Pergunta da banca: por que não alcançamos os 99%?

Ainda não executamos uma reprodução equivalente. Os 98,7% do AutoCode representam concordância com vereditos oficiais em um conjunto de 720 problemas. Nosso 0/5 é outro experimento, com perguntas numéricas e saída JSON. Não existe percentual local comparável. Além disso, usamos contratos fixos e modelo menor, sem o pipeline completo de múltiplas rodadas e seleção de verificadores. A resposta científica é reproduzir o protocolo em dados comuns e medir, com controle de modelo e recursos. Não é correto atribuir os 99% ao protótipo nem afirmar uma queda quantitativa ainda não medida.
