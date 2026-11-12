#!/usr/bin/env bash
# ==============================================================================
# AutoTutor CP - Script de Inicialização e Orquestração do Sistema
#
# Arquitetura Unificada:
# 1. Backend REST API Gateway (Python Starlette/FastAPI) -> Porta 8000
# 2. Frontend Next.js 14 App Router (Tailwind + Monaco)  -> Porta 3000
#
# Uso:
#   ./iniciar_sistema.sh              -> Inicia os serviços com health check ativo
#   ./iniciar_sistema.sh --stop       -> Encerra todos os serviços e libera portas
#   ./iniciar_sistema.sh --status     -> Exibe o status atual dos serviços
#   ./iniciar_sistema.sh --logs       -> Acompanha os logs combinados em tempo real
#   ./iniciar_sistema.sh --no-browser -> Inicia sem abrir o navegador
# ==============================================================================

set -u

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/autotutor_cp"
FRONTEND_DIR="$PROJECT_DIR/frontend"

BACKEND_LOG="$PROJECT_DIR/.backend_api.log"
FRONTEND_LOG="$PROJECT_DIR/.next_frontend.log"

BACKEND_PORT=8000
FRONTEND_PORT=3000

# Paleta ANSI Sóbria e Funcional
CLR_RESET="\033[0m"
CLR_BOLD="\033[1m"
CLR_DIM="\033[2m"
CLR_BLUE="\033[38;5;39m"
CLR_GREEN="\033[38;5;42m"
CLR_YELLOW="\033[38;5;214m"
CLR_RED="\033[38;5;196m"
CLR_CYAN="\033[38;5;44m"
CLR_GRAY="\033[38;5;244m"

# ------------------------------------------------------------------------------
# Funções Auxiliares de Portas e Processos
# ------------------------------------------------------------------------------
liberar_porta() {
    local port="$1"
    local found=false

    # Verifica se porta está em uso
    if command -v fuser >/dev/null 2>&1; then
        if fuser "${port}/tcp" >/dev/null 2>&1; then
            found=true
            fuser -k -TERM "${port}/tcp" >/dev/null 2>&1 || true
            sleep 0.5
            if fuser "${port}/tcp" >/dev/null 2>&1; then
                fuser -k -KILL "${port}/tcp" >/dev/null 2>&1 || true
            fi
        fi
    elif command -v lsof >/dev/null 2>&1; then
        local pids
        pids=$(lsof -ti:"${port}" 2>/dev/null || true)
        if [ -n "$pids" ]; then
            found=true
            echo "$pids" | xargs -r kill -TERM 2>/dev/null || true
            sleep 0.5
            echo "$pids" | xargs -r kill -9 2>/dev/null || true
        fi
    fi

    # Garante liberação
    sleep 0.5
    return 0
}

parar_todos_os_servicos() {
    echo -e "${CLR_YELLOW}🛑 Encerrando instâncias ativas do AutoTutor CP...${CLR_RESET}"
    
    # Encerra processos registrados
    if [ -n "${BACKEND_PID:-}" ]; then
        kill -TERM "$BACKEND_PID" 2>/dev/null || true
    fi
    if [ -n "${FRONTEND_PID:-}" ]; then
        kill -TERM "$FRONTEND_PID" 2>/dev/null || true
    fi

    # Encerra filhos diretos caso existam
    pkill -f "api_server.py" 2>/dev/null || true
    pkill -f "next-server" 2>/dev/null || true

    # Libera portas 8000 e 3000
    liberar_porta "$BACKEND_PORT"
    liberar_porta "$FRONTEND_PORT"

    echo -e "${CLR_GREEN}✓ Portas ${BACKEND_PORT} e ${FRONTEND_PORT} liberadas com sucesso.${CLR_RESET}"
}

