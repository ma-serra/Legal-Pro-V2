#!/usr/bin/env python3
"""
Script para corrigir a distribuição de casos para refletir exatamente os 35 advogados
que são exibidos no dashboard e distribuir os 163 casos entre eles.
"""

import sys
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import random
import math

# Configuração do banco de dados
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    """Cria conexão com o banco de dados"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def get_top_35_lawyers():
    """
    Obtém os mesmos 35 advogados que são exibidos no dashboard
    (ordenados por total_casos descendente, igual ao main.py)
    """
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT advogado_nome, total_casos
            FROM lawyer_metrics 
            ORDER BY total_casos DESC, advogado_nome
            LIMIT 35
        """)
        result = cur.fetchall()
        return [(row['advogado_nome'], row['total_casos']) for row in result]
    finally:
        conn.close()

def get_lawyers_with_areas():
    """Obtém áreas jurídicas dos advogados do processo_juridico"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT advogado_do_caso, area_juridica
            FROM processo_juridico
        """)
        result = cur.fetchall()
        
        lawyer_areas = {}
        for row in result:
            lawyer_areas[row['advogado_do_caso']] = row['area_juridica']
        
        return lawyer_areas
    finally:
        conn.close()

def distribute_163_cases_among_35_lawyers(top_35_lawyers, lawyer_areas):
    """
    Distribui 163 casos entre os 35 advogados de forma equilibrada
    """
    total_casos = 163
    num_lawyers = len(top_35_lawyers)
    
    if num_lawyers != 35:
        print(f"❌ ERRO: Esperados 35 advogados, encontrados {num_lawyers}")
        return {}
    
    # Calcular distribuição base
    casos_por_advogado = total_casos // num_lawyers  # 163 // 35 = 4
    casos_extras = total_casos % num_lawyers  # 163 % 35 = 23
    
    print(f"📊 Distribuindo {total_casos} casos entre {num_lawyers} advogados:")
    print(f"   Base: {casos_por_advogado} casos cada")
    print(f"   {casos_extras} advogados receberão +1 caso (total: {casos_por_advogado + 1})")
    print(f"   {num_lawyers - casos_extras} advogados receberão {casos_por_advogado} casos")
    
    case_distribution = {}
    total_distribuido = 0
    
    # Distribuir casos
    for i, (lawyer_name, current_cases) in enumerate(top_35_lawyers):
        # Primeiros 23 advogados recebem 5 casos, os outros 12 recebem 4 casos
        new_cases = casos_por_advogado + (1 if i < casos_extras else 0)
        area = lawyer_areas.get(lawyer_name, 'N/A')
        
        case_distribution[lawyer_name] = {
            'total_casos': new_cases,
            'area': area,
            'casos_antes': current_cases
        }
        total_distribuido += new_cases
        
        if i < 10:  # Mostrar primeiros 10
            print(f"   {lawyer_name} ({area}): {current_cases} → {new_cases} casos")
    
    print(f"\n✅ Total de casos distribuídos: {total_distribuido}")
    return case_distribution

def reset_other_lawyers_to_zero(top_35_names, dry_run=True):
    """
    Reseta todos os outros advogados (não nos top 35) para 0 casos
    """
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        
        # Buscar todos os advogados que NÃO estão nos top 35
        placeholders = ','.join(['%s'] * len(top_35_names))
        cur.execute(f"""
            SELECT advogado_nome, total_casos 
            FROM lawyer_metrics 
            WHERE advogado_nome NOT IN ({placeholders})
            AND total_casos > 0
        """, top_35_names)
        
        other_lawyers = cur.fetchall()
        print(f"📊 {len(other_lawyers)} advogados fora dos top 35 serão resetados para 0 casos")
        
        if dry_run:
            for lawyer in other_lawyers[:5]:  # Mostrar primeiros 5
                print(f"   {lawyer['advogado_nome']}: {lawyer['total_casos']} → 0 casos")
            if len(other_lawyers) > 5:
                print(f"   ... e mais {len(other_lawyers) - 5} advogados")
            return len(other_lawyers)
        
        # Resetar casos para 0
        if other_lawyers:
            cur.execute(f"""
                UPDATE lawyer_metrics 
                SET total_casos = 0, updated_at = CURRENT_TIMESTAMP
                WHERE advogado_nome NOT IN ({placeholders})
            """, top_35_names)
            
            conn.commit()
            print(f"✅ {len(other_lawyers)} advogados resetados para 0 casos")
        
        return len(other_lawyers)
    finally:
        conn.close()

