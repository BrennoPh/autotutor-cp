# RFC: Validação e Execução de Código C++ no Quadro Branco Algorítmico

**Status:** APROVADO PARA IMPLEMENTAÇÃO  
**Autor:** software-architect-planner  
**Componente:** `autotutor_cp/core/whiteboard_engine.py` e `autotutor_cp/core/cpp_whiteboard_executor.py`  
**Data:** 2026-11-06  

---

## 1. Contexto e Problema
O Quadro Branco Algorítmico do AutoTutor CP (`/whiteboard`) permitia a simulação didática de grafos (geração de fita de passos/snapshots), mas usava apenas uma heurística textual frágil em Python (`any(k in code_lower for k in ('bfs', 'queue'))`).
Se o aluno digitasse código C++ real, texto arbitrário, anotações ou código com erro de sintaxe, o sistema não diferenciava se aquilo era de fato código C++ válido para execução ou apenas texto descritivo.

## 2. Requisitos e Objetivos
1. **Classificação Rigorosa de Código:**
   - Detectar se a entrada é texto comum/anotações (`not_code`).
   - Detectar se é código C++ com erro sintático (`syntax_error`).
   - Detectar se é código C++ compilável e executável (`compiled`).
2. **Harness C++ Flexível:**
   - Suportar tanto programas completos com `int main()` quanto funções avulsas de maratona (ex.: `void dfs(...)` ou `void bfs(...)`), injetando harness compatível quando necessário.
3. **Segurança e Isolamento:**
   - Compilação isolada com `g++ -O2 -std=c++17 -Wall`.
   - Limite estrito de tempo de compilação (3s) e de execução (1.5s).
   - Bloqueio ou captura de TLE/RE.
4. **Geração da Fita de Simulação (Tape):**
   - Extrair a fita de execução (`tape`) sincronizada com os nós e arestas desenhados no quadro.
   - Retorno estruturado e retrocompatível com a interface do Next.js.

## 3. Contrato da API (`POST /api/whiteboard/simulate`)

### Entrada (Request Payload):
```json
{
  "code_text": "string (código C++ ou anotação)",
  "nodes": [{"id": "1", "label": "1"}, {"id": "2", "label": "2"}],
  "edges": [{"from": "1", "to": "2", "directed": true}],
  "start_node": "1",
  "max_steps": 500
}
```

### Saída (Response Payload):
```json
{
  "is_valid_cpp": true,
  "compilation_status": "compiled | syntax_error | not_code",
  "compiler_message": "string detalhando o status ou erro",
  "execution_output": "string stdout gerado",
  "tape": [
    {
      "step_index": 0,
      "line": 1,
      "active_node": "1",
      "active_edge": null,
      "node_states": {"1": "visiting", "2": "unvisited"},
      "edge_states": {"1-2": "normal"},
      "queue": ["1"],
      "call_stack": [],
      "log": "Nó 1 adicionado na fila."
    }
  ],
  "total_steps": 1
}
```

## 4. Critérios de Aceite para o QA
- [AC-1] Texto puro em português sem palavras-chave de C++ é classificado como `not_code` (`is_valid_cpp: false`) com mensagem informativa.
- [AC-2] Código com `int x = ;` ou erro de sintaxe C++ é classificado como `syntax_error` com a mensagem exata do `g++`.
- [AC-3] Código C++ válido com `main()` e grafo compilam e geram a fita de execução com veredito `compiled`.
- [AC-4] Função C++ avulsa (ex.: `void bfs(int s, ...)` sem `main`) recebe auto-harness, compila e gera a fita de execução.
- [AC-5] Código que entra em loop infinito (while true) é interrompido pelo timeout sem travar o servidor.