verificar_status_servicos() {
    echo -e "${CLR_BOLD}🔍 Verificando status dos serviços do AutoTutor CP:${CLR_RESET}"
    
    # 1. Backend Status
    local backend_http=""
    if command -v curl >/dev/null 2>&1; then
        backend_http=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:${BACKEND_PORT}/api/problems" 2>/dev/null || true)
    fi

    if [ "$backend_http" = "200" ]; then
        echo -e "   [${CLR_GREEN}● ONLINE${CLR_RESET}] Backend API Gateway  -> http://localhost:${BACKEND_PORT} (HTTP 200)"
    else
        echo -e "   [${CLR_RED}○ OFFLINE${CLR_RESET}] Backend API Gateway -> Porta ${BACKEND_PORT} não responde"
    fi

    # 2. Frontend Status
    local frontend_http=""
    if command -v curl >/dev/null 2>&1; then
        frontend_http=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:${FRONTEND_PORT}" 2>/dev/null || true)
    fi

    if [ -n "$frontend_http" ] && [ "$frontend_http" -ge 200 ] && [ "$frontend_http" -lt 400 ]; then
        echo -e "   [${CLR_GREEN}● ONLINE${CLR_RESET}] Frontend Next.js     -> http://localhost:${FRONTEND_PORT} (HTTP ${frontend_http})"
    else
        echo -e "   [${CLR_RED}○ OFFLINE${CLR_RESET}] Frontend Next.js    -> Porta ${FRONTEND_PORT} não responde"
    fi
}

# ------------------------------------------------------------------------------
# Roteamento de Parâmetros CLI
# ------------------------------------------------------------------------------
NO_BROWSER=false

for arg in "$@"; do
    case "$arg" in
        --stop|-k|--kill)
            parar_todos_os_servicos
            exit 0
            ;;
        --status|-s)
            verificar_status_servicos
            exit 0
            ;;
        --logs|-l)
            echo -e "${CLR_BOLD}Streaming de logs combinados (Ctrl+C para sair):${CLR_RESET}"
            tail -f "$BACKEND_LOG" "$FRONTEND_LOG" 2>/dev/null
            exit 0
            ;;
        --no-browser)
            NO_BROWSER=true
            ;;
        --help|-h)
            echo "Uso: ./iniciar_sistema.sh [opções]"
            echo "Opções:"
            echo "  (sem argumentos)   Inicia Backend e Frontend com health check ativo"
            echo "  --stop             Encerra todos os serviços em execução"
            echo "  --status           Mostra status das portas e endpoints"
            echo "  --logs             Acompanha saída dos logs em tempo real"
            echo "  --no-browser       Não abre o navegador automaticamente"
            exit 0
            ;;
    esac
done

# ------------------------------------------------------------------------------
# Verificação de Pré-Requisitos do Ambiente
# ------------------------------------------------------------------------------
echo -e "${CLR_BOLD}════════════════════════════════════════════════════════════════════════${CLR_RESET}"
echo -e "${CLR_BLUE}${CLR_BOLD}⚡ AutoTutor CP · Inicializador do Sistema Unificado${CLR_RESET}"
echo -e "${CLR_BOLD}════════════════════════════════════════════════════════════════════════${CLR_RESET}"

# 1. Python Venv
PYTHON_BIN=""
if [ -x "$BACKEND_DIR/.venv/bin/python" ]; then
    PYTHON_BIN="$BACKEND_DIR/.venv/bin/python"
elif [ -x "$PROJECT_DIR/.venv/bin/python" ]; then
    PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3)"
else
    echo -e "${CLR_RED}❌ Erro crítico: Python não encontrado no sistema.${CLR_RESET}"
    exit 1
fi

# 2. Node & NPM
if ! command -v npm >/dev/null 2>&1; then
    echo -e "${CLR_RED}❌ Erro crítico: 'npm' não está instalado no PATH.${CLR_RESET}"
    exit 1
fi

# 3. Frontend node_modules
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${CLR_YELLOW}⚠️  Dependências do frontend não encontradas. Executando npm install...${CLR_RESET}"
    (cd "$FRONTEND_DIR" && npm install)
fi

# 4. Libera portas antes da inicialização
echo -e "${CLR_GRAY}→ Liberando portas ${BACKEND_PORT} e ${FRONTEND_PORT} se ocupadas...${CLR_RESET}"
liberar_porta "$BACKEND_PORT"
liberar_porta "$FRONTEND_PORT"

