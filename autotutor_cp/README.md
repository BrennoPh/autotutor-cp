# AutoTutor-CP

Aplicação local em Python/Streamlit para geração validada de problemas C++17, tutoria adaptativa e recuperação de problemas por essência matemática. Implementa os mecanismos descritos no pedido, inspirados em AutoCode, OI-Assistant e CODIGEN; não pretende reproduzir resultados experimentais dos artigos.

## Executar

Requer Python 3.10+ e GCC com `g++` no PATH. No Linux, instale o pacote de compilação da sua distribuição; no macOS use GCC/Homebrew ou ferramentas de desenvolvimento compatíveis; no Windows use MinGW-w64 com `g++` no PATH.

A partir da pasta `autotutor_cp`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

No Windows, crie o ambiente com `py -m venv .venv` e ative com `.venv\Scripts\activate`. O diretório `workspace/` é criado automaticamente se necessário. 

Selecione um problema, escreva o código e submeta. A primeira submissão de cada problema-semente prepara e valida os testes, podendo levar alguns segundos. Problemas adaptados são verificados antes de aparecer no seletor. Os exemplos são públicos; as soluções de referência não são exibidas na interface do aluno.

## Estrutura

```text
autotutor_cp/
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── data/seed_problems.json
├── data/learning_content.json
├── data/progress.sqlite3     # criado localmente, ignorado pelo Git
├── core/
│   ├── __init__.py
│   ├── mini_judge.py
│   ├── runner.py
│   ├── autocode_engine.py
│   ├── problem_bank.py
│   ├── rag_retriever.py
│   ├── codigen_tutor.py
│   ├── llm_client.py
│   ├── learning_engine.py
│   ├── learning_views.py
│   ├── progress_store.py
│   ├── ui.py
│   └── theme.css
├── tests/
│   ├── test_system.py
│   ├── test_ui.py
│   ├── test_llm.py
│   └── test_learning.py
└── workspace/.gitkeep
```

## Interface do juiz online

O tema escuro é o padrão; **Preferências → Tema escuro** permite alternar para o claro. A página inicial mostra apenas duas ações principais. Há seis áreas de navegação: Início, Problemas, Estudar, Turmas, Progresso e Configurações. Filtros adicionais ficam recolhidos, e o catálogo tem páginas de 20 itens.

**Estudar** reúne diagnóstico de 18 perguntas, trilha por pré-requisitos, nove módulos com 72 slides, ilustrações, vídeos, fixação e Laboratório IA. **Progresso** mostra gráficos reais e submissões. A Arena mantém editor, tutoria e correção para os problemas locais.

### Catálogo e fontes

