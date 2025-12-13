#!/bin/bash

# Script PostgreSQL com senha temporária simples

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}=== CONFIGURANDO POSTGRESQL COM SENHA TEMPORÁRIA ===${NC}"
echo ""

# Configurações TEMPORÁRIAS
LOCAL_DB_NAME="neondb_local"
LOCAL_USER="dmay"
LOCAL_PASSWORD="temp123"  # Senha temporária simples
DATA_DIR="$HOME/postgres_data"
LOG_FILE="$HOME/postgres.log"

echo -e "${YELLOW}Configurações temporárias:${NC}"
echo "  Base de dados: $LOCAL_DB_NAME"
echo "  Usuário: $LOCAL_USER"
echo "  Senha: $LOCAL_PASSWORD (temporária)"
echo "  Diretório de dados: $DATA_DIR"
echo ""

# Limpar diretório existente
if [[ -d "$DATA_DIR" ]]; then
    echo "Removendo dados antigos..."
    rm -rf "$DATA_DIR"
fi

mkdir -p "$DATA_DIR"

echo "Inicializando banco com senha temporária..."
echo "Quando solicitar senha, digite: $LOCAL_PASSWORD"
echo ""

# Inicializar com senha simples
initdb -D "$DATA_DIR" -U "$LOCAL_USER" --auth-local=md5 --auth-host=md5 --pwprompt << EOF
$LOCAL_PASSWORD
$LOCAL_PASSWORD
EOF

echo -e "${GREEN}✓ Cluster inicializado${NC}"

# Configurar PostgreSQL
cat >> "$DATA_DIR/postgresql.conf" << EOF

# Configurações para Replit
port = 5433
listen_addresses = 'localhost'
max_connections = 20
shared_buffers = 32MB
EOF

cat > "$DATA_DIR/pg_hba.conf" << EOF
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
EOF

echo -e "${GREEN}✓ PostgreSQL configurado${NC}"

# Iniciar servidor
echo "Iniciando servidor..."
pg_ctl -D "$DATA_DIR" -l "$LOG_FILE" start

sleep 3

# Criar banco
echo "Criando banco $LOCAL_DB_NAME..."
PGPASSWORD="$LOCAL_PASSWORD" createdb -h localhost -p 5433 -U "$LOCAL_USER" "$LOCAL_DB_NAME"

echo -e "${GREEN}✓ Banco criado${NC}"

# Testar conexão
if PGPASSWORD="$LOCAL_PASSWORD" psql -h localhost -p 5433 -U "$LOCAL_USER" -d "$LOCAL_DB_NAME" -c "SELECT version();" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Conexão funcionando${NC}"
else
    echo -e "${RED}✗ Erro na conexão${NC}"
    exit 1
fi

# Criar script de controle com senha temporária
cat > postgres_control.sh << EOF
#!/bin/bash

DATA_DIR="$HOME/postgres_data"
LOG_FILE="$HOME/postgres.log"
TEMP_PASSWORD="$LOCAL_PASSWORD"

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
        PGPASSWORD="\$TEMP_PASSWORD" psql -h localhost -p 5433 -U $LOCAL_USER -d $LOCAL_DB_NAME
        ;;
    change-password)
        echo "Digite a nova senha para o usuário $LOCAL_USER:"
        PGPASSWORD="\$TEMP_PASSWORD" psql -h localhost -p 5433 -U $LOCAL_USER -d $LOCAL_DB_NAME -c "ALTER USER $LOCAL_USER PASSWORD '\$2';"
        echo "Senha alterada. Atualize o script de controle manualmente."
        ;;
    *)
        echo "Uso: \$0 {start|stop|restart|status|connect|change-password [nova_senha]}"
        exit 1
        ;;
esac
EOF

chmod +x postgres_control.sh

echo ""
echo -e "${CYAN}=== CONFIGURAÇÃO CONCLUÍDA ===${NC}"
echo ""
echo -e "${GREEN}PostgreSQL configurado com sucesso!${NC}"
echo ""
echo -e "${YELLOW}Credenciais temporárias:${NC}"
echo "  Host: localhost"
echo "  Porta: 5433"
echo "  Database: $LOCAL_DB_NAME"
echo "  Usuário: $LOCAL_USER"
echo "  Senha: $LOCAL_PASSWORD"
echo ""
echo "String de conexão:"
echo "postgresql://$LOCAL_USER:$LOCAL_PASSWORD@localhost:5433/$LOCAL_DB_NAME"
echo ""
echo -e "${YELLOW}Para alterar senha depois:${NC}"
echo "./postgres_control.sh change-password 'C4n31r0#425#!404?'"
echo ""
echo -e "${YELLOW}Próximo passo:${NC}"
echo "Execute o script de migração para copiar dados do Neon"
