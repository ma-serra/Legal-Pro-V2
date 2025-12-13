#!/usr/bin/env python3
"""
Script para popular dados dos advogados com métricas realistas
"""

import os
import sys
import random
from datetime import datetime, timedelta
import re

# Adicionar o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import ProcessoJuridico, Situacao, User
from sqlalchemy import text

def extract_lawyers_from_file(file_path):
    """Extrai todos os nomes dos advogados do arquivo"""
    lawyers = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Encontrar todos os nomes que começam com "Dr" ou "Dra"
        pattern = r'^(Dr(?:a)?\.?\s*[^\\n]+)$'
        matches = re.findall(pattern, content, re.MULTILINE)
        
        for match in matches:
            # Limpar o nome
            name = match.strip()
            if name and len(name) > 3:  # Evitar matches muito curtos
                lawyers.append(name)
                
        # Remover duplicatas mantendo ordem
        seen = set()
        unique_lawyers = []
        for lawyer in lawyers:
            if lawyer not in seen:
                seen.add(lawyer)
                unique_lawyers.append(lawyer)
                
        return unique_lawyers
        
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return []

def generate_realistic_financial_data():
    """Gera dados financeiros realistas para um advogado"""
    
    # Valores base realistas
    base_carteira = random.choice([
        random.uniform(50000, 200000),    # Advogados juniores
        random.uniform(200000, 500000),   # Advogados plenos
        random.uniform(500000, 1500000),  # Advogados seniores
        random.uniform(1500000, 5000000)  # Sócios/Partners
    ])
    
    total_casos = random.randint(1, 15)
    
    # Honorários baseados na carteira (15-35% da carteira)
    honorarios_rate = random.uniform(0.15, 0.35)
    honorarios_faturados = base_carteira * honorarios_rate
    
    # Custos operacionais (3-8% da carteira)
    custos_rate = random.uniform(0.03, 0.08)
    custos_operacionais = base_carteira * custos_rate
    
    # Margem líquida
    margem_liquida = honorarios_faturados - custos_operacionais
    
    # Eficiência (60-95%)
    eficiencia = random.uniform(60.0, 95.0)
    
    # Taxa de sucesso (70-95%)
    taxa_sucesso = random.uniform(70.0, 95.0)
    
    # Produtividade financeira (margem / carteira * 100)
    produtividade_financeira = (margem_liquida / base_carteira * 100) if base_carteira > 0 else 0
    
    # ROI Individual (10-40%)
    roi_individual = random.uniform(10.0, 40.0)
    
    # Casos por milhão
    casos_por_milhao = (total_casos / (base_carteira / 1000000)) if base_carteira > 0 else 0
    
    # Capital de giro (10-20% da carteira)
    capital_giro = base_carteira * random.uniform(0.10, 0.20)
    
    # Provisão vs Pagamento (80-98% de conversão)
    conversao_pagamento = random.uniform(80.0, 98.0)
    
    return {
        'total_casos': total_casos,
        'eficiencia': round(eficiencia, 1),
        'carteira_total': round(base_carteira, 2),
        'remuneracao': round(honorarios_faturados, 2),
        'produtividade_financeira': round(produtividade_financeira, 1),
        'margem_media': round((margem_liquida / honorarios_faturados * 100) if honorarios_faturados > 0 else 0, 1),
        'produtividade_tecnica': round(random.uniform(75.0, 95.0), 1),
        'roi_individual': round(roi_individual, 1),
        'casos_por_milhao': round(casos_por_milhao, 1),
        'eficiencia_geral': round(eficiencia, 1),
        'capital_giro_necessario': round(capital_giro, 2),
        'conversao_pagamento': round(conversao_pagamento, 1),
        'honorarios_faturados': round(honorarios_faturados, 2),
        'custos_operacionais': round(custos_operacionais, 2),
        'margem_liquida': round(margem_liquida, 2),
        'taxa_sucesso': round(taxa_sucesso, 1)
    }

def generate_legal_area():
    """Gera uma área jurídica aleatória"""
    areas = [
        'Direito Civil', 'Direito Penal', 'Direito Trabalhista', 
        'Direito Tributário', 'Direito Empresarial', 'Direito do Consumidor',
        'Direito Bancário', 'Direito Imobiliário', 'Direito Previdenciário',
        'Direito Digital', 'Direito Ambiental', 'Direito Securitário',
        'Direito Agrário', 'Negociação e Conflitos'
    ]
    return random.choice(areas)

