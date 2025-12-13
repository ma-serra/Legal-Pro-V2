#!/usr/bin/env python3
"""
Script para adicionar os 18 assistentes jurídicos principais ao sistema multi-agente
Cada assistente coordena uma área jurídica específica e gerencia os agentes especializados
"""

import os
import psycopg2
from datetime import datetime
import json

def conectar_database():
    """Conecta ao banco PostgreSQL"""
    try:
        connection = psycopg2.connect(os.environ.get('DATABASE_URL'))
        return connection
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

def criar_18_assistentes_principais():
    """Cria os 18 assistentes jurídicos principais"""
    
    assistentes = [
        {
            'nome': 'Assistente de Direito Penal',
            'area_juridica': 'Direito Penal',
            'classe': 'AssistentePrincipal',
            'descricao': 'Assistente principal especializado em Direito Penal, coordena análises criminais, defesas e acusações',
            'nivel_especializacao': 5,
            'capacidades': ['análise_criminal', 'defesa_penal', 'recursos_criminais', 'júri_popular'],
            'icone': 'fas fa-gavel',
            'cor_destaque': '#dc3545'
        },
        {
            'nome': 'Assistente de Direito Civil',
            'area_juridica': 'Direito Civil',
            'classe': 'AssistentePrincipal',
            'descricao': 'Assistente principal para questões civis, contratos, responsabilidade civil e direitos reais',
            'nivel_especializacao': 5,
            'capacidades': ['contratos_civis', 'responsabilidade_civil', 'direitos_reais', 'obrigações'],
            'icone': 'fas fa-handshake',
            'cor_destaque': '#007bff'
        },
        {
            'nome': 'Assistente de Direito Empresarial',
            'area_juridica': 'Direito Empresarial',
            'classe': 'AssistentePrincipal',
            'descricao': 'Especialista em direito societário, contratos empresariais e governança corporativa',
            'nivel_especializacao': 5,
            'capacidades': ['direito_societário', 'contratos_empresariais', 'fusões_aquisições', 'compliance'],
            'icone': 'fas fa-building',
            'cor_destaque': '#28a745'
        },
        {
            'nome': 'Assistente de Direito Tributário',
            'area_juridica': 'Direito Tributário',
            'classe': 'AssistentePrincipal',
            'descricao': 'Especialista em tributos, planejamento tributário e contencioso fiscal',
            'nivel_especializacao': 5,
            'capacidades': ['planejamento_tributário', 'contencioso_fiscal', 'impostos_federais', 'elisão_fiscal'],
            'icone': 'fas fa-calculator',
            'cor_destaque': '#ffc107'
        },
        {
            'nome': 'Assistente de Direito Trabalhista',
            'area_juridica': 'Direito Trabalhista',
            'classe': 'AssistentePrincipal',
            'descricao': 'Especialista em relações trabalhistas, CLT e direitos dos trabalhadores',
            'nivel_especializacao': 5,
            'capacidades': ['clt_avançada', 'relações_trabalhistas', 'rescisão_contratual', 'direitos_trabalhistas'],
            'icone': 'fas fa-users',
            'cor_destaque': '#fd7e14'
        },
        {
            'nome': 'Assistente de Direito Constitucional',
            'area_juridica': 'Direito Constitucional',
            'classe': 'AssistentePrincipal',
            'descricao': 'Especialista em direito constitucional, direitos fundamentais e controle de constitucionalidade',
            'nivel_especializacao': 5,
            'capacidades': ['direitos_fundamentais', 'controle_constitucionalidade', 'organização_poderes', 'federalismo'],
            'icone': 'fas fa-balance-scale',
            'cor_destaque': '#6610f2'
        },
        {
            'nome': 'Assistente de Direito Administrativo',
            'area_juridica': 'Direito Administrativo',
            'classe': 'AssistentePrincipal',
            'descricao': 'Especialista em direito público, licitações, contratos administrativos e servidores públicos',
            'nivel_especializacao': 5,
            'capacidades': ['licitações_contratos', 'servidores_públicos', 'improbidade_administrativa', 'concessões'],
            'icone': 'fas fa-university',
            'cor_destaque': '#6f42c1'
        },
        {
            'nome': 'Assistente de Direito de Família',
            'area_juridica': 'Direito de Família',
            'classe': 'AssistentePrincipal',
            'descricao': 'Especialista em relações familiares, divórcio, guarda, alimentos e sucessões',
            'nivel_especializacao': 5,
            'capacidades': ['direito_familiar', 'divórcio_separação', 'guarda_filhos', 'pensão_alimentícia'],
            'icone': 'fas fa-home',
            'cor_destaque': '#e83e8c'
        },
        {
            'nome': 'Assistente de Direito do Consumidor',
            'area_juridica': 'Direito do Consumidor',
            'classe': 'AssistentePrincipal',
            'descricao': 'Especialista em CDC, relações de consumo e proteção dos direitos do consumidor',
            'nivel_especializacao': 5,
            'capacidades': ['cdc_completo', 'relações_consumo', 'práticas_abusivas', 'danos_morais'],
            'icone': 'fas fa-shopping-cart',
            'cor_destaque': '#17a2b8'
        },
        {
            'nome': 'Assistente de Direito Previdenciário',
            'area_juridica': 'Direito Previdenciário',
            'classe': 'AssistentePrincipal',
            'descricao': 'Especialista em previdência social, benefícios previdenciários e revisões',
            'nivel_especializacao': 5,
            'capacidades': ['benefícios_previdenciários', 'aposentadorias', 'auxílios', 'revisão_benefícios'],
            'icone': 'fas fa-id-card',
            'cor_destaque': '#6c757d'
        },
        {
            'nome': 'Assistente de Direito Ambiental',
            'area_juridica': 'Direito Ambiental',
            'classe': 'AssistentePrincipal',
            'descricao': 'Especialista em legislação ambiental, licenciamento e crimes ambientais',
            'nivel_especializacao': 5,
            'capacidades': ['licenciamento_ambiental', 'crimes_ambientais', 'recursos_hídricos', 'unidades_conservação'],
            'icone': 'fas fa-leaf',
            'cor_destaque': '#198754'
        },
        {
            'nome': 'Assistente de Direito Bancário',
            'area_juridica': 'Direito Bancário',
            'classe': 'AssistentePrincipal',
            'descricao': 'Especialista em operações bancárias, contratos bancários e sistema financeiro',
            'nivel_especializacao': 5,
            'capacidades': ['contratos_bancários', 'operações_financeiras', 'spc_serasa', 'recuperação_crédito'],
            'icone': 'fas fa-university',
            'cor_destaque': '#0d6efd'
        },
        {
            'nome': 'Assistente de Direito Imobiliário',
            'area_juridica': 'Direito Imobiliário',
            'classe': 'AssistentePrincipal',
            'descricao': 'Especialista em transações imobiliárias, financiamentos e direito urbanístico',
            'nivel_especializacao': 5,
            'capacidades': ['transações_imobiliárias', 'financiamento_habitacional', 'usucapião', 'incorporações'],
            'icone': 'fas fa-building',
            'cor_destaque': '#fd7e14'
        },
        {
            'nome': 'Assistente de Direito Digital',
            'area_juridica': 'Direito Digital',
            'classe': 'AssistentePrincipal',
            'descricao': 'Especialista em LGPD, crimes cibernéticos, contratos digitais e tecnologia jurídica',
            'nivel_especializacao': 5,
            'capacidades': ['lgpd_completa', 'crimes_cibernéticos', 'contratos_digitais', 'marco_civil_internet'],
            'icone': 'fas fa-laptop',
            'cor_destaque': '#20c997'
        },
        {
            'nome': 'Assistente de Direito Agrário',
            'area_juridica': 'Direito Agrário',
            'classe': 'AssistentePrincipal',
            'descricao': 'Especialista em reforma agrária, agricultura familiar e regularização fundiária',
            'nivel_especializacao': 5,
            'capacidades': ['reforma_agrária', 'agricultura_familiar', 'regularização_fundiária', 'conflitos_agrários'],
            'icone': 'fas fa-seedling',
            'cor_destaque': '#795548'
        },
        {
            'nome': 'Assistente de Direito Securitário',
            'area_juridica': 'Direito Securitário',
            'classe': 'AssistentePrincipal',
            'descricao': 'Especialista em seguros, resseguros e direito securitário completo',
            'nivel_especializacao': 5,
            'capacidades': ['contratos_seguro', 'sinistros', 'resseguros', 'seguros_especializados'],
            'icone': 'fas fa-shield-alt',
            'cor_destaque': '#9c27b0'
        },
        {
            'nome': 'Assistente de Propriedade Intelectual',
            'area_juridica': 'Propriedade Intelectual',
            'classe': 'AssistentePrincipal',
            'descricao': 'Especialista em marcas, patentes, direitos autorais e propriedade industrial',
            'nivel_especializacao': 5,
            'capacidades': ['marcas_patentes', 'direitos_autorais', 'software_propriedade', 'transferência_tecnologia'],
            'icone': 'fas fa-lightbulb',
            'cor_destaque': '#ff5722'
        },
        {
            'nome': 'Assistente de Análise de Riscos',
            'area_juridica': 'Análise de Riscos Jurídicos',
            'classe': 'AssistentePrincipal',
            'descricao': 'Especialista em análise de riscos jurídicos, compliance e due diligence',
            'nivel_especializacao': 5,
            'capacidades': ['análise_riscos', 'due_diligence', 'compliance_corporativo', 'gestão_riscos'],
            'icone': 'fas fa-chart-line',
            'cor_destaque': '#607d8b'
        }
    ]
    
    return assistentes

