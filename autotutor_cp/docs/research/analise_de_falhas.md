# Análise de falhas e ameaças à validade

## Observado

O piloto externo não apresentou falhas: três saídas passaram pelos testes disponíveis na primeira tentativa. Isso não mede taxa de falha generalizável. RAG citou soma de prefixos entre competências; sua necessidade neste contrato não foi revisada. Declarações de competências são registradas, sem prova de que o algoritmo é obrigatório. A revisão automática não certifica que o enunciado coincide semanticamente com o código.

A recuperação semântica trouxe um documento sobre pintura de arestas; o re-ranking trouxe Wavelet Tree. São candidatos a ruído, não erros formalmente anotados. A diversificação híbrida manteve os mesmos três documentos nesta consulta e o mesmo Jaccard agregado do híbrido (0,067); não houve redução observada. Recuperação por competências incluiu análise de complexidade e teve Jaccard menor (0,0448), o que não comprova melhor relevância pedagógica.

A indexação inicial levou cerca de 90,7 segundos junto da busca. Registrar essa operação como busca aquecida distorceria a comparação. Cache ocupou aproximadamente 2,2 MB, sem medir pico de RAM. Falta benchmark repetido com índice pronto e hardware caracterizado.

No desenvolvimento, o limite de processos aplicado antes de entrar no namespace impediu o fork do bubblewrap, pois contava processos/threads do usuário no host. A limitação foi movida para dentro do namespace com prlimit; o teste isolado voltou a passar. Um erro de número de placeholders no ledger foi corrigido antes da primeira requisição; não foi erro da API.

## Verificado por testes

O transporte simulado confirma interrupção após erros de cota/autenticação/parâmetros; saída sem schema é rejeitada antes da execução; exemplos inconsistentes são rejeitados; falta de sandbox bloqueia código; o sandbox impede leitura de arquivo do host, acesso à chave pelo ambiente e conexão externa. A revisão iterativa encaminha diagnóstico e para após uma correção. Esses testes verificam comportamento do software, sem medir qualidade do modelo.

## Limitações abertas

Não há avaliação humana, conjuntos de relevância revisados, estudantes reais, parâmetros BKT ajustados, estudo causal, comparação atual controlada com modelo local, testes oficiais externos ou provas formais. O grafo é editorial; alguns temas permanecem fora da agregação de nove tópicos do diagnóstico legado. O protótipo de 15 competências não corrige automaticamente todo o histórico da aplicação.

Os contratos restringem a matemática do problema: variedade narrativa não equivale a originalidade algorítmica. Passar 43 casos não demonstra que soluções triviais são inviáveis em todo o domínio. Não há taxa de acurácia comparável aos 98,7% do AutoCode.

O orçamento zero é uma política do cliente e da cota gratuita informada pelo usuário, não consulta independente ao faturamento do provedor. Não existe fallback pago automático. Para manter essa condição, não habilitar faturamento externo nem substituir a chave por credencial de projeto pago.

O isolamento atual é um protótipo local verificado, não certificação para exposição pública multiusuário. Mudanças do sistema operacional podem indisponibilizar user namespaces; nesse caso execução deve continuar bloqueada.
