"""
Script para criar usuário admin no Railway PostgreSQL
Conecta direto e cria com hash de senha correto
"""

import psycopg2
from werkzeug.security import generate_password_hash
from urllib.parse import urlparse

# Dados de conexão Railway
DATABASE_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"

# Dados do usuário
EMAIL = "arsdatascience@gmail.com"
USERNAME = "dmay"
PASSWORD = "C4rn31r0$425#401!"
FIRST_NAME = "Denis"
LAST_NAME = "May"

def criar_usuario_admin():
    """Cria usuário admin com senha hashada corretamente"""
    
    print("=" * 70)
    print("🔐 CRIANDO USUÁRIO ADMIN NO RAILWAY")
    print("=" * 70)
    
    # Parse da URL
    parsed = urlparse(DATABASE_URL)
    
    try:
        # Conectar ao banco
        print("\n🔌 Conectando ao Railway PostgreSQL...")
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path[1:]  # Remove o / inicial
        )
        cursor = conn.cursor()
        print("✅ Conectado com sucesso!")
        
        # Gerar hash da senha
        print(f"\n🔒 Gerando hash da senha...")
        password_hash = generate_password_hash(PASSWORD)
        print(f"✅ Hash gerado: {password_hash[:50]}...")
        
        # Verificar se usuário existe
        print(f"\n🔍 Verificando se usuário já existe...")
        cursor.execute('SELECT id, username, email FROM "user" WHERE email = %s', (EMAIL,))
        usuario_existente = cursor.fetchone()
        
        if usuario_existente:
            print(f"⚠️  Usuário já existe (ID: {usuario_existente[0]})")
            print(f"   Deletando usuário antigo...")
            cursor.execute('DELETE FROM "user" WHERE email = %s', (EMAIL,))
            conn.commit()
            print("✅ Usuário antigo deletado")
        
        # Criar novo usuário
        print(f"\n🔨 Criando novo usuário admin...")
        cursor.execute('''
            INSERT INTO "user" 
            (username, email, password_hash, first_name, last_name, 
             active, is_admin, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        ''', (USERNAME, EMAIL, password_hash, FIRST_NAME, LAST_NAME, True, True))
        
        conn.commit()
        print("✅ Usuário criado com sucesso!")
        
        # Verificar criação
        print(f"\n✓ Verificando criação...")
        cursor.execute('''
            SELECT id, username, email, is_admin, active, created_at
            FROM "user" 
            WHERE email = %s
        ''', (EMAIL,))
        usuario = cursor.fetchone()
        
        print("\n" + "=" * 70)
        print("✅ USUÁRIO ADMIN CRIADO COM SUCESSO!")
        print("=" * 70)
        print(f"ID: {usuario[0]}")
        print(f"Username: {usuario[1]}")
        print(f"Email: {usuario[2]}")
        print(f"Is Admin: {usuario[3]}")
        print(f"Active: {usuario[4]}")
        print(f"Created: {usuario[5]}")
        print("=" * 70)
        print("\n🔐 CREDENCIAIS DE LOGIN:")
        print(f"   Email: {EMAIL}")
        print(f"   Senha: {PASSWORD}")
        print("=" * 70)
        print("\n✅ Teste agora em: https://hub-legal-pro.vercel.app/login")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        print(traceback.format_exc())
        print("\n💡 Verifique:")
        print("   1. A URL do banco está correta")
        print("   2. Você tem psycopg2 instalado: pip install psycopg2-binary")
        print("   3. Você tem werkzeug instalado: pip install werkzeug")

if __name__ == '__main__':
    criar_usuario_admin()
