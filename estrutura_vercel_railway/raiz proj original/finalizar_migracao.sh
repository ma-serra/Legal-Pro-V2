#!/bin/bash

DB1_HOST="ep-late-tree-aectaew7.c-2.us-east-2.aws.neon.tech"
DB1_PASSWORD="npg_YDKTIQge3i4o"
DB1_USER="neondb_owner"

DB2_HOST="ep-withered-smoke-afgjgeem.c-2.us-west-2.aws.neon.tech" 
DB2_PASSWORD="npg_F3M8RaEktGdQ"
DB2_USER="neondb_owner"

unset PGUSER PGHOST PGDATABASE

echo "Finalizando migração das tabelas restantes..."

# Obter lista de todas as tabelas e migrar uma por vez
all_tables=$(PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -U "$DB2_USER" -d neondb -t -c "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;" | grep -v '^$' | sed 's/^ *//')

contador=0
total=$(echo "$all_tables" | wc -l)

echo "$all_tables" | while read table; do
    ((contador++))
    echo "[$contador/$total] Processando: $table"
    
    # Verificar se já tem dados
    current_count=$(PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -U "$DB1_USER" -d neondb -t -c "SELECT COUNT(*) FROM public.$table;" 2>/dev/null | tr -d ' ')
    
    if [[ "$current_count" -gt 0 ]]; then
        echo "  Já tem $current_count registros - pulando"
        continue
    fi
    
    # Contar na origem
    source_count=$(PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -U "$DB2_USER" -d neondb -t -c "SELECT COUNT(*) FROM public.$table;" 2>/dev/null | tr -d ' ')
    
    if [[ "$source_count" -eq 0 ]]; then
        echo "  Tabela vazia na origem - pulando"
        continue
    fi
    
    echo "  Migrando $source_count registros..."
    
    # Migrar dados
    if PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -U "$DB2_USER" -d neondb -c "COPY public.$table TO STDOUT WITH CSV;" | PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -U "$DB1_USER" -d neondb -c "COPY public.$table FROM STDIN WITH CSV;" > /dev/null 2>&1; then
        echo "  ✓ $table migrada"
    else
        echo "  ✗ Erro em $table"
    fi
done

echo "Migração finalizada!"
