#!/usr/bin/env python3
"""
Script de verificação de prontidão para deploy no Render
Verifica se todos os arquivos necessários estão presentes e configurados corretamente
"""

import os
import sys
import json
from pathlib import Path

def check_file_exists(file_path, description):
    """Verifica se um arquivo existe"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - AUSENTE")
        return False

def check_requirements_txt():
    """Verifica o arquivo requirements.txt"""
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
            required_packages = [
                'Flask',
                'gunicorn',
                'psycopg2-binary',
                'SQLAlchemy',
                'Flask-SQLAlchemy',
                'openai'
            ]
            
            missing = []
            for package in required_packages:
                if package.lower() not in content.lower():
                    missing.append(package)
            
            if missing:
                print(f"❌ Pacotes obrigatórios ausentes: {', '.join(missing)}")
                return False
            else:
                print("✅ requirements.txt contém todos os pacotes obrigatórios")
                return True
    except FileNotFoundError:
        print("❌ requirements.txt não encontrado")
        return False

def check_procfile():
    """Verifica o Procfile"""
    try:
        with open('Procfile', 'r') as f:
            content = f.read().strip()
            if 'gunicorn' in content and 'main:app' in content and '$PORT' in content:
                print("✅ Procfile configurado corretamente")
                return True
            else:
                print("❌ Procfile mal configurado")
                return False
    except FileNotFoundError:
        print("❌ Procfile não encontrado")
        return False

def check_main_app():
    """Verifica se main.py existe e tem a estrutura básica"""
    try:
        with open('main.py', 'r') as f:
            content = f.read()
            if 'Flask' in content and 'app' in content:
                print("✅ main.py existe e parece ter estrutura Flask")
                return True
            else:
                print("❌ main.py não parece ser uma aplicação Flask válida")
                return False
    except FileNotFoundError:
        print("❌ main.py não encontrado")
        return False

def check_environment_variables():
    """Lista variáveis de ambiente necessárias"""
    required_vars = [
        'SESSION_SECRET',
        'DATABASE_URL',
        'OPENAI_API_KEY'
    ]
    
    optional_vars = [
        'ANTHROPIC_API_KEY',
        'GOOGLE_API_KEY',
        'ASSEMBLYAI_API_KEY',
        'QDRANT_URL',
        'QDRANT_API_KEY'
    ]
    
    print("\n📋 Variáveis de ambiente OBRIGATÓRIAS para o Render:")
    for var in required_vars:
        print(f"   - {var}")
    
    print("\n📋 Variáveis de ambiente OPCIONAIS:")
    for var in optional_vars:
        print(f"   - {var}")
    
    return True

def main():
    """Função principal de verificação"""
    print("🔍 Verificando prontidão para deploy no Render...\n")
    
    checks = []
    
    # Verificar arquivos essenciais
    checks.append(check_file_exists('Procfile', 'Arquivo de comando do Render'))
    checks.append(check_file_exists('requirements.txt', 'Dependências Python'))
    checks.append(check_file_exists('runtime.txt', 'Versão do Python'))
    checks.append(check_file_exists('main.py', 'Aplicação principal'))
    
    # Verificar arquivos de deploy criados
    checks.append(check_file_exists('render.yaml', 'Configuração automática'))
    checks.append(check_file_exists('gunicorn.conf.py', 'Configuração Gunicorn'))
    checks.append(check_file_exists('.env.example', 'Template de variáveis'))
    checks.append(check_file_exists('README_DEPLOY_RENDER.md', 'Guia de deploy'))
    checks.append(check_file_exists('DEPLOY_CHECKLIST.md', 'Checklist de deploy'))
    
    # Verificações de conteúdo
    checks.append(check_requirements_txt())
    checks.append(check_procfile())
    checks.append(check_main_app())
    
    # Informações sobre variáveis de ambiente
    check_environment_variables()
    
    # Resultado final
    total_checks = len(checks)
    passed_checks = sum(checks)
    
    print(f"\n📊 Resultado: {passed_checks}/{total_checks} verificações passaram")
    
    if passed_checks == total_checks:
        print("🎉 SUCESSO! Aplicação pronta para deploy no Render")
        print("\n📝 Próximos passos:")
        print("1. Commit e push para o GitHub")
        print("2. Criar Web Service no Render")
        print("3. Configurar variáveis de ambiente")
        print("4. Fazer deploy")
        return True
    else:
        print("⚠️  ATENÇÃO! Alguns itens precisam ser corrigidos antes do deploy")
        print("Consulte o README_DEPLOY_RENDER.md para mais detalhes")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)