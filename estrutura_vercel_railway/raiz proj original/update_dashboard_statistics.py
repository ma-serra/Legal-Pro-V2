#!/usr/bin/env python3
"""
Script de Atualização das Estatísticas do Dashboard
Atualiza os números dos cards conforme a imagem fornecida com dados reais do banco de dados
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json

def get_database_connection():
    """Estabelece conexão com o banco de dados PostgreSQL"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL não encontrada nas variáveis de ambiente")
        
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar com o banco de dados: {e}")
        return None

def get_current_statistics():
    """Coleta estatísticas atuais do sistema"""
    conn = get_database_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Estatísticas principais
        stats_query = """
        SELECT 
            -- Documentos (incluindo todos os documentos processados nas tabelas vetoriais)
            (SELECT COUNT(*) FROM legal_documents) +
            (SELECT COUNT(*) FROM embeddings_direito_penal) +
            (SELECT COUNT(*) FROM embeddings_direito_civil) +
            (SELECT COUNT(*) FROM embeddings_direito_trabalhista) +
            (SELECT COUNT(*) FROM embeddings_direito_administrativo) +
            (SELECT COUNT(*) FROM embeddings_direito_empresarial) +
            (SELECT COUNT(*) FROM embeddings_direito_tributario) +
            (SELECT COUNT(*) FROM embeddings_direito_consumidor) +
            (SELECT COUNT(*) FROM embeddings_direito_ambiental) +
            (SELECT COUNT(*) FROM embeddings_direito_bancario) +
            (SELECT COUNT(*) FROM embeddings_direito_agrario) as total_documentos,
            (SELECT COUNT(*) FROM arquivo_transcricao) as total_transcricoes,
            
            -- Base Vetorial
            (SELECT COUNT(*) FROM information_schema.tables 
             WHERE table_schema = 'public' 
             AND table_name LIKE 'embeddings_%') as tabelas_embeddings,
            
            -- Agentes
            (SELECT COUNT(*) FROM agente_juridico WHERE ativo = true) as agentes_ativos,
            (SELECT COUNT(*) FROM agente_juridico) as total_agentes,
            (SELECT COUNT(DISTINCT classe) FROM agente_juridico WHERE ativo = true) as tipos_agentes,
            
            -- Templates
            (SELECT COUNT(*) FROM template_juridico WHERE ativo = true) as templates_ativos,
            (SELECT COUNT(*) FROM template_juridico) as total_templates,
            (SELECT COUNT(DISTINCT area_juridica) FROM template_juridico 
             WHERE area_juridica IS NOT NULL AND ativo = true) as areas_templates,
            
            -- Usuários e Sistema
            (SELECT COUNT(*) FROM "user") as total_usuarios,
            (SELECT COUNT(*) FROM "user" WHERE active = true) as usuarios_ativos,
            (SELECT COUNT(DISTINCT categoria_id) FROM agente_juridico 
             WHERE categoria_id IS NOT NULL) as categorias_cobertas
        """
        
        cursor.execute(stats_query)
        stats = cursor.fetchone()
        
        # Estatísticas detalhadas por área
        areas_query = """
        SELECT 
            area_juridica,
            COUNT(*) as quantidade_templates,
            COUNT(CASE WHEN ativo = true THEN 1 END) as templates_ativos
        FROM template_juridico 
        WHERE area_juridica IS NOT NULL
        GROUP BY area_juridica
        ORDER BY quantidade_templates DESC
        """
        
        cursor.execute(areas_query)
        areas_stats = cursor.fetchall()
        
        # Estatísticas de agentes por categoria
        agentes_query = """
        SELECT 
            c.nome as categoria,
            COUNT(a.id) as quantidade_agentes,
            COUNT(CASE WHEN a.ativo = true THEN 1 END) as agentes_ativos
        FROM categoria_juridica c
        LEFT JOIN agente_juridico a ON c.id = a.categoria_id
        GROUP BY c.id, c.nome
        ORDER BY quantidade_agentes DESC
        """
        
        cursor.execute(agentes_query)
        agentes_stats = cursor.fetchall()
        
        # Informações sobre embeddings
        embeddings_query = """
        SELECT 
            table_name,
            (SELECT COUNT(*) FROM information_schema.columns 
             WHERE table_name = t.table_name 
             AND column_name = 'embedding') as has_embedding_column
        FROM information_schema.tables t
        WHERE table_schema = 'public' 
        AND table_name LIKE 'embeddings_%'
        """
        
        cursor.execute(embeddings_query)
        embeddings_tables = cursor.fetchall()
        
        return {
            'stats': dict(stats),
            'areas': [dict(area) for area in areas_stats],
            'agentes': [dict(agente) for agente in agentes_stats],
            'embeddings_tables': [dict(table) for table in embeddings_tables],
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Erro ao coletar estatísticas: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def calculate_dashboard_numbers(stats_data):
    """Calcula os números dos cards do dashboard baseado nas estatísticas reais"""
    if not stats_data:
        return None
    
    stats = stats_data['stats']
    areas = stats_data['areas']
    
    # Card 1: Documentos
    total_docs = stats['total_documentos'] + stats['total_transcricoes']
    areas_cobertas = len([area for area in areas if area['templates_ativos'] > 0])
    
    # Card 2: Base Vetorial  
    total_embeddings = stats['tabelas_embeddings']
    dimensoes = 1536  # Padrão OpenAI
    
    # Card 3: Agentes
    total_agentes = stats['agentes_ativos']
    especialistas = stats['tipos_agentes']
    
    # Card 4: Templates
    total_templates_card = stats['templates_ativos']
    areas_especializadas = stats['areas_templates']
    
    dashboard_data = {
        'documentos': {
            'numero_principal': total_docs,
            'areas_cobertas': areas_cobertas,
            'processados': total_docs,
            'formatos': 'PDF/DOCX'
        },
        'base_vetorial': {
            'numero_principal': total_embeddings,
            'embeddings_ativos': 'Embeddings ativos',
            'tabelas': total_embeddings,
            'dimensoes': dimensoes
        },
        'agentes': {
            'numero_principal': total_agentes,
            'especialistas': especialistas,
            'tipos_especialistas': f"{especialistas} especialistas",
            'areas_atendidas': areas_cobertas
        },
        'templates': {
            'numero_principal': total_templates_card,
            'areas_especializadas': areas_especializadas,
            'descricao': f"{areas_especializadas} áreas especializadas",
            'categoria': 'Templates'
        }
    }
    
    return dashboard_data

def update_template_files(dashboard_data):
    """Atualiza os arquivos de template com os novos números"""
    if not dashboard_data:
        print("❌ Dados do dashboard não disponíveis")
        return False
    
    # Mapeamento de arquivos para atualizar
    template_files = [
        'templates/home_dashboard.html',
        'templates/index.html',
        'templates/legal_design_pro_v2/dashboard.html'
    ]
    
    updates_made = 0
    
    for template_file in template_files:
        if os.path.exists(template_file):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Substituições para números hardcoded
                replacements = [
                    # Documentos
                    ('{{ stats.total_documents or 0 }}', str(dashboard_data['documentos']['numero_principal'])),
                    ('{{ stats.total_documents or 25 }}', str(dashboard_data['documentos']['processados'])),
                    
                    # Base Vetorial
                    ('<h6 class="mb-0">20</h6>', f'<h6 class="mb-0">{dashboard_data["base_vetorial"]["tabelas"]}</h6>'),
                    ('<h6 class="mb-0">1536</h6>', f'<h6 class="mb-0">{dashboard_data["base_vetorial"]["dimensoes"]}</h6>'),
                    
                    # Agentes
                    ('<h4 class="mb-1 fw-bold">140</h4>', f'<h4 class="mb-1 fw-bold">{dashboard_data["agentes"]["numero_principal"]}</h4>'),
                    
                    # Templates
                    ('<h4 class="mb-1 fw-bold">42</h4>', f'<h4 class="mb-1 fw-bold">{dashboard_data["templates"]["numero_principal"]}</h4>'),
                    
                    # Áreas cobertas
                    ('16 áreas cobertas', f'{dashboard_data["documentos"]["areas_cobertas"]} áreas cobertas'),
                ]
                
                original_content = content
                for old_text, new_text in replacements:
                    content = content.replace(old_text, new_text)
                
                if content != original_content:
                    with open(template_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ Atualizado: {template_file}")
                    updates_made += 1
                else:
                    print(f"ℹ️  Nenhuma alteração necessária: {template_file}")
                    
            except Exception as e:
                print(f"❌ Erro ao atualizar {template_file}: {e}")
        else:
            print(f"⚠️  Arquivo não encontrado: {template_file}")
    
    return updates_made > 0

def generate_statistics_report(stats_data, dashboard_data):
    """Gera relatório detalhado das estatísticas"""
    if not stats_data or not dashboard_data:
        return
    
    print("\n" + "="*60)
    print("📊 RELATÓRIO DE ESTATÍSTICAS DO SISTEMA")
    print("="*60)
    
    print(f"\n🗓️  Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    print("\n📋 RESUMO DOS CARDS DO DASHBOARD:")
    print("-" * 40)
    
    # Card Documentos
    docs = dashboard_data['documentos']
    print(f"📄 DOCUMENTOS: {docs['numero_principal']}")
    print(f"   • Áreas cobertas: {docs['areas_cobertas']}")
    print(f"   • Processados: {docs['processados']}")
    print(f"   • Formatos: {docs['formatos']}")
    
    # Card Base Vetorial
    base = dashboard_data['base_vetorial']
    print(f"\n🗄️  BASE VETORIAL: {base['numero_principal']}")
    print(f"   • Tabelas: {base['tabelas']}")
    print(f"   • Dimensões: {base['dimensoes']}")
    
    # Card Agentes
    agentes = dashboard_data['agentes']
    print(f"\n🤖 AGENTES: {agentes['numero_principal']}")
    print(f"   • Especialistas: {agentes['especialistas']}")
    print(f"   • Áreas atendidas: {agentes['areas_atendidas']}")
    
    # Card Templates
    templates = dashboard_data['templates']
    print(f"\n📋 TEMPLATES: {templates['numero_principal']}")
    print(f"   • Áreas especializadas: {templates['areas_especializadas']}")
    
    print("\n📈 ESTATÍSTICAS DETALHADAS:")
    print("-" * 40)
    
    stats = stats_data['stats']
    print(f"• Total de agentes no sistema: {stats['total_agentes']}")
    print(f"• Agentes ativos: {stats['agentes_ativos']}")
    print(f"• Total de templates: {stats['total_templates']}")
    print(f"• Templates ativos: {stats['templates_ativos']}")
    print(f"• Usuários registrados: {stats['total_usuarios']}")
    print(f"• Usuários ativos: {stats['usuarios_ativos']}")
    print(f"• Categorias cobertas: {stats['categorias_cobertas']}")
    
    # Top 5 áreas por templates
    print(f"\n🏆 TOP 5 ÁREAS COM MAIS TEMPLATES:")
    print("-" * 40)
    for i, area in enumerate(stats_data['areas'][:5], 1):
        print(f"{i}. {area['area_juridica']}: {area['templates_ativos']} ativos de {area['quantidade_templates']} total")
    
    print("\n" + "="*60)

def main():
    """Função principal do script"""
    print("🚀 Iniciando atualização das estatísticas do dashboard...")
    
    # Coletar estatísticas atuais
    print("\n📊 Coletando estatísticas do banco de dados...")
    stats_data = get_current_statistics()
    
    if not stats_data:
        print("❌ Falha ao coletar estatísticas. Abortando.")
        return False
    
    # Calcular números do dashboard
    print("🔢 Calculando números dos cards...")
    dashboard_data = calculate_dashboard_numbers(stats_data)
    
    if not dashboard_data:
        print("❌ Falha ao calcular dados do dashboard. Abortando.")
        return False
    
    # Atualizar arquivos de template
    print("📝 Atualizando arquivos de template...")
    success = update_template_files(dashboard_data)
    
    # Gerar relatório
    generate_statistics_report(stats_data, dashboard_data)
    
    # Salvar dados para referência futura
    try:
        output_file = f"dashboard_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'statistics': stats_data,
                'dashboard': dashboard_data
            }, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n💾 Dados salvos em: {output_file}")
    except Exception as e:
        print(f"⚠️  Erro ao salvar dados: {e}")
    
    if success:
        print("\n✅ Atualização das estatísticas concluída com sucesso!")
        print("ℹ️  Reinicie o servidor para ver as mudanças refletidas.")
    else:
        print("\n⚠️  Algumas atualizações podem não ter sido aplicadas.")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Operação cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)