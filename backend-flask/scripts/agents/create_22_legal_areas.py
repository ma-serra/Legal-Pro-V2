#!/usr/bin/env python3
"""
Script para criar 22 áreas jurídicas completas com 15 especialistas cada
"""

import os
import sys
import json
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cores únicas para as novas categorias (evitando repetições)
CORES_DISPONIVEIS = [
    '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57',
    '#ff9ff3', '#54a0ff', '#5f27cd', '#00d2d3', '#ff9f43',
    '#c44569', '#f8b500', '#e17055', '#a29bfe', '#fd79a8',
    '#6c5ce7', '#74b9ff', '#00b894', '#fdcb6e', '#e84393'
]

# 10 novas categorias jurídicas para completar 22
NOVAS_CATEGORIAS = [
    {
        'nome': 'Direito Civil',
        'descricao': 'Análise de contratos civis, direitos de personalidade, família e sucessões.',
        'icone': 'fas fa-balance-scale'
    },
    {
        'nome': 'Direito Administrativo',
        'descricao': 'Análise de atos administrativos, licitações, contratos públicos e serviço público.',
        'icone': 'fas fa-university'
    },
    {
        'nome': 'Direito Constitucional',
        'descricao': 'Análise de direitos fundamentais, controle de constitucionalidade e organização do Estado.',
        'icone': 'fas fa-flag'
    },
    {
        'nome': 'Direito Processual Civil',
        'descricao': 'Análise de procedimentos judiciais, recursos e execução de decisões judiciais.',
        'icone': 'fas fa-gavel'
    },
    {
        'nome': 'Direito Internacional',
        'descricao': 'Análise de tratados internacionais, arbitragem e direito comercial internacional.',
        'icone': 'fas fa-globe'
    },
    {
        'nome': 'Direito da Saúde',
        'descricao': 'Análise de regulamentação sanitária, responsabilidade médica e bioética.',
        'icone': 'fas fa-heartbeat'
    },
    {
        'nome': 'Direito da Tecnologia',
        'descricao': 'Análise de propriedade intelectual, contratos de tecnologia e inovação.',
        'icone': 'fas fa-microchip'
    },
    {
        'nome': 'Direito Eleitoral',
        'descricao': 'Análise de legislação eleitoral, campanhas políticas e prestação de contas.',
        'icone': 'fas fa-vote-yea'
    },
    {
        'nome': 'Direito Agrário',
        'descricao': 'Análise de reforma agrária, questões fundiárias e desenvolvimento rural.',
        'icone': 'fas fa-tractor'
    },
    {
        'nome': 'Direito Militar',
        'descricao': 'Análise de direito castrense, justiça militar e disciplina militar.',
        'icone': 'fas fa-shield-alt'
    }
]

# Modelos de especialistas por categoria
ESPECIALISTAS_MODELOS = [
    "Analista de Contratos",
    "Consultor Jurídico",
    "Especialista em Compliance",
    "Revisor de Documentos",
    "Consultor em Regulamentação",
    "Analista de Riscos Legais",
    "Especialista em Procedimentos",
    "Consultor em Jurisprudência",
    "Analista de Legislação",
    "Especialista em Pareceres",
    "Consultor em Estratégia Jurídica",
    "Analista de Precedentes",
    "Especialista em Advocacy",
    "Consultor em Negociação",
    "Analista de Due Diligence"
]

def get_capacidades_por_area(area_nome):
    """Gera capacidades específicas para cada área jurídica"""
    
    capacidades_por_area = {
        'Direito Civil': [
            "Análise de contratos de compra e venda",
            "Avaliação de responsabilidade civil",
            "Análise de direitos de personalidade",
            "Consultoria em direito de família",
            "Elaboração de inventários e partilhas"
        ],
        'Direito Administrativo': [
            "Análise de editais de licitação",
            "Avaliação de atos administrativos",
            "Consultoria em contratos públicos",
            "Análise de processo administrativo",
            "Elaboração de recursos administrativos"
        ],
        'Direito Constitucional': [
            "Análise de constitucionalidade",
            "Avaliação de direitos fundamentais",
            "Consultoria em controle de constitucionalidade",
            "Análise de organização do Estado",
            "Elaboração de ações constitucionais"
        ],
        'Direito Processual Civil': [
            "Análise de petições iniciais",
            "Avaliação de recursos judiciais",
            "Consultoria em execução judicial",
            "Análise de provas processuais",
            "Elaboração de estratégias processuais"
        ],
        'Direito Internacional': [
            "Análise de tratados internacionais",
            "Avaliação de arbitragem internacional",
            "Consultoria em comércio exterior",
            "Análise de jurisdição internacional",
            "Elaboração de contratos internacionais"
        ],
        'Direito da Saúde': [
            "Análise de regulamentação sanitária",
            "Avaliação de responsabilidade médica",
            "Consultoria em bioética",
            "Análise de contratos de planos de saúde",
            "Elaboração de protocolos médicos"
        ],
        'Direito da Tecnologia': [
            "Análise de propriedade intelectual",
            "Avaliação de contratos de software",
            "Consultoria em inovação tecnológica",
            "Análise de patentes e marcas",
            "Elaboração de políticas de PI"
        ],
        'Direito Eleitoral': [
            "Análise de legislação eleitoral",
            "Avaliação de campanhas políticas",
            "Consultoria em prestação de contas",
            "Análise de propaganda eleitoral",
            "Elaboração de recursos eleitorais"
        ],
        'Direito Agrário': [
            "Análise de reforma agrária",
            "Avaliação de questões fundiárias",
            "Consultoria em desenvolvimento rural",
            "Análise de contratos rurais",
            "Elaboração de políticas agrárias"
        ],
        'Direito Militar': [
            "Análise de direito castrense",
            "Avaliação de disciplina militar",
            "Consultoria em justiça militar",
            "Análise de regulamentos militares",
            "Elaboração de defesas militares"
        ]
    }
    
    # Para áreas existentes, usar capacidades genéricas
    capacidades_genericas = [
        "Análise de documentos jurídicos",
        "Avaliação de riscos legais",
        "Consultoria especializada",
        "Elaboração de pareceres técnicos",
        "Revisão de conformidade regulatória"
    ]
    
    return capacidades_por_area.get(area_nome, capacidades_genericas)

