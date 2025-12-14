#!/usr/bin/env python3
"""
Script para LIMPAR as tabelas SaaS antigas e aplicar V2 limpo
"""

import psycopg2
import sys
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway')

def clean_and_apply_v2():
    """Limpa tabelas antigas e aplica V2"""
    
    print("=" * 70)
    print("🧹 LIMPANDO TABELAS SAAS ANTIGAS E APLICANDO V2")
    print("=" * 70)
    
    try:
        print("\n🔌 Conectando ao Railway PostgreSQL...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        print("✅ Conectado!")
        
        # Dropar tabelas antigas em ordem reversa
        print("\n🗑️  Removendo tabelas SaaS V1 (se existirem)...")
        old_tables = [
            'tenant_invitations',
            'usage_records',
            'invoices',
            'subscriptions',
            'tenants',
        ]
        
        for table in old_tables:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                print(f"   ✓ Removida: {table}")
            except:
                pass
        
        conn.commit()
        print("✅ Tabelas antigas removidas!")
        
        # Limpar colunas antigas da tabela user
        print("\n🧹 Limpando colunas antigas da tabela user...")
        try:
            cursor.execute("ALTER TABLE \"user\" DROP COLUMN IF EXISTS tenant_id CASCADE")
            cursor.execute("ALTER TABLE \"user\" DROP COLUMN IF EXISTS role_in_tenant CASCADE")
            cursor.execute("ALTER TABLE \"user\" DROP COLUMN IF EXISTS tenancy_id CASCADE")
            cursor.execute("ALTER TABLE \"user\" DROP COLUMN IF EXISTS role_in_tenancy CASCADE")
            conn.commit()
            print("✅ Colunas antigas removidas")
        except Exception as e:
            print(f"⚠️  Aviso ao limpar user: {e}")
            conn.rollback()
        
        # Aplicar schema V2
        print("\n📄 Aplicando Schema V2...")
        with open('saas_schema_v2.sql', 'r', encoding='utf-8') as f:
            sql_schema = f.read()
        
        cursor.execute(sql_schema)
        conn.commit()
        
        print("✅ Schema V2 aplicado!")
        
        # Verificar tabelas
        print("\n🔍 Verificando tabelas criadas...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('subscription_plans', 'tenancy', 'client', 
                              'user_client_access', 'subscriptions', 'invoices')
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        print(f"\n✅ {len(tables)} tabelas:")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Verificar planos
        cursor.execute("SELECT COUNT(*) FROM subscription_plans")
        plan_count = cursor.fetchone()[0]
        print(f"\n✅ {plan_count} planos de assinatura criados")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ SCHEMA SAAS V2 INSTALADO COM SUCESSO!")
        print("=" * 70)
        print("\n📊 TENANCY → USER → CLIENT implementado!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == '__main__':
    success = clean_and_apply_v2()
    sys.exit(0 if success else 1)
