#!/bin/bash

# Script para configurar PostgreSQL local no Replit

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}=== CONFIGURANDO POSTGRESQL LOCAL NO REPLIT ===${NC}"
echo ""

# Configurações
LOCAL_DB_NAME="neondb_local"
LOCAL_USER="admin"
LOCAL_PASSWORD="123456"
DATA_DIR="$HOME/postgres_data"
LOG_FILE="$HOME/postgres.log"

echo -e "${YELLOW}Configurações do banco local:${NC}"
echo "  Base de dados: $LOCAL_DB_NAME"
echo "  Usuário: $LOCAL_USER"
echo "  Senha: $LOCAL_PASSWORD"
echo "  Diretório de dados: $DATA_DIR"
echo ""

# Função para verificar se PostgreSQL está instalado
check_postgresql() {
    if command -v postgres &> /dev/null && command -v psql &> /dev/null; then
        echo -e "${GREEN}✓ PostgreSQL já está instalado${NC}"
        postgres --version
        return 0
    else
        echo -e "${RED}✗ PostgreSQL não encontrado${NC}"
        return 1
    fi
}

# Função para instalar PostgreSQL se necessário
install_postgresql() {
    echo -e "${YELLOW}Instalando PostgreSQL...${NC}"
    
    # Adicionar ao replit.nix se não existir
    if [[ ! -f "replit.nix" ]]; then
        echo "Criando replit.nix..."
        cat > replit.nix << 'EOF'
{ pkgs }: {
  deps = [
    pkgs.postgresql_16
  ];
}
EOF
    else
        echo "Verificando replit.nix existente..."
        if ! grep -q "postgresql" replit.nix; then
            echo "Adicionando PostgreSQL ao replit.nix..."
            # Backup do arquivo original
            cp replit.nix replit.nix.backup
            
            # Adicionar PostgreSQL
            sed -i 's/deps = \[/deps = [\n    pkgs.postgresql_16,/' replit.nix
        fi
    fi
    
    echo "Instalando via nix..."
    nix-env -iA nixpkgs.postgresql_16
    
    # Atualizar PATH
    export PATH="/nix/store/$(ls /nix/store | grep postgresql | head -1)/bin:$PATH"
    
    echo -e "${GREEN}✓ PostgreSQL instalado${NC}"
}

# Função para inicializar cluster de banco
init_database() {
    echo -e "${YELLOW}Inicializando cluster de banco de dados...${NC}"
    
    # Remover diretório existente se houver
    if [[ -d "$DATA_DIR" ]]; then
        echo "Removendo dados antigos..."
        rm -rf "$DATA_DIR"
    fi
    
    # Criar diretório
    mkdir -p "$DATA_DIR"
    
    # Inicializar banco
    echo "Executando initdb..."
    initdb -D "$DATA_DIR" -U "$LOCAL_USER" --pwprompt --auth-local=md5 --auth-host=md5 << EOF
$LOCAL_PASSWORD
$LOCAL_PASSWORD
EOF
    
    echo -e "${GREEN}✓ Cluster inicializado${NC}"
}

# Função para configurar PostgreSQL
configure_postgresql() {
    echo -e "${YELLOW}Configurando PostgreSQL...${NC}"
    
    # Configurar postgresql.conf
    cat >> "$DATA_DIR/postgresql.conf" << EOF

# Configurações customizadas para Replit
port = 5433
listen_addresses = 'localhost'
max_connections = 20
shared_buffers = 32MB
effective_cache_size = 128MB
work_mem = 2MB
maintenance_work_mem = 16MB
checkpoint_completion_target = 0.9
wal_buffers = 1MB
default_statistics_target = 100
EOF

    # Configurar pg_hba.conf para permitir conexões locais
    cat > "$DATA_DIR/pg_hba.conf" << EOF
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
EOF
    
    echo -e "${GREEN}✓ PostgreSQL configurado${NC}"
}

# Função para iniciar servidor
start_server() {
    echo -e "${YELLOW}Iniciando servidor PostgreSQL...${NC}"
    
    # Verificar se já está rodando
    if pg_ctl -D "$DATA_DIR" status &> /dev/null; then
        echo -e "${GREEN}✓ Servidor já está rodando${NC}"
        return 0
    fi
    
    # Iniciar servidor em background
    pg_ctl -D "$DATA_DIR" -l "$LOG_FILE" start
    
    # Aguardar servidor ficar pronto
    echo "Aguardando servidor ficar pronto..."
    sleep 3
    
    # Verificar status
    if pg_ctl -D "$DATA_DIR" status &> /dev/null; then
        echo -e "${GREEN}✓ Servidor PostgreSQL iniciado${NC}"
        echo "  Log: $LOG_FILE"
        echo "  Porta: 5433"
    else
        echo -e "${RED}✗ Falha ao iniciar servidor${NC}"
        echo "Verificar log: $LOG_FILE"
        return 1
    fi
}

