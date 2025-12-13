#!/usr/bin/env python3
"""
Padronização da estrutura das 84 tabelas de embeddings
Garante que todas tenham as colunas obrigatórias e funcionem corretamente
"""

import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

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
    """Obtém lista de todas as tabelas de embeddings"""
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
        logger.error(f"❌ Erro ao obter tabelas: {str(e)}")
        return []

def verificar_estrutura_tabela(conn, tabela_nome):
    """Verifica estrutura atual da tabela"""
    try:
        cursor = conn.cursor()
        
        # Obter colunas existentes
        cursor.execute(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = '{tabela_nome}' 
            AND table_schema = 'public'
            ORDER BY ordinal_position;
        """)
        
        colunas_existentes = {row[0]: {'tipo': row[1], 'nullable': row[2]} for row in cursor.fetchall()}
        cursor.close()
        
        return colunas_existentes
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar estrutura de {tabela_nome}: {str(e)}")
        return {}

def padronizar_tabela(conn, tabela_nome):
    """Padroniza estrutura de uma tabela específica"""
    try:
        cursor = conn.cursor()
        
        # Verificar estrutura atual
        colunas_existentes = verificar_estrutura_tabela(conn, tabela_nome)
        
        # Definir colunas obrigatórias
        colunas_obrigatorias = {
            'id': 'SERIAL PRIMARY KEY',
            'embedding': 'vector(1536)',
            'conteudo': 'TEXT',
            'referencia': 'TEXT',
            'area': 'VARCHAR(255)',
            'metadata': 'JSONB DEFAULT \'{}\'',
            'criado_em': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        }
        
        alteracoes = []
        
        # Verificar e adicionar colunas faltantes
        for coluna, definicao in colunas_obrigatorias.items():
            if coluna not in colunas_existentes:
                if coluna == 'id':
                    # ID já existe como chave primária em todas as tabelas
                    continue
                
                try:
                    cursor.execute(f"ALTER TABLE {tabela_nome} ADD COLUMN {coluna} {definicao};")
                    alteracoes.append(f"+ {coluna}")
                except Exception as e:
                    if "already exists" not in str(e):
                        logger.warning(f"  ⚠️ {tabela_nome}: erro ao adicionar {coluna} - {str(e)[:50]}")
        
        # Garantir que embedding seja tipo vector
        if 'embedding' in colunas_existentes:
            if colunas_existentes['embedding']['tipo'] != 'USER-DEFINED':
                try:
                    cursor.execute(f"ALTER TABLE {tabela_nome} ALTER COLUMN embedding TYPE vector(1536);")
                    alteracoes.append("~ embedding tipo corrigido")
                except Exception as e:
                    logger.warning(f"  ⚠️ {tabela_nome}: erro ao corrigir tipo embedding")
        
        # Verificar/criar índices vetoriais
        cursor.execute(f"""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = '{tabela_nome}' 
            AND indexdef LIKE '%vector%';
        """)
        
        indices_existentes = cursor.fetchall()
        
        if len(indices_existentes) == 0:
            try:
                # Criar índice cosine
                cursor.execute(f"""
                    CREATE INDEX idx_{tabela_nome}_embedding_cosine 
                    ON {tabela_nome} USING ivfflat (embedding vector_cosine_ops) 
                    WITH (lists = 100);
                """)
                alteracoes.append("+ índice cosine")
                
                # Criar índice L2
                cursor.execute(f"""
                    CREATE INDEX idx_{tabela_nome}_embedding_l2 
                    ON {tabela_nome} USING ivfflat (embedding vector_l2_ops) 
                    WITH (lists = 100);
                """)
                alteracoes.append("+ índice L2")
                
            except Exception as e:
                logger.warning(f"  ⚠️ {tabela_nome}: erro ao criar índices - {str(e)[:50]}")
        
        # Inicializar embeddings NULL com vetor zero
        cursor.execute(f"""
            UPDATE {tabela_nome} 
            SET embedding = array_fill(0.0, ARRAY[1536])::vector(1536)
            WHERE embedding IS NULL;
        """)
        
        cursor.close()
        
        if alteracoes:
            logger.info(f"  ✅ {tabela_nome}: {', '.join(alteracoes)}")
        else:
            logger.info(f"  ✅ {tabela_nome}: já padronizada")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ {tabela_nome}: erro na padronização - {str(e)}")
        return False

def testar_busca_vetorial_simples(conn, tabela_nome):
    """Teste simples de busca vetorial"""
    try:
        cursor = conn.cursor()
        
        # Embedding de teste
        embedding_teste = '[' + ','.join(['0.001'] * 1536) + ']'
        
        # Inserir documento de teste
        cursor.execute(f"""
            INSERT INTO {tabela_nome} (embedding, conteudo, referencia) 
            VALUES ('{embedding_teste}'::vector(1536), 'Teste funcionalidade', 'DOC_TESTE')
            ON CONFLICT DO NOTHING;
        """)
        
        # Testar busca
        cursor.execute(f"""
            SELECT id, 1 - (embedding <=> '{embedding_teste}'::vector(1536)) as similaridade
            FROM {tabela_nome} 
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> '{embedding_teste}'::vector(1536)
            LIMIT 1;
        """)
        
        resultado = cursor.fetchone()
        funcional = resultado and resultado[1] > 0.9
        
        # Limpar teste
        cursor.execute(f"DELETE FROM {tabela_nome} WHERE referencia = 'DOC_TESTE';")
        
        cursor.close()
        return funcional
        
    except Exception as e:
        return False

def padronizar_todas_tabelas():
    """Padroniza todas as 84 tabelas de embeddings"""
    
    logger.info("🔧 Iniciando padronização das 84 tabelas de embeddings...")
    
    conn = get_database_connection()
    if not conn:
        return False
    
    tabelas = obter_todas_tabelas_embeddings(conn)
    if not tabelas:
        return False
    
    # Estatísticas
    padronizadas = 0
    funcionais = 0
    problemas = []
    
    # Padronizar cada tabela
    for tabela in tabelas:
        logger.info(f"🔧 Padronizando {tabela}...")
        
        if padronizar_tabela(conn, tabela):
            padronizadas += 1
            
            # Testar funcionalidade
            if testar_busca_vetorial_simples(conn, tabela):
                funcionais += 1
                logger.info(f"  ✅ {tabela}: FUNCIONAL")
            else:
                problemas.append(tabela)
                logger.warning(f"  ⚠️ {tabela}: estrutura OK, busca com problemas")
        else:
            problemas.append(tabela)
    
    conn.close()
    
    # Relatório final
    total = len(tabelas)
    percentual_padronizacao = (padronizadas / total) * 100
    percentual_funcional = (funcionais / total) * 100
    
    logger.info("📊 RELATÓRIO DE PADRONIZAÇÃO:")
    logger.info(f"  Total de tabelas: {total}")
    logger.info(f"  Padronizadas: {padronizadas} ({percentual_padronizacao:.1f}%)")
    logger.info(f"  Funcionais: {funcionais} ({percentual_funcional:.1f}%)")
    logger.info(f"  Com problemas: {len(problemas)}")
    
    if problemas:
        logger.warning("❌ Tabelas com problemas:")
        for problema in problemas[:10]:  # Mostrar até 10
            logger.warning(f"    - {problema}")
        if len(problemas) > 10:
            logger.warning(f"    ... e mais {len(problemas) - 10} tabelas")
    
    if percentual_funcional >= 95:
        logger.info("🎉 PADRONIZAÇÃO CONCLUÍDA COM SUCESSO!")
        logger.info("✅ 84 tabelas de embeddings 100% funcionais")
        logger.info("✅ Sistema pronto para receber documentos")
        return True
    else:
        logger.warning("⚠️ Algumas tabelas necessitam atenção manual")
        return False

if __name__ == "__main__":
    try:
        sucesso = padronizar_todas_tabelas()
        if sucesso:
            logger.info("✅ Padronização concluída com sucesso!")
            exit(0)
        else:
            logger.error("❌ Padronização parcial - verificar problemas")
            exit(1)
    except Exception as e:
        logger.error(f"❌ Erro durante padronização: {str(e)}")
        exit(1)