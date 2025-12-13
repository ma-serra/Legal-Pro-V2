"""
Script para verificar estado dos bancos e executar migração correta
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

def check_database(config, name):
    """Verifica tabelas em um banco"""
    print("\n" + "="*60)
    print("📊 Verificando banco: {}".format(name))
    print("="*60)
    
    try:
        conn = psycopg2.connect(**config)
        cur = conn.cursor()
        
        # Listar tabelas
        cur.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)
        
        tables = [row[0] for row in cur.fetchall()]
        
        print("\n✅ Total de tabelas: {}".format(len(tables)))
        
        if tables:
            print("\n📋 Tabelas encontradas:")
            for i, table in enumerate(tables, 1):
                # Contar registros
                try:
                    cur.execute('SELECT COUNT(*) FROM "{}"'.format(table))
                    count = cur.fetchone()[0]
                    print("  {}. {} ({} registros)".format(i, table, count))
                except:
                    print("  {}. {} (erro ao contar)".format(i, table))
        else:
            print("\n❌ NENHUMA TABELA ENCONTRADA!")
        
        cur.close()
        conn.close()
        
        return tables
        
    except Exception as e:
        print("\n❌ Erro ao conectar: {}".format(e))
        return []

def migrate_with_create(source_conn, dest_conn, table):
    """Migra tabela criando estrutura primeiro"""
    try:
        print("\n  🔄 Migrando: {}".format(table))
        
        # Buscar dados da origem
        source_cur = source_conn.cursor(cursor_factory=RealDictCursor)
        source_cur.execute('SELECT * FROM "{}"'.format(table))
        rows = source_cur.fetchall()
        
        if not rows:
            print("    ⚪ Tabela vazia - pulando")
            source_cur.close()
            return True
        
        # Obter estrutura da tabela
        source_struct = source_conn.cursor()
        source_struct.execute("""
            SELECT column_name, data_type, character_maximum_length, 
                   is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = '{}'
            ORDER BY ordinal_position
        """.format(table))
        
        columns_def = []
        for col in source_struct.fetchall():
            col_name, dtype, max_len, nullable, default = col
            col_sql = '"{}" {}'.format(col_name, dtype)
            
            if max_len and dtype == 'character varying':
                col_sql += '({})'.format(max_len)
            
            if nullable == 'NO':
                col_sql += ' NOT NULL'
                
            columns_def.append(col_sql)
        
        # Criar tabela no destino
        dest_cur = dest_conn.cursor()
        
        # Drop se existir
        dest_cur.execute('DROP TABLE IF EXISTS "{}" CASCADE'.format(table))
        
        # Criar tabela
        create_sql = 'CREATE TABLE "{}" ({})'.format(table, ', '.join(columns_def))
        dest_cur.execute(create_sql)
        dest_conn.commit()
        
        print("    ✅ Estrutura criada")
        
        # Inserir dados
        columns = list(rows[0].keys())
        placeholders = ', '.join(['%s'] * len(columns))
        cols_str = ', '.join(['"{}"'.format(col) for col in columns])
        
        insert_sql = 'INSERT INTO "{}" ({}) VALUES ({})'.format(table, cols_str, placeholders)
        
        inserted = 0
        for row in rows:
            try:
                values = [row[col] for col in columns]
                dest_cur.execute(insert_sql, values)
                inserted += 1
            except Exception as e:
                print("    ⚠️ Erro em registro: {}".format(str(e)[:50]))
        
        dest_conn.commit()
        dest_cur.close()
        source_cur.close()
        source_struct.close()
        
        print("    ✅ {} registros inseridos".format(inserted))
        return True
        
    except Exception as e:
        print("    ❌ ERRO: {}".format(e))
        return False

def main():
    print("\n" + "="*60)
    print("🔍 DIAGNÓSTICO E MIGRAÇÃO DE BANCO DE DADOS")
    print("="*60)
    
    # Verificar estado atual
    print("\n📊 VERIFICANDO ESTADO ATUAL...")
    
    source_tables = check_database(SOURCE, "ORIGEM (Antigo)")
    dest_tables = check_database(DEST, "DESTINO (Railway)")
    
    if not source_tables:
        print("\n❌ Erro: Banco origem não tem tabelas ou não conectou!")
        return False
    
    print("\n" + "="*60)
    print("📋 RESUMO")
    print("="*60)
    print("ORIGEM: {} tabelas".format(len(source_tables)))
    print("DESTINO: {} tabelas".format(len(dest_tables)))
    
    if len(dest_tables) == len(source_tables):
        print("\n✅ Bancos parecem sincronizados!")
        return True
    
    print("\n⚠️  DESTINO ESTÁ VAZIO OU INCOMPLETO!")
    print("\n👉 Executando migração completa...")
    
    input("\nPressione ENTER para continuar...")
    
    # Conectar
    print("\n📡 Conectando aos bancos...")
    source_conn = psycopg2.connect(**SOURCE)
    dest_conn = psycopg2.connect(**DEST)
    
    print("✅ Conectado!")
    
    # Migrar cada tabela
    print("\n🔄 Migrando {} tabelas...".format(len(source_tables)))
    
    success = 0
    failed = 0
    
    for table in source_tables:
        if migrate_with_create(source_conn, dest_conn, table):
            success += 1
        else:
            failed += 1
    
    source_conn.close()
    dest_conn.close()
    
    # Resultado
    print("\n" + "="*60)
    print("✅ MIGRAÇÃO CONCLUÍDA!")
    print("="*60)
    print("\n📊 Resultados:")
    print("  ✅ Sucesso: {} tabelas".format(success))
    print("  ❌ Falhas: {} tabelas".format(failed))
    
    if failed == 0:
        print("\n🎉 PERFEITO! Todas as tabelas foram migradas!")
    
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
        print("\n\n⚠️ Operação cancelada")
        sys.exit(1)
    except Exception as e:
        print("\n❌ Erro: {}".format(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)