# ------------------------------------------------------------------------------
# Rotina de Encerramento Gracioso (Ctrl+C ou SIGTERM)
# ------------------------------------------------------------------------------
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    echo ""
    echo -e "${CLR_YELLOW}🛑 Sinal de interrupção recebido. Encerrando serviços...${CLR_RESET}"
    parar_todos_os_servicos
    echo -e "${CLR_GREEN}✓ AutoTutor CP encerrado com segurança. Até logo!${CLR_RESET}"
    exit 0
}

trap cleanup SIGINT SIGTERM SIGHUP

# ------------------------------------------------------------------------------
# Inicialização dos Serviços
# ------------------------------------------------------------------------------

# 1. Inicia Backend Headless
echo -e "${CLR_BLUE}🚀 Iniciando Backend API Gateway na porta ${BACKEND_PORT}...${CLR_RESET}"
cd "$PROJECT_DIR"
PYTHONPATH="$BACKEND_DIR:$PROJECT_DIR" "$PYTHON_BIN" "$BACKEND_DIR/api_server.py" > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!

# 2. Inicia Frontend Next.js (utiliza build de produção pré-compilado para navegação ultrarrápida se existir)
echo -e "${CLR_BLUE}🚀 Iniciando Frontend Next.js na porta ${FRONTEND_PORT}...${CLR_RESET}"
cd "$FRONTEND_DIR"
if [ -d "$FRONTEND_DIR/.next" ]; then
    npm start -- -p "$FRONTEND_PORT" > "$FRONTEND_LOG" 2>&1 &
else
    npm run dev -- -p "$FRONTEND_PORT" > "$FRONTEND_LOG" 2>&1 &
fi
FRONTEND_PID=$!

cd "$PROJECT_DIR"

# ------------------------------------------------------------------------------
# Health Check Ativo & Confiável
# ------------------------------------------------------------------------------
echo -e "${CLR_GRAY}⏳ Aguardando prontidão dos serviços...${CLR_RESET}"

# A. Polling no Backend (até 15s)
backend_ready=false
for i in $(seq 1 30); do
    if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo -e "\n${CLR_RED}❌ Falha: O processo do Backend encerrou inesperadamente.${CLR_RESET}"
        echo -e "${CLR_RED}Últimas linhas de .backend_api.log:${CLR_RESET}"
        tail -n 25 "$BACKEND_LOG"
        cleanup
    fi

    if command -v curl >/dev/null 2>&1; then
        status_code=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:${BACKEND_PORT}/api/problems" 2>/dev/null || true)
        if [ "$status_code" = "200" ]; then
            backend_ready=true
            break
        fi
    else
        sleep 1
        backend_ready=true
        break
    fi
    sleep 0.5
done

if [ "$backend_ready" != "true" ]; then
    echo -e "\n${CLR_RED}❌ Timeout aguardando resposta do Backend na porta ${BACKEND_PORT}.${CLR_RESET}"
    tail -n 20 "$BACKEND_LOG"
    cleanup
fi
echo -e "   ${CLR_GREEN}✓ Backend REST API Gateway online em http://localhost:${BACKEND_PORT}${CLR_RESET}"

# B. Polling no Frontend (até 25s)
frontend_ready=false
for i in $(seq 1 50); do
    if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo -e "\n${CLR_RED}❌ Falha: O processo do Frontend encerrou inesperadamente.${CLR_RESET}"
        echo -e "${CLR_RED}Últimas linhas de .next_frontend.log:${CLR_RESET}"
        tail -n 25 "$FRONTEND_LOG"
        cleanup
    fi

    if command -v curl >/dev/null 2>&1; then
        status_code=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:${FRONTEND_PORT}" 2>/dev/null || true)
        if [ -n "$status_code" ] && [ "$status_code" -ge 200 ] && [ "$status_code" -lt 400 ]; then
            frontend_ready=true
            break
        fi
    else
        sleep 1
        frontend_ready=true
        break
    fi
    sleep 0.5
done

if [ "$frontend_ready" != "true" ]; then
    echo -e "\n${CLR_RED}❌ Timeout aguardando resposta do Frontend na porta ${FRONTEND_PORT}.${CLR_RESET}"
    tail -n 20 "$FRONTEND_LOG"
    cleanup
