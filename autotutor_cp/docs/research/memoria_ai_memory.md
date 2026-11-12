# Memória de longo prazo do AutoTutor

## Objetivo

O AutoTutor preserva contexto de estudo individual entre sessões sem treinar o
modelo, sem alterar pesos e sem chamar uma API em segundo plano. A memória é
uma evidência de atividades registradas, não uma certificação de domínio.

## Técnica aplicada

A implementação adapta o fluxo `capture → consolidate → recall → handoff` do
projeto [ai-memory](https://github.com/akitaonrails/ai-memory):

1. **Captura**: a criação de material, problema, questionário, submissão,
   mudança de estado da biblioteca e interação de IA cria uma observação
   sanitizada. Código de submissão, solução de referência e credenciais não
   são copiados para o índice recuperável.
2. **Consolidação**: as observações produzem `memoria.md` e `handoff.md` por
   perfil. São páginas Markdown legíveis e portáveis; a consolidação é local e
   determinística, sem LLM.
3. **Recuperação**: um índice SQLite/FTS derivado localiza as páginas mais
   relacionadas ao novo pedido. O contexto inserido no prompt é limitado e
   traz uma política explícita: leitura e conteúdo gerado não provam domínio.
4. **Handoff/exportação**: o aluno baixa JSON completo ou um pacote Markdown
   para continuar em outro sistema. A exportação inclui páginas, eventos e
   trilha de auditoria.

As páginas em `data/memory/<perfil>/` são a fonte de verdade operacional. O
índice SQLite pode ser recriado a partir delas; ele existe apenas para busca e
não substitui a exportação humana legível.

## Privacidade e limites

A memória é vinculada ao `profile_id`; consultas e exportações usam esse
escopo. Credenciais são removidas antes da captura. O app preserva no banco os
artefatos privados existentes, mas a memória guarda metadados e intenções de
estudo em vez de duplicar códigos ou soluções de referência. O professor não
obtém acesso a essa memória por padrão.

O sistema também não faz uma inferência do tipo “o aluno domina DP porque
abriu um material”. Evidências de questionários e vereditos continuam sendo a
base para análises de aprendizagem.
