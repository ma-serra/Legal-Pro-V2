#!/usr/bin/env python3
"""
Script para remover os advogados com 0 casos da tabela lawyer_metrics
para evitar conflitos futuros e manter apenas os 35 advogados ativos.
"""

import sys
import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuração do banco de dados
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    """Cria conexão com o banco de dados"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def get_lawyers_with_zero_cases():
    """Obtém a lista de advogados com 0 casos"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT advogado_nome, total_casos, created_at, updated_at
            FROM lawyer_metrics 
            WHERE total_casos = 0
            ORDER BY advogado_nome
        """)
        result = cur.fetchall()
        return result
    finally:
        conn.close()

def remove_zero_case_lawyers(dry_run=True):
    """Remove os advogados com 0 casos da tabela"""
    
    # Primeiro, verificar quantos registros serão removidos
    zero_case_lawyers = get_lawyers_with_zero_cases()
    total_count = len(zero_case_lawyers)
    
    print(f"📊 Encontrados {total_count} advogados com 0 casos")
    
    if total_count == 0:
        print("✅ Nenhum advogado com 0 casos encontrado!")
        return
    
    if dry_run:
        print("\n🔍 MODO DRY-RUN - Prévia dos advogados que serão removidos:")
        for i, lawyer in enumerate(zero_case_lawyers[:10]):
            print(f"   {i+1}. {lawyer['advogado_nome']} (casos: {lawyer['total_casos']})")
        
        if total_count > 10:
            print(f"   ... e mais {total_count - 10} advogados")
        
        print(f"\n⚠️  Total a ser removido: {total_count} registros")
        print("   Use --confirm para executar a remoção")
        return
    
    # Executar a remoção
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        
        print(f"🗑️  Removendo {total_count} advogados com 0 casos...")
        
        # Executar DELETE
        cur.execute("""
            DELETE FROM lawyer_metrics 
            WHERE total_casos = 0
        """)
        
        deleted_count = cur.rowcount
        conn.commit()
        
        print(f"✅ {deleted_count} advogados removidos com sucesso!")
        
        # Verificar resultado final
        cur.execute("SELECT COUNT(*) as total_remaining FROM lawyer_metrics")
        remaining = cur.fetchone()['total_remaining']
        
        cur.execute("SELECT SUM(total_casos) as total_cases FROM lawyer_metrics")
        total_cases = cur.fetchone()['total_cases']
        
        print(f"📊 Resultado final:")
        print(f"   - Advogados restantes: {remaining}")
        print(f"   - Total de casos: {total_cases}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro ao remover registros: {e}")
        raise
    finally:
        conn.close()

def main():
    """Função principal"""
    print("🧹 Iniciando limpeza de advogados com 0 casos...\n")
    
    # Verificar argumentos
    dry_run = "--dry-run" in sys.argv or "--preview" in sys.argv
    confirm = "--confirm" in sys.argv
    
    if not dry_run and not confirm:
        print("❌ Para executar a remoção, use --confirm")
        print("   Para prévia, use --dry-run ou --preview")
        return
    
    # Verificar estado atual
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) as total FROM lawyer_metrics")
        total_lawyers = cur.fetchone()['total']
        
        cur.execute("SELECT COUNT(*) as active FROM lawyer_metrics WHERE total_casos > 0")
        active_lawyers = cur.fetchone()['active']
        
        cur.execute("SELECT COUNT(*) as zero FROM lawyer_metrics WHERE total_casos = 0")
        zero_lawyers = cur.fetchone()['zero']
        
        print(f"📊 Estado atual da tabela lawyer_metrics:")
        print(f"   - Total de advogados: {total_lawyers}")
        print(f"   - Advogados ativos (casos > 0): {active_lawyers}")
        print(f"   - Advogados com 0 casos: {zero_lawyers}")
        print()
        
    finally:
        conn.close()
    
    # Executar limpeza
    remove_zero_case_lawyers(dry_run=dry_run)
    
    if not dry_run:
        print(f"\n✅ Limpeza concluída com sucesso!")
        print("   A tabela lawyer_metrics agora contém apenas os advogados ativos")
        print("   Isso evitará conflitos futuros no sistema")

if __name__ == "__main__":
    main()