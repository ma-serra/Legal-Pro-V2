#!/usr/bin/env python3
"""
Script para corrigir nomes duplicados de agentes e garantir capacidades únicas
"""

import os
import sys
import json
import hashlib
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_hierarchical_capabilities():
    """Cria capacidades específicas por hierarquia profissional"""
    return {
        'Sênior': {
            'direito_previdenciario': [
                'Coordenação de estratégias previdenciárias complexas',
                'Supervisão de equipes de benefícios sociais',
                'Gestão de carteiras de clientes de alta complexidade',
                'Auditoria de sistemas previdenciários corporativos',
                'Mentoria em planejamento de aposentadorias especiais'
            ],
            'direito_urbanistico': [
                'Coordenação de projetos urbanos de grande porte',
                'Supervisão de licenciamentos ambientais complexos',
                'Gestão de equipes multidisciplinares urbanas',
                'Auditoria de planos diretores municipais',
                'Mentoria em operações urbanas consorciadas'
            ],
            'credito_juridico': [
                'Coordenação de estruturações financeiras complexas',
                'Supervisão de operações de crédito de alto valor',
                'Gestão de portfólios de garantias diversificadas',
                'Auditoria de políticas de crédito institucionais',
                'Mentoria em recuperação de créditos problemáticos'
            ]
        },
        'Especialista': {
            'direito_previdenciario': [
                'Análise técnica de aposentadorias especiais',
                'Cálculo de benefícios previdenciários complexos',
                'Consultoria em revisões de benefícios INSS',
                'Orientação em contribuições facultativas',
                'Recursos administrativos previdenciários'
            ],
            'direito_urbanistico': [
                'Análise técnica de zoneamento urbano',
                'Consultoria em regularização fundiária',
                'Orientação em parcelamento do solo',
                'Licenciamento de empreendimentos urbanos',
                'Recursos em órgãos ambientais municipais'
            ],
            'credito_juridico': [
                'Análise técnica de capacidade creditícia',
                'Estruturação de garantias reais e pessoais',
                'Consultoria em contratos de financiamento',
                'Orientação em cessão de créditos',
                'Recursos em instituições financeiras'
            ]
        },
        'Consultor': {
            'direito_previdenciario': [
                'Consultoria em planejamento previdenciário familiar',
                'Orientação sobre regimes previdenciários',
                'Análise de viabilidade de contribuições',
                'Estratégias de otimização previdenciária',
                'Educação previdenciária corporativa'
            ],
            'direito_urbanistico': [
                'Consultoria em direito imobiliário urbano',
                'Orientação sobre usucapião urbano',
                'Análise de viabilidade de empreendimentos',
                'Estratégias de regularização predial',
                'Educação em legislação urbana'
            ],
            'credito_juridico': [
                'Consultoria em estruturação de financiamentos',
                'Orientação sobre produtos de crédito',
                'Análise de viabilidade de operações',
                'Estratégias de negociação bancária',
                'Educação financeira jurídica'
            ]
        },
        'Analista': {
            'direito_previdenciario': [
                'Análise documental previdenciária',
                'Verificação de direitos adquiridos',
                'Controle de prazos previdenciários',
                'Pesquisa de jurisprudência previdenciária',
                'Preparação de petições previdenciárias'
            ],
            'direito_urbanistico': [
                'Análise documental urbana',
                'Verificação de regularidade predial',
                'Controle de prazos administrativos',
                'Pesquisa de legislação municipal',
                'Preparação de requerimentos urbanos'
            ],
            'credito_juridico': [
                'Análise documental de operações de crédito',
                'Verificação de garantias oferecidas',
                'Controle de vencimentos financeiros',
                'Pesquisa de jurisprudência bancária',
                'Preparação de contratos de crédito'
            ]
        },
        'Pleno': {
            'direito_previdenciario': [
                'Execução de cálculos previdenciários medianos',
                'Acompanhamento de processos administrativos',
                'Interface com órgãos previdenciários',
                'Suporte técnico em benefícios sociais',
                'Desenvolvimento de rotinas previdenciárias'
            ],
            'direito_urbanistico': [
                'Execução de projetos urbanos de média complexidade',
                'Acompanhamento de licenciamentos municipais',
                'Interface com órgãos públicos urbanos',
                'Suporte técnico em questões prediais',
                'Desenvolvimento de processos urbanos'
            ],
            'credito_juridico': [
                'Execução de operações de crédito medianas',
                'Acompanhamento de garantias em curso',
                'Interface com instituições financeiras',
                'Suporte técnico em produtos bancários',
                'Desenvolvimento de rotinas creditícias'
            ]
        }
    }

