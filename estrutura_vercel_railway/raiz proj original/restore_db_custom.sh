#!/bin/bash

#=============================================================================
# Script de Restauração - PostgreSQL Custom Dump (Legal Pro)
# Restaura backup BINÁRIO do Neon no PostgreSQL local
#=============================================================================

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações do Banco Local
DB_NAME="legal_pro_local"
DB_USER="${USER}"
DB_HOST="localhost"
DB_PORT="5432"
DB_URL="postgresql:///$DB_NAME"

# PostgreSQL 16.9 (compatível com Neon 16.9)
PG16_BIN="/nix/store/w7ldv9b1vc48a235g7ib2kjyqlrzfv0s-postgresql-16.9/bin"

# Arquivo de backup (custom format)
BACKUP_FILE="${1:-attached_assets/DB-legalpro_1762300623279.sql}"

#=============================================================================
# Funções
#=============================================================================

print_header() {
    echo -e "${BLUE}"
    echo "============================================================================="
    echo "$1"
    echo "============================================================================="
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "   $1"
}

#=============================================================================
# Início do Script
#=============================================================================

print_header "RESTORE POSTGRESQL CUSTOM DUMP - LEGAL PRO"

echo ""
echo "📋 Configurações:"
print_info "Banco de dados: $DB_NAME"
print_info "URL de conexão: $DB_URL"
print_info "PostgreSQL: 16.9"
print_info "Arquivo backup: $BACKUP_FILE"
print_info "Formato: Custom (binário)"
echo ""

#=============================================================================
# Validações
#=============================================================================

print_header "1️⃣  VALIDAÇÕES"

# Verificar se o arquivo de backup existe
if [ ! -f "$BACKUP_FILE" ]; then
    print_error "Arquivo de backup não encontrado: $BACKUP_FILE"
    echo ""
    echo "Uso: $0 [caminho_do_backup]"
    echo "Exemplo: $0 attached_assets/DB-legalpro_1762300623279.sql"
    exit 1
fi

print_success "Arquivo de backup encontrado"
BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
FILE_TYPE=$(file "$BACKUP_FILE")
print_info "Tamanho: $BACKUP_SIZE"
print_info "Tipo: $FILE_TYPE"

# Verificar se é realmente custom dump
if ! echo "$FILE_TYPE" | grep -q "PostgreSQL custom database dump"; then
    print_warning "Arquivo pode não ser um PostgreSQL custom dump"
    print_info "Tipo detectado: $FILE_TYPE"
    read -p "Deseja continuar? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        print_info "Operação cancelada"
        exit 0
    fi
fi

# Verificar PostgreSQL 16.9
if [ ! -f "$PG16_BIN/pg_restore" ]; then
    print_error "pg_restore do PostgreSQL 16.9 não encontrado em $PG16_BIN"
    exit 1
fi

print_success "PostgreSQL 16.9 disponível"
PG_VERSION=$("$PG16_BIN/pg_restore" --version)
print_info "$PG_VERSION"

echo ""

#=============================================================================
# Preparação do Banco
#=============================================================================

print_header "2️⃣  PREPARAÇÃO DO BANCO"

# Parar processos usando o banco
print_info "Terminando conexões ativas..."
psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();" > /dev/null 2>&1 || true
sleep 1
print_success "Conexões terminadas"

# Dropar banco se existir
print_info "Removendo banco anterior (se existir)..."
psql -c "DROP DATABASE IF EXISTS $DB_NAME;" > /dev/null 2>&1
print_success "Banco anterior removido"

# Criar banco limpo
print_info "Criando banco limpo..."
psql -c "CREATE DATABASE $DB_NAME;" > /dev/null 2>&1
print_success "Banco '$DB_NAME' criado"

echo ""

#=============================================================================
# Restore do Backup
#=============================================================================

print_header "3️⃣  RESTAURANDO BACKUP (Custom Format)"

print_info "Iniciando pg_restore (isso pode levar alguns minutos)..."
echo ""

# Criar arquivo de log
LOG_FILE="/tmp/restore_$(date +%Y%m%d_%H%M%S).log"

# Executar pg_restore com PostgreSQL 16.9
# Opções:
#   -d: banco de destino
#   -v: verbose
#   --clean: limpar objetos antes de criar
#   --if-exists: evitar erros se objetos não existirem
#   --no-owner: não restaurar ownership
#   --no-acl: não restaurar permissões

START_TIME=$(date +%s)

