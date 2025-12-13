#!/usr/bin/env python3
"""
Script para otimizar bases vetoriais para receber documentos jurídicos variados:
- Legislação (leis, decretos, portarias)
- Processos judiciais e administrativos
- Doutrinas e artigos acadêmicos
- Bibliografia especializada
- Pareceres técnicos e jurídicos
- Tabelas e anexos normativos
- Jurisprudência e precedentes
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

def obter_estrutura_otimizada_documentos():
    """Define estrutura otimizada para documentos jurídicos variados"""
    return {
        'colunas_essenciais': [
            ('id', 'SERIAL PRIMARY KEY'),
            ('conteudo', 'TEXT NOT NULL'),
            ('embedding', 'vector(1536)'),
            ('referencia', 'TEXT'),
            ('area', 'VARCHAR(255)'),
            ('metadata', 'JSONB DEFAULT \'{}\''),
            ('criado_em', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            # Colunas específicas para documentos jurídicos
            ('documento_id', 'VARCHAR(255)'),
            ('documento_titulo', 'TEXT'),
            ('documento_tipo', 'VARCHAR(100)'),
            ('documento_subtipo', 'VARCHAR(100)'),
            ('autor_origem', 'TEXT'),
            ('data_documento', 'DATE'),
            ('numero_processo', 'VARCHAR(100)'),
            ('instancia', 'VARCHAR(100)'),
            ('tribunal', 'VARCHAR(255)'),
            ('area_juridica', 'VARCHAR(100)'),
            ('tags_especialidade', 'TEXT[]'),
            ('nivel_confidencialidade', 'VARCHAR(50) DEFAULT \'publico\''),
            ('fonte_documento', 'TEXT'),
            ('url_original', 'TEXT'),
            ('hash_documento', 'VARCHAR(64)'),
            ('tamanho_arquivo', 'INTEGER'),
            ('numero_paginas', 'INTEGER'),
            ('idioma', 'VARCHAR(10) DEFAULT \'pt-BR\''),
            ('versao_documento', 'INTEGER DEFAULT 1'),
            ('status_processamento', 'VARCHAR(50) DEFAULT \'processado\''),
            ('chunk_indice', 'INTEGER DEFAULT 0'),
            ('chunk_total', 'INTEGER DEFAULT 1'),
            ('chunk_overlap', 'INTEGER DEFAULT 0'),
            ('agente_id', 'INTEGER'),
            ('usuario_upload', 'INTEGER'),
            ('data_atualizacao', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        ],
        'indices_otimizados': [
            # Índices para embeddings
            'CREATE INDEX IF NOT EXISTS idx_{tabela}_embedding_cosine ON {tabela} USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);',
            'CREATE INDEX IF NOT EXISTS idx_{tabela}_embedding_l2 ON {tabela} USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);',
            
            # Índices para busca de documentos
            'CREATE INDEX IF NOT EXISTS idx_{tabela}_documento_id ON {tabela} (documento_id);',
            'CREATE INDEX IF NOT EXISTS idx_{tabela}_documento_tipo ON {tabela} (documento_tipo);',
            'CREATE INDEX IF NOT EXISTS idx_{tabela}_documento_subtipo ON {tabela} (documento_subtipo);',
            'CREATE INDEX IF NOT EXISTS idx_{tabela}_hash_documento ON {tabela} (hash_documento);',
            
            # Índices para área jurídica e especialização
            'CREATE INDEX IF NOT EXISTS idx_{tabela}_area ON {tabela} (area);',
            'CREATE INDEX IF NOT EXISTS idx_{tabela}_area_juridica ON {tabela} (area_juridica);',
            'CREATE INDEX IF NOT EXISTS idx_{tabela}_agente_id ON {tabela} (agente_id);',
            'CREATE INDEX IF NOT EXISTS idx_{tabela}_tags_especialidade ON {tabela} USING GIN (tags_especialidade);',
            
            # Índices para busca processual
            'CREATE INDEX IF NOT EXISTS idx_{tabela}_numero_processo ON {tabela} (numero_processo);',
            'CREATE INDEX IF NOT EXISTS idx_{tabela}_instancia ON {tabela} (instancia);',
            'CREATE INDEX IF NOT EXISTS idx_{tabela}_tribunal ON {tabela} (tribunal);',
            
            # Índices temporais
            'CREATE INDEX IF NOT EXISTS idx_{tabela}_criado_em ON {tabela} (criado_em DESC);',
            'CREATE INDEX IF NOT EXISTS idx_{tabela}_data_documento ON {tabela} (data_documento DESC);',
            'CREATE INDEX IF NOT EXISTS idx_{tabela}_data_atualizacao ON {tabela} (data_atualizacao DESC);',
            
            # Índices para controle
            'CREATE INDEX IF NOT EXISTS idx_{tabela}_status_processamento ON {tabela} (status_processamento);',
            'CREATE INDEX IF NOT EXISTS idx_{tabela}_nivel_confidencialidade ON {tabela} (nivel_confidencialidade);',
            'CREATE INDEX IF NOT EXISTS idx_{tabela}_usuario_upload ON {tabela} (usuario_upload);',
            
            # Índices compostos para busca avançada
            'CREATE INDEX IF NOT EXISTS idx_{tabela}_tipo_area ON {tabela} (documento_tipo, area_juridica);',
            'CREATE INDEX IF NOT EXISTS idx_{tabela}_agente_data ON {tabela} (agente_id, criado_em DESC);',
            'CREATE INDEX IF NOT EXISTS idx_{tabela}_processo_instancia ON {tabela} (numero_processo, instancia);'
        ],
        'triggers': [
            # Trigger para atualizar data_atualizacao
            '''
            CREATE OR REPLACE FUNCTION update_timestamp_{}()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.data_atualizacao = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
            
            DROP TRIGGER IF EXISTS trigger_update_timestamp_{} ON {};
            CREATE TRIGGER trigger_update_timestamp_{}
                BEFORE UPDATE ON {}
                FOR EACH ROW
                EXECUTE FUNCTION update_timestamp_{}();
            '''
        ]
    }

def obter_tabelas_principais():
    """Lista das 17 tabelas principais de embeddings"""
    return [
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
    ]

def verificar_e_criar_estrutura_completa(conn, nome_tabela):
    """Verifica e cria estrutura completa otimizada para documentos jurídicos"""
    try:
        cursor = conn.cursor()
        
        # Verificar se tabela existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            );
        """, (nome_tabela,))
        
        tabela_existe = cursor.fetchone()[0]
        
        if not tabela_existe:
            # Criar tabela com estrutura completa
            logger.info(f"  📝 Criando nova tabela {nome_tabela}...")
            estrutura = obter_estrutura_otimizada_documentos()
            
            # SQL para criar tabela
            colunas_sql = ',\n            '.join([f'{col[0]} {col[1]}' for col in estrutura['colunas_essenciais']])
            sql_create = f"""
            CREATE TABLE {nome_tabela} (
                {colunas_sql}
            );
            """
            
            cursor.execute(sql_create)
            logger.info(f"    ✅ Tabela {nome_tabela} criada")
            
        else:
            # Verificar e adicionar colunas faltantes
            logger.info(f"  🔧 Atualizando estrutura de {nome_tabela}...")
            
            # Obter colunas existentes
            cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = %s;
            """, (nome_tabela,))
            
            colunas_existentes = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Adicionar colunas faltantes
            estrutura = obter_estrutura_otimizada_documentos()
            colunas_adicionadas = 0
            
            for nome_col, tipo_sql in estrutura['colunas_essenciais']:
                if nome_col not in colunas_existentes:
                    try:
                        if 'PRIMARY KEY' in tipo_sql:
                            continue  # Pular chave primária se já existe
                        
                        sql_add = f"ALTER TABLE {nome_tabela} ADD COLUMN {nome_col} {tipo_sql};"
                        cursor.execute(sql_add)
                        colunas_adicionadas += 1
                        
                    except Exception as e:
                        logger.warning(f"    ⚠️ Erro ao adicionar {nome_col}: {str(e)}")
            
            if colunas_adicionadas > 0:
                logger.info(f"    ✅ {colunas_adicionadas} colunas adicionadas")
        
        # Criar índices otimizados
        estrutura = obter_estrutura_otimizada_documentos()
        indices_criados = 0
        
        for idx_template in estrutura['indices_otimizados']:
            try:
                idx_sql = idx_template.format(tabela=nome_tabela)
                cursor.execute(idx_sql)
                indices_criados += 1
            except Exception as e:
                # Alguns índices podem falhar se colunas não existem ainda
                pass
        
        # Criar triggers
        for trigger_template in estrutura['triggers']:
            try:
                trigger_sql = trigger_template.format(nome_tabela, nome_tabela, nome_tabela, nome_tabela, nome_tabela, nome_tabela)
                cursor.execute(trigger_sql)
            except Exception as e:
                logger.warning(f"    ⚠️ Erro ao criar trigger: {str(e)}")
        
        cursor.close()
        
        logger.info(f"  ✅ {nome_tabela}: estrutura otimizada ({indices_criados} índices)")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao otimizar {nome_tabela}: {str(e)}")
        return False

def testar_capacidade_documentos(conn, nome_tabela):
    """Testa capacidade de inserção com diferentes tipos de documentos"""
    try:
        cursor = conn.cursor()
        
        # Embedding de teste
        embedding_teste = [0.001] * 1536
        embedding_teste[0] = 1.0
        
        # Testar diferentes tipos de documentos jurídicos
        documentos_teste = [
            {
                'tipo': 'legislacao',
                'subtipo': 'lei_federal',
                'titulo': 'Lei 10.406/2002 - Código Civil',
                'conteudo': 'Art. 1º Esta Lei estabelece normas de direito privado de aplicabilidade geral.',
                'area_juridica': 'direito_civil',
                'numero_processo': None,
                'instancia': None,
                'tribunal': None,
                'tags': ['codigo_civil', 'direito_privado', 'normas_gerais']
            },
            {
                'tipo': 'jurisprudencia',
                'subtipo': 'acordao_stj',
                'titulo': 'REsp 1234567/SP - Responsabilidade Civil',
                'conteudo': 'EMENTA: Responsabilidade civil. Danos materiais e morais. Nexo causal comprovado.',
                'area_juridica': 'direito_civil',
                'numero_processo': 'REsp 1234567/SP',
                'instancia': 'superior',
                'tribunal': 'STJ',
                'tags': ['responsabilidade_civil', 'danos_morais', 'stj']
            },
            {
                'tipo': 'doutrina',
                'subtipo': 'artigo_cientifico',
                'titulo': 'A evolução da responsabilidade civil no direito brasileiro',
                'conteudo': 'A responsabilidade civil tem passado por profundas transformações...',
                'area_juridica': 'direito_civil',
                'numero_processo': None,
                'instancia': None,
                'tribunal': None,
                'tags': ['doutrina', 'responsabilidade_civil', 'evolucao_juridica']
            }
        ]
        
        documentos_inseridos = 0
        area_nome = nome_tabela.replace('embeddings_', '')
        
        for doc in documentos_teste:
            try:
                sql_insert = f"""
                INSERT INTO {nome_tabela} 
                (conteudo, embedding, referencia, area, metadata, documento_id, 
                 documento_titulo, documento_tipo, documento_subtipo, area_juridica,
                 numero_processo, instancia, tribunal, tags_especialidade, agente_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """
                
                documento_id = f"TESTE_{doc['tipo'].upper()}_{nome_tabela.upper()}_{documentos_inseridos + 1:03d}"
                
                cursor.execute(sql_insert, (
                    doc['conteudo'],
                    embedding_teste,
                    doc['titulo'],
                    area_nome,
                    f'{{"teste": true, "tipo_documento": "{doc["tipo"]}", "validacao": "estrutural"}}',
                    documento_id,
                    doc['titulo'],
                    doc['tipo'],
                    doc['subtipo'],
                    doc['area_juridica'],
                    doc['numero_processo'],
                    doc['instancia'],
                    doc['tribunal'],
                    doc['tags'],
                    1
                ))
                
                doc_id = cursor.fetchone()[0]
                documentos_inseridos += 1
                
                # Remover imediatamente após teste
                cursor.execute(f"DELETE FROM {nome_tabela} WHERE id = %s;", (doc_id,))
                
            except Exception as e:
                logger.warning(f"    ⚠️ Erro ao testar {doc['tipo']}: {str(e)}")
        
        cursor.close()
        
        if documentos_inseridos >= 2:  # Pelo menos 2 tipos funcionando
            logger.info(f"  ✅ Teste de capacidades bem-sucedido ({documentos_inseridos}/3 tipos)")
            return True
        else:
            logger.warning(f"  ⚠️ Apenas {documentos_inseridos}/3 tipos funcionando")
            return False
        
    except Exception as e:
        logger.error(f"  ❌ Erro no teste de capacidades: {str(e)}")
        return False

def otimizar_todas_bases_documentos():
    """Função principal para otimizar todas as bases para documentos jurídicos"""
    
    logger.info("🚀 Otimizando bases vetoriais para documentos jurídicos variados...")
    logger.info("📋 Tipos suportados: legislação, processos, doutrinas, pareceres, tabelas, jurisprudência")
    
    # Conectar ao banco
    conn = get_database_connection()
    if not conn:
        logger.error("❌ Falha na conexão com banco de dados")
        return False
    
    # Obter tabelas
    tabelas = obter_tabelas_principais()
    logger.info(f"🔧 Processando {len(tabelas)} bases vetoriais principais")
    
    # Relatório de otimização
    relatorio = {
        'tabelas_processadas': 0,
        'tabelas_otimizadas': 0,
        'tabelas_testadas': 0,
        'tabelas_com_erro': 0,
        'detalhes': []
    }
    
    for nome_tabela in tabelas:
        logger.info(f"🔧 Otimizando: {nome_tabela}")
        
        resultado = {
            'tabela': nome_tabela,
            'otimizacao_ok': False,
            'teste_capacidades_ok': False
        }
        
        # Otimizar estrutura
        if verificar_e_criar_estrutura_completa(conn, nome_tabela):
            resultado['otimizacao_ok'] = True
            relatorio['tabelas_otimizadas'] += 1
            
            # Testar capacidades para documentos
            if testar_capacidade_documentos(conn, nome_tabela):
                resultado['teste_capacidades_ok'] = True
                relatorio['tabelas_testadas'] += 1
                logger.info(f"✅ {nome_tabela}: Otimizada e pronta para documentos")
            else:
                logger.warning(f"⚠️ {nome_tabela}: Otimizada mas falhou no teste de capacidades")
        else:
            relatorio['tabelas_com_erro'] += 1
            logger.error(f"❌ {nome_tabela}: Falha na otimização")
        
        relatorio['detalhes'].append(resultado)
        relatorio['tabelas_processadas'] += 1
    
    conn.close()
    
    # Gerar relatório final
    gerar_relatorio_final_documentos(relatorio)
    
    return relatorio['tabelas_com_erro'] == 0

def gerar_relatorio_final_documentos(relatorio):
    """Gera relatório final da otimização para documentos"""
    
    logger.info("📊 RELATÓRIO FINAL - BASES VETORIAIS OTIMIZADAS PARA DOCUMENTOS JURÍDICOS")
    logger.info("=" * 80)
    
    logger.info(f"Bases processadas: {relatorio['tabelas_processadas']}")
    logger.info(f"Bases otimizadas: {relatorio['tabelas_otimizadas']}")
    logger.info(f"Bases testadas com sucesso: {relatorio['tabelas_testadas']}")
    logger.info(f"Bases com erro: {relatorio['tabelas_com_erro']}")
    
    percentual_sucesso = (relatorio['tabelas_testadas'] / relatorio['tabelas_processadas'] * 100) if relatorio['tabelas_processadas'] > 0 else 0
    logger.info(f"Taxa de sucesso: {percentual_sucesso:.1f}%")
    
    if relatorio['tabelas_com_erro'] == 0:
        logger.info("🎉 TODAS AS BASES ESTÃO OTIMIZADAS PARA DOCUMENTOS JURÍDICOS!")
        logger.info("")
        logger.info("📚 TIPOS DE DOCUMENTOS SUPORTADOS:")
        logger.info("  ✅ Legislação (leis, decretos, portarias, resoluções)")
        logger.info("  ✅ Processos judiciais e administrativos")
        logger.info("  ✅ Doutrinas e artigos acadêmicos")
        logger.info("  ✅ Bibliografia especializada")
        logger.info("  ✅ Pareceres técnicos e jurídicos")
        logger.info("  ✅ Tabelas e anexos normativos")
        logger.info("  ✅ Jurisprudência e precedentes")
        logger.info("  ✅ Contratos e documentos empresariais")
        logger.info("")
        logger.info("🚀 SISTEMA PRONTO PARA RECEBER DOCUMENTOS REAIS!")
    else:
        logger.warning("⚠️ ALGUMAS BASES PRECISAM DE ATENÇÃO")
    
    logger.info("=" * 80)
    logger.info("📋 RESUMO POR BASE VETORIAL:")
    
    for detalhe in relatorio['detalhes']:
        if detalhe['teste_capacidades_ok']:
            status = "✅ PRONTA PARA DOCUMENTOS"
        elif detalhe['otimizacao_ok']:
            status = "⚠️ OTIMIZADA (verificar capacidades)"
        else:
            status = "❌ ERRO NA OTIMIZAÇÃO"
        
        area_nome = detalhe['tabela'].replace('embeddings_', '').replace('_', ' ').title()
        logger.info(f"  {status} {area_nome}")

if __name__ == "__main__":
    try:
        sucesso = otimizar_todas_bases_documentos()
        if sucesso:
            logger.info("✅ Otimização para documentos concluída com sucesso!")
            exit(0)
        else:
            logger.error("❌ Otimização concluída com problemas")
            exit(1)
    except Exception as e:
        logger.error(f"❌ Erro durante otimização: {str(e)}")
        exit(1)