#!/bin/bash

# Script para restaurar arquivo SQL existente

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}=== RESTAURAR ARQUIVO SQL EXISTENTE ===${NC}"
echo ""

# Configurações do banco destino
DB1_HOST="ep-late-tree-aectaew7.c-2.us-east-2.aws.neon.tech"
DB1_PASSWORD="npg_YDKTIQge3i4o"
DB1_USER="neondb_owner"
DB1_DATABASE="neondb"

unset PGUSER PGHOST PGDATABASE

# Verificar se arquivo existe
SQL_FILE="db_original_hub_legal_pro.sql"

if [[ ! -f "$SQL_FILE" ]]; then
    echo -e "${RED}Erro: Arquivo $SQL_FILE não encontrado${NC}"
    echo "Certifique-se de que o arquivo está no diretório atual: $(pwd)"
    ls -la *.sql 2>/dev/null || echo "Nenhum arquivo .sql encontrado"
    exit 1
fi

echo -e "${GREEN}✓ Arquivo encontrado: $SQL_FILE${NC}"
file_size=$(du -h "$SQL_FILE" | cut -f1)
echo "Tamanho: $file_size"
echo ""

echo -e "${YELLOW}⚠️  ATENÇÃO: Esta operação irá:${NC}"
echo "1. APAGAR todos os dados do DB1 (us-east-2)"
echo "2. Restaurar o arquivo $SQL_FILE no DB1"
echo "3. Substituir COMPLETAMENTE o conteúdo do DB1"
echo ""
read -p "Confirma a restauração? (s/N): " confirm

if [[ ! "$confirm" =~ ^[SsYy]$ ]]; then
    echo -e "${YELLOW}Operação cancelada.${NC}"
    exit 0
fi

echo ""
echo -e "${CYAN}=== INICIANDO RESTAURAÇÃO ===${NC}"
echo ""

# Verificar conectividade
echo -e "${YELLOW}1. Verificando conectividade...${NC}"
if ! PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -U "$DB1_USER" -d "$DB1_DATABASE" -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${RED}Erro: Não foi possível conectar ao DB1${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Conectado ao DB1${NC}"
echo ""

# Limpar banco destino
echo -e "${YELLOW}2. Limpando banco destino...${NC}"
PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -U "$DB1_USER" -d "$DB1_DATABASE" << 'EOF'
DO $$ 
DECLARE 
    r RECORD;
BEGIN
    -- Desabilitar verificações de chave estrangeira
    SET session_replication_role = replica;
    
    -- Remover todas as tabelas
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') 
    LOOP
        EXECUTE 'DROP TABLE IF EXISTS public.' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;
    
    -- Reabilitar verificações
    SET session_replication_role = DEFAULT;
END $$;
EOF

echo -e "${GREEN}✓ Banco limpo${NC}"
echo ""

# Restaurar arquivo
echo -e "${YELLOW}3. Restaurando arquivo SQL...${NC}"
echo "Importando $SQL_FILE..."

if PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -U "$DB1_USER" -d "$DB1_DATABASE" -f "$SQL_FILE" > restore_$(date +%Y%m%d_%H%M%S).log 2>&1; then
    echo -e "${GREEN}✓ Restauração concluída${NC}"
else
    echo -e "${RED}✗ Erro durante a restauração${NC}"
    echo "Verifique o arquivo de log gerado"
    exit 1
fi

echo ""

# Verificar resultado
echo -e "${YELLOW}4. Verificando resultado...${NC}"
table_count=$(PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOS
