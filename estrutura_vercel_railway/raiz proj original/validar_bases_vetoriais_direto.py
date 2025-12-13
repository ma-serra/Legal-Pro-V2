#!/usr/bin/env python3
"""
Validação direta das bases vetoriais sem inicializar o sistema completo
"""

import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import json

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

def verificar_extensao_pgvector(conn):
    """Verifica se a extensão pgvector está instalada"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector');")
        pgvector_instalado = cursor.fetchone()[0]
        cursor.close()
        
        if pgvector_instalado:
            logger.info("✅ Extensão pgvector está instalada")
            return True
        else:
            logger.error("❌ Extensão pgvector NÃO está instalada")
            return False
            
    except Exception as e:
        logger.error(f"Erro ao verificar pgvector: {str(e)}")
        return False

def obter_categorias_juridicas(conn):
    """Obtém todas as categorias jurídicas ativas"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT c.id, c.nome, COUNT(a.id) as total_agentes
            FROM categoria_juridica c
            LEFT JOIN agente_juridico a ON c.id = a.categoria_id AND a.ativo = true
            WHERE c.ativa = true
            GROUP BY c.id, c.nome
            ORDER BY c.nome;
        """)
        
        categorias = cursor.fetchall()
        cursor.close()
        
        logger.info(f"📊 Encontradas {len(categorias)} categorias jurídicas ativas")
        return categorias
        
    except Exception as e:
        logger.error(f"Erro ao obter categorias: {str(e)}")
        return []

def gerar_nome_tabela_embedding(categoria_nome):
    """Gera nome padronizado para tabela de embedding"""
    # Mapeamento direto das categorias
    mapeamento_categorias = {
        'Direito Bancário': 'embeddings_direito_bancario',
        'Direito Securitário': 'embeddings_direito_securitario',
        'Direito Trabalhista': 'embeddings_direito_trabalhista',
        'Direito Previdenciário': 'embeddings_direito_previdenciario',
        'Direito Tributário': 'embeddings_direito_tributario',
        'Direito Imobiliário': 'embeddings_direito_imobiliario',
        'Direito Digital': 'embeddings_direito_digital',
        'Direito Empresarial': 'embeddings_direito_empresarial',
        'Análise de Riscos Jurídicos': 'embeddings_analise_riscos',
        'Direito Penal': 'embeddings_direito_penal',
        'Direito Ambiental': 'embeddings_direito_ambiental',
        'Direito do Consumidor': 'embeddings_direito_consumidor',
        'Direito Civil': 'embeddings_direito_civil',
        'Negociação e Conflitos': 'embeddings_negocios_juridicos',
        'Direito de Família': 'embeddings_direito_familia',
        'Direito Administrativo': 'embeddings_direito_administrativo',
        'Direito Constitucional': 'embeddings_direito_constitucional'
    }
    
    return mapeamento_categorias.get(categoria_nome, f"embeddings_{categoria_nome.lower().replace(' ', '_')}")

def verificar_tabela_existe(conn, nome_tabela):
    """Verifica se uma tabela existe no banco de dados"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            );
        """, (nome_tabela,))
        
        existe = cursor.fetchone()[0]
        cursor.close()
        return existe
        
    except Exception as e:
        logger.error(f"Erro ao verificar existência da tabela {nome_tabela}: {str(e)}")
        return False

def verificar_estrutura_tabela(conn, nome_tabela):
    """Verifica se a estrutura da tabela está correta"""
    try:
        cursor = conn.cursor()
        
        # Obter colunas da tabela
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = %s
            ORDER BY ordinal_position;
        """, (nome_tabela,))
        
        colunas_existentes = cursor.fetchall()
        
        # Obter índices da tabela
        cursor.execute("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = %s
            AND schemaname = 'public';
        """, (nome_tabela,))
        
        indices_existentes = cursor.fetchall()
        
        cursor.close()
        
        # Colunas essenciais esperadas
        colunas_essenciais = [
            'id', 'documento_id', 'conteudo_texto', 'embedding', 
            'data_criacao', 'agente_id', 'categoria_juridica'
        ]
        
        colunas_dict = {col[0]: col for col in colunas_existentes}
        colunas_faltantes = [col for col in colunas_essenciais if col not in colunas_dict]
        
        # Verificar se tem coluna embedding com tipo vector
        embedding_ok = False
        if 'embedding' in colunas_dict:
            embedding_col = colunas_dict['embedding']
            if embedding_col[1] == 'USER-DEFINED':  # Tipo vector aparece como USER-DEFINED
                embedding_ok = True
        
        return {
            'colunas_existentes': len(colunas_existentes),
            'colunas_faltantes': colunas_faltantes,
            'indices_existentes': len(indices_existentes),
            'embedding_ok': embedding_ok,
            'estrutura_valida': len(colunas_faltantes) == 0 and embedding_ok
        }
        
    except Exception as e:
        logger.error(f"Erro ao verificar estrutura da tabela {nome_tabela}: {str(e)}")
        return None

def criar_tabela_embedding(conn, nome_tabela):
    """Cria tabela de embedding com estrutura padrão"""
    try:
        cursor = conn.cursor()
        
        # SQL para criar a tabela
        sql_create = f"""
        CREATE TABLE IF NOT EXISTS {nome_tabela} (
            id SERIAL PRIMARY KEY,
            documento_id VARCHAR(255) NOT NULL,
            documento_nome TEXT,
            documento_tipo VARCHAR(100),
            conteudo_texto TEXT NOT NULL,
            embedding vector(1536),
            metadata JSONB DEFAULT '{{}}',
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            agente_id INTEGER,
            categoria_juridica VARCHAR(255),
            chunk_index INTEGER DEFAULT 0,
            chunk_total INTEGER DEFAULT 1
        );
        """
        
        cursor.execute(sql_create)
        
        # Criar índices essenciais
        indices_sql = [
            f"CREATE INDEX IF NOT EXISTS idx_{nome_tabela}_embedding_cosine ON {nome_tabela} USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);",
            f"CREATE INDEX IF NOT EXISTS idx_{nome_tabela}_documento_id ON {nome_tabela} (documento_id);",
            f"CREATE INDEX IF NOT EXISTS idx_{nome_tabela}_agente_id ON {nome_tabela} (agente_id);",
            f"CREATE INDEX IF NOT EXISTS idx_{nome_tabela}_categoria ON {nome_tabela} (categoria_juridica);",
            f"CREATE INDEX IF NOT EXISTS idx_{nome_tabela}_data_criacao ON {nome_tabela} (data_criacao DESC);"
        ]
        
        for sql_index in indices_sql:
            try:
                cursor.execute(sql_index)
            except Exception as e:
                logger.warning(f"Aviso ao criar índice: {str(e)}")
        
        cursor.close()
        logger.info(f"✅ Tabela {nome_tabela} criada com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabela {nome_tabela}: {str(e)}")
        return False

def testar_insercao_embedding(conn, nome_tabela):
    """Testa inserção de um embedding de exemplo"""
    try:
        cursor = conn.cursor()
        
        # Criar um embedding de teste (1536 dimensões)
        embedding_teste = [0.001] * 1536
        embedding_teste[0] = 1.0
        
        sql_insert = f"""
        INSERT INTO {nome_tabela} 
        (documento_id, documento_nome, documento_tipo, conteudo_texto, embedding, metadata, agente_id, categoria_juridica)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        
        cursor.execute(sql_insert, (
            'TESTE_VALIDACAO_001',
            'Documento de Teste Estrutural',
            'PDF',
            'Este é um documento de teste para validar a capacidade de inserção de embeddings na base vetorial.',
            embedding_teste,
            json.dumps({"teste": True, "validacao": "estrutural", "dimensao": 1536}),
            1,
            'teste_estrutural'
        ))
        
        doc_id = cursor.fetchone()[0]
        
        # Testar busca por similaridade
        cursor.execute(f"""
            SELECT id, documento_id, 1 - (embedding <=> %s) as similaridade
            FROM {nome_tabela} 
            WHERE id = %s;
        """, (embedding_teste, doc_id))
        
        resultado = cursor.fetchone()
        
        # Remover o documento de teste
        cursor.execute(f"DELETE FROM {nome_tabela} WHERE id = %s;", (doc_id,))
        
        cursor.close()
        
        if resultado and resultado[2] > 0.9:  # Similaridade alta
            logger.info(f"✅ Teste de inserção e busca em {nome_tabela} bem-sucedido")
            return True
        else:
            logger.warning(f"⚠️ Teste de similaridade em {nome_tabela} com resultado inesperado")
            return False
        
    except Exception as e:
        logger.error(f"❌ Erro no teste de inserção em {nome_tabela}: {str(e)}")
        return False

def validar_bases_vetoriais():
    """Função principal para validar todas as bases vetoriais"""
    
    logger.info("🚀 Iniciando validação das bases vetoriais...")
    
    # Conectar ao banco
    conn = get_database_connection()
    if not conn:
        logger.error("❌ Falha na conexão com banco de dados")
        return False
    
    # Verificar pgvector
    if not verificar_extensao_pgvector(conn):
        logger.error("❌ pgvector não está disponível")
        conn.close()
        return False
    
    # Obter categorias
    categorias = obter_categorias_juridicas(conn)
    if not categorias:
        logger.error("❌ Nenhuma categoria encontrada")
        conn.close()
        return False
    
    logger.info(f"📊 Processando {len(categorias)} categorias jurídicas")
    
    # Relatório de validação
    relatorio = {
        'categorias_processadas': 0,
        'tabelas_existentes': 0,
        'tabelas_criadas': 0,
        'tabelas_com_problemas': 0,
        'tabelas_validadas': 0,
        'detalhes': []
    }
    
    for categoria_id, categoria_nome, total_agentes in categorias:
        nome_tabela = gerar_nome_tabela_embedding(categoria_nome)
        
        logger.info(f"🔍 Validando: {categoria_nome} ({total_agentes} agentes) → {nome_tabela}")
        
        resultado_categoria = {
            'categoria': categoria_nome,
            'nome_tabela': nome_tabela,
            'total_agentes': total_agentes,
            'tabela_existe': False,
            'estrutura_valida': False,
            'teste_insercao_ok': False,
            'problemas': []
        }
        
        # Verificar se tabela existe
        if verificar_tabela_existe(conn, nome_tabela):
            resultado_categoria['tabela_existe'] = True
            relatorio['tabelas_existentes'] += 1
            
            # Verificar estrutura
            estrutura = verificar_estrutura_tabela(conn, nome_tabela)
            if estrutura and estrutura['estrutura_valida']:
                resultado_categoria['estrutura_valida'] = True
                
                # Testar inserção
                if testar_insercao_embedding(conn, nome_tabela):
                    resultado_categoria['teste_insercao_ok'] = True
                    relatorio['tabelas_validadas'] += 1
                    logger.info(f"✅ {categoria_nome}: Validação completa")
                else:
                    resultado_categoria['problemas'].append("Falha no teste de inserção")
                    relatorio['tabelas_com_problemas'] += 1
                    
            else:
                if estrutura:
                    if estrutura['colunas_faltantes']:
                        resultado_categoria['problemas'].append(f"Colunas faltantes: {estrutura['colunas_faltantes']}")
                    if not estrutura['embedding_ok']:
                        resultado_categoria['problemas'].append("Coluna embedding não está configurada corretamente")
                else:
                    resultado_categoria['problemas'].append("Erro ao analisar estrutura")
                relatorio['tabelas_com_problemas'] += 1
                
        else:
            # Criar tabela
            logger.info(f"📝 Criando tabela {nome_tabela}...")
            if criar_tabela_embedding(conn, nome_tabela):
                resultado_categoria['tabela_existe'] = True
                resultado_categoria['estrutura_valida'] = True
                relatorio['tabelas_criadas'] += 1
                
                # Testar inserção na nova tabela
                if testar_insercao_embedding(conn, nome_tabela):
                    resultado_categoria['teste_insercao_ok'] = True
                    relatorio['tabelas_validadas'] += 1
                    logger.info(f"✅ {categoria_nome}: Tabela criada e validada")
                else:
                    resultado_categoria['problemas'].append("Falha no teste de inserção na nova tabela")
                    relatorio['tabelas_com_problemas'] += 1
            else:
                resultado_categoria['problemas'].append("Falha na criação da tabela")
                relatorio['tabelas_com_problemas'] += 1
        
        relatorio['detalhes'].append(resultado_categoria)
        relatorio['categorias_processadas'] += 1
    
    conn.close()
    
    # Gerar relatório final
    gerar_relatorio_final(relatorio)
    
    return relatorio['tabelas_com_problemas'] == 0

def gerar_relatorio_final(relatorio):
    """Gera relatório final da validação"""
    
    logger.info("📊 RELATÓRIO FINAL DE VALIDAÇÃO DAS BASES VETORIAIS")
    logger.info("=" * 70)
    
    logger.info(f"Categorias processadas: {relatorio['categorias_processadas']}")
    logger.info(f"Tabelas já existentes: {relatorio['tabelas_existentes']}")
    logger.info(f"Tabelas criadas: {relatorio['tabelas_criadas']}")
    logger.info(f"Tabelas validadas: {relatorio['tabelas_validadas']}")
    logger.info(f"Tabelas com problemas: {relatorio['tabelas_com_problemas']}")
    
    if relatorio['tabelas_com_problemas'] == 0:
        logger.info("🎉 TODAS AS BASES VETORIAIS ESTÃO FUNCIONAIS!")
    else:
        logger.warning("⚠️ PROBLEMAS ENCONTRADOS:")
        
        for detalhe in relatorio['detalhes']:
            if detalhe['problemas']:
                logger.warning(f"  ❌ {detalhe['categoria']}:")
                for problema in detalhe['problemas']:
                    logger.warning(f"     - {problema}")
    
    logger.info("=" * 70)
    logger.info("📋 RESUMO POR CATEGORIA:")
    
    for detalhe in relatorio['detalhes']:
        status = "✅" if detalhe['teste_insercao_ok'] else "❌"
        logger.info(f"  {status} {detalhe['categoria']} ({detalhe['total_agentes']} agentes)")
        logger.info(f"     Tabela: {detalhe['nome_tabela']}")
        if detalhe['problemas']:
            logger.info(f"     Problemas: {', '.join(detalhe['problemas'])}")

if __name__ == "__main__":
    try:
        sucesso = validar_bases_vetoriais()
        if sucesso:
            logger.info("✅ Validação concluída com sucesso!")
            exit(0)
        else:
            logger.error("❌ Validação concluída com problemas")
            exit(1)
    except Exception as e:
        logger.error(f"❌ Erro durante validação: {str(e)}")
        exit(1)