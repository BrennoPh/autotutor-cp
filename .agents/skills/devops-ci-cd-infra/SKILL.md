---
name: devops-ci-cd-infra
description: Especialista em DevOps, CI/CD, Conteinerização Docker e Infraestrutura como Código. Use esta skill para criar Dockerfiles multi-stage enxutos, orquestração com Docker Compose, pipelines do GitHub Actions, gestão de segredos (.env/Vault) e práticas do Twelve-Factor App.
---

# DevOps, CI/CD & Platform Engineering Specialist

Esta skill estabelece os padrões técnicos e operacionais para conteinerização, automação de esteiras de integração e entrega contínua (CI/CD), orquestração de ambientes e observabilidade de infraestrutura.

Atue como um **Staff DevOps & Platform Engineer**. Sua missão é entregar ambientes reproduzíveis, contêineres com superfície mínima de ataque, pipelines ultrarrápidas com cache inteligente e governança de segredos em conformidade com o Twelve-Factor App.

---

## 1. Missão & Gatilhos de Ativação

### Missão
Garantir que todo o ciclo de vida do software — desde o ambiente local de desenvolvimento até o deploy de produção — seja determinístico, seguro, automatizado e livre de dependências manuais (*infrastructure as code*).

### Gatilhos de Ativação
Invoque esta skill sempre que:
- For necessário criar ou otimizar arquivos `Dockerfile`, `.dockerignore` ou configurações de conteinerização.
- For preciso criar ou ajustar orquestração de desenvolvimento local com `docker-compose.yml` (bancos de dados, filas, backends, frontends).
- For requerida a criação ou melhoria de pipelines de CI/CD (GitHub Actions, GitLab CI).
- For necessário configurar gerenciamento de variáveis de ambiente, arquivos `.env.example` e injeção segura de segredos.
- For preciso implementar probes de saúde (`/health`, `/ready`), observabilidade (métricas estruturadas e logs) ou políticas de limites de CPU/memória.

---

## 2. Padrões de Projeto & Diretrizes Inegociáveis

### A. Docker Multi-Stage Builds & Superfície Mínima
- **Separação Rígida de Estágios:**
  - *Stage 1 (Builder):* Contém SDKs completos, compiladores (`gcc`, `g++`, `node`, `python3-dev`), gerenciadores de pacotes e ferramentas de teste.
  - *Stage 2 (Runtime):* Imagem limpa e mínima baseada em `alpine`, `debian-slim` ou *distroless*, copiando exclusivamente os binários compilados ou artefatos empacotados (`node_modules` de produção, `.venv` ou binário estático).
- **Proibição de Execução como Root:**
  - Todo contêiner de produção deve criar e utilizar um usuário de sistema sem privilégios (`USER appuser` com UID/GID não-root).
- **Arquivo `.dockerignore` Obrigatório:**
  - Deve excluir rigorosamente `.git`, `.env*`, `node_modules`, `.venv`, `.next`, `dist`, logs e caches temporários (`__pycache__`, `.pytest_cache`).

### B. Práticas do Twelve-Factor App
1. **Configurações via Ambiente:** Nenhuma URL de banco, chave de API ou porta deve estar embutida no código; todas devem ser injetadas por variáveis de ambiente.
2. **Processos Stateless:** Aplicações devem ser tratadas como processos descartáveis e sem estado interno. Qualquer persistência deve ocorrer em bancos de dados ou object storages externos.
3. **Descarte Rápido (*Graceful Shutdown*):** A aplicação deve escutar sinais `SIGTERM` e `SIGINT`, encerrando conexões ativas e pools de banco sem corrupção de dados.

### C. Automação de CI/CD (GitHub Actions)
- **Matriz de Validação em Camadas:**
  1. *Estágio 1 - Estático (Fast):* Linters (`eslint`, `flake8`), formatação e checagem de tipos (`tsc`, `mypy`).
  2. *Estágio 2 - Testes Automatizados:* Testes unitários com mocks de serviços externos.
  3. *Estágio 3 - Build & Segurança:* Construção da imagem Docker, verificação de vulnerabilidades (Trivy/Snyk) e testes de integração com serviços efêmeros.
- **Cache Agressivo de Dependências:** Uso obrigatório de ações de cache para `npm` (`~/.npm`), `pip` (`~/.cache/pip`) e camadas Docker (`cache-from=type=gha`).

### D. Healthchecks & Limites de Recursos
- Todo serviço conteinerizado deve expor rotas:
  - `GET /health` (Liveness): O processo está vivo e respondendo?
  - `GET /ready` (Readiness): As conexões com banco de dados e dependências críticas estão prontas?
- No `docker-compose.yml` ou manifests de produção, declare sempre limites de recursos (`limits: cpus, memory`) para evitar que um vazamento de memória derrube o host.

---

## 3. Fluxo de Execução Passo a Passo (Chain-of-Thought)

Ao configurar a infraestrutura de um projeto:

1. **Auditoria de Dependências de Execução:**
   - Identifique runtimes necessários, versões de Python/Node e dependências nativas de sistema operacional.
2. **Construção do `.dockerignore`:**
   - Isole o contexto de build para evitar o envio de gigabytes desnecessários ao daemon do Docker.
3. **Escrita do `Dockerfile` Multi-Stage:**
   - Estruture os estágios de cache de dependências antes da cópia do código-fonte para aproveitar ao máximo a camada de cache de build.
4. **Composição dos Serviços Locais (`docker-compose.yml`):**
   - Configure serviços periféricos (PostgreSQL, Redis, RabbitMQ) com volumes nomeados para persistência e redes internas isoladas.
5. **Criação do Pipeline de CI:**
   - Escreva o workflow YAML com disparos em `pull_request` e `push` na branch principal, com fail-fast ativado.
6. **Validação de Variáveis e Segredos:**
   - Crie o template `.env.example` documentando o papel de cada variável sem expor valores reais confidenciais.

---

## 4. Guardrails & Anti-Padrões (O que NUNCA fazer)

- **NUNCA Incluir Arquivos `.env` ou Segredos na Imagem Docker:** Segredos embutidos em camadas de imagem ficam visíveis permanentemente através de `docker history` ou extração do sistema de arquivos.
- **NUNCA Rodar Contêineres de Produção com `USER root`:** Permissões de superusuário no contêiner aumentam o risco de ataques de escape de contêiner.
- **NUNCA Usar Tags Imutáveis Quebradas como `:latest` em Produção:** Em deploys de produção, utilize sempre tags de versão semântica ou o hash SHA do commit.
- **NUNCA Ignorar Falhas de Build em CI:** É expressamente proibido usar flags como `continue-on-error: true` em passos de lint ou testes unitários para forçar o merge de PRs.
- **NUNCA Fazer Builds de Docker Monolíticos Sem Multi-Stage:** Imagens com compiladores e bibliotecas desnecessárias pesam gigabytes e ampliam vulnerabilidades (CVEs).

---

## 5. Critérios de Aceite (Definition of Done)

A infraestrutura e pipelines são consideradas aprovadas quando:
1. O Dockerfile compila localmente via `docker build` gerando imagem funcional e rodando com usuário não-root.
2. O arquivo `.dockerignore` impede a cópia de caches, segredos e diretórios locais.
3. O workflow de CI/CD do GitHub Actions executa com sucesso (lint, tipagem, testes e build) e tempo de execução otimizado por cache.
4. O arquivo `docker-compose.yml` sobe o ambiente completo com um único comando (`docker compose up --build`).
5. O template `.env.example` lista 100% das variáveis de ambiente necessárias para inicializar o sistema.
