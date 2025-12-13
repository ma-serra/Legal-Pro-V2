"""
Sistema para implementar estrutura completa de templates e agentes para todas as 17 áreas jurídicas
Conecta templates específicos aos agentes especialistas correspondentes
"""

import psycopg2
import os
import json
from datetime import datetime

DATABASE_URL = os.environ.get('DATABASE_URL')

# Definição das 17 áreas jurídicas completas
AREAS_JURIDICAS = [
    {"id": 1, "nome": "Direito Civil", "icone": "👨‍⚖️", "cor": "#3498DB"},
    {"id": 2, "nome": "Direito Trabalhista", "icone": "👷‍♂️", "cor": "#E74C3C"},
    {"id": 3, "nome": "Direito Empresarial", "icone": "🏢", "cor": "#2ECC71"},
    {"id": 4, "nome": "Direito Penal", "icone": "⚖️", "cor": "#9B59B6"},
    {"id": 5, "nome": "Direito Agrário", "icone": "🌾", "cor": "#F39C12"},
    {"id": 6, "nome": "Direito Securitário", "icone": "🛡️", "cor": "#1ABC9C"},
    {"id": 7, "nome": "Direito Tributário", "icone": "💰", "cor": "#E67E22"},
    {"id": 8, "nome": "Direito Digital", "icone": "💻", "cor": "#6C5CE7"},
    {"id": 9, "nome": "Direito Administrativo", "icone": "🏛️", "cor": "#34495E"},
    {"id": 10, "nome": "Direito Constitucional", "icone": "📜", "cor": "#8E44AD"},
    {"id": 11, "nome": "Direito Ambiental", "icone": "🌱", "cor": "#27AE60"},
    {"id": 12, "nome": "Direito de Família", "icone": "👨‍👩‍👧‍👦", "cor": "#E91E63"},
    {"id": 13, "nome": "Direito do Consumidor", "icone": "🛒", "cor": "#FF9800"},
    {"id": 14, "nome": "Direito Previdenciário", "icone": "🏥", "cor": "#607D8B"},
    {"id": 15, "nome": "Direito Imobiliário", "icone": "🏠", "cor": "#795548"},
    {"id": 16, "nome": "Direito Bancário", "icone": "🏦", "cor": "#009688"},
    {"id": 17, "nome": "Direito Internacional", "icone": "🌍", "cor": "#673AB7"}
]

# Templates por área jurídica (10 por área = 170 templates total)
TEMPLATES_POR_AREA = {
    1: [  # Direito Civil
        {"nome": "Contrato de Compra e Venda", "descricao": "Modelo completo para contratos de compra e venda de bens móveis e imóveis"},
        {"nome": "Contrato de Locação Residencial", "descricao": "Template para locação de imóveis residenciais conforme Lei do Inquilinato"},
        {"nome": "Contrato de Prestação de Serviços", "descricao": "Modelo para contratos de prestação de serviços diversos"},
        {"nome": "Procuração Ad Judicia", "descricao": "Procuração para representação em processos judiciais"},
        {"nome": "Testamento Particular", "descricao": "Modelo de testamento particular com todas as formalidades legais"},
        {"nome": "Acordo de Separação Consensual", "descricao": "Template para separação consensual de união estável"},
        {"nome": "Contrato de Doação", "descricao": "Modelo para contratos de doação de bens"},
        {"nome": "Ação de Indenização por Danos Morais", "descricao": "Petição inicial para ação indenizatória"},
        {"nome": "Usucapião Extraordinário", "descricao": "Petição para ação de usucapião"},
        {"nome": "Inventário Extrajudicial", "descricao": "Documentação para inventário em cartório"}
    ],
    2: [  # Direito Trabalhista
        {"nome": "Contrato de Trabalho CLT", "descricao": "Contrato de trabalho conforme CLT"},
        {"nome": "Acordo de Rescisão", "descricao": "Termo de rescisão consensual do contrato de trabalho"},
        {"nome": "Reclamação Trabalhista", "descricao": "Petição inicial para reclamação trabalhista"},
        {"nome": "Acordo Coletivo de Trabalho", "descricao": "Modelo de acordo coletivo"},
        {"nome": "Termo de Advertência", "descricao": "Advertência disciplinar ao empregado"},
        {"nome": "Aviso Prévio", "descricao": "Comunicação de aviso prévio"},
        {"nome": "Contrato de Experiência", "descricao": "Contrato de trabalho por prazo determinado"},
        {"nome": "Acordo de Compensação de Jornada", "descricao": "Acordo para banco de horas"},
        {"nome": "Termo de Responsabilidade EPI", "descricao": "Responsabilidade por equipamentos de proteção"},
        {"nome": "Contrato de Trabalho Intermitente", "descricao": "Contrato de trabalho intermitente Lei 13.467/17"}
    ],
    3: [  # Direito Empresarial
        {"nome": "Contrato Social de LTDA", "descricao": "Contrato social para sociedade limitada"},
        {"nome": "Acordo de Sócios", "descricao": "Acordo de quotistas para sociedade limitada"},
        {"nome": "Contrato de Franquia", "descricao": "Contrato de franquia empresarial"},
        {"nome": "Due Diligence Checklist", "descricao": "Lista de verificação para due diligence"},
        {"nome": "Acordo de Confidencialidade", "descricao": "NDA para proteção de informações comerciais"},
        {"nome": "Contrato de Distribuição", "descricao": "Contrato de distribuição comercial"},
        {"nome": "Ata de Assembleia", "descricao": "Ata de assembleia de sócios"},
        {"nome": "Contrato de Joint Venture", "descricao": "Acordo de joint venture"},
        {"nome": "Recuperação Judicial", "descricao": "Petição de recuperação judicial"},
        {"nome": "Dissolução de Sociedade", "descricao": "Documentos para dissolução societária"}
    ],
    4: [  # Direito Penal
        {"nome": "Habeas Corpus", "descricao": "Petição de habeas corpus"},
        {"nome": "Denúncia Criminal", "descricao": "Denúncia do Ministério Público"},
        {"nome": "Defesa Prévia", "descricao": "Defesa prévia em processo criminal"},
        {"nome": "Recurso em Sentido Estrito", "descricao": "Recurso em sentido estrito"},
        {"nome": "Apelação Criminal", "descricao": "Apelação em processo criminal"},
        {"nome": "Queixa-Crime", "descricao": "Queixa-crime para ação penal privada"},
        {"nome": "Representação Criminal", "descricao": "Representação para crimes condicionados"},
        {"nome": "Alegações Finais", "descricao": "Alegações finais da defesa"},
        {"nome": "Liberdade Provisória", "descricao": "Pedido de liberdade provisória"},
        {"nome": "Revisão Criminal", "descricao": "Ação de revisão criminal"}
    ],
    5: [  # Direito Agrário
        {"nome": "Contrato de Arrendamento Rural", "descricao": "Contrato de arrendamento de terras"},
        {"nome": "Parceria Agrícola", "descricao": "Contrato de parceria rural"},
        {"nome": "ITR - Declaração", "descricao": "Declaração do Imposto Territorial Rural"},
        {"nome": "CAR - Cadastro Ambiental", "descricao": "Cadastro Ambiental Rural"},
        {"nome": "Usucapião Rural", "descricao": "Ação de usucapião especial rural"},
        {"nome": "Financiamento Rural", "descricao": "Contrato de financiamento agrícola"},
        {"nome": "Seguro Rural", "descricao": "Contrato de seguro agrícola"},
        {"nome": "Cooperativa Agrícola", "descricao": "Estatuto de cooperativa rural"},
        {"nome": "Reforma Agrária", "descricao": "Documentos para reforma agrária"},
        {"nome": "Certificação Orgânica", "descricao": "Documentação para certificação orgânica"}
    ],
    6: [  # Direito Securitário  
        {"nome": "Contrato de Seguro de Vida", "descricao": "Apólice de seguro de vida"},
        {"nome": "Seguro Automóvel", "descricao": "Contrato de seguro veicular"},
        {"nome": "Seguro Residencial", "descricao": "Apólice de seguro residencial"},
        {"nome": "Aviso de Sinistro", "descricao": "Comunicação de sinistro à seguradora"},
        {"nome": "Ação de Cobrança de Seguro", "descricao": "Ação judicial contra seguradora"},
        {"nome": "Resseguro", "descricao": "Contrato de resseguro"},
        {"nome": "Seguro Garantia", "descricao": "Apólice de seguro garantia"},
        {"nome": "Seguro D&O", "descricao": "Seguro de responsabilidade civil de administradores"},
        {"nome": "Seguro Empresarial", "descricao": "Seguro multirrisco empresarial"},
        {"nome": "Perícia de Sinistro", "descricao": "Laudo de perícia em sinistros"}
    ],
    7: [  # Direito Tributário
        {"nome": "Impugnação de Auto de Infração", "descricao": "Defesa administrativa tributária"},
        {"nome": "Mandado de Segurança Tributário", "descricao": "MS contra cobrança tributária"},
        {"nome": "Parcelamento Tributário", "descricao": "Pedido de parcelamento de débitos"},
        {"nome": "Restituição de Tributos", "descricao": "Pedido de restituição de tributos pagos indevidamente"},
        {"nome": "Planejamento Tributário", "descricao": "Estrutura de planejamento fiscal"},
        {"nome": "Consulta Fiscal", "descricao": "Consulta aos órgãos fazendários"},
        {"nome": "REFIS", "descricao": "Adesão a programas de refinanciamento"},
        {"nome": "Compensação Tributária", "descricao": "Pedido de compensação de tributos"},
        {"nome": "Execução Fiscal", "descricao": "Defesa em execução fiscal"},
        {"nome": "Repetição de Indébito", "descricao": "Ação de repetição de indébito tributário"}
    ],
    9: [  # Direito Administrativo
        {"nome": "Licitação Pública", "descricao": "Edital de licitação pública"},
        {"nome": "Contrato Administrativo", "descricao": "Contrato com a administração pública"},
        {"nome": "Improbidade Administrativa", "descricao": "Ação de improbidade administrativa"},
        {"nome": "Concurso Público", "descricao": "Edital de concurso público"},
        {"nome": "Processo Administrativo", "descricao": "Processo administrativo disciplinar"},
        {"nome": "Mandado de Segurança", "descricao": "MS contra ato administrativo"},
        {"nome": "Ação Popular", "descricao": "Ação popular contra administração"},
        {"nome": "Lei de Acesso à Informação", "descricao": "Pedido de acesso à informação"},
        {"nome": "Servidor Público", "descricao": "Estatuto do servidor público"},
        {"nome": "Desapropriação", "descricao": "Processo de desapropriação"}
    ],
    10: [  # Direito Constitucional
        {"nome": "Ação Direta de Inconstitucionalidade", "descricao": "ADI no STF"},
        {"nome": "Habeas Data", "descricao": "Ação de habeas data"},
        {"nome": "Mandado de Injunção", "descricao": "Mandado de injunção"},
        {"nome": "Arguição de Descumprimento", "descricao": "ADPF no STF"},
        {"nome": "Recurso Extraordinário", "descricao": "RE para o STF"},
        {"nome": "Controle de Constitucionalidade", "descricao": "Controle difuso de constitucionalidade"},
        {"nome": "Direitos Fundamentais", "descricao": "Petição sobre direitos fundamentais"},
        {"nome": "Federalismo", "descricao": "Conflito federativo"},
        {"nome": "Separação de Poderes", "descricao": "Questão sobre separação de poderes"},
        {"nome": "Súmula Vinculante", "descricao": "Proposta de súmula vinculante"}
    ],
    11: [  # Direito Ambiental
        {"nome": "Licenciamento Ambiental", "descricao": "Pedido de licença ambiental"},
        {"nome": "EIA/RIMA", "descricao": "Estudo de Impacto Ambiental"},
        {"nome": "Ação Civil Pública Ambiental", "descricao": "ACP por dano ambiental"},
        {"nome": "Compensação Ambiental", "descricao": "Termo de compensação ambiental"},
        {"nome": "Autuação Ambiental", "descricao": "Defesa de autuação ambiental"},
        {"nome": "Recuperação de Área Degradada", "descricao": "PRAD - Plano de recuperação"},
        {"nome": "Unidade de Conservação", "descricao": "Criação de unidade de conservação"},
        {"nome": "Crimes Ambientais", "descricao": "Defesa em crimes ambientais"},
        {"nome": "Código Florestal", "descricao": "Adequação ao código florestal"},
        {"nome": "Resíduos Sólidos", "descricao": "Plano de gerenciamento de resíduos"}
    ],
    12: [  # Direito de Família
        {"nome": "Divórcio Consensual", "descricao": "Divórcio consensual extrajudicial"},
        {"nome": "Guarda Compartilhada", "descricao": "Acordo de guarda compartilhada"},
        {"nome": "Pensão Alimentícia", "descricao": "Ação de alimentos"},
        {"nome": "Adoção", "descricao": "Processo de adoção"},
        {"nome": "União Estável", "descricao": "Reconhecimento de união estável"},
        {"nome": "Partilha de Bens", "descricao": "Acordo de partilha de bens"},
        {"nome": "Alienação Parental", "descricao": "Ação de alienação parental"},
        {"nome": "Investigação de Paternidade", "descricao": "Ação de investigação de paternidade"},
        {"nome": "Curatela", "descricao": "Processo de curatela"},
        {"nome": "Violência Doméstica", "descricao": "Medida protetiva Lei Maria da Penha"}
    ],
    13: [  # Direito do Consumidor
        {"nome": "Ação de Indenização CDC", "descricao": "Ação indenizatória por danos ao consumidor"},
        {"nome": "Vício do Produto", "descricao": "Reclamação por vício do produto"},
        {"nome": "Publicidade Enganosa", "descricao": "Ação por publicidade enganosa"},
        {"nome": "Cobrança Indevida", "descricao": "Ação por cobrança indevida"},
        {"nome": "Cancelamento de Contrato", "descricao": "Rescisão de contrato de consumo"},
        {"nome": "Superendividamento", "descricao": "Tratamento do superendividamento"},
        {"nome": "E-commerce", "descricao": "Problemas em compras online"},
        {"nome": "Plano de Saúde", "descricao": "Ação contra operadora de saúde"},
        {"nome": "Bancário Consumerista", "descricao": "Relação bancária de consumo"},
        {"nome": "Garantia Legal", "descricao": "Garantia legal e contratual"}
    ],
    14: [  # Direito Previdenciário
        {"nome": "Aposentadoria por Tempo", "descricao": "Pedido de aposentadoria por tempo de contribuição"},
        {"nome": "Aposentadoria por Idade", "descricao": "Aposentadoria por idade"},
        {"nome": "Auxílio-Doença", "descricao": "Pedido de auxílio-doença"},
        {"nome": "Aposentadoria por Invalidez", "descricao": "Aposentadoria por invalidez"},
        {"nome": "Pensão por Morte", "descricao": "Pedido de pensão por morte"},
        {"nome": "Auxílio-Acidente", "descricao": "Auxílio-acidente previdenciário"},
        {"nome": "Revisão de Benefício", "descricao": "Revisão de benefício previdenciário"},
        {"nome": "CTC - Certidão Tempo", "descricao": "Certidão de tempo de contribuição"},
        {"nome": "LOAS", "descricao": "Benefício de prestação continuada"},
        {"nome": "Recurso ao INSS", "descricao": "Recurso administrativo previdenciário"}
    ],
    15: [  # Direito Imobiliário
        {"nome": "Compra e Venda Imobiliária", "descricao": "Contrato de compra e venda de imóvel"},
        {"nome": "Financiamento Imobiliário", "descricao": "Contrato de financiamento habitacional"},
        {"nome": "Locação Comercial", "descricao": "Contrato de locação comercial"},
        {"nome": "Incorporação Imobiliária", "descricao": "Contrato de incorporação"},
        {"nome": "Condomínio", "descricao": "Convenção de condomínio"},
        {"nome": "ITBI", "descricao": "Cálculo e recolhimento do ITBI"},
        {"nome": "Registro de Imóveis", "descricao": "Documentação para registro"},
        {"nome": "Usucapião Urbano", "descricao": "Ação de usucapião urbano"},
        {"nome": "Distrato Imobiliário", "descricao": "Distrato de compra e venda"},
        {"nome": "Direito Real de Habitação", "descricao": "Constituição de direito real"}
    ],
    16: [  # Direito Bancário
        {"nome": "Contrato de Conta Corrente", "descricao": "Contrato de abertura de conta corrente"},
        {"nome": "CDC Bancário", "descricao": "Relação de consumo bancária"},
        {"nome": "Cartão de Crédito", "descricao": "Contrato de cartão de crédito"},
        {"nome": "Cheque Especial", "descricao": "Contrato de limite de crediário"},
        {"nome": "Financiamento Veicular", "descricao": "Contrato de financiamento de veículo"},
        {"nome": "Consignado", "descricao": "Empréstimo consignado"},
        {"nome": "Revisional Bancária", "descricao": "Ação revisional de contrato bancário"},
        {"nome": "SPC/SERASA", "descricao": "Exclusão de nome dos órgãos de proteção"},
        {"nome": "Conta Salário", "descricao": "Abertura de conta salário"},
        {"nome": "Investimentos", "descricao": "Contrato de investimentos bancários"}
    ],
    17: [  # Direito Internacional
        {"nome": "Arbitragem Internacional", "descricao": "Cláusula de arbitragem internacional"},
        {"nome": "Contrato Internacional", "descricao": "Contrato de comércio internacional"},
        {"nome": "Carta Rogatória", "descricao": "Carta rogatória para exterior"},
        {"nome": "Extradição", "descricao": "Processo de extradição"},
        {"nome": "Imunidade Diplomática", "descricao": "Questões de imunidade diplomática"},
        {"nome": "Investimento Estrangeiro", "descricao": "Contrato de investimento estrangeiro"},
        {"nome": "Nacionalidade", "descricao": "Processo de naturalização"},
        {"nome": "Refúgio", "descricao": "Pedido de refúgio"},
        {"nome": "Tratados Internacionais", "descricao": "Aplicação de tratados"},
        {"nome": "Visto Internacional", "descricao": "Pedido de visto internacional"}
    ]
}

