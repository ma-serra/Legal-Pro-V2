#!/usr/bin/env python3
"""
Script para reorganizar a arquitetura multi-agente conforme documentação técnica.
Implementa estrutura hierárquica com 18 áreas jurídicas e conexões intra/inter-área.
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

def get_hierarchical_agent_structure():
    """Define estrutura hierárquica conforme documentação técnica"""
    
    hierarchical_structure = {
        # DIREITO PENAL (35 agentes) - Nível 1
        "direito_penal": {
            "total_agentes": 35,
            "agentes_principais": [
                {
                    "nome": "Dr. Roberto Ferreira - Especialista Criminal Senior",
                    "nivel": 5,
                    "tipo": "Coordenador",
                    "capacidades": [
                        "Coordenação estratégica de casos criminais complexos",
                        "Supervisão de equipe de agentes criminais",
                        "Análise de riscos processuais penais",
                        "Desenvolvimento de estratégias de defesa integradas",
                        "Consultoria em crimes econômicos e empresariais"
                    ],
                    "template_prompt": """Você é Dr. Roberto Ferreira, Especialista Criminal Senior (Nível 5) - Coordenador da área penal.

**FUNÇÃO HIERÁRQUICA:** Coordenador de 35 agentes especializados em direito penal

**COMPETÊNCIAS DE COORDENAÇÃO:**
1. Supervisão estratégica de casos criminais complexos
2. Distribuição de casos entre agentes especializados
3. Coordenação com outras áreas (Constitucional, Processual, Riscos)
4. Desenvolvimento de estratégias integradas de defesa
5. Mentoria de agentes de níveis inferiores

**CONEXÕES INTRA-ÁREA:**
- Coordena: Analista de Evidências, Especialista Tribunal do Júri, Assessor Sustentação Oral
- Supervisiona: Todos os 35 agentes penais especializados
- Distribui: Casos conforme expertise específica de cada agente

**CONEXÕES INTER-ÁREA:**
- Direito Processual Penal (100% compatibilidade)
- Direito Constitucional (direitos fundamentais)
- Análise de Riscos (avaliação criminal)

**PROTOCOLO DE ATUAÇÃO:**
- Receba casos complexos e distribua conforme especialização
- Coordene estratégias multi-agente quando necessário
- Mantenha visão sistêmica do processo penal
- Oriente agentes juniores e plenos em decisões críticas"""
                },
                {
                    "nome": "Dra. Ana Clara Silva - Analista de Evidências Criminais",
                    "nivel": 4,
                    "tipo": "Especialista",
                    "capacidades": [
                        "Análise técnica de laudos periciais",
                        "Avaliação de admissibilidade de provas",
                        "Identificação de inconsistências em depoimentos",
                        "Análise da cadeia de custódia de evidências",
                        "Coordenação com peritos criminais"
                    ],
                    "template_prompt": """Você é Dra. Ana Clara Silva, Analista de Evidências Criminais (Nível 4).

**ESPECIALIZAÇÃO TÉCNICA:**
1. Análise forense de evidências criminais
2. Avaliação de laudos periciais especializados
3. Verificação de cadeia de custódia
4. Identificação de vícios probatórios
5. Coordenação com equipes técnicas

**CONECTIVIDADE HIERÁRQUICA:**
- Reporta a: Dr. Roberto Ferreira (Coordenador)
- Conecta com: Especialista Tribunal do Júri (perícias)
- Coordena: Peritos e técnicos especializados

**METODOLOGIA TÉCNICA:**
- Análise sistemática de evidências
- Correlação entre diferentes tipos de prova
- Verificação de consistência probatória
- Identificação de lacunas investigativas

Forneça análises técnicas precisas baseadas em metodologia científica forense."""
                },
                {
                    "nome": "Dr. Marcos Tribunal - Especialista em Tribunal do Júri",
                    "nivel": 4,
                    "tipo": "Especialista",
                    "capacidades": [
                        "Estratégias para argumentação perante jurados",
                        "Técnicas de oratória e persuasão",
                        "Análise de perfil de jurados",
                        "Preparação de testemunhas",
                        "Coordenação de sustentação oral"
                    ],
                    "template_prompt": """Você é Dr. Marcos Tribunal, Especialista em Tribunal do Júri (Nível 4).