# Função para criar banco de dados
create_database() {
    echo -e "${YELLOW}Criando banco de dados $LOCAL_DB_NAME...${NC}"
    
    # Conectar e criar banco
    PGPASSWORD="$LOCAL_PASSWORD" createdb -h localhost -p 5433 -U "$LOCAL_USER" "$LOCAL_DB_NAME"
    
    echo -e "${GREEN}✓ Banco $LOCAL_DB_NAME criado${NC}"
}

# Função para testar conexão
test_connection() {
    echo -e "${YELLOW}Testando conexão...${NC}"
    
    if PGPASSWORD="$LOCAL_PASSWORD" psql -h localhost -p 5433 -U "$LOCAL_USER" -d "$LOCAL_DB_NAME" -c "SELECT version();" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Conexão bem-sucedida${NC}"
        
        # Mostrar informações da conexão
        echo ""
        echo -e "${CYAN}=== INFORMAÇÕES DE CONEXÃO ===${NC}"
        echo "Host: localhost"
        echo "Porta: 5433"
        echo "Base de dados: $LOCAL_DB_NAME"
        echo "Usuário: $LOCAL_USER"
        echo "Senha: $LOCAL_PASSWORD"
        echo ""
        echo "String de conexão:"
        echo "postgresql://$LOCAL_USER:$LOCAL_PASSWORD@localhost:5433/$LOCAL_DB_NAME"
        
        return 0
    else
        echo -e "${RED}✗ Falha na conexão${NC}"
        return 1
    fi
}

# Função para criar script de controle
create_control_script() {
    echo -e "${YELLOW}Criando script de controle...${NC}"
    
    cat > postgres_control.sh << 'EOF'
#!/bin/bash

DATA_DIR="$HOME/postgres_data"
LOG_FILE="$HOME/postgres.log"

case "$1" in
    start)
        echo "Iniciando PostgreSQL..."
        pg_ctl -D "$DATA_DIR" -l "$LOG_FILE" start
        ;;
    stop)
        echo "Parando PostgreSQL..."
        pg_ctl -D "$DATA_DIR" stop
        ;;
    restart)
        echo "Reiniciando PostgreSQL..."
        pg_ctl -D "$DATA_DIR" restart
        ;;
    status)
        pg_ctl -D "$DATA_DIR" status
        ;;
    log)
        tail -f "$LOG_FILE"
        ;;
    connect)
        PGPASSWORD="123456" psql -h localhost -p 5433 -U admin -d neondb_local
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|status|log|connect}"
        exit 1
        ;;
esac
EOF

    chmod +x postgres_control.sh
    echo -e "${GREEN}✓ Script de controle criado: ./postgres_control.sh${NC}"
}

# Executar configuração completa
echo "Iniciando configuração..."
echo ""

# 1. Verificar/instalar PostgreSQL
if ! check_postgresql; then
    install_postgresql
    
    # Recarregar PATH
    export PATH="/nix/store/$(ls /nix/store | grep postgresql | tail -1)/bin:$PATH"
    
    if ! check_postgresql; then
        echo -e "${RED}Erro: Não foi possível instalar PostgreSQL${NC}"
        echo "Tente reiniciar o Replit e executar novamente."
        exit 1
    fi
fi

# 2. Inicializar banco
init_database

# 3. Configurar
configure_postgresql

# 4. Iniciar servidor
start_server

# 5. Criar banco
create_database

# 6. Testar conexão
test_connection

# 7. Criar script de controle
create_control_script

echo ""
echo -e "${CYAN}=== CONFIGURAÇÃO CONCLUÍDA ===${NC}"
echo ""
echo -e "${GREEN}PostgreSQL local configurado com sucesso!${NC}"
echo ""
echo -e "${YELLOW}Comandos úteis:${NC}"
echo "  ./postgres_control.sh start    # Iniciar servidor"
echo "  ./postgres_control.sh stop     # Parar servidor"
echo "  ./postgres_control.sh status   # Ver status"
echo "  ./postgres_control.sh connect  # Conectar ao banco"
echo "  ./postgres_control.sh log      # Ver logs"
echo ""
echo -e "${YELLOW}Para migrar dados do Neon:${NC}"
echo "  Execute o próximo script de migração que vou criar."
echo ""

# Criar arquivo .env com as configurações
cat > .env.local << EOF
# PostgreSQL Local Configuration
LOCAL_DB_HOST=localhost
LOCAL_DB_PORT=5433
LOCAL_DB_NAME=$LOCAL_DB_NAME
LOCAL_DB_USER=$LOCAL_USER
LOCAL_DB_PASSWORD=$LOCAL_PASSWORD
LOCAL_DB_URL=postgresql://$LOCAL_USER:$LOCAL_PASSWORD@localhost:5433/$LOCAL_DB_NAME
EOF

echo -e "${GREEN}✓ Configurações salvas em .env.local${NC}"