São **752 problemas na base inicial: 39 com correção local e 713 referências externas**. O conjunto reúne 15 exercícios originais e 737 registros únicos oriundos do [CSES](https://cses.fi/problemset/) e dos módulos Bronze/Silver do [USACO Guide](https://usaco.guide/). Destes registros, 24 tarefas CSES já foram incorporadas ao juiz local, mantendo seus IDs e sem duplicar o catálogo. Importação conferida em 24/10/2026. O catálogo externo contém título, seção, tópico, dificuldade aproximada e endereço oficial; não copia enunciados ou soluções. A dificuldade estimada não equivale à classificação oficial de cada juiz.

Exercícios externos abrem o enunciado e recebem submissões **no juiz de origem**. Aqui o aluno pode registrar andamento, conclusão e comprovante; o professor pode confirmar essa conclusão. Autodeclarações e confirmações são distintas de um AC produzido pelo Mini-Judge. Os 30 problemas locais possuem correção no app. O filtro **Correção → Dentro do AutoTutor** mostra esses exercícios.

### Mais 24 exercícios no juiz local

O pacote inclui Missing Number, Repetitions, Increasing Array, Bit Strings, Trailing Zeros, Coin Piles, Distinct Numbers, Maximum Subarray Sum, Stick Lengths, Missing Coin Sum, Ferris Wheel, Movie Festival, Apartments, Dice Combinations, Minimizing Coins, Coin Combinations I e II, Removing Digits, Grid Paths I, Book Shop, Counting Rooms, Subarray Sums II, Range Xor Queries e Static Range Minimum Queries.

Cada tarefa possui reformulação didática em português, exemplo próprio, contrato de entrada compatível com a origem, solução C++17 e suíte determinística própria. Há enumeração em casos pequenos, entradas de fronteira e casos grandes. O C++ é comparado com um oráculo Python independente; nos casos pequenos, são usadas busca completa, recursão ou cálculo direto quando aplicável. Casos grandes recebem verificação escalável. Os limites locais são 2 s e 256 MB, diferentes dos limites oficiais. Não foram importados testes ocultos do CSES; **AC local não representa AC oficial** e concordância finita não prova correção.

Na primeira submissão, a suíte é gerada e conferida antes de avaliar o código do aluno. Contas antigas recebem os novos exercícios sem perder rascunhos, histórico ou exercícios gerados. Conclusões externas antigas das tarefas promovidas não viram automaticamente ACs locais. A geração adaptativa escolhe entre os 39 contratos suportados, incluindo as tarefas incorporadas e os oito novos contratos de intervalos e grafos.

As seis fontes fornecidas pelo usuário estão disponíveis na biblioteca. Maratona UFMG, Neps, YouKn0wWho e TLE são recursos de estudo; seus catálogos não foram importados. Para atualizar os metadados públicos CSES/USACO, execute `python scripts/import_catalog.py` (requer internet). O script elimina duplicatas por URL e preserva a origem.

### Contas, turmas e trios

Crie uma conta de Aluno ou Professor na tela inicial. O primeiro cadastro pode vincular o progresso anônimo anterior; os demais começam separados. A senha é armazenada com PBKDF2-SHA256, salt individual e 600 mil iterações. Sessões expiram em 24 horas, são revogadas ao sair e não sobrevivem ao recarregamento completo do navegador. Após cinco erros de senha, há bloqueio de 15 minutos. Não há recuperação de senha por email.

Professores criam turmas com código de entrada, publicam listas do catálogo e acompanham indicadores dos alunos inscritos. Ao entrar por código, o aluno compartilha com o professor resumo de exercícios, questionários e desempenho; conversas privadas com a IA não aparecem nesse painel. Outros professores não podem consultar a turma. Cada aluno vê as listas e seus próprios trios.

O formador usa o modelo de IA selecionado para analisar estatísticas por assunto e propor trios, conforme complementaridade, equilíbrio entre trios ou níveis semelhantes. Os participantes são enviados com códigos anônimos; não são enviados nomes, usuários ou conversas privadas. O modelo recebe ACs locais, conclusões externas confirmadas e autodeclarações separados. Não há pesos fixos de habilidade na decisão da interface.

O professor pode pedir um trio ou a turma inteira, com até 30 alunos por rodada no modelo leve (pedidos que excedam o contexto são recusados; reduza o grupo). A resposta precisa incluir cada participante exatamente uma vez, em trio de três ou na lista de espera. Propostas inválidas não são salvas. Mudanças de participantes, evidências, estratégia ou modelo invalidam a proposta em tela. A sugestão não garante o ótimo global ou desempenho em competição; o professor publica somente ao salvar.

O painel permite **Analisar turma com IA**. A interpretação é arquivada na biblioteca privada do professor; as conversas privadas dos alunos continuam fora do acompanhamento.

### Conectar o Gemini

1. Na barra lateral, abra **Assistente IA**, selecione **Gemini** e informe a chave e o modelo.
2. Abra **Configurações** e use **Testar conexão**. Selecionar o provedor ou colar a chave, por si só, não faz uma chamada e não é tratado como fallback.
3. Se o modelo não estiver disponível, use **Buscar modelos disponíveis**, selecione um modelo de texto e clique em **Usar modelo selecionado**. Teste novamente.

O modelo inicial agora é `gemini-flash-latest`; um modelo escolhido manualmente continua editável. A listagem de modelos usa os modelos retornados pela conta e filtra suporte a `generateContent`; a listagem não substitui o teste de geração. Erros 401/403, 404, 429 e 5xx têm explicações distintas. O diagnóstico mostra o código HTTP e o detalhe redigido da API, sem incluir a chave nos eventos; pedidos e respostas são guardados separadamente no histórico local de chamadas. Espaços nas extremidades da chave/modelo e o prefixo `models/` são normalizados.

Modelos preview podem aceitar `generateContent` sem aceitar `system_instruction`. Se a API retornar explicitamente HTTP 400 com “Developer instruction is not enabled” (ou indicação equivalente de recurso não suportado), o adaptador repete a solicitação colocando as orientações no conteúdo do pedido. As orientações pedagógicas e os filtros locais continuam ativos, embora instruções no pedido não tenham a mesma separação de papéis que instruções de sistema. A incompatibilidade é memorizada por modelo no perfil local, evitando repetir o erro conhecido a cada ação. Se o modelo rejeitar explicitamente o modo JSON, o adaptador pede JSON por texto e mantém a validação do resultado. Há no máximo duas adaptações de parâmetros por chamada. Se a API informar explicitamente “This model only supports Interactions API”, o adaptador passa para `client.interactions.create`, preservando instruções e validação de JSON, com `store=False`, sem ferramentas e sem encadear conversas remotas. A escolha desse endpoint também é memorizada. Erros de chave, cota, rede e parâmetros não relacionados não acionam essas adaptações. Requer `google-genai>=2.3`. Uma resposta recuperada dessa forma é identificada como resposta da API em formato compatível, sem ser confundida com fallback local.

Respostas JSON inválidas, respostas vazias e rejeições pedagógicas também são registradas. Uma resposta de API filtrada pelo tutor não é confundida com falha de conexão. Exemplos comentados curtos em materiais independentes são permitidos; diagnósticos após falha continuam sem patches executáveis. Os testes da integração usam respostas simuladas do SDK; uma conexão real exige a chave do usuário e é confirmada pelo botão na interface.

## O que funciona sem API

- MiniJudge compila com `g++ -O2 -std=c++17` e emite AC, WA, TLE, RE e CE. A comparação preserva espaços internos e ignora espaços finais e linhas vazias no fim. Cada teste tem seu próprio limite de tempo; a avaliação para na primeira falha. Conjuntos vazios são rejeitados.
- Seis problemas clássicos completos: BFS, DP de elementos não adjacentes, seleção de intervalos, partição por capacidade, soma de prefixos e diâmetro de árvore. Todos possuem enunciado, exemplo, solução eficiente e oráculo independente de força bruta.
- AutoCode enumera pequenos domínios: sequências de até três valores, grafos simples de até quatro vértices, intervalos de um domínio pequeno e árvores por listas de pais. Acrescenta testes aleatórios reprodutíveis, valores extremos e instâncias grandes. Na família Prefix Sum, o teste de estresse também aumenta Q.
- A validação checa gramática e restrições; compara `std` com `brute` apenas nas entradas pequenas e calcula as saídas oficiais grandes com `std`. Também verifica os exemplos. Divergências ou falhas de execução rejeitam o exercício. O selo registra contagens, semente, data e hash das fontes. Concordância finita não constitui prova de correção e não garante que toda solução subótima exceda o tempo em toda máquina.
- A adaptação usa o modelo selecionado para produzir o enunciado e as duas soluções, preservando o contrato da família. As soluções passam por testes independentes antes da publicação.
- RAG utiliza três espaços TF-IDF densos NumPy independentes: pergunta, conceitos/essência e resumo. A combinação usa pesos 0,25/0,45/0,30. Sem API, extração é uma aproximação por similaridade e ordenação é vetorial; as justificativas locais descrevem a estrutura do candidato sem prometer equivalência matemática.
- Tutor oferece hipóteses por veredito, contraexemplo observado, perguntas, materiais, comentários sobre o código e lacunas relacionadas ao histórico. Não apresenta as soluções de referência. Fluxogramas são gerados deterministicamente a partir da família; Mermaid é carregado por CDN, e a fonte permanece disponível sem internet.

## APIs opcionais

Na barra lateral escolha Gemini ou OpenAI, informe a chave e o identificador de um modelo disponível na sua conta. O modelo é editável; os valores iniciais são sugestões de configuração, sem garantia de acesso ou disponibilidade. Chamadas de geração têm timeout de 90 segundos. As chaves ficam em memória na sessão, sem persistência em arquivos.

O adaptador usa os SDKs oficiais: [OpenAI Chat Completions](https://developers.openai.com/api/reference/python/resources/chat/subresources/completions/methods/create) e [Google Gen AI](https://googleapis.github.io/python-genai/). Em erro de API, a interface informa a falha e usa as funções locais. Dados enviados podem incluir enunciado, código, caso falho e histórico recente; nenhuma chave é incluída nos prompts.

A geração por LLM reformula narrativa e limite de N, fornecendo novas fontes `std_cpp` e `brute_cpp`, mas mantém o objetivo e a gramática de um dos contratos suportados: o validador é explícito, não aceita formatos arbitrários. Isso permite verificar todas as entradas antes de executar. Problemas novos fora desses contratos requerem adicionar gerador, validador e oráculo independentes.

O reranker recebe apenas candidatos recuperados; IDs desconhecidos ou duplicados são descartados. Guardrails usam exemplos few-shot e filtro conservador de saída após falhas, bloqueando blocos executáveis e mantendo perguntas e pistas. São controles pedagógicos de melhor esforço, não garantia contra toda forma de revelação textual. Anotações preservam o código do próprio aluno e adicionam comentários determinísticos. Em CE, RE e TLE as pistas locais são hipóteses, não análise estática completa.

## Execução e limites de isolamento

Este projeto é um protótipo local para código confiável. `subprocess` não é um sandbox: programas de alunos e fontes geradas pelo LLM executam com as permissões do usuário, podendo acessar rede e arquivos. Não exponha o app a submissões públicas sem mover compilação e execução para contêiner/VM descartável, sem rede, sem credenciais e com limites do sistema operacional.

Em POSIX, um launcher separado aplica limites de CPU, memória virtual (256 MB), tamanho de arquivos/saída, descritores e core dumps. O processo roda em diretório temporário, com grupo separado, timeout de parede e encerramento do grupo. O tempo reportado inclui o launcher. A saída é truncada e o excesso causa RE. A compilação tem timeout de 25 segundos e diagnósticos limitados na interface, mas não está isolada nem sujeita aos mesmos limites do executável.

No Windows há timeout do processo principal e arquivos temporários, mas os limites POSIX e o encerramento de processos descendentes não se aplicam. A portabilidade do código e o caminho Windows foram implementados, porém a validação desta entrega ocorreu no Linux.

Histórico, resultados, rascunhos, questionários, aulas estudadas e problemas gerados são persistidos no SQLite e vinculados à conta autenticada. Parâmetros de URL não selecionam perfis. A primeira conta pode recuperar o progresso anterior, preservado também em `data/backups/before-classrooms.sqlite3` nesta migração. O controle de contas não altera os limites de execução C++ descritos acima.

## Biblioteca, diagnóstico e trilha adaptativa

Os módulos cobrem Fundamentos, Estruturas de Dados, Prefix Sum, Busca Binária, Matemática, Guloso, DP, Grafos e Árvores. Cada aula inclui objetivos, quatro seções explicativas, exemplo rastreado, fragmento C++ comentado, erros frequentes, desafio e duas questões de fixação. Há **72 slides** ao todo, visualização no app e download de apresentações HTML independentes com navegação por teclado e impressão para PDF; não são arquivos PowerPoint.

As ilustrações SVG são esquemas didáticos autorais: prefixos, intervalo da busca binária, estados de DP, fila FIFO, Euclides, pares de laços, seleção de intervalos, camadas da BFS e estrela de árvore. As demonstrações com etapas são controladas por sliders e funcionam sem API ou CDN. Os dados dessas ilustrações são exemplos, separados das estatísticas reais do aluno.

As recomendações de vídeo têm título, canal, URL e fonte no [catálogo educacional AoCPC](https://aocpc-community.github.io/aocpc-guide/guide/aprender/), consultado em 24/10/2026. Links foram conferidos no catálogo, sem alegação de ter assistido às aulas ou garantia de disponibilidade/incorporação pelo YouTube. O player só é aberto ao ativar o controle correspondente.

O diagnóstico tem 18 questões de múltipla escolha, duas por tópico, sem alternativa pré-selecionada. O gabarito determina os acertos, mas não converte porcentagens automaticamente em nível. A ação **Analisar meu aprendizado com IA** envia as estatísticas por tópico, resultados recentes, leituras e tempo disponível ao modelo, que propõe nível, confiança, pontos fortes, lacunas e uma trilha justificada. Sem evidência válida de questões ou problemas, o nível precisa ser **Não avaliado**. Trata-se de uma hipótese do modelo, não certificação de proficiência.

A IA decide a ordem pedagógica e as ações; o aplicativo verifica IDs do currículo, duplicatas, campos obrigatórios e pré-requisitos. Resposta inválida interrompe a operação sem um plano por regras. A análise fica salva em SQLite e na biblioteca com modelo, provedor e impressão digital das evidências. Alterar as atividades, horas ou modelo exige nova análise, por ação explícita; a navegação não dispara inferências.

No painel, cada questão conta com sua resposta mais recente para evitar inflação por repetições. O gráfico temporal mantém todas as atividades, avisando que elas podem ter assuntos e dificuldades diferentes. A distribuição de vereditos usa todas as submissões; a aprovação de problemas por tópico usa a última submissão de cada problema. Assuntos sem respostas não recebem zero. Os gráficos aparecem somente quando existem dados do perfil.

## Pedidos personalizados no Laboratório IA

O campo **O que você quer aprender?** aceita até 2000 caracteres para explicar uma dúvida específica. As opções de tamanho são Curto (aproximadamente 150–250 palavras), Médio (350–550) e Longo (700–1100), sem contar referências. A profundidade pode ser Visão geral, Passo a passo ou Aprofundada. Exemplos e exercícios podem ser desativados separadamente, inclusive quando o tipo de material normalmente os sugere. A extensão é uma orientação ao modelo, não um limite rígido.

O pedido, as preferências e o histórico do próprio aluno são enviados ao motor escolhido. No motor Ollama, o modelo recebe a aula relacionada como contexto e escreve a explicação conforme o pedido. O acervo não substitui a geração em caso de falha. O pedido e as opções ficam preservados ao navegar e entrar novamente. Cada material guarda uma cópia das preferências e do objetivo na biblioteca, junto ao conteúdo e às referências.

## Biblioteca ampliada e coleção pessoal

A biblioteca tem cinco seções: **Aulas**, **Acervo RAG**, **Guias de aprofundamento**, **Referências** e **Minha coleção**. Mantém as nove aulas, 72 slides e ilustrações, e acrescenta nove guias autorais com cerca de 3500 palavras, 18 exercícios comentados e prática vinculada ao juiz local. Os guias explicam invariantes, provas, complexidade, rastreamento de exemplos e erros comuns. Eles podem ser baixados para leitura offline.

São 49 referências únicas com assunto, formato, idioma, origem e situação de verificação: módulos do USACO Guide, artigos do CP-Algorithms, videoaulas AoCPC e Errichto, curso CP Initiative e os seis recursos indicados pelo usuário. O canal Maratona UFMG é confirmado pela página oficial do DCC. YouKn0wWho e TLE permanecem indicados como recursos cujo conteúdo não pôde ser inspecionado; não há alegação de importar suas aulas. Resumos e metadados são locais; os artigos completos e vídeos continuam nas plataformas de origem. Reprodução de vídeos é opcional e depende da incorporação autorizada pelo provedor.

Materiais, explicações de código, diagnósticos, exercícios gerados e recomendações solicitadas são arquivados automaticamente em Minha coleção, inclusive registros anteriores da conta. A consulta é paginada, sem o limite de 100 itens da antiga lista do Laboratório, e permite buscar título ou conteúdo e filtrar tipo/andamento. A coleção não mostra as soluções de referência dos exercícios gerados. Referências podem ser guardadas sem duplicar o mesmo endereço; links informados pelo aluno e links de IA fora da curadoria recebem rótulo de não verificados.

Cada item, guia e referência aceita andamento (Quero estudar, Estudando, Estudado) e anotações pessoais persistidas por conta. A exportação em Configurações inclui esses registros. Novos materiais incluem referências da curadoria correspondente ao assunto; o pedido à IA fornece uma lista de links permitidos, sem prometer que outras citações geradas foram verificadas. Marcar um item como estudado é um registro pessoal, separado da avaliação de domínio.

Os arquivos `data/local_classics.json`, `data/deep_guides.json` e `data/study_resources.json` contêm os conteúdos versionados. Os respectivos scripts `scripts/build_local_pack.py`, `scripts/build_deep_guides.py` e `scripts/build_resources.py` reconstroem esses dados a partir das definições editoriais incluídas no projeto; não fazem busca ao vivo. Uma atualização de curadoria exige conferir novamente as fontes e a data registrada.

## Banco local e memória para a IA

O banco padrão é `data/progress.sqlite3`, criado automaticamente com SQLite, sem servidor externo. Para usar outro arquivo, configure `AUTOTUTOR_PROGRESS_DB`. As transações usam WAL e as conexões são fechadas após cada operação. O arquivo e seus auxiliares estão no `.gitignore`.

- `library_state`: andamento e anotações pessoais de cada item de estudo.
- `users`, `sessions`, `login_failures`: contas, hashes, sessões e limitação de tentativas.
- `classrooms`, `memberships`, `assignments`, `external_progress`, `formations`: turmas, inscrições, listas, conclusões externas e trios.
- `profiles`: snapshot por identificador de perfil, incluindo progresso, histórico, rascunhos, problemas e últimos resultados.
- `artifacts`: registros de conteúdos, exercícios gerados, submissões completas com código e resultados, orientações, questionários e eventos de leitura. Criar outro material não sobrescreve o registro anterior.
- `model_calls`: provedor, modelo, instruções do app, pedido enviado, resposta ou erro e tamanho do contexto histórico usado. Clientes SDK, cabeçalhos e o campo de chave de API não são armazenados; a chave configurada é ocultada caso apareça no registro de chamada.

Em Configurações, **Exportar dados do perfil** inclui snapshot, todos os artefatos e chamadas armazenadas. O Laboratório permite consultar os 100 materiais mais recentes; os demais continuam no banco e na exportação. A interface salva o progresso ao responder, navegar ou concluir ações. Cada conta nova começa separada das anteriores.

Antes de uma geração, o adaptador consulta o banco para montar um contexto de até 7000 caracteres: nível escolhido, desempenho observado por assunto, até seis submissões recentes, aulas lidas e até três trechos de materiais relacionados selecionados entre os 100 mais recentes. Não envia o banco inteiro nem usa respostas de outros perfis. A orientação do tutor trata o histórico como dado, nunca como instrução a executar. O teste de conexão usa somente uma mensagem curta e não envia esse histórico.

Essa memória melhora o contexto disponível para personalizar a resposta; **não retreina o modelo, não faz fine-tuning e não altera seus pesos**. As APIs ainda podem errar. O armazenamento de pedidos e respostas é local; na geração, o pedido atual e o resumo histórico são enviados ao provedor escolhido, conforme a configuração do usuário.

## Verificar

Com o ambiente ativado:

```bash
pytest -q
```

Os testes verificam cinco vereditos reais, detalhes de WA, timeout, limpeza, compilador ausente, rejeição de oráculo incorreto, sete referências contra força bruta e entradas grandes, adaptação local, recuperação semântica e fluxos da interface Streamlit. Os provedores reais não são chamados pela suíte automatizada. A avaliação opt-in do Qwen usa o motor local sem chave.


## Llama 3.2 1B como IA local padrão

O motor local padrão voltou a ser **Llama 3.2 1B** (`llama3.2:1b`) via Ollama, a pedido do usuário para reduzir consumo de memória. O Qwen2.5 3B foi removido da instalação. Sessões antigas que apontavam para ele migram para o Llama. Gemini, OpenAI, DeepSeek e Qwen por API continuam disponíveis; chaves e dados de estudo não são alterados por essa migração.

Use `bash scripts/start_app_local.sh` para iniciar o sistema e o motor local. O Llama já está instalado; para uma instalação nova, use `ollama pull llama3.2:1b`. Os scripts limitam o servidor a um modelo e uma geração por vez. Cada chamada usa dois núcleos de CPU, lote de 128, contexto de 4096 e saída máxima de 2048 tokens. `keep_alive=0` descarrega o modelo ao final da resposta, em vez de retê-lo por dois minutos. Cada nova solicitação pode precisar carregar os pesos novamente.

O transporte permanece restrito a HTTP de loopback, sem proxy, credenciais remotas ou redirecionamentos. Os modelos ficam em `.models/`. Conteúdos extensos e qualidade pedagógica continuam sujeitos às limitações do modelo de 1B; os resultados anteriores não o certificam como tutor confiável.

### Onde a IA participa

- Nível, confiança, interpretação das estatísticas e trilha: `core/ai_coach.py`.
- Análise da turma e escolha/justificativa dos trios: mesmo serviço, com evidências permitidas ao professor.
- Diagnóstico de submissões, explicações, comentários de código, lacunas, materiais e fluxogramas: `core/codigen_tutor.py`.
- Extração matemática e reordenação justificada dos candidatos de busca: `core/rag_retriever.py`.
- Adaptação de problemas: `core/autocode_engine.py`, com validação independente obrigatória.

A interface usa `LLMClient(require_model=True)`: indisponibilidade, JSON inválido, falha de validação ou conteúdo rejeitado interrompem a operação, sem substituir por orientação do acervo. As funções legadas determinísticas permanecem somente para compatibilidade interna e testes de regressão; não são oferecidas como motor da aplicação.

Cálculos de porcentagem, gráficos, gabaritos, permissões, armazenamento, validação de IDs e juiz C++ continuam sendo operações objetivas. A IA interpreta os dados; ela não inventa estatísticas nem concede AC sem executar os testes. A biblioteca permanece como material de referência e fonte factual de contexto para o modelo, sem servir como resposta substituta em caso de falha. Isso é uso de contexto/RAG, não treinamento dos pesos.

### Avaliação reproduzível

`python scripts/evaluate_qwen.py` executa somente entradas sintéticas: conexão, explicação de prefixos, correção de premissa matemática errada, análise de aluno e turma, formação de trios e recuperação de problemas. Salva respostas e tempos em `.runtime/qwen-evaluation.json`. As suítes automatizadas usam transporte simulado para verificar fluxos, isolamento, auditoria e rejeição de propostas inválidas, sem certificar a veracidade das respostas.

O Llama 3.2 1B foi testado anteriormente e apresentou erros conceituais mesmo com aula correta no contexto. O Qwen foi testado anteriormente e retirado por consumo de memória; tamanho maior, JSON válido e conexão bem-sucedida não demonstram qualidade pedagógica. Considere tempo, memória e revisão humana das respostas antes de ampliar o uso.

Referências: [Qwen no Ollama](https://ollama.com/library/qwen2.5:3b), [ficha oficial](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct), [API de chat](https://docs.ollama.com/api/chat).

## DeepSeek e Qwen por API

Em **Assistente IA → Motor de IA**, escolha **DeepSeek · API** ou **Qwen · API Alibaba Cloud**. Informe a chave e o modelo; em **Configurações**, use **Testar conexão** ou **Buscar modelos disponíveis**. Selecionar o serviço não faz chamadas. As chaves ficam somente na sessão, separadas por provedor e fora do banco local. Os históricos e respostas passam pela mesma auditoria, biblioteca e validação, sem resposta substituta por regras em caso de falha.

- **DeepSeek:** endpoint oficial `https://api.deepseek.com`, modelo inicial `deepseek-flash`. O nome pode ser editado ou escolhido no catálogo retornado pela conta.
- **Qwen por API:** Alibaba Cloud Model Studio, modelo inicial `qwen-plus`. Região inicial Singapura; também disponíveis Virgínia, Pequim e Hong Kong. A região e o workspace devem corresponder à chave. Sem workspace, usa o domínio DashScope compartilhado da região; com um ID válido, usa o domínio oficial dedicado. O catálogo consulta `/api/v1/models` com filtro Qwen/texto e paginação limitada a 1000 resultados. Um ID também pode ser informado manualmente.
- A opção **Modelo Qwen exige raciocínio ativo** controla `enable_thinking`. Começa desativada para o modelo inicial e suas operações em JSON. Alguns modelos exigem raciocínio; nesse caso ative a opção e confira a compatibilidade com JSON. Rejeições aparecem com diagnóstico, sem troca silenciosa de modelo ou provedor.
- **Ollama** continua sendo a execução local de `llama3.2:1b`, independente de uma conta de API Qwen.

Os testes usam respostas simuladas para conferir endpoints, região, isolamento de chaves, catálogo, JSON, histórico e auditoria. Não houve chamada real aos serviços pagos nesta instalação, pois nenhuma chave nova foi fornecida para isso.

Documentação conferida em 04/11/2026: [DeepSeek](https://api-docs.deepseek.com/), [JSON DeepSeek](https://api-docs.deepseek.com/guides/json_mode/), [Qwen/OpenAI compatível](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope), [regiões e endpoints Qwen](https://help.aliyun.com/en/model-studio/base-url), [catálogo Qwen](https://www.alibabacloud.com/help/en/model-studio/list-models).

### Resultado local desta sessão

A conexão real com `qwen2.5:3b` funcionou e o modelo carregado ocupou cerca de 2,17 GB segundo o Ollama, com contexto 4096 e execução em CPU. Na primeira rodada, uma explicação calculou o intervalo corretamente, mas trouxe recomendação incorreta sobre prefixos após atualização e trocou os dados do pedido pelos do exemplo da base. Uma pergunta com premissa falsa e análises estatísticas também tiveram erros.

Após explicitar o contexto, fornecer porcentagens calculadas e exigir JSON Schema, a análise de aluno e o trio passaram no formato, mas continuaram inventando fatos: acertos foram invertidos, aulas não estudadas foram declaradas concluídas e apareceu um corte de nota inexistente para excluir um aluno do trio. A análise agregada repetiu algumas porcentagens corretas e inventou outras. Um reteste de material excedeu 300 segundos. Os tempos incluem carga e espera entre rodadas; não são benchmark isolado.

Portanto, **o Qwen2.5 3B não foi aprovado para análises confiáveis nesta avaliação**. Foi removido desta instalação a pedido do usuário; provedores de API são alternativas configuráveis, sem alegação de qualidade avaliada até teste real. Os resultados brutos e a revisão manual ficam em `.runtime/qwen-evaluation-initial.json` e `.runtime/qwen-evaluation.json`.

## Acervo inicial para RAG: conteúdo de verdade

O pacote inclui **321 documentos e 1607 trechos**: 164 artigos CP-Algorithms, 138 módulos USACO Guide e 19 aulas/guias autorais em português. Há 87 documentos classificados na trilha **Base**; os demais são complementares. A base inicial cobre implementação/ad hoc, vetores, ordenação, busca binária, soma de prefixos, BFS, DFS, árvores, DP e matemática básica, além das referências avançadas.

O conteúdo compartilhado fica em `data/knowledge.sqlite3`, separado dos perfis e conversas. Textos são armazenados uma vez por documento, compactados com zlib; os trechos guardam somente posições no documento. Um índice **SQLite FTS5/BM25** permite buscar os trechos sem carregar uma matriz densa ou enviar toda a biblioteca à API. O banco usa aproximadamente 4,4 MiB nesta edição. `data/knowledge.json.gz` exporta os mesmos textos e metadados em JSON compactado, com aproximadamente 0,81 MiB, para portabilidade. PostgreSQL não é necessário para esta instalação local.

A busca usa palavras e aliases bilíngues de programação; não há um novo modelo de embeddings nem treinamento de pesos. O RAG dos problemas continua usando seus espaços TF-IDF e reordenação por IA. Agora também recebe trechos do acervo didático. Na geração de materiais, o pedido e o assunto recuperam até quatro trechos, limitados a 2400 caracteres no Ollama ou 6500 nos provedores externos. Os trechos entram efetivamente no pedido da IA, com fontes e licenças; o material salva os IDs e referências recuperados na biblioteca. A IA escreve em português, mesmo quando a referência está em inglês. Se o modelo falhar, não há substituição por texto pronto.

Em **Biblioteca → Acervo RAG**, é possível pesquisar, filtrar a base por assunto/fonte, ler o texto, guardar anotações privadas e baixar o artigo com seus créditos. A busca e a leitura não exigem chamada à API. A marcação de Base é organização editorial para começar pelo assunto, não uma estimativa automática de proficiência do aluno.

### Fontes, limpeza e versões

As versões estão fixadas em `data/knowledge_sources.json`. A importação mantém URL, título, autores disponíveis, idioma, licença, revisão e hash do conteúdo. O download verifica o SHA do blob Git; não executa código ou componentes MDX. Componentes de interface, blocos identificados como soluções de problemas e programas completos são removidos; fórmulas e fragmentos didáticos são preservados. O texto fica identificado como uma adaptação automática, sem alegação de revisão pedagógica integral.

CP-Algorithms usa **CC BY-SA 4.0**; USACO Guide usa **CC BY-NC-SA 4.0**. Os documentos mantêm suas licenças próprias e créditos, inclusive na exportação. O conteúdo USACO é destinado aqui ao uso educacional não comercial. As aulas autorais mantêm a identificação do projeto. Vídeos permanecem como links; nenhum vídeo ou transcrição foi baixado. CSES, Neps e demais recursos anteriores continuam no catálogo e nas referências conforme o conteúdo já disponível.

Para reconstruir sem copiar bancos privados:

```bash
python scripts/fetch_knowledge_sources.py --output .runtime/knowledge_sources
python scripts/import_knowledge.py --sources .runtime/knowledge_sources --database data/knowledge.sqlite3 --export data/knowledge.json.gz
python scripts/evaluate_knowledge.py
```

Uma importação repetida é idempotente: não duplica documentos ou trechos. Alterações substituem o documento e reconstroem o índice em transação. Também é possível importar o pacote com `python scripts/import_knowledge.py --import-json data/knowledge.json.gz --database data/knowledge.sqlite3`.

## Trilhas por assunto, calendário e preferência de aprendizado

Em **Aprendizado → Minha trilha → Por assunto**, informe por exemplo “Quero aprender DP”, o objetivo, o assunto de referência, os dias disponíveis, o tempo diário e o horizonte máximo. Escolha entre equilíbrio, aprender resolvendo problemas, teoria primeiro ou vídeos e exemplos. A IA recebe evidências do perfil e um conjunto limitado de conteúdos do acervo, vídeos e problemas reais. Ela decide a sequência, os objetivos, o número de sessões e o tempo estimado de cada atividade.

O aplicativo valida IDs e tipos de recursos, mistura de atividades disponíveis e orçamento diário, e aplica as sessões aos dias da semana escolhidos. Ele soma as estimativas da IA para mostrar duração e tempo restante; não atribui tempo por uma faixa fixa de nota. As datas são calculadas a partir do calendário do usuário. Uma saída inválida interrompe a criação, sem uma trilha pronta substituta. No modelo local leve, a primeira etapa fica limitada a oito sessões para caber no contexto; em API, até 24 sessões, sempre dentro do horizonte disponível.

A trilha abre artigos no acervo, vídeos nos links e problemas na Arena. Recursos externos continuam identificados com correção no juiz de origem. Cada atividade tem uma marcação de conclusão persistida em `topic_plan_progress`, com escopo de conta. O plano é um artefato `topic_plan` e aparece na biblioteca; a exportação do perfil inclui seu progresso. Concluir uma atividade não é tratado como prova de domínio.

A opção **Replanejar próximas sessões com IA** usa as atividades concluídas e o relato do aluno para gerar outra etapa. A nova versão aponta para a anterior, preservando a trilha e suas marcações. As durações são estimativas do modelo e podem exigir ajustes; os testes automatizados verificam contratos, calendário e persistência, não eficácia educacional.

## Recomendações de modelos e diagnóstico de saldo

Em Configurações há recomendações por provedor, com opções de maior capacidade e de uso diário, fontes oficiais e data de revisão em `data/model_recommendations.json`. Os botões apenas selecionam o modelo, sem fazer chamada ou mudar de empresa. As sugestões são inferências técnicas a partir das capacidades documentadas, sem ranking empírico entre as APIs nesta instalação. O Llama 1B é o padrão leve; o Qwen3B foi removido e não foi aprovado na avaliação anterior.

O diagnóstico prioriza o `status_code` HTTP numérico em vez do campo textual `code` de SDKs compatíveis. **HTTP 402 no DeepSeek significa saldo insuficiente**, com mensagem própria; não deve aparecer como erro genérico de parâmetros ou de autenticação. As chaves, cotas e saldos continuam sendo administrados no provedor.

O pacote JSON compactado acompanha o código. Na primeira abertura com o caminho padrão, a aplicação recria o banco público se ele não existir, sem fazer chamadas à IA ou substituir um banco existente. Caminhos personalizados em `AUTOTUTOR_KNOWLEDGE_DB` devem ser preparados com o importador. O banco reconstruído é ignorado pelo Git; o pacote JSON mantém a distribuição compacta.


A criação de problemas no Laboratório IA usa o pedido específico como prioridade sobre o assunto de referência. A IA seleciona um contrato suportado; pedidos incompatíveis são recusados, sem escolher outro assunto. Segment Tree possui contrato próprio de atribuição pontual e mínimo em intervalos, com testes pequenos, aleatórios e grandes. As duas soluções geradas também são comparadas ao contrato original.


### Páginas de estudo e navegação

Criar estudo com IA e Meus estudos são entradas diretas no menu. O início reúne ações de estudo, trilhas, biblioteca, leituras recentes e fundamentos de programação competitiva. Os materiais são abertos em uma página própria com sumário, leitura em coluna, estimativa de tempo, anotações, marcação de estudo, referências e download. O endereço `?estudo=<id>` permite reabrir o conteúdo após entrar na conta proprietária; ele não libera acesso a outras contas.

O modo Longo usa uma faixa orientadora de 1000–1600 palavras e permite uma meta de 500–20000 caracteres (5000 por padrão). Uma quantidade explícita de caracteres no pedido tem prioridade sobre a faixa de palavras. A geração recebe orientação para desenvolver pré-requisitos, intuição, modelagem, correção, complexidade de tempo e memória e casos de borda. A extensão real depende do modelo; o leitor informa o tamanho efetivamente recebido, sem completar o texto com repetições ou conteúdo por regras.


## Evolução do RAG e diversidade de prática

Consulte [o projeto de evolução](docs/PLANO_EVOLUCAO.md) e `data/study_sources_report.json` para a cobertura real das fontes. Novos materiais usam trechos externos; links de vídeos e problemas ficam separados de evidência teórica. O gerador escolhe entre 39 contratos locais e prioriza contratos não usados entre os oito últimos gerados no perfil; a interface permite revisão explícita quando necessária. A quantidade de contratos por assunto é limitada.


Artigo com foco em IA: [fonte LaTeX SBC](docs/artigo_sbc/artigo.tex), [PDF](docs/artigo_sbc/artigo.pdf) e [instruções](docs/artigo_sbc/README.md).


## Experimentos de IA com orçamento zero

O Laboratório IA inclui um painel experimental com Gemini 3.1 Flash-Lite, fontes externas recuperadas e validação independente por contrato. A configuração usa `.env` privado (modelo em `.env.example`). Não há ativação de faturamento nem fallback pago; o adaptador limita tentativas e tokens e interrompe ao atingir cota. O usuário deve manter a chave em projeto com cota gratuita. O limite financeiro autorizado é zero.

Consulte [metodologia e comandos](docs/research/metodologia.md), [resultados observados](docs/research/resultados.md), [fundamentação](docs/research/fundamentacao_teorica.md) e [próximos experimentos](docs/research/roadmap.md). Sem `--live`, o script de piloto usa uma fixture offline e não chama APIs. O juiz da aplicação requer Linux, bubblewrap, prlimit e namespaces disponíveis; sem isolamento, bloqueia execução de código.


## Recorte atual: fundamentos

O piloto agora começa com soma de prefixos e oferece nove objetivos básicos. Tópicos avançados no painel experimental são opcionais. Veja [o mapeamento e protocolo acadêmico](docs/research/foco_fundamentos.md). Os resultados anteriores ficam preservados; o piloto avançado não representa avaliação de iniciantes.
