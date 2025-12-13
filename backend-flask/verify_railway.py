"""Script rápido para verificar se migração funcionou"""
import psycopg2

RAILWAY = {
    'host': 'gondola.proxy.rlwy.net',
    'port': 11843,
    'database': 'railway',
    'user': 'postgres',
    'password': 'XKtolNYAChqKElojyEfgzUdfpExZmBtM'
}

try:
    conn = psycopg2.connect(**RAILWAY)
    cur = conn.cursor()
    
    # Contar tabelas
    cur.execute("SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public'")
    total_tables = cur.fetchone()[0]
    
    # Contar registros em tabelas principais
    cur.execute('SELECT COUNT(*) FROM "user"')
    users = cur.fetchone()[0]
    
    cur.execute('SELECT COUNT(*) FROM agente_juridico')
    agentes = cur.fetchone()[0]
    
    cur.execute('SELECT COUNT(*) FROM template_juridico')
    templates = cur.fetchone()[0]
    
    print("\n✅ RAILWAY DATABASE - VERIFICAÇÃO")
    print("="*50)
    print("Total de tabelas: {}".format(total_tables))
    print("Usuários: {}".format(users))
    print("Agentes: {}".format(agentes))
    print("Templates: {}".format(templates))
    print("\n🎉 MIGRAÇÃO BEM-SUCEDIDA!")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print("\n❌ Erro: {}".format(e))
