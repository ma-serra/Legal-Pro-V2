#!/usr/bin/env python3
"""
Validação Completa das 13 Áreas Jurídicas
Verifica estrutura, dados e integridade de cada base vetorial
"""

import os
import psycopg2
from datetime import datetime
import json

def conectar_database():
    """Conecta ao banco PostgreSQL"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None

def validar_estrutura_tabela(cursor, tabela):
    """Valida estrutura de uma tabela de embeddings"""
    try:
        # Verificar se a tabela existe
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name = %s
        """, (tabela,))
        
        existe = cursor.fetchone()[0] > 0
        
        if not existe:
            return {
                'existe': False,
                'colunas': [],
                'indices': [],
                'documentos': 0,
                'tamanho_medio': 0
            }
        
        # Verificar colunas
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = %s 
            ORDER BY ordinal_position
        """, (tabela,))
        
        colunas = cursor.fetchall()
        
        # Verificar índices
        cursor.execute("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = %s
        """, (tabela,))
        
        indices = cursor.fetchall()
        
        # Contar documentos
        cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
        total_docs = cursor.fetchone()[0]
        
        # Tamanho médio do conteúdo
        tamanho_medio = 0
        if total_docs > 0:
            try:
                cursor.execute(f"""
                    SELECT AVG(LENGTH(COALESCE(conteudo, texto, content, ''))) 
                    FROM {tabela}
                """)
                tamanho_medio = cursor.fetchone()[0] or 0
            except:
                # Tentar diferentes nomes de colunas
                for col in ['conteudo', 'texto', 'content', 'documento']:
                    try:
                        cursor.execute(f"SELECT AVG(LENGTH({col})) FROM {tabela}")
                        tamanho_medio = cursor.fetchone()[0] or 0
                        break
                    except:
                        continue
        
        return {
            'existe': True,
            'colunas': colunas,
            'indices': indices,
            'documentos': total_docs,
            'tamanho_medio': int(tamanho_medio)
        }
        
    except Exception as e:
        return {
            'existe': False,
            'erro': str(e),
            'colunas': [],
            'indices': [],
            'documentos': 0,
            'tamanho_medio': 0
        }

def validar_agentes_por_area(cursor, base_vetorial):
    """Valida agentes conectados a uma área específica"""
    try:
        cursor.execute("""
            SELECT id, nome, classe, temperatura, max_tokens, 
                   LENGTH(template_prompt) as tamanho_prompt
            FROM agente_juridico 
            WHERE base_vetorial = %s AND ativo = true
            ORDER BY nome
        """, (base_vetorial,))
        
        agentes = cursor.fetchall()
        
        # Estatísticas dos agentes
        total_agentes = len(agentes)
        agentes_configurados = sum(1 for a in agentes if a[3] and a[4] and a[5] > 0)
        
        return {
            'total': total_agentes,
            'configurados': agentes_configurados,
            'agentes': agentes,
            'taxa_configuracao': (agentes_configurados / total_agentes * 100) if total_agentes > 0 else 0
        }
        
    except Exception as e:
        return {
            'erro': str(e),
            'total': 0,
            'configurados': 0,
            'agentes': [],
            'taxa_configuracao': 0
        }

