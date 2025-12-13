#!/usr/bin/env python3
"""
Script para corrigir e padronizar estruturas das bases vetoriais
Adiciona colunas faltantes e cria índices necessários
"""

import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_connection():
    """Estabelece conexão direta com PostgreSQL"""
    try:
        DATABASE_URL = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar com banco de dados: {str(e)}")
        return None

def obter_tabelas_embeddings(conn):
    """Obtém todas as tabelas de embeddings existentes"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'embeddings_%'
            ORDER BY table_name;
        """)
        
        tabelas = [row[0] for row in cursor.fetchall()]
        cursor.close()
        
        logger.info(f"📊 Encontradas {len(tabelas)} tabelas de embeddings")
        return tabelas
        
    except Exception as e:
        logger.error(f"Erro ao obter tabelas: {str(e)}")
        return []

def verificar_estrutura_tabela(conn, nome_tabela):
    """Verifica colunas existentes na tabela"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = %s
            ORDER BY ordinal_position;
        """, (nome_tabela,))
        
        colunas = {row[0]: row for row in cursor.fetchall()}
        cursor.close()
        return colunas
        
    except Exception as e:
        logger.error(f"Erro ao verificar estrutura de {nome_tabela}: {str(e)}")
        return {}

def corrigir_estrutura_tabela(conn, nome_tabela):
    """Corrige estrutura da tabela adicionando colunas faltantes"""
    try:
        cursor = conn.cursor()
        
        # Obter estrutura atual
        colunas_existentes = verificar_estrutura_tabela(conn, nome_tabela)
        
        # Definir colunas obrigatórias
        colunas_obrigatorias = {
            'id': 'SERIAL PRIMARY KEY',
            'documento_id': 'VARCHAR(255)',
            'documento_nome': 'TEXT',
            'documento_tipo': 'VARCHAR(100)',
            'conteudo_texto': 'TEXT',
            'embedding': 'vector(1536)',
            'metadata': 'JSONB DEFAULT \'{}\'',
            'data_criacao': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'data_atualizacao': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'agente_id': 'INTEGER',
            'categoria_juridica': 'VARCHAR(255)',
            'chunk_index': 'INTEGER DEFAULT 0',
            'chunk_total': 'INTEGER DEFAULT 1'
        }
        
        colunas_adicionadas = []
        
        # Adicionar colunas faltantes
        for coluna, tipo_sql in colunas_obrigatorias.items():
            if coluna not in colunas_existentes:
                try:
                    if 'PRIMARY KEY' in tipo_sql:
                        # Pular se for chave primária e já existir uma
                        continue
                    
                    sql_add = f"ALTER TABLE {nome_tabela} ADD COLUMN {coluna} {tipo_sql};"
                    cursor.execute(sql_add)
                    colunas_adicionadas.append(coluna)
                    logger.info(f"  ✅ Coluna {coluna} adicionada")
                    
                except Exception as e:
                    logger.warning(f"  ⚠️ Erro ao adicionar coluna {coluna}: {str(e)}")
        
        # Criar índices essenciais
        indices_criados = []
        indices_sql = [
            f"CREATE INDEX IF NOT EXISTS idx_{nome_tabela}_embedding_cosine ON {nome_tabela} USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);",
            f"CREATE INDEX IF NOT EXISTS idx_{nome_tabela}_documento_id ON {nome_tabela} (documento_id);",
            f"CREATE INDEX IF NOT EXISTS idx_{nome_tabela}_agente_id ON {nome_tabela} (agente_id);",
            f"CREATE INDEX IF NOT EXISTS idx_{nome_tabela}_categoria ON {nome_tabela} (categoria_juridica);",
            f"CREATE INDEX IF NOT EXISTS idx_{nome_tabela}_documento_tipo ON {nome_tabela} (documento_tipo);",
            f"CREATE INDEX IF NOT EXISTS idx_{nome_tabela}_data_criacao ON {nome_tabela} (data_criacao DESC);"
        ]
        
        for sql_index in indices_sql:
            try:
                cursor.execute(sql_index)
                indices_criados.append(sql_index.split('idx_')[1].split(' ')[0])
            except Exception as e:
                logger.warning(f"  ⚠️ Erro ao criar índice: {str(e)}")
        
        cursor.close()
        
        logger.info(f"✅ {nome_tabela}: {len(colunas_adicionadas)} colunas adicionadas, {len(indices_criados)} índices criados")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao corrigir estrutura de {nome_tabela}: {str(e)}")
        return False

