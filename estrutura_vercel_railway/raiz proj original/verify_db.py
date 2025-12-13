#!/usr/bin/env python3
import os
import psycopg2
from urllib.parse import urlparse

def verify_environment_variables():
    """Verifica se todas as variáveis estão definidas corretamente"""
    print("=== VERIFICAÇÃO DAS VARIÁVEIS DE AMBIENTE ===")

    # Variáveis esperadas - verificando apenas a presença
    required_vars = ['DATABASE_URL', 'PGDATABASE', 'PGHOST', 'PGPORT', 'PGUSER', 'PGPASSWORD']

    all_ok = True

    for var_name in required_vars:
        actual_value = os.environ.get(var_name)

        if actual_value:
            print(f"✅ {var_name}: DEFINIDA")
        else:
            print(f"❌ {var_name}: NÃO DEFINIDA")
            all_ok = False

    return all_ok

def test_database_connection():
    """Testa a conexão com o banco usando DATABASE_URL"""
    print("\n=== TESTE DE CONEXÃO COM O BANCO ===")

    database_url = os.environ.get('DATABASE_URL')

    if not database_url:
        print("❌ DATABASE_URL não encontrada!")
        return False

    try:
        # Testa conexão usando DATABASE_URL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        # Testa queries básicas
        cursor.execute("SELECT version();")
        version_result = cursor.fetchone()
        version = version_result[0] if version_result else "Versão não disponível"
        print(f"✅ Conexão bem-sucedida!")
        print(f"📊 Versão PostgreSQL: {version}")

        # Testa informações do banco
        cursor.execute("SELECT current_database(), current_user;")
        db_info = cursor.fetchone()
        if db_info:
            print(f"🗄️  Banco atual: {db_info[0]}")
            print(f"👤 Usuário atual: {db_info[1]}")
        else:
            print("❌ Não foi possível obter informações do banco")

        # Lista algumas tabelas (se existirem)
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            LIMIT 5;
        """)
        tables = cursor.fetchall()

        if tables:
            print(f"📋 Tabelas encontradas: {[table[0] for table in tables]}")
        else:
            print("📋 Nenhuma tabela encontrada (banco vazio)")

        cursor.close()
        conn.close()
        return True

    except psycopg2.OperationalError as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_individual_variables():
    """Testa conexão usando variáveis individuais (PGHOST, PGUSER, etc.)"""
    print("\n=== TESTE COM VARIÁVEIS INDIVIDUAIS ===")

    try:
        conn = psycopg2.connect(
            host=os.environ.get('PGHOST'),
            database=os.environ.get('PGDATABASE'),
            user=os.environ.get('PGUSER'),
            password=os.environ.get('PGPASSWORD'),
            port=os.environ.get('PGPORT', '5432'),
            sslmode='require'
        )

        cursor = conn.cursor()
        cursor.execute("SELECT 'Conexão individual OK' as status;")
        result = cursor.fetchone()
        if result:
            print(f"✅ {result[0]}")
        else:
            print("❌ Erro ao verificar status da conexão")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Erro na conexão individual: {e}")
        return False

def main():
    print("🔍 VERIFICANDO CONFIGURAÇÃO DO NEON POSTGRESQL")
    print("=" * 50)

    # 1. Verifica variáveis de ambiente
    vars_ok = verify_environment_variables()

    if not vars_ok:
        print("\n❌ PROBLEMA: Variáveis de ambiente não estão corretas!")
        print("👉 Verifique os Secrets no Replit e reinicie a aplicação")
        return False

    # 2. Testa conexão via DATABASE_URL
    url_connection_ok = test_database_connection()

    # 3. Testa conexão via variáveis individuais
    individual_connection_ok = test_individual_variables()

    # Resultado final
    print("\n" + "=" * 50)
    if vars_ok and url_connection_ok and individual_connection_ok:
        print("🎉 TUDO OK! Configuração do PostgreSQL está correta!")
        print("✅ Variáveis atualizadas com sucesso")
        print("✅ Conexão com Neon funcionando")
    else:
        print("❌ PROBLEMAS ENCONTRADOS:")
        if not vars_ok:
            print("   - Variáveis de ambiente incorretas")
        if not url_connection_ok:
            print("   - Falha na conexão via DATABASE_URL")
        if not individual_connection_ok:
            print("   - Falha na conexão via variáveis individuais")

    return vars_ok and url_connection_ok and individual_connection_ok

if __name__ == "__main__":
    main()