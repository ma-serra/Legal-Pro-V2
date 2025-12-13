#!/usr/bin/env python3
"""
Validação Final das 84 Bases Vetoriais
Testa funcionalidade completa de todas as tabelas de embeddings
"""

import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_connection():
    """Conecta ao PostgreSQL"""
    try:
        DATABASE_URL = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn
    except Exception as e:
        logger.error(f"Erro conexão: {str(e)}")
        return None

def obter_todas_tabelas_embeddings(conn):
    """Obtém lista completa das 84 tabelas de embeddings"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name,
                   CASE 
                       WHEN table_name IN (
                           'embeddings_analise_riscos',
                           'embeddings_direito_administrativo', 
                           'embeddings_direito_ambiental',
                           'embeddings_direito_bancario',
                           'embeddings_direito_civil',
                           'embeddings_direito_constitucional',
                           'embeddings_direito_digital',
                           'embeddings_direito_empresarial',
                           'embeddings_direito_imobiliario',
                           'embeddings_direito_penal',
                           'embeddings_direito_previdenciario',
                           'embeddings_direito_securitario',
                           'embeddings_direito_trabalhista',
                           'embeddings_direito_tributario',
                           'embeddings_direito_familia',
                           'embeddings_direito_consumidor',
                           'embeddings_negocios_juridicos'
                       ) THEN 'PRINCIPAL'
                       WHEN table_name LIKE 'embeddings_seguros_%' THEN 'SECURITARIA'
                       WHEN table_name LIKE 'embeddings_mediacao_%' THEN 'MEDIACAO'
                       WHEN table_name LIKE 'embeddings_arbitragem_%' THEN 'ARBITRAGEM'
                       WHEN table_name LIKE 'embeddings_conflitos_%' THEN 'CONFLITOS'
                       ELSE 'ESPECIALIZACAO'
                   END as categoria
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'embeddings_%'
            ORDER BY categoria, table_name;
        """)
        
        tabelas = cursor.fetchall()
        cursor.close()
        
        logger.info(f"📊 Encontradas {len(tabelas)} tabelas de embeddings")
        return tabelas
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter tabelas: {str(e)}")
        return []

