"""
Script para criar o usuário dmay com senha específica
"""

from werkzeug.security import generate_password_hash
from models import db, User
from main import create_app

def create_dmay_user():
    """Cria o usuário dmay com a senha especificada"""
    app = create_app()
    
    with app.app_context():
        # Verificar se o usuário já existe
        existing_user = User.query.filter_by(username='dmay').first()
        
        if existing_user:
            # Atualizar senha do usuário existente
            existing_user.password_hash = generate_password_hash('C4rn31r0$425$')
            db.session.commit()
            print("Senha do usuário dmay atualizada com sucesso!")
        else:
            # Criar novo usuário
            new_user = User(
                username='dmay',
                email='dmay@sistema.com',
                password_hash=generate_password_hash('C4rn31r0$425$'),
                is_admin=True  # Definir como admin
            )
            
            db.session.add(new_user)
            db.session.commit()
            print("Usuário dmay criado com sucesso!")

if __name__ == '__main__':
    create_dmay_user()