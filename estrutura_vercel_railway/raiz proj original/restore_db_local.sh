#!/bin/bash

#=============================================================================
# Script de Restauração - PostgreSQL Local (Legal Pro)
# Restaura backup do Neon no PostgreSQL local para desenvolvimento
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
DB_USER="${USER}"  # Usuário atual do sistema
DB_HOST="localhost"
DB_PORT="5432"
DB_URL="postgresql:///$DB_NAME"

# PostgreSQL 16.9 (compatível com Neon)
PG16_BIN="/nix/store/w7ldv9b1vc48a235g7ib2kjyqlrzfv0s-postgresql-16.9/bin"

# Arquivo de backup (padrão)
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

print_header "RESTORE POSTGRESQL LOCAL - LEGAL PRO"

echo ""
echo "📋 Configurações:"
print_info "Banco de dados: $DB_NAME"
print_info "URL de conexão: $DB_URL"
print_info "PostgreSQL: 16.9"
print_info "Arquivo backup: $BACKUP_FILE"
echo ""

#=============================================================================
# Validações
#=============================================================================

print_header "1️⃣  VALIDAÇÕES"

# Verificar se o arquivo de backup existe
if [ ! -f "$BACKUP_FILE" ]; then
    print_error "Arquivo de backup não encontrado: $BACKUP_FILE"
    echo ""
    echo "Uso: $0 [caminho_do_backup.sql]"
    echo "Exemplo: $0 attached_assets/DB-legalpro_1762300623279.sql"
    exit 1
fi

print_success "Arquivo de backup encontrado"
BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
BACKUP_LINES=$(wc -l < "$BACKUP_FILE")
print_info "Tamanho: $BACKUP_SIZE"
print_info "Linhas: $BACKUP_LINES"

# Verificar PostgreSQL 16.9
if [ ! -f "$PG16_BIN/psql" ]; then
    print_error "PostgreSQL 16.9 não encontrado em $PG16_BIN"
    exit 1
fi

print_success "PostgreSQL 16.9 disponível"
PG_VERSION=$("$PG16_BIN/psql" --version)
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

print_header "3️⃣  RESTAURANDO BACKUP"

print_info "Iniciando restore (isso pode levar alguns minutos)..."
echo ""

# Criar arquivo de log
LOG_FILE="/tmp/restore_$(date +%Y%m%d_%H%M%S).log"

# Executar restore com PostgreSQL 16.9
START_TIME=$(date +%s)

if "$PG16_BIN/psql" -d "$DB_NAME" -f "$BACKUP_FILE" > "$LOG_FILE" 2>&1; then
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    print_success "Restore concluído em ${DURATION}s"
else
    print_error "Erro durante o restore"
    print_warning "Verificando log para detalhes..."
    echo ""
    tail -20 "$LOG_FILE"
    echo ""
    print_info "Log completo em: $LOG_FILE"
    exit 1
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

# Listar algumas tabelas
print_info "Primeiras 10 tabelas:"
psql -d "$DB_NAME" -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY table_name LIMIT 10;" -t | while read -r table; do
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
echo "   # Executar o sistema com banco local"
echo "   export USE_LOCAL_DB=true && python3 main.py"
echo ""