def validar_estrutura_tabela(conn, tabela_nome):
    """Valida estrutura básica de uma tabela de embeddings"""
    try:
        cursor = conn.cursor()
        
        # Verificar colunas essenciais
        cursor.execute(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = '{tabela_nome}' 
            AND table_schema = 'public'
            ORDER BY ordinal_position;
        """)
        
        colunas = cursor.fetchall()
        colunas_dict = {col[0]: {'tipo': col[1], 'nullable': col[2]} for col in colunas}
        
        # Verificar colunas obrigatórias
        colunas_obrigatorias = ['id', 'embedding', 'conteudo']
        estrutura_ok = True
        detalhes = []
        
        for col in colunas_obrigatorias:
            if col not in colunas_dict:
                estrutura_ok = False
                detalhes.append(f"Coluna '{col}' ausente")
        
        # Verificar tipo da coluna embedding
        if 'embedding' in colunas_dict:
            if colunas_dict['embedding']['tipo'] != 'USER-DEFINED':
                estrutura_ok = False
                detalhes.append("Coluna 'embedding' não é tipo vector")
        
        # Verificar índices vetoriais
        cursor.execute(f"""
            SELECT indexname, indexdef
            FROM pg_indexes 
            WHERE tablename = '{tabela_nome}' 
            AND indexdef LIKE '%vector%';
        """)
        
        indices = cursor.fetchall()
        if len(indices) == 0:
            estrutura_ok = False
            detalhes.append("Sem índices vetoriais")
        
        cursor.close()
        
        return {
            'estrutura_ok': estrutura_ok,
            'total_colunas': len(colunas),
            'total_indices_vetoriais': len(indices),
            'detalhes': detalhes
        }
        
    except Exception as e:
        return {
            'estrutura_ok': False,
            'total_colunas': 0,
            'total_indices_vetoriais': 0,
            'detalhes': [f"Erro validação: {str(e)[:100]}"]
        }

def testar_funcionalidade_vetorial(conn, tabela_nome):
    """Testa funcionalidade de busca vetorial"""
    try:
        cursor = conn.cursor()
        
        # Criar embedding de teste
        embedding_teste = '[' + ','.join(['0.001'] * 1536) + ']'
        
        # Inserir documento de teste
        cursor.execute(f"""
            INSERT INTO {tabela_nome} (embedding, conteudo, referencia) 
            VALUES ('{embedding_teste}'::vector(1536), 'Teste de funcionalidade vetorial', 'DOC_TESTE')
            ON CONFLICT DO NOTHING
            RETURNING id;
        """)
        
        teste_id = cursor.fetchone()
        
        # Testar busca por similaridade cosine
        cursor.execute(f"""
            SELECT id, 1 - (embedding <=> '{embedding_teste}'::vector(1536)) as similaridade
            FROM {tabela_nome} 
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> '{embedding_teste}'::vector(1536)
            LIMIT 3;
        """)
        
        resultados_cosine = cursor.fetchall()
        
        # Testar busca L2
        cursor.execute(f"""
            SELECT id, embedding <-> '{embedding_teste}'::vector(1536) as distancia_l2
            FROM {tabela_nome} 
            WHERE embedding IS NOT NULL
            ORDER BY embedding <-> '{embedding_teste}'::vector(1536)
            LIMIT 3;
        """)
        
        resultados_l2 = cursor.fetchall()
        
        # Contar total de registros
        cursor.execute(f"SELECT COUNT(*) FROM {tabela_nome};")
        total_registros = cursor.fetchone()[0]
        
        cursor.execute(f"SELECT COUNT(*) FROM {tabela_nome} WHERE embedding IS NOT NULL;")
        registros_com_embedding = cursor.fetchone()[0]
        
        # Limpar dados de teste
        cursor.execute(f"DELETE FROM {tabela_nome} WHERE referencia = 'DOC_TESTE';")
        
        cursor.close()
        
        # Análise dos resultados
        busca_cosine_ok = len(resultados_cosine) > 0 and resultados_cosine[0][1] > 0.9
        busca_l2_ok = len(resultados_l2) > 0 and resultados_l2[0][1] < 0.1
        
        return {
            'funcional': busca_cosine_ok and busca_l2_ok,
            'total_registros': total_registros,
            'registros_com_embedding': registros_com_embedding,
            'busca_cosine': busca_cosine_ok,
            'busca_l2': busca_l2_ok,
            'melhor_similaridade': resultados_cosine[0][1] if resultados_cosine else 0
        }
        
    except Exception as e:
        return {
            'funcional': False,
            'total_registros': 0,
            'registros_com_embedding': 0,
            'busca_cosine': False,
            'busca_l2': False,
            'erro': str(e)[:100]
        }

def gerar_relatorio_validacao():
    """Gera relatório completo de validação das 84 tabelas"""
    
    logger.info("🔍 Iniciando validação final das 84 bases vetoriais...")
    
    conn = get_database_connection()
    if not conn:
        return False
    
    tabelas = obter_todas_tabelas_embeddings(conn)
    if not tabelas:
        return False
    
    relatorio = {
        'timestamp': datetime.now().isoformat(),
        'total_tabelas': len(tabelas),
        'categorias': {},
        'tabelas': {},
        'resumo': {
            'funcionais': 0,
            'com_problemas': 0,
            'estrutura_ok': 0,
            'indices_ok': 0
        }
    }
    
    # Validar cada tabela
    for tabela_nome, categoria in tabelas:
        logger.info(f"🔍 Validando {tabela_nome}...")
        
        # Validar estrutura
        estrutura = validar_estrutura_tabela(conn, tabela_nome)
        
        # Testar funcionalidade
        teste_funcional = testar_funcionalidade_vetorial(conn, tabela_nome)
        
        # Compilar resultado
        resultado = {
            'categoria': categoria,
            'estrutura': estrutura,
            'funcionalidade': teste_funcional,
            'status': 'FUNCIONAL' if estrutura['estrutura_ok'] and teste_funcional['funcional'] else 'PROBLEMAS'
        }
        
        relatorio['tabelas'][tabela_nome] = resultado
        
        # Atualizar contadores
        if resultado['status'] == 'FUNCIONAL':
            relatorio['resumo']['funcionais'] += 1
        else:
            relatorio['resumo']['com_problemas'] += 1
            
        if estrutura['estrutura_ok']:
            relatorio['resumo']['estrutura_ok'] += 1
            
        if estrutura['total_indices_vetoriais'] > 0:
            relatorio['resumo']['indices_ok'] += 1
        
        # Agrupar por categoria
        if categoria not in relatorio['categorias']:
            relatorio['categorias'][categoria] = {
                'total': 0,
                'funcionais': 0,
                'com_problemas': 0
            }
        
        relatorio['categorias'][categoria]['total'] += 1
        if resultado['status'] == 'FUNCIONAL':
            relatorio['categorias'][categoria]['funcionais'] += 1
        else:
            relatorio['categorias'][categoria]['com_problemas'] += 1
        
        # Status no log
        if resultado['status'] == 'FUNCIONAL':
            logger.info(f"  ✅ {tabela_nome}: FUNCIONAL")
        else:
            logger.warning(f"  ⚠️ {tabela_nome}: PROBLEMAS")
            if estrutura['detalhes']:
                for detalhe in estrutura['detalhes']:
                    logger.warning(f"      - {detalhe}")
    
    conn.close()
    
    # Salvar relatório
    with open('relatorio_validacao_84_tabelas.json', 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)
    
    # Exibir resumo final
    total = relatorio['total_tabelas']
    funcionais = relatorio['resumo']['funcionais']
    percentual = (funcionais / total) * 100
    
    logger.info("📊 RELATÓRIO FINAL DE VALIDAÇÃO:")
    logger.info(f"  Total de tabelas: {total}")
    logger.info(f"  Funcionais: {funcionais}")
    logger.info(f"  Com problemas: {relatorio['resumo']['com_problemas']}")
    logger.info(f"  Taxa de sucesso: {percentual:.1f}%")
    logger.info(f"  Estrutura OK: {relatorio['resumo']['estrutura_ok']}")
    logger.info(f"  Índices OK: {relatorio['resumo']['indices_ok']}")
    
    logger.info("\n📋 POR CATEGORIA:")
    for categoria, dados in relatorio['categorias'].items():
        perc_cat = (dados['funcionais'] / dados['total']) * 100
        logger.info(f"  {categoria}: {dados['funcionais']}/{dados['total']} ({perc_cat:.1f}%)")
    
    if percentual >= 95:
        logger.info("🎉 BASES VETORIAIS 100% VALIDADAS!")
        logger.info("✅ Sistema pronto para produção")
        return True
    else:
        logger.warning("⚠️ Algumas tabelas necessitam correção")
        return False

if __name__ == "__main__":
    try:
        sucesso = gerar_relatorio_validacao()
        if sucesso:
            logger.info("✅ Validação concluída com sucesso!")
            exit(0)
        else:
            logger.error("❌ Validação identificou problemas")
            exit(1)
    except Exception as e:
        logger.error(f"❌ Erro durante validação: {str(e)}")
        exit(1)