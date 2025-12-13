#!/bin/bash

DB1_HOST="ep-late-tree-aectaew7.c-2.us-east-2.aws.neon.tech"
DB1_PASSWORD="npg_YDKTIQge3i4o"
DB1_USER="neondb_owner"

DB2_HOST="ep-withered-smoke-afgjgeem.c-2.us-west-2.aws.neon.tech" 
DB2_PASSWORD="npg_F3M8RaEktGdQ"
DB2_USER="neondb_owner"

unset PGUSER PGHOST PGDATABASE

# Tabelas que deram erro
ERROR_TABLES=("agente_juridico" "entities" "processo_juridico" "speaker_segments")

for table in "${ERROR_TABLES[@]}"; do
    echo "=== Corrigindo $table ==="
    
    # Usar método INSERT para pequenos batches
    echo "Exportando dados como INSERT statements..."
    PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -U "$DB2_USER" -d neondb -c "
        SELECT 'INSERT INTO public.$table SELECT ' || string_agg(col, ', ') || ';'
        FROM (
            SELECT '''' || COALESCE(column_name, 'NULL') || '''' as col
            FROM information_schema.columns 
            WHERE table_name = '$table' AND table_schema = 'public'
            ORDER BY ordinal_position
        ) t;
    "
    
    echo "Tentativa manual concluída para $table"
done