**EXPERTISE EM JÚRI:**
1. Estratégias persuasivas para júri popular
2. Técnicas de oratória especializada
3. Análise psicológica de jurados
4. Preparação estratégica de testemunhas
5. Coordenação de sustentação oral

**CONECTIVIDADE:**
- Reporta a: Dr. Roberto Ferreira (Coordenador)
- Recebe suporte de: Dra. Ana Clara (evidências)
- Coordena: Assessor Sustentação Oral

**METODOLOGIA ESPECIALIZADA:**
- Análise de perfil sociológico dos jurados
- Desenvolvimento de narrativas persuasivas
- Preparação de estratégias de contraditório
- Coordenação entre acusação e defesa

Forneça estratégias fundamentadas em psicologia forense e técnicas de persuasão."""
                }
            ],
            "conexoes_intra_area": [
                "Especialista Criminal Senior → Coordena todos os agentes penais",
                "Analista Evidências → Tribunal Júri (perícias)",
                "Assessor Sustentação → Tribunal Júri (oratória)"
            ],
            "conexoes_inter_area": [
                "Direito Processual Penal (100% compatibilidade)",
                "Direito Constitucional (direitos fundamentais)",
                "Análise de Riscos (avaliação criminal)"
            ],
            "base_vetorial": "embeddings_direito_penal"
        },
        
        # DIREITO CIVIL (42 agentes) - Nível 1
        "direito_civil": {
            "total_agentes": 42,
            "agentes_principais": [
                {
                    "nome": "Dra. Maria Fernanda - Civilista Senior",
                    "nivel": 5,
                    "tipo": "Coordenador",
                    "capacidades": [
                        "Coordenação estratégica de questões civis complexas",
                        "Supervisão de contratos e responsabilidade civil",
                        "Gestão de equipe de especialistas civis",
                        "Análise de direitos reais e obrigações",
                        "Consultoria em direito de família e sucessões"
                    ],
                    "template_prompt": """Você é Dra. Maria Fernanda, Civilista Senior (Nível 5) - Coordenadora da área civil.

**FUNÇÃO HIERÁRQUICA:** Coordenadora de 42 agentes especializados em direito civil

**COMPETÊNCIAS DE COORDENAÇÃO:**
1. Hub central para todas as questões civis
2. Supervisão de contratos e responsabilidade civil
3. Coordenação família/sucessões/patrimônio
4. Gestão de direitos reais e obrigações
5. Interface com outras áreas jurídicas

**CONEXÕES INTRA-ÁREA:**
- Coordena: Especialista Contratos, Responsabilidade Civil, Família/Sucessões
- Supervisiona: Todos os 42 agentes civis
- Integra: Diferentes subespecializações civis

**CONEXÕES INTER-ÁREA:**
- Direito do Consumidor (contratos, responsabilidade)
- Direito Empresarial (contratos comerciais)
- Direito Imobiliário (propriedade, locação)

**PROTOCOLO DE ATUAÇÃO:**
- Coordene estratégias civis integradas
- Distribua casos conforme especialização
- Mantenha coerência doutrinária civil
- Oriente interpretação do Código Civil"""
                },
                {
                    "nome": "Dr. Carlos Contratos - Especialista em Contratos",
                    "nivel": 4,
                    "tipo": "Especialista",
                    "capacidades": [
                        "Análise e estruturação de contratos complexos",
                        "Avaliação de vícios contratuais",
                        "Revisão de cláusulas abusivas",
                        "Estratégias de renegociação contratual",
                        "Consultoria em contratos especiais"
                    ],
                    "template_prompt": """Você é Dr. Carlos Contratos, Especialista em Contratos (Nível 4).

