#!/usr/bin/env python3
"""
Script para atualizar a performance dos advogados baseado em dados realistas:
1. Campo "provisão vs pagamento" baseado na performance das áreas com variação aleatória
2. Campos "carteira", "remuneração" e "capital de giro" com valores realistas
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

def get_area_performance():
    """Obtém a performance de provisão vs pagamento por área jurídica"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                area_juridica,
                SUM(valor_da_causa) * 0.23 as provisao_total,
                SUM(COALESCE(pagamento, 0)) as pagamento_realizado,
                CASE 
                    WHEN SUM(valor_da_causa) * 0.23 > 0 
                    THEN (SUM(COALESCE(pagamento, 0)) / (SUM(valor_da_causa) * 0.23) * 100)
                    ELSE 0 
                END as taxa_realizacao
            FROM processo_juridico 
            GROUP BY area_juridica 
            ORDER BY taxa_realizacao DESC
        """)
        result = cur.fetchall()
        
        area_performance = {}
        for row in result:
            area_performance[row['area_juridica']] = {
                'taxa_realizacao': float(row['taxa_realizacao']),
                'provisao_total': float(row['provisao_total']),
                'pagamento_realizado': float(row['pagamento_realizado'])
            }
        
        return area_performance
    finally:
        conn.close()

def get_lawyer_areas():
    """Obtém a área jurídica principal de cada advogado"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT advogado_do_caso, area_juridica
            FROM processo_juridico 
            GROUP BY advogado_do_caso, area_juridica
            ORDER BY advogado_do_caso
        """)
        result = cur.fetchall()
        
        lawyer_areas = {}
        for row in result:
            lawyer_areas[row['advogado_do_caso']] = row['area_juridica']
        
        return lawyer_areas
    finally:
        conn.close()

def get_financial_baselines():
    """Obtém valores base financeiros do sistema para calcular valores realistas"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        
        # Valores totais do sistema
        cur.execute("""
            SELECT 
                SUM(valor_da_causa) as valor_total_causas,
                COUNT(*) as total_processos,
                AVG(valor_da_causa) as valor_medio_causa
            FROM processo_juridico
        """)
        totals = cur.fetchone()
        
        return {
            'valor_total_causas': float(totals['valor_total_causas'] or 0),
            'total_processos': int(totals['total_processos'] or 0),
            'valor_medio_causa': float(totals['valor_medio_causa'] or 0)
        }
    finally:
        conn.close()

def calculate_realistic_values(total_casos, area_performance_rate, financial_baselines):
    """Calcula valores realistas para carteira, remuneração e capital de giro"""
    
    # Valor médio por caso baseado nos dados reais
    base_value_per_case = financial_baselines['valor_medio_causa']
    
    # Carteira total: baseada no número de casos e valor médio com variação
    variacao_carteira = random.uniform(0.7, 1.5)  # Variação entre 70% e 150%
    carteira_total = total_casos * base_value_per_case * variacao_carteira
    
    # Remuneração: entre 10% e 20% da carteira total (padrão advocacia)
    taxa_remuneracao = random.uniform(0.10, 0.20)
    remuneracao = carteira_total * taxa_remuneracao
    
    # Capital de giro: entre 15% e 30% da carteira total
    taxa_capital_giro = random.uniform(0.15, 0.30)
    capital_giro = carteira_total * taxa_capital_giro
    
    # Provisão vs pagamento: baseado na performance da área com variação individual
    # Variação de ±15% da taxa da área
    variacao_individual = random.uniform(-15, 15)
    provisao_vs_pagamento = max(10, min(100, area_performance_rate + variacao_individual))
    
    return {
        'carteira_total': round(carteira_total, 2),
        'remuneracao': round(remuneracao, 2),
        'capital_giro_necessario': round(capital_giro, 2),
        'provisao_vs_pagamento': round(provisao_vs_pagamento, 1)
    }