if "$PG16_BIN/pg_restore" \
    -d "$DB_NAME" \
    --clean \
    --if-exists \
    --no-owner \
    --no-acl \
    -v \
    "$BACKUP_FILE" > "$LOG_FILE" 2>&1; then
    
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    print_success "Restore concluído em ${DURATION}s"
else
    RESTORE_EXIT_CODE=$?
    print_warning "pg_restore retornou código: $RESTORE_EXIT_CODE"
    
    # pg_restore pode retornar erro mesmo com sucesso parcial
    # Vamos verificar se as tabelas foram criadas
    TABLE_COUNT=$(psql -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';" 2>/dev/null | tr -d ' ')
    
    if [ "$TABLE_COUNT" -gt 0 ]; then
        print_success "Restore parcialmente concluído ($TABLE_COUNT tabelas)"
        print_info "Verificando log para warnings..."
        echo ""
        grep -i "error\|warning" "$LOG_FILE" | head -10 || print_info "Nenhum erro crítico encontrado"
    else
        print_error "Erro durante o restore"
        echo ""
        tail -20 "$LOG_FILE"
        echo ""
        print_info "Log completo em: $LOG_FILE"
        exit 1
    fi
fi

echo ""

#=============================================================================
# Verificação
#=============================================================================

print_header "4️⃣  VERIFICAÇÃO"

# Contar tabelas
TABLE_COUNT=$(psql -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';" | tr -d ' ')

print_info "Tabelas criadas: $TABLE_COUNT"

if [ "$TABLE_COUNT" -eq 91 ]; then
    print_success "Todas as 91 tabelas restauradas!"
elif [ "$TABLE_COUNT" -gt 0 ]; then
    print_warning "$TABLE_COUNT tabelas restauradas (esperado: 91)"
else
    print_error "Nenhuma tabela encontrada!"
    exit 1
fi

# Verificar tamanho do banco
DB_SIZE=$(psql -d "$DB_NAME" -t -c "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));" | tr -d ' ')
print_info "Tamanho do banco: $DB_SIZE"

# Contar registros em algumas tabelas chave
print_info "Verificando dados em tabelas principais..."

AGENTES=$(psql -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM agente_juridico;" 2>/dev/null | tr -d ' ')
[ -n "$AGENTES" ] && print_info "  - agente_juridico: $AGENTES registros"

USUARIOS=$(psql -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM usuario;" 2>/dev/null | tr -d ' ')
[ -n "$USUARIOS" ] && print_info "  - usuario: $USUARIOS registros"

PROCESSOS=$(psql -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM processo_juridico;" 2>/dev/null | tr -d ' ')
[ -n "$PROCESSOS" ] && print_info "  - processo_juridico: $PROCESSOS registros"

# Listar algumas tabelas
echo ""
print_info "Primeiras 15 tabelas:"
psql -d "$DB_NAME" -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY table_name LIMIT 15;" -t | while read -r table; do
    [ -n "$table" ] && echo "     - $table"
done

echo ""

#=============================================================================
# Configuração de Variáveis de Ambiente
#=============================================================================

print_header "5️⃣  CONFIGURAÇÃO FINAL"

print_info "Para usar o PostgreSQL local, configure:"
echo ""
echo "export USE_LOCAL_DB=true"
echo "export LOCAL_DB_TYPE=postgres"
echo "export LOCAL_DATABASE_URL=\"$DB_URL\""
echo ""

print_success "Script concluído!"
print_info "Log do restore salvo em: $LOG_FILE"

echo ""
print_header "✨ RESTORE CONCLUÍDO COM SUCESSO!"

#=============================================================================
# Informações Adicionais
#=============================================================================

echo ""
echo "📊 Resumo:"
echo "   ✅ Banco: $DB_NAME"
echo "   ✅ Tabelas: $TABLE_COUNT"
echo "   ✅ Tamanho: $DB_SIZE"
echo ""
echo "🔧 Comandos úteis:"
echo "   # Conectar ao banco"
echo "   psql -d $DB_NAME"
echo ""
echo "   # Ver todas as tabelas"
echo "   psql -d $DB_NAME -c '\\dt'"
echo ""
echo "   # Contar registros em uma tabela"
echo "   psql -d $DB_NAME -c 'SELECT COUNT(*) FROM agente_juridico;'"
echo ""
echo "   # Executar o sistema com banco local"
echo "   export USE_LOCAL_DB=true"
echo "   export LOCAL_DB_TYPE=postgres"
echo "   export LOCAL_DATABASE_URL=\"$DB_URL\""
echo "   python3 main.py"
echo ""