def generate_realistic_process_data(lawyer_name, financial_data):
    """Gera dados realistas para processos de um advogado"""
    processes = []
    num_processes = financial_data['total_casos']
    
    # Distribuir valor da carteira entre os processos
    remaining_value = financial_data['carteira_total']
    
    for i in range(num_processes):
        if i == num_processes - 1:
            # Último processo recebe valor restante
            valor_causa = remaining_value
        else:
            # Distribuir de forma desigual (alguns processos grandes, outros pequenos)
            if random.random() < 0.3:  # 30% chance de processo grande
                valor_causa = remaining_value * random.uniform(0.4, 0.7)
            else:
                valor_causa = remaining_value * random.uniform(0.05, 0.25)
            
            remaining_value -= valor_causa
            remaining_value = max(0, remaining_value)
        
        # Dados do processo
        area_juridica = generate_legal_area()
        
        # Status baseado na taxa de sucesso
        sucesso = random.random() < (financial_data['taxa_sucesso'] / 100)
        if sucesso:
            status = random.choice(['FINALIZADO COM PAGAMENTO', 'FINALIZADO POR ACORDO'])
        else:
            status = random.choice(['FINALIZADO IMPROCEDENTE', 'EM ANDAMENTO'])
        
        # Risco baseado no valor
        if valor_causa > 500000:
            risco = 'ALTO'
        elif valor_causa > 100000:
            risco = 'MÉDIO'
        else:
            risco = 'BAIXO'
        
        # Estado aleatório
        estados = ['SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'DF', 'BA', 'GO', 'ES']
        estado = random.choice(estados)
        
        # Datas
        data_inicio = datetime.now() - timedelta(days=random.randint(30, 365))
        
        process_data = {
            'numero_processo': f"{random.randint(1000000, 9999999)}-{random.randint(10, 99)}.{random.randint(2020, 2025)}.{random.randint(1, 9)}.{random.randint(10, 99)}.{random.randint(1000, 9999)}",
            'advogado_do_caso': lawyer_name,
            'cliente': f"Cliente {i+1} de {lawyer_name.split()[-1]}",
            'area_juridica': area_juridica,
            'valor_da_causa': round(valor_causa, 2),
            'status': status,
            'risco': risco,
            'estado': estado,
            'data_distribuicao': data_inicio.date(),
            'data_entrada': data_inicio.date(),
            'situacao_id': 1,  # Ativo
            'polo': f'Foro de {estado}',
            'pagamento': round(valor_causa * random.uniform(0.7, 0.9), 2) if 'PAGAMENTO' in status else None,
            'acordo': round(valor_causa * random.uniform(0.6, 0.8), 2) if 'ACORDO' in status else None,
            'provisao': round(valor_causa * 0.2, 2)  # 20% de provisão
        }
        
        processes.append(process_data)
    
    return processes

def create_lawyer_performance_record(lawyer_name, financial_data):
    """Cria registro de performance para o advogado"""
    return {
        'advogado_do_caso': lawyer_name,
        'processos_quantidade': financial_data['total_casos'],
        'total_casos': financial_data['total_casos'],
        'valor_total_carteira': financial_data['carteira_total'],
        'honorarios_faturados': financial_data['honorarios_faturados'],
        'custos_operacionais': financial_data['custos_operacionais'],
        'margem_liquida': financial_data['margem_liquida'],
        'ticket_medio': financial_data['carteira_total'] / financial_data['total_casos'] if financial_data['total_casos'] > 0 else 0,
        'processos_ganhos': int(financial_data['total_casos'] * financial_data['taxa_sucesso'] / 100),
        'processos_perdidos': financial_data['total_casos'] - int(financial_data['total_casos'] * financial_data['taxa_sucesso'] / 100),
        'taxa_sucesso': financial_data['taxa_sucesso'],
        'tempo_medio_conclusao': random.randint(90, 180),
        'eficiencia': financial_data['eficiencia'],
        'produtividade_financeira': financial_data['produtividade_financeira'],
        'roi_individual': financial_data['roi_individual'],
        'casos_por_milhao': financial_data['casos_por_milhao'],
        'capital_giro_necessario': financial_data['capital_giro_necessario'],
        'conversao_pagamento': financial_data['conversao_pagamento'],
        'has_data': True
    }

def populate_lawyers_data():
    """Função principal para popular dados dos advogados"""
    
    print("🚀 Iniciando população de dados dos advogados...")
    
    # Caminho do arquivo
    file_path = "attached_assets/Pasted-Dr-a-Fernando-Aparecida-Total-de-Casos-1-Efici-ncia-0-0-Carteira-Total-R-0-Remune-1758303938097_1758303938098.txt"
    
    # Extrair advogados do arquivo
    print("📄 Extraindo nomes dos advogados do arquivo...")
    lawyers = extract_lawyers_from_file(file_path)
    
    if not lawyers:
        print("❌ Nenhum advogado encontrado no arquivo!")
        return
    
    print(f"✅ Encontrados {len(lawyers)} advogados únicos")
    
    with app.app_context():
        try:
            # Verificar se tabela de situações existe
            existing_situacoes = db.session.query(Situacao).count()
            if existing_situacoes == 0:
                print("📝 Criando situações padrão...")
                situacao_ativa = Situacao(id=1, nome="Ativo", descricao="Processo ativo")
                situacao_encerrada = Situacao(id=2, nome="Encerrado", descricao="Processo encerrado")
                db.session.add(situacao_ativa)
                db.session.add(situacao_encerrada)
                db.session.commit()
            
            total_processes_created = 0
            
            for i, lawyer in enumerate(lawyers, 1):
                print(f"👨‍💼 Processando advogado {i}/{len(lawyers)}: {lawyer}")
                
                # Verificar se já existe
                existing = ProcessoJuridico.query.filter_by(advogado_do_caso=lawyer).first()
                if existing:
                    print(f"   ⚠️  Advogado já existe no banco. Pulando...")
                    continue
                
                # Gerar dados financeiros realistas
                financial_data = generate_realistic_financial_data()
                
                # Gerar processos para o advogado
                processes = generate_realistic_process_data(lawyer, financial_data)
                
                # Inserir processos no banco
                for process_data in processes:
                    processo = ProcessoJuridico(**process_data)
                    db.session.add(processo)
                    total_processes_created += 1
                
                print(f"   ✅ Criados {len(processes)} processos (Carteira: R$ {financial_data['carteira_total']:,.2f})")
                
                # Commit a cada 10 advogados para evitar transações muito grandes
                if i % 10 == 0:
                    db.session.commit()
                    print(f"💾 Salvos {i} advogados no banco...")
            
            # Commit final
            db.session.commit()
            
            print(f"\n🎉 População completa!")
            print(f"👨‍💼 Total de advogados processados: {len(lawyers)}")
            print(f"📋 Total de processos criados: {total_processes_created}")
            print(f"💰 Sistema de métricas financeiras ativado!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro durante população: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    populate_lawyers_data()