#!/bin/bash

set -e

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

for table in "${TABLES[@]}"; do
    echo "Migrando $table..."
    
    # Exportar CSV
    PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -U "$DB2_USER" -d neondb -c "
        COPY (SELECT * FROM public.$table) TO STDOUT WITH CSV HEADER;
    " > "$table.csv"
    
    # Obter CREATE TABLE
    PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -U "$DB2_USER" -d neondb -t -c "
        SELECT 'CREATE TABLE IF NOT EXISTS public.$table (' ||
        string_agg(column_name || ' ' || data_type || 
        CASE WHEN is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END, ', ') ||
        ');' FROM information_schema.columns 
        WHERE table_name = '$table' GROUP BY table_name;
    " | PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -U "$DB1_USER" -d neondb
    
    # Importar dados
    PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -U "$DB1_USER" -d neondb -c "
        COPY public.$table FROM STDIN WITH CSV HEADER;
    " < "$table.csv"
    
    rm "$table.csv"
    echo "$table migrada."
done

echo "Migração concluída. Execute ./comparar_dbs.sh para verificar."
