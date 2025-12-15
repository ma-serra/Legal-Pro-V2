"""
Script para resetar senha do usuário admin
"""
import psycopg2
from werkzeug.security import generate_password_hash

db_url = 'postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway'

# Nova senha
NEW_PASSWORD = 'C4rn31r0$425#2025'

conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()

print("=== Resetando Senha do Usuário ===\n")

# Listar usuários
cur.execute('SELECT id, username, email, active FROM "user";')
users = cur.fetchall()

print(f"Usuários encontrados: {len(users)}\n")
for user in users:
    print(f"ID: {user[0]}, User: {user[1]}, Email: {user[2]}, Ativo: {user[3]}")

if users:
    # Pegar primeiro usuário (admin)
    user_id = users[0][0]
    username = users[0][1]
    
    # Gerar hash da nova senha
    password_hash = generate_password_hash(NEW_PASSWORD)
    
    # Atualizar senha
    cur.execute("""
        UPDATE "user" 
        SET password_hash = %s, active = TRUE
        WHERE id = %s;
    """, (password_hash, user_id))
    
    print(f"\n✅ Senha resetada com sucesso!")
    print(f"\nCredenciais de acesso:")
    print(f"  Username: {username}")
    print(f"  Password: {NEW_PASSWORD}")
    print(f"\n⚠️  IMPORTANTE: Trocar esta senha após o login!")

cur.close()
conn.close()
