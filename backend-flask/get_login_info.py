import psycopg2

db_url = 'postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway'

conn = psycopg2.connect(db_url)
cur = conn.cursor()

cur.execute('SELECT id, username, email, active FROM "user" WHERE username = %s;', ('dmay',))
user = cur.fetchone()

if user:
    print("=== Credenciais de Login ===\n")
    print(f"Email: {user[2]}")
    print(f"Senha: C4rn31r0$425#2025")
    print(f"Status: {'Ativo' if user[3] else 'Inativo'}")
    print(f"\n✅ Use o EMAIL acima para fazer login!")
else:
    print("Usuário não encontrado")

cur.close()
conn.close()
