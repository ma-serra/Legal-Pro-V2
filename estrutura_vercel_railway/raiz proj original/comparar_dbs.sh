#!/bin/bash

# Script para comparar estruturas de dois bancos PostgreSQL
# Executa no Bash do Replit

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}=== COMPARAÇÃO DE BANCOS DE DADOS POSTGRESQL ===${NC}"
echo ""

# Configurações dos bancos
DB1_HOST="ep-late-tree-aectaew7.c-2.us-east-2.aws.neon.tech"
DB1_PORT="5432"
DB1_DATABASE="neondb"
DB1_USER="neondb_owner"
DB1_PASSWORD="npg_YDKTIQge3i4o"
DB1_NAME="DB1 (us-east-2)"

DB2_HOST="ep-withered-smoke-afgjgeem.c-2.us-west-2.aws.neon.tech"
DB2_PORT="5432"
DB2_DATABASE="neondb"
DB2_USER="neondb_owner"
DB2_PASSWORD="npg_F3M8RaEktGdQ"
DB2_NAME="DB2 (us-west-2)"

# Verificar se psql está disponível
if ! command -v psql &> /dev/null; then
    echo -e "${RED}ERRO: psql não encontrado.${NC}"
    echo -e "${YELLOW}PostgreSQL foi instalado mas pode não estar no PATH.${NC}"
    echo -e "${YELLOW}Tente reiniciar o shell ou execute: source ~/.bashrc${NC}"
    exit 1
fi

# Função para executar query PostgreSQL
execute_query() {
    local host=$1
    local port=$2
    local database=$3
    local user=$4
    local password=$5
    local query=$6
    
    PGPASSWORD="$password" psql -h "$host" -p "$port" -U "$user" -d "$database" -t -c "$query" 2>/dev/null
}

# Função para testar conectividade
test_connection() {
    local host=$1
    local port=$2
    local database=$3
    local user=$4
    local password=$5
    local name=$6
    
    echo -n "Testando conexão com $name..."
    
    if result=$(execute_query "$host" "$port" "$database" "$user" "$password" "SELECT 1;"); then
        if [[ -n "$result" ]]; then
            echo -e " ${GREEN}✓ CONECTADO${NC}"
            return 0
        fi
    fi
    
    echo -e " ${RED}✗ FALHA${NC}"
    return 1
}

# Função para obter lista de tabelas
get_tables() {
    local host=$1
    local port=$2
    local database=$3
    local user=$4
    local password=$5
    
    local query="SELECT schemaname || '.' || tablename FROM pg_tables WHERE schemaname NOT IN ('information_schema', 'pg_catalog', 'pg_toast') ORDER BY schemaname, tablename;"
    
    execute_query "$host" "$port" "$database" "$user" "$password" "$query" | grep -v '^$' | sed 's/^ *//' | sed 's/ *$//'
}

# Função para obter detalhes de uma tabela
get_table_details() {
    local host=$1
    local port=$2
    local database=$3
    local user=$4
    local password=$5
    local schema=$6
    local table=$7
    
    local query="SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_schema = '$schema' AND table_name = '$table' ORDER BY ordinal_position;"
    
    execute_query "$host" "$port" "$database" "$user" "$password" "$query"
}

echo -e "${YELLOW}=== TESTE DE CONECTIVIDADE ===${NC}"

# Testar conectividade
if ! test_connection "$DB1_HOST" "$DB1_PORT" "$DB1_DATABASE" "$DB1_USER" "$DB1_PASSWORD" "$DB1_NAME"; then
    echo -e "${RED}Não foi possível conectar ao DB1. Verifique as credenciais.${NC}"
    exit 1
fi

if ! test_connection "$DB2_HOST" "$DB2_PORT" "$DB2_DATABASE" "$DB2_USER" "$DB2_PASSWORD" "$DB2_NAME"; then
    echo -e "${RED}Não foi possível conectar ao DB2. Verifique as credenciais.${NC}"
    exit 1
fi

echo ""

# Obter tabelas de ambos os bancos
echo -e "${YELLOW}=== OBTENDO ESTRUTURAS DAS TABELAS ===${NC}"
echo -n "Analisando $DB1_NAME..."
tables1=$(get_tables "$DB1_HOST" "$DB1_PORT" "$DB1_DATABASE" "$DB1_USER" "$DB1_PASSWORD")
echo -e " ${GREEN}✓${NC}"

echo -n "Analisando $DB2_NAME..."
tables2=$(get_tables "$DB2_HOST" "$DB2_PORT" "$DB2_DATABASE" "$DB2_USER" "$DB2_PASSWORD")
echo -e " ${GREEN}✓${NC}"

echo ""

# Converter para arrays
mapfile -t array1 <<< "$tables1"
mapfile -t array2 <<< "$tables2"

# Filtrar linhas vazias
array1_filtered=()
for item in "${array1[@]}"; do
    [[ -n "$item" ]] && array1_filtered+=("$item")
done

array2_filtered=()
for item in "${array2[@]}"; do
    [[ -n "$item" ]] && array2_filtered+=("$item")
done

# Comparar tabelas
echo -e "${YELLOW}=== COMPARAÇÃO DE TABELAS ===${NC}"
echo -e "${CYAN}Total de tabelas em $DB1_NAME: ${#array1_filtered[@]}${NC}"
echo -e "${CYAN}Total de tabelas em $DB2_NAME: ${#array2_filtered[@]}${NC}"
echo ""

