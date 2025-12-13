#!/bin/bash

set -e

# Configurações
DB1_HOST="ep-late-tree-aectaew7.c-2.us-east-2.aws.neon.tech"
DB1_PASSWORD="npg_YDKTIQge3i4o"
DB1_USER="neondb_owner"

DB2_HOST="ep-withered-smoke-afgjgeem.c-2.us-west-2.aws.neon.tech" 
DB2_PASSWORD="npg_F3M8RaEktGdQ"
DB2_USER="neondb_owner"

# Tabelas restantes (pulando agente_conexoes que já foi)
TABLES=(
    "agente_mensagens" "audio_transcriptions" "cadastro_clientes" 
    "configuracoes_global_agente" "fluxo_resultado" "legal_design_pieces"
    "perfis_profissionais" "propriedades_rurais" "sessoes_colaborativas" 
    "tons_voz" "transcricoes_audio"
)

unset PGUSER PGHOST PGDATABASE

echo "Continuando migração das 11 tabelas restantes..."

for table in "${TABLES[@]}"; do
    echo "Processando: $table"
    
    # Criar estrutura
    create_sql=$(PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -U "$DB2_USER" -d neondb -t -c "
        SELECT 'CREATE TABLE IF NOT EXISTS public.' || table_name || ' (' ||
        string_agg(column_name || ' ' || 
            CASE WHEN data_type = 'ARRAY' THEN udt_name
                 WHEN data_type = 'USER-DEFINED' THEN 'text'
                 ELSE data_type END ||
            CASE WHEN is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END,
            ', ' ORDER BY ordinal_position) || ');'
        FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = '$table'
        GROUP BY table_name;
    " | sed 's/^ *//')
    
    PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -U "$DB1_USER" -d neondb -c "$create_sql"
    
    # Migrar dados
    temp_file=$(mktemp)
    PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -U "$DB2_USER" -d neondb -c "COPY public.$table TO STDOUT WITH CSV HEADER;" > "$temp_file"
    PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -U "$DB1_USER" -d neondb -c "COPY public.$table FROM STDIN WITH CSV HEADER;" < "$temp_file"
    rm "$temp_file"
    
    echo "$table ✓"
done

echo "Migração das 11 tabelas restantes concluída!"
