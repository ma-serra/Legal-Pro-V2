#!/bin/bash

# Script simplificado para clonar tabelas específicas entre bancos PostgreSQL
# Método mais direto usando pg_dump

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}=== CLONAGEM SIMPLIFICADA DE TABELAS POSTGRESQL ===${NC}"
echo ""

# Configurações dos bancos
DB1_HOST="ep-late-tree-aectaew7.c-2.us-east-2.aws.neon.tech"
DB1_PORT="5432"
DB1_DATABASE="neondb"
DB1_USER="neondb_owner"
DB1_PASSWORD="npg_YDKTIQge3i4o"

DB2_HOST="ep-withered-smoke-afgjgeem.c-2.us-west-2.aws.neon.tech"
DB2_PORT="5432"
DB2_DATABASE="neondb"
DB2_USER="neondb_owner"
DB2_PASSWORD="npg_F3M8RaEktGdQ"

# Tabelas faltantes
TABLES=(
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

echo -e "${YELLOW}MÉTODO 1: Clonagem individual por tabela${NC}"
echo ""

# Função para clonar uma tabela específica
clone_table() {
    local table_name=$1
    echo -e "${CYAN}=== Clonando tabela: $table_name ===${NC}"
    
    # Criar arquivo temporário
    local temp_file=$(mktemp)
    
    echo -n "  1. Exportando estrutura e dados da origem..."
    if PGPASSWORD="$DB2_PASSWORD" pg_dump \
        -h "$DB2_HOST" -p "$DB2_PORT" -U "$DB2_USER" -d "$DB2_DATABASE" \
        -t "public.$table_name" \
        --no-owner --no-privileges \
        > "$temp_file" 2>/dev/null; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${RED}✗${NC}"
        rm -f "$temp_file"
        return 1
    fi
    
    echo -n "  2. Importando para destino..."
    if PGPASSWORD="$DB1_PASSWORD" psql \
        -h "$DB1_HOST" -p "$DB1_PORT" -U "$DB1_USER" -d "$DB1_DATABASE" \
        -f "$temp_file" > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${RED}✗${NC}"
        rm -f "$temp_file"
        return 1
    fi
    
    # Verificar se foi criada
    echo -n "  3. Verificando criação..."
    local count=$(PGPASSWORD="$DB1_PASSWORD" psql \
        -h "$DB1_HOST" -p "$DB1_PORT" -U "$DB1_USER" -d "$DB1_DATABASE" \
        -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '$table_name';" 2>/dev/null | tr -d ' ')
    
    if [[ "$count" == "1" ]]; then
        echo -e " ${GREEN}✓ Tabela criada${NC}"
        
        # Contar registros
        local record_count=$(PGPASSWORD="$DB1_PASSWORD" psql \
            -h "$DB1_HOST" -p "$DB1_PORT" -U "$DB1_USER" -d "$DB1_DATABASE" \
            -t -c "SELECT COUNT(*) FROM public.$table_name;" 2>/dev/null | tr -d ' ')
        echo -e "     ${GREEN}$record_count registros importados${NC}"
    else
        echo -e " ${RED}✗ Tabela não foi criada${NC}"
        rm -f "$temp_file"
        return 1
    fi
    
    rm -f "$temp_file"
    echo ""
    return 0
}

# Testar conectividade
echo -e "${YELLOW}Testando conectividade...${NC}"
if ! PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -p "$DB1_PORT" -U "$DB1_USER" -d "$DB1_DATABASE" -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${RED}Erro: Não conectou ao DB1${NC}"
    exit 1
fi

if ! PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -p "$DB2_PORT" -U "$DB2_USER" -d "$DB2_DATABASE" -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${RED}Erro: Não conectou ao DB2${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Ambos os bancos conectados${NC}"
echo ""

# Confirmar operação
echo -e "${YELLOW}Irá clonar ${#TABLES[@]} tabelas do DB2 para o DB1${NC}"
read -p "Continuar? (s/N): " confirm
if [[ ! "$confirm" =~ ^[SsYy]$ ]]; then
    echo "Cancelado."
    exit 0
fi
echo ""

# Clonar cada tabela
success_count=0
failed_tables=()

for table in "${TABLES[@]}"; do
    if clone_table "$table"; then
        ((success_count++))
    else
        failed_tables+=("$table")
        echo -e "${RED}Falha ao clonar $table${NC}"
    fi
done

echo ""
echo -e "${CYAN}=== RESUMO ===${NC}"
echo -e "Sucessos: ${GREEN}$success_count${NC}"
echo -e "Falhas: ${RED}${#failed_tables[@]}${NC}"

if [[ ${#failed_tables[@]} -gt 0 ]]; then
    echo -e "${RED}Tabelas que falharam:${NC}"
    for table in "${failed_tables[@]}"; do
        echo -e "  - $table"
    done
    echo ""
    echo -e "${YELLOW}=== MÉTODO ALTERNATIVO ===\n"
    echo -e "Para as tabelas que falharam, você pode tentar manualmente:${NC}"
    echo ""
    for table in "${failed_tables[@]}"; do
        echo -e "${YELLOW}# Para a tabela $table:${NC}"
        echo "PGPASSWORD='$DB2_PASSWORD' pg_dump -h $DB2_HOST -p $DB2_PORT -U $DB2_USER -d $DB2_DATABASE -t 'public.$table' --no-owner --no-privileges > $table.sql"
        echo "PGPASSWORD='$DB1_PASSWORD' psql -h $DB1_HOST -p $DB1_PORT -U $DB1_USER -d $DB1_DATABASE -f $table.sql"
        echo ""
    done
fi

echo ""

# Corrigir colunas faltantes na tabela validacao_multi_agente_analise
echo -e "${YELLOW}=== CORRIGINDO COLUNAS FALTANTES ===${NC}"

echo "Adicionando colunas faltantes na tabela validacao_multi_agente_analise..."

# Adicionar as colunas que falharam anteriormente
if PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -p "$DB1_PORT" -U "$DB1_USER" -d "$DB1_DATABASE" -c "
ALTER TABLE public.validacao_multi_agente_analise 
ADD COLUMN IF NOT EXISTS exportado_docx boolean DEFAULT false;
" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Coluna exportado_docx adicionada${NC}"
else
    echo -e "${RED}✗ Erro ao adicionar exportado_docx${NC}"
fi

if PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -p "$DB1_PORT" -U "$DB1_USER" -d "$DB1_DATABASE" -c "
ALTER TABLE public.validacao_multi_agente_analise 
ADD COLUMN IF NOT EXISTS exportado_txt boolean DEFAULT false;
" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Coluna exportado_txt adicionada${NC}"
else
    echo -e "${RED}✗ Erro ao adicionar exportado_txt${NC}"
fi

echo ""

# Verificação final
echo -e "${YELLOW}=== VERIFICAÇÃO FINAL ===${NC}"
db1_count=$(PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -p "$DB1_PORT" -U "$DB1_USER" -d "$DB1_DATABASE" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')
db2_count=$(PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -p "$DB2_PORT" -U "$DB2_USER" -d "$DB2_DATABASE" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')

echo "DB1: $db1_count tabelas"
echo "DB2: $db2_count tabelas"

if [[ "$db1_count" == "$db2_count" ]]; then
    echo -e "${GREEN}✅ SINCRONIZAÇÃO COMPLETA!${NC}"
else
    echo -e "${YELLOW}⚠️ Ainda há diferenças. Execute: ./comparar_dbs.sh${NC}"
fi

echo ""
echo -e "${CYAN}=== CLONAGEM CONCLUÍDA ===${NC}"