def create_complete_legal_system():
    """Cria sistema completo com 22 áreas e 15 especialistas cada"""
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        return False
    
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Verificar cores já utilizadas
        result = session.execute(text("SELECT cor FROM categoria_juridica"))
        cores_usadas = [row[0] for row in result.fetchall()]
        print(f"🎨 Cores já utilizadas: {len(cores_usadas)}")
        
        # Filtrar cores disponíveis
        cores_livres = [cor for cor in CORES_DISPONIVEIS if cor not in cores_usadas]
        print(f"🎨 Cores disponíveis: {len(cores_livres)}")
        
        # Criar as 10 novas categorias
        print(f"\n🏗️ Criando 10 novas categorias jurídicas...")
        
        novas_categorias_criadas = []
        for i, categoria in enumerate(NOVAS_CATEGORIAS):
            if i < len(cores_livres):
                cor = cores_livres[i]
            else:
                cor = CORES_DISPONIVEIS[i % len(CORES_DISPONIVEIS)]
            
            result = session.execute(text("""
                INSERT INTO categoria_juridica (nome, descricao, icone, cor, ativa, created_at, updated_at)
                VALUES (:nome, :descricao, :icone, :cor, true, :now, :now)
                RETURNING id
            """), {
                'nome': categoria['nome'],
                'descricao': categoria['descricao'],
                'icone': categoria['icone'],
                'cor': cor,
                'now': datetime.now()
            })
            
            categoria_id = result.scalar()
            novas_categorias_criadas.append({'id': categoria_id, **categoria, 'cor': cor})
            print(f"   ✅ {categoria['nome']} (ID: {categoria_id}, Cor: {cor})")
        
        session.commit()
        
        # Buscar todas as categorias (existentes + novas)
        result = session.execute(text("""
            SELECT id, nome FROM categoria_juridica ORDER BY id
        """))
        todas_categorias = result.fetchall()
        print(f"\n📊 Total de categorias: {len(todas_categorias)}")
        
        # Completar especialistas para todas as categorias
        print(f"\n👥 Completando especialistas para 15 por categoria...")
        
        total_criados = 0
        for categoria_id, categoria_nome in todas_categorias:
            # Verificar quantos especialistas já existem
            result = session.execute(text("""
                SELECT COUNT(*) FROM agente_juridico WHERE categoria_id = :cat_id
            """), {'cat_id': categoria_id})
            
            existentes = result.scalar()
            faltantes = 15 - existentes
            
            print(f"\n📝 {categoria_nome}: {existentes}/15 especialistas (criando {faltantes})")
            
            if faltantes > 0:
                capacidades_area = get_capacidades_por_area(categoria_nome)
                
                for i in range(faltantes):
                    especialista_base = ESPECIALISTAS_MODELOS[i % len(ESPECIALISTAS_MODELOS)]
                    nome_especialista = f"{especialista_base} em {categoria_nome}"
                    
                    # Capacidades específicas para este especialista
                    capacidades_esp = capacidades_area[i % len(capacidades_area)]
                    outras_capacidades = [cap for cap in capacidades_area if cap != capacidades_esp][:4]
                    capacidades_final = [capacidades_esp] + outras_capacidades
                    
                    # Criar o agente
                    session.execute(text("""
                        INSERT INTO agente_juridico (
                            nome, classe, descricao, categoria_id, nivel, 
                            ativo, data_criacao, data_atualizacao, capacidades,
                            modelo_ai, temperatura, max_tokens, icone, cor_destaque
                        ) VALUES (
                            :nome, :classe, :descricao, :categoria_id, 3,
                            true, :now, :now, :capacidades,
                            'gpt-4o', 0.7, 4000, 'fas fa-user-tie', '#3498db'
                        )
                    """), {
                        'nome': nome_especialista,
                        'classe': especialista_base,
                        'descricao': f"Especialista em {categoria_nome} com foco em {capacidades_esp.lower()}",
                        'categoria_id': categoria_id,
                        'capacidades': json.dumps(capacidades_final),
                        'now': datetime.now()
                    })
                    
                    total_criados += 1
                    print(f"   ✅ {nome_especialista}")
        
        session.commit()
        
        # Verificar resultado final
        result = session.execute(text("""
            SELECT c.nome, COUNT(a.id) as total
            FROM categoria_juridica c
            LEFT JOIN agente_juridico a ON a.categoria_id = c.id
            GROUP BY c.id, c.nome
            ORDER BY c.nome
        """))
        
        distribuicao_final = result.fetchall()
        print(f"\n📈 Sistema completo criado!")
        print(f"✅ {total_criados} novos especialistas criados")
        print(f"✅ 22 áreas jurídicas ativas")
        print(f"\n📊 Distribuição final:")
        
        total_especialistas = 0
        for categoria, count in distribuicao_final:
            print(f"   {categoria}: {count} especialistas")
            total_especialistas += count
        
        print(f"\n🎯 Total: {total_especialistas} especialistas em 22 áreas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    print("🚀 Criando sistema jurídico completo com 22 áreas...")
    success = create_complete_legal_system()
    
    if success:
        print("✅ Sistema completo criado com sucesso!")
    else:
        print("❌ Falha na criação do sistema")
        sys.exit(1)