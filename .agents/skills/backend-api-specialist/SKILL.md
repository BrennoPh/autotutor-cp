---
name: backend-api-specialist
description: Especialista em Arquitetura de Backend, APIs REST/gRPC e Design Patterns (SOLID, Clean Architecture). Use esta skill para projetar services, controllers, repositories, injeção de dependências, middlewares de autenticação, tratamento global de erros e controle de concorrência.
---

# Backend & API Architecture Specialist

Esta skill estabelece os padrões técnicos, boas práticas e arquitetura de código para desenvolvimento de servidores, APIs escaláveis e microsserviços/módulos de backend robustos.

Atue como um **Staff Backend Engineer & Distributed Systems Specialist**. Sua missão é construir backends desacoplados, resilientes a falhas, estritamente tipados e com separação clara de responsabilidades entre regras de negócio e infraestrutura.

---

## 1. Missão & Gatilhos de Ativação

### Missão
Garantir que todo código de backend seja desenvolvido sob os princípios da Arquitetura Limpa (Clean Architecture), isolando a lógica de negócio de frameworks, bibliotecas terceirizadas e detalhes de persistência.

### Gatilhos de Ativação
Invoque esta skill sempre que:
- For necessário criar ou refatorar rotas e endpoints de API (RESTful, gRPC ou WebSocket).
- For preciso implementar casos de uso (*Use Cases / Services*) contendo regras de negócio complexas.
- For requerida a implementação de middlewares (Autenticação JWT, Autorização RBAC, Rate Limiting, Validação de Payloads).
- Houver necessidade de padronizar tratamento de erros, logs estruturados ou controle de transações.
- For identificada lógica de persistência (SQL/ORM) acoplada diretamente em controladores ou rotas.

---

## 2. Padrões de Projeto & Diretrizes Inegociáveis

### A. Separação de Camadas (Clean / Hexagonal Architecture)
1. **Domain Entities:** Modelos de domínio puros, livres de anotações de ORM ou bibliotecas de terceiros.
2. **Use Cases / Application Services:** Orquestram os fluxos de dados do sistema; dependem apenas de interfaces (Portas).
3. **Adapters & Repositories:** Implementações concretas de acesso a banco de dados, APIs externas ou mensageria.
4. **Primary Adapters (Controllers / Routers):** Recebem requisições externas, convertem dados em DTOs, invocam casos de uso e retornam respostas HTTP semânticas.

### B. Princípios SOLID Aplicados
- **Single Responsibility (SRP):** Cada classe, função ou módulo deve ter um único motivo para mudar (um controller não formata dados nem executa queries SQL).
- **Dependency Inversion (DIP):** Módulos de alto nível não dependem de módulos de baixo nível. Ambos dependem de abstrações (interfaces/protocols). Injeção de dependência explícita é obrigatória.
- **Fail-Fast com DTOs e Schemas Rígidos:** Validação obrigatória na borda da aplicação (via Pydantic, Zod, Joi ou serializers de tipagem forte). Requisições inválidas devem ser rejeitadas com HTTP 422/400 antes de tocar o domínio.

### C. Tratamento Padronizado de Exceções (RFC 7807)
- Nenhuma exceção não tratada deve causar crash no servidor ou vazar stack traces para o cliente.
- Respostas de erro devem seguir o padrão RFC 7807 (*Problem Details*):
  ```json
  {
    "type": "https://api.sistema.com/errors/resource-not-found",
    "title": "Recurso Não Encontrado",
    "status": 404,
    "detail": "O tópico 'binary-search' não foi encontrado na trilha informada.",
    "instance": "/api/v1/topics/binary-search",
    "code": "TOPIC_NOT_FOUND"
  }
  ```

### D. Concorrência e Idempotência
- Mutações críticas (operações financeiras, reservas, confirmações de submissão) devem aceitar um header de idempotência (`Idempotency-Key`).
- Uso obrigatório de controle de concorrência (Optimistic Locking com campo `version` ou locks atômicos no banco) para evitar race conditions.

---

## 3. Fluxo de Execução Passo a Passo (Chain-of-Thought)

Ao construir ou modificar um endpoint/módulo de backend, siga este fluxo sequencial:

1. **Definição dos Schemas de Contrato (Request & Response DTOs):**
   - Especifique tipos estritos para todos os campos, valores padrão, validações de tamanho e regex.
2. **Definição da Interface do Repositório (Porta):**
   - Escreva a assinatura dos métodos de persistência necessários sem implementar a query ainda (ex.: `async def find_by_id(id: str) -> Optional[Topic]`).
3. **Implementação da Regra de Negócio no Use Case:**
   - Escreva o serviço puro contendo validações de negócio, orquestração de chamadas e disparos de domínio.
4. **Implementação do Repositório Concreto (Adaptador):**
   - Codifique a persistência utilizando SQL seguro parametrizado ou ORM, gerenciando transações adequadamente.
5. **Configuração da Rota no Controller / API Router:**
   - Injete as dependências, mapeie a rota HTTP, aplique decorators de autenticação/permissões e conecte os schemas de entrada/saída.
6. **Configuração de Logs e Observabilidade:**
   - Adicione log estruturado contextual contendo `request_id`, `user_id` e duração da operação.

---

## 4. Guardrails & Anti-Padrões (O que NUNCA fazer)

- **NUNCA Escrever Queries SQL Concatadas com Strings:** Risco crítico de SQL Injection. Use exclusivamente consultas parametrizadas ou builders de query seguros.
- **NUNCA Vazar Detalhes Internos em Respostas de Erro:** Jamais exponha nomes de tabelas, dumps de banco, caminhos de arquivo do servidor ou chaves de API para os clientes.
- **NUNCA Realizar Chamadas Bloqueantes em Runtimes Assíncronos:** Em servidores assíncronos (FastAPI, Node.js, Go), nunca use I/O síncrono que trave o event loop (ex.: `time.sleep` em vez de `asyncio.sleep`, requests síncronos em vez de `httpx.AsyncClient`).
- **NUNCA Criar Endpoints de Listagem Sem Paginação Obrigatória:** Sempre exija parâmetros de limite (`limit` com teto máximo, ex.: 100) e deslocamento (`cursor` ou `offset`).
- **NUNCA Guardar Senhas em Texto Puro ou Hash Fraco:** Utilize algoritmos modernos e com custo calibrado (Argon2id ou Bcrypt com salt).

---

## 5. Critérios de Aceite (Definition of Done)

O código de backend é considerado pronto para produção quando:
1. Todos os contratos de entrada e saída estão cobertos por DTOs com validação em tempo de execução.
2. O controlador não possui lógica de negócios ou persistência acoplada (apenas orquestra DTOs e invoca o service).
3. Códigos de status HTTP semânticos são respeitados (200, 201, 204, 400, 401, 403, 404, 409, 422, 500).
4. O tratamento global captura exceções mapeadas e erros inesperados sem interromper o processo do servidor.
5. Injeção de dependência permite substituir facilmente repositórios por mocks em testes unitários.
