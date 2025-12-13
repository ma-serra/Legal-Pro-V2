#!/usr/bin/env python3
"""
Script de Migração de Banco de Dados
Migra dados do servidor antigo para Railway PostgreSQL
"""

import subprocess
import os
import sys
from urllib.parse import unquote
from datetime import datetime

# Decodificar caracteres especiais da URL
def decode_db_password(encoded):
    """Decodifica senha com caracteres especiais URL-encoded"""
    return unquote(encoded)

# Configurações do banco ORIGEM (antigo)
SOURCE_HOST = "147.93.68.169"
SOURCE_PORT = "5433"
SOURCE_DB = "hublegalpro_db"
SOURCE_USER = "arsdatascience"
SOURCE_PASSWORD_ENCODED = "xJ%3Erh%7Dzv%3FjU%3B21%3Ft"
SOURCE_PASSWORD = decode_db_password(SOURCE_PASSWORD_ENCODED)  # xJ>rh}zv?jU;21?t

# Configurações do banco DESTINO (Railway)
DEST_HOST = "gondola.proxy.rlwy.net"
DEST_PORT = "11843"
DEST_DB = "railway"
DEST_USER = "postgres"
DEST_PASSWORD = "XKtolNYAChqKElojyEfgzUdfpExZmBtM"

# Arquivo temporário para o dump
DUMP_FILE = f"backup_hublegalpro_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"

def run_command(cmd, env_vars=None):
    """Executa comando com variáveis de ambiente"""
    try:
        print(f"\n🔧 Executando: {cmd[0]}")
        
        # Preparar environment
        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)
        
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout:
            print(f"✅ Output: {result.stdout[:200]}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro: {e}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"❌ Comando não encontrado: {cmd[0]}")
        print(f"💡 Instale PostgreSQL client tools:")
        print(f"   Windows: choco install postgresql")
        print(f"   Linux: sudo apt-get install postgresql-client")
        print(f"   Mac: brew install postgresql")
        return False

def step1_dump_source():
    """Passo 1: Fazer dump do banco origem"""
    print("\n" + "="*60)
    print("📦 PASSO 1: Fazendo backup do banco ORIGEM")
    print("="*60)
    
    cmd = [
        "pg_dump",
        "-h", SOURCE_HOST,
        "-p", SOURCE_PORT,
        "-U", SOURCE_USER,
        "-d", SOURCE_DB,
        "-F", "c",  # Custom format (mais eficiente)
        "-f", DUMP_FILE,
        "--verbose"
    ]
    
    env_vars = {
        "PGPASSWORD": SOURCE_PASSWORD
    }
    
    print(f"🔗 Conectando em: {SOURCE_HOST}:{SOURCE_PORT}/{SOURCE_DB}")
    print(f"👤 Usuário: {SOURCE_USER}")
    print(f"💾 Arquivo: {DUMP_FILE}")
    
    success = run_command(cmd, env_vars)
    
    if success and os.path.exists(DUMP_FILE):
        size = os.path.getsize(DUMP_FILE)
        print(f"✅ Dump criado com sucesso! Tamanho: {size / 1024 / 1024:.2f} MB")
        return True
    else:
        print("❌ Falha ao criar dump")
        return False

def step2_restore_destination():
    """Passo 2: Restaurar no banco Railway"""
    print("\n" + "="*60)
    print("📥 PASSO 2: Restaurando no banco RAILWAY")
    print("="*60)
    
    cmd = [
        "pg_restore",
        "-h", DEST_HOST,
        "-p", DEST_PORT,
        "-U", DEST_USER,
        "-d", DEST_DB,
        "--clean",  # Limpa objetos existentes antes
        "--if-exists",  # Não erro se não existir
        "--no-owner",  # Não define ownership
        "--no-acl",  # Não define permissões
        "--verbose",
        DUMP_FILE
    ]
    
    env_vars = {
        "PGPASSWORD": DEST_PASSWORD
    }
    
    print(f"🔗 Conectando em: {DEST_HOST}:{DEST_PORT}/{DEST_DB}")
    print(f"👤 Usuário: {DEST_USER}")
    print(f"📦 Restaurando de: {DUMP_FILE}")
    
    success = run_command(cmd, env_vars)
    
    if success:
        print("✅ Restore concluído com sucesso!")
        return True
    else:
        print("❌ Falha ao restaurar")
        return False

def step3_verify():
    """Passo 3: Verificar migração"""
    print("\n" + "="*60)
    print("🔍 PASSO 3: Verificando migração")
    print("="*60)
    
    # Contar tabelas no destino
    cmd = [
        "psql",
        "-h", DEST_HOST,
        "-p", DEST_PORT,
        "-U", DEST_USER,
        "-d", DEST_DB,
        "-c", "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"
    ]
    
    env_vars = {
        "PGPASSWORD": DEST_PASSWORD
    }
    
    print("📊 Contando tabelas no Railway...")
    success = run_command(cmd, env_vars)
    
    return success

def cleanup():
    """Remove arquivo temporário"""
    if os.path.exists(DUMP_FILE):
        try:
            os.remove(DUMP_FILE)
            print(f"\n🗑️  Arquivo temporário removido: {DUMP_FILE}")
        except:
            print(f"\n⚠️  Não foi possível remover: {DUMP_FILE}")

def main():
    """Função principal"""
    print("\n" + "="*60)
    print("🚀 MIGRAÇÃO DE BANCO DE DADOS")
    print("="*60)
    print(f"\n📍 ORIGEM: {SOURCE_HOST}:{SOURCE_PORT}/{SOURCE_DB}")
    print(f"📍 DESTINO: {DEST_HOST}:{DEST_PORT}/{DEST_DB}")
    print("\n⚠️  ATENÇÃO: Esta operação irá SUBSTITUIR os dados no Railway!")
    
    input("\n👉 Pressione ENTER para continuar ou Ctrl+C para cancelar...")
    
    # Passo 1: Dump
    if not step1_dump_source():
        print("\n❌ Migração FALHOU no passo 1 (dump)")
        return False
    
    # Passo 2: Restore
    if not step2_restore_destination():
        print("\n❌ Migração FALHOU no passo 2 (restore)")
        cleanup()
        return False
    
    # Passo 3: Verificar
    step3_verify()
    
    # Cleanup
    cleanup()
    
    print("\n" + "="*60)
    print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*60)
    print("\n📋 Próximos passos:")
    print("1. Verifique os dados no Railway")
    print("2. Teste as funcionalidades do sistema")
    print("3. Atualize a variável DATABASE_URL no Railway para:")
    print(f"   postgresql://{DEST_USER}:{DEST_PASSWORD}@{DEST_HOST}:{DEST_PORT}/{DEST_DB}")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário")
        cleanup()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        cleanup()
        sys.exit(1)
