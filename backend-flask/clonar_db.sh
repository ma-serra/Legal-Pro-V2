#!/bin/bash

# Script para clonar DB2 (us-west-2) para DB1 (us-east-2)
# Foca em adicionar tabelas faltantes e sincronizar estruturas

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}=== CLONAGEM DE BANCO DE DADOS POSTGRESQL ===${NC}"
echo -e "${YELLOW}Origem: DB2 (us-west-2) -> Destino: DB1 (us-east-2)${NC}"
echo ""

# Configurações dos bancos
# DB1 (DESTINO) - us-east-2
DB1_HOST="ep-late-tree-aectaew7.c-2.us-east-2.aws.neon.tech"
DB1_PORT="5432"
DB1_DATABASE="neondb"
DB1_USER="neondb_owner"
DB1_PASSWORD="npg_YDKTIQge3i4o"

# DB2 (ORIGEM) - us-west-2
DB2_HOST="ep-withered-smoke-afgjgeem.c-2.us-west-2.aws.neon.tech"
DB2_PORT="5432"
DB2_DATABASE="neondb"
DB2_USER="neondb_owner"
DB2_PASSWORD="npg_F3M8RaEktGdQ"

# Tabelas que precisam ser adicionadas ao DB1
MISSING_TABLES=(
    "agente_conexoes"
    "agente_mensagens"
    "audio_transcriptions"
    "cadastro_clientes"
    "configuracoes_global_agente"
    "fluxo_resultado"
    "legal_design_pieces"
    "perfis_profissionais"
    "propriedades_rurais"
    "sessoes_colaborativas"
    "tons_voz"
    "transcricoes_audio"
)

# Função para executar comando no banco
execute_db_command() {
    local host=$1
    local port=$2
    local database=$3
    local user=$4
    local password=$5
    local command=$6
    local description=$7
    
    echo -n "  $description..."
    
    if PGPASSWORD="$password" psql -h "$host" -p "$port" -U "$user" -d "$database" -c "$command" > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        return 0
    else
        echo -e " ${RED}✗${NC}"
        return 1
    fi
}

# Função para obter CREATE TABLE de uma tabela
get_table_create_statement() {
    local host=$1
    local port=$2
    local database=$3
    local user=$4
    local password=$5
    local table_name=$6
    
    local query="
    SELECT 
        'CREATE TABLE public.' || tablename || ' (' ||
        array_to_string(
            array_agg(
                column_name || ' ' || 
                CASE 
                    WHEN data_type = 'character varying' THEN 'varchar(' || character_maximum_length || ')'
                    WHEN data_type = 'character' THEN 'char(' || character_maximum_length || ')'
                    WHEN data_type = 'numeric' THEN 'numeric(' || numeric_precision || ',' || numeric_scale || ')'
                    ELSE data_type 
                END ||
                CASE WHEN is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END ||
                CASE WHEN column_default IS NOT NULL THEN ' DEFAULT ' || column_default ELSE '' END
                ORDER BY ordinal_position
            ), 
            ', '
        ) || ');' as create_statement
    FROM information_schema.columns c
    JOIN information_schema.tables t ON c.table_name = t.table_name
    WHERE c.table_schema = 'public' 
    AND c.table_name = '$table_name'
    AND t.table_schema = 'public'
    GROUP BY tablename;
    "
    
    PGPASSWORD="$password" psql -h "$host" -p "$port" -U "$user" -d "$database" -t -c "$query" 2>/dev/null | sed 's/^ *//' | sed 's/ *$//'
}

# Função para obter dados de uma tabela
get_table_data() {
    local host=$1
    local port=$2
    local database=$3
    local user=$4
    local password=$5
    local table_name=$6
    
    PGPASSWORD="$password" pg_dump -h "$host" -p "$port" -U "$user" -d "$database" -t "public.$table_name" --data-only --inserts 2>/dev/null
}

# Função para verificar se tabela existe
table_exists() {
    local host=$1
    local port=$2
    local database=$3
    local user=$4
    local password=$5
    local table_name=$6
    
    local query="SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '$table_name');"
    local result=$(PGPASSWORD="$password" psql -h "$host" -p "$port" -U "$user" -d "$database" -t -c "$query" 2>/dev/null | tr -d ' ')
    
    [[ "$result" == "t" ]]
}

echo -e "${YELLOW}=== VERIFICANDO CONECTIVIDADE ===${NC}"

# Testar conectividade
if ! PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -p "$DB1_PORT" -U "$DB1_USER" -d "$DB1_DATABASE" -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${RED}Erro: Não foi possível conectar ao DB1 (destino)${NC}"
    exit 1
fi
echo -e "${GREEN}✓ DB1 (destino) conectado${NC}"

if ! PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -p "$DB2_PORT" -U "$DB2_USER" -d "$DB2_DATABASE" -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${RED}Erro: Não foi possível conectar ao DB2 (origem)${NC}"
    exit 1
fi
echo -e "${GREEN}✓ DB2 (origem) conectado${NC}"

echo ""

