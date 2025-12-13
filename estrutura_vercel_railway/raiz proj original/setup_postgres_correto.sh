#!/bin/bash

# Script para configurar PostgreSQL local no Replit com credenciais corretas

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}=== CONFIGURANDO POSTGRESQL LOCAL NO REPLIT ===${NC}"
echo ""

# Configurações CORRETAS
LOCAL_DB_NAME="neondb_local"
LOCAL_USER="dmay"
LOCAL_PASSWORD="C4n31r0#425#!404?"
DATA_DIR="$HOME/postgres_data"
LOG_FILE="$HOME/postgres.log"

echo -e "${YELLOW}Configurações do banco local:${NC}"
echo "  Base de dados: $LOCAL_DB_NAME"
echo "  Usuário: $LOCAL_USER" 
echo "  Senha: $LOCAL_PASSWORD"
echo "  Diretório de dados: $DATA_DIR"
echo ""

# Remover diretório existente se houver
if [[ -d "$DATA_DIR" ]]; then
    echo "Removendo dados antigos..."
    rm -rf "$DATA_DIR"
fi

# Criar diretório
mkdir -p "$DATA_DIR"

# Inicializar banco com suas credenciais
echo "Executando initdb com usuário $LOCAL_USER..."
initdb -D "$DATA_DIR" -U "$LOCAL_USER" --auth-local=md5 --auth-host=md5 --pwprompt << EOF
$LOCAL_PASSWORD
$LOCAL_PASSWORD
EOF

echo -e "${GREEN}✓ Cluster inicializado${NC}"

# Configurar postgresql.conf
cat >> "$DATA_DIR/postgresql.conf" << EOF

# Configurações customizadas para Replit
port = 5433
listen_addresses = 'localhost'
max_connections = 20
shared_buffers = 32MB
EOF

# Configurar pg_hba.conf
cat > "$DATA_DIR/pg_hba.conf" << EOF
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
EOF

echo -e "${GREEN}✓ PostgreSQL configurado${NC}"

# Iniciar servidor
echo "Iniciando servidor PostgreSQL..."
pg_ctl -D "$DATA_DIR" -l "$LOG_FILE" start

# Aguardar servidor ficar pronto
sleep 3

# Criar banco de dados
echo "Criando banco de dados $LOCAL_DB_NAME..."
PGPASSWORD="$LOCAL_PASSWORD" createdb -h localhost -p 5433 -U "$LOCAL_USER" "$LOCAL_DB_NAME"

echo -e "${GREEN}✓ Banco $LOCAL_DB_NAME criado${NC}"

# Testar conexão
if PGPASSWORD="$LOCAL_PASSWORD" psql -h localhost -p 5433 -U "$LOCAL_USER" -d "$LOCAL_DB_NAME" -c "SELECT version();" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Conexão bem-sucedida${NC}"
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
else
    echo -e "${RED}✗ Falha na conexão${NC}"
fi

# Criar script de controle
cat > postgres_control.sh << EOF
#!/bin/bash

DATA_DIR="$HOME/postgres_data"
LOG_FILE="$HOME/postgres.log"

case "\$1" in
    start)
        echo "Iniciando PostgreSQL..."
        pg_ctl -D "\$DATA_DIR" -l "\$LOG_FILE" start
        ;;
    stop)
        echo "Parando PostgreSQL..."
        pg_ctl -D "\$DATA_DIR" stop
        ;;
    restart)
        echo "Reiniciando PostgreSQL..."
        pg_ctl -D "\$DATA_DIR" restart
        ;;
    status)
        pg_ctl -D "\$DATA_DIR" status
        ;;
    connect)
        PGPASSWORD="$LOCAL_PASSWORD" psql -h localhost -p 5433 -U $LOCAL_USER -d $LOCAL_DB_NAME
        ;;
    *)
        echo "Uso: \$0 {start|stop|restart|status|connect}"
        exit 1
        ;;
esac
EOF

chmod +x postgres_control.sh
echo -e "${GREEN}✓ Script de controle criado: ./postgres_control.sh${NC}"

echo ""
echo -e "${CYAN}=== CONFIGURAÇÃO CONCLUÍDA ===${NC}"
echo -e "${GREEN}PostgreSQL local configurado com suas credenciais!${NC}"
