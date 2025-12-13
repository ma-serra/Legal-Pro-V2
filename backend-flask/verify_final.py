"""Verificar resultado final da migração"""
import psycopg2

RAILWAY = {
    'host': 'gondola.proxy.rlwy.net',
    'port': 11843,
    'database': 'railway',
    'user': 'postgres',
    'password': 'XKtolNYAChqKElojyEfgzUdfpExZmBtM'
}

print("\n" + "="*60)
print("🔍 VERIFICAÇÃO FINAL - RAILWAY DATABASE")
print("="*60)

try:
    conn = psycopg2.connect(**RAILWAY)
    cur = conn.cursor()
    
    # Total de tabelas
    cur.execute("""
        SELECT COUNT(*) 
        FROM pg_tables 
        WHERE schemaname = 'public'
    """)
    total = cur.fetchone()[0]
    
    print("\n📊 Total de tabelas: {}".format(total))
    
    if total == 0:
        print("\n❌ NENHUMA TABELA ENCONTRADA!")
        print("Migração FALHOU novamente!")
    else:
        print("\n✅ TABELAS CRIADAS COM SUCESSO!")
        
        # Listar algumas tabelas importantes
        cur.execute("""
            SELECT tablename, 
                   (SELECT COUNT(*) FROM pg_class WHERE relname = tablename AND relkind = 'r')
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename
            LIMIT 20
        """)
        
        print("\n📋 Primeiras 20 tabelas:")
        for i, row in enumerate(cur.fetchall(), 1):
            table = row[0]
            try:
                cur.execute('SELECT COUNT(*) FROM "{}"'.format(table))
                count = cur.fetchone()[0]
                print("  {}. {} ({} registros)".format(i, table, count))
            except:
                print("  {}. {} (erro ao contar)".format(i, table))
        
        # Tabelas principais
        print("\n🔑 Tabelas Principais:")
        tables_check = ['agente_juridico', 'template_juridico', 'categoria_juridica', 
                       'permission', 'processo_juridico', 'entities']
        
        for table in tables_check:
            try:
                cur.execute('SELECT COUNT(*) FROM "{}"'.format(table))
                count = cur.fetchone()[0]
                print("  ✅ {}: {} registros".format(table, count))
            except Exception as e:
                print("  ❌ {}: {}".format(table, str(e)[:50]))
    
    cur.close()
    conn.close()
    
    print("\n" + "="*60)
    if total > 0:
        print("✅ MIGRAÇÃO CONFIRMADA!")
        print("="*60)
        print("\n📋 Próximo passo:")
        print("Atualizar DATABASE_URL no Railway para:")
        print("postgresql://{}:{}@{}:{}/{}".format(
            RAILWAY['user'], RAILWAY['password'], 
            RAILWAY['host'], RAILWAY['port'], RAILWAY['database']
        ))
    else:
        print("❌ MIGRAÇÃO FALHOU!")
        print("="*60)
        
except Exception as e:
    print("\n❌ Erro ao verificar: {}".format(e))
    import traceback
    traceback.print_exc()
