#!/bin/bash

# Script para verificar se já existe PostgreSQL ativo no Replit

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}=== VERIFICANDO POSTGRESQL EXISTENTE NO REPLIT ===${NC}"
echo ""

# 1. Verificar se PostgreSQL está instalado
echo -e "${YELLOW}1. Verificando instalação do PostgreSQL...${NC}"
if command -v postgres &> /dev/null; then
    echo -e "   ${GREEN}✓ PostgreSQL encontrado${NC}"
    postgres --version
    postgres_path=$(which postgres)
    echo "   Localização: $postgres_path"
else
    echo -e "   ${RED}✗ PostgreSQL não instalado${NC}"
fi

if command -v psql &> /dev/null; then
    echo -e "   ${GREEN}✓ psql encontrado${NC}"
    psql --version
else
    echo -e "   ${RED}✗ psql não encontrado${NC}"
fi

echo ""

# 2. Verificar processos PostgreSQL em execução
echo -e "${YELLOW}2. Verificando processos PostgreSQL ativos...${NC}"
postgres_processes=$(ps aux | grep postgres | grep -v grep || true)
if [[ -n "$postgres_processes" ]]; then
    echo -e "   ${GREEN}✓ Processos PostgreSQL encontrados:${NC}"
    echo "$postgres_processes" | while read line; do
        echo "   $line"
    done
else
    echo -e "   ${RED}✗ Nenhum processo PostgreSQL ativo${NC}"
fi

echo ""

# 3. Verificar portas PostgreSQL em uso
echo -e "${YELLOW}3. Verificando portas PostgreSQL (5432, 5433)...${NC}"
for port in 5432 5433; do
    if netstat -tuln 2>/dev/null | grep ":$port " > /dev/null; then
        echo -e "   ${GREEN}✓ Porta $port em uso${NC}"
        netstat -tuln | grep ":$port "
    else
        echo -e "   ${RED}✗ Porta $port livre${NC}"
    fi
done

echo ""

# 4. Verificar diretórios de dados PostgreSQL comuns
echo -e "${YELLOW}4. Verificando diretórios de dados...${NC}"
data_dirs=(
    "$HOME/postgres_data"
    "$HOME/.postgres"
    "/tmp/postgres"
    "/var/lib/postgresql"
    "$HOME/postgresql"
)

for dir in "${data_dirs[@]}"; do
    if [[ -d "$dir" ]]; then
        echo -e "   ${GREEN}✓ Encontrado: $dir${NC}"
        ls -la "$dir" | head -5
        
        # Verificar se é um diretório de dados PostgreSQL válido
        if [[ -f "$dir/PG_VERSION" ]]; then
            pg_version=$(cat "$dir/PG_VERSION")
            echo -e "     ${CYAN}PostgreSQL versão: $pg_version${NC}"
            
            # Verificar se o cluster está ativo
            if [[ -f "$dir/postmaster.pid" ]]; then
                echo -e "     ${GREEN}✓ Cluster ativo (postmaster.pid existe)${NC}"
                pid=$(head -1 "$dir/postmaster.pid")
                echo "     PID do processo: $pid"
            else
                echo -e "     ${YELLOW}⚠ Cluster inativo (sem postmaster.pid)${NC}"
            fi
        fi
        echo ""
    else
        echo -e "   ${RED}✗ Não encontrado: $dir${NC}"
    fi
done

echo ""

# 5. Tentar conectar em portas comuns
echo -e "${YELLOW}5. Testando conexões PostgreSQL...${NC}"

# Tester conexões com diferentes combinações
test_connections=(
    "localhost:5432:postgres:postgres"
    "localhost:5433:postgres:postgres"
    "localhost:5432:admin:123456"
    "localhost:5433:admin:123456"
    "localhost:5433:dmay:C4n31r0#425#!404?"
    "localhost:5432:runner"
    "localhost:5433:runner"
)

