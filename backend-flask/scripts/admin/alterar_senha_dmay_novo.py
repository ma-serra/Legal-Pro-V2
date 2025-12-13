"""
Script para criar/alterar senha do usuário dmay
"""
import os
import sys
from werkzeug.security import generate_password_hash

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def alterar_senha_dmay():
    """Cria ou altera a senha do usuário dmay"""
    try:
        from main import app, db
        from models import User
        
        with app.app_context():
            # Procurar usuário dmay
            user = User.query.filter_by(username='dmay').first()
            
            if user:
                # Usuário existe, alterar senha
                user.password_hash = generate_password_hash('C4rn31r0#425#')
                print("Senha do usuário dmay alterada com sucesso!")
            else:
                # Usuário não existe, criar
                user = User(
                    username='dmay',
                    email='dmay@sistema.com',
                    password_hash=generate_password_hash('C4rn31r0#425#'),
                    first_name='DMAY',
                    last_name='Sistema',
                    is_admin=True,
                    active=True
                )
                db.session.add(user)
                print("Usuário dmay criado com sucesso!")
            
            db.session.commit()
            print("Operação concluída com sucesso!")
            
    except Exception as e:
        print(f"Erro: {str(e)}")
        if 'db' in locals():
            db.session.rollback()

if __name__ == '__main__':
    alterar_senha_dmay()