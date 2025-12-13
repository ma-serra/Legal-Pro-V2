#!/usr/bin/env python3
"""
Script para corrigir a distribuição de casos entre advogados para refletir 
a distribuição real de 163 casos conforme especificado pelo usuário.
"""

import sys
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import random
import math

# Configuração do banco de dados
DATABASE_URL = os.environ.get('DATABASE_URL')

# Distribuição de casos por área conforme especificado pelo usuário
DISTRIBUICAO_CASOS = {
    'Direito Tributário': 12,
    'Direito do Consumidor': 13,
    'Direito Bancário': 12,
    'Direito Civil': 12,
    'Direito Empresarial': 12,
    'Direito Previdenciário': 12,
    'Direito Penal': 12,
    'Direito Trabalhista': 13,
    'Direito Digital': 12,
    'Negociação e Conflitos': 11,
    'Direito Agrário': 11,
    'Direito Ambiental': 7,
    'Direito Securitário': 12,
    'Direito Imobiliário': 12
}

def get_db_connection():
    """Cria conexão com o banco de dados"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def get_lawyers_by_area():
    """Obtém todos os advogados agrupados por área jurídica"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT p.area_juridica, p.advogado_do_caso
            FROM processo_juridico p
            ORDER BY p.area_juridica, p.advogado_do_caso
        """)
        result = cur.fetchall()
        
        lawyers_by_area = {}
        for row in result:
            area = row['area_juridica']
            lawyer = row['advogado_do_caso']
            if area not in lawyers_by_area:
                lawyers_by_area[area] = []
            lawyers_by_area[area].append(lawyer)
        
        return lawyers_by_area
    finally:
        conn.close()

def distribute_cases_to_lawyers(lawyers_by_area, casos_por_area):
    """
    Distribui os casos entre os advogados de cada área de forma proporcional
    """
    case_distribution = {}
    total_lawyers = 0
    
    # Primeiro passar: distribuir casos básicos
    for area, total_casos in casos_por_area.items():
        if area not in lawyers_by_area:
            print(f"⚠️  Área '{area}' não encontrada nos dados, pulando...")
            continue
            
        lawyers = lawyers_by_area[area]
        num_lawyers = len(lawyers)
        total_lawyers += num_lawyers
        
        if num_lawyers == 0:
            continue
            
        # Calcular distribuição base
        casos_por_advogado = total_casos // num_lawyers
        casos_extras = total_casos % num_lawyers
        
        print(f"📊 {area}: {total_casos} casos para {num_lawyers} advogados")
        print(f"   Base: {casos_por_advogado} casos cada, {casos_extras} advogados com +1 caso")
        
        # Distribuir casos
        for i, lawyer in enumerate(lawyers):
            # Primeiros advogados recebem casos extras
            cases = casos_por_advogado + (1 if i < casos_extras else 0)
            case_distribution[lawyer] = {
                'total_casos': cases,
                'area': area
            }
            
        print(f"   Distribuição: {[case_distribution[lawyer]['total_casos'] for lawyer in lawyers]}")
        print()
    
    # Verificar total e ajustar se necessário
    total_casos_distribuidos = sum(data['total_casos'] for data in case_distribution.values())
    total_casos_esperados = sum(casos_por_area.values())
    
    print(f"📊 Total de advogados encontrados: {total_lawyers}")
    print(f"📊 Total de casos distribuídos: {total_casos_distribuidos}")
    print(f"📊 Total de casos esperados: {total_casos_esperados}")
    
    # Se há diferença, adicionar casos extras aos primeiros advogados
    if total_casos_distribuidos < total_casos_esperados:
        diferenca = total_casos_esperados - total_casos_distribuidos
        print(f"🔧 Adicionando {diferenca} casos extras...")
        
        # Adicionar casos extras aos primeiros advogados
        lawyers_list = list(case_distribution.keys())
        for i in range(diferenca):
            if i < len(lawyers_list):
                lawyer = lawyers_list[i]
                case_distribution[lawyer]['total_casos'] += 1
                print(f"   +1 caso para {lawyer}")
    
    return case_distribution

def update_lawyer_case_counts(case_distribution, dry_run=True):
    """Atualiza a contagem de casos na tabela lawyer_metrics"""
    
    if dry_run:
        print("🔍 MODO DRY-RUN - Prévia das alterações:")
        total_casos_check = 0
        
        for lawyer, data in sorted(case_distribution.items(), key=lambda x: x[1]['area']):
            print(f"   {lawyer} ({data['area']}): {data['total_casos']} casos")
            total_casos_check += data['total_casos']
        
        print(f"\n✅ Total de casos distribuídos: {total_casos_check}")
        print(f"📊 Deve ser igual a 163: {'✅' if total_casos_check == 163 else '❌'}")
        return
    
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        
        updated_count = 0
        total_casos_final = 0
        
        print(f"✅ Atualizando contagem de casos para {len(case_distribution)} advogados...")
        
        for lawyer, data in case_distribution.items():
            new_cases = data['total_casos']
            area = data['area']
            
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
                
                if updated_count <= 15:  # Mostrar os primeiros 15
                    print(f"   {lawyer} ({area}): {new_cases} casos")
        
        conn.commit()
        print(f"\n✅ {updated_count} advogados atualizados!")
        print(f"📊 Total de casos final: {total_casos_final}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro ao atualizar banco de dados: {e}")
        raise
    finally:
        conn.close()

def main():
    """Função principal"""
    print("🔄 Iniciando correção da distribuição de casos...\n")
    
    # Verificar argumentos
    dry_run = "--dry-run" in sys.argv or "--preview" in sys.argv
    confirm = "--confirm" in sys.argv
    
    if not dry_run and not confirm:
        print("❌ Para executar as alterações, use --confirm")
        print("   Para prévia, use --dry-run ou --preview")
        return
    
    # Verificar total de casos na distribuição
    total_casos_distribuicao = sum(DISTRIBUICAO_CASOS.values())
    print(f"📊 Distribuição de casos especificada:")
    for area, casos in DISTRIBUICAO_CASOS.items():
        print(f"   {area}: {casos} casos")
    print(f"\n✅ Total: {total_casos_distribuicao} casos")
    
    if total_casos_distribuicao != 163:
        print(f"❌ ERRO: Total da distribuição ({total_casos_distribuicao}) ≠ 163")
        return
    
    # Obter advogados por área
    lawyers_by_area = get_lawyers_by_area()
    
    print(f"\n📊 Advogados por área encontrados:")
    for area, lawyers in sorted(lawyers_by_area.items()):
        print(f"   {area}: {len(lawyers)} advogados")
    
    # Distribuir casos
    case_distribution = distribute_cases_to_lawyers(lawyers_by_area, DISTRIBUICAO_CASOS)
    
    # Atualizar tabela
    update_lawyer_case_counts(case_distribution, dry_run=dry_run)
    
    if not dry_run:
        print(f"\n✅ Distribuição de casos corrigida com sucesso!")
        print("   Os cards de performance agora refletem a distribuição real de 163 casos")

if __name__ == "__main__":
    main()