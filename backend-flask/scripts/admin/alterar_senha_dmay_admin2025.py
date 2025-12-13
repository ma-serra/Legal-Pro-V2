#!/usr/bin/env python3
"""
Script para alterar a senha do usuário dmay para admin@2025
"""

import os
import sys
from werkzeug.security import generate_password_hash

# Adicionar o diretório raiz ao Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from models import User, db
    from app import app
    
    def alterar_senha_dmay_admin2025():
        """Altera a senha do usuário dmay para admin@2025"""
        with app.app_context():
            try:
                # Buscar o usuário dmay
                user = User.query.filter_by(username='dmay').first()
                
                if not user:
                    print("❌ Usuário 'dmay' não encontrado!")
                    return False
                
                # Nova senha solicitada
                nova_senha = "admin@2025"
                
                # Gerar hash da nova senha
                password_hash = generate_password_hash(nova_senha)
                
                # Atualizar a senha
                user.password_hash = password_hash
                
                # Garantir que o usuário está ativo e é admin
                user.active = True
                user.is_admin = True
                
                db.session.commit()
                
                print("✅ Senha do usuário 'dmay' alterada com sucesso!")
                print(f"👤 Username: {user.username}")
                print(f"📧 Email: {user.email}")
                print(f"🔑 Nova senha: {nova_senha}")
                print(f"🔧 Admin: {user.is_admin}")
                print(f"✅ Ativo: {user.active}")
                print("🔒 Use essas credenciais para fazer login no sistema")
                
                return True
                
            except Exception as e:
                print(f"❌ Erro ao alterar senha: {str(e)}")
                db.session.rollback()
                return False
    
    if __name__ == "__main__":
        print("🔧 Alterando senha do usuário dmay para admin@2025...")
        sucesso = alterar_senha_dmay_admin2025()
        if sucesso:
            print("✅ Operação concluída com sucesso!")
        else:
            print("❌ Falha na operação")

except ImportError:
    # Fallback usando conexão direta ao PostgreSQL
    import psycopg2
    
    def alterar_senha_postgres():
        """Altera senha usando conexão direta ao PostgreSQL"""
        database_url = os.environ.get('DATABASE_URL')
        
        if not database_url:
            print("❌ DATABASE_URL não encontrada")
            return False
        
        try:
            # Conectar ao banco
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()
            
            # Nova senha
            nova_senha = "admin@2025"
            
            # Gerar hash da senha usando Werkzeug (mesmo método do Flask)
            password_hash = generate_password_hash(nova_senha)
            
            # Atualizar no banco
            cursor.execute('UPDATE "user" SET password_hash = %s, active = true, is_admin = true WHERE username = %s', 
                          (password_hash, 'dmay'))
            
            # Verificar se alguma linha foi afetada
            if cursor.rowcount > 0:
                conn.commit()
                print("✅ Senha do usuário 'dmay' alterada com sucesso!")
                print(f"👤 Username: dmay")
                print(f"🔑 Nova senha: {nova_senha}")
                print("🔧 Admin: True")
                print("✅ Ativo: True")
                print("🔒 Use essas credenciais para fazer login no sistema")
                return True
            else:
                print("❌ Usuário 'dmay' não encontrado")
                return False
            
        except Exception as e:
            print(f"❌ Erro ao alterar senha: {str(e)}")
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    if __name__ == "__main__":
        print("🔧 Alterando senha do usuário dmay para admin@2025 (método PostgreSQL)...")
        sucesso = alterar_senha_postgres()
        if sucesso:
            print("✅ Operação concluída com sucesso!")
        else:
            print("❌ Falha na operação")