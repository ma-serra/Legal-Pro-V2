#!/usr/bin/env python3
"""
Script para alterar a senha do usuário dmay
"""

import os
import sys
from werkzeug.security import generate_password_hash

# Adicionar o diretório raiz ao Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import User, db
from app import app

def alterar_senha_dmay():
    """Altera a senha do usuário dmay"""
    with app.app_context():
        try:
            # Buscar o usuário dmay
            user = User.query.filter_by(username='dmay').first()
            
            if not user:
                print("❌ Usuário 'dmay' não encontrado!")
                return False
            
            # Nova senha
            nova_senha = "C4rn31r0#425#"
            
            # Gerar hash da nova senha
            password_hash = generate_password_hash(nova_senha)
            
            # Atualizar a senha
            user.password_hash = password_hash
            db.session.commit()
            
            print(f"✅ Senha do usuário '{user.username}' alterada com sucesso!")
            print(f"📧 Email: {user.email}")
            print(f"🔑 Nova senha: {nova_senha}")
            print("🔒 Use essas credenciais para fazer login no sistema")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao alterar senha: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("🔧 Alterando senha do usuário dmay...")
    alterar_senha_dmay()