def inserir_assistentes_database(assistentes):
    """Insere os assistentes no banco de dados"""
    
    connection = conectar_database()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Verificar assistentes existentes
        cursor.execute("SELECT nome FROM agente_juridico WHERE classe = %s", ('AssistentePrincipal',))
        existentes = {row[0] for row in cursor.fetchall()}
        
        assistentes_inseridos = 0
        
        for assistente in assistentes:
            if assistente['nome'] in existentes:
                print(f"✓ {assistente['nome']} já existe")
                continue
            
            # Inserir assistente
            sql = """
            INSERT INTO agente_juridico (
                nome, classe, descricao, area_juridica, nivel_especializacao,
                ativo, data_criacao, data_atualizacao, modelo_ai, temperatura,
                top_p, max_tokens, icone, cor_destaque, capacidades,
                qdrant_collection, usar_busca_hibrida, embedding_model,
                usa_base_universal, prioridade_base_universal
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            )
            """
            
            valores = (
                assistente['nome'],
                assistente['classe'],
                assistente['descricao'],
                assistente['area_juridica'],
                assistente['nivel_especializacao'],
                True,  # ativo
                datetime.now(),
                datetime.now(),
                'gpt-4o-mini',  # modelo_ai
                0.7,  # temperatura
                0.9,  # top_p
                4000,  # max_tokens
                assistente['icone'],
                assistente['cor_destaque'],
                json.dumps(assistente['capacidades']),
                assistente['area_juridica'].lower().replace(' ', '_'),  # qdrant_collection
                True,  # usar_busca_hibrida
                'text-embedding-3-small',  # embedding_model
                True,  # usa_base_universal
                1  # prioridade_base_universal
            )
            
            cursor.execute(sql, valores)
            assistentes_inseridos += 1
            print(f"✅ {assistente['nome']} inserido com sucesso")
        
        connection.commit()
        print(f"\n🎉 {assistentes_inseridos} assistentes principais adicionados ao sistema!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inserir assistentes: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()

def atualizar_sistema_multi_agente():
    """Atualiza configurações do sistema multi-agente"""
    
    connection = conectar_database()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Criar tabela de comunicação multi-agente se não existir
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS comunicacao_multi_agente (
            id SERIAL PRIMARY KEY,
            origem_id INTEGER REFERENCES agente_juridico(id),
            destino_id INTEGER REFERENCES agente_juridico(id),
            tipo_comunicacao VARCHAR(50) NOT NULL,
            mensagem TEXT NOT NULL,
            status VARCHAR(20) DEFAULT 'pendente',
            prioridade VARCHAR(10) DEFAULT 'media',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processado_em TIMESTAMP,
            resposta TEXT,
            metadados JSONB
        )
        """)
        
        # Criar índices para performance
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_comunicacao_origem ON comunicacao_multi_agente(origem_id);
        CREATE INDEX IF NOT EXISTS idx_comunicacao_destino ON comunicacao_multi_agente(destino_id);
        CREATE INDEX IF NOT EXISTS idx_comunicacao_status ON comunicacao_multi_agente(status);
        CREATE INDEX IF NOT EXISTS idx_comunicacao_criado ON comunicacao_multi_agente(criado_em);
        """)
        
        # Criar tabela de hierarquia de agentes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS hierarquia_agentes (
            id SERIAL PRIMARY KEY,
            assistente_principal_id INTEGER REFERENCES agente_juridico(id),
            agente_especializado_id INTEGER REFERENCES agente_juridico(id),
            nivel_hierarquia INTEGER DEFAULT 1,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(assistente_principal_id, agente_especializado_id)
        )
        """)
        
        connection.commit()
        print("✅ Sistema multi-agente atualizado com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar sistema: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()

def estabelecer_hierarquias():
    """Estabelece hierarquias entre assistentes principais e agentes especializados"""
    
    connection = conectar_database()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Obter assistentes principais
        cursor.execute("""
        SELECT id, nome, area_juridica 
        FROM agente_juridico 
        WHERE classe = 'AssistentePrincipal'
        """)
        assistentes = cursor.fetchall()
        
        hierarquias_criadas = 0
        
        for assistente_id, assistente_nome, area_juridica in assistentes:
            # Encontrar agentes especializados da mesma área
            cursor.execute("""
            SELECT id FROM agente_juridico 
            WHERE area_juridica = %s AND classe != 'AssistentePrincipal' AND id != %s
            """, (area_juridica, assistente_id))
            
            agentes_especializados = cursor.fetchall()
            
            for agente_id, in agentes_especializados:
                # Inserir hierarquia se não existir
                cursor.execute("""
                INSERT INTO hierarquia_agentes (assistente_principal_id, agente_especializado_id, nivel_hierarquia)
                VALUES (%s, %s, 1)
                ON CONFLICT (assistente_principal_id, agente_especializado_id) DO NOTHING
                """, (assistente_id, agente_id))
                
                if cursor.rowcount > 0:
                    hierarquias_criadas += 1
        
        connection.commit()
        print(f"✅ {hierarquias_criadas} hierarquias estabelecidas entre assistentes e agentes especializados!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao estabelecer hierarquias: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()

def gerar_relatorio_final():
    """Gera relatório final dos 18 assistentes"""
    
    connection = conectar_database()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        # Contar assistentes principais por área
        cursor.execute("""
        SELECT area_juridica, COUNT(*) as total_assistentes,
               COUNT(CASE WHEN classe = 'AssistentePrincipal' THEN 1 END) as assistentes_principais
        FROM agente_juridico 
        WHERE area_juridica IS NOT NULL
        GROUP BY area_juridica
        ORDER BY area_juridica
        """)
        
        estatisticas = cursor.fetchall()
        
        print("\n" + "="*80)
        print("🎯 RELATÓRIO FINAL - 18 ASSISTENTES JURÍDICOS PRINCIPAIS")
        print("="*80)
        
        for area, total, principais in estatisticas:
            if principais > 0:
                print(f"📋 {area:<35} | Assistente Principal: {principais} | Agentes: {total-principais}")
        
        # Contar total de comunicações possíveis
        cursor.execute("SELECT COUNT(*) FROM agente_juridico WHERE classe = 'AssistentePrincipal'")
        total_assistentes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM agente_juridico")
        total_agentes = cursor.fetchone()[0]
        
        print(f"\n📊 ESTATÍSTICAS GERAIS:")
        print(f"   • Assistentes Principais: {total_assistentes}")
        print(f"   • Total de Agentes: {total_agentes}")
        print(f"   • Conexões Potenciais: {total_assistentes * (total_agentes - total_assistentes)}")
        
        print("\n✅ Sistema Multi-Agente com 18 Assistentes Principais está OPERACIONAL!")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")
    finally:
        cursor.close()
        connection.close()

def main():
    """Função principal"""
    print("🚀 INICIANDO CRIAÇÃO DOS 18 ASSISTENTES JURÍDICOS PRINCIPAIS")
    print("="*70)
    
    # 1. Criar assistentes
    assistentes = criar_18_assistentes_principais()
    print(f"📋 {len(assistentes)} assistentes principais definidos")
    
    # 2. Inserir no banco
    if inserir_assistentes_database(assistentes):
        print("✅ Assistentes inseridos com sucesso!")
    else:
        print("❌ Erro na inserção dos assistentes")
        return
    
    # 3. Atualizar sistema
    if atualizar_sistema_multi_agente():
        print("✅ Sistema multi-agente configurado!")
    else:
        print("❌ Erro na configuração do sistema")
        return
    
    # 4. Estabelecer hierarquias
    if estabelecer_hierarquias():
        print("✅ Hierarquias estabelecidas!")
    else:
        print("❌ Erro ao estabelecer hierarquias")
        return
    
    # 5. Relatório final
    gerar_relatorio_final()

if __name__ == "__main__":
    main()