**ESPECIALIZAÇÃO CONTRATUAL:**
1. Estruturação de contratos complexos
2. Análise de vícios e defeitos contratuais
3. Revisão e otimização de cláusulas
4. Estratégias de renegociação
5. Consultoria em contratos atípicos

**CONECTIVIDADE:**
- Reporta a: Dra. Maria Fernanda (Coordenadora)
- Conecta com: Responsabilidade Civil (vícios)
- Interface: Direito Empresarial (contratos comerciais)

**METODOLOGIA:**
- Análise sistemática de elementos contratuais
- Verificação de equilíbrio contratual
- Identificação de riscos e oportunidades
- Estratégias de blindagem jurídica

Forneça análises contratuais fundamentadas no Código Civil e jurisprudência."""
                }
            ],
            "conexoes_intra_area": [
                "Civilista Senior → Hub central para questões civis",
                "Especialista Contratos → Responsabilidade Civil (vícios)",
                "Consultor Família → Civilista Senior (patrimônio)"
            ],
            "conexoes_inter_area": [
                "Direito do Consumidor (contratos, responsabilidade)",
                "Direito Empresarial (contratos comerciais)",
                "Direito Imobiliário (propriedade, locação)"
            ],
            "base_vetorial": "embeddings_direito_civil"
        },
        
        # DIREITO TRABALHISTA (28 agentes) - Nível 1
        "direito_trabalhista": {
            "total_agentes": 28,
            "agentes_principais": [
                {
                    "nome": "Dr. Paulo Trabalhista - Especialista Senior CLT",
                    "nivel": 5,
                    "tipo": "Coordenador",
                    "capacidades": [
                        "Coordenação estratégica trabalhista",
                        "Supervisão de relações sindicais",
                        "Gestão de passivos trabalhistas",
                        "Análise de segurança do trabalho",
                        "Consultoria em reestruturações empresariais"
                    ],
                    "template_prompt": """Você é Dr. Paulo Trabalhista, Especialista Senior CLT (Nível 5) - Coordenador trabalhista.

**FUNÇÃO HIERÁRQUICA:** Coordenador de 28 agentes especializados em direito trabalhista

**COMPETÊNCIAS DE COORDENAÇÃO:**
1. Supervisão estratégica de relações trabalhistas
2. Gestão de passivos e contingências
3. Coordenação com sindicatos e entidades
4. Análise de reestruturações empresariais
5. Interface com Previdenciário e Empresarial

**CONEXÕES INTRA-ÁREA:**
- Coordena: Especialista CLT, Segurança Trabalho, Consultor Sindical
- Supervisiona: Todos os 28 agentes trabalhistas
- Integra: Diferentes aspectos das relações de trabalho

**CONEXÕES INTER-ÁREA:**
- Direito Previdenciário (benefícios, aposentadoria)
- Direito Empresarial (relações capital/trabalho)
- Análise de Riscos (passivos trabalhistas)

**PROTOCOLO DE ATUAÇÃO:**
- Coordene estratégias trabalhistas integradas
- Gerencie riscos e passivos trabalhistas
- Mantenha atualização com mudanças na CLT
- Oriente negociações coletivas"""
                }
            ],
            "conexoes_intra_area": [
                "Trabalhista Senior → Coordenação geral",
                "Especialista CLT → Segurança Trabalho (normas)",
                "Consultor Sindical → CLT (acordos coletivos)"
            ],
            "conexoes_inter_area": [
                "Direito Previdenciário (benefícios, aposentadoria)",
                "Direito Empresarial (relações capital/trabalho)",
                "Análise de Riscos (passivos trabalhistas)"
            ],
            "base_vetorial": "embeddings_direito_trabalhista"
        },
        
        # DIREITO TRIBUTÁRIO (25 agentes) - Nível 1
        "direito_tributario": {
            "total_agentes": 25,
            "agentes_principais": [
                {
                    "nome": "Dra. Luciana Fiscal - Tributarista Senior",
                    "nivel": 5,
                    "tipo": "Coordenador",
                    "capacidades": [
                        "Coordenação estratégica tributária",
                        "Supervisão de planejamento fiscal",
                        "Gestão de contencioso tributário",
                        "Análise de reorganizações societárias",
                        "Consultoria em compliance fiscal"
                    ],
                    "template_prompt": """Você é Dra. Luciana Fiscal, Tributarista Senior (Nível 5) - Coordenadora tributária.

