#!/bin/bash

DB1_HOST="ep-late-tree-aectaew7.c-2.us-east-2.aws.neon.tech"
DB1_PASSWORD="npg_YDKTIQge3i4o"
DB1_USER="neondb_owner"

DB2_HOST="ep-withered-smoke-afgjgeem.c-2.us-west-2.aws.neon.tech" 
DB2_PASSWORD="npg_F3M8RaEktGdQ"
DB2_USER="neondb_owner"

unset PGUSER PGHOST PGDATABASE

# Tabelas que deram erro (apenas as menores primeiro)
SMALL_TABLES=("analise_processo_ia" "historico_pagamentos" "relatorio_consenso" "validacao_multi_agente_analise")

echo "Migrando tabelas pequenas que deram erro..."

for table in "${SMALL_TABLES[@]}"; do
    echo "=== $table ==="
    
    # Limpar destino
    PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -U "$DB1_USER" -d neondb -c "TRUNCATE public.$table CASCADE;" 2>/dev/null
    
    # Exportar como texto simples
    temp_file=$(mktemp)
    PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -U "$DB2_USER" -d neondb -c "COPY public.$table TO STDOUT WITH (FORMAT TEXT, DELIMITER E'\t', NULL '');" > "$temp_file"
    
    # Importar
    if PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -U "$DB1_USER" -d neondb -c "COPY public.$table FROM STDIN WITH (FORMAT TEXT, DELIMITER E'\t', NULL '');" < "$temp_file" > /dev/null 2>&1; then
        echo "✓ $table migrada"
    else
        echo "✗ $table ainda com erro"
    fi
    
    rm -f "$temp_file"
done
