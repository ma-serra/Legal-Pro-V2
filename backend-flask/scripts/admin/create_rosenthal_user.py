"""
Script para criar o usuário rosenthal com senha específica e privilégios de administrador
"""

from werkzeug.security import generate_password_hash
from models import db, User
from main import create_app

def create_rosenthal_user():
    """Cria o usuário rosenthal com a senha especificada e privilégios de administrador"""
    app = create_app()
    
    with app.app_context():
        # Verificar se o usuário já existe
        existing_user = User.query.filter_by(username='rosenthal').first()
        
        if existing_user:
            # Atualizar senha e privilégios do usuário existente
            existing_user.password_hash = generate_password_hash('rosenthal#2025@')
            existing_user.is_admin = True
            existing_user.active = True
            db.session.commit()
            print("✅ Usuário rosenthal atualizado com sucesso!")
            print("   • Username: rosenthal")
            print("   • Senha: rosenthal#2025@")
            print("   • Status: Administrador")
        else:
            # Criar novo usuário
            new_user = User(
                username='rosenthal',
                email='rosenthal@sistema.com',
                password_hash=generate_password_hash('rosenthal#2025@'),
                first_name='Rosenthal',
                last_name='Admin',
                is_admin=True,  # Definir como administrador
                active=True
            )
            
            db.session.add(new_user)
            db.session.commit()
            print("✅ Usuário rosenthal criado com sucesso!")
            print("   • Username: rosenthal")
            print("   • Email: rosenthal@sistema.com")
            print("   • Senha: rosenthal#2025@")
            print("   • Status: Administrador")
            print("   • Nome: Rosenthal Admin")

if __name__ == '__main__':
    create_rosenthal_user()