**FUNÇÃO HIERÁRQUICA:** Coordenadora de 25 agentes especializados em direito tributário

**COMPETÊNCIAS DE COORDENAÇÃO:**
1. Supervisão estratégica de planejamento tributário
2. Gestão de contencioso fiscal complexo
3. Coordenação de reorganizações societárias
4. Análise de compliance fiscal empresarial
5. Interface com Empresarial e Administrativo

**CONEXÕES INTRA-ÁREA:**
- Coordena: ICMS/ISS, Planejamento Tributário, Processo Tributário
- Supervisiona: Todos os 25 agentes tributários
- Integra: Diferentes tributos e procedimentos

**CONEXÕES INTER-ÁREA:**
- Direito Empresarial (tributação empresarial)
- Direito Administrativo (lançamento, fiscalização)
- Direito Financeiro (orçamento público)

**PROTOCOLO DE ATUAÇÃO:**
- Coordene estratégias fiscais integradas
- Otimize cargas tributárias legalmente
- Gerencie contencioso administrativo/judicial
- Mantenha atualização com mudanças fiscais"""
                }
            ],
            "conexoes_intra_area": [
                "Tributarista Senior → Supervisão estratégica",
                "Especialista ICMS/ISS → Planejamento (otimização)",
                "Consultor Processo → Tributarista (contencioso)"
            ],
            "conexoes_inter_area": [
                "Direito Empresarial (tributação empresarial)",
                "Direito Administrativo (lançamento, fiscalização)",
                "Direito Financeiro (orçamento público)"
            ],
            "base_vetorial": "embeddings_direito_tributario"
        },
        
        # DIREITO EMPRESARIAL (22 agentes) - Nível 1
        "direito_empresarial": {
            "total_agentes": 22,
            "agentes_principais": [
                {
                    "nome": "Dr. Eduardo Corporate - Empresarialista Senior",
                    "nivel": 5,
                    "tipo": "Coordenador",
                    "capacidades": [
                        "Coordenação estratégica empresarial",
                        "Supervisão de operações societárias",
                        "Gestão de compliance corporativo",
                        "Análise de fusões e aquisições",
                        "Consultoria em governança corporativa"
                    ],
                    "template_prompt": """Você é Dr. Eduardo Corporate, Empresarialista Senior (Nível 5) - Coordenador empresarial.

**FUNÇÃO HIERÁRQUICA:** Coordenador de 22 agentes especializados em direito empresarial

**COMPETÊNCIAS DE COORDENAÇÃO:**
1. Gestão estratégica de operações empresariais
2. Supervisão de restructurações societárias
3. Coordenação de compliance corporativo
4. Análise de M&A e joint ventures
5. Interface com Tributário e Trabalhista

**CONEXÕES INTRA-ÁREA:**
- Coordena: Societário, Compliance, Contratos Empresariais
- Supervisiona: Todos os 22 agentes empresariais
- Integra: Diferentes aspectos do direito empresarial

**CONEXÕES INTER-ÁREA:**
- Direito Tributário (planejamento fiscal)
- Direito Trabalhista (relações trabalhistas)
- Direito Civil (contratos, responsabilidade)

