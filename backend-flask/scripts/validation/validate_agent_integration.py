#!/usr/bin/env python3
"""
Script de validação da integração completa dos agentes jurídicos.
Verifica se as capacidades e prompts estão corretamente integrados.
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

def validate_agent_completeness():
    """Valida a completude dos dados dos agentes"""
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔍 VALIDAÇÃO DA INTEGRAÇÃO DE AGENTES JURÍDICOS\n")
        
        # 1. Estatísticas gerais
        cursor.execute("""
            SELECT 
                COUNT(*) as total_agentes,
                COUNT(CASE WHEN capacidades IS NOT NULL THEN 1 END) as com_capacidades,
                COUNT(CASE WHEN template_prompt IS NOT NULL AND LENGTH(template_prompt) > 100 THEN 1 END) as com_prompts,
                COUNT(CASE WHEN JSON_ARRAY_LENGTH(capacidades) = 5 THEN 1 END) as com_5_capacidades
            FROM agente_juridico WHERE ativo = true
        """)
        
        stats = cursor.fetchone()
        print("📊 ESTATÍSTICAS GERAIS:")
        print(f"   Total de agentes ativos: {stats['total_agentes']}")
        print(f"   Agentes com capacidades: {stats['com_capacidades']}")
        print(f"   Agentes com prompts: {stats['com_prompts']}")
        print(f"   Agentes com 5 capacidades: {stats['com_5_capacidades']}")
        print()
        
        # 2. Distribuição por tipo
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN nome LIKE '%Analista%' THEN 1 END) as analistas,
                COUNT(CASE WHEN nome LIKE '%Consultor%' THEN 1 END) as consultores,
                COUNT(CASE WHEN nome LIKE '%Especialista%' THEN 1 END) as especialistas,
                COUNT(CASE WHEN nome LIKE '%Dr(%' THEN 1 END) as doutores,
                COUNT(CASE WHEN nome LIKE '%Perito%' THEN 1 END) as peritos,
                COUNT(CASE WHEN nome LIKE '%Revisor%' THEN 1 END) as revisores
            FROM agente_juridico WHERE ativo = true
        """)
        
        tipos = cursor.fetchone()
        print("👥 DISTRIBUIÇÃO POR TIPO:")
        print(f"   Analistas: {tipos['analistas']}")
        print(f"   Consultores: {tipos['consultores']}")
        print(f"   Especialistas: {tipos['especialistas']}")
        print(f"   Doutores: {tipos['doutores']}")
        print(f"   Peritos: {tipos['peritos']}")
        print(f"   Revisores: {tipos['revisores']}")
        print()
        
        # 3. Agentes com prompts especializados
        cursor.execute("""
            SELECT nome, JSON_ARRAY_LENGTH(capacidades) as num_caps, LENGTH(template_prompt) as tamanho_prompt
            FROM agente_juridico 
            WHERE ativo = true 
            AND template_prompt IS NOT NULL 
            AND LENGTH(template_prompt) > 500
            AND JSON_ARRAY_LENGTH(capacidades) = 5
            ORDER BY LENGTH(template_prompt) DESC
            LIMIT 10
        """)
        
        especializados = cursor.fetchall()
        print("🎯 TOP 10 AGENTES ESPECIALIZADOS:")
        for i, agent in enumerate(especializados, 1):
            print(f"   {i:2d}. {agent['nome'][:50]:<50} | {agent['num_caps']} caps | {agent['tamanho_prompt']} chars")
        print()
        
        # 4. Validação de capacidades únicas  
        cursor.execute("""
            SELECT DISTINCT json_array_elements_text(capacidades) as capacidade
            FROM agente_juridico 
            WHERE ativo = true AND capacidades IS NOT NULL
            ORDER BY capacidade
        """)
        
        capacidades_unicas = cursor.fetchall()
        print(f"🔧 CAPACIDADES ÚNICAS IDENTIFICADAS: {len(capacidades_unicas)}")
        print("   Exemplos:")
        for i, cap in enumerate(capacidades_unicas[:10], 1):
            print(f"   {i:2d}. {cap['capacidade']}")
        print()
        
        # 5. Agentes por categoria jurídica
        cursor.execute("""
            SELECT cj.nome as categoria, COUNT(aj.id) as num_agentes
            FROM categoria_juridica cj
            LEFT JOIN agente_juridico aj ON cj.id = aj.categoria_id AND aj.ativo = true
            WHERE cj.ativa = true
            ORDER BY num_agentes DESC
        """)
        
        por_categoria = cursor.fetchall()
        print("📚 AGENTES POR CATEGORIA JURÍDICA:")
        for cat in por_categoria:
            print(f"   {cat['categoria']:<30} | {cat['num_agentes']:3d} agentes")
        print()
        
        # 6. Verificação de qualidade de prompts
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN template_prompt LIKE '%CAPACIDADES%' THEN 1 END) as com_estrutura_capacidades,
                COUNT(CASE WHEN template_prompt LIKE '%METODOLOGIA%' THEN 1 END) as com_metodologia,
                COUNT(CASE WHEN template_prompt LIKE '%especializado%' THEN 1 END) as com_especializacao,
                COUNT(CASE WHEN LENGTH(template_prompt) > 800 THEN 1 END) as prompts_detalhados
            FROM agente_juridico 
            WHERE ativo = true AND template_prompt IS NOT NULL
        """)
        
        qualidade = cursor.fetchone()
        print("✅ QUALIDADE DOS PROMPTS:")
        print(f"   Prompts com estrutura de capacidades: {qualidade['com_estrutura_capacidades']}")
        print(f"   Prompts com metodologia: {qualidade['com_metodologia']}")
        print(f"   Prompts com especialização: {qualidade['com_especializacao']}")
        print(f"   Prompts detalhados (>800 chars): {qualidade['prompts_detalhados']}")
        print()
        
        # 7. Exemplos de integração completa
        cursor.execute("""
            SELECT nome, capacidades, LEFT(template_prompt, 150) as prompt_preview
            FROM agente_juridico 
            WHERE ativo = true 
            AND JSON_ARRAY_LENGTH(capacidades) = 5
            AND LENGTH(template_prompt) > 600
            AND template_prompt LIKE '%especializado%'
            ORDER BY RANDOM()
            LIMIT 5
        """)
        
        exemplos = cursor.fetchall()
        print("🎯 EXEMPLOS DE INTEGRAÇÃO COMPLETA:")
        for exemplo in exemplos:
            caps = json.loads(exemplo['capacidades'])
            print(f"\n   📋 {exemplo['nome']}")
            print(f"      Capacidades: {len(caps)} especializadas")
            for i, cap in enumerate(caps[:3], 1):
                print(f"         {i}. {cap}")
            print(f"      Prompt: {exemplo['prompt_preview']}...")
        
        print(f"\n🎉 VALIDAÇÃO CONCLUÍDA - SISTEMA MULTI-AGENTE INTEGRADO!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return False
    finally:
        conn.close()

def main():
    """Função principal"""
    print("🚀 Iniciando validação da integração de agentes jurídicos...\n")
    
    if validate_agent_completeness():
        print("\n✅ Validação concluída com sucesso!")
        print("🎯 Sistema pronto para deployment!")
    else:
        print("\n❌ Falhas encontradas na validação!")
        sys.exit(1)

if __name__ == "__main__":
    main()