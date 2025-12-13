"""
Script para corrigir capacidades dos agentes de Análise de Riscos Jurídicos
Cada agente deve ter capacidades específicas para sua especialidade
"""

import psycopg2
import os
from datetime import datetime

def conectar_database():
    """Conecta ao banco PostgreSQL"""
    try:
        connection = psycopg2.connect(
            host=os.environ.get('PGHOST'),
            database=os.environ.get('PGDATABASE'),
            user=os.environ.get('PGUSER'),
            password=os.environ.get('PGPASSWORD'),
            port=os.environ.get('PGPORT', 5432)
        )
        return connection
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None

def definir_capacidades_especializadas():
    """Define capacidades específicas para cada agente de riscos"""
    return {
        'Consultor de Risco de Responsabilidade Civil': [
            'Análise de responsabilidade civil extracontratual',
            'Avaliação de danos morais e materiais',
            'Análise de nexo causal em acidentes',
            'Consultoria em seguros de responsabilidade civil',
            'Análise de casos de responsabilidade médica',
            'Avaliação de riscos em atividades de risco',
            'Consultoria em responsabilidade do Estado',
            'Análise de responsabilidade por danos ambientais'
        ],
        
        'Consultor em Risco Tributário': [
            'Análise de riscos em planejamento tributário',
            'Avaliação de contingências fiscais',
            'Consultoria em elisão e evasão fiscal',
            'Análise de autuações e multas tributárias',
            'Avaliação de riscos em reorganizações societárias',
            'Consultoria em tributação internacional',
            'Análise de benefícios fiscais e incentivos',
            'Avaliação de riscos em fusões e aquisições'
        ],
        
        'Consultor em Riscos de Compliance': [
            'Análise de programas de compliance',
            'Avaliação de riscos de corrupção',
            'Consultoria em lei anticorrupção',
            'Análise de políticas internas de compliance',
            'Avaliação de riscos de lavagem de dinheiro',
            'Consultoria em due diligence de terceiros',
            'Análise de canal de denúncias',
            'Avaliação de treinamentos em compliance'
        ],
        
        'Especialista em Risco Contratual Internacional': [
            'Análise de contratos internacionais',
            'Avaliação de riscos cambiais',
            'Consultoria em arbitragem internacional',
            'Análise de cláusulas de força maior',
            'Avaliação de riscos políticos',
            'Consultoria em contratos de exportação',
            'Análise de jurisdição e lei aplicável',
            'Avaliação de garantias internacionais'
        ],
        
        'Especialista em Risco Societário': [
            'Análise de riscos em governança corporativa',
            'Avaliação de conflitos societários',
            'Consultoria em reorganizações societárias',
            'Análise de responsabilidade de administradores',
            'Avaliação de riscos em assembleia de acionistas',
            'Consultoria em alienação de controle',
            'Análise de acordo de acionistas',
            'Avaliação de riscos em IPO'
        ],
        
        'Especialista em Risco Trabalhista': [
            'Análise de passivos trabalhistas',
            'Avaliação de riscos em demissões',
            'Consultoria em terceirização',
            'Análise de riscos em convenções coletivas',
            'Avaliação de acidentes de trabalho',
            'Consultoria em medicina e segurança do trabalho',
            'Análise de riscos em home office',
            'Avaliação de contingências trabalhistas'
        ],
        
        'Especialista em Risco de Propriedade Intelectual': [
            'Análise de violação de patentes',
            'Avaliação de riscos em marcas',
            'Consultoria em direitos autorais',
            'Análise de segredos comerciais',
            'Avaliação de riscos em licenciamento',
            'Consultoria em transferência de tecnologia',
            'Análise de concorrência desleal',
            'Avaliação de riscos em inovação'
        ],
        
        'Especialista em Riscos em Licitações': [
            'Análise de editais de licitação',
            'Avaliação de riscos em propostas',
            'Consultoria em impugnações',
            'Análise de recursos administrativos',
            'Avaliação de riscos contratuais públicos',
            'Consultoria em compliance público',
            'Análise de sanções administrativas',
            'Avaliação de riscos em contratos administrativos'
        ],
        
        'Orquestrador Multi-Agente': [
            'Coordenação de análises multi-agente',
            'Síntese de pareceres especializados',
            'Gestão de fluxos de análise',
            'Coordenação de equipes jurídicas',
            'Análise integrada de riscos',
            'Gestão de projetos jurídicos complexos',
            'Coordenação de estudos multidisciplinares',
            'Síntese executiva de análises'
        ]
    }

