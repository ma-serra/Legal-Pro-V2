#!/bin/bash

# Script para monitorar migração em tempo real

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configurações dos bancos
DB1_HOST="ep-late-tree-aectaew7.c-2.us-east-2.aws.neon.tech"
DB1_PASSWORD="npg_YDKTIQge3i4o"
DB1_USER="neondb_owner"

DB2_HOST="ep-withered-smoke-afgjgeem.c-2.us-west-2.aws.neon.tech" 
DB2_PASSWORD="npg_F3M8RaEktGdQ"
DB2_USER="neondb_owner"

unset PGUSER PGHOST PGDATABASE

echo -e "${CYAN}=== MONITOR DE MIGRAÇÃO EM TEMPO REAL ===${NC}"
echo ""

# Função para contar tabelas com dados
count_tables_with_data() {
    local host=$1
    local password=$2
    local user=$3
    
    PGPASSWORD="$password" psql -h "$host" -U "$user" -d neondb -t -c "
        SELECT COUNT(*) FROM (
            SELECT schemaname, tablename,
                   (xpath('/row/c/text()', query_to_xml('SELECT COUNT(*) as c FROM ' || quote_ident(schemaname) || '.' || quote_ident(tablename), false, true, '')))[1]::text::int as row_count
            FROM pg_tables 
            WHERE schemaname = 'public'
        ) t WHERE row_count > 0;
    " 2>/dev/null | tr -d ' '
}

# Função para contar total de registros
count_total_records() {
    local host=$1
    local password=$2
    local user=$3
    
    PGPASSWORD="$password" psql -h "$host" -U "$user" -d neondb -t -c "
        SELECT SUM(row_count) FROM (
            SELECT (xpath('/row/c/text()', query_to_xml('SELECT COUNT(*) as c FROM ' || quote_ident(schemaname) || '.' || quote_ident(tablename), false, true, '')))[1]::text::int as row_count
            FROM pg_tables 
            WHERE schemaname = 'public'
        ) t;
    " 2>/dev/null | tr -d ' '
}

# Função para listar últimas tabelas com dados
get_latest_tables() {
    local host=$1
    local password=$2
    local user=$3
    
    PGPASSWORD="$password" psql -h "$host" -U "$user" -d neondb -t -c "
        SELECT tablename || ' (' || row_count || ' registros)' 
        FROM (
            SELECT schemaname, tablename,
                   (xpath('/row/c/text()', query_to_xml('SELECT COUNT(*) as c FROM ' || quote_ident(schemaname) || '.' || quote_ident(tablename), false, true, '')))[1]::text::int as row_count
            FROM pg_tables 
            WHERE schemaname = 'public'
        ) t 
        WHERE row_count > 0 
        ORDER BY tablename 
        LIMIT 10;
    " 2>/dev/null | grep -v '^$' | sed 's/^ *//'
}

echo "Iniciando monitoramento..."
echo "Pressione Ctrl+C para parar"
echo ""

contador=0
while true; do
    ((contador++))
    clear
    
    echo -e "${CYAN}=== MONITOR DE MIGRAÇÃO - Atualização #$contador ===${NC}"
    echo -e "${YELLOW}$(date '+%H:%M:%S')${NC}"
    echo ""
    
    # Contar dados na origem
    echo -n "Contando dados na origem (DB2)..."
    origem_tabelas=$(count_tables_with_data "$DB2_HOST" "$DB2_PASSWORD" "$DB2_USER")
    origem_registros=$(count_total_records "$DB2_HOST" "$DB2_PASSWORD" "$DB2_USER")
    echo -e " ${GREEN}✓${NC}"
    
    # Contar dados no destino
    echo -n "Contando dados no destino (DB1)..."
    destino_tabelas=$(count_tables_with_data "$DB1_HOST" "$DB1_PASSWORD" "$DB1_USER")
    destino_registros=$(count_total_records "$DB1_HOST" "$DB1_PASSWORD" "$DB1_USER")
    echo -e " ${GREEN}✓${NC}"
    
    echo ""
    echo -e "${CYAN}=== STATUS ATUAL ===${NC}"
    echo -e "DB2 (origem):  ${GREEN}$origem_tabelas tabelas${NC} com ${GREEN}$origem_registros registros${NC}"
    echo -e "DB1 (destino): ${YELLOW}$destino_tabelas tabelas${NC} com ${YELLOW}$destino_registros registros${NC}"
    
    # Calcular progresso
    if [[ "$origem_registros" -gt 0 ]]; then
        progresso=$((destino_registros * 100 / origem_registros))
        echo ""
        echo -e "${CYAN}Progresso da migração: ${YELLOW}$progresso%${NC}"
        
        # Barra de progresso visual
        barra=""
        for i in {1..50}; do
            if [[ $((i * 2)) -le $progresso ]]; then
                barra+="█"
            else
                barra+="░"
            fi
        done
        echo -e "[${GREEN}$barra${NC}] $progresso%"
    fi
    
    echo ""
    echo -e "${CYAN}=== ÚLTIMAS TABELAS MIGRADAS NO DB1 ===${NC}"
    latest_tables=$(get_latest_tables "$DB1_HOST" "$DB1_PASSWORD" "$DB1_USER")
    if [[ -n "$latest_tables" ]]; then
        echo "$latest_tables" | head -10
    else
        echo -e "${YELLOW}Nenhuma tabela com dados ainda${NC}"
    fi
    
    # Verificar se a migração foi concluída
    if [[ "$destino_registros" -eq "$origem_registros" ]] && [[ "$destino_registros" -gt 0 ]]; then
        echo ""
        echo -e "${GREEN}🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO! 🎉${NC}"
        echo -e "${GREEN}Todos os $origem_registros registros foram migrados.${NC}"
        break
    fi
    
    echo ""
    echo -e "${YELLOW}Próxima atualização em 10 segundos...${NC}"
    echo -e "${YELLOW}Pressione Ctrl+C para parar o monitoramento${NC}"
    
    sleep 10
done
