#!/usr/bin/env python3
"""
Script para aplicar schema SaaS V2 no PostgreSQL Railway
Hierarquia: TENANCY → USER → CLIENT
"""

import psycopg2
import sys
import os

# Database URL do Railway
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway')

def apply_saas_schema_v2():
    """Aplica schema SaaS V2 no banco de dados"""
    
    print("=" * 70)
    print("🚀 APLICANDO SCHEMA SAAS V2 - TENANCY → USER → CLIENT")
    print("=" * 70)
    
    try:
        # Conectar ao banco
        print("\n🔌 Conectando ao Railway PostgreSQL...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        print("✅ Conectado com sucesso!")
        
        # Ler arquivo SQL V2
        print("\n📄 Lendo schema SQL V2...")
        with open('saas_schema_v2.sql', 'r', encoding='utf-8') as f:
            sql_schema = f.read()
        
        # Executar SQL
        print("\n⚙️  Executando comandos SQL...")
        cursor.execute(sql_schema)
        conn.commit()
        
        print("✅ Schema V2 aplicado com sucesso!")
        
        # Verificar tabelas criadas
        print("\n🔍 Verificando tabelas SaaS criadas...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('subscription_plans', 'tenancy', 'client', 'subscriptions', 
                              'invoices', 'tenancy_invitations', 'usage_records', 'user_client_access')
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        print(f"\n✅ {len(tables)} tabelas SaaS encontradas:")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Verificar planos criados
        print("\n💰 Verificando planos de assinatura...")
        cursor.execute("SELECT id, name, slug, price_monthly FROM subscription_plans ORDER BY price_monthly")
        plans = cursor.fetchall()
        
        print(f"\n✅ {len(plans)} planos criados:")
        for plan in plans:
            print(f"   - {plan[1]} ({plan[2]}): R$ {plan[3]}/mês")
        
        # Verificar alterações na tabela user
        print("\n👥 Verificando colunas adicionadas à tabela 'user'...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'user' 
            AND column_name IN ('tenancy_id', 'role_in_tenancy')
            ORDER BY column_name
        """)
        user_cols = cursor.fetchall()
        
        if user_cols:
            print(f"✅ Colunas adicionadas à tabela 'user':")
            for col in user_cols:
                print(f"   - {col[0]}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ SCHEMA SAAS V2 APLICADO COM SUCESSO!")
        print("=" * 70)
        print("\n📊 Hierarquia implementada:")
        print("   1️⃣  TENANCY (Cliente do sistema - quem contrata)")
        print("   2️⃣  USER (Usuários - advogados que usam)")
        print("   3️⃣  CLIENT (Clientes atendidos pelo escritório)")
        print("\n📌 Próximos passos:")
        print("   1. Atualizar routes_saas.py com APIs de CLIENT")
        print("   2. Commit e deploy: git push")
        print("   3. Testar signup e client management")
        print("\n🎯 Sistema SaaS pronto para produção!")
        
        return True
        
    except FileNotFoundError:
        print("\n❌ ERRO: Arquivo saas_schema_v2.sql não encontrado!")
        print("   Certifique-se de estar no diretório backend-flask/")
        return False
        
    except Exception as e:
        print(f"\n❌ ERRO ao aplicar schema: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == '__main__':
    success = apply_saas_schema_v2()
    sys.exit(0 if success else 1)
