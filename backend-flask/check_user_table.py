import psycopg2

db_url = 'postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway'

conn = psycopg2.connect(db_url)
cur = conn.cursor()

print("Verificando tabelas de usuario:\n")

# Buscar todas as tabelas que contenham 'user'
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name LIKE '%user%';
""")

tables = cur.fetchall()
print("Tabelas encontradas:")
for t in tables:
    print(f"  - {t[0]}")

# Verificar estrutura da tabela user
if tables:
    table_name = tables[0][0]
    print(f"\nEstrutura da tabela '{table_name}':")
    cur.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = '{table_name}'
        LIMIT 10;
    """)
    for col in cur.fetchall():
        print(f"  - {col[0]}: {col[1]}")

cur.close()
conn.close()
