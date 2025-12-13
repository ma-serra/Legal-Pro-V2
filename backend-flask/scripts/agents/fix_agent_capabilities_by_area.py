#!/usr/bin/env python3
"""
Script para corrigir capacidades dos agentes por área jurídica específica.
Cada área terá capacidades únicas e especializadas.
"""
import os
import sys
import json
import psycopg2
from psycopg2.extras import RealDictCursor

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_database_connection():
    """Obtém conexão com o banco de dados"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        return psycopg2.connect(database_url)
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None

def get_specialized_capabilities_by_area():
    """Define capacidades específicas por área jurídica"""
    
    area_capabilities = {
        "Direito Bancário": {
            "base_capacidades": [
                "Análise de contratos bancários",
                "Avaliação de riscos financeiros", 
                "Consultoria em produtos bancários",
                "Compliance bancário e regulamentação",
                "Negociação de condições creditícias"
            ],
            "nivel_5": [
                "Gestão estratégica de carteiras bancárias",
                "Supervisão de compliance regulatório",
                "Coordenação de operações complexas",
                "Mentoria em produtos financeiros",
                "Consultoria executiva bancária"
            ],
            "nivel_4": [
                "Estruturação de operações bancárias",
                "Análise atuarial de crédito",
                "Consultoria em produtos financeiros",
                "Auditoria de processos bancários",
                "Gestão de riscos especializados"
            ],
            "nivel_3": [
                "Análise de casos bancários complexos",
                "Coordenação de projetos financeiros",
                "Supervisão de processos creditícios",
                "Desenvolvimento de soluções bancárias",
                "Treinamento de equipes bancárias"
            ]
        },
        
        "Direito Securitário": {
            "base_capacidades": [
                "Análise de apólices de seguro",
                "Verificação de coberturas contratadas",
                "Avaliação de exclusões e limitações",
                "Análise de prêmios e franquias",
                "Orientação sobre renovações"
            ],
            "nivel_5": [
                "Gestão estratégica de produtos securitários",
                "Análise atuarial de riscos",
                "Estruturação de apólices complexas",
                "Gestão de sinistros especializados",
                "Consultoria em resseguros"
            ],
            "nivel_4": [
                "Análise técnica de sinistros",
                "Consultoria em coberturas especiais",
                "Auditoria de processos securitários",
                "Avaliação de riscos empresariais",
                "Estruturação de produtos seguros"
            ],
            "nivel_3": [
                "Execução de análises securitárias",
                "Coordenação de processos de sinistros",
                "Supervisão de avaliações de risco",
                "Desenvolvimento de coberturas",
                "Treinamento em produtos de seguro"
            ]
        },
        
        "Direito Trabalhista": {
            "base_capacidades": [
                "Análise de contratos de trabalho",
                "Cálculo de verbas rescisórias",
                "Avaliação de cumprimento da CLT",
                "Orientação sobre direitos trabalhistas",
                "Consultoria em relações sindicais"
            ],
            "nivel_5": [
                "Gestão estratégica de relações trabalhistas",
                "Supervisão de passivos trabalhistas",
                "Negociação coletiva de trabalho",
                "Estruturação de benefícios corporativos",
                "Consultoria em reestruturações empresariais"
            ],
            "nivel_4": [
                "Análise de processos trabalhistas complexos",
                "Consultoria em segurança do trabalho",
                "Auditoria de práticas trabalhistas",
                "Gestão de contingências trabalhistas",
                "Especialização em acordos coletivos"
            ],
            "nivel_3": [
                "Execução de análises trabalhistas",
                "Coordenação de processos CLT",
                "Supervisão de cálculos trabalhistas",
                "Desenvolvimento de políticas internas",
                "Treinamento em legislação trabalhista"
            ]
        },
        
        "Direito Tributário": {
            "base_capacidades": [
                "Análise de obrigações tributárias",
                "Planejamento fiscal empresarial",
                "Consultoria em impostos federais",
                "Avaliação de benefícios fiscais",
                "Orientação sobre compliance fiscal"
            ],
            "nivel_5": [
                "Gestão estratégica de planejamento tributário",
                "Supervisão de contencioso fiscal",
                "Coordenação de reorganizações societárias",
                "Consultoria executiva em tributos",
                "Mentoria em otimização fiscal"
            ],
            "nivel_4": [
                "Estruturação de operações fiscais",
                "Análise de contingências tributárias",
                "Consultoria em tributos especiais",
                "Auditoria fiscal especializada",
                "Gestão de processos administrativos"
            ],
            "nivel_3": [
                "Execução de análises tributárias",
                "Coordenação de processos fiscais",
                "Supervisão de cálculos de impostos",
                "Desenvolvimento de estratégias fiscais",
                "Treinamento em legislação tributária"
            ]
        },
        
        "Direito Empresarial": {
            "base_capacidades": [
                "Análise de contratos societários",
                "Consultoria em fusões e aquisições",
                "Avaliação de governança corporativa",
                "Orientação sobre compliance empresarial",
                "Estruturação de operações societárias"
            ],
            "nivel_5": [
                "Gestão estratégica de operações empresariais",
                "Supervisão de M&A complexos",
                "Coordenação de reestruturações societárias",
                "Consultoria executiva corporativa",
                "Mentoria em governança empresarial"
            ],
            "nivel_4": [
                "Estruturação de joint ventures",
                "Análise de due diligence",
                "Consultoria em reorganizações",
                "Auditoria de processos societários",
                "Gestão de compliance corporativo"
            ],
            "nivel_3": [
                "Execução de análises societárias",
                "Coordenação de processos empresariais",
                "Supervisão de contratos comerciais",
                "Desenvolvimento de estruturas societárias",
                "Treinamento em direito empresarial"
            ]
        },
        
        "Direito Penal": {
            "base_capacidades": [
                "Análise de tipos penais",
                "Estratégias para Tribunal do Júri",
                "Avaliação de provas criminais",
                "Orientação sobre defesas penais",
                "Consultoria em compliance criminal"
            ],
            "nivel_5": [
                "Coordenação estratégica de casos criminais",
                "Supervisão de equipe criminal",
                "Análise de riscos processuais penais",
                "Desenvolvimento de estratégias integradas",
                "Consultoria em crimes empresariais"
            ],
            "nivel_4": [
                "Análise técnica de evidências criminais",
                "Consultoria em crimes econômicos",
                "Auditoria de processos penais",
                "Especialização em criminal compliance",
                "Gestão de crises criminais"
            ],
            "nivel_3": [
                "Execução de análises criminais",
                "Coordenação de processos penais",
                "Supervisão de investigações",
                "Desenvolvimento de estratégias defensivas",
                "Treinamento em direito penal"
            ]
        },
        
        "Direito Digital": {
            "base_capacidades": [
                "Implementação da LGPD",
                "Gestão de incidentes de dados",
                "Consultoria em proteção de dados",
                "Avaliação de riscos digitais",
                "Orientação sobre compliance digital"
            ],
            "nivel_5": [
                "Gestão estratégica de transformação digital",
                "Supervisão de projetos LGPD",
                "Coordenação de segurança de dados",
                "Consultoria executiva em tecnologia",
                "Mentoria em inovação digital"
            ],
            "nivel_4": [
                "Estruturação de programas de privacidade",
                "Análise de impacto de dados",
                "Consultoria em cibersegurança",
                "Auditoria de sistemas digitais",
                "Gestão de conformidade tecnológica"
            ],
            "nivel_3": [
                "Execução de análises de privacidade",
                "Coordenação de projetos digitais",
                "Supervisão de compliance LGPD",
                "Desenvolvimento de políticas de dados",
                "Treinamento em direito digital"
            ]
        },
        
        "Direito Previdenciário": {
            "base_capacidades": [
                "Análise de benefícios previdenciários",
                "Cálculo de aposentadorias",
                "Consultoria em perícia médica",
                "Orientação sobre INSS",
                "Avaliação de incapacidades"
            ],
            "nivel_5": [
                "Gestão estratégica de benefícios",
                "Supervisão de processos previdenciários",
                "Coordenação de perícias complexas",
                "Consultoria executiva previdenciária",
                "Mentoria em direitos previdenciários"
            ],
            "nivel_4": [
                "Análise técnica de incapacidades",
                "Consultoria em aposentadorias especiais",
                "Auditoria previdenciária",
                "Especialização em benefícios rurais",
                "Gestão de processos administrativos"
            ],
            "nivel_3": [
                "Execução de análises previdenciárias",
                "Coordenação de processos INSS",
                "Supervisão de cálculos atuariais",
                "Desenvolvimento de estratégias previdenciárias",
                "Treinamento em legislação previdenciária"
            ]
        },
        
        "Direito do Consumidor": {
            "base_capacidades": [
                "Análise de relações de consumo",
                "Avaliação de vícios de produtos",
                "Consultoria em direitos básicos",
                "Orientação sobre CDC",
                "Mediação de conflitos consumeristas"
            ],
            "nivel_5": [
                "Gestão estratégica de defesa do consumidor",
                "Supervisão de processos coletivos",
                "Coordenação de ações civis públicas",
                "Consultoria executiva consumerista",
                "Mentoria em proteção do consumidor"
            ],
            "nivel_4": [
                "Análise técnica de danos materiais",
                "Consultoria em publicidade abusiva",
                "Auditoria de práticas comerciais",
                "Especialização em e-commerce",
                "Gestão de recall de produtos"
            ],
            "nivel_3": [
                "Execução de análises consumeristas",
                "Coordenação de processos CDC",
                "Supervisão de mediações",
                "Desenvolvimento de políticas de consumo",
                "Treinamento em direito do consumidor"
            ]
        },
        
        "Direito Ambiental": {
            "base_capacidades": [
                "Análise de licenciamento ambiental",
                "Consultoria em conformidade ambiental",
                "Avaliação de impactos ambientais",
                "Orientação sobre legislação ambiental",
                "Gestão de riscos ambientais"
            ],
            "nivel_5": [
                "Gestão estratégica ambiental",
                "Supervisão de projetos sustentáveis",
                "Coordenação de licenciamentos complexos",
                "Consultoria executiva ambiental",
                "Mentoria em sustentabilidade"
            ],
            "nivel_4": [
                "Análise técnica de EIA/RIMA",
                "Consultoria em energia renovável",
                "Auditoria ambiental especializada",
                "Especialização em crimes ambientais",
                "Gestão de passivos ambientais"
            ],
            "nivel_3": [
                "Execução de análises ambientais",
                "Coordenação de processos de licenciamento",
                "Supervisão de monitoramento ambiental",
                "Desenvolvimento de políticas ambientais",
                "Treinamento em legislação ambiental"
            ]
        },
        
        "Direito Imobiliário": {
            "base_capacidades": [
                "Análise de contratos imobiliários",
                "Consultoria em incorporações",
                "Avaliação de registros imobiliários",
                "Orientação sobre locações",
                "Gestão de patrimônio imobiliário"
            ],
            "nivel_5": [
                "Gestão estratégica de empreendimentos",
                "Supervisão de grandes incorporações",
                "Coordenação de projetos imobiliários",
                "Consultoria executiva imobiliária",
                "Mentoria em desenvolvimento urbano"
            ],
            "nivel_4": [
                "Estruturação de fundos imobiliários",
                "Análise de viabilidade de projetos",
                "Consultoria em financiamento imobiliário",
                "Auditoria de cartórios",
                "Especialização em direito urbanístico"
            ],
            "nivel_3": [
                "Execução de análises imobiliárias",
                "Coordenação de processos registrais",
                "Supervisão de contratos de locação",
                "Desenvolvimento de projetos habitacionais",
                "Treinamento em direito imobiliário"
            ]
        },
        
        "Análise de Riscos Jurídicos": {
            "base_capacidades": [
                "Due diligence jurídica",
                "Análise de riscos multidisciplinares",
                "Consultoria em compliance integrado",
                "Avaliação de contingências",
                "Gestão de auditoria jurídica"
            ],
            "nivel_5": [
                "Coordenação transversal de análise de riscos",
                "Supervisão de due diligence complexa",
                "Gestão de compliance sistêmico",
                "Análise de riscos estratégicos",
                "Consultoria executiva em auditoria"
            ],
            "nivel_4": [
                "Análise técnica de contingências",
                "Consultoria em gestão de riscos",
                "Auditoria jurídica especializada",
                "Especialização em compliance setorial",
                "Gestão de crises jurídicas"
            ],
            "nivel_3": [
                "Execução de análises de risco",
                "Coordenação de processos de auditoria",
                "Supervisão de compliance operacional",
                "Desenvolvimento de controles internos",
                "Treinamento em gestão de riscos"
            ]
        }
    }
    
    return area_capabilities

def update_agent_capabilities():
    """Atualiza capacidades dos agentes por área específica"""
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        area_capabilities = get_specialized_capabilities_by_area()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔧 CORRIGINDO CAPACIDADES DOS AGENTES POR ÁREA...")
        print("🎯 Aplicando especialização por área jurídica\n")
        
        total_updated = 0
        
        for area_nome, capacidades_data in area_capabilities.items():
            print(f"📋 ÁREA: {area_nome}")
            
            # Busca categoria correspondente
            cursor.execute("""
                SELECT id FROM categoria_juridica 
                WHERE nome ILIKE %s OR nome ILIKE %s
            """, (f"%{area_nome}%", f"%{area_nome.replace('Direito ', '')}%"))
            
            categoria = cursor.fetchone()
            if not categoria:
                print(f"   ⚠️  Categoria não encontrada")
                continue
            
            categoria_id = categoria['id']
            
            # Atualiza agentes por nível
            for nivel in [5, 4, 3]:
                if f"nivel_{nivel}" in capacidades_data:
                    capacidades = capacidades_data[f"nivel_{nivel}"]
                else:
                    capacidades = capacidades_data["base_capacidades"]
                
                cursor.execute("""
                    UPDATE agente_juridico 
                    SET capacidades = %s
                    WHERE categoria_id = %s 
                    AND ativo = true 
                    AND (nivel_especializacao = %s OR nivel_especializacao IS NULL)
                """, (json.dumps(capacidades, ensure_ascii=False), categoria_id, nivel))
                
                updated_count = cursor.rowcount
                total_updated += updated_count
                
                if updated_count > 0:
                    print(f"   ✅ Nível {nivel}: {updated_count} agentes atualizados")
            
            # Atualiza agentes sem nível específico com capacidades base
            cursor.execute("""
                UPDATE agente_juridico 
                SET capacidades = %s
                WHERE categoria_id = %s 
                AND ativo = true 
                AND nivel_especializacao NOT IN (3, 4, 5)
            """, (json.dumps(capacidades_data["base_capacidades"], ensure_ascii=False), categoria_id))
            
            base_updated = cursor.rowcount
            total_updated += base_updated
            
            if base_updated > 0:
                print(f"   ✅ Base: {base_updated} agentes atualizados")
        
        conn.commit()
        
        print(f"\n🎉 CORREÇÃO CONCLUÍDA!")
        print(f"📊 Total de agentes atualizados: {total_updated}")
        print(f"🎯 Capacidades específicas por área aplicadas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na correção: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def validate_capabilities():
    """Valida capacidades corrigidas"""
    conn = get_database_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("\n📊 VALIDAÇÃO DAS CAPACIDADES CORRIGIDAS:")
        
        # Amostra de capacidades por área
        cursor.execute("""
            SELECT cj.nome as categoria, aj.nome as agente, aj.capacidades
            FROM agente_juridico aj
            JOIN categoria_juridica cj ON aj.categoria_id = cj.id
            WHERE aj.ativo = true 
            AND aj.capacidades IS NOT NULL
            ORDER BY cj.nome, aj.nivel_especializacao DESC
            LIMIT 20
        """)
        
        samples = cursor.fetchall()
        
        current_area = None
        for sample in samples:
            if sample['categoria'] != current_area:
                current_area = sample['categoria']
                print(f"\n🎯 {current_area}:")
            
            capacidades = json.loads(sample['capacidades']) if sample['capacidades'] else []
            primeira_capacidade = capacidades[0] if capacidades else "Sem capacidades"
            print(f"   • {sample['agente']}: {primeira_capacidade}")
        
        # Estatísticas gerais
        cursor.execute("""
            SELECT cj.nome as categoria, 
                   COUNT(*) as total_agentes,
                   COUNT(CASE WHEN aj.capacidades IS NOT NULL THEN 1 END) as com_capacidades
            FROM agente_juridico aj
            JOIN categoria_juridica cj ON aj.categoria_id = cj.id
            WHERE aj.ativo = true
            GROUP BY cj.nome
            ORDER BY COUNT(*) DESC
        """)
        
        stats = cursor.fetchall()
        print(f"\n📈 ESTATÍSTICAS POR ÁREA:")
        for stat in stats:
            percentual = (stat['com_capacidades'] * 100.0 / stat['total_agentes']) if stat['total_agentes'] > 0 else 0
            print(f"   {stat['categoria']}: {stat['com_capacidades']}/{stat['total_agentes']} ({percentual:.1f}%)")
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
    finally:
        conn.close()

def main():
    """Função principal"""
    print("🚀 INICIANDO CORREÇÃO DE CAPACIDADES POR ÁREA...")
    
    if update_agent_capabilities():
        validate_capabilities()
        print("\n🎯 Capacidades corrigidas por área específica!")
    else:
        print("\n❌ Falha na correção!")
        sys.exit(1)

if __name__ == "__main__":
    main()