# Prompt de confirmação
echo -e "${YELLOW}ATENÇÃO: Este script irá modificar o banco DB1 (us-east-2)${NC}"
echo -e "${YELLOW}Operações que serão realizadas:${NC}"
echo -e "  1. Adicionar ${#MISSING_TABLES[@]} tabelas faltantes"
echo -e "  2. Corrigir estrutura da tabela validacao_multi_agente_analise"
echo -e "  3. Importar dados das tabelas adicionadas"
echo ""
read -p "Deseja continuar? (s/N): " confirm

if [[ ! "$confirm" =~ ^[SsYy]$ ]]; then
    echo -e "${YELLOW}Operação cancelada pelo usuário.${NC}"
    exit 0
fi

echo ""

# FASE 1: Criar estruturas das tabelas faltantes
echo -e "${YELLOW}=== FASE 1: CRIANDO ESTRUTURAS DAS TABELAS FALTANTES ===${NC}"

for table in "${MISSING_TABLES[@]}"; do
    echo -e "${CYAN}Processando tabela: $table${NC}"
    
    # Verificar se já existe no destino
    if table_exists "$DB1_HOST" "$DB1_PORT" "$DB1_DATABASE" "$DB1_USER" "$DB1_PASSWORD" "$table"; then
        echo -e "  ${YELLOW}Tabela $table já existe no destino - pulando${NC}"
        continue
    fi
    
    # Obter CREATE TABLE da origem
    echo -n "  Obtendo estrutura da origem..."
    create_statement=$(get_table_create_statement "$DB2_HOST" "$DB2_PORT" "$DB2_DATABASE" "$DB2_USER" "$DB2_PASSWORD" "$table")
    
    if [[ -n "$create_statement" ]]; then
        echo -e " ${GREEN}✓${NC}"
        
        # Criar tabela no destino
        if execute_db_command "$DB1_HOST" "$DB1_PORT" "$DB1_DATABASE" "$DB1_USER" "$DB1_PASSWORD" "$create_statement" "Criando tabela no destino"; then
            echo -e "  ${GREEN}✓ Tabela $table criada com sucesso${NC}"
        else
            echo -e "  ${RED}✗ Erro ao criar tabela $table${NC}"
            echo -e "  ${YELLOW}Comando SQL: $create_statement${NC}"
        fi
    else
        echo -e " ${RED}✗${NC}"
        echo -e "  ${RED}✗ Não foi possível obter estrutura da tabela $table${NC}"
    fi
    
    echo ""
done

# FASE 2: Corrigir tabela validacao_multi_agente_analise
echo -e "${YELLOW}=== FASE 2: CORRIGINDO ESTRUTURA DA TABELA validacao_multi_agente_analise ===${NC}"

echo "Analisando diferenças na tabela validacao_multi_agente_analise..."

