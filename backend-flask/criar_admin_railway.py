"""
Criador de Admin User - Versão Simplificada
Pede a URL do banco e cria o admin
"""

from werkzeug.security import generate_password_hash
import psycopg2
from urllib.parse import urlparse

def criar_admin_railway():
    print("=" * 70)
    print("🔐 CRIAR USUÁRIO ADMIN NO RAILWAY")
    print("=" * 70)
    
    # Pedir URL do banco
    print("\n📝 Cole a DATABASE_URL do Railway:")
    print("   (No Railway: Postgres service → Connect → Copy DATABASE_URL)")
    database_url = input("\n> ").strip()
    
    if not database_url:
        print("❌ URL do banco não fornecida!")
        return
    
    # Parse da URL
    try:
        parsed = urlparse(database_url)
        
        # Conectar ao banco
        print("\n🔌 Conectando ao banco...")
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path[1:]  # Remove o / inicial
        )
        cursor = conn.cursor()
        
        # Gerar hash da senha
        password_hash = generate_password_hash('admin123')
        
        # Verificar se admin existe
        cursor.execute('SELECT id, username FROM "user" WHERE username = %s', ('admin',))
        admin_existente = cursor.fetchone()
        
        if admin_existente:
            print(f"\n⚠️  Admin já existe (ID: {admin_existente[0]})")
            print("   Atualizando para garantir acesso...")
            
            cursor.execute('''
                UPDATE "user" 
                SET is_admin = true, 
                    active = true, 
                    password_hash = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE username = %s
            ''', (password_hash, 'admin'))
            
            conn.commit()
            print("✅ Admin atualizado com sucesso!")
        else:
            print("\n🔨 Criando novo admin...")
            
            cursor.execute('''
                INSERT INTO "user" 
                (username, email, password_hash, first_name, last_name, 
                 active, is_admin, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', ('admin', 'admin@legalpro.com', password_hash, 
                  'Administrator', 'System', True, True))
            
            conn.commit()
            print("✅ Admin criado com sucesso!")
        
        # Verificar criação
        cursor.execute('SELECT id, username, email, is_admin FROM "user" WHERE username = %s', ('admin',))
        admin = cursor.fetchone()
        
        print("\n" + "=" * 70)
        print("✅ CREDENCIAIS DE ACESSO")
        print("=" * 70)
        print(f"   ID: {admin[0]}")
        print(f"   Username: {admin[1]}")
        print(f"   Email: {admin[2]}")
        print(f"   Password: admin123")
        print(f"   Is Admin: {admin[3]}")
        print("=" * 70)
        
        cursor.close()
        conn.close()
        
        print("\n✅ Tudo pronto! Você pode fazer login agora em:")
        print("   https://hub-legal-pro.vercel.app/login")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        print("\n💡 Verifique se:")
        print("   1. A URL do banco está correta")
        print("   2. Você tem acesso ao banco")
        print("   3. O psycopg2 está instalado: pip install psycopg2-binary")

if __name__ == '__main__':
    criar_admin_railway()