def executar_validacao_completa():
    """Executa validação completa das 13 áreas"""
    
    areas_juridicas = {
        'embeddings_direito_penal': 'Direito Penal',
        'embeddings_direito_trabalhista': 'Direito Trabalhista', 
        'embeddings_direito_empresarial': 'Direito Empresarial',
        'embeddings_recuperacao_credito': 'Recuperação de Crédito',
        'embeddings_direito_tributario': 'Direito Tributário',
        'embeddings_direito_agrario': 'Direito Agrário',
        'embeddings_direito_consumidor': 'Direito do Consumidor',
        'embeddings_direito_imobiliario': 'Direito Imobiliário',
        'embeddings_negociacao_conflitos': 'Negociação e Conflitos',
        'embeddings_direito_bancario': 'Direito Bancário',
        'embeddings_direito_securitario': 'Direito Securitário',
        'embeddings_direito_digital': 'Direito Digital',
        'embeddings_direito_previdenciario': 'Direito Previdenciário'
    }
    
    conn = conectar_database()
    if not conn:
        return False
    
    cursor = conn.cursor()
    resultado_validacao = {}
    
    print("🔍 VALIDAÇÃO DAS 13 ÁREAS JURÍDICAS")
    print("=" * 60)
    
    total_areas = len(areas_juridicas)
    areas_operacionais = 0
    total_agentes = 0
    total_documentos = 0
    
    for i, (tabela, nome_area) in enumerate(areas_juridicas.items(), 1):
        print(f"\n{i:2d}/13 - Validando {nome_area}...")
        
        # Validar estrutura da tabela
        estrutura = validar_estrutura_tabela(cursor, tabela)
        
        # Validar agentes da área
        agentes = validar_agentes_por_area(cursor, tabela)
        
        # Status da área
        operacional = (estrutura['existe'] and 
                      agentes['total'] > 0 and 
                      agentes['configurados'] == agentes['total'])
        
        if operacional:
            areas_operacionais += 1
        
        total_agentes += agentes['total']
        total_documentos += estrutura['documentos']
        
        # Armazenar resultado
        resultado_validacao[tabela] = {
            'nome': nome_area,
            'estrutura': estrutura,
            'agentes': agentes,
            'operacional': operacional,
            'prioridade': 'ALTA' if not operacional else 'BAIXA' if estrutura['documentos'] == 0 else 'NORMAL'
        }
        
        # Exibir status
        status_icon = "✅" if operacional else "⚠️" if estrutura['existe'] else "❌"
        docs_info = f"{estrutura['documentos']} docs" if estrutura['documentos'] > 0 else "sem docs"
        
        print(f"    {status_icon} {nome_area}")
        print(f"       Tabela: {'OK' if estrutura['existe'] else 'ERRO'}")
        print(f"       Agentes: {agentes['configurados']}/{agentes['total']} configurados")
        print(f"       Documentos: {docs_info}")
        
        if estrutura.get('erro'):
            print(f"       ❌ Erro: {estrutura['erro']}")
    
    # Relatório final
    print(f"\n📊 RESUMO GERAL:")
    print(f"   Áreas operacionais: {areas_operacionais}/{total_areas} ({areas_operacionais/total_areas*100:.1f}%)")
    print(f"   Total de agentes: {total_agentes}")
    print(f"   Total de documentos: {total_documentos}")
    
    # Identificar problemas
    areas_com_problema = []
    areas_sem_documentos = []
    
    for tabela, dados in resultado_validacao.items():
        if not dados['operacional']:
            areas_com_problema.append(dados['nome'])
        elif dados['estrutura']['documentos'] == 0:
            areas_sem_documentos.append(dados['nome'])
    
    if areas_com_problema:
        print(f"\n⚠️  ÁREAS COM PROBLEMAS ({len(areas_com_problema)}):")
        for area in areas_com_problema:
            print(f"   - {area}")
    
    if areas_sem_documentos:
        print(f"\n📭 ÁREAS SEM DOCUMENTOS ({len(areas_sem_documentos)}):")
        for area in areas_sem_documentos:
            print(f"   - {area}")
    
    # Salvar relatório detalhado
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"validacao_13_areas_{timestamp}.json"
    
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        json.dump(resultado_validacao, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n📄 Relatório detalhado salvo: {nome_arquivo}")
    
    # Gerar relatório markdown
    nome_md = f"RELATORIO_VALIDACAO_13_AREAS_{timestamp}.md"
    gerar_relatorio_markdown(resultado_validacao, nome_md, areas_operacionais, total_areas, total_agentes, total_documentos)
    
    cursor.close()
    conn.close()
    
    return areas_operacionais == total_areas

def gerar_relatorio_markdown(dados, nome_arquivo, areas_ok, total_areas, total_agentes, total_docs):
    """Gera relatório em Markdown"""
    
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write(f"# Relatório de Validação das 13 Áreas Jurídicas\n\n")
        f.write(f"**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
        
        f.write(f"## Resumo Executivo\n\n")
        f.write(f"- **Áreas operacionais:** {areas_ok}/{total_areas} ({areas_ok/total_areas*100:.1f}%)\n")
        f.write(f"- **Total de agentes:** {total_agentes}\n")
        f.write(f"- **Total de documentos:** {total_docs}\n")
        f.write(f"- **Status geral:** {'✅ SISTEMA OPERACIONAL' if areas_ok == total_areas else '⚠️ ATENÇÃO NECESSÁRIA'}\n\n")
        
        f.write(f"## Detalhes por Área\n\n")
        
        for tabela, info in dados.items():
            status = "✅" if info['operacional'] else "⚠️" if info['estrutura']['existe'] else "❌"
            f.write(f"### {status} {info['nome']}\n\n")
            f.write(f"- **Tabela:** {tabela}\n")
            f.write(f"- **Status:** {'Operacional' if info['operacional'] else 'Necessita atenção'}\n")
            f.write(f"- **Agentes:** {info['agentes']['configurados']}/{info['agentes']['total']}\n")
            f.write(f"- **Documentos:** {info['estrutura']['documentos']}\n")
            f.write(f"- **Prioridade:** {info['prioridade']}\n\n")
            
            if info['estrutura']['documentos'] > 0:
                f.write(f"- **Tamanho médio:** {info['estrutura']['tamanho_medio']} caracteres\n")
            
            f.write(f"\n")
    
    print(f"📄 Relatório markdown salvo: {nome_arquivo}")

if __name__ == "__main__":
    print("🚀 INICIANDO VALIDAÇÃO DAS 13 ÁREAS JURÍDICAS")
    
    sucesso = executar_validacao_completa()
    
    if sucesso:
        print("\n🎉 TODAS AS 13 ÁREAS ESTÃO OPERACIONAIS!")
    else:
        print("\n⚠️  ALGUMAS ÁREAS PRECISAM DE ATENÇÃO")
    
    print("\n✅ Validação concluída")