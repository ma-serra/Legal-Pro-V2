#!/bin/bash

# Script para diagnosticar problemas com as tabelas faltantes

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}=== DIAGNÓSTICO DE TABELAS FALTANTES ===${NC}"
echo ""

# Configurações dos bancos
DB2_HOST="ep-withered-smoke-afgjgeem.c-2.us-west-2.aws.neon.tech"
DB2_PORT="5432" 
DB2_DATABASE="neondb"
DB2_USER="neondb_owner"
DB2_PASSWORD="npg_F3M8RaEktGdQ"

# Tabelas para investigar
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

echo -e "${YELLOW}Investigando por que as tabelas não podem ser exportadas...${NC}"
echo ""

# Função para verificar se tabela existe e suas características
investigate_table() {
    local table_name=$1
    echo -e "${CYAN}=== Investigando: $table_name ===${NC}"
    
    # 1. Verificar se a tabela existe
    echo -n "  1. Verificando existência..."
    local exists=$(PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -p "$DB2_PORT" -U "$DB2_USER" -d "$DB2_DATABASE" -t -c "
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = '$table_name'
        );" 2>/dev/null | tr -d ' ')
    
    if [[ "$exists" == "t" ]]; then
        echo -e " ${GREEN}✓ Existe${NC}"
    else
        echo -e " ${RED}✗ NÃO EXISTE${NC}"
        echo ""
        return 1
    fi
    
    # 2. Verificar permissões
    echo -n "  2. Verificando permissões..."
    local perms=$(PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -p "$DB2_PORT" -U "$DB2_USER" -d "$DB2_DATABASE" -t -c "
        SELECT privilege_type FROM information_schema.role_table_grants 
        WHERE table_schema = 'public' AND table_name = '$table_name' AND grantee = '$DB2_USER';" 2>/dev/null)
    
    if [[ -n "$perms" ]]; then
        echo -e " ${GREEN}✓ Tem permissões${NC}"
        echo "     Permissões: $(echo $perms | tr '\n' ',' | sed 's/,$//')"
    else
        echo -e " ${YELLOW}⚠ Verificando permissões globais...${NC}"
    fi
    
    # 3. Contar registros
    echo -n "  3. Contando registros..."
    local count=$(PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -p "$DB2_PORT" -U "$DB2_USER" -d "$DB2_DATABASE" -t -c "
        SELECT COUNT(*) FROM public.$table_name;" 2>/dev/null | tr -d ' ')
    
    if [[ -n "$count" ]]; then
        echo -e " ${GREEN}✓ $count registros${NC}"
    else
        echo -e " ${RED}✗ Erro ao contar${NC}"
    fi
    
    # 4. Verificar estrutura básica
    echo -n "  4. Verificando estrutura..."
    local columns=$(PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -p "$DB2_PORT" -U "$DB2_USER" -d "$DB2_DATABASE" -t -c "
        SELECT COUNT(*) FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = '$table_name';" 2>/dev/null | tr -d ' ')
    
    if [[ -n "$columns" ]]; then
        echo -e " ${GREEN}✓ $columns colunas${NC}"
    else
        echo -e " ${RED}✗ Erro ao verificar estrutura${NC}"
    fi
    
    # 5. Testar pg_dump com verbose
    echo -n "  5. Testando pg_dump verbose..."
    local dump_test=$(PGPASSWORD="$DB2_PASSWORD" pg_dump -h "$DB2_HOST" -p "$DB2_PORT" -U "$DB2_USER" -d "$DB2_DATABASE" -t "public.$table_name" --schema-only --verbose 2>&1)
    
    if echo "$dump_test" | grep -q "CREATE TABLE"; then
        echo -e " ${GREEN}✓ pg_dump funciona${NC}"
    else
        echo -e " ${RED}✗ pg_dump falha${NC}"
        echo "     Erro: $(echo "$dump_test" | head -3)"
    fi
    
    echo ""
}

# Investigar cada tabela
for table in "${TABLES[@]}"; do
    investigate_table "$table"
done

echo ""
echo -e "${YELLOW}=== TENTATIVA ALTERNATIVA: DUMP MANUAL ===${NC}"
echo ""

# Tentar comando manual mais simples para uma tabela como teste
echo "Testando comando manual para a primeira tabela:"
echo ""

table_test="agente_conexoes"
echo -e "${CYAN}Comando de teste para $table_test:${NC}"
echo "PGPASSWORD='$DB2_PASSWORD' pg_dump -h $DB2_HOST -p $DB2_PORT -U $DB2_USER -d $DB2_DATABASE -t 'public.$table_test' --verbose"
echo ""

echo "Executando teste..."
PGPASSWORD="$DB2_PASSWORD" pg_dump -h "$DB2_HOST" -p "$DB2_PORT" -U "$DB2_USER" -d "$DB2_DATABASE" -t "public.$table_test" --verbose 2>&1 | head -20

echo ""
echo -e "${YELLOW}=== VERIFICAÇÃO DE VERSÃO DO PG_DUMP ===${NC}"
pg_dump --version

echo ""
echo -e "${YELLOW}=== LISTAGEM COMPLETA DE TABELAS NO DB2 ===${NC}"
echo "Verificando se essas tabelas realmente existem:"

PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -p "$DB2_PORT" -U "$DB2_USER" -d "$DB2_DATABASE" -c "
SELECT schemaname, tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('agente_conexoes', 'agente_mensagens', 'audio_transcriptions', 'cadastro_clientes', 'configuracoes_global_agente', 'fluxo_resultado', 'legal_design_pieces', 'perfis_profissionais', 'propriedades_rurais', 'sessoes_colaborativas', 'tons_voz', 'transcricoes_audio')
ORDER BY tablename;"

echo ""
echo -e "${CYAN}=== DIAGNÓSTICO CONCLUÍDO ===${NC}"
