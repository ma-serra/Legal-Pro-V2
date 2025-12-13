"""
Script para criar usuário administrador temporário
"""
from main import app
from models import User, Role, db
from werkzeug.security import generate_password_hash

def create_admin_user():
    with app.app_context():
        try:
            # Verificar se já existe usuário admin
            admin_user = User.query.filter_by(username='admin').first()
            if admin_user:
                print("Usuário admin já existe")
                admin_user.is_admin = True
                db.session.commit()
                return
            
            # Criar role de admin se não existir
            admin_role = Role.query.filter_by(name='admin').first()
            if not admin_role:
                admin_role = Role()
                admin_role.name = 'admin'
                admin_role.description = 'Administrador do sistema'
                db.session.add(admin_role)
                db.session.commit()
            
            # Criar usuário admin
            admin_user = User()
            admin_user.username = 'admin'
            admin_user.email = 'admin@sistema.com'
            admin_user.password_hash = generate_password_hash('admin123')
            admin_user.is_admin = True
            admin_user.active = True
            admin_user.first_name = 'Administrador'
            admin_user.last_name = 'Sistema'
            admin_user.role_id = admin_role.id
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("✅ Usuário administrador criado com sucesso!")
            print("Username: admin")
            print("Password: admin123")
            
        except Exception as e:
            print(f"❌ Erro ao criar usuário admin: {e}")
            db.session.rollback()

if __name__ == "__main__":
    create_admin_user()