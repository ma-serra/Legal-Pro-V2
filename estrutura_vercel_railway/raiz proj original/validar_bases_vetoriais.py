#!/usr/bin/env python3
"""
Script para validar bases vetoriais de todos os agentes jurídicos.
Verifica se as tabelas estão criadas corretamente e seguem o padrão estrutural
para receber embeddings de arquivos e documentos.
"""

import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from main import db
from models import AgenteJuridico, CategoriaJuridica
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

def verificar_extensao_pgvector(conn):
    """Verifica se a extensão pgvector está instalada"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT EXISTS(
                SELECT 1 FROM pg_extension WHERE extname = 'vector'
            );
        """)
        
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

def obter_estrutura_tabela_esperada():
    """Define a estrutura esperada para tabelas de embeddings"""
    return {
        'colunas_obrigatorias': [
            ('id', 'SERIAL PRIMARY KEY'),
            ('documento_id', 'VARCHAR(255)'),
            ('documento_nome', 'TEXT'),
            ('documento_tipo', 'VARCHAR(100)'),
            ('conteudo_texto', 'TEXT'),
            ('embedding', 'vector(1536)'),  # OpenAI ada-002 dimensão
            ('metadata', 'JSONB'),
            ('data_criacao', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            ('data_atualizacao', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            ('agente_id', 'INTEGER'),
            ('categoria_juridica', 'VARCHAR(255)'),
            ('chunk_index', 'INTEGER DEFAULT 0'),
            ('chunk_total', 'INTEGER DEFAULT 1')
        ],
        'indices_obrigatorios': [
            'idx_{tabela}_embedding_cosine',
            'idx_{tabela}_documento_id',
            'idx_{tabela}_agente_id',
            'idx_{tabela}_categoria',
            'idx_{tabela}_documento_tipo'
        ]
    }

def obter_agentes_e_categorias():
    """Obtém todos os agentes ativos e suas categorias"""
    try:
        agentes = db.session.query(
            AgenteJuridico.id,
            AgenteJuridico.nome,
            AgenteJuridico.categoria_id,
            CategoriaJuridica.nome.label('categoria_nome')
        ).join(CategoriaJuridica).filter(
            AgenteJuridico.ativo == True,
            CategoriaJuridica.ativa == True
        ).all()
        
        logger.info(f"📊 Encontrados {len(agentes)} agentes ativos")
        return agentes
        
    except Exception as e:
        logger.error(f"Erro ao obter agentes: {str(e)}")
        return []

def gerar_nome_tabela_embedding(categoria_nome, agente_nome=None):
    """Gera nome padronizado para tabela de embedding"""
    # Normalizar nome da categoria
    categoria_normalizada = categoria_nome.lower()
    categoria_normalizada = categoria_normalizada.replace(' ', '_')
    categoria_normalizada = categoria_normalizada.replace('ã', 'a')
    categoria_normalizada = categoria_normalizada.replace('ç', 'c')
    categoria_normalizada = categoria_normalizada.replace('õ', 'o')
    categoria_normalizada = categoria_normalizada.replace('é', 'e')
    categoria_normalizada = categoria_normalizada.replace('á', 'a')
    categoria_normalizada = categoria_normalizada.replace('ê', 'e')
    categoria_normalizada = categoria_normalizada.replace('í', 'i')
    categoria_normalizada = categoria_normalizada.replace('ó', 'o')
    categoria_normalizada = categoria_normalizada.replace('ú', 'u')
    
    # Mapear nomes específicos
    mapeamento_categorias = {
        'direito_bancario': 'direito_bancario',
        'direito_securitario': 'direito_securitario', 
        'direito_trabalhista': 'direito_trabalhista',
        'direito_previdenciario': 'direito_previdenciario',
        'direito_tributario': 'direito_tributario',
        'direito_imobiliario': 'direito_imobiliario',
        'direito_digital': 'direito_digital',
        'direito_empresarial': 'direito_empresarial',
        'analise_de_riscos_juridicos': 'analise_riscos',
        'direito_penal': 'direito_penal',
        'direito_ambiental': 'direito_ambiental',
        'direito_do_consumidor': 'direito_consumidor',
        'direito_civil': 'direito_civil',
        'negociacao_e_conflitos': 'negocios_juridicos',
        'direito_de_familia': 'direito_familia',
        'direito_administrativo': 'direito_administrativo',
        'direito_constitucional': 'direito_constitucional'
    }
    
    nome_tabela = mapeamento_categorias.get(categoria_normalizada, categoria_normalizada)
    return f'embeddings_{nome_tabela}'

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
        
        estrutura_esperada = obter_estrutura_tabela_esperada()
        
        # Verificar colunas obrigatórias
        colunas_dict = {col[0]: col for col in colunas_existentes}
        colunas_faltantes = []
        colunas_incorretas = []
        
        for nome_col, tipo_esperado in estrutura_esperada['colunas_obrigatorias']:
            if nome_col not in colunas_dict:
                colunas_faltantes.append(nome_col)
            else:
                col_info = colunas_dict[nome_col]
                # Verificações básicas de tipo
                if 'vector' in tipo_esperado and col_info[1] != 'USER-DEFINED':
                    colunas_incorretas.append((nome_col, col_info[1], 'vector'))
                elif 'SERIAL' in tipo_esperado and col_info[1] not in ['integer', 'bigint']:
                    colunas_incorretas.append((nome_col, col_info[1], 'integer'))
        
        # Verificar índices importantes
        indices_dict = {idx[0]: idx[1] for idx in indices_existentes}
        indices_faltantes = []
        
        for idx_template in estrutura_esperada['indices_obrigatorios']:
            idx_nome = idx_template.replace('{tabela}', nome_tabela)
            if idx_nome not in indices_dict:
                # Verificar se existe índice similar
                idx_similar_existe = any(
                    idx_nome.split('_')[-1] in idx_existente 
                    for idx_existente in indices_dict.keys()
                )
                if not idx_similar_existe:
                    indices_faltantes.append(idx_nome)
        
        return {
            'colunas_existentes': len(colunas_existentes),
            'colunas_faltantes': colunas_faltantes,
            'colunas_incorretas': colunas_incorretas,
            'indices_existentes': len(indices_existentes),
            'indices_faltantes': indices_faltantes,
            'estrutura_valida': len(colunas_faltantes) == 0 and len(colunas_incorretas) == 0
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
        
        # Criar índices
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
        
        # Criar um embedding de teste (1536 dimensões com zeros)
        embedding_teste = [0.0] * 1536
        embedding_teste[0] = 1.0  # Definir primeiro valor como 1.0
        
        sql_insert = f"""
        INSERT INTO {nome_tabela} 
        (documento_id, documento_nome, documento_tipo, conteudo_texto, embedding, metadata, agente_id, categoria_juridica)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        
        cursor.execute(sql_insert, (
            'TEST_DOC_001',
            'Documento de Teste',
            'PDF',
            'Este é um documento de teste para validar a inserção de embeddings.',
            embedding_teste,
            '{"teste": true, "validacao": "estrutural"}',
            1,
            'teste'
        ))
        
        doc_id = cursor.fetchone()[0]
        
        # Remover o documento de teste
        cursor.execute(f"DELETE FROM {nome_tabela} WHERE id = %s;", (doc_id,))
        
        cursor.close()
        logger.info(f"✅ Teste de inserção em {nome_tabela} bem-sucedido")
        return True
        
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
    
    # Obter agentes
    agentes = obter_agentes_e_categorias()
    if not agentes:
        logger.error("❌ Nenhum agente encontrado")
        conn.close()
        return False
    
    # Agrupar por categoria para criar uma tabela por área jurídica
    categorias_agentes = {}
    for agente in agentes:
        categoria = agente.categoria_nome
        if categoria not in categorias_agentes:
            categorias_agentes[categoria] = []
        categorias_agentes[categoria].append(agente)
    
    logger.info(f"📊 Processando {len(categorias_agentes)} categorias jurídicas")
    
    # Relatório de validação
    relatorio = {
        'categorias_processadas': 0,
        'tabelas_existentes': 0,
        'tabelas_criadas': 0,
        'tabelas_com_problemas': 0,
        'tabelas_validadas': 0,
        'detalhes': []
    }
    
    for categoria_nome, agentes_categoria in categorias_agentes.items():
        nome_tabela = gerar_nome_tabela_embedding(categoria_nome)
        
        logger.info(f"🔍 Validando categoria: {categoria_nome} (tabela: {nome_tabela})")
        
        resultado_categoria = {
            'categoria': categoria_nome,
            'nome_tabela': nome_tabela,
            'total_agentes': len(agentes_categoria),
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
            if estrutura:
                if estrutura['estrutura_valida']:
                    resultado_categoria['estrutura_valida'] = True
                    
                    # Testar inserção
                    if testar_insercao_embedding(conn, nome_tabela):
                        resultado_categoria['teste_insercao_ok'] = True
                        relatorio['tabelas_validadas'] += 1
                        logger.info(f"✅ {categoria_nome}: Validação completa")
                    else:
                        resultado_categoria['problemas'].append("Falha no teste de inserção")
                        
                else:
                    problemas_estrutura = []
                    if estrutura['colunas_faltantes']:
                        problemas_estrutura.append(f"Colunas faltantes: {estrutura['colunas_faltantes']}")
                    if estrutura['colunas_incorretas']:
                        problemas_estrutura.append(f"Colunas incorretas: {estrutura['colunas_incorretas']}")
                    if estrutura['indices_faltantes']:
                        problemas_estrutura.append(f"Índices faltantes: {estrutura['indices_faltantes']}")
                    
                    resultado_categoria['problemas'].extend(problemas_estrutura)
                    relatorio['tabelas_com_problemas'] += 1
                    
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
            logger.info(f"     Problemas: {len(detalhe['problemas'])}")

if __name__ == "__main__":
    try:
        sucesso = validar_bases_vetoriais()
        if sucesso:
            logger.info("✅ Validação concluída com sucesso!")
        else:
            logger.error("❌ Validação concluída com problemas")
    except Exception as e:
        logger.error(f"❌ Erro durante validação: {str(e)}")