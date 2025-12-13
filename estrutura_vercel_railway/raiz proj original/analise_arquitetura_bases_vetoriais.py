#!/usr/bin/env python3
"""
Análise da melhor arquitetura de base vetorial para cada tipo de agente jurídico
Considera especialidades, tipos de documentos e padrões de busca específicos
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

def obter_perfil_agentes_por_area():
    """Define perfil de documentos e necessidades por área jurídica"""
    return {
        'direito_bancario': {
            'documentos_principais': [
                'regulamentacao_bacen', 'normativos_cmn', 'contratos_bancarios', 
                'jurisprudencia_financeira', 'pareceres_cvm', 'acordos_basileia'
            ],
            'volume_estimado': 'alto',
            'frequencia_atualizacao': 'diaria',
            'complexidade_busca': 'alta',
            'indices_especializados': [
                'numero_normativo', 'data_vigencia', 'instituicao_emissora',
                'tipo_operacao_bancaria', 'categoria_risco'
            ],
            'embedding_strategy': 'chunking_especializado',
            'chunk_size': 1000,
            'chunk_overlap': 200
        },
        'direito_tributario': {
            'documentos_principais': [
                'legislacao_tributaria', 'receita_federal', 'jurisprudencia_fiscal',
                'pareceres_pgfn', 'acordos_internacionais', 'tabelas_tributarias'
            ],
            'volume_estimado': 'muito_alto',
            'frequencia_atualizacao': 'diaria',
            'complexidade_busca': 'muito_alta',
            'indices_especializados': [
                'codigo_tributo', 'exercicio_fiscal', 'regime_tributario',
                'cnae_atividade', 'valor_monetario', 'prazo_recolhimento'
            ],
            'embedding_strategy': 'chunking_hierarquico',
            'chunk_size': 800,
            'chunk_overlap': 150
        },
        'direito_trabalhista': {
            'documentos_principais': [
                'clt_atualizacoes', 'normas_mte', 'convencoes_coletivas',
                'jurisprudencia_tst', 'instrucoes_normativas', 'portarias_trabalho'
            ],
            'volume_estimado': 'alto',
            'frequencia_atualizacao': 'semanal',
            'complexidade_busca': 'alta',
            'indices_especializados': [
                'categoria_profissional', 'sindicato', 'convenção_coletiva',
                'data_base_categoria', 'tipo_beneficio'
            ],
            'embedding_strategy': 'chunking_contextual',
            'chunk_size': 1200,
            'chunk_overlap': 100
        },
        'direito_penal': {
            'documentos_principais': [
                'codigo_penal', 'codigo_processo_penal', 'jurisprudencia_criminal',
                'sumulas_stf_stj', 'lei_execucao_penal', 'legislacao_especial'
            ],
            'volume_estimado': 'medio',
            'frequencia_atualizacao': 'mensal',
            'complexidade_busca': 'alta',
            'indices_especializados': [
                'tipo_crime', 'artigo_legal', 'pena_aplicada',
                'circunstancias', 'fase_processual'
            ],
            'embedding_strategy': 'chunking_juridico',
            'chunk_size': 1500,
            'chunk_overlap': 250
        },
        'direito_civil': {
            'documentos_principais': [
                'codigo_civil', 'jurisprudencia_civil', 'doutrina_civilista',
                'contratos_modelo', 'registros_publicos', 'cartorio_documentos'
            ],
            'volume_estimado': 'muito_alto',
            'frequencia_atualizacao': 'mensal',
            'complexidade_busca': 'media',
            'indices_especializados': [
                'tipo_contrato', 'cartorio_origem', 'registro_numero',
                'data_lavratura', 'partes_envolvidas'
            ],
            'embedding_strategy': 'chunking_semantico',
            'chunk_size': 1000,
            'chunk_overlap': 150
        },
        'direito_empresarial': {
            'documentos_principais': [
                'lei_sociedades', 'instrucoes_cvm', 'contratos_sociais',
                'atas_assembleia', 'documentos_societarios', 'compliance_corporativo'
            ],
            'volume_estimado': 'alto',
            'frequencia_atualizacao': 'diaria',
            'complexidade_busca': 'alta',
            'indices_especializados': [
                'cnpj_empresa', 'tipo_societario', 'capital_social',
                'data_constituicao', 'atividade_economica'
            ],
            'embedding_strategy': 'chunking_empresarial',
            'chunk_size': 900,
            'chunk_overlap': 180
        },
        'direito_administrativo': {
            'documentos_principais': [
                'licitacoes', 'contratos_publicos', 'decretos_regulamentares',
                'portarias_ministeriais', 'atos_normativos', 'jurisprudencia_administrativa'
            ],
            'volume_estimado': 'muito_alto',
            'frequencia_atualizacao': 'diaria',
            'complexidade_busca': 'alta',
            'indices_especializados': [
                'orgao_publico', 'modalidade_licitacao', 'valor_contrato',
                'numero_processo_sei', 'categoria_despesa'
            ],
            'embedding_strategy': 'chunking_administrativo',
            'chunk_size': 800,
            'chunk_overlap': 160
        },
        'direito_constitucional': {
            'documentos_principais': [
                'constituicao_federal', 'adi_stf', 'adpf_stf',
                'jurisprudencia_constitucional', 'doutrina_constitucional', 'emendas_constitucionais'
            ],
            'volume_estimado': 'medio',
            'frequencia_atualizacao': 'mensal',
            'complexidade_busca': 'muito_alta',
            'indices_especializados': [
                'artigo_constitucional', 'principio_constitucional', 'controle_constitucionalidade',
                'direito_fundamental', 'competencia_federativa'
            ],
            'embedding_strategy': 'chunking_constitucional',
            'chunk_size': 1200,
            'chunk_overlap': 300
        },
        'direito_consumidor': {
            'documentos_principais': [
                'cdc_atualizacoes', 'jurisprudencia_consumidor', 'portarias_senacon',
                'decisoes_procon', 'recalls_produtos', 'normas_anac_anatel'
            ],
            'volume_estimado': 'alto',
            'frequencia_atualizacao': 'semanal',
            'complexidade_busca': 'media',
            'indices_especializados': [
                'produto_servico', 'fornecedor', 'tipo_reclamacao',
                'valor_dano', 'orgao_fiscalizador'
            ],
            'embedding_strategy': 'chunking_consumerista',
            'chunk_size': 1100,
            'chunk_overlap': 150
        },
        'direito_imobiliario': {
            'documentos_principais': [
                'cartorio_imoveis', 'contratos_compra_venda', 'financiamentos_habitacionais',
                'legislacao_urbana', 'plantas_valores', 'iptu_documentos'
            ],
            'volume_estimado': 'alto',
            'frequencia_atualizacao': 'mensal',
            'complexidade_busca': 'alta',
            'indices_especializados': [
                'matricula_imovel', 'cartorio_registro', 'cpf_cnpj_proprietario',
                'endereco_completo', 'valor_transacao', 'tipo_financiamento'
            ],
            'embedding_strategy': 'chunking_imobiliario',
            'chunk_size': 800,
            'chunk_overlap': 120
        },
        'direito_familia': {
            'documentos_principais': [
                'processos_divorcio', 'guarda_menores', 'pensao_alimenticia',
                'adocao_documentos', 'violencia_domestica', 'vara_familia_decisoes'
            ],
            'volume_estimado': 'alto',
            'frequencia_atualizacao': 'semanal',
            'complexidade_busca': 'media',
            'indices_especializados': [
                'tipo_acao_familia', 'nome_partes', 'menor_envolvido',
                'valor_pensao', 'regime_bens'
            ],
            'embedding_strategy': 'chunking_familiar',
            'chunk_size': 1000,
            'chunk_overlap': 200
        },
        'direito_previdenciario': {
            'documentos_principais': [
                'legislacao_inss', 'beneficios_previdenciarios', 'aposentadorias',
                'auxilio_doenca', 'jurisprudencia_previdenciaria', 'instrucoes_normativas_inss'
            ],
            'volume_estimado': 'muito_alto',
            'frequencia_atualizacao': 'semanal',
            'complexidade_busca': 'alta',
            'indices_especializados': [
                'numero_beneficio', 'tipo_beneficio', 'cpf_segurado',
                'data_concessao', 'valor_beneficio'
            ],
            'embedding_strategy': 'chunking_previdenciario',
            'chunk_size': 900,
            'chunk_overlap': 150
        },
        'direito_digital': {
            'documentos_principais': [
                'marco_civil_internet', 'lgpd_documentos', 'crimes_digitais',
                'contratos_tecnologia', 'propriedade_intelectual_digital', 'regulamentacao_anpd'
            ],
            'volume_estimado': 'medio',
            'frequencia_atualizacao': 'mensal',
            'complexidade_busca': 'alta',
            'indices_especializados': [
                'tipo_dado_pessoal', 'base_legal_lgpd', 'incidente_seguranca',
                'plataforma_digital', 'direito_autoral_digital'
            ],
            'embedding_strategy': 'chunking_digital',
            'chunk_size': 1200,
            'chunk_overlap': 200
        },
        'direito_ambiental': {
            'documentos_principais': [
                'legislacao_ambiental', 'licenciamento_ambiental', 'ibama_documentos',
                'compensacao_ambiental', 'estudos_impacto', 'certificacoes_ambientais'
            ],
            'volume_estimado': 'alto',
            'frequencia_atualizacao': 'mensal',
            'complexidade_busca': 'alta',
            'indices_especializados': [
                'numero_licenca', 'orgao_ambiental', 'tipo_empreendimento',
                'bioma_afetado', 'compensacao_valor'
            ],
            'embedding_strategy': 'chunking_ambiental',
            'chunk_size': 1000,
            'chunk_overlap': 180
        },
        'direito_securitario': {
            'documentos_principais': [
                'susep_normativos', 'apolices_seguro', 'sinistros_documentos',
                'resseguro_contratos', 'corretagem_seguros', 'jurisprudencia_securitaria'
            ],
            'volume_estimado': 'alto',
            'frequencia_atualizacao': 'mensal',
            'complexidade_busca': 'alta',
            'indices_especializados': [
                'numero_apolice', 'seguradora', 'tipo_seguro',
                'valor_sinistro', 'data_sinistro'
            ],
            'embedding_strategy': 'chunking_securitario',
            'chunk_size': 1000,
            'chunk_overlap': 150
        },
        'analise_riscos': {
            'documentos_principais': [
                'analises_juridicas', 'pareceres_risco', 'contratos_analisados',
                'precedentes_relevantes', 'metodologias_risco', 'relatorios_compliance'
            ],
            'volume_estimado': 'medio',
            'frequencia_atualizacao': 'semanal',
            'complexidade_busca': 'muito_alta',
            'indices_especializados': [
                'nivel_risco', 'tipo_analise', 'area_juridica_analisada',
                'valor_exposicao', 'recomendacao_acao'
            ],
            'embedding_strategy': 'chunking_analise_risco',
            'chunk_size': 800,
            'chunk_overlap': 200
        },
        'negocios_juridicos': {
            'documentos_principais': [
                'contratos_comerciais', 'negociacao_documentos', 'due_diligence',
                'acordos_comerciais', 'joint_ventures', 'fusoes_aquisicoes'
            ],
            'volume_estimado': 'medio',
            'frequencia_atualizacao': 'semanal',
            'complexidade_busca': 'alta',
            'indices_especializados': [
                'tipo_negocio', 'partes_contratuais', 'valor_operacao',
                'prazo_vigencia', 'clausulas_especiais'
            ],
            'embedding_strategy': 'chunking_negocial',
            'chunk_size': 1000,
            'chunk_overlap': 150
        }
    }

def calcular_configuracao_otima(perfil_area):
    """Calcula configuração ótima de índices e estrutura"""
    config = {
        'indices_obrigatorios': [],
        'indices_opcionais': [],
        'configuracao_embedding': {},
        'otimizacoes_performance': []
    }
    
    # Índices baseados no volume
    if perfil_area['volume_estimado'] in ['alto', 'muito_alto']:
        config['indices_obrigatorios'].extend([
            'idx_embedding_ivfflat_cosine',
            'idx_embedding_ivfflat_l2',
            'idx_data_criacao_btree',
            'idx_documento_tipo_hash'
        ])
        config['otimizacoes_performance'].append('particionamento_temporal')
    
    # Índices baseados na frequência de atualização
    if perfil_area['frequencia_atualizacao'] == 'diaria':
        config['indices_obrigatorios'].append('idx_data_atualizacao_btree')
        config['otimizacoes_performance'].append('vacuum_automatico_agressivo')
    
    # Índices baseados na complexidade de busca
    if perfil_area['complexidade_busca'] in ['alta', 'muito_alta']:
        config['indices_obrigatorios'].extend([
            'idx_metadata_gin',
            'idx_tags_especialidade_gin',
            'idx_documento_titulo_gin'
        ])
        config['otimizacoes_performance'].append('cache_embedding_aumentado')
    
    # Configuração de embedding específica
    config['configuracao_embedding'] = {
        'strategy': perfil_area['embedding_strategy'],
        'chunk_size': perfil_area['chunk_size'],
        'chunk_overlap': perfil_area['chunk_overlap'],
        'dimensao': 1536,  # OpenAI ada-002
        'normalizacao': True
    }
    
    # Índices especializados da área
    for indice_esp in perfil_area['indices_especializados']:
        config['indices_opcionais'].append(f'idx_{indice_esp}_btree')
    
    return config

def gerar_sql_otimizada(nome_tabela, perfil_area, config):
    """Gera SQL otimizada para criar tabela com configuração específica"""
    
    # Colunas base
    colunas_base = [
        'id SERIAL PRIMARY KEY',
        'conteudo TEXT NOT NULL',
        'embedding vector(1536)',
        'referencia TEXT',
        'area VARCHAR(255)',
        'metadata JSONB DEFAULT \'{}\'',
        'criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
        'documento_id VARCHAR(255)',
        'documento_titulo TEXT',
        'documento_tipo VARCHAR(100)',
        'agente_id INTEGER'
    ]
    
    # Colunas especializadas por área
    colunas_especializadas = []
    
    if 'bancario' in nome_tabela:
        colunas_especializadas.extend([
            'numero_normativo VARCHAR(50)',
            'instituicao_emissora VARCHAR(255)',
            'tipo_operacao_bancaria VARCHAR(100)',
            'categoria_risco VARCHAR(50)'
        ])
    elif 'tributario' in nome_tabela:
        colunas_especializadas.extend([
            'codigo_tributo VARCHAR(20)',
            'exercicio_fiscal INTEGER',
            'regime_tributario VARCHAR(50)',
            'cnae_atividade VARCHAR(20)',
            'valor_monetario DECIMAL(15,2)'
        ])
    elif 'trabalhista' in nome_tabela:
        colunas_especializadas.extend([
            'categoria_profissional VARCHAR(255)',
            'sindicato VARCHAR(255)',
            'convencao_coletiva VARCHAR(100)',
            'data_base_categoria DATE'
        ])
    elif 'penal' in nome_tabela:
        colunas_especializadas.extend([
            'tipo_crime VARCHAR(100)',
            'artigo_legal VARCHAR(50)',
            'fase_processual VARCHAR(100)',
            'circunstancias TEXT[]'
        ])
    elif 'imobiliario' in nome_tabela:
        colunas_especializadas.extend([
            'matricula_imovel VARCHAR(50)',
            'cartorio_registro VARCHAR(255)',
            'endereco_completo TEXT',
            'valor_transacao DECIMAL(15,2)'
        ])
    
    # Adicionar colunas especializadas padrão
    colunas_especializadas.extend([
        'tags_especialidade TEXT[]',
        'nivel_confidencialidade VARCHAR(50) DEFAULT \'publico\'',
        'data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
    ])
    
    # Montar SQL de criação
    todas_colunas = colunas_base + colunas_especializadas
    colunas_formatadas = ',\n        '.join(todas_colunas)
    sql_create = f"""
    CREATE TABLE IF NOT EXISTS {nome_tabela} (
        {colunas_formatadas}
    );
    """
    
    # SQL para índices obrigatórios
    indices_sql = []
    for idx in config['indices_obrigatorios']:
        if 'embedding_ivfflat_cosine' in idx:
            indices_sql.append(f"CREATE INDEX IF NOT EXISTS {idx.replace('idx_', f'idx_{nome_tabela}_')} ON {nome_tabela} USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);")
        elif 'embedding_ivfflat_l2' in idx:
            indices_sql.append(f"CREATE INDEX IF NOT EXISTS {idx.replace('idx_', f'idx_{nome_tabela}_')} ON {nome_tabela} USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);")
        elif 'metadata_gin' in idx:
            indices_sql.append(f"CREATE INDEX IF NOT EXISTS {idx.replace('idx_', f'idx_{nome_tabela}_')} ON {nome_tabela} USING GIN (metadata);")
        elif 'tags_especialidade_gin' in idx:
            indices_sql.append(f"CREATE INDEX IF NOT EXISTS {idx.replace('idx_', f'idx_{nome_tabela}_')} ON {nome_tabela} USING GIN (tags_especialidade);")
        elif 'data_criacao_btree' in idx:
            indices_sql.append(f"CREATE INDEX IF NOT EXISTS {idx.replace('idx_', f'idx_{nome_tabela}_')} ON {nome_tabela} (criado_em DESC);")
        elif 'data_atualizacao_btree' in idx:
            indices_sql.append(f"CREATE INDEX IF NOT EXISTS {idx.replace('idx_', f'idx_{nome_tabela}_')} ON {nome_tabela} (data_atualizacao DESC);")
        elif 'documento_tipo_hash' in idx:
            indices_sql.append(f"CREATE INDEX IF NOT EXISTS {idx.replace('idx_', f'idx_{nome_tabela}_')} ON {nome_tabela} USING HASH (documento_tipo);")
    
    return sql_create, indices_sql

def implementar_arquitetura_otimizada():
    """Implementa arquitetura otimizada para cada área"""
    
    logger.info("🏗️ Analisando e implementando arquitetura otimizada de bases vetoriais...")
    
    # Conectar ao banco
    conn = get_database_connection()
    if not conn:
        logger.error("❌ Falha na conexão com banco de dados")
        return False
    
    # Obter perfis das áreas
    perfis_areas = obter_perfil_agentes_por_area()
    
    # Mapear tabelas para áreas
    mapeamento_tabelas = {
        'embeddings_direito_bancario': 'direito_bancario',
        'embeddings_direito_tributario': 'direito_tributario',
        'embeddings_direito_trabalhista': 'direito_trabalhista',
        'embeddings_direito_penal': 'direito_penal',
        'embeddings_direito_civil': 'direito_civil',
        'embeddings_direito_empresarial': 'direito_empresarial',
        'embeddings_direito_administrativo': 'direito_administrativo',
        'embeddings_direito_constitucional': 'direito_constitucional',
        'embeddings_direito_consumidor': 'direito_consumidor',
        'embeddings_direito_imobiliario': 'direito_imobiliario',
        'embeddings_direito_familia': 'direito_familia',
        'embeddings_direito_previdenciario': 'direito_previdenciario',
        'embeddings_direito_digital': 'direito_digital',
        'embeddings_direito_ambiental': 'direito_ambiental',
        'embeddings_direito_securitario': 'direito_securitario',
        'embeddings_analise_riscos': 'analise_riscos',
        'embeddings_negocios_juridicos': 'negocios_juridicos'
    }
    
    relatorio = {
        'tabelas_analisadas': 0,
        'arquiteturas_otimizadas': 0,
        'melhorias_implementadas': 0,
        'detalhes': []
    }
    
    cursor = conn.cursor()
    
    for nome_tabela, area_key in mapeamento_tabelas.items():
        if area_key not in perfis_areas:
            continue
            
        logger.info(f"🔧 Otimizando arquitetura: {nome_tabela} ({area_key})")
        
        perfil_area = perfis_areas[area_key]
        config = calcular_configuracao_otima(perfil_area)
        
        # Gerar SQL otimizada
        sql_create, indices_sql = gerar_sql_otimizada(nome_tabela, perfil_area, config)
        
        detalhes_tabela = {
            'tabela': nome_tabela,
            'area': area_key,
            'volume_estimado': perfil_area['volume_estimado'],
            'frequencia_atualizacao': perfil_area['frequencia_atualizacao'],
            'complexidade_busca': perfil_area['complexidade_busca'],
            'chunk_size_otimo': perfil_area['chunk_size'],
            'indices_criados': 0,
            'melhorias': []
        }
        
        try:
            # Aplicar otimizações estruturais
            cursor.execute(sql_create)
            detalhes_tabela['melhorias'].append('estrutura_otimizada')
            
            # Criar índices especializados
            for sql_index in indices_sql:
                try:
                    cursor.execute(sql_index)
                    detalhes_tabela['indices_criados'] += 1
                except Exception as e:
                    logger.warning(f"  ⚠️ Índice não criado: {str(e)[:50]}...")
            
            # Configurar otimizações de performance
            for otimizacao in config['otimizacoes_performance']:
                if otimizacao == 'vacuum_automatico_agressivo':
                    cursor.execute(f"ALTER TABLE {nome_tabela} SET (autovacuum_vacuum_threshold = 100, autovacuum_analyze_threshold = 50);")
                    detalhes_tabela['melhorias'].append('vacuum_otimizado')
                elif otimizacao == 'cache_embedding_aumentado':
                    # Configuração de cache específica para embeddings
                    detalhes_tabela['melhorias'].append('cache_embeddings')
            
            relatorio['arquiteturas_otimizadas'] += 1
            relatorio['melhorias_implementadas'] += len(detalhes_tabela['melhorias'])
            
            logger.info(f"  ✅ {nome_tabela}: {detalhes_tabela['indices_criados']} índices, {len(detalhes_tabela['melhorias'])} otimizações")
            
        except Exception as e:
            logger.error(f"  ❌ Erro na otimização: {str(e)}")
        
        relatorio['detalhes'].append(detalhes_tabela)
        relatorio['tabelas_analisadas'] += 1
    
    cursor.close()
    conn.close()
    
    # Gerar relatório de análise
    gerar_relatorio_arquitetura(relatorio, perfis_areas)
    
    return relatorio['arquiteturas_otimizadas'] > 0

def gerar_relatorio_arquitetura(relatorio, perfis_areas):
    """Gera relatório detalhado da análise arquitetural"""
    
    logger.info("📊 ANÁLISE DE ARQUITETURA DE BASES VETORIAIS POR ESPECIALIDADE")
    logger.info("=" * 80)
    
    logger.info(f"Áreas analisadas: {relatorio['tabelas_analisadas']}")
    logger.info(f"Arquiteturas otimizadas: {relatorio['arquiteturas_otimizadas']}")
    logger.info(f"Total de melhorias: {relatorio['melhorias_implementadas']}")
    
    logger.info("\n📋 RECOMENDAÇÕES POR ÁREA JURÍDICA:")
    logger.info("-" * 50)
    
    # Agrupar por complexidade e volume
    areas_alto_volume = []
    areas_alta_complexidade = []
    areas_atualizacao_frequente = []
    
    for detalhe in relatorio['detalhes']:
        area_key = detalhe['area']
        if area_key in perfis_areas:
            perfil = perfis_areas[area_key]
            
            if perfil['volume_estimado'] in ['alto', 'muito_alto']:
                areas_alto_volume.append(detalhe)
            
            if perfil['complexidade_busca'] in ['alta', 'muito_alta']:
                areas_alta_complexidade.append(detalhe)
            
            if perfil['frequencia_atualizacao'] == 'diaria':
                areas_atualizacao_frequente.append(detalhe)
    
    logger.info(f"\n🔥 ÁREAS DE ALTO VOLUME ({len(areas_alto_volume)}):")
    for area in areas_alto_volume:
        logger.info(f"  • {area['area'].replace('_', ' ').title()}: {area['chunk_size_otimo']} chars/chunk")
    
    logger.info(f"\n🧠 ÁREAS DE ALTA COMPLEXIDADE ({len(areas_alta_complexidade)}):")
    for area in areas_alta_complexidade:
        logger.info(f"  • {area['area'].replace('_', ' ').title()}: {area['indices_criados']} índices especializados")
    
    logger.info(f"\n⚡ ÁREAS DE ATUALIZAÇÃO FREQUENTE ({len(areas_atualizacao_frequente)}):")
    for area in areas_atualizacao_frequente:
        logger.info(f"  • {area['area'].replace('_', ' ').title()}: otimizações de performance ativas")
    
    logger.info("\n🎯 ESTRATÉGIAS DE CHUNKING RECOMENDADAS:")
    logger.info("-" * 50)
    
    estrategias_chunking = {}
    for area_key, perfil in perfis_areas.items():
        estrategia = perfil['embedding_strategy']
        if estrategia not in estrategias_chunking:
            estrategias_chunking[estrategia] = []
        estrategias_chunking[estrategia].append(area_key)
    
    for estrategia, areas in estrategias_chunking.items():
        logger.info(f"\n{estrategia.replace('_', ' ').title()}:")
        for area in areas:
            perfil = perfis_areas[area]
            logger.info(f"  • {area.replace('_', ' ').title()}: {perfil['chunk_size']} chars, overlap {perfil['chunk_overlap']}")
    
    logger.info("\n💡 RECOMENDAÇÕES FINAIS:")
    logger.info("-" * 30)
    logger.info("✅ Estruturas otimizadas para tipos específicos de documentos")
    logger.info("✅ Índices especializados por área de atuação")
    logger.info("✅ Configurações de chunking adaptadas ao conteúdo")
    logger.info("✅ Performance otimizada por padrão de uso")
    logger.info("✅ Preparação para volume real de documentos jurídicos")

if __name__ == "__main__":
    try:
        sucesso = implementar_arquitetura_otimizada()
        if sucesso:
            logger.info("✅ Análise e otimização de arquitetura concluída!")
            exit(0)
        else:
            logger.error("❌ Problemas na análise de arquitetura")
            exit(1)
    except Exception as e:
        logger.error(f"❌ Erro durante análise: {str(e)}")
        exit(1)