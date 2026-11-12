# Automação de desenvolvimento com Gemini e AntiGravity

O ciclo usa chats separados com quatro papéis:

1. **Analista**: escopo, riscos e critérios de aceitação.
2. **Implementador**: proposta por arquivo e testes necessários.
3. **Revisor**: procura regressões, custo, privacidade e falhas pedagógicas.
4. **Coordenador**: transforma a revisão em uma próxima tarefa objetiva.

A resposta de cada papel é a entrada do próximo. A saída do coordenador torna-
se a tarefa do ciclo seguinte. Nenhum papel edita automaticamente o projeto:
isso impede que uma resposta de modelo seja aplicada sem revisão e testes.

## Executar

Primeiro execute uma simulação local, que não usa a API:

```bash
.venv/bin/python scripts/gemini_development_cycle.py \
  --task "Melhorar a aula de BFS para iniciantes" --cycles 1
```

Para chamar o Gemini configurado na `.env`, use `--live`. A execução é
limitada a 12 ciclos; cada ciclo possui quatro chamadas e respeita um intervalo
entre elas. Use um objetivo específico, execute poucos ciclos e revise os
arquivos em `.runtime/development_cycles/`.

```bash
.venv/bin/python scripts/gemini_development_cycle.py \
  --task "Corrigir a recuperação de memória de estudos" \
  --cycles 1 --live --append-handoff
```

`--append-handoff` acrescenta apenas a proposta final em
`.ai-memory/handoffs/gemini-ciclos.md`. Os transcripts detalhados ficam no
diretório da execução e não devem ser publicados sem revisão.

## Skills e memória

Antes de cada papel, o orquestrador fornece a memória de projeto e pede que o
papel siga sua responsabilidade. As skills reais do Codex continuam sendo
executadas pelo Codex quando ele implementa a alteração; o Gemini recebe as
restrições e contratos correspondentes, não uma falsa alegação de que executou
uma skill local.

O hook de encerramento em `.cursor/hooks.json` só registra que a sessão acabou;
ele não envia nada à API nem captura o transcript bruto. Assim, o próximo chat
encontra os handoffs sem expor conversas privadas.

## Executar com AntiGravity

O projeto possui quatro agentes nativos em `.agents/agents/`: `autotutor-analista`,
`autotutor-implementador`, `autotutor-revisor` e `autotutor-coordenador`. O
AntiGravity descobre agentes de projeto nesse local. O orquestrador usa o modo
headless `agy -p`, com um chat independente por papel; a resposta de cada chat
é passada ao próximo papel.

Depois de instalar e autenticar o AntiGravity CLI, primeiro simule:

```bash
.venv/bin/python scripts/antigravity_development_cycle.py \
  --task "Revisar o fluxo de memória de estudos" --cycles 1
```

Para executar os agentes reais, use:

```bash
.venv/bin/python scripts/antigravity_development_cycle.py \
  --task "Revisar o fluxo de memória de estudos" \
  --cycles 1 --live --append-handoff
```

O ciclo não concede modo perigoso ao AntiGravity e não aplica arquivos sozinho.
Ele salva a rastreabilidade em `.runtime/development_cycles/` e, quando pedido,
acrescenta somente o handoff final à AI Memory. O modo headless e os agentes de
projeto seguem a documentação oficial do [AntiGravity CLI](https://antigravity.google/docs/cli/headless/) e de [agentes personalizados](https://antigravity.google/docs/cli/commands/agents/).
