#!/usr/bin/env python3
"""
Script para atualizar as capacidades específicas dos agentes jurídicos.
Baseado nas definições encontradas em multiagent/utils/init_juridico_db.py
"""
import os
import sys
import json
import psycopg2
from psycopg2.extras import RealDictCursor

# Adiciona o diretório raiz ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_database_connection():
    """Obtém conexão com o banco de dados"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL não encontrada nas variáveis de ambiente")
        
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"Erro ao conectar com banco: {e}")
        return None

def get_specialized_capacidades():
    """Define as capacidades específicas para cada tipo de agente jurídico"""
    capacidades_mapping = {
        # Agentes Bancários
        "Analista de Compliance Bancário": [
            "Análise de conformidade regulatória bancária",
            "Avaliação de políticas de compliance",
            "Identificação de riscos de conformidade",
            "Elaboração de relatórios regulatórios",
            "Monitoramento de mudanças regulamentares"
        ],
        "Consultor em Resseguros": [
            "Análise de contratos de resseguro",
            "Avaliação de cláusulas contratuais",
            "Verificação de conformidade SUSEP",
            "Gestão de riscos de resseguro",
            "Elaboração de pareceres técnicos"
        ],
        "Especialista em Cartões de Crédito": [
            "Análise de contratos de cartão de crédito",
            "Verificação de conformidade com Bacen",
            "Avaliação de práticas comerciais",
            "Análise de tarifas e encargos",
            "Resolução de conflitos contratuais"
        ],
        
        # Agentes Securitários
        "Analista de Apólices de Seguro": [
            "Análise detalhada de apólices",
            "Verificação de coberturas contratadas",
            "Avaliação de exclusões e limitações",
            "Análise de prêmios e franquias",
            "Orientação sobre renovações"
        ],
        "Consultor em Sinistros": [
            "Análise de procedimentos de sinistros",
            "Avaliação de documentação necessária",
            "Verificação de prazos regulamentares",
            "Análise de negativas de cobertura",
            "Mediação de conflitos securitários"
        ],
        
        # Agentes Trabalhistas
        "Analista de Benefícios Trabalhistas": [
            "Análise de benefícios obrigatórios",
            "Verificação de cumprimento da CLT",
            "Avaliação de benefícios adicionais",
            "Cálculo de verbas rescisórias",
            "Orientação sobre direitos trabalhistas"
        ],
        "Especialista em Relações Sindicais": [
            "Análise de acordos coletivos",
            "Negociação com sindicatos",
            "Verificação de cláusulas sindicais",
            "Gestão de conflitos trabalhistas",
            "Orientação sobre contribuições sindicais"
        ],
        
        # Agentes Previdenciários
        "Analista de Perícia Médica Previdenciária": [
            "Análise de laudos médicos periciais",
            "Avaliação de incapacidade laboral",
            "Verificação de nexo causal",
            "Orientação sobre benefícios por incapacidade",
            "Acompanhamento de revisões periciais"
        ],
        "Consultor em Aposentadorias": [
            "Cálculo de tempo de contribuição",
            "Análise de regras de transição",
            "Verificação de direitos adquiridos",
            "Planejamento previdenciário",
            "Orientação sobre aposentadorias especiais"
        ],
        
        # Agentes Tributários
        "Analista de Planejamento Tributário": [
            "Estruturação de planejamento fiscal",
            "Análise de regimes tributários",
            "Otimização da carga tributária",
            "Verificação de benefícios fiscais",
            "Elaboração de estudos tributários"
        ],
        "Especialista em Contencioso Fiscal": [
            "Defesa em processos administrativos",
            "Análise de autos de infração",
            "Recursos em esferas administrativas",
            "Parcelamentos e transações",
            "Estratégias de defesa fiscal"
        ],
        
        # Agentes Imobiliários
        "Consultor em Direito Urbanístico": [
            "Análise de zoneamento urbano",
            "Verificação de conformidade urbanística",
            "Licenciamentos e aprovações",
            "Regularização fundiária",
            "Análise de impactos urbanísticos"
        ],
        "Analista de Contratos Imobiliários": [
            "Análise de contratos de compra e venda",
            "Verificação de documentação imobiliária",
            "Análise de financiamentos imobiliários",
            "Due diligence imobiliária",
            "Resolução de conflitos contratuais"
        ],
        
        # Agentes Empresariais
        "Analista de Governança Corporativa": [
            "Estruturação de governança corporativa",
            "Análise de políticas internas",
            "Verificação de compliance corporativo",
            "Elaboração de códigos de conduta",
            "Gestão de riscos corporativos"
        ],
        "Consultor em Fusões e Aquisições": [
            "Due diligence jurídica",
            "Estruturação de operações de M&A",
            "Análise de contratos societários",
            "Verificação regulatória de operações",
            "Negociação de termos contratuais"
        ],
        
        # Agentes Digitais/Tecnologia
        "Analista de Proteção de Dados": [
            "Implementação de conformidade LGPD",
            "Análise de políticas de privacidade",
            "Gestão de incidentes de dados",
            "Elaboração de contratos de processamento",
            "Treinamento em proteção de dados"
        ],
        "Especialista em Direito Digital": [
            "Análise de contratos digitais",
            "Verificação de termos de uso",
            "Proteção de propriedade intelectual",
            "Compliance em plataformas digitais",
            "Resolução de conflitos online"
        ],
        
        # Agentes Ambientais
        "Consultor em Licenciamento Ambiental": [
            "Análise de processos de licenciamento",
            "Verificação de conformidade ambiental",
            "Elaboração de estudos ambientais",
            "Gestão de condicionantes ambientais",
            "Renovação de licenças ambientais"
        ],
        "Analista de Compliance Ambiental": [
            "Auditoria de conformidade ambiental",
            "Análise de legislação ambiental",
            "Gestão de passivos ambientais",
            "Elaboração de planos de adequação",
            "Monitoramento regulatório ambiental"
        ]
    }
    
    return capacidades_mapping

def update_agent_capacidades():
    """Atualiza as capacidades dos agentes no banco de dados"""
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        capacidades_mapping = get_specialized_capacidades()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Primeiro, obtém todos os agentes que precisam de atualização
        cursor.execute("""
            SELECT id, nome, capacidades 
            FROM agente_juridico 
            WHERE ativo = true
            ORDER BY nome
        """)
        
        agentes = cursor.fetchall()
        updated_count = 0
        
        for agente in agentes:
            nome = agente['nome']
            
            # Verifica se existe capacidade específica para este agente
            if nome in capacidades_mapping:
                new_capacidades = capacidades_mapping[nome]
                
                # Atualiza as capacidades
                cursor.execute("""
                    UPDATE agente_juridico 
                    SET capacidades = %s 
                    WHERE id = %s
                """, (json.dumps(new_capacidades, ensure_ascii=False), agente['id']))
                
                updated_count += 1
                print(f"✅ Atualizado: {nome}")
            else:
                # Para agentes sem mapeamento específico, usa capacidades genéricas
                current_caps = agente['capacidades']
                if not current_caps or (isinstance(current_caps, list) and len(current_caps) < 3):
                    generic_capacidades = [
                        f"Análise especializada em {nome.lower()}",
                        "Elaboração de pareceres jurídicos",
                        "Consultoria técnica especializada",
                        "Verificação de conformidade legal",
                        "Gestão de riscos jurídicos"
                    ]
                    
                    cursor.execute("""
                        UPDATE agente_juridico 
                        SET capacidades = %s 
                        WHERE id = %s
                    """, (json.dumps(generic_capacidades, ensure_ascii=False), agente['id']))
                    
                    updated_count += 1
                    print(f"⚠️  Atualizado (genérico): {nome}")
        
        conn.commit()
        print(f"\n🎉 Total de agentes atualizados: {updated_count}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar capacidades: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    """Função principal"""
    print("🚀 Iniciando atualização das capacidades dos agentes jurídicos...")
    
    if update_agent_capacidades():
        print("✅ Atualização concluída com sucesso!")
    else:
        print("❌ Falha na atualização!")
        sys.exit(1)

if __name__ == "__main__":
    main()