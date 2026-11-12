# AutoTutor CP 🚀

Plataforma unificada e inteligente para tutoria adaptativa e aprendizado em **Programação Competitiva** com **C++17**, combinando execução e validação formal de código (Mini-Judge local), tutoria pedagógica socrática guiada por LLMs (inspirada em *AutoCode*, *OI-Assistant* e *CODIGEN*) e interface interativa moderna.

---

## 🏛️ Arquitetura do Sistema

O projeto é estruturado em uma arquitetura desacoplada de alto desempenho:

- **Backend Core & API Gateway (`autotutor_cp/`)**:
  - Python 3.10+ (Starlette / FastAPI) rodando na porta `8000`.
  - Mini-Judge C++17 local com limites de tempo (TLE) e memória (MLE) em sandbox.
  - Motor de RAG para recuperação por essência matemática e pedagógica.
  - Orquestração de agentes de tutoria socrática e personas de estudo.
- **Frontend Web (`frontend/`)**:
  - Next.js 14 (App Router) + React 18 + Tailwind CSS rodando na porta `3000`.
  - Editor de código interativo, suporte a Markdown com LaTeX (KaTeX) e diagramas Mermaid.
- **Orquestrador de Serviços (`iniciar_sistema.sh`)**:
  - Script bash para gerenciar ciclo de vida, health check e logs dos serviços simultaneamente.

---

## 📋 Pré-requisitos

- **Python**: versão `3.10` ou superior.
- **Node.js**: versão `18.17` ou superior (com `npm`).
- **Compilador C++**: `g++` (GCC) com suporte a C++17 instalado no PATH do sistema.
  - Linux (Debian/Ubuntu): `sudo apt install build-essential`
  - macOS: `xcode-select --install` ou via Homebrew
  - Windows: MinGW-w64 configurado no PATH

---

## ⚙️ Configuração de Ambiente (.env)

O AutoTutor CP requer a configuração de credenciais de LLM para as funcionalidades socráticas do tutor.

> **Segurança:** O arquivo `.env` contém credenciais sensíveis e **nunca** deve ser versionado no Git. Ele já está protegido pelo `.gitignore`.

1. Navegue até o diretório do backend e copie o modelo de exemplo:
   ```bash
   cp autotutor_cp/.env.example autotutor_cp/.env
   ```

2. Edite o arquivo `autotutor_cp/.env` e defina suas credenciais:
   ```ini
   LLM_PROVIDER=Gemini
   LLM_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta
   LLM_API_KEY=sua_chave_gemini_aqui
   LLM_MODEL=gemini-3.1-flash-lite
   LLM_TEMPERATURE=0.3
   LLM_MAX_OUTPUT_TOKENS=4096
   ```

3. Ajuste as permissões do arquivo para leitura exclusiva do seu usuário:
   ```bash
   chmod 600 autotutor_cp/.env
   ```

---

## 🚀 Como Executar o Sistema

### Opção 1: Inicialização Unificada (Recomendado)

O script `iniciar_sistema.sh` realiza o health check automático e sobe tanto o backend (porta 8000) quanto o frontend (porta 3000):

```bash
# Iniciar o sistema completo
./iniciar_sistema.sh

# Para verificar o status dos serviços
./iniciar_sistema.sh --status

# Para acompanhar logs em tempo real
./iniciar_sistema.sh --logs

# Para encerrar todos os serviços
./iniciar_sistema.sh --stop
```

O aplicativo estará acessível em: **[http://localhost:3000](http://localhost:3000)**.

---

### Opção 2: Inicialização Manual (Desenvolvimento)

#### 1. Backend Python
```bash
cd autotutor_cp

# Criar e ativar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Iniciar API Server
python3 api_server.py
```
*API disponível em `http://localhost:8000` (docs em `/docs` ou `/openapi.json`).*

#### 2. Frontend Next.js
Em outro terminal:
```bash
cd frontend

# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm run dev
```
*Frontend disponível em `http://localhost:3000`.*

---

## 🧪 Testes Automatizados

Para rodar a suíte completa de testes unitários e de integração do backend:

```bash
cd autotutor_cp
source .venv/bin/activate
pytest tests/ -v
```

---

## 📁 Estrutura do Repositório

```text
.
├── autotutor_cp/             # Backend Python, Judge e Core IA
│   ├── api_server.py         # API REST Starlette/FastAPI (Porta 8000)
│   ├── app.py                # Interface Streamlit legada/alternativa
│   ├── config.py             # Configurações globais
│   ├── core/                 # Mini-Judge, RAG, Tutor Socrático e LLM Client
│   ├── data/                 # Bancos de problemas e sementes educacionais
│   ├── scripts/              # Utilitários e migrações
│   └── tests/                # Testes unitários e de integração
├── frontend/                 # Frontend Next.js 14 App Router (Porta 3000)
│   ├── src/                  # Componentes React, hooks, Monaco e layout
│   └── package.json          # Dependências do frontend
├── .agents/                  # Skills, agentes e automação de desenvolvimento
├── .ai-memory/               # Memória de handoff e especificações técnicas
├── iniciar_sistema.sh        # Orquestrador do ecossistema completo
├── .gitignore                # Proteção unificada de segredos e artefatos locais
└── README.md                 # Documentação principal
```

---

## 🔒 Segurança e Boas Práticas

- Arquivos `.env`, bancos de dados locais (`*.sqlite3`), diretórios temporários (`.runtime/`, `workspace/`) e dependências compiladas (`.venv/`, `node_modules/`, `.next/`) são rigorosamente bloqueados pelo `.gitignore`.
- Antes de submeter contribuições, certifique-se de não expor nenhuma chave privada ou arquivo binário de grande porte.