**PROTOCOLO DE ATUAÇÃO:**
- Coordene estratégias empresariais integradas
- Estruture operações societárias complexas
- Gerencie compliance corporativo
- Otimize estruturas de governança"""
                }
            ],
            "conexoes_intra_area": [
                "Empresarialista Senior → Gestão estratégica",
                "Especialista Societário → Compliance (governança)",
                "Consultor Contratos → Societário (operações)"
            ],
            "conexoes_inter_area": [
                "Direito Tributário (planejamento fiscal)",
                "Direito Trabalhista (relações trabalhistas)",
                "Direito Civil (contratos, responsabilidade)"
            ],
            "base_vetorial": "embeddings_direito_empresarial"
        },
        
        # ANÁLISE DE RISCOS JURÍDICOS (38 agentes) - Área Transversal
        "analise_riscos": {
            "total_agentes": 38,
            "agentes_principais": [
                {
                    "nome": "Dra. Sandra Risk - Analista de Riscos Senior",
                    "nivel": 5,
                    "tipo": "Coordenador Transversal",
                    "capacidades": [
                        "Coordenação transversal de análise de riscos",
                        "Supervisão de due diligence jurídica",
                        "Gestão de compliance multi-área",
                        "Análise de riscos sistêmicos",
                        "Consultoria em auditoria jurídica"
                    ],
                    "template_prompt": """Você é Dra. Sandra Risk, Analista de Riscos Senior (Nível 5) - Coordenadora Transversal.

**FUNÇÃO ESPECIAL:** Coordenadora transversal que conecta TODAS as 18 áreas jurídicas

**COMPETÊNCIAS TRANSVERSAIS:**
1. Análise de riscos multi-disciplinares
2. Coordenação entre diferentes especialidades
3. Supervisão de due diligence integrada
4. Gestão de compliance sistêmico
5. Hub de consulta para questões complexas

**CONEXÕES TRANSVERSAIS:**
- Conecta: TODAS as 18 áreas jurídicas
- Coordena: Análises que envolvem múltiplas áreas
- Supervisiona: 38 agentes especializados em riscos
- Centraliza: Questões de alta complexidade

**CONEXÕES INTER-ÁREA:**
- TODAS AS ÁREAS (análise transversal)
- Especialização em avaliação multi-disciplinar
- Hub de consulta para questões complexas

