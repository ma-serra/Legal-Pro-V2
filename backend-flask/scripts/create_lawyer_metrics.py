#!/usr/bin/env python3
"""
Script para criar e popular métricas avançadas dos advogados
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

def generate_realistic_metrics(base_processes=1):
    """Gera métricas realistas baseadas no número de processos"""
    
    # Adicionar maior aleatoriedade no número de casos
    # Gerar distribuição mais diversificada independente do número atual de processos
    distribution_type = random.choice(['low', 'medium', 'high', 'very_high'])
    
    if distribution_type == 'low':
        # Advogados com poucos casos (1-5)
        total_casos_aleatorio = random.randint(1, 5)
    elif distribution_type == 'medium':
        # Advogados com casos médios (6-15)
        total_casos_aleatorio = random.randint(6, 15)
    elif distribution_type == 'high':
        # Advogados com muitos casos (16-30)
        total_casos_aleatorio = random.randint(16, 30)
    else:  # very_high
        # Advogados com casos muito altos (31-50)
        total_casos_aleatorio = random.randint(31, 50)
    
    # Ainda aplicar alguma influência do número original (mas menor)
    if base_processes > 1:
        # Para advogados que já têm processos, dar um pequeno boost
        total_casos_aleatorio += random.randint(0, min(base_processes, 10))
    
    # Usar o número aleatorio como scale_factor
    scale_factor = total_casos_aleatorio
    
    # Valores base realistas 
    carteira_total = random.uniform(50000, 2000000) * scale_factor
    
    # Eficiência baseada na experiência (60-95%)
    eficiencia = random.uniform(60.0, 95.0)
    
    # Remuneração (15-35% da carteira)
    remuneracao = carteira_total * random.uniform(0.15, 0.35)
    
    # Produtividade financeira (10-30%)
    produtividade_financeira = random.uniform(10.0, 30.0)
    
    # Margem média (50-80%)
    margem_media = random.uniform(50.0, 80.0)
    
    # Produtividade técnica (70-95%)
    produtividade_tecnica = random.uniform(70.0, 95.0)
    
    # ROI individual (15-45%)
    roi_individual = random.uniform(15.0, 45.0)
    
    # Casos por milhão
    casos_por_milhao = (scale_factor / (carteira_total / 1000000)) if carteira_total > 0 else 0
    
    # Eficiência geral (similar à eficiência)
    eficiencia_geral = eficiencia + random.uniform(-5, 5)
    eficiencia_geral = max(60.0, min(95.0, eficiencia_geral))  # Clamping
    
    # Capital de giro necessário (10-25% da carteira)
    capital_giro_necessario = carteira_total * random.uniform(0.10, 0.25)
    
    # Provisão vs pagamento (75-98% de conversão)
    provisao_vs_pagamento = random.uniform(75.0, 98.0)
    
    # Métricas adicionais para dashboard
    taxa_sucesso = random.uniform(70.0, 95.0)
    tempo_medio_conclusao = random.randint(90, 180)
    honorarios_faturados = remuneracao
    custos_operacionais = carteira_total * random.uniform(0.03, 0.08)
    margem_liquida = honorarios_faturados - custos_operacionais
    ticket_medio = carteira_total / scale_factor if scale_factor > 0 else 0
    
    return {
        'total_casos': total_casos_aleatorio,
        'eficiencia': round(eficiencia, 1),
        'carteira_total': round(carteira_total, 2),
        'remuneracao': round(remuneracao, 2),
        'produtividade_financeira': round(produtividade_financeira, 1),
        'margem_media': round(margem_media, 1),
        'produtividade_tecnica': round(produtividade_tecnica, 1),
        'roi_individual': round(roi_individual, 1),
        'casos_por_milhao': round(casos_por_milhao, 1),
        'eficiencia_geral': round(eficiencia_geral, 1),
        'capital_giro_necessario': round(capital_giro_necessario, 2),
        'provisao_vs_pagamento': round(provisao_vs_pagamento, 1),
        'taxa_sucesso': round(taxa_sucesso, 1),
        'tempo_medio_conclusao': tempo_medio_conclusao,
        'honorarios_faturados': round(honorarios_faturados, 2),
        'custos_operacionais': round(custos_operacionais, 2),
        'margem_liquida': round(margem_liquida, 2),
        'ticket_medio': round(ticket_medio, 2)
    }

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

def create_lawyer_metrics_table(cursor):
    """Cria tabela de métricas dos advogados"""
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lawyer_metrics (
            id SERIAL PRIMARY KEY,
            advogado_nome VARCHAR(200) UNIQUE NOT NULL,
            total_casos INTEGER DEFAULT 0,
            eficiencia DECIMAL(5,2) DEFAULT 0.0,
            carteira_total DECIMAL(15,2) DEFAULT 0.0,
            remuneracao DECIMAL(15,2) DEFAULT 0.0,
            produtividade_financeira DECIMAL(5,2) DEFAULT 0.0,
            margem_media DECIMAL(5,2) DEFAULT 0.0,
            produtividade_tecnica DECIMAL(5,2) DEFAULT 0.0,
            roi_individual DECIMAL(5,2) DEFAULT 0.0,
            casos_por_milhao DECIMAL(10,2) DEFAULT 0.0,
            eficiencia_geral DECIMAL(5,2) DEFAULT 0.0,
            capital_giro_necessario DECIMAL(15,2) DEFAULT 0.0,
            provisao_vs_pagamento DECIMAL(5,2) DEFAULT 0.0,
            taxa_sucesso DECIMAL(5,2) DEFAULT 0.0,
            tempo_medio_conclusao INTEGER DEFAULT 0,
            honorarios_faturados DECIMAL(15,2) DEFAULT 0.0,
            custos_operacionais DECIMAL(15,2) DEFAULT 0.0,
            margem_liquida DECIMAL(15,2) DEFAULT 0.0,
            ticket_medio DECIMAL(15,2) DEFAULT 0.0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    print("✅ Tabela lawyer_metrics criada/verificada com sucesso!")

def populate_lawyer_metrics():
    """Função principal para popular métricas dos advogados"""
    
    print("🚀 Iniciando população de métricas dos advogados...")
    
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
        
        # Criar tabela de métricas
        create_lawyer_metrics_table(cursor)
        conn.commit()
        
        # Popular métricas para cada advogado
        updated_count = 0
        created_count = 0
        
        for i, lawyer in enumerate(lawyers, 1):
            print(f"📊 Processando métricas para {i}/{len(lawyers)}: {lawyer}")
            
            # Verificar quantos processos o advogado tem
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM processo_juridico 
                WHERE advogado_do_caso = %s
            """, (lawyer,))
            result = cursor.fetchone()
            total_processos = result['count'] if result else 1
            
            # Verificar se já tem métricas
            cursor.execute("""
                SELECT id FROM lawyer_metrics 
                WHERE advogado_nome = %s
            """, (lawyer,))
            existing = cursor.fetchone()
            
            # Gerar métricas realistas
            metrics = generate_realistic_metrics(total_processos)
            
            if existing:
                # Atualizar métricas existentes
                cursor.execute("""
                    UPDATE lawyer_metrics SET
                        total_casos = %s,
                        eficiencia = %s,
                        carteira_total = %s,
                        remuneracao = %s,
                        produtividade_financeira = %s,
                        margem_media = %s,
                        produtividade_tecnica = %s,
                        roi_individual = %s,
                        casos_por_milhao = %s,
                        eficiencia_geral = %s,
                        capital_giro_necessario = %s,
                        provisao_vs_pagamento = %s,
                        taxa_sucesso = %s,
                        tempo_medio_conclusao = %s,
                        honorarios_faturados = %s,
                        custos_operacionais = %s,
                        margem_liquida = %s,
                        ticket_medio = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE advogado_nome = %s
                """, (
                    metrics['total_casos'],
                    metrics['eficiencia'],
                    metrics['carteira_total'],
                    metrics['remuneracao'],
                    metrics['produtividade_financeira'],
                    metrics['margem_media'],
                    metrics['produtividade_tecnica'],
                    metrics['roi_individual'],
                    metrics['casos_por_milhao'],
                    metrics['eficiencia_geral'],
                    metrics['capital_giro_necessario'],
                    metrics['provisao_vs_pagamento'],
                    metrics['taxa_sucesso'],
                    metrics['tempo_medio_conclusao'],
                    metrics['honorarios_faturados'],
                    metrics['custos_operacionais'],
                    metrics['margem_liquida'],
                    metrics['ticket_medio'],
                    lawyer
                ))
                updated_count += 1
                print(f"   ✅ Métricas atualizadas (Carteira: R$ {metrics['carteira_total']:,.2f})")
            else:
                # Criar novas métricas
                cursor.execute("""
                    INSERT INTO lawyer_metrics (
                        advogado_nome, total_casos, eficiencia, carteira_total,
                        remuneracao, produtividade_financeira, margem_media,
                        produtividade_tecnica, roi_individual, casos_por_milhao,
                        eficiencia_geral, capital_giro_necessario, provisao_vs_pagamento,
                        taxa_sucesso, tempo_medio_conclusao, honorarios_faturados,
                        custos_operacionais, margem_liquida, ticket_medio
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    lawyer,
                    metrics['total_casos'],
                    metrics['eficiencia'],
                    metrics['carteira_total'],
                    metrics['remuneracao'],
                    metrics['produtividade_financeira'],
                    metrics['margem_media'],
                    metrics['produtividade_tecnica'],
                    metrics['roi_individual'],
                    metrics['casos_por_milhao'],
                    metrics['eficiencia_geral'],
                    metrics['capital_giro_necessario'],
                    metrics['provisao_vs_pagamento'],
                    metrics['taxa_sucesso'],
                    metrics['tempo_medio_conclusao'],
                    metrics['honorarios_faturados'],
                    metrics['custos_operacionais'],
                    metrics['margem_liquida'],
                    metrics['ticket_medio']
                ))
                created_count += 1
                print(f"   ✅ Métricas criadas (Carteira: R$ {metrics['carteira_total']:,.2f})")
            
            # Commit a cada 20 advogados
            if i % 20 == 0:
                conn.commit()
                print(f"💾 Salvas métricas de {i} advogados...")
        
        # Commit final
        conn.commit()
        
        print(f"\n🎉 População de métricas completa!")
        print(f"👨‍💼 Total de advogados processados: {len(lawyers)}")
        print(f"📊 Métricas criadas: {created_count}")
        print(f"🔄 Métricas atualizadas: {updated_count}")
        print(f"💰 Sistema de métricas avançadas ativado!")
        
        # Mostrar estatísticas
        cursor.execute("SELECT COUNT(*) as count FROM lawyer_metrics")
        total_metrics = cursor.fetchone()['count']
        print(f"📈 Total de registros de métricas no banco: {total_metrics}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro durante população: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    populate_lawyer_metrics()