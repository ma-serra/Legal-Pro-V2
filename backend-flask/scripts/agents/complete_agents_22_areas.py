#!/usr/bin/env python3
"""
Script para completar 15 agentes em cada uma das 22 áreas existentes
"""

import os
import sys
import json
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Modelos de especialistas por categoria
ESPECIALISTAS_MODELOS = [
    "Analista Jurídico",
    "Consultor Especializado", 
    "Revisor de Conformidade",
    "Especialista em Regulamentação",
    "Analista de Riscos",
    "Consultor em Compliance",
    "Especialista em Procedimentos",
    "Analista de Contratos",
    "Consultor em Jurisprudência",
    "Especialista em Pareceres",
    "Analista de Legislação",
    "Consultor Estratégico",
    "Especialista em Advocacy",
    "Analista de Precedentes",
    "Consultor em Negociação"
]

def get_capacidades_por_area(area_nome):
    """Gera capacidades específicas para cada área jurídica"""
    
    capacidades_por_area = {
        'Direito Bancário': [
            "Análise de contratos bancários", "Avaliação de riscos financeiros", 
            "Consultoria em regulamentação bancária", "Análise de operações de crédito",
            "Elaboração de pareceres sobre produtos financeiros"
        ],
        'Direito Securitário': [
            "Análise de apólices de seguro", "Avaliação de sinistros", 
            "Consultoria em resseguros", "Análise de contratos de seguro",
            "Elaboração de regulamentos securitários"
        ],
        'Direito Trabalhista': [
            "Análise de contratos de trabalho", "Avaliação de rescisões", 
            "Consultoria em acordos coletivos", "Análise de folha de pagamento",
            "Elaboração de defesas trabalhistas"
        ],
        'Direito Previdenciário': [
            "Análise de benefícios previdenciários", "Avaliação de perícias médicas", 
            "Consultoria em aposentadorias", "Análise de contribuições previdenciárias",
            "Elaboração de recursos previdenciários"
        ],
        'Direito Tributário': [
            "Análise fiscal e tributária", "Avaliação de planejamento tributário", 
            "Consultoria em contencioso fiscal", "Análise de obrigações acessórias",
            "Elaboração de defesas fiscais"
        ],
        'Direito Imobiliário': [
            "Análise de contratos imobiliários", "Avaliação de incorporações", 
            "Consultoria em locações", "Análise de direito registral",
            "Elaboração de escrituras e registros"
        ],
        'Direito Digital': [
            "Análise de contratos digitais", "Avaliação de LGPD", 
            "Consultoria em propriedade intelectual", "Análise de e-commerce",
            "Elaboração de políticas de privacidade"
        ],
        'Direito Empresarial': [
            "Análise de contratos societários", "Avaliação de fusões e aquisições", 
            "Consultoria em governança corporativa", "Análise de due diligence",
            "Elaboração de estatutos sociais"
        ],
        'Análise de Riscos Jurídicos': [
            "Identificação de riscos jurídicos", "Avaliação de compliance", 
            "Consultoria em gestão de riscos", "Análise de exposições legais",
            "Elaboração de matriz de riscos"
        ],
        'Direito Penal': [
            "Análise de crimes econômicos", "Avaliação de compliance criminal", 
            "Consultoria em defesa corporativa", "Análise de lavagem de dinheiro",
            "Elaboração de defesas penais"
        ],
        'Direito Ambiental': [
            "Análise de licenciamento ambiental", "Avaliação de impactos ambientais", 
            "Consultoria em sustentabilidade", "Análise de responsabilidade ambiental",
            "Elaboração de estudos ambientais"
        ],
        'Direito do Consumidor': [
            "Análise de relações de consumo", "Avaliação de práticas comerciais", 
            "Consultoria em defesa do consumidor", "Análise de produtos e serviços",
            "Elaboração de políticas de atendimento"
        ],
        'Direito Civil': [
            "Análise de contratos civis", "Avaliação de responsabilidade civil", 
            "Consultoria em direito de família", "Análise de direitos de personalidade",
            "Elaboração de inventários"
        ],
        'Direito Administrativo': [
            "Análise de atos administrativos", "Avaliação de licitações", 
            "Consultoria em contratos públicos", "Análise de processo administrativo",
            "Elaboração de recursos administrativos"
        ],
        'Direito Constitucional': [
            "Análise de constitucionalidade", "Avaliação de direitos fundamentais", 
            "Consultoria em controle de constitucionalidade", "Análise de organização do Estado",
            "Elaboração de ações constitucionais"
        ],
        'Direito Processual Civil': [
            "Análise de procedimentos judiciais", "Avaliação de recursos", 
            "Consultoria em execução judicial", "Análise de provas processuais",
            "Elaboração de estratégias processuais"
        ],
        'Direito Internacional': [
            "Análise de tratados internacionais", "Avaliação de arbitragem internacional", 
            "Consultoria em comércio exterior", "Análise de jurisdição internacional",
            "Elaboração de contratos internacionais"
        ],
        'Direito da Saúde': [
            "Análise de regulamentação sanitária", "Avaliação de responsabilidade médica", 
            "Consultoria em bioética", "Análise de planos de saúde",
            "Elaboração de protocolos médicos"
        ],
        'Direito da Tecnologia': [
            "Análise de propriedade intelectual", "Avaliação de contratos de software", 
            "Consultoria em inovação tecnológica", "Análise de patentes e marcas",
            "Elaboração de políticas de PI"
        ],
        'Direito Eleitoral': [
            "Análise de legislação eleitoral", "Avaliação de campanhas políticas", 
            "Consultoria em prestação de contas", "Análise de propaganda eleitoral",
            "Elaboração de recursos eleitorais"
        ],
        'Direito Agrário': [
            "Análise de reforma agrária", "Avaliação de questões fundiárias", 
            "Consultoria em desenvolvimento rural", "Análise de contratos rurais",
            "Elaboração de políticas agrárias"
        ],
        'Direito Militar': [
            "Análise de direito castrense", "Avaliação de disciplina militar", 
            "Consultoria em justiça militar", "Análise de regulamentos militares",
            "Elaboração de defesas militares"
        ]
    }
    
    # Capacidades genéricas como fallback
    capacidades_genericas = [
        "Análise de documentos jurídicos", "Avaliação de riscos legais", 
        "Consultoria especializada", "Elaboração de pareceres técnicos",
        "Revisão de conformidade regulatória"
    ]
    
    return capacidades_por_area.get(area_nome, capacidades_genericas)