# Obter estruturas detalhadas de ambas as tabelas
echo -n "  Obtendo estrutura da origem (DB2)..."
db2_columns=$(PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -p "$DB2_PORT" -U "$DB2_USER" -d "$DB2_DATABASE" -t -c "
SELECT column_name || '|' || data_type || '|' || COALESCE(character_maximum_length::text, '') || '|' || is_nullable || '|' || COALESCE(column_default, '')
FROM information_schema.columns 
WHERE table_schema = 'public' AND table_name = 'validacao_multi_agente_analise'
ORDER BY ordinal_position;
" 2>/dev/null)
echo -e " ${GREEN}✓${NC}"

echo -n "  Obtendo estrutura do destino (DB1)..."
db1_columns=$(PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -p "$DB1_PORT" -U "$DB1_USER" -d "$DB1_DATABASE" -t -c "
SELECT column_name || '|' || data_type || '|' || COALESCE(character_maximum_length::text, '') || '|' || is_nullable || '|' || COALESCE(column_default, '')
FROM information_schema.columns 
WHERE table_schema = 'public' AND table_name = 'validacao_multi_agente_analise'
ORDER BY ordinal_position;
" 2>/dev/null)
echo -e " ${GREEN}✓${NC}"

# Encontrar diferenças
echo "  Analisando diferenças..."
temp_db1=$(mktemp)
temp_db2=$(mktemp)
echo "$db1_columns" | grep -v '^$' > "$temp_db1"
echo "$db2_columns" | grep -v '^$' > "$temp_db2"

missing_columns=$(comm -13 <(sort "$temp_db1") <(sort "$temp_db2"))

if [[ -n "$missing_columns" ]]; then
    echo -e "  ${YELLOW}Colunas faltantes encontradas no DB1:${NC}"
    while IFS='|' read -r col_name col_type col_length nullable default_val; do
        [[ -z "$col_name" ]] && continue
        echo -e "    - $col_name ($col_type)"
        
        # Construir comando ALTER TABLE
        alter_cmd="ALTER TABLE public.validacao_multi_agente_analise ADD COLUMN $col_name "
        
        if [[ "$col_type" == "character varying" && -n "$col_length" ]]; then
            alter_cmd+="varchar($col_length)"
        elif [[ "$col_type" == "character" && -n "$col_length" ]]; then
            alter_cmd+="char($col_length)"
        else
            alter_cmd+="$col_type"
        fi
        
        if [[ "$nullable" == "NO" ]]; then
            alter_cmd+=" NOT NULL"
        fi
        
        if [[ -n "$default_val" ]]; then
            alter_cmd+=" DEFAULT $default_val"
        fi
        
        alter_cmd+=";"
        
        # Executar comando
        if execute_db_command "$DB1_HOST" "$DB1_PORT" "$DB1_DATABASE" "$DB1_USER" "$DB1_PASSWORD" "$alter_cmd" "Adicionando coluna $col_name"; then
            echo -e "    ${GREEN}✓ Coluna $col_name adicionada${NC}"
        else
            echo -e "    ${RED}✗ Erro ao adicionar coluna $col_name${NC}"
        fi
        
    done <<< "$missing_columns"
else
    echo -e "  ${GREEN}✓ Nenhuma diferença estrutural encontrada${NC}"
fi

rm -f "$temp_db1" "$temp_db2"

echo ""

# FASE 3: Importar dados
echo -e "${YELLOW}=== FASE 3: IMPORTANDO DADOS DAS TABELAS CRIADAS ===${NC}"

for table in "${MISSING_TABLES[@]}"; do
    echo -e "${CYAN}Importando dados da tabela: $table${NC}"
    
    # Verificar se tabela existe no destino
    if ! table_exists "$DB1_HOST" "$DB1_PORT" "$DB1_DATABASE" "$DB1_USER" "$DB1_PASSWORD" "$table"; then
        echo -e "  ${RED}✗ Tabela $table não existe no destino - pulando${NC}"
        continue
    fi
    
    # Contar registros na origem
    echo -n "  Verificando dados na origem..."
    count_origin=$(PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -p "$DB2_PORT" -U "$DB2_USER" -d "$DB2_DATABASE" -t -c "SELECT COUNT(*) FROM public.$table;" 2>/dev/null | tr -d ' ')
    
    if [[ "$count_origin" == "0" ]]; then
        echo -e " ${YELLOW}Tabela vazia - pulando${NC}"
        continue
    fi
    
    echo -e " ${GREEN}$count_origin registros${NC}"
    
    # Exportar e importar dados
    echo -n "  Exportando e importando dados..."
    
    if PGPASSWORD="$DB2_PASSWORD" pg_dump -h "$DB2_HOST" -p "$DB2_PORT" -U "$DB2_USER" -d "$DB2_DATABASE" -t "public.$table" --data-only --inserts 2>/dev/null | \
       PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -p "$DB1_PORT" -U "$DB1_USER" -d "$DB1_DATABASE" > /dev/null 2>&1; then
        
        # Verificar se dados foram importados
        count_dest=$(PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -p "$DB1_PORT" -U "$DB1_USER" -d "$DB1_DATABASE" -t -c "SELECT COUNT(*) FROM public.$table;" 2>/dev/null | tr -d ' ')
        echo -e " ${GREEN}✓ $count_dest registros importados${NC}"
    else
        echo -e " ${RED}✗ Erro na importação${NC}"
    fi
    
    echo ""
done

# FASE 4: Verificação final
echo -e "${YELLOW}=== FASE 4: VERIFICAÇÃO FINAL ===${NC}"

echo "Executando nova comparação para verificar sincronização..."

# Contar tabelas novamente
db1_count=$(PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -p "$DB1_PORT" -U "$DB1_USER" -d "$DB1_DATABASE" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')
db2_count=$(PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -p "$DB2_PORT" -U "$DB2_USER" -d "$DB2_DATABASE" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')

echo -e "DB1 (destino): $db1_count tabelas"
echo -e "DB2 (origem): $db2_count tabelas"

if [[ "$db1_count" == "$db2_count" ]]; then
    echo -e "${GREEN}✅ SINCRONIZAÇÃO CONCLUÍDA COM SUCESSO!${NC}"
    echo -e "${GREEN}Ambos os bancos agora têm o mesmo número de tabelas.${NC}"
else
    difference=$((db2_count - db1_count))
    echo -e "${YELLOW}⚠️  Ainda há $difference tabela(s) de diferença.${NC}"
    echo -e "${YELLOW}Execute o script de comparação novamente para verificar detalhes.${NC}"
fi

echo ""

# Resumo de comandos úteis
echo -e "${YELLOW}=== COMANDOS ÚTEIS PARA VERIFICAÇÃO ===${NC}"
echo -e "${BLUE}Verificar sincronização: ./comparar_dbs.sh --detalhes${NC}"
echo -e "${BLUE}Conectar ao DB1: PGPASSWORD='$DB1_PASSWORD' psql -h $DB1_HOST -p $DB1_PORT -U $DB1_USER -d $DB1_DATABASE${NC}"
echo -e "${BLUE}Conectar ao DB2: PGPASSWORD='$DB2_PASSWORD' psql -h $DB2_HOST -p $DB2_PORT -U $DB2_USER -d $DB2_DATABASE${NC}"

echo ""
echo -e "${CYAN}=== CLONAGEM CONCLUÍDA ===${NC}"