for conn in "${test_connections[@]}"; do
    IFS=':' read -r host port user pass <<< "$conn"
    
    echo -n "   Testando $host:$port com usuário '$user'..."
    
    if [[ -n "$pass" ]]; then
        if PGPASSWORD="$pass" psql -h "$host" -p "$port" -U "$user" -d postgres -c "SELECT 1;" > /dev/null 2>&1; then
            echo -e " ${GREEN}✓ CONECTOU${NC}"
            
            # Listar bancos de dados
            echo "     Bancos disponíveis:"
            PGPASSWORD="$pass" psql -h "$host" -p "$port" -U "$user" -d postgres -t -c "SELECT datname FROM pg_database WHERE datistemplate = false;" 2>/dev/null | grep -v '^$' | sed 's/^ */     - /'
            echo ""
        else
            echo -e " ${RED}✗${NC}"
        fi
    else
        # Tentar sem senha
        if psql -h "$host" -p "$port" -U "$user" -d postgres -c "SELECT 1;" > /dev/null 2>&1; then
            echo -e " ${GREEN}✓ CONECTOU (sem senha)${NC}"
            
            # Listar bancos de dados
            echo "     Bancos disponíveis:"
            psql -h "$host" -p "$port" -U "$user" -d postgres -t -c "SELECT datname FROM pg_database WHERE datistemplate = false;" 2>/dev/null | grep -v '^$' | sed 's/^ */     - /'
            echo ""
        else
            echo -e " ${RED}✗${NC}"
        fi
    fi
done

echo ""

# 6. Verificar arquivos de configuração existentes
echo -e "${YELLOW}6. Verificando arquivos de configuração...${NC}"
config_files=(
    "$HOME/.pgpass"
    "$HOME/.psqlrc"
    "$HOME/postgres_data/postgresql.conf"
    "$HOME/postgres_data/pg_hba.conf"
    "./postgres_control.sh"
    "./.env.local"
)

for file in "${config_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo -e "   ${GREEN}✓ Encontrado: $file${NC}"
        if [[ "$file" == *".conf" ]] || [[ "$file" == ".env.local" ]]; then
            echo "     Primeiras linhas:"
            head -5 "$file" | sed 's/^/     /'
        fi
    else
        echo -e "   ${RED}✗ Não encontrado: $file${NC}"
    fi
done

echo ""

# 7. Verificar logs PostgreSQL
echo -e "${YELLOW}7. Verificando logs PostgreSQL...${NC}"
log_files=(
    "$HOME/postgres.log"
    "$HOME/postgresql.log"
    "/tmp/postgres.log"
    "$HOME/postgres_data/log/postgresql.log"
)

for log in "${log_files[@]}"; do
    if [[ -f "$log" ]]; then
        echo -e "   ${GREEN}✓ Log encontrado: $log${NC}"
        echo "     Tamanho: $(du -h "$log" | cut -f1)"
        echo "     Últimas linhas:"
        tail -3 "$log" 2>/dev/null | sed 's/^/     /' || echo "     (erro ao ler log)"
        echo ""
    else
        echo -e "   ${RED}✗ Log não encontrado: $log${NC}"
    fi
done

echo ""

# Resumo e recomendações
echo -e "${CYAN}=== RESUMO E RECOMENDAÇÕES ===${NC}"

if ps aux | grep postgres | grep -v grep > /dev/null; then
    echo -e "${GREEN}✅ PostgreSQL ativo encontrado no sistema${NC}"
    echo ""
    echo -e "${YELLOW}Recomendações:${NC}"
    echo "1. Use a instância existente se as credenciais funcionarem"
    echo "2. Verifique os bancos de dados disponíveis nas conexões que funcionaram"
    echo "3. Se necessário, pare a instância atual antes de criar uma nova"
    echo ""
    echo -e "${YELLOW}Para parar PostgreSQL existente:${NC}"
    echo "sudo pkill postgres  # ou"
    echo "pg_ctl -D [DATA_DIR] stop"
else
    echo -e "${RED}❌ Nenhum PostgreSQL ativo encontrado${NC}"
    echo ""
    echo -e "${YELLOW}Recomendações:${NC}"
    echo "1. Pode prosseguir com a instalação de um novo PostgreSQL local"
    echo "2. Use o script de configuração que criamos"
    echo "3. Escolha suas credenciais personalizadas"
fi

echo ""
echo -e "${CYAN}=== VERIFICAÇÃO CONCLUÍDA ===${NC}"