# Criar arquivos temporários para comparação
temp1=$(mktemp)
temp2=$(mktemp)
printf '%s\n' "${array1_filtered[@]}" | sort > "$temp1"
printf '%s\n' "${array2_filtered[@]}" | sort > "$temp2"

# Tabelas apenas em DB1
only_in_db1=$(comm -23 "$temp1" "$temp2")
if [[ -n "$only_in_db1" ]]; then
    echo -e "${RED}❌ Tabelas apenas em $DB1_NAME:${NC}"
    while IFS= read -r table; do
        [[ -n "$table" ]] && echo -e "   ${RED}- $table${NC}"
    done <<< "$only_in_db1"
    echo ""
fi

# Tabelas apenas em DB2
only_in_db2=$(comm -13 "$temp1" "$temp2")
if [[ -n "$only_in_db2" ]]; then
    echo -e "${RED}❌ Tabelas apenas em $DB2_NAME:${NC}"
    while IFS= read -r table; do
        [[ -n "$table" ]] && echo -e "   ${RED}- $table${NC}"
    done <<< "$only_in_db2"
    echo ""
fi

# Tabelas comuns
common_tables=$(comm -12 "$temp1" "$temp2")
if [[ -n "$common_tables" ]]; then
    echo -e "${GREEN}✅ Tabelas presentes em ambos os bancos:${NC}"
    while IFS= read -r table; do
        [[ -n "$table" ]] && echo -e "   ${GREEN}- $table${NC}"
    done <<< "$common_tables"
    echo ""
fi

# Análise detalhada (se há argumento --detalhes)
if [[ "$1" == "--detalhes" ]] && [[ -n "$common_tables" ]]; then
    echo -e "${YELLOW}=== ANÁLISE DETALHADA DAS ESTRUTURAS ===${NC}"
    
    while IFS= read -r full_table; do
        [[ -z "$full_table" ]] && continue
        
        schema=$(echo "$full_table" | cut -d'.' -f1)
        table=$(echo "$full_table" | cut -d'.' -f2)
        
        echo ""
        echo -e "${CYAN}--- Analisando tabela: $full_table ---${NC}"
        
        # Obter estrutura de ambas as tabelas
        struct1=$(get_table_details "$DB1_HOST" "$DB1_PORT" "$DB1_DATABASE" "$DB1_USER" "$DB1_PASSWORD" "$schema" "$table")
        struct2=$(get_table_details "$DB2_HOST" "$DB2_PORT" "$DB2_DATABASE" "$DB2_USER" "$DB2_PASSWORD" "$schema" "$table")
        
        if [[ -n "$struct1" ]] && [[ -n "$struct2" ]]; then
            # Comparar número de colunas (simplificado)
            cols1_count=$(echo "$struct1" | wc -l)
            cols2_count=$(echo "$struct2" | wc -l)
            
            if [[ $cols1_count -eq $cols2_count ]]; then
                echo -e "   ${GREEN}✅ Mesmo número de colunas ($cols1_count)${NC}"
            else
                echo -e "   ${RED}❌ Número de colunas diferente: DB1($cols1_count) vs DB2($cols2_count)${NC}"
            fi
        fi
    done <<< "$common_tables"
fi

# Cleanup
rm -f "$temp1" "$temp2"

# Resumo final
echo ""
echo -e "${YELLOW}=== RESUMO FINAL ===${NC}"

only_in_db1_count=$(echo "$only_in_db1" | grep -c . || true)
only_in_db2_count=$(echo "$only_in_db2" | grep -c . || true)
common_count=$(echo "$common_tables" | grep -c . || true)

total_issues=$((only_in_db1_count + only_in_db2_count))

if [[ $total_issues -eq 0 ]]; then
    echo -e "${GREEN}✅ ESTRUTURAS IDÊNTICAS${NC}"
    echo -e "${GREEN}Ambos os bancos possuem exatamente as mesmas tabelas.${NC}"
else
    echo -e "${RED}❌ DIFERENÇAS ENCONTRADAS${NC}"
    echo -e "${RED}Total de discrepâncias: $total_issues${NC}"
    
    if [[ $only_in_db1_count -gt 0 ]]; then
        echo -e "${RED}- $only_in_db1_count tabela(s) apenas em $DB1_NAME${NC}"
    fi
    if [[ $only_in_db2_count -gt 0 ]]; then
        echo -e "${RED}- $only_in_db2_count tabela(s) apenas em $DB2_NAME${NC}"
    fi
fi

echo ""
echo -e "${CYAN}Tabelas comuns: $common_count${NC}"
echo ""

# Comandos úteis
echo -e "${YELLOW}=== COMANDOS ÚTEIS ===${NC}"
echo -e "${BLUE}Para análise detalhada: ./comparar_dbs.sh --detalhes${NC}"
echo -e "${BLUE}Para conectar ao DB1: PGPASSWORD='$DB1_PASSWORD' psql -h $DB1_HOST -p $DB1_PORT -U $DB1_USER -d $DB1_DATABASE${NC}"
echo -e "${BLUE}Para conectar ao DB2: PGPASSWORD='$DB2_PASSWORD' psql -h $DB2_HOST -p $DB2_PORT -U $DB2_USER -d $DB2_DATABASE${NC}"

echo ""
echo -e "${CYAN}=== SCRIPT CONCLUÍDO ===${NC}"
