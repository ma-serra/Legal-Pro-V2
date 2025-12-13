"""
Migração de Banco de Dados usando Python puro (sem pg_dump)
Copia estrutura e dados diretamente via Python
"""

import psycopg2
from psycopg2.extras import RealDictCursor
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
        print("✅ Conectado em {}:{}/{}".format(config['host'], config['port'], config['database']))
        return conn
    except Exception as e:
        print("❌ Erro ao conectar: {}".format(e))
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

def copy_table_data(source_conn, dest_conn, table):
    """Copia dados de uma tabela"""
    try:
        # Get data from source
        source_cur = source_conn.cursor(cursor_factory=RealDictCursor)
        source_cur.execute('SELECT * FROM "{}"'.format(table))
        rows = source_cur.fetchall()
        
        if not rows:
            print("  ⚪ {}: vazia".format(table))
            return True
        
        # Insert into destination
        columns = list(rows[0].keys())
        placeholders = ', '.join(['%s'] * len(columns))
        cols_str = ', '.join(['"{}"'.format(col) for col in columns])
        
        dest_cur = dest_conn.cursor()
        
        # Clear existing data
        dest_cur.execute('DELETE FROM "{}"'.format(table))
        
        # Insert new data
        insert_sql = 'INSERT INTO "{}" ({}) VALUES ({})'.format(table, cols_str, placeholders)
        
        for row in rows:
            values = [row[col] for col in columns]
            dest_cur.execute(insert_sql, values)
        
        dest_conn.commit()
        dest_cur.close()
        source_cur.close()
        
        print("  ✅ {}: {} registros copiados".format(table, len(rows)))
        return True
        
    except Exception as e:
        print("  ❌ {}: ERRO - {}".format(table, e))
        return False

def main():
    print("\n" + "="*60)
    print("🚀 MIGRAÇÃO DE BANCO DE DADOS (Python Nativo)")
    print("="*60)
    print("\n📍 ORIGEM: {}:{}/{}".format(SOURCE['host'], SOURCE['port'], SOURCE['database']))
    print("📍 DESTINO: {}:{}/{}".format(DEST['host'], DEST['port'], DEST['database']))
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
    print("✅ Encontradas {} tabelas".format(len(tables)))
    
    # Copiar dados
    print("\n📊 Copiando dados...")
    success_count = 0
    fail_count = 0
    
    for table in tables:
        if copy_table_data(source_conn, dest_conn, table):
            success_count += 1
        else:
            fail_count += 1
    
    # Fechar conexões
    source_conn.close()
    dest_conn.close()
    
    # Resultado
    print("\n" + "="*60)
    print("✅ MIGRAÇÃO CONCLUÍDA!")
    print("="*60)
    print("\n📊 Resultados:")
    print("  ✅ Sucesso: {} tabelas".format(success_count))
    print("  ❌ Falhas: {} tabelas".format(fail_count))
    print("\n📋 Próximos passos:")
    print("1. Verifique os dados no Railway")
    print("2. Atualize DATABASE_URL no Railway:")
    print("   postgresql://{}:{}@{}:{}/{}".format(
        DEST['user'], DEST['password'], DEST['host'], DEST['port'], DEST['database']
    ))
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada")
        sys.exit(1)
    except Exception as e:
        print("\n❌ Erro: {}".format(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)
