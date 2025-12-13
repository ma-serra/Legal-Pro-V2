#!/usr/bin/env python3
"""
Sincronização Rápida - Legal Pro
Script simplificado para sincronização rápida entre bases
"""

import os
import psycopg2
import sys
from datetime import datetime

def quick_sync():
    """Sincronização rápida Development → Production"""
    
    print("🔄 SINCRONIZAÇÃO RÁPIDA - LEGAL PRO")
    print("="*40)
    
    # Verificar se todas as variáveis estão disponíveis
    required_vars = ['PGHOST', 'PGDATABASE', 'PGUSER', 'PGPASSWORD', 'PGPORT']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Variáveis não configuradas: {', '.join(missing_vars)}")
        return False
    
    try:
        # Conectar Development
        dev_url = "postgresql://neondb_owner:npg_F3M8RaEktGdQ@ep-withered-smoke-afgjgeem.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require"
        dev_conn = psycopg2.connect(dev_url)
        print("✅ Conectado à base Development")
        
        # Conectar Production
        prod_url = "postgresql://neondb_owner:npg_dNFh9jaHLf7k@ep-sweet-boat-af7qtkoo.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require"
        prod_conn = psycopg2.connect(prod_url)
        print("✅ Conectado à base Production")
        
        # Tabelas para sincronizar
        tables_to_sync = [
            'analise_processo_ia',
            'processo_juridico', 
            'user'
        ]
        
        # Estatísticas comparativas
        for table in tables_to_sync:
            try:
                with dev_conn.cursor() as dev_cur:
                    dev_cur.execute(f"SELECT COUNT(*) FROM {table}")
                    dev_count = dev_cur.fetchone()[0]
                
                with prod_conn.cursor() as prod_cur:
                    prod_cur.execute(f"SELECT COUNT(*) FROM {table}")
                    prod_count = prod_cur.fetchone()[0]
                
                diff = dev_count - prod_count
                status = "✅" if diff == 0 else "⚠️" if abs(diff) < 10 else "❌"
                print(f"{status} {table}: Dev={dev_count}, Prod={prod_count}, Diff={diff:+d}")
            except Exception as e:
                print(f"❌ {table}: Erro ao verificar - {e}")
        
        print("\n🔄 Análise de sincronização concluída")
        print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        dev_conn.close()
        prod_conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

if __name__ == '__main__':
    success = quick_sync()
    sys.exit(0 if success else 1)