fi
echo -e "   ${CLR_GREEN}✓ Frontend Next.js pronto em http://localhost:${FRONTEND_PORT}${CLR_RESET}"

# ------------------------------------------------------------------------------
# Painel Informativo Final
# ------------------------------------------------------------------------------
echo ""
echo -e "${CLR_BOLD}════════════════════════════════════════════════════════════════════════${CLR_RESET}"
echo -e "${CLR_GREEN}${CLR_BOLD}✨ AutoTutor CP · Sistema 100% Operacional!${CLR_RESET}"
echo -e "${CLR_BOLD}════════════════════════════════════════════════════════════════════════${CLR_RESET}"
echo ""
echo -e "${CLR_BOLD}🌐 APLICAÇÃO (Frontend Next.js):${CLR_RESET}"
echo -e "   • Início & Dashboard:            ${CLR_BLUE}http://localhost:${FRONTEND_PORT}${CLR_RESET}"
echo -e "   • Arena de Prática & Juiz:       ${CLR_BLUE}http://localhost:${FRONTEND_PORT}/workspace${CLR_RESET}"
echo -e "   • Quadro Branco & Estúdio DP:    ${CLR_BLUE}http://localhost:${FRONTEND_PORT}/whiteboard${CLR_RESET}"
echo -e "   • Laboratório Técnico:           ${CLR_BLUE}http://localhost:${FRONTEND_PORT}/lab${CLR_RESET}"
echo -e "   • Repetição Espaçada & Memória:  ${CLR_BLUE}http://localhost:${FRONTEND_PORT}/repetition${CLR_RESET}"
echo -e "   • Biblioteca & Apostilas:        ${CLR_BLUE}http://localhost:${FRONTEND_PORT}/biblioteca${CLR_RESET}"
echo ""
echo -e "${CLR_BOLD}⚙️  BACKEND HEADLESS (REST API Gateway):${CLR_RESET}"
echo -e "   • API Base:                      ${CLR_GRAY}http://localhost:${BACKEND_PORT}${CLR_RESET}"
echo -e "   • Catálogo de Problemas:         ${CLR_GRAY}http://localhost:${BACKEND_PORT}/api/problems${CLR_RESET}"
echo -e "   • Configurações & Status IA:     ${CLR_GRAY}http://localhost:${BACKEND_PORT}/api/config/llm${CLR_RESET}"
echo ""
echo -e "${CLR_BOLD}📋 Visualização de Logs:${CLR_RESET}"
echo -e "   Backend:  ${CLR_DIM}tail -f .backend_api.log${CLR_RESET}"
echo -e "   Frontend: ${CLR_DIM}tail -f .next_frontend.log${CLR_RESET}"
echo -e "${CLR_BOLD}════════════════════════════════════════════════════════════════════════${CLR_RESET}"
echo -e "${CLR_YELLOW}Pressione [Ctrl + C] para encerrar todos os serviços a qualquer momento.${CLR_RESET}"
echo ""

# ------------------------------------------------------------------------------
# Abertura Automática no Navegador (se ambiente gráfico detectado)
# ------------------------------------------------------------------------------
if [ "$NO_BROWSER" = "false" ] && { [ -n "${DISPLAY:-}" ] || [ -n "${WAYLAND_DISPLAY:-}" ]; }; then
    if command -v xdg-open >/dev/null 2>&1; then
        xdg-open "http://localhost:${FRONTEND_PORT}" >/dev/null 2>&1 &
    fi
fi

# ------------------------------------------------------------------------------
# Loop de Supervisão de Processos
# ------------------------------------------------------------------------------
while true; do
    if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo -e "\n${CLR_RED}⚠️  O Backend parou inesperadamente. Encerrando o sistema...${CLR_RESET}"
        tail -n 15 "$BACKEND_LOG"
        cleanup
    fi

    if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo -e "\n${CLR_RED}⚠️  O Frontend parou inesperadamente. Encerrando o sistema...${CLR_RESET}"
        tail -n 15 "$FRONTEND_LOG"
        cleanup
    fi

    sleep 2
done
