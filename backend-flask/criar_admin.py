"""
Script para criar usuário administrador
Execute este script para criar um admin no banco de dados
"""

from main import app, db
from models import User
from werkzeug.security import generate_password_hash
import sys

def criar_usuario_admin():
    """Cria usuário administrador no banco de dados"""
    
    with app.app_context():
        try:
            # Verificar se admin já existe
            admin_existente = User.query.filter_by(username='admin').first()
            
            if admin_existente:
                print("⚠️  Usuário 'admin' já existe!")
                print(f"   ID: {admin_existente.id}")
                print(f"   Email: {admin_existente.email}")
                print(f"   Admin: {admin_existente.is_admin}")
                
                resposta = input("\n❓ Deseja redefinir a senha? (s/n): ").lower()
                if resposta == 's':
                    admin_existente.set_password('admin123')
                    admin_existente.is_admin = True
                    admin_existente.active = True
                    db.session.commit()
                    print("✅ Senha redefinida para 'admin123'")
                    print("✅ Usuário configurado como admin ativo")
                return
            
            # Criar novo usuário admin
            print("🔨 Criando novo usuário administrador...")
            
            novo_admin = User(
                username='admin',
                email='admin@legalpro.com',
                first_name='Administrator',
                last_name='System',
                is_admin=True,
                active=True
            )
            
            # Definir senha
            novo_admin.set_password('admin123')
            
            # Adicionar ao banco
            db.session.add(novo_admin)
            db.session.commit()
            
            print("✅ Usuário administrador criado com sucesso!")
            print("\n📋 Credenciais de acesso:")
            print("   Username: admin")
            print("   Email: admin@legalpro.com")
            print("   Password: admin123")
            print("\n⚠️  IMPORTANTE: Altere a senha após o primeiro login!")
            
        except Exception as e:
            print(f"❌ Erro ao criar usuário: {e}")
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    print("=" * 60)
    print("🔐 CRIAÇÃO DE USUÁRIO ADMINISTRADOR")
    print("=" * 60)
    criar_usuario_admin()
    print("=" * 60)