def update_top_35_cases(case_distribution, dry_run=True):
    """Atualiza os casos dos top 35 advogados"""
    
    if dry_run:
        print("\n🔍 MODO DRY-RUN - Prévia das alterações dos top 35:")
        total_check = 0
        for lawyer, data in list(case_distribution.items())[:10]:
            print(f"   {lawyer} ({data['area']}): {data['casos_antes']} → {data['total_casos']} casos")
            total_check += data['total_casos']
        
        total_final = sum(data['total_casos'] for data in case_distribution.values())
        print(f"\n✅ Total de casos após redistribuição: {total_final}")
        print(f"📊 Deve ser igual a 163: {'✅' if total_final == 163 else '❌'}")
        return
    
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        
        updated_count = 0
        total_casos_final = 0
        
        print(f"✅ Atualizando {len(case_distribution)} advogados dos top 35...")
        
        for lawyer, data in case_distribution.items():
            new_cases = data['total_casos']
            
            # Atualizar na tabela
            cur.execute("""
                UPDATE lawyer_metrics 
                SET 
                    total_casos = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE advogado_nome = %s
            """, (new_cases, lawyer))
            
            if cur.rowcount > 0:
                updated_count += 1
                total_casos_final += new_cases
                
                if updated_count <= 10:  # Mostrar os primeiros 10
                    print(f"   {lawyer}: {data['casos_antes']} → {new_cases} casos")
        
        conn.commit()
        print(f"\n✅ {updated_count} advogados dos top 35 atualizados!")
        print(f"📊 Total de casos final: {total_casos_final}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro ao atualizar banco de dados: {e}")
        raise
    finally:
        conn.close()

def main():
    """Função principal"""
    print("🔄 Iniciando correção da distribuição para 35 advogados...\n")
    
    # Verificar argumentos
    dry_run = "--dry-run" in sys.argv or "--preview" in sys.argv
    confirm = "--confirm" in sys.argv
    
    if not dry_run and not confirm:
        print("❌ Para executar as alterações, use --confirm")
        print("   Para prévia, use --dry-run ou --preview")
        return
    
    # Obter os top 35 advogados (mesmo critério do main.py)
    top_35_lawyers = get_top_35_lawyers()
    print(f"📊 Top 35 advogados encontrados (ordenados por casos):")
    for i, (name, cases) in enumerate(top_35_lawyers[:10]):
        print(f"   {i+1}. {name}: {cases} casos")
    if len(top_35_lawyers) > 10:
        print(f"   ... e mais {len(top_35_lawyers) - 10} advogados")
    
    if len(top_35_lawyers) != 35:
        print(f"❌ ERRO: Esperados 35 advogados, encontrados {len(top_35_lawyers)}")
        return
    
    # Obter áreas dos advogados
    lawyer_areas = get_lawyers_with_areas()
    
    # Distribuir 163 casos entre os 35 advogados
    case_distribution = distribute_163_cases_among_35_lawyers(top_35_lawyers, lawyer_areas)
    
    # Resetar outros advogados para 0
    top_35_names = [name for name, _ in top_35_lawyers]
    reset_count = reset_other_lawyers_to_zero(top_35_names, dry_run=dry_run)
    
    # Atualizar os top 35
    update_top_35_cases(case_distribution, dry_run=dry_run)
    
    if not dry_run:
        print(f"\n✅ Distribuição corrigida com sucesso!")
        print(f"   - 35 advogados com 163 casos distribuídos")
        print(f"   - {reset_count} outros advogados resetados para 0 casos")
        print("   Os cards agora refletem exatamente os 163 casos entre 35 advogados")

if __name__ == "__main__":
    main()