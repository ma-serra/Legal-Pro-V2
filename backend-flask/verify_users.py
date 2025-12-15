import psycopg2

db_url = 'postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway'

conn = psycopg2.connect(db_url)
cur = conn.cursor()

# Ver colunas
cur.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'user'
    ORDER BY ordinal_position;
""")
print("Colunas da tabela user:")
colunas = [row[0] for row in cur.fetchall()]
for col in colunas:
    print(f"  - {col}")

# Contar usuários
cur.execute('SELECT COUNT(*) FROM "user";')
print(f"\nTotal: {cur.fetchone()[0]} usuário(s)")

# Listar apenas ID e username
cur.execute('SELECT id, username FROM "user" LIMIT 5;')
print("\nUsuários:")
for row in cur.fetchall():
    print(f"  ID: {row[0]}, Username: {row[1]}")

cur.close()
conn.close()