def fix_duplicate_names_and_capabilities():
    """Corrige nomes duplicados e capacidades dos agentes"""
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        return False
    
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Buscar agentes duplicados
        result = session.execute(text("""
            SELECT nome, array_agg(id ORDER BY id) as ids
            FROM agente_juridico 
            GROUP BY nome 
            HAVING COUNT(*) > 1
            ORDER BY COUNT(*) DESC
        """))
        
        duplicates = result.fetchall()
        print(f"🔍 Encontrados {len(duplicates)} nomes duplicados")
        
        capabilities_dict = create_hierarchical_capabilities()
        updated_count = 0
        
        for duplicate in duplicates:
            nome_base, ids = duplicate
            print(f"📝 Corrigindo {len(ids)} agentes com nome: {nome_base}")
            
            for i, agent_id in enumerate(ids):
                # Criar nome único baseado na hierarquia
                if i == 0:
                    # Primeiro agente mantém o nome original
                    novo_nome = nome_base
                    nivel = 'Especialista'
                else:
                    # Outros agentes recebem sufixos hierárquicos
                    niveis = ['Sênior', 'Pleno', 'Júnior', 'Consultor', 'Analista']
                    nivel = niveis[i % len(niveis)]
                    
                    if nivel not in nome_base:
                        novo_nome = f"{nome_base} - {nivel}"
                    else:
                        novo_nome = f"{nome_base} {i+1}"
                
                # Determinar área especializada
                nome_lower = nome_base.lower()
                if 'previdenciário' in nome_lower or 'previdência' in nome_lower:
                    area = 'direito_previdenciario'
                elif 'urbanístico' in nome_lower or 'urbano' in nome_lower:
                    area = 'direito_urbanistico'
                elif 'crédito' in nome_lower or 'bancário' in nome_lower:
                    area = 'credito_juridico'
                else:
                    area = 'direito_previdenciario'  # fallback
                
                # Obter capacidades específicas
                if nivel in capabilities_dict and area in capabilities_dict[nivel]:
                    capacidades = capabilities_dict[nivel][area]
                else:
                    # Capacidades genéricas únicas
                    hash_value = int(hashlib.md5(f"{agent_id}{novo_nome}".encode()).hexdigest(), 16)
                    capacidades = [
                        f"Análise jurídica especializada #{hash_value % 1000}",
                        f"Consultoria técnica em {area.replace('_', ' ')}",
                        f"Gestão de processos específicos #{(hash_value + 1) % 1000}",
                        f"Auditoria de conformidade #{(hash_value + 2) % 1000}",
                        f"Orientação estratégica #{(hash_value + 3) % 1000}"
                    ]
                
                # Atualizar no banco
                capacidades_json = json.dumps(capacidades, ensure_ascii=False)
                session.execute(
                    text("UPDATE agente_juridico SET nome = :nome, capacidades = :caps WHERE id = :id"),
                    {"nome": novo_nome, "caps": capacidades_json, "id": agent_id}
                )
                
                updated_count += 1
                print(f"   ✅ {agent_id}: {novo_nome} - {nivel}")
        
        session.commit()
        print(f"\n🎉 {updated_count} agentes atualizados com nomes únicos e capacidades específicas")
        
        # Verificar resultado
        result = session.execute(text("SELECT COUNT(*) as total, COUNT(DISTINCT nome) as unicos FROM agente_juridico"))
        stats = result.fetchone()
        print(f"📊 Total: {stats[0]} agentes, Únicos: {stats[1]} nomes")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    print("🚀 Corrigindo nomes duplicados e capacidades...")
    success = fix_duplicate_names_and_capabilities()
    
    if success:
        print("✅ Correção concluída!")
    else:
        print("❌ Falha na correção")
        sys.exit(1)