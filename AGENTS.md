# Protocolo de Integração Contínua entre Chats (SDLC Multi-Agente)

Este arquivo é carregado automaticamente em **TODOS os chats e sessões do Antigravity** neste projeto.

---

## 1. Diretriz de Barramento Compartilhado (State Bus)
Todos os chats (`Planejador`, `Back_End`, `Testes`, `Front_End`, `Prompts`) operam conectados ao **Barramento de Estado Compartilhado**:
- **Arquivo de Estado Vivo:** `.ai-memory/handoffs/pipeline_state.json`
- **Memória de Longo Prazo:** `.ai-memory/handoffs/projeto-atual.md`

Ao iniciar ou continuar qualquer tarefa, você **DEVE**:
1. Ler `.ai-memory/handoffs/pipeline_state.json` para saber em que estágio o pipeline está e qual foi o último output gerado pelo chat anterior.
2. Assumir sua responsabilidade de acordo com a sua persona/chat.
3. Ao concluir suas alterações, atualizar `.ai-memory/handoffs/pipeline_state.json` com seu output e definir o próximo estágio.

---

## 2. Regras de Transição de Estado

### Se você estiver no chat `Planejador` (`software-architect-planner`):
- **Input:** Requisito do usuário ou relatório de falha arquitetural do QA.
- **Ação:** Cria a RFC técnica com contratos, models e critérios de aceite. Salva em `.ai-memory/handoffs/spec-atual.md`.
- **Output:** Atualiza `pipeline_state.json` com:
  - `"active_stage": "BACKEND"`
  - `"last_output_by": "Planejador"`
  - `"next_action": "Implementar rotas e models definidos em spec-atual.md"`

### Se você estiver no chat `Back_End` (`backend-api-specialist`):
- **Input:** Especificação em `.ai-memory/handoffs/spec-atual.md` ou relatório de erro do QA.
- **Ação:** Implementa o código em Python (FastAPI/Starlette/Core), respeitando contratos e limites assintóticos.
- **Output:** Atualiza `pipeline_state.json` com:
  - `"active_stage": "QA"`
  - `"last_output_by": "Back_End"`
  - `"modified_files": [...]`
  - `"next_action": "Executar e criar suíte de testes automatizados"`

### Se você estiver no chat `Testes` (`project-qa-testing`):
- **Input:** Arquivos modificados pelo Backend e critérios da spec.
- **Ação:** Executa `python3 -m pytest <test_path> -v`.
- **Decisão no Loop:**
  - **Se houver falhas:** Atualiza `pipeline_state.json` com `"active_stage": "BACKEND"`, `"status": "FAILED"` e anexa os logs de erro para que o Back_End corrija imediatamente.
  - **Se 100% dos testes passarem:** Atualiza `pipeline_state.json` com `"active_stage": "FRONTEND"` (ou `"DONE"`), consolida o handoff em `.ai-memory/handoffs/projeto-atual.md`.

### Se você estiver no chat `Front_End` (`frontend-ux-specialist`):
- **Input:** Endpoints testados e especificação da feature.
- **Ação:** Implementa componentes React/Next.js 14, hooks e serviços de API.
- **Output:** Atualiza `pipeline_state.json` com `"active_stage": "DONE"`.

---

## 3. Formato do `pipeline_state.json`
```json
{
  "current_feature": "Nome da funcionalidade",
  "active_stage": "PLANNER | BACKEND | QA | FRONTEND | DONE",
  "status": "IN_PROGRESS | FAILED | APPROVED",
  "last_output_by": "Nome da persona",
  "updated_at": "ISO-8601",
  "artifacts": {
    "spec_file": ".ai-memory/handoffs/spec-atual.md",
    "modified_files": [],
    "test_file": "",
    "test_status": "PASSED | FAILED",
    "feedback": ""
  },
  "next_action": "Instrução clara para a próxima persona"
}
```

---

## 4. REGRA DE OURO: ZERO COPY-PASTE (Execução 100% Autônoma)
- **É ESTRITAMENTE PROIBIDO** dizer ao usuário frases como: *"Copie e cole o bloco abaixo no chat de Front-End/Back-End/Testes"*.
- O usuário **NÃO DEVE** copiar nem colar texto entre chats.
- Toda a comunicação entre as etapas deve ser gravada no barramento (`pipeline_state.json` e `spec-atual.md`).
- O Daemon autônomo em segundo plano consome esse arquivo e avança o ciclo automaticamente.

