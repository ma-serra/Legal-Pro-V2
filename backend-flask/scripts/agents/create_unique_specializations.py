#!/usr/bin/env python3
"""
Script para criar especializações únicas baseadas na experiência e área de cada agente.
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
        print(f"Erro ao conectar: {e}")
        return None

def create_specialized_capacities():
    """Cria capacidades especializadas baseadas no nível do agente"""
    
    specialization_matrix = {
        "Sênior": {
            "prefix": "Gestão estratégica e",
            "capacidades_base": [
                "Liderança de equipes jurídicas",
                "Desenvolvimento de estratégias complexas", 
                "Mentoria de profissionais juniores",
                "Negociação de alto nível",
                "Consultoria estratégica executiva"
            ]
        },
        "Pleno": {
            "prefix": "Execução especializada em",
            "capacidades_base": [
                "Análise de casos complexos",
                "Coordenação de projetos jurídicos",
                "Supervisão de processos",
                "Desenvolvimento de soluções inovadoras",
                "Treinamento de equipes operacionais"
            ]
        },
        "Júnior": {
            "prefix": "Suporte operacional em",
            "capacidades_base": [
                "Pesquisa jurídica especializada",
                "Elaboração de minutas",
                "Acompanhamento processual",
                "Organização de documentação",
                "Suporte em análises técnicas"
            ]
        },
        "Especialista": {
            "prefix": "Expertise técnica avançada em",
            "capacidades_base": [
                "Consultoria técnica especializada",
                "Desenvolvimento de metodologias",
                "Pesquisa e inovação jurídica",
                "Análise de cenários complexos",
                "Elaboração de pareceres técnicos"
            ]
        }
    }
    
    return specialization_matrix

def update_specialized_agents():
    """Atualiza agentes com especializações únicas"""
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        specialization_matrix = create_specialized_capacities()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("Criando especializações únicas para cada agente...")
        
        updated_count = 0
        
        for level, spec_data in specialization_matrix.items():
            # Busca agentes de cada nível
            cursor.execute("""
                SELECT id, nome, categoria_id 
                FROM agente_juridico 
                WHERE ativo = true 
                AND nome LIKE %s
                ORDER BY id
            """, (f"% - {level}",))
            
            agents = cursor.fetchall()
            
            for agent in agents:
                # Extrai área base do nome
                base_name = agent['nome'].replace(f" - {level}", "")
                area_focus = base_name.lower()
                
                # Cria capacidades específicas baseadas na área e nível
                if "bancário" in area_focus or "crédito" in area_focus:
                    domain_caps = [
                        f"{spec_data['prefix']} operações bancárias complexas",
                        "Análise de riscos financeiros avançados",
                        "Estruturação de produtos bancários",
                        "Compliance regulatório especializado",
                        "Gestão de carteiras de crédito"
                    ]
                elif "securitário" in area_focus or "seguro" in area_focus:
                    domain_caps = [
                        f"{spec_data['prefix']} produtos securitários",
                        "Análise atuarial de riscos",
                        "Estruturação de apólices complexas",
                        "Gestão de sinistros especializados",
                        "Consultoria em resseguros"
                    ]
                elif "trabalhista" in area_focus or "clt" in area_focus:
                    domain_caps = [
                        f"{spec_data['prefix']} relações trabalhistas",
                        "Gestão de passivos trabalhistas",
                        "Negociação com sindicatos",
                        "Estruturação de benefícios",
                        "Consultoria em reestruturações"
                    ]
                elif "previdenciário" in area_focus or "perícia" in area_focus:
                    domain_caps = [
                        f"{spec_data['prefix']} benefícios previdenciários",
                        "Análise de incapacidades complexas",
                        "Planejamento previdenciário estratégico",
                        "Gestão de recursos periciais",
                        "Consultoria em aposentadorias"
                    ]
                elif "tributário" in area_focus or "fiscal" in area_focus:
                    domain_caps = [
                        f"{spec_data['prefix']} planejamento tributário",
                        "Estruturação fiscal complexa",
                        "Gestão de contencioso fiscal",
                        "Otimização de cargas tributárias",
                        "Consultoria em reorganizações"
                    ]
                elif "digital" in area_focus or "lgpd" in area_focus:
                    domain_caps = [
                        f"{spec_data['prefix']} tecnologia e privacidade",
                        "Implementação de compliance digital",
                        "Gestão de dados corporativos",
                        "Consultoria em transformação digital",
                        "Estratégias de proteção cibernética"
                    ]
                else:
                    # Capacidades genéricas baseadas no nível
                    domain_caps = spec_data['capacidades_base']
                
                # Cria prompt especializado
                specialized_prompt = f"""Você é {agent['nome']}, um profissional {level.lower()} especializado em {base_name.lower()}.

**NÍVEL DE ESPECIALIZAÇÃO: {level.upper()}**

**SUAS CAPACIDADES PRINCIPAIS:**
{chr(10).join([f"{i+1}. {cap}" for i, cap in enumerate(domain_caps)])}

**METODOLOGIA DE TRABALHO:**
- Abordagem {level.lower()} com foco em resultados
- Análise fundamentada em experiência prática
- Soluções adaptadas ao nível de complexidade
- Orientação baseada em melhores práticas do mercado

**INSTRUÇÕES:**
- Forneça análises técnicas precisas
- Adapte a profundidade conforme a complexidade
- Identifique oportunidades e riscos
- Ofereça recomendações práticas e implementáveis

Responda sempre de forma profissional e fundamentada em sua experiência como {level.lower()}."""
                
                # Atualiza o agente
                cursor.execute("""
                    UPDATE agente_juridico 
                    SET capacidades = %s,
                        template_prompt = %s
                    WHERE id = %s
                """, (
                    json.dumps(domain_caps, ensure_ascii=False),
                    specialized_prompt,
                    agent['id']
                ))
                
                updated_count += 1
                print(f"Atualizado: {agent['nome']}")
        
        conn.commit()
        print(f"\nTotal de agentes especializados: {updated_count}")
        return True
        
    except Exception as e:
        print(f"Erro na especialização: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    """Função principal"""
    print("Iniciando criação de especializações únicas...")
    
    if update_specialized_agents():
        print("Especialização concluída com sucesso!")
        print("Agentes agora possuem capacidades únicas baseadas em seu nível!")
    else:
        print("Falha na especialização!")
        sys.exit(1)

if __name__ == "__main__":
    main()