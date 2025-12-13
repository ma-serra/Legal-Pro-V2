"""
Migração de Banco de Dados usando Python puro (sem pg_dump)
Copia estrutura e dados diretamente via Python
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import sys

# Configurações
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

def connect_db(config):
    """Conecta ao banco"""
    try:
        conn = psycopg2.connect(**config)
        print(f"✅ Conectado em {config['host']}:{config['port']}/{config['database']}")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None

def get_tables(conn):
    """Lista todas as tabelas"""
    cur = conn.cursor()
    cur.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY tablename
    """)
    tables = [row[0] for row in cur.fetchall()]
    cur.close()
    return tables

def get_create_table_sql(conn, table):
    """Obtém SQL de criação da tabela"""
    cur = conn.cursor()
    
    # Get column definitions
    cur.execute(f"""
        SELECT column_name, data_type, character_maximum_length,
               is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = '{table}'
        ORDER BY ordinal_position
    """)
    
    columns = []
    for row in cur.fetchall():
        col_name, data_type, max_len, nullable, default = row
        
        # Build column definition
        col_def = f'"{col_name}" {data_type}'
        if max_len:
            col_def += f'({max_len})'
        if nullable == 'NO':
            col_def += ' NOT NULL'
        if default:
            col_def += f' DEFAULT {default}'
            
        columns.append(col_def)
    
    # Get primary key
    cur.execute(f"""
        SELECT a.attname
        FROM pg_index i
        JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
        WHERE i.indrelid = '{table}'::regclass AND i.indisprimary
    """)
    pk_cols = [row[0] for row in cur.fetchall()]
    
    sql = f'CREATE TABLE IF NOT EXISTS "{table}" (\n  '
    sql += ',\n  '.join(columns)
    
    if pk_cols:
        sql += f',\n  PRIMARY KEY ({", ".join([f\'"{col}"\' for col in pk_cols])})'
    
    sql += '\n);'
    
    cur.close()
    return sql

def copy_table_data(source_conn, dest_conn, table):
    """Copia dados de uma tabela"""
    try:
        # Get data from source
        source_cur = source_conn.cursor(cursor_factory=RealDictCursor)
        source_cur.execute(f'SELECT * FROM "{table}"')
        rows = source_cur.fetchall()
        
        if not rows:
            print(f"  ⚪ {table}: vazia")
            return True
        
        # Insert into destination
        if rows:
            columns = list(rows[0].keys())
            placeholders = ', '.join(['%s'] * len(columns))
            cols_str = ', '.join([f'"{col}"' for col in columns])
            
            dest_cur = dest_conn.cursor()
            
            # Clear existing data
            dest_cur.execute(f'TRUNCATE TABLE "{table}" CASCADE')
            
            # Insert new data
            insert_sql = f'INSERT INTO "{table}" ({cols_str}) VALUES ({placeholders})'
            
            for row in rows:
                values = [row[col] for col in columns]
                dest_cur.execute(insert_sql, values)
            
            dest_conn.commit()
            dest_cur.close()
            
        source_cur.close()
        print(f"  ✅ {table}: {len(rows)} registros copiados")
        return True
        
    except Exception as e:
        print(f"  ❌ {table}: ERRO - {e}")
        return False

def main():
    print("\n" + "="*60)
    print("🚀 MIGRAÇÃO DE BANCO DE DADOS (Python Nativo)")
    print("="*60)
    print(f"\n📍 ORIGEM: {SOURCE['host']}:{SOURCE['port']}/{SOURCE['database']}")
    print(f"📍 DESTINO: {DEST['host']}:{DEST['port']}/{DEST['database']}")
    print("\n⚠️  Esta operação irá SUBSTITUIR os dados no Railway!")
    
    input("\n👉 Pressione ENTER para continuar ou Ctrl+C para cancelar...")
    
    # Conectar
    print("\n📡 Conectando aos bancos...")
    source_conn = connect_db(SOURCE)
    if not source_conn:
        return False
        
    dest_conn = connect_db(DEST)
    if not dest_conn:
        source_conn.close()
        return False
    
    # Obter tabelas
    print("\n📋 Listando tabelas...")
    tables = get_tables(source_conn)
    print(f"✅ Encontradas {len(tables)} tabelas")
    
    # Criar estrutura
    print("\n🏗️  Criando estrutura no destino...")
    dest_cur = dest_conn.cursor()
    
    for table in tables:
        try:
            create_sql = get_create_table_sql(source_conn, table)
            dest_cur.execute(create_sql)
            print(f"  ✅ {table}")
        except Exception as e:
            print(f"  ⚠️  {table}: {e}")
    
    dest_conn.commit()
    dest_cur.close()
    
    # Copiar dados
    print("\n📊 Copiando dados...")
    success_count = 0
    fail_count = 0
    
    for table in tables:
        if copy_table_data(source_conn, dest_conn, table):
            success_count += 1
        else:
            fail_count += 1
    
    # Fechrar conexões
    source_conn.close()
    dest_conn.close()
    
    # Resultado
    print("\n" + "="*60)
    print("✅ MIGRAÇÃO CONCLUÍDA!")
    print("="*60)
    print(f"\n📊 Resultados:")
    print(f"  ✅ Sucesso: {success_count} tabelas")
    print(f"  ❌ Falhas: {fail_count} tabelas")
    print(f"\n📋 Próximos passos:")
    print("1. Verifique os dados no Railway")
    print("2. Atualize DATABASE_URL no Railway:")
    print(f"   postgresql://{DEST['user']}:{DEST['password']}@{DEST['host']}:{DEST['port']}/{DEST['database']}")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)