def atualizar_capacidades_agentes():
    """Atualiza as capacidades de cada agente específico"""
    connection = conectar_database()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        capacidades_map = definir_capacidades_especializadas()
        
        print("🔧 Atualizando capacidades dos agentes de Análise de Riscos...")
        
        # Primeiro, vamos encontrar o categoria_id para "Análise de Riscos Jurídicos"
        cursor.execute("""
            SELECT id FROM categoria_juridica 
            WHERE nome = 'Análise de Riscos Jurídicos'
        """)
        
        categoria_result = cursor.fetchone()
        if not categoria_result:
            print("❌ Categoria 'Análise de Riscos Jurídicos' não encontrada")
            return
        
        categoria_id = categoria_result[0]
        print(f"📋 Categoria ID encontrado: {categoria_id}")
        
        for nome_agente, capacidades in capacidades_map.items():
            # Criar JSON de capacidades
            import json
            capacidades_json = json.dumps(capacidades, ensure_ascii=False)
            
            # Atualizar o agente
            cursor.execute("""
                UPDATE agente_juridico 
                SET capacidades = %s::json
                WHERE nome = %s 
                AND categoria_id = %s
            """, (capacidades_json, nome_agente, categoria_id))
            
            if cursor.rowcount > 0:
                print(f"✅ {nome_agente}: {len(capacidades)} capacidades atualizadas")
            else:
                print(f"⚠️ {nome_agente}: Agente não encontrado")
        
        connection.commit()
        print(f"\n✅ Capacidades atualizadas para {len(capacidades_map)} agentes!")
        
    except Exception as e:
        print(f"❌ Erro ao atualizar capacidades: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def verificar_capacidades_atualizadas():
    """Verifica se as capacidades foram atualizadas corretamente"""
    connection = conectar_database()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        # Primeiro, encontrar o categoria_id
        cursor.execute("""
            SELECT id FROM categoria_juridica 
            WHERE nome = 'Análise de Riscos Jurídicos'
        """)
        
        categoria_result = cursor.fetchone()
        if not categoria_result:
            print("❌ Categoria 'Análise de Riscos Jurídicos' não encontrada")
            return
        
        categoria_id = categoria_result[0]
        
        cursor.execute("""
            SELECT nome, capacidades
            FROM agente_juridico 
            WHERE categoria_id = %s
            ORDER BY nome
        """, (categoria_id,))
        
        resultados = cursor.fetchall()
        
        print("\n📋 Verificação das capacidades atualizadas:")
        print("=" * 60)
        
        for nome, capacidades in resultados:
            import json
            if isinstance(capacidades, list):
                cap_list = capacidades
            elif isinstance(capacidades, str):
                try:
                    cap_list = json.loads(capacidades)
                except:
                    cap_list = capacidades.split('; ') if capacidades else []
            else:
                cap_list = []
            
            print(f"\n🔍 {nome}")
            print(f"   Capacidades: {len(cap_list)}")
            for i, cap in enumerate(cap_list[:3], 1):  # Mostra apenas as 3 primeiras
                print(f"   {i}. {cap}")
            if len(cap_list) > 3:
                print(f"   ... e mais {len(cap_list) - 3} capacidades")
        
    except Exception as e:
        print(f"❌ Erro ao verificar capacidades: {e}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    print("🚀 Iniciando correção das capacidades dos agentes de Análise de Riscos")
    print("=" * 60)
    
    atualizar_capacidades_agentes()
    verificar_capacidades_atualizadas()
    
    print("\n🎯 Correção de capacidades concluída!")