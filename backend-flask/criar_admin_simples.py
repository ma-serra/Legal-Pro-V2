"""
Script Python simplificado para criar usuário admin
Usa conexão direta com SQLAlchemy
"""

import os
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash

# URL do banco de dados Railway (variável de ambiente)
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/legal_pro')

# Converter postgres:// para postgresql:// se necessário
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

def criar_admin():
    """Cria usuário admin diretamente no banco"""
    
    engine = create_engine(DATABASE_URL)
    
    # Gerar hash da senha
    password_hash = generate_password_hash('admin123')
    
    with engine.connect() as conn:
        # Verificar se admin já existe
        result = conn.execute(text('SELECT id, username, email FROM "user" WHERE username = :username'), 
                            {'username': 'admin'})
        admin_existente = result.fetchone()
        
        if admin_existente:
            print(f"⚠️  Admin já existe: {admin_existente}")
            # Atualizar para garantir que é admin
            conn.execute(
                text('''UPDATE "user" 
                       SET is_admin = true, 
                           active = true, 
                           password_hash = :password_hash,
                           updated_at = CURRENT_TIMESTAMP
                       WHERE username = :username'''),
                {'password_hash': password_hash, 'username': 'admin'}
            )
            conn.commit()
            print("✅ Usuário atualizado para admin com senha 'admin123'")
        else:
            # Criar novo admin
            conn.execute(
                text('''INSERT INTO "user" 
                       (username, email, password_hash, first_name, last_name, 
                        active, is_admin, created_at, updated_at)
                       VALUES (:username, :email, :password_hash, :first_name, :last_name,
                               :active, :is_admin, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)'''),
                {
                    'username': 'admin',
                    'email': 'admin@legalpro.com',
                    'password_hash': password_hash,
                    'first_name': 'Administrator',
                    'last_name': 'System',
                    'active': True,
                    'is_admin': True
                }
            )
            conn.commit()
            print("✅ Usuário admin criado com sucesso!")
        
        print("\n📋 Credenciais:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Email: admin@legalpro.com")

if __name__ == '__main__':
    print("🔐 Criando usuário admin...")
    criar_admin()