def testar_funcionamento_tabela(conn, nome_tabela):
    """Testa inserção e busca na tabela corrigida"""
    try:
        cursor = conn.cursor()
        
        # Criar embedding de teste
        embedding_teste = [0.001] * 1536
        embedding_teste[0] = 1.0
        
        # Inserir documento de teste
        sql_insert = f"""
        INSERT INTO {nome_tabela} 
        (documento_id, documento_nome, documento_tipo, conteudo_texto, embedding, metadata, agente_id, categoria_juridica)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        
        cursor.execute(sql_insert, (
            f'TESTE_{nome_tabela.upper()}_001',
            'Documento de Teste Estrutural',
            'PDF',
            'Conteúdo de teste para validar funcionamento da base vetorial após correção estrutural.',
            embedding_teste,
            '{"teste": true, "correcao_estrutural": true}',
            1,
            nome_tabela.replace('embeddings_', '')
        ))
        
        doc_id = cursor.fetchone()[0]
        
        # Testar busca por similaridade
        cursor.execute(f"""
            SELECT id, documento_id, 1 - (embedding <=> %s) as similaridade
            FROM {nome_tabela} 
            WHERE id = %s;
        """, (embedding_teste, doc_id))
        
        resultado = cursor.fetchone()
        
        # Remover documento de teste
        cursor.execute(f"DELETE FROM {nome_tabela} WHERE id = %s;", (doc_id,))
        
        cursor.close()
        
        if resultado and resultado[2] > 0.9:
            logger.info(f"  ✅ Teste funcional bem-sucedido")
            return True
        else:
            logger.warning(f"  ⚠️ Teste funcional com resultado inesperado")
            return False
        
    except Exception as e:
        logger.error(f"  ❌ Erro no teste funcional: {str(e)}")
        return False

def corrigir_todas_bases_vetoriais():
    """Função principal para corrigir todas as bases vetoriais"""
    
    logger.info("🔧 Iniciando correção das bases vetoriais...")
    
    # Conectar ao banco
    conn = get_database_connection()
    if not conn:
        logger.error("❌ Falha na conexão com banco de dados")
        return False
    
    # Obter tabelas de embeddings
    tabelas = obter_tabelas_embeddings(conn)
    if not tabelas:
        logger.error("❌ Nenhuma tabela de embeddings encontrada")
        conn.close()
        return False
    
    logger.info(f"🔧 Processando {len(tabelas)} tabelas de embeddings")
    
    # Relatório de correção
    relatorio = {
        'tabelas_processadas': 0,
        'tabelas_corrigidas': 0,
        'tabelas_com_erro': 0,
        'tabelas_testadas': 0,
        'detalhes': []
    }
    
    for nome_tabela in tabelas:
        logger.info(f"🔧 Corrigindo estrutura: {nome_tabela}")
        
        resultado = {
            'tabela': nome_tabela,
            'correcao_ok': False,
            'teste_ok': False,
            'erro': None
        }
        
        # Corrigir estrutura
        if corrigir_estrutura_tabela(conn, nome_tabela):
            resultado['correcao_ok'] = True
            relatorio['tabelas_corrigidas'] += 1
            
            # Testar funcionamento
            if testar_funcionamento_tabela(conn, nome_tabela):
                resultado['teste_ok'] = True
                relatorio['tabelas_testadas'] += 1
                logger.info(f"✅ {nome_tabela}: Correção e teste bem-sucedidos")
            else:
                logger.warning(f"⚠️ {nome_tabela}: Corrigida mas falhou no teste")
        else:
            resultado['erro'] = 'Falha na correção estrutural'
            relatorio['tabelas_com_erro'] += 1
            logger.error(f"❌ {nome_tabela}: Falha na correção")
        
        relatorio['detalhes'].append(resultado)
        relatorio['tabelas_processadas'] += 1
    
    conn.close()
    
    # Gerar relatório final
    gerar_relatorio_final(relatorio)
    
    return relatorio['tabelas_com_erro'] == 0

def gerar_relatorio_final(relatorio):
    """Gera relatório final da correção"""
    
    logger.info("📊 RELATÓRIO FINAL DE CORREÇÃO DAS BASES VETORIAIS")
    logger.info("=" * 70)
    
    logger.info(f"Tabelas processadas: {relatorio['tabelas_processadas']}")
    logger.info(f"Tabelas corrigidas: {relatorio['tabelas_corrigidas']}")
    logger.info(f"Tabelas testadas: {relatorio['tabelas_testadas']}")
    logger.info(f"Tabelas com erro: {relatorio['tabelas_com_erro']}")
    
    if relatorio['tabelas_com_erro'] == 0:
        logger.info("🎉 TODAS AS BASES VETORIAIS FORAM CORRIGIDAS COM SUCESSO!")
    else:
        logger.warning("⚠️ ALGUMAS TABELAS TIVERAM PROBLEMAS:")
        
        for detalhe in relatorio['detalhes']:
            if detalhe['erro']:
                logger.warning(f"  ❌ {detalhe['tabela']}: {detalhe['erro']}")
    
    logger.info("=" * 70)
    logger.info("📋 RESUMO POR TABELA:")
    
    for detalhe in relatorio['detalhes']:
        if detalhe['teste_ok']:
            status = "✅ FUNCIONAL"
        elif detalhe['correcao_ok']:
            status = "⚠️ CORRIGIDA (teste falhou)"
        else:
            status = "❌ ERRO"
        
        logger.info(f"  {status} {detalhe['tabela']}")

if __name__ == "__main__":
    try:
        sucesso = corrigir_todas_bases_vetoriais()
        if sucesso:
            logger.info("✅ Correção concluída com sucesso!")
            exit(0)
        else:
            logger.error("❌ Correção concluída com problemas")
            exit(1)
    except Exception as e:
        logger.error(f"❌ Erro durante correção: {str(e)}")
        exit(1)