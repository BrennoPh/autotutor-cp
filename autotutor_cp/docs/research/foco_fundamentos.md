# Reposicionamento do AutoTutor nos fundamentos

Revisão de 5/11/2026. Público: iniciantes em programação competitiva, com noções iniciais de uma linguagem. Pergunta: como RAG e validação ajudam a produzir explicações e exercícios básicos confiáveis sob restrições de hardware e cota gratuita?

## Escopo

Fundamentos e simulação Ad Hoc; vetores e contagem; ordenação; prefixos; busca binária; guloso introdutório; BFS; DFS; DP elementar. Avançar significa aprofundar exemplos e raciocínio nesses temas antes de acrescentar estruturas avançadas. SegTree, lazy propagation e Block-Cut Tree ficam fora da avaliação principal e continuam como extensões opcionais. O mapa de nove objetivos para contratos está em `data/research/basic_curriculum.json`. Matemática básica, strings e árvores simples podem compor expansão curricular posterior, sem supor que já há contrato específico para todo subtópico.

## Mapeamento do que já existe

- Plataforma funcional: login, turmas, área do professor, persistência SQLite, biblioteca, páginas de estudos, trilhas, problemas e juiz. A formação de trios e análises por IA exigem validação de suas justificativas.
- Corpus: 302 textos externos integrais, 19 materiais autorais e 5230 referências. Um link não é texto integral. A biblioteca é maior que a cobertura efetiva de RAG.
- Geração: 39 contratos locais. Nove objetivos básicos agora têm associação explícita no experimento. O modelo cria variações sob contratos, sem certificação de novidade algorítmica.
- RAG em materiais e caminho experimental: BM25, busca densa local, RRF, re-ranking lexical, diversificação e expansão por competências. Os caminhos legados não foram todos substituídos por essa arquitetura experimental.
- Verificação: schema, compilação, exemplos, testes diferenciais e referência confiável. O juiz da aplicação restringe filesystem e rede, além de recursos. Sem sandbox, bloqueia execução.
- IA do estudante: resumos de evidências no produto e BKT experimental com perfis sintéticos. O grafo agora tem 18 competências. Parâmetros e limiares não foram calibrados.
- Provedor: Gemini 3.1 Flash-Lite no painel de pesquisa e Llama 3.2 1B como opção local. Outros provedores legados permanecem disponíveis em suas configurações, sem uso nesta revisão.

## Relação com os artigos

AutoCode inspira gerar, confrontar soluções e corrigir. A adaptação local usa contratos e oráculos conhecidos; não reproduz o benchmark de vereditos oficiais, os modelos nem a avaliação de originalidade. OI-Assistant inspira busca de problemas semelhantes e aprendizagem interativa; separar narrativa, conceito e estratégia ajuda a evitar recomendações apenas superficiais. Codigen é referência adicional para autoria e personalização; a interface visual do artigo não foi reproduzida.

A contribuição acadêmica mais consistente é um estudo de integração e avaliação de IA para fundamentos, com mecanismo verificável e custo autorizado zero. Não é necessário inventar uma arquitetura de rede nem atribuir ao projeto resultados dos artigos.

## Melhorias com a API em ordem de utilidade

1. Curar referências introdutórias por objetivo e exercício, com licença, trecho e nível revisados. Filtrar pré-requisitos avançados irrelevantes, medir recuperação com julgamentos humanos e manter BM25 como baseline econômico.
2. Pedir explicação com intuição, exemplo pequeno verificável, invariante ou transição, complexidade e erro comum. Produzir dicas em etapas. Salvar a versão com proveniência e permitir revisão pelo professor.
3. Calcular estatísticas e respostas esperadas por software, usando a IA para interpretar evidências. Rejeitar justificativas que inventem números ou atribuam domínio a um único erro. Isso preserva análise por IA sem delegar aritmética verificável ao gerador.
4. Gerar variações básicas com schema e contrato, validar antes de publicar. Uma passagem nos testes não certifica clareza, dificuldade ou que o algoritmo-alvo é necessário.
5. Acrescentar cache local por objetivo, nível, versão do corpus/prompt e preferências somente após política de revisão. O sistema já persiste materiais, mas cache automático de respostas por chave ainda é proposta.
6. Personalizar a partir de evidências graduais revisadas. BKT ainda é protótipo probabilístico com dados sintéticos. IRT, DKT e GraphRAG completo não têm necessidade demonstrada nesta fase.

