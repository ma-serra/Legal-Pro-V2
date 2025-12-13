#!/bin/bash

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}=== SINCRONIZAÇÃO ENTRE BANCOS NEON ===${NC}"
echo ""

# Configurações dos bancos Neon
DB1_HOST="ep-late-tree-aectaew7.c-2.us-east-2.aws.neon.tech"
DB1_PASSWORD="npg_YDKTIQge3i4o"
DB1_USER="neondb_owner"

DB2_HOST="ep-withered-smoke-afgjgeem.c-2.us-west-2.aws.neon.tech" 
DB2_PASSWORD="npg_F3M8RaEktGdQ"
DB2_USER="neondb_owner"

# Tabelas faltantes
TABLES=(
    "agente_conexoes" "agente_mensagens" "audio_transcriptions"
    "cadastro_clientes" "configuracoes_global_agente" "fluxo_resultado"
    "legal_design_pieces" "perfis_profissionais" "propriedades_rurais"
    "sessoes_colaborativas" "tons_voz" "transcricoes_audio"
)

# Limpar variáveis que podem interferir
unset PGUSER
unset PGHOST
unset PGDATABASE

# Função para criar tabela com tipos de dados corretos
create_table() {
    local table_name=$1
    echo -n "  Criando estrutura para $table_name..."
    
    # Obter CREATE TABLE mais robusto
    local create_sql=$(PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -U "$DB2_USER" -d neondb -t -c "
        SELECT 
            'CREATE TABLE IF NOT EXISTS public.' || table_name || ' (' ||
            string_agg(
                column_name || ' ' || 
                CASE 
                    WHEN data_type = 'ARRAY' THEN udt_name
                    WHEN data_type = 'USER-DEFINED' THEN 'text'
                    WHEN data_type = 'character varying' THEN 
                        CASE WHEN character_maximum_length IS NOT NULL 
                        THEN 'varchar(' || character_maximum_length || ')' 
                        ELSE 'text' END
                    WHEN data_type = 'character' THEN 'char(' || character_maximum_length || ')'
                    WHEN data_type = 'numeric' THEN 
                        CASE WHEN numeric_precision IS NOT NULL 
                        THEN 'numeric(' || numeric_precision || ',' || COALESCE(numeric_scale, 0) || ')' 
                        ELSE 'numeric' END
                    WHEN data_type = 'timestamp without time zone' THEN 'timestamp'
                    WHEN data_type = 'timestamp with time zone' THEN 'timestamptz'
                    ELSE data_type 
                END ||
                CASE WHEN is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END ||
                CASE 
                    WHEN column_default IS NOT NULL AND column_default NOT LIKE '%::%' 
                    THEN ' DEFAULT ' || column_default 
                    ELSE '' 
                END,
                ', ' ORDER BY ordinal_position
            ) || ');' as create_statement
        FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = '$table_name'
        GROUP BY table_name;
    " 2>/dev/null | sed 's/^ *//' | sed 's/ *$//')
    
    if [[ -n "$create_sql" ]]; then
        if PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -U "$DB1_USER" -d neondb -c "$create_sql" > /dev/null 2>&1; then
            echo -e " ${GREEN}✓${NC}"
            return 0
        else
            echo -e " ${RED}✗${NC}"
            echo "SQL: $create_sql"
            return 1
        fi
    else
        echo -e " ${RED}✗ (sem estrutura)${NC}"
        return 1
    fi
}

# Função para migrar dados
migrate_data() {
    local table_name=$1
    echo -n "  Migrando dados de $table_name..."
    
    # Contar registros na origem
    local count=$(PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -U "$DB2_USER" -d neondb -t -c "SELECT COUNT(*) FROM public.$table_name;" 2>/dev/null | tr -d ' ')
    
    if [[ "$count" == "0" ]]; then
        echo -e " ${YELLOW}vazia${NC}"
        return 0
    fi
    
    # Arquivo temporário
    local temp_file=$(mktemp)
    
    # Exportar como CSV
    if PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -U "$DB2_USER" -d neondb -c "
        COPY public.$table_name TO STDOUT WITH (FORMAT CSV, HEADER true, DELIMITER ',', QUOTE '\"', NULL '\\N', ESCAPE '\"');
    " > "$temp_file" 2>/dev/null; then
        
        # Importar no destino
        if PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -U "$DB1_USER" -d neondb -c "
            COPY public.$table_name FROM STDIN WITH (FORMAT CSV, HEADER true, DELIMITER ',', QUOTE '\"', NULL '\\N', ESCAPE '\"');
        " < "$temp_file" > /dev/null 2>&1; then
            echo -e " ${GREEN}✓ $count registros${NC}"
        else
            echo -e " ${RED}✗ erro importação${NC}"
        fi
    else
        echo -e " ${RED}✗ erro exportação${NC}"
    fi
    
    rm -f "$temp_file"
}

# Executar migração
echo -e "${YELLOW}Migrando ${#TABLES[@]} tabelas...${NC}"
echo ""

success_count=0
failed_tables=()

for table in "${TABLES[@]}"; do
    echo -e "${CYAN}Processando: $table${NC}"
    
    if create_table "$table"; then
        migrate_data "$table"
        ((success_count++))
    else
        failed_tables+=("$table")
        echo -e "  ${RED}Falha ao criar $table${NC}"
    fi
    
    echo ""
done

echo ""
echo -e "${CYAN}=== RESUMO ===${NC}"
echo -e "Sucessos: ${GREEN}$success_count${NC}"
echo -e "Falhas: ${RED}${#failed_tables[@]}${NC}"

if [[ ${#failed_tables[@]} -gt 0 ]]; then
    echo -e "${RED}Tabelas que falharam:${NC}"
    for table in "${failed_tables[@]}"; do
        echo "  - $table"
    done
fi

echo ""
echo -e "${YELLOW}Execute './comparar_dbs.sh' para verificar o resultado${NC}"
