#!/usr/bin/env python3
"""
Script para redefinir senha do usuário
"""
import os
import sys
from werkzeug.security import generate_password_hash
from sqlalchemy import create_engine, text

def reset_password():
    # Configurar conexão com banco
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        return False
    
    engine = create_engine(database_url)
    
    # Gerar hash da senha "admin123"
    password_hash = generate_password_hash("admin123")
    print(f"✅ Hash gerado: {password_hash}")
    
    # Atualizar senha no banco
    with engine.connect() as conn:
        result = conn.execute(
            text('UPDATE "user" SET password_hash = :hash WHERE username = :username'),
            {"hash": password_hash, "username": "dmay"}
        )
        conn.commit()
        print(f"✅ Senha atualizada para usuário 'dmay'")
        print("🔑 Credenciais: dmay / admin123")
    
    return True

if __name__ == "__main__":
    reset_password()