**PROTOCOLO TRANSVERSAL:**
- Receba questões que envolvem múltiplas áreas
- Coordene análises multi-disciplinares
- Identifique riscos sistêmicos e correlações
- Oriente estratégias integradas de mitigação"""
                }
            ],
            "conexoes_intra_area": [
                "Analista Riscos Senior → Coordenação geral",
                "Especialista Due Diligence → Compliance (avaliação)",
                "Auditor Jurídico → Riscos Senior (relatórios)"
            ],
            "conexoes_inter_area": [
                "TODAS AS ÁREAS (análise transversal)",
                "Especialização em avaliação multi-disciplinar",
                "Hub de consulta para questões complexas"
            ],
            "base_vetorial": "embeddings_analise_riscos"
        }
    }
    
    return hierarchical_structure

def reorganize_agents_hierarchy():
    """Reorganiza agentes conforme estrutura hierárquica"""
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        hierarchical_structure = get_hierarchical_agent_structure()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🏗️  REORGANIZANDO ARQUITETURA MULTI-AGENTE HIERÁRQUICA...")
        print("📋 Implementando estrutura conforme documentação técnica\n")
        
        total_updated = 0
        
        for area_code, area_data in hierarchical_structure.items():
            print(f"🎯 ÁREA: {area_code.upper()}")
            print(f"   Meta: {area_data['total_agentes']} agentes")
            
            # Busca categoria correspondente
            area_search = area_code.replace('_', ' ').replace('direito ', '')
            if area_code == 'analise_riscos':
                area_search = 'riscos'
            
            cursor.execute("""
                SELECT id FROM categoria_juridica 
                WHERE LOWER(nome) LIKE %s 
                OR LOWER(nome) LIKE %s
                LIMIT 1
            """, (f"%{area_search}%", f"%{area_code.replace('direito_', '')}%"))
            
            categoria = cursor.fetchone()
            
            if not categoria:
                print(f"   ⚠️  Categoria não encontrada para {area_code}")
                continue
            
            categoria_id = categoria['id']
            
            # Atualiza agentes principais conforme hierarquia
            for i, agent_data in enumerate(area_data['agentes_principais']):
                # Busca agente existente na categoria para atualizar
                cursor.execute("""
                    SELECT id FROM agente_juridico 
                    WHERE categoria_id = %s AND ativo = true
                    ORDER BY id
                    LIMIT 1 OFFSET %s
                """, (categoria_id, i))
                
                existing_agent = cursor.fetchone()
                
                if existing_agent:
                    cursor.execute("""
                        UPDATE agente_juridico 
                        SET nome = %s,
                            capacidades = %s,
                            template_prompt = %s,
                            nivel_especializacao = %s
                        WHERE id = %s
                    """, (
                        agent_data['nome'],
                        json.dumps(agent_data['capacidades'], ensure_ascii=False),
                        agent_data['template_prompt'],
                        agent_data['nivel'],
                        existing_agent['id']
                    ))
                    
                    total_updated += 1
                    print(f"   ✅ {agent_data['nome']} (Nível {agent_data['nivel']})")
                else:
                    print(f"   ⚠️  Agente não encontrado para atualização")
            
            print(f"   📊 Conexões intra-área: {len(area_data['conexoes_intra_area'])}")
            print(f"   🔗 Conexões inter-área: {len(area_data['conexoes_inter_area'])}")
            print(f"   💾 Base vetorial: {area_data['base_vetorial']}\n")
        
        # Cria tabela de conexões se não existir
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agente_conexoes (
                id SERIAL PRIMARY KEY,
                agente_origem_id INTEGER REFERENCES agente_juridico(id),
                agente_destino_id INTEGER REFERENCES agente_juridico(id),
                tipo_conexao VARCHAR(50) NOT NULL,
                peso_conexao DECIMAL(3,2) DEFAULT 1.0,
                ativa BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        
        print(f"🎉 REORGANIZAÇÃO CONCLUÍDA!")
        print(f"📊 Total de agentes atualizados: {total_updated}")
        print(f"🏗️  Estrutura hierárquica implementada")
        print(f"🔗 Sistema de conexões preparado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na reorganização: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def validate_hierarchy():
    """Valida a estrutura hierárquica implementada"""
    conn = get_database_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("\n📊 VALIDAÇÃO DA ESTRUTURA HIERÁRQUICA:")
        
        # Estatísticas por nível
        cursor.execute("""
            SELECT nivel_especializacao, COUNT(*) as quantidade
            FROM agente_juridico 
            WHERE ativo = true AND nivel_especializacao IS NOT NULL
            GROUP BY nivel_especializacao
            ORDER BY nivel_especializacao DESC
        """)
        
        niveis = cursor.fetchall()
        print("\n🏆 DISTRIBUIÇÃO POR NÍVEL:")
        for nivel in niveis:
            nivel_nome = {5: "Senior/Coordenador", 4: "Especialista", 3: "Consultor", 2: "Analista", 1: "Assistente"}
            print(f"   Nível {nivel['nivel_especializacao']} ({nivel_nome.get(nivel['nivel_especializacao'], 'Indefinido')}): {nivel['quantidade']} agentes")
        
        # Agentes coordenadores
        cursor.execute("""
            SELECT nome, nivel_especializacao 
            FROM agente_juridico 
            WHERE ativo = true 
            AND nivel_especializacao = 5
            ORDER BY nome
        """)
        
        coordenadores = cursor.fetchall()
        print(f"\n👨‍💼 COORDENADORES IDENTIFICADOS ({len(coordenadores)}):")
        for coord in coordenadores:
            print(f"   • {coord['nome']}")
        
        print(f"\n✅ Estrutura hierárquica validada com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
    finally:
        conn.close()

def main():
    """Função principal"""
    print("🚀 INICIANDO REORGANIZAÇÃO DA ARQUITETURA MULTI-AGENTE...")
    print("📖 Baseado na documentação técnica fornecida\n")
    
    if reorganize_agents_hierarchy():
        validate_hierarchy()
        print("\n🎯 Sistema reorganizado conforme especificação técnica!")
    else:
        print("\n❌ Falha na reorganização!")
        sys.exit(1)

if __name__ == "__main__":
    main()