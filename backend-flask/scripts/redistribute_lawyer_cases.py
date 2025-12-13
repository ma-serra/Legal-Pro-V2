#!/usr/bin/env python3
"""
Script para redistribuir os casos entre advogados baseado na distribuição proporcional por área jurídica.
Mantém o total de 163 processos distribuídos proporcionalmente às áreas jurídicas existentes.
"""

import sys
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import math

# Configuração do banco de dados
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    """Cria conexão com o banco de dados"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def get_area_distribution():
    """Obtém a distribuição atual de processos por área jurídica"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT area_juridica, COUNT(*) as total_processos 
            FROM processo_juridico 
            GROUP BY area_juridica 
            ORDER BY total_processos DESC
        """)
        result = cur.fetchall()
        return [(row['area_juridica'], row['total_processos']) for row in result]
    finally:
        conn.close()

def get_lawyers_by_area():
    """Obtém os advogados que trabalham em cada área jurídica"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT advogado_do_caso, area_juridica, COUNT(*) as casos 
            FROM processo_juridico 
            GROUP BY advogado_do_caso, area_juridica 
            ORDER BY area_juridica, casos DESC
        """)
        result = cur.fetchall()
        
        lawyers_by_area = {}
        for row in result:
            area = row['area_juridica']
            lawyer = row['advogado_do_caso']
            cases = row['casos']
            
            if area not in lawyers_by_area:
                lawyers_by_area[area] = []
            lawyers_by_area[area].append((lawyer, cases))
        
        return lawyers_by_area
    finally:
        conn.close()

def calculate_proportional_distribution(total_cases=163):
    """Calcula a distribuição proporcional baseada na distribuição real de processos"""
    area_distribution = get_area_distribution()
    total_real_cases = sum(count for _, count in area_distribution)
    
    print(f"📊 Distribuição atual de processos por área:")
    for area, count in area_distribution:
        percentage = (count / total_real_cases) * 100
        print(f"   {area}: {count} processos ({percentage:.1f}%)")
    
    # Calcular targets proporcionais
    area_targets = {}
    allocated_so_far = 0
    remainders = []
    
    for area, count in area_distribution:
        proportion = count / total_real_cases
        target = proportion * total_cases
        floor_target = math.floor(target)
        remainder = target - floor_target
        
        area_targets[area] = floor_target
        allocated_so_far += floor_target
        remainders.append((remainder, area))
    
    # Distribuir os casos restantes usando largest remainder method
    remaining = total_cases - allocated_so_far
    remainders.sort(reverse=True)  # Maiores restos primeiro
    
    for i in range(remaining):
        _, area = remainders[i]
        area_targets[area] += 1
    
    print(f"\n🎯 Metas proporcionais para {total_cases} casos:")
    for area, target in area_targets.items():
        print(f"   {area}: {target} casos")
    
    return area_targets

def distribute_cases_to_lawyers(area_targets):
    """Distribui os casos de cada área entre os advogados dessa área"""
    lawyers_by_area = get_lawyers_by_area()
    lawyer_totals = {}
    
    for area, target_cases in area_targets.items():
        if area not in lawyers_by_area:
            print(f"⚠️  Área {area} não tem advogados históricos")
            continue
            
        area_lawyers = lawyers_by_area[area]
        total_historical_cases = sum(cases for _, cases in area_lawyers)
        
        print(f"\n📍 Distribuindo {target_cases} casos para {area}:")
        print(f"   Advogados na área: {len(area_lawyers)}")
        
        allocated_in_area = 0
        remainders = []
        
        # Primeira passada: casos baseados na proporção histórica
        for lawyer, historical_cases in area_lawyers:
            if total_historical_cases > 0:
                proportion = historical_cases / total_historical_cases
            else:
                proportion = 1.0 / len(area_lawyers)  # Divisão igual se não há histórico
                
            target = proportion * target_cases
            floor_target = math.floor(target)
            remainder = target - floor_target
            
            if lawyer not in lawyer_totals:
                lawyer_totals[lawyer] = 0
            
            lawyer_totals[lawyer] += floor_target
            allocated_in_area += floor_target
            remainders.append((remainder, lawyer))
            
            print(f"      {lawyer}: {floor_target} casos (proporção: {proportion:.3f})")
        
        # Segunda passada: distribuir resto usando largest remainder
        remaining_in_area = target_cases - allocated_in_area
        remainders.sort(reverse=True)
        
        for i in range(remaining_in_area):
            if i < len(remainders):
                _, lawyer = remainders[i]
                lawyer_totals[lawyer] += 1
                print(f"      {lawyer}: +1 caso (resto)")
    
    return lawyer_totals

def update_lawyer_metrics(lawyer_totals, dry_run=True):
    """Atualiza a tabela lawyer_metrics com os novos totais"""
    total_sum = sum(lawyer_totals.values())
    
    if dry_run:
        print(f"\n🔍 MODO DRY-RUN - Prévia das alterações:")
        print(f"   Total de casos a serem distribuídos: {total_sum}")
        
        for lawyer, total in sorted(lawyer_totals.items(), key=lambda x: x[1], reverse=True):
            print(f"   {lawyer}: {total} casos")
        
        return total_sum
    
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        updated_count = 0
        
        print(f"\n✅ Atualizando {len(lawyer_totals)} advogados...")
        
        for lawyer, total in lawyer_totals.items():
            # Verificar se o advogado existe na tabela
            cur.execute("SELECT total_casos FROM lawyer_metrics WHERE advogado_nome = %s", (lawyer,))
            result = cur.fetchone()
            
            if result:
                old_total = result['total_casos']
                cur.execute(
                    "UPDATE lawyer_metrics SET total_casos = %s WHERE advogado_nome = %s",
                    (total, lawyer)
                )
                updated_count += 1
                print(f"   {lawyer}: {old_total} → {total} casos")
            else:
                print(f"   ⚠️  Advogado {lawyer} não encontrado na tabela lawyer_metrics")
        
        conn.commit()
        print(f"\n✅ {updated_count} advogados atualizados")
        print(f"   Total distribuído: {total_sum} casos")
        
        return total_sum
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro ao atualizar banco de dados: {e}")
        raise
    finally:
        conn.close()

def main():
    """Função principal"""
    print("🔄 Iniciando redistribuição de casos entre advogados...\n")
    
    # Verificar argumentos
    dry_run = "--dry-run" in sys.argv or "--preview" in sys.argv
    confirm = "--confirm" in sys.argv
    
    if not dry_run and not confirm:
        print("❌ Para executar as alterações, use --confirm")
        print("   Para prévia, use --dry-run ou --preview")
        return
    
    # Calcular distribuição proporcional
    area_targets = calculate_proportional_distribution(total_cases=163)
    
    # Distribuir casos entre advogados
    lawyer_totals = distribute_cases_to_lawyers(area_targets)
    
    # Atualizar banco de dados
    total_distributed = update_lawyer_metrics(lawyer_totals, dry_run=dry_run)
    
    if total_distributed == 163:
        print(f"\n✅ Distribuição concluída com sucesso! Total: {total_distributed} casos")
    else:
        print(f"\n⚠️  Aviso: Total distribuído ({total_distributed}) difere do esperado (163)")

if __name__ == "__main__":
    main()