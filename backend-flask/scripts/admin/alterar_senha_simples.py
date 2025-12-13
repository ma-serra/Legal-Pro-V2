#!/usr/bin/env python3
"""
Script simples para alterar senha do usuário dmay
"""

import os
import psycopg2
from werkzeug.security import generate_password_hash

def alterar_senha():
    # Conectar ao banco usando a URL do ambiente
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        return
    
    try:
        # Conectar ao banco
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Nova senha
        nova_senha = "C4rn31r0#425#"
        
        # Gerar hash da senha usando Werkzeug (mesmo método do Flask)
        password_hash = generate_password_hash(nova_senha)
        
        # Atualizar no banco
        cursor.execute('UPDATE "user" SET password_hash = %s WHERE username = %s', 
                      (password_hash, 'dmay'))
        
        # Verificar se alguma linha foi afetada
        if cursor.rowcount > 0:
            conn.commit()
            print("✅ Senha do usuário 'dmay' alterada com sucesso!")
            print(f"🔑 Nova senha: {nova_senha}")
            print("🔒 Use essas credenciais para fazer login no sistema")
        else:
            print("❌ Usuário 'dmay' não encontrado")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao alterar senha: {str(e)}")

if __name__ == "__main__":
    print("🔧 Alterando senha do usuário dmay...")
    alterar_senha()