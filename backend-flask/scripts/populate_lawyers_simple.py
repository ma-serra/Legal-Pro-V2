#!/usr/bin/env python3
"""
Script simplificado para popular dados dos advogados
"""

import os
import sys
import random
import re
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor

def extract_lawyers_from_file(file_path):
    """Extrai todos os nomes dos advogados do arquivo"""
    lawyers = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Encontrar todos os nomes que começam com "Dr" ou "Dra"
        pattern = r'^(Dr(?:a)?\.?\s*[^\n]+)$'
        matches = re.findall(pattern, content, re.MULTILINE)
        
        for match in matches:
            # Limpar o nome
            name = match.strip()
            if name and len(name) > 3 and 'Total de Casos' not in name and 'Eficiência' not in name:
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

def connect_to_database():
    """Conecta ao banco PostgreSQL"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL não encontrada!")
            return None
            
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None

def create_tables_if_not_exist(cursor):
    """Cria tabelas necessárias se não existirem"""
    
    # Tabela de situações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS situacao (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            descricao TEXT
        )
    """)
    
    # Inserir situações padrão se não existirem
    cursor.execute("SELECT COUNT(*) FROM situacao")
    result = cursor.fetchone()
    if result['count'] == 0:
        cursor.execute("""
            INSERT INTO situacao (id, nome, descricao) VALUES 
            (1, 'Ativo', 'Processo ativo'),
            (2, 'Encerrado', 'Processo encerrado')
        """)
    
    # Tabela de processos jurídicos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processo_juridico (
            id SERIAL PRIMARY KEY,
            numero_processo VARCHAR(50) UNIQUE NOT NULL,
            advogado_do_caso VARCHAR(200),
            cliente VARCHAR(200),
            area_juridica VARCHAR(100),
            valor_da_causa DECIMAL(15,2),
            status VARCHAR(100),
            risco VARCHAR(20),
            estado VARCHAR(2),
            polo VARCHAR(200),
            data_distribuicao DATE,
            data_entrada DATE,
            situacao_id INTEGER REFERENCES situacao(id),
            pagamento DECIMAL(15,2),
            acordo DECIMAL(15,2),
            provisao DECIMAL(15,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

def populate_lawyers_data():
    """Função principal para popular dados dos advogados"""
    
    print("🚀 Iniciando população de dados dos advogados...")
    
    # Caminho do arquivo
    file_path = "../attached_assets/Pasted-Dr-a-Fernando-Aparecida-Total-de-Casos-1-Efici-ncia-0-0-Carteira-Total-R-0-Remune-1758303938097_1758303938098.txt"
    
    # Extrair advogados do arquivo
    print("📄 Extraindo nomes dos advogados do arquivo...")
    lawyers = extract_lawyers_from_file(file_path)
    
    if not lawyers:
        print("❌ Nenhum advogado encontrado no arquivo!")
        return
    
    print(f"✅ Encontrados {len(lawyers)} advogados únicos")
    
    # Conectar ao banco
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Criar tabelas se necessário
        create_tables_if_not_exist(cursor)
        conn.commit()
        
        total_processes_created = 0
        
        for i, lawyer in enumerate(lawyers, 1):
            print(f"👨‍💼 Processando advogado {i}/{len(lawyers)}: {lawyer}")
            
            # Verificar se já existe
            cursor.execute("SELECT COUNT(*) FROM processo_juridico WHERE advogado_do_caso = %s", (lawyer,))
            result = cursor.fetchone()
            existing_count = result['count']
            
            if existing_count > 0:
                print(f"   ⚠️  Advogado já tem {existing_count} processos. Pulando...")
                continue
            
            # Gerar dados financeiros realistas
            financial_data = generate_realistic_financial_data()
            
            # Criar processos para o advogado
            num_processes = financial_data['total_casos']
            remaining_value = financial_data['carteira_total']
            
            for j in range(num_processes):
                # Distribuir valor da carteira
                if j == num_processes - 1:
                    valor_causa = remaining_value
                else:
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
                
                # Gerar número de processo único
                numero_processo = f"{random.randint(1000000, 9999999)}-{random.randint(10, 99)}.{random.randint(2020, 2025)}.{random.randint(1, 9)}.{random.randint(10, 99)}.{random.randint(1000, 9999)}"
                
                # Inserir processo
                cursor.execute("""
                    INSERT INTO processo_juridico (
                        numero_processo, advogado_do_caso, cliente, area_juridica,
                        valor_da_causa, status, risco, estado, polo,
                        data_distribuicao, data_entrada, situacao_id,
                        pagamento, acordo, provisao
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    numero_processo,
                    lawyer,
                    f"Cliente {j+1} de {lawyer.split()[-1]}",
                    area_juridica,
                    round(valor_causa, 2),
                    status,
                    risco,
                    estado,
                    f'Foro de {estado}',
                    data_inicio.date(),
                    data_inicio.date(),
                    1,  # situacao_id: Ativo
                    round(valor_causa * random.uniform(0.7, 0.9), 2) if 'PAGAMENTO' in status else None,
                    round(valor_causa * random.uniform(0.6, 0.8), 2) if 'ACORDO' in status else None,
                    round(valor_causa * 0.2, 2)  # 20% de provisão
                ))
                
                total_processes_created += 1
            
            print(f"   ✅ Criados {num_processes} processos (Carteira: R$ {financial_data['carteira_total']:,.2f})")
            
            # Commit a cada 10 advogados
            if i % 10 == 0:
                conn.commit()
                print(f"💾 Salvos {i} advogados no banco...")
        
        # Commit final
        conn.commit()
        
        print(f"\n🎉 População completa!")
        print(f"👨‍💼 Total de advogados processados: {len(lawyers)}")
        print(f"📋 Total de processos criados: {total_processes_created}")
        print(f"💰 Sistema de métricas financeiras ativado!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro durante população: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    populate_lawyers_data()