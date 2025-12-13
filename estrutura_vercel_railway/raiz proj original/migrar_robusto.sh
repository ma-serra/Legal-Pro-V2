#!/bin/bash

DB1_HOST="ep-late-tree-aectaew7.c-2.us-east-2.aws.neon.tech"
DB1_PASSWORD="npg_YDKTIQge3i4o"
DB1_USER="neondb_owner"

DB2_HOST="ep-withered-smoke-afgjgeem.c-2.us-west-2.aws.neon.tech" 
DB2_PASSWORD="npg_F3M8RaEktGdQ"
DB2_USER="neondb_owner"

unset PGUSER PGHOST PGDATABASE

# Tabelas prioritárias em ordem de importância
PRIORITY_TABLES=(
    "user" "documento" "template_juridico" "legal_templates_juridicos"
    "processo_juridico" "documento_carregado" "analise_juridica"
    "chunk_documento" "transcricao" "historico_documento"
)

echo "Migrando tabelas prioritárias com tratamento de erros..."

for table in "${PRIORITY_TABLES[@]}"; do
    echo "=== $table ==="
    
    # Verificar se já tem dados
    current=$(PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -U "$DB1_USER" -d neondb -t -c "SELECT COUNT(*) FROM public.$table;" 2>/dev/null | tr -d ' ')
    
    if [[ "$current" -gt 0 ]]; then
        echo "Já tem $current registros - pulando"
        continue
    fi
    
    # Contar origem
    source=$(PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -U "$DB2_USER" -d neondb -t -c "SELECT COUNT(*) FROM public.$table;" 2>/dev/null | tr -d ' ')
    
    if [[ "$source" -eq 0 ]]; then
        echo "Vazia na origem - pulando"
        continue
    fi
    
    echo "Migrando $source registros..."
    
    # Tentar migração com tratamento de erro
    temp_file=$(mktemp)
    
    if PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -U "$DB2_USER" -d neondb -c "COPY public.$table TO STDOUT WITH (FORMAT CSV, HEADER false, DELIMITER ',', NULL '');" > "$temp_file" 2>/dev/null; then
        
        if PGPASSWORD="$DB1_PASSWORD" psql -h "$DB1_HOST" -U "$DB1_USER" -d neondb -c "COPY public.$table FROM STDIN WITH (FORMAT CSV, HEADER false, DELIMITER ',', NULL '');" < "$temp_file" > /dev/null 2>&1; then
            echo "✓ Sucesso"
        else
            echo "✗ Erro na importação - tentando método alternativo"
            # Método alternativo: INSERT linha por linha para tabelas pequenas
            if [[ "$source" -lt 100 ]]; then
                echo "Tentando INSERT individual..."
                PGPASSWORD="$DB2_PASSWORD" psql -h "$DB2_HOST" -U "$DB2_USER" -d neondb -c "
                    SELECT 'INSERT INTO public.$table VALUES (' || 
                           string_agg(COALESCE('''' || replace(col::text, '''', '''''') || '''', 'NULL'), ',') || 
                           ');'
                    FROM (SELECT * FROM public.$table LIMIT 10) t,
                    unnest(string_to_array(replace(row(t.*)::text, '(', ''), ')')) WITH ORDINALITY AS u(col, pos)
                    GROUP BY row(t.*);
                " 2>/dev/null
            fi
        fi
    else
        echo "✗ Erro na exportação"
    fi
    
    rm -f "$temp_file"
    echo ""
done

echo "Migração das tabelas prioritárias concluída"