## Limitações locais efetivamente observadas

As quatro tarefas básicas antigas com Llama 1B não passaram no verificador original. BFS e DFS apresentaram respostas incompatíveis, DP truncou com limite de 256 tokens, e prefixos mostrou valor coincidente com explicação/schema inconsistentes. Não resumir como “0% de capacidade de resolver o básico”. Qwen2.5 3B apresentou timeout acima de 300 segundos em material e justificativas estatísticas falsas em outros testes sintéticos. Não houve comparação pareada controlada entre famílias ou entre local/API.

O modelo 1B respondeu a um teste simples de conexão com tamanho de modelo reportado de cerca de 1,37 GiB; não é medida de RAM total. Os tempos registrados não isolam carga concorrente. O artigo deve reconhecer limite de tokens, schema, prompt, idioma e hardware como possíveis fatores, sem atribuir todo erro ao tamanho do modelo.

## Até onde a gratuidade permite ir

A tabela oficial consultada lista entrada e saída gratuitas do Gemini 3.1 Flash-Lite no free tier. Os limites reais são por projeto e devem ser consultados no AI Studio; não há um número universal de alunos/dia garantido. O teto de seis chamadas por dia UTC e 150000 tokens reservados pertence ao nosso adaptador, não ao Google. Não foi consultado faturamento privado. O usuário informou cota gratuita; nenhuma rotina habilita cobrança ou alternativa paga.

Com geração sob demanda, biblioteca persistente e recuperação local, é viável planejar demonstrações e experimentos pequenos. Para uma turma, o consumo cresce com alunos, gerações e correções, portanto não há promessa de disponibilidade contínua. Ferramentas adicionais e cache gerenciado não são necessários e não são habilitados. Dados públicos e sintéticos permanecem adequados a esta etapa; não enviar dados pessoais aos serviços gratuitos.

Planejamento: quatro temas × três condições = 12 chamadas para checar o protocolo, pelo menos dois dias se houver seis chamadas livres/dia. Com três repetições por célula, 36 chamadas e pelo menos seis dias nessas mesmas condições. São cenários, sem consumo novo nesta revisão. O resultado avançado anterior só comprova que o adaptador e a validação funcionaram naquele contrato.

## Artigo e defesa

Título recomendado: “Inteligência Artificial no Ensino dos Fundamentos de Programação Competitiva: Recuperação, Validação e Limitações sob Orçamento Zero de API”. Organizar introdução com público e problema, teoria de LLM/RAG/BKT, relação explícita com os artigos, arquitetura, evidências locais básicas, protocolo API, limitações e próximos estudos. Apresentar sempre o que está implementado, testado e apenas proposto.

A apresentação segue o mesmo argumento, com notas para fala e fontes. O próximo resultado que mais fortalece o artigo é uma comparação básica pareada, com revisão humana cega de enunciados e dicas. Aumento de funcionalidades ou de quantidade de links, sozinho, não demonstra contribuição científica.

Fontes oficiais: [preços](https://ai.google.dev/gemini-api/docs/pricing), [cotas](https://ai.google.dev/gemini-api/docs/rate-limits), [AI Studio](https://aistudio.google.com/rate-limit), [termos gratuitos](https://ai.google.dev/gemini-api/terms), [AutoCode](https://proceedings.iclr.cc/paper_files/paper/2026/hash/1bd78da0966968409e65b5e0b5dbb57e-Abstract-Conference.html), [OI-Assistant](https://ioi.te.lv/oi/files/volume19.pdf), [Codigen](https://doi.org/10.1109/VL-HCC65237.2025.00038).

## Verificação desta revisão

O teste offline de prefixos passou com solução conhecida. A auditoria de nove consultas BM25 encontrou ausência de resultados para “Vetores e contagem”; a expansão bilíngue corrigiu a ausência de candidatos, mas a primeira fonte passou a ser MEX, exigindo revisão pedagógica. Recuperar algo não significa recuperar o ideal. Os relatórios preservam antes e depois. Nenhuma chamada nova foi enviada à API e nenhum parâmetro de faturamento foi alterado.