def update_lawyer_metrics(dry_run=True):
    """Atualiza as métricas dos advogados com valores realistas"""
    
    # Obter dados base
    area_performance = get_area_performance()
    lawyer_areas = get_lawyer_areas()
    financial_baselines = get_financial_baselines()
    
    print(f"📊 Performance por área jurídica:")
    for area, perf in sorted(area_performance.items(), key=lambda x: x[1]['taxa_realizacao'], reverse=True):
        print(f"   {area}: {perf['taxa_realizacao']:.1f}%")
    
    print(f"\n💰 Valores base do sistema:")
    print(f"   Total de processos: {financial_baselines['total_processos']}")
    print(f"   Valor total das causas: R$ {financial_baselines['valor_total_causas']:,.2f}")
    print(f"   Valor médio por causa: R$ {financial_baselines['valor_medio_causa']:,.2f}")
    
    if dry_run:
        print(f"\n🔍 MODO DRY-RUN - Prévia das alterações:")
        
        # Mostrar alguns exemplos
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT advogado_nome, total_casos FROM lawyer_metrics ORDER BY total_casos DESC LIMIT 10")
            lawyers = cur.fetchall()
            
            for lawyer in lawyers:
                lawyer_name = lawyer['advogado_nome']
                total_casos = lawyer['total_casos']
                
                # Buscar área do advogado
                area = lawyer_areas.get(lawyer_name, 'Direito Civil')  # Default se não encontrar
                area_rate = area_performance.get(area, {'taxa_realizacao': 50})['taxa_realizacao']
                
                # Calcular novos valores
                new_values = calculate_realistic_values(total_casos, area_rate, financial_baselines)
                
                print(f"   {lawyer_name} ({area}):")
                print(f"      Total casos: {total_casos}")
                print(f"      Taxa área: {area_rate:.1f}% → Nova taxa individual: {new_values['provisao_vs_pagamento']:.1f}%")
                print(f"      Nova carteira: R$ {new_values['carteira_total']:,.2f}")
                print(f"      Nova remuneração: R$ {new_values['remuneracao']:,.2f}")
                print(f"      Novo capital de giro: R$ {new_values['capital_giro_necessario']:,.2f}")
                print()
        finally:
            conn.close()
        
        return
    
    # Atualizar todos os advogados
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        
        # Buscar todos os advogados
        cur.execute("SELECT advogado_nome, total_casos FROM lawyer_metrics")
        lawyers = cur.fetchall()
        
        updated_count = 0
        print(f"\n✅ Atualizando {len(lawyers)} advogados...")
        
        for lawyer in lawyers:
            lawyer_name = lawyer['advogado_nome']
            total_casos = lawyer['total_casos']
            
            # Buscar área do advogado
            area = lawyer_areas.get(lawyer_name, 'Direito Civil')  # Default se não encontrar
            area_rate = area_performance.get(area, {'taxa_realizacao': 50})['taxa_realizacao']
            
            # Calcular novos valores
            new_values = calculate_realistic_values(total_casos, area_rate, financial_baselines)
            
            # Atualizar no banco
            cur.execute("""
                UPDATE lawyer_metrics 
                SET 
                    carteira_total = %s,
                    remuneracao = %s,
                    capital_giro_necessario = %s,
                    provisao_vs_pagamento = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE advogado_nome = %s
            """, (
                new_values['carteira_total'],
                new_values['remuneracao'],
                new_values['capital_giro_necessario'],
                new_values['provisao_vs_pagamento'],
                lawyer_name
            ))
            
            updated_count += 1
            
            if updated_count <= 10:  # Mostrar os primeiros 10
                print(f"   {lawyer_name} ({area}): Taxa {area_rate:.1f}% → {new_values['provisao_vs_pagamento']:.1f}%")
        
        conn.commit()
        print(f"\n✅ {updated_count} advogados atualizados com sucesso!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro ao atualizar banco de dados: {e}")
        raise
    finally:
        conn.close()

def main():
    """Função principal"""
    print("🔄 Iniciando atualização de performance dos advogados...\n")
    
    # Verificar argumentos
    dry_run = "--dry-run" in sys.argv or "--preview" in sys.argv
    confirm = "--confirm" in sys.argv
    
    if not dry_run and not confirm:
        print("❌ Para executar as alterações, use --confirm")
        print("   Para prévia, use --dry-run ou --preview")
        return
    
    # Atualizar métricas
    update_lawyer_metrics(dry_run=dry_run)
    
    if not dry_run:
        print(f"\n✅ Atualização concluída com sucesso!")
        print("   - Campo 'provisão vs pagamento' baseado na performance das áreas com variação individual")
        print("   - Campos 'carteira', 'remuneração' e 'capital de giro' com valores realistas")

if __name__ == "__main__":
    main()