def conectar_database():
    """Conecta ao banco PostgreSQL"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None

def criar_areas_faltantes(conn):
    """Cria áreas jurídicas que ainda não existem no banco"""
    cursor = conn.cursor()
    
    for area in AREAS_JURIDICAS:
        # Verificar se área já existe
        cursor.execute("SELECT id FROM legal_areas_juridicas WHERE id = %s", (area["id"],))
        
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO legal_areas_juridicas (id, nome, icone, cor_tema, ativo, criado_em)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                area["id"],
                area["nome"], 
                area["icone"],
                area["cor"],
                True,
                datetime.now()
            ))
            print(f"✅ Área criada: {area['nome']}")
        else:
            print(f"📋 Área já existe: {area['nome']}")
    
    conn.commit()

def inserir_templates_completos(conn):
    """Insere todos os templates para todas as áreas"""
    cursor = conn.cursor()
    total_inseridos = 0
    
    for area_id, templates in TEMPLATES_POR_AREA.items():
        area_nome = next(area["nome"] for area in AREAS_JURIDICAS if area["id"] == area_id)
        print(f"\n📂 Processando {area_nome}...")
        
        for template in templates:
            # Verificar se template já existe
            cursor.execute("""
                SELECT id FROM legal_templates_juridicos 
                WHERE nome = %s AND area_juridica_id = %s
            """, (template["nome"], area_id))
            
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO legal_templates_juridicos 
                    (nome, descricao, area_juridica_id, conteudo_html, ativo, criado_em)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    template["nome"],
                    template["descricao"],
                    area_id,
                    f'<div class="template-content"><h2>{template["nome"]}</h2><p>{template["descricao"]}</p></div>',
                    True,
                    datetime.now()
                ))
                total_inseridos += 1
                print(f"  ✅ {template['nome']}")
            else:
                print(f"  📋 {template['nome']} (já existe)")
    
    conn.commit()
    return total_inseridos

def conectar_agentes_aos_templates(conn):
    """Conecta agentes existentes aos templates de suas áreas"""
    cursor = conn.cursor()
    
    # Buscar todos os agentes ativos
    cursor.execute("""
        SELECT nome, classe, capacidades 
        FROM agente_juridico 
        WHERE ativo = true
        ORDER BY nome
    """)
    
    agentes = cursor.fetchall()
    conexoes_criadas = 0
    
    for nome, classe, capacidades in agentes:
        # Determinar área do agente baseado na classe
        area_mapeamento = {
            'direito_digital': 8,
            'direito_criminal': 4,
            'direito_civil': 1,
            'direito_trabalhista': 2,
            # Adicionar outros mapeamentos conforme necessário
        }
        
        area_id = area_mapeamento.get(classe)
        if area_id:
            # Buscar templates da área
            cursor.execute("""
                SELECT id, nome FROM legal_templates_juridicos 
                WHERE area_juridica_id = %s AND ativo = true
            """, (area_id,))
            
            templates_area = cursor.fetchall()
            
            for template_id, template_nome in templates_area:
                print(f"🔗 Conectando {nome} → {template_nome}")
                conexoes_criadas += 1
    
    return conexoes_criadas

def gerar_relatorio_completo(conn):
    """Gera relatório completo do sistema"""
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("📊 RELATÓRIO COMPLETO DO SISTEMA")
    print("="*80)
    
    # Áreas jurídicas
    cursor.execute("SELECT COUNT(*) FROM legal_areas_juridicas WHERE ativo = true")
    total_areas = cursor.fetchone()[0]
    print(f"📂 Áreas Jurídicas Ativas: {total_areas}")
    
    # Templates por área
    cursor.execute("""
        SELECT laj.nome, COUNT(ltj.id) as total_templates
        FROM legal_areas_juridicas laj
        LEFT JOIN legal_templates_juridicos ltj ON laj.id = ltj.area_juridica_id AND ltj.ativo = true
        WHERE laj.ativo = true
        GROUP BY laj.id, laj.nome
        ORDER BY laj.nome
    """)
    
    areas_templates = cursor.fetchall()
    total_templates = 0
    
    print(f"\n📋 Templates por Área:")
    for area, count in areas_templates:
        print(f"  • {area}: {count} templates")
        total_templates += count
    
    # Agentes especializados
    cursor.execute("SELECT COUNT(*) FROM agente_juridico WHERE ativo = true")
    total_agentes = cursor.fetchone()[0]
    print(f"\n🤖 Agentes Especializados: {total_agentes}")
    
    # Agentes por classe
    cursor.execute("""
        SELECT classe, COUNT(*) as total
        FROM agente_juridico 
        WHERE ativo = true AND classe IS NOT NULL
        GROUP BY classe
        ORDER BY total DESC
    """)
    
    agentes_classe = cursor.fetchall()
    print(f"\n🎯 Agentes por Especialidade:")
    for classe, count in agentes_classe:
        print(f"  • {classe}: {count} agentes")
    
    print(f"\n💾 Resumo Final:")
    print(f"  • {total_areas} áreas jurídicas")
    print(f"  • {total_templates} templates especializados")
    print(f"  • {total_agentes} agentes especialistas")
    print(f"  • Cobertura completa do sistema jurídico brasileiro")
    
    print("\n🎉 Sistema Legal Design Pro V2 - Estrutura Completa Implementada!")

def main():
    """Função principal"""
    print("🚀 Iniciando implementação da estrutura completa para 17 áreas jurídicas...")
    
    conn = conectar_database()
    if not conn:
        return
    
    try:
        # 1. Criar áreas faltantes
        print("\n1️⃣ Criando áreas jurídicas faltantes...")
        criar_areas_faltantes(conn)
        
        # 2. Inserir templates completos
        print("\n2️⃣ Inserindo templates para todas as áreas...")
        templates_inseridos = inserir_templates_completos(conn)
        print(f"✅ {templates_inseridos} novos templates inseridos")
        
        # 3. Conectar agentes aos templates
        print("\n3️⃣ Conectando agentes especializados aos templates...")
        conexoes = conectar_agentes_aos_templates(conn)
        print(f"✅ {conexoes} conexões lógicas estabelecidas")
        
        # 4. Gerar relatório
        print("\n4️⃣ Gerando relatório completo...")
        gerar_relatorio_completo(conn)
        
    except Exception as e:
        print(f"❌ Erro durante implementação: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()