def complete_agents_22_areas():
    """Completa 15 agentes para cada uma das 22 áreas"""
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        return False
    
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Buscar todas as categorias
        result = session.execute(text("""
            SELECT id, nome FROM categoria_juridica ORDER BY id
        """))
        todas_categorias = result.fetchall()
        print(f"📊 Total de categorias: {len(todas_categorias)}")
        
        # Completar especialistas para todas as categorias
        print(f"\n👥 Completando para 15 especialistas por categoria...")
        
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
                    nome_especialista = f"{especialista_base} - {categoria_nome}"
                    
                    # Capacidades específicas para este especialista
                    capacidades_esp = capacidades_area[i % len(capacidades_area)]
                    outras_capacidades = [cap for cap in capacidades_area if cap != capacidades_esp][:4]
                    capacidades_final = [capacidades_esp] + outras_capacidades
                    
                    descricao = f"Especialista em {categoria_nome} com foco em {capacidades_esp.lower()}"
                    
                    # Criar o agente
                    session.execute(text("""
                        INSERT INTO agente_juridico (
                            nome, classe, descricao, categoria_id, nivel, 
                            ativo, data_criacao, data_atualizacao, capacidades,
                            modelo_ai, temperatura, max_tokens, icone, cor_destaque
                        ) VALUES (
                            :nome, :classe, :descricao, :categoria_id, 'Especialista',
                            true, :now, :now, :capacidades,
                            'gpt-4o', 0.7, 4000, 'fas fa-user-tie', '#3498db'
                        )
                    """), {
                        'nome': nome_especialista,
                        'classe': especialista_base,
                        'descricao': descricao,
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
        print(f"\n📈 Sistema completo!")
        print(f"✅ {total_criados} novos especialistas criados")
        print(f"✅ {len(todas_categorias)} áreas jurídicas ativas")
        print(f"\n📊 Distribuição final:")
        
        total_especialistas = 0
        for categoria, count in distribuicao_final:
            print(f"   {categoria}: {count} especialistas")
            total_especialistas += count
        
        print(f"\n🎯 Total: {total_especialistas} especialistas em {len(todas_categorias)} áreas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    print("🚀 Completando sistema com 15 especialistas por área...")
    success = complete_agents_22_areas()
    
    if success:
        print("✅ Sistema completo!")
    else:
        print("❌ Falha na conclusão")
        sys.exit(1)