#!/bin/bash

# Script para migrar TODOS os dados de TODAS as 81 tabelas
# De: DB2 (us-west-2) → Para: DB1 (us-east-2)

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}=== MIGRAÇÃO COMPLETA DE TODOS OS DADOS ===${NC}"
echo -e "${YELLOW}ORIGEM: DB2 (us-west-2) → DESTINO: DB1 (us-east-2)${NC}"
echo ""

# Configurações dos bancos
DB1_HOST="ep-late-tree-aectaew7.c-2.us-east-2.aws.neon.tech"
DB1_PASSWORD="npg_YDKTIQge3i4o"
DB1_USER="neondb_owner"
DB1_DATABASE="neondb"

DB2_HOST="ep-withered-smoke-afgjgeem.c-2.us-west-2.aws.neon.tech" 
DB2_PASSWORD="npg_F3M8RaEktGdQ"
DB2_USER="neondb_owner"
DB2_DATABASE="neondb"

# Limpar variáveis que podem interferir
unset PGUSER PGHOST PGDATABASE

# Função para obter lista de todas as tabelas
get_all_tables() {
    PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -U "$DB2_USER" -d "$DB2_DATABASE" -t -c "
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        ORDER BY tablename;
    " 2>/dev/null | grep -v '^$' | sed 's/^ *//' | sed 's/ *$//'
}

# Função para verificar se tabela tem dados
check_table_data() {
    local table_name=$1
    local count=$(PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -U "$DB2_USER" -d "$DB2_DATABASE" -t -c "SELECT COUNT(*) FROM public.$table_name;" 2>/dev/null | tr -d ' ')
    echo "$count"
}

# Função para migrar dados de uma tabela
migrate_table_data() {
    local table_name=$1
    local count_origin=$2
    
    echo -n "  Limpando destino..."
    # Limpar dados existentes no destino
    if PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -U "$DB1_USER" -d "$DB1_DATABASE" -c "TRUNCATE public.$table_name CASCADE;" > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${YELLOW}⚠ (tabela pode não existir)${NC}"
    fi
    
    echo -n "  Exportando dados..."
    local temp_file=$(mktemp)
    
    if PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -U "$DB2_USER" -d "$DB2_DATABASE" -c "
        COPY public.$table_name TO STDOUT WITH (FORMAT CSV, HEADER true, DELIMITER ',', QUOTE '\"', NULL '\\N', ESCAPE '\"');
    " > "$temp_file" 2>/dev/null; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${RED}✗${NC}"
        rm -f "$temp_file"
        return 1
    fi
    
    echo -n "  Importando dados..."
    if PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -U "$DB1_USER" -d "$DB1_DATABASE" -c "
        COPY public.$table_name FROM STDIN WITH (FORMAT CSV, HEADER true, DELIMITER ',', QUOTE '\"', NULL '\\N', ESCAPE '\"');
    " < "$temp_file" > /dev/null 2>&1; then
        
        # Verificar quantos registros foram importados
        local count_dest=$(PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -U "$DB1_USER" -d "$DB1_DATABASE" -t -c "SELECT COUNT(*) FROM public.$table_name;" 2>/dev/null | tr -d ' ')
        
        if [[ "$count_dest" == "$count_origin" ]]; then
            echo -e " ${GREEN}✓ $count_dest registros${NC}"
        else
            echo -e " ${YELLOW}⚠ $count_dest de $count_origin registros${NC}"
        fi
    else
        echo -e " ${RED}✗ erro na importação${NC}"
        rm -f "$temp_file"
        return 1
    fi
    
    rm -f "$temp_file"
    return 0
}

# Verificar conectividade
echo -e "${YELLOW}Verificando conectividade...${NC}"
if ! PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -U "$DB1_USER" -d "$DB1_DATABASE" -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${RED}Erro: Não foi possível conectar ao DB1 (destino)${NC}"
    exit 1
fi

if ! PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -U "$DB2_USER" -d "$DB2_DATABASE" -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${RED}Erro: Não foi possível conectar ao DB2 (origem)${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Conectividade OK${NC}"
echo ""

# Obter lista de todas as tabelas
echo -e "${YELLOW}Obtendo lista de tabelas...${NC}"
all_tables=$(get_all_tables)
table_count=$(echo "$all_tables" | wc -l)
echo -e "${CYAN}Total de tabelas encontradas: $table_count${NC}"
echo ""

# Confirmar operação
echo -e "${YELLOW}⚠️  ATENÇÃO: Esta operação irá:${NC}"
echo "1. Limpar TODOS os dados existentes no DB1"
echo "2. Substituir com TODOS os dados do DB2"
echo "3. Afetar todas as $table_count tabelas"
echo ""
read -p "Tem certeza que deseja continuar? (s/N): " confirm

if [[ ! "$confirm" =~ ^[SsYy]$ ]]; then
    echo -e "${YELLOW}Operação cancelada pelo usuário.${NC}"
    exit 0
fi

echo ""
echo -e "${CYAN}=== INICIANDO MIGRAÇÃO COMPLETA ===${NC}"
echo ""

# Contadores
total_tables=0
tables_with_data=0
empty_tables=0
success_count=0
failed_tables=()
total_records=0

# Processar cada tabela
while IFS= read -r table; do
    [[ -z "$table" ]] && continue
    
    ((total_tables++))
    echo -e "${CYAN}[$total_tables/$table_count] Processando: $table${NC}"
    
    # Verificar se tem dados na origem
    count_origin=$(check_table_data "$table")
    
    if [[ "$count_origin" == "0" ]]; then
        echo -e "  ${YELLOW}Tabela vazia - pulando${NC}"
        ((empty_tables++))
    else
        echo -e "  ${GREEN}$count_origin registros encontrados${NC}"
        ((tables_with_data++))
        
        if migrate_table_data "$table" "$count_origin"; then
            ((success_count++))
            ((total_records += count_origin))
        else
            failed_tables+=("$table")
        fi
    fi
    
    echo ""
    
done <<< "$all_tables"

# Relatório final
echo ""
echo -e "${CYAN}=== RELATÓRIO FINAL ===${NC}"
echo -e "Total de tabelas processadas: ${CYAN}$total_tables${NC}"
echo -e "Tabelas com dados: ${GREEN}$tables_with_data${NC}"
echo -e "Tabelas vazias: ${YELLOW}$empty_tables${NC}"
echo -e "Migrações bem-sucedidas: ${GREEN}$success_count${NC}"
echo -e "Falhas: ${RED}${#failed_tables[@]}${NC}"
echo -e "Total de registros migrados: ${GREEN}$total_records${NC}"

if [[ ${#failed_tables[@]} -gt 0 ]]; then
    echo ""
    echo -e "${RED}Tabelas que falharam:${NC}"
    for table in "${failed_tables[@]}"; do
        echo "  - $table"
    done
fi

echo ""
if [[ ${#failed_tables[@]} -eq 0 ]]; then
    echo -e "${GREEN}✅ MIGRAÇÃO COMPLETA REALIZADA COM SUCESSO!${NC}"
    echo -e "${GREEN}Todos os dados do DB2 foram migrados para o DB1.${NC}"
else
    echo -e "${YELLOW}⚠️ Migração concluída com algumas falhas.${NC}"
    echo -e "${YELLOW}Verifique as tabelas que falharam acima.${NC}"
fi

echo ""
echo -e "${YELLOW}Para verificar o resultado:${NC}"
echo "  ./comparar_dbs.sh --detalhes"
echo ""
echo -e "${CYAN}=== MIGRAÇÃO CONCLUÍDA ===${NC}"
