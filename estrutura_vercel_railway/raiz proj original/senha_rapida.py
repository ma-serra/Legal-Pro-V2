#!/usr/bin/env python3
"""Script rápido para alterar senha do usuário dmay"""

import os
import sys
from werkzeug.security import generate_password_hash
import psycopg2

def alterar_senha():
    try:
        # Conectar ao banco
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cursor = conn.cursor()
        
        # Gerar hash da senha
        nova_senha = "123456"
        senha_hash = generate_password_hash(nova_senha)
        
        # Atualizar senha
        cursor.execute('UPDATE "user" SET password_hash = %s WHERE username = %s', (senha_hash, 'dmay'))
        conn.commit()
        
        print(f"✅ Senha alterada para: {nova_senha}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    alterar_senha()