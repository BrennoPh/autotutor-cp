# Reprodução do AutoCode no AutoTutor-CP

Plano construído a partir da auditoria e das perguntas de 05/11/2026. **Este arquivo é uma proposta de implementação e avaliação. O pipeline completo não foi implementado nem executado durante a auditoria.**

## O resultado que queremos reproduzir

O AutoCode não é um modelo treinado chamado “AutoCode”. É um procedimento que organiza modelos, geração de programas e validação em rodadas. Na versão ICLR 2026:

- A Tabela 1 usa **OpenAI o3** e reporta 91,1% de concordância de vereditos em 7.538 problemas e 195.988 submissões.
- A Tabela 2 usa **GPT-5-High**, conforme nomenclatura do artigo, e reporta 98,7% em outro conjunto de 720 problemas, com 33 submissões por problema e distribuição própria.
- O apêndice também compara AutoCode e HardTests mantendo **GPT-4o** ou **o3** no mesmo desenho.

Fonte: [AutoCode, versão publicada](https://openreview.net/pdf?id=F96nsbbhXC). Identificação: [ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/1bd78da0966968409e65b5e0b5dbb57e-Abstract-Conference.html).

Uma reprodução exata exige os mesmos dados, configuração e modelos. Uma reprodução metodológica pode trocar o modelo, desde que registre essa diferença e avalie a nova condição. Não presumir que uma versão atual de um modelo equivale ao snapshot histórico do artigo.

## O que já temos e o que falta

Temos compilação, execução limitada, validação de entradas para contratos conhecidos, referências eficientes, força bruta ou oráculos Python, três categorias de casos e persistência. A adaptação de um problema é comparada ao objetivo do contrato original.

Faltam as rodadas completas para problemas abertos, seleção de validadores e checkers candidatos, geração de estruturas novas com verificação correspondente e avaliação com submissões cujo veredito oficial é conhecido. O recuperador de materiais e o seletor de problemas também são caminhos distintos hoje. Trocar somente o nome do modelo não acrescenta essas etapas.

## Arquitetura de reprodução proposta

1. **Especificação versionada:** enunciado, operações, restrições e comportamento esperado. Separar um problema existente, usado para avaliar testes, de um problema novo, usado para avaliar autoria.
2. **Candidatos de validador:** gerar programas que rejeitem entradas ilegais. Conferi-los com casos válidos e inválidos preparados independentemente, incluindo fronteiras.
3. **Geradores de dados:** pequenos enumeráveis, casos aleatórios/extremos e entradas grandes. Toda entrada passa pelo validador escolhido. Registrar seed e programa gerador.
4. **Checker:** comparação exata quando a resposta é única. Se houver múltiplas respostas válidas, criar e selecionar checker específico com testes independentes. Respostas interativas exigem outro componente; começar por tarefas não interativas.
5. **Soluções:** gerar eficiente e força bruta. Compilar e confrontar saídas em casos pequenos; usar oráculos ou referências independentes quando disponíveis. Erros comuns entre soluções continuam possíveis.
6. **Rodadas de reparo:** devolver mensagens do compilador, entradas rejeitadas e contraexemplos ao modelo. Limitar tentativas e custo. Preservar também candidatos rejeitados, em vez de registrar apenas a melhor saída.
7. **Seleção e publicação:** escolher verificadores por desempenho no conjunto de desenvolvimento e publicar somente após verificações. Não usar o conjunto final para corrigir o pipeline.
8. **Auditoria externa comum:** executar os testes gerados sobre submissões com vereditos oficiais. Essa é a avaliação independente, diferente da concordância interna entre duas soluções.

O diagrama e os componentes dessa seção são futuros. Não devem ser confundidos com a arquitetura atual apresentada no slide 12.

## Experimento com Gemini 3.1 Flash-Lite

O modelo oficial `gemini-3.1-flash-lite` oferece texto estruturado e raciocínio. Pode assumir as tarefas de geração por API, enquanto a máquina local executa compilação, armazenamento e juiz. [Documentação oficial do modelo](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite).

A disponibilidade de JSON e raciocínio torna a integração possível; não demonstra capacidade para obter 98,7% nessa tarefa. A Google o descreve para tarefas leves e alto volume. Compará-lo com modelo mais capaz, mantendo o mesmo pipeline, permite avaliar o efeito de capacidade. Não afirmar previamente que a melhoria acontecerá.

A página oficial de preços, consultada em 05/11/2026, informa camada gratuita para o modelo, sujeita às cotas do projeto. A cota efetiva deve ser conferida no AI Studio. Um plano gratuito pode servir a um piloto, mas não assegura volume para repetir integralmente as amostras do artigo. [Preços](https://ai.google.dev/gemini-api/docs/pricing) e [limites](https://ai.google.dev/gemini-api/docs/rate-limits).

Antes de rodadas extensas, medir conexão, conformidade de saída, capacidade de gerar referências corretas e custo por tentativa. Manter checkpoint para retomar após quota ou indisponibilidade e política de tentativas que não esconda falhas. Não é necessário enviar dados pessoais de estudantes para esse benchmark.

## Métricas comparáveis

- **Concordância:** fração de vereditos iguais aos oficiais. Definir antes se a comparação considera classes completas ou somente aceito/rejeitado.
- **Falso aceite:** proporção de soluções oficialmente erradas que nossos testes aceitam.
- **Falsa rejeição:** proporção de soluções oficialmente corretas que nossos testes rejeitam.
- **Rendimento:** problemas/validadores publicáveis por tentativa, contando rejeições e reparos.
- **Custo:** tokens, chamadas, tempo e recursos por tentativa e por resultado válido.

Uma alta concordância pode esconder um problema se o conjunto tiver classes desbalanceadas. Por isso os três primeiros indicadores devem aparecer juntos, com tamanho e distribuição da amostra. Usar as mesmas submissões em comparações pareadas e separar desenvolvimento de teste.

O nosso 0/5 de perguntas numéricas **não entra como taxa de concordância do juiz**. Os 207 testes aprovados **não entram como taxa de acerto do gerador**. Essas avaliações tratam de objetos diferentes.

## Viabilidade sem pagamento e benefícios estudantis

O piloto Gemini é o caminho gratuito diretamente pertinente à aplicação, sujeito à conta e quotas. Modelos OpenAI não foram identificados com concessão automática de API para estudante no Brasil nas fontes consultadas. A oferta [Codex for Students](https://developers.openai.com/community/students) atende estudantes elegíveis nos EUA e Canadá e distingue créditos de Codex de créditos API.

Há um [benefício de créditos API para assinaturas Pro e Business elegíveis](https://developers.openai.com/api/docs/guides/chatgpt-api-credits), que exige ativação. Plus não aparece como elegível nesse benefício. Isso não é uma bolsa estudantil. O [GitHub Student Developer Pack](https://education.github.com/pack) inclui créditos Azure, sem garantir acesso aos modelos específicos usados no artigo. A disponibilidade pessoal não foi consultada nem presumida.

## Primeiro resultado útil

O primeiro resultado deve responder: “Com um conjunto autorizado e reservado de problemas e submissões, qual concordância nosso protocolo atual obtém, e quanto muda ao introduzir o ciclo de geração e verificação com Gemini?”

Essa comparação demonstra o efeito da implementação. Depois, uma ablação entre modelos distingue o efeito do procedimento e o efeito da capacidade do gerador. Chegar a um percentual específico será um resultado observado, não uma condição para selecionar somente casos favoráveis.
