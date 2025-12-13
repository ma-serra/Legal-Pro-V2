#!/bin/bash

# Script PostgreSQL sem prompt de senha

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}=== CONFIGURANDO POSTGRESQL SEM PROMPT ===${NC}"
echo ""

LOCAL_DB_NAME="neondb_local"
LOCAL_USER="dmay"
LOCAL_PASSWORD="temp123"
DATA_DIR="$HOME/postgres_data"
LOG_FILE="$HOME/postgres.log"

echo "Removendo dados antigos..."
rm -rf "$DATA_DIR"
mkdir -p "$DATA_DIR"

echo "Inicializando sem prompt de senha..."
# Usar trust temporariamente
initdb -D "$DATA_DIR" -U "$LOCAL_USER" --auth-local=trust --auth-host=trust

echo -e "${GREEN}✓ Cluster inicializado${NC}"

# Configurar PostgreSQL
cat >> "$DATA_DIR/postgresql.conf" << 'EOF'

# Configurações para Replit  
port = 5433
listen_addresses = 'localhost'
max_connections = 20
shared_buffers = 32MB
EOF

echo -e "${GREEN}✓ PostgreSQL configurado${NC}"

# Iniciar servidor
echo "Iniciando servidor..."
pg_ctl -D "$DATA_DIR" -l "$LOG_FILE" start

sleep 3

# Criar banco
echo "Criando banco..."
createdb -h localhost -p 5433 -U "$LOCAL_USER" "$LOCAL_DB_NAME"

# Agora configurar senha via SQL
echo "Configurando senha..."
psql -h localhost -p 5433 -U "$LOCAL_USER" -d "$LOCAL_DB_NAME" -c "ALTER USER $LOCAL_USER PASSWORD '$LOCAL_PASSWORD';"

# Atualizar pg_hba.conf para usar md5
cat > "$DATA_DIR/pg_hba.conf" << 'EOF'
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
EOF

# Recarregar configuração
pg_ctl -D "$DATA_DIR" reload

echo "Testando conexão com senha..."
if PGPASSWORD="$LOCAL_PASSWORD" psql -h localhost -p 5433 -U "$LOCAL_USER" -d "$LOCAL_DB_NAME" -c "SELECT 'Conexão OK' as status;" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Conexão funcionando${NC}"
else
    echo -e "${RED}✗ Erro na conexão${NC}"
fi

# Criar script de controle
cat > postgres_control.sh << EOF
#!/bin/bash

DATA_DIR="$HOME/postgres_data"
LOG_FILE="$HOME/postgres.log"

case "\$1" in
    start)
        pg_ctl -D "\$DATA_DIR" -l "\$LOG_FILE" start
        ;;
    stop)
        pg_ctl -D "\$DATA_DIR" stop
        ;;
    status)
        pg_ctl -D "\$DATA_DIR" status
        ;;
    connect)
        PGPASSWORD="$LOCAL_PASSWORD" psql -h localhost -p 5433 -U $LOCAL_USER -d $LOCAL_DB_NAME
        ;;
    *)
        echo "Uso: \$0 {start|stop|status|connect}"
        ;;
esac
EOF

chmod +x postgres_control.sh

echo ""
echo -e "${CYAN}=== CONFIGURAÇÃO CONCLUÍDA ===${NC}"
echo "Host: localhost"
echo "Porta: 5433"  
echo "Database: $LOCAL_DB_NAME"
echo "Usuário: $LOCAL_USER"
echo "Senha: $LOCAL_PASSWORD"
echo ""
echo "Teste a conexão: ./postgres_control.sh connect"
