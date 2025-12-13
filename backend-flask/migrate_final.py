"""
Migração robusta com commits parciais e debug detalhado
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import sys

SOURCE = {
    'host': '147.93.68.169',
    'port': 5433,
    'database': 'hublegalpro_db',
    'user': 'arsdatascience',
    'password': 'xJ>rh}zv?jU;21?t'
}

DEST = {
    'host': 'gondola.proxy.rlwy.net',
    'port': 11843,
    'database': 'railway',
    'user': 'postgres',
    'password': 'XKtolNYAChqKElojyEfgzUdfpExZmBtM'
}

def migrate_table_robust(source_conn, dest_conn, table):
    """Migra tabela com autocommit e debug"""
    print("\n🔄 Migrando: {}".format(table))
    
    try:
        # Fonte
        src_cur = source_conn.cursor(cursor_factory=RealDictCursor)
        src_cur.execute('SELECT * FROM "{}"'.format(table))
        rows = src_cur.fetchall()
        
        if not rows:
            print("  ⚪ Vazia - pulando")
            src_cur.close()
            return True
        
        print("  📊 {} registros encontrados".format(len(rows)))
        
        # Destino - usar autocommit
        dest_conn.autocommit = True
        dest_cur = dest_conn.cursor()
        
        # Drop e Create
        print("  🗑️  Dropping se existir...")
        dest_cur.execute('DROP TABLE IF EXISTS "{}" CASCADE'.format(table))
        
        # Obter estrutura
        src_struct = source_conn.cursor()
        src_struct.execute("""
            SELECT column_name, data_type, character_maximum_length, 
                   is_nullable, column_default, udt_name
            FROM information_schema.columns
            WHERE table_name = '{}'
            ORDER BY ordinal_position
        """.format(table))
        
        cols_def = []
        for col in src_struct.fetchall():
            col_name, dtype, max_len, nullable, default, udt = col
            
            # Usar udt_name para tipos corretos
            if udt == 'varchar' and max_len:
                col_sql = '"{}" VARCHAR({})'.format(col_name, max_len)
            elif udt in ['int4', 'integer']:
                col_sql = '"{}" INTEGER'.format(col_name)
            elif udt in ['int8', 'bigint']:
                col_sql = '"{}" BIGINT'.format(col_name)
            elif udt == 'bool':
                col_sql = '"{}" BOOLEAN'.format(col_name)
            elif udt == 'timestamp':
                col_sql = '"{}" TIMESTAMP'.format(col_name)
            elif udt == 'date':
                col_sql = '"{}" DATE'.format(col_name)
            elif udt == 'text':
                col_sql = '"{}" TEXT'.format(col_name)
            elif udt == 'numeric':
                col_sql = '"{}" NUMERIC'.format(col_name)
            elif udt == 'json':
                col_sql = '"{}" JSON'.format(col_name)
            elif udt == 'jsonb':
                col_sql = '"{}" JSONB'.format(col_name)
            else:
                col_sql = '"{}" {}'.format(col_name, udt.upper())
            
            if nullable == 'NO':
                col_sql += ' NOT NULL'
            
            cols_def.append(col_sql)
        
        if not cols_def:
            print("  ❌ Sem colunas encontradas!")
            return False
        
        create_sql = 'CREATE TABLE "{}" ({})'.format(table, ', '.join(cols_def))
        print("  🏗️  Criando estrutura...")
        dest_cur.execute(create_sql)
        print("  ✅ Tabela criada")
        
        # Inserir dados
        columns = list(rows[0].keys())
        placeholders = ', '.join(['%s'] * len(columns))
        cols_str = ', '.join(['"{}"'.format(col) for col in columns])
        insert_sql = 'INSERT INTO "{}" ({}) VALUES ({})'.format(table, cols_str, placeholders)
        
        print("  📥 Inserindo {} registros...".format(len(rows)))
        inserted = 0
        errors = 0
        
        for i, row in enumerate(rows):
            try:
                values = [row[col] for col in columns]
                dest_cur.execute(insert_sql, values)
                inserted += 1
                
                if (i + 1) % 100 == 0:
                    print("    ... {} registros inseridos".format(i + 1))
                    
            except Exception as e:
                errors += 1
                if errors <= 3:
                    print("    ⚠️  Erro no registro {}: {}".format(i+1, str(e)[:60]))
        
        dest_cur.close()
        src_cur.close()
        src_struct.close()
        
        print("  ✅ Concluído: {} inseridos, {} erros".format(inserted, errors))
        return inserted > 0
        
    except Exception as e:
        print("  ❌ ERRO FATAL: {}".format(e))
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "="*60)
    print("🚀 MIGRAÇÃO ROBUSTA COM AUTOCOMMIT")
    print("="*60)
    
    print("\n📡 Conectando...")
    
    try:
        source_conn = psycopg2.connect(**SOURCE)
        print("✅ Conectado na ORIGEM")
    except Exception as e:
        print("❌ Erro ao conectar origem: {}".format(e))
        return False
    
    try:
        dest_conn = psycopg2.connect(**DEST)
        print("✅ Conectado no DESTINO (Railway)")
    except Exception as e:
        print("❌ Erro ao conectar Railway: {}".format(e))
        source_conn.close()
        return False
    
    # Listar tabelas
    src_cur = source_conn.cursor()
    src_cur.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY tablename
    """)
    tables = [row[0] for row in src_cur.fetchall()]
    src_cur.close()
    
    print("\n📋 Encontradas {} tabelas para migrar".format(len(tables)))
    print("\n⚠️  Este processo criará as tabelas no Railway!")
    
    input("\n👉 Pressione ENTER para continuar...")
    
    # Migrar
    print("\n🔄 Iniciando migração...")
    success = 0
    failed = 0
    
    for i, table in enumerate(tables, 1):
        print("\n[{}/{}]".format(i, len(tables)))
        if migrate_table_robust(source_conn, dest_conn, table):
            success += 1
        else:
            failed += 1
    
    source_conn.close()
    dest_conn.close()
    
    # Resultado
    print("\n" + "="*60)
    print("✅ MIGRAÇÃO FINALIZADA!")
    print("="*60)
    print("\n📊 Resultados:")
    print("  ✅ Sucesso: {} tabelas".format(success))
    print("  ❌ Falhas: {} tabelas".format(failed))
    
    if success > 0:
        print("\n🎉 Tabelas migradas com sucesso!")
        print("\n📋 Próximo passo:")
        print("Atualizar DATABASE_URL no Railway para:")
        print("postgresql://{}:{}@{}:{}/{}".format(
            DEST['user'], DEST['password'], DEST['host'], DEST['port'], DEST['database']
        ))
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelado")
        sys.exit(1)
    except Exception as e:
        print("\n❌ Erro: {}".format(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)
