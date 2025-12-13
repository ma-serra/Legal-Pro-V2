#!/usr/bin/env python3
"""
Script para definir e implementar a melhor estrutura de integração
entre bases vetoriais e assistentes jurídicos especializados
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

def obter_estrutura_integracao_por_area():
    """Define estrutura de integração específica para cada área jurídica"""
    return {
        'direito_bancario': {
            'assistente_base': 'AssistenteBancario',
            'especializacoes': [
                'regulamentacao_bacen', 'operacoes_credito', 'compliance_financeiro',
                'contratos_bancarios', 'crimes_financeiros'
            ],
            'busca_vetorial': {
                'estrategia': 'hierarquica_ponderada',
                'campos_priorizados': ['numero_normativo', 'instituicao_emissora', 'tipo_operacao_bancaria'],
                'filtros_contextuais': ['data_vigencia', 'categoria_risco'],
                'similaridade_minima': 0.75,
                'max_resultados': 10
            },
            'contexto_especializado': {
                'memoria_conversacional': True,
                'historico_consultas': True,
                'cache_resultados': 'medio_prazo',
                'validacao_juridica': True
            },
            'integracao_agentes': {
                'colaboracao_areas': ['direito_empresarial', 'direito_tributario'],
                'escalacao_complexidade': ['analise_riscos'],
                'compartilha_contexto': True
            }
        },
        'direito_tributario': {
            'assistente_base': 'AssistenteTributario',
            'especializacoes': [
                'lucro_real', 'lucro_presumido', 'simples_nacional', 
                'planejamento_tributario', 'execucao_fiscal'
            ],
            'busca_vetorial': {
                'estrategia': 'multimodal_tributaria',
                'campos_priorizados': ['codigo_tributo', 'exercicio_fiscal', 'regime_tributario'],
                'filtros_contextuais': ['cnae_atividade', 'valor_monetario'],
                'similaridade_minima': 0.80,
                'max_resultados': 15
            },
            'contexto_especializado': {
                'memoria_conversacional': True,
                'historico_consultas': True,
                'cache_resultados': 'longo_prazo',
                'validacao_juridica': True,
                'calculos_automaticos': True
            },
            'integracao_agentes': {
                'colaboracao_areas': ['direito_empresarial', 'direito_bancario'],
                'escalacao_complexidade': ['analise_riscos'],
                'compartilha_contexto': True
            }
        },
        'direito_penal': {
            'assistente_base': 'AssistentePenal',
            'especializacoes': [
                'crimes_patrimoniais', 'crimes_contra_pessoa', 'crimes_tributarios',
                'execucao_penal', 'processo_penal', 'tribunal_juri'
            ],
            'busca_vetorial': {
                'estrategia': 'juridica_contextual',
                'campos_priorizados': ['tipo_crime', 'artigo_legal', 'fase_processual'],
                'filtros_contextuais': ['circunstancias', 'pena_aplicada'],
                'similaridade_minima': 0.70,
                'max_resultados': 8
            },
            'contexto_especializado': {
                'memoria_conversacional': True,
                'historico_consultas': True,
                'cache_resultados': 'medio_prazo',
                'validacao_juridica': True,
                'precedentes_relevantes': True
            },
            'integracao_agentes': {
                'colaboracao_areas': ['direito_processual', 'direito_constitucional'],
                'escalacao_complexidade': ['analise_riscos'],
                'compartilha_contexto': False  # Maior confidencialidade
            }
        },
        'direito_trabalhista': {
            'assistente_base': 'AssistenteTrabalhista',
            'especializacoes': [
                'contratos_trabalho', 'convencoes_coletivas', 'seguranca_trabalho',
                'processo_trabalhista', 'previdencia_social'
            ],
            'busca_vetorial': {
                'estrategia': 'contextual_trabalhista',
                'campos_priorizados': ['categoria_profissional', 'sindicato', 'tipo_beneficio'],
                'filtros_contextuais': ['convencao_coletiva', 'data_base_categoria'],
                'similaridade_minima': 0.72,
                'max_resultados': 12
            },
            'contexto_especializado': {
                'memoria_conversacional': True,
                'historico_consultas': True,
                'cache_resultados': 'medio_prazo',
                'validacao_juridica': True,
                'calculos_trabalhistas': True
            },
            'integracao_agentes': {
                'colaboracao_areas': ['direito_previdenciario', 'direito_empresarial'],
                'escalacao_complexidade': ['analise_riscos'],
                'compartilha_contexto': True
            }
        },
        'direito_civil': {
            'assistente_base': 'AssistenteCivil',
            'especializacoes': [
                'contratos_civis', 'responsabilidade_civil', 'direitos_reais',
                'familia_sucessoes', 'registros_publicos'
            ],
            'busca_vetorial': {
                'estrategia': 'semantica_civil',
                'campos_priorizados': ['tipo_contrato', 'registro_numero', 'partes_envolvidas'],
                'filtros_contextuais': ['cartorio_origem', 'data_lavratura'],
                'similaridade_minima': 0.68,
                'max_resultados': 10
            },
            'contexto_especializado': {
                'memoria_conversacional': True,
                'historico_consultas': True,
                'cache_resultados': 'longo_prazo',
                'validacao_juridica': True
            },
            'integracao_agentes': {
                'colaboracao_areas': ['direito_familia', 'direito_imobiliario'],
                'escalacao_complexidade': ['analise_riscos'],
                'compartilha_contexto': True
            }
        }
    }

def obter_mapeamento_agentes_tabelas():
    """Mapeia agentes para suas respectivas tabelas de embeddings"""
    conn = get_database_connection()
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor()
        
        # Buscar agentes ativos e suas áreas
        cursor.execute("""
            SELECT a.id, a.nome, a.capacidades, c.nome as categoria_nome
            FROM agente_juridico a
            JOIN categoria_juridica c ON a.categoria_id = c.id
            WHERE a.ativo = true AND c.ativa = true
            ORDER BY c.nome, a.nome;
        """)
        
        agentes_data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Mapear para estrutura organizada
        mapeamento = {}
        for agente_id, nome, capacidades_json, categoria in agentes_data:
            
            # Determinar tabela de embeddings
            categoria_normalizada = categoria.lower().replace(' ', '_')
            if categoria_normalizada == 'análise_de_riscos_jurídicos':
                tabela_embedding = 'embeddings_analise_riscos'
            elif categoria_normalizada == 'negociação_e_conflitos':
                tabela_embedding = 'embeddings_negocios_juridicos'
            else:
                tabela_embedding = f'embeddings_{categoria_normalizada}'
            
            # Processar capacidades
            capacidades = []
            if capacidades_json:
                try:
                    if isinstance(capacidades_json, str):
                        capacidades = json.loads(capacidades_json)
                    elif isinstance(capacidades_json, list):
                        capacidades = capacidades_json
                except:
                    capacidades = []
            
            if categoria not in mapeamento:
                mapeamento[categoria] = {
                    'tabela_embedding': tabela_embedding,
                    'agentes': []
                }
            
            mapeamento[categoria]['agentes'].append({
                'id': agente_id,
                'nome': nome,
                'capacidades': capacidades,
                'tabela_embedding': tabela_embedding
            })
        
        return mapeamento
        
    except Exception as e:
        logger.error(f"Erro ao mapear agentes: {str(e)}")
        return {}

def criar_estrutura_integracao_assistente(conn, area_categoria, config_area, agentes_area):
    """Cria estrutura de integração específica para uma área"""
    try:
        cursor = conn.cursor()
        tabela_embedding = agentes_area['tabela_embedding']
        
        logger.info(f"  🔧 Configurando integração para {area_categoria}")
        
        # 1. Criar view especializada para consultas do assistente
        view_name = f"view_assistente_{tabela_embedding.replace('embeddings_', '')}"
        sql_view = f"""
        CREATE OR REPLACE VIEW {view_name} AS
        SELECT 
            id,
            conteudo,
            embedding,
            referencia,
            area,
            metadata,
            criado_em,
            documento_id,
            documento_titulo,
            documento_tipo,
            agente_id,
            tags_especialidade,
            -- Campos de busca otimizada
            ts_rank_cd(to_tsvector('portuguese', COALESCE(conteudo, '')), 
                      plainto_tsquery('portuguese', '')) as relevancia_texto,
            -- Metadados estruturados para filtragem
            COALESCE(metadata->>'nivel_confidencialidade', 'publico') as nivel_acesso,
            COALESCE(metadata->>'fonte_documento', 'sistema') as fonte,
            COALESCE(metadata->>'validado', 'false')::boolean as validado_juridicamente
        FROM {tabela_embedding}
        WHERE documento_tipo IS NOT NULL;
        """
        
        cursor.execute(sql_view)
        
        # 2. Criar função de busca especializada para o assistente
        func_name = f"busca_assistente_{tabela_embedding.replace('embeddings_', '')}"
        sql_function = f"""
        CREATE OR REPLACE FUNCTION {func_name}(
            query_embedding vector(1536),
            filtro_agente_id INTEGER DEFAULT NULL,
            filtro_tipo_documento VARCHAR DEFAULT NULL,
            limite INTEGER DEFAULT 10,
            similaridade_minima FLOAT DEFAULT 0.7
        )
        RETURNS TABLE(
            id INTEGER,
            conteudo TEXT,
            referencia TEXT,
            similaridade FLOAT,
            metadata JSONB,
            agente_responsavel VARCHAR,
            relevancia_contextual FLOAT
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT 
                e.id,
                e.conteudo,
                e.referencia,
                (1 - (e.embedding <=> query_embedding)) as similaridade,
                e.metadata,
                COALESCE(a.nome, 'Sistema') as agente_responsavel,
                -- Cálculo de relevância contextual baseado em múltiplos fatores
                (
                    (1 - (e.embedding <=> query_embedding)) * 0.6 +
                    CASE WHEN e.agente_id = filtro_agente_id THEN 0.2 ELSE 0.0 END +
                    CASE WHEN e.metadata->>'validado' = 'true' THEN 0.1 ELSE 0.0 END +
                    CASE WHEN e.criado_em > CURRENT_DATE - INTERVAL '1 year' THEN 0.1 ELSE 0.05 END
                ) as relevancia_contextual
            FROM {tabela_embedding} e
            LEFT JOIN agente_juridico a ON e.agente_id = a.id
            WHERE 
                (1 - (e.embedding <=> query_embedding)) >= similaridade_minima
                AND (filtro_agente_id IS NULL OR e.agente_id = filtro_agente_id)
                AND (filtro_tipo_documento IS NULL OR e.documento_tipo = filtro_tipo_documento)
                AND e.conteudo IS NOT NULL
            ORDER BY relevancia_contextual DESC, similaridade DESC
            LIMIT limite;
        END;
        $$ LANGUAGE plpgsql;
        """
        
        cursor.execute(sql_function)
        
        # 3. Criar trigger para manter contexto atualizado
        trigger_name = f"trigger_contexto_{tabela_embedding}"
        sql_trigger = f"""
        CREATE OR REPLACE FUNCTION atualizar_contexto_{tabela_embedding.replace('embeddings_', '')}()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Atualizar metadados contextuais quando documento é modificado
            NEW.metadata = NEW.metadata || jsonb_build_object(
                'ultima_atualizacao', CURRENT_TIMESTAMP,
                'versao_contexto', COALESCE((OLD.metadata->>'versao_contexto')::integer, 0) + 1
            );
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        DROP TRIGGER IF EXISTS {trigger_name} ON {tabela_embedding};
        CREATE TRIGGER {trigger_name}
            BEFORE UPDATE ON {tabela_embedding}
            FOR EACH ROW
            EXECUTE FUNCTION atualizar_contexto_{tabela_embedding.replace('embeddings_', '')}();
        """
        
        cursor.execute(sql_trigger)
        
        # 4. Criar tabela de histórico de consultas do assistente
        tabela_historico = f"historico_consultas_{tabela_embedding.replace('embeddings_', '')}"
        sql_historico = f"""
        CREATE TABLE IF NOT EXISTS {tabela_historico} (
            id SERIAL PRIMARY KEY,
            agente_id INTEGER REFERENCES agente_juridico(id),
            usuario_id INTEGER,
            query_original TEXT,
            query_embedding vector(1536),
            resultados_ids INTEGER[],
            similaridades FLOAT[],
            contexto_sessao JSONB,
            feedback_qualidade INTEGER CHECK (feedback_qualidade BETWEEN 1 AND 5),
            tempo_resposta_ms INTEGER,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata_consulta JSONB DEFAULT '{{}}'
        );
        
        CREATE INDEX IF NOT EXISTS idx_{tabela_historico}_agente_data 
        ON {tabela_historico} (agente_id, criado_em DESC);
        
        CREATE INDEX IF NOT EXISTS idx_{tabela_historico}_embedding_similar 
        ON {tabela_historico} USING ivfflat (query_embedding vector_cosine_ops) WITH (lists = 50);
        """
        
        cursor.execute(sql_historico)
        
        # 5. Criar função de aprendizado contextual
        func_aprendizado = f"aprender_contexto_{tabela_embedding.replace('embeddings_', '')}"
        sql_aprendizado = f"""
        CREATE OR REPLACE FUNCTION {func_aprendizado}(
            agente_id INTEGER,
            consulta_bem_sucedida BOOLEAN,
            contexto_utilizado JSONB
        )
        RETURNS VOID AS $$
        BEGIN
            -- Atualizar pesos de relevância baseado no feedback
            IF consulta_bem_sucedida THEN
                UPDATE {tabela_embedding}
                SET metadata = metadata || jsonb_build_object(
                    'score_relevancia', 
                    COALESCE((metadata->>'score_relevancia')::float, 1.0) * 1.1,
                    'consultas_sucesso',
                    COALESCE((metadata->>'consultas_sucesso')::integer, 0) + 1
                )
                WHERE agente_id = agente_id
                AND id = ANY(ARRAY(SELECT jsonb_array_elements_text(contexto_utilizado->'documentos_utilizados'))::integer[]);
            ELSE
                UPDATE {tabela_embedding}
                SET metadata = metadata || jsonb_build_object(
                    'score_relevancia', 
                    COALESCE((metadata->>'score_relevancia')::float, 1.0) * 0.95,
                    'consultas_falha',
                    COALESCE((metadata->>'consultas_falha')::integer, 0) + 1
                )
                WHERE agente_id = agente_id
                AND id = ANY(ARRAY(SELECT jsonb_array_elements_text(contexto_utilizado->'documentos_utilizados'))::integer[]);
            END IF;
        END;
        $$ LANGUAGE plpgsql;
        """
        
        cursor.execute(sql_aprendizado)
        
        cursor.close()
        
        # Configurar parâmetros específicos da área
        melhorias = [
            'view_assistente_criada',
            'funcao_busca_especializada',
            'trigger_contexto_ativo',
            'historico_consultas_implementado',
            'aprendizado_contextual_ativo'
        ]
        
        logger.info(f"    ✅ {len(melhorias)} componentes de integração criados")
        return melhorias
        
    except Exception as e:
        logger.error(f"    ❌ Erro na integração: {str(e)}")
        return []

def implementar_integracao_assistentes():
    """Implementa estrutura completa de integração assistentes-bases vetoriais"""
    
    logger.info("🤖 Implementando integração assistentes-bases vetoriais...")
    
    # Conectar ao banco
    conn = get_database_connection()
    if not conn:
        logger.error("❌ Falha na conexão com banco de dados")
        return False
    
    # Obter mapeamento atual
    mapeamento_agentes = obter_mapeamento_agentes_tabelas()
    if not mapeamento_agentes:
        logger.error("❌ Nenhum agente encontrado para integração")
        conn.close()
        return False
    
    # Obter configurações de integração
    configs_integracao = obter_estrutura_integracao_por_area()
    
    relatorio = {
        'areas_processadas': 0,
        'integracoes_criadas': 0,
        'componentes_implementados': 0,
        'areas_com_erro': 0,
        'detalhes': []
    }
    
    for categoria, agentes_info in mapeamento_agentes.items():
        # Mapear categoria para configuração
        categoria_key = categoria.lower().replace(' ', '_')
        if categoria_key == 'análise_de_riscos_jurídicos':
            categoria_key = 'analise_riscos'
        elif categoria_key == 'negociação_e_conflitos':
            categoria_key = 'negocios_juridicos'
        
        logger.info(f"🔧 Processando área: {categoria} ({len(agentes_info['agentes'])} agentes)")
        
        resultado_area = {
            'categoria': categoria,
            'total_agentes': len(agentes_info['agentes']),
            'tabela_embedding': agentes_info['tabela_embedding'],
            'componentes_criados': [],
            'agentes_integrados': 0
        }
        
        # Usar configuração específica ou genérica
        if categoria_key in configs_integracao:
            config_area = configs_integracao[categoria_key]
        else:
            # Configuração genérica para áreas não mapeadas
            config_area = {
                'busca_vetorial': {
                    'estrategia': 'semantica_generica',
                    'similaridade_minima': 0.70,
                    'max_resultados': 10
                },
                'contexto_especializado': {
                    'memoria_conversacional': True,
                    'cache_resultados': 'medio_prazo'
                }
            }
        
        # Implementar integração para a área
        componentes = criar_estrutura_integracao_assistente(conn, categoria, config_area, agentes_info)
        
        if componentes:
            resultado_area['componentes_criados'] = componentes
            resultado_area['agentes_integrados'] = len(agentes_info['agentes'])
            relatorio['integracoes_criadas'] += 1
            relatorio['componentes_implementados'] += len(componentes)
            
            logger.info(f"  ✅ {categoria}: {len(componentes)} componentes, {len(agentes_info['agentes'])} agentes")
        else:
            relatorio['areas_com_erro'] += 1
            logger.error(f"  ❌ {categoria}: Falha na integração")
        
        relatorio['detalhes'].append(resultado_area)
        relatorio['areas_processadas'] += 1
    
    conn.close()
    
    # Gerar relatório de integração
    gerar_relatorio_integracao(relatorio)
    
    return relatorio['areas_com_erro'] == 0

def gerar_relatorio_integracao(relatorio):
    """Gera relatório detalhado da integração assistentes-bases"""
    
    logger.info("📊 RELATÓRIO DE INTEGRAÇÃO ASSISTENTES-BASES VETORIAIS")
    logger.info("=" * 70)
    
    logger.info(f"Áreas jurídicas processadas: {relatorio['areas_processadas']}")
    logger.info(f"Integrações criadas: {relatorio['integracoes_criadas']}")
    logger.info(f"Componentes implementados: {relatorio['componentes_implementados']}")
    logger.info(f"Áreas com erro: {relatorio['areas_com_erro']}")
    
    total_agentes = sum(area['total_agentes'] for area in relatorio['detalhes'])
    agentes_integrados = sum(area['agentes_integrados'] for area in relatorio['detalhes'])
    
    logger.info(f"Total de agentes: {total_agentes}")
    logger.info(f"Agentes integrados: {agentes_integrados}")
    
    if relatorio['areas_com_erro'] == 0:
        logger.info("🎉 TODAS AS INTEGRAÇÕES FORAM IMPLEMENTADAS COM SUCESSO!")
        logger.info("")
        logger.info("🚀 FUNCIONALIDADES ATIVAS:")
        logger.info("  ✅ Busca vetorial especializada por área")
        logger.info("  ✅ Views otimizadas para consultas de assistentes")
        logger.info("  ✅ Histórico de consultas e aprendizado contextual")
        logger.info("  ✅ Triggers de atualização automática")
        logger.info("  ✅ Funções de relevância contextual")
        logger.info("  ✅ Sistema de feedback e melhoria contínua")
    else:
        logger.warning("⚠️ ALGUMAS INTEGRAÇÕES FALHARAM")
    
    logger.info("=" * 70)
    logger.info("📋 RESUMO POR ÁREA JURÍDICA:")
    
    for area in relatorio['detalhes']:
        if area['agentes_integrados'] > 0:
            status = "✅ INTEGRADA"
            detalhes = f"{len(area['componentes_criados'])} componentes"
        else:
            status = "❌ FALHA"
            detalhes = "verificar logs"
        
        logger.info(f"  {status} {area['categoria']}")
        logger.info(f"     Agentes: {area['agentes_integrados']}/{area['total_agentes']}")
        logger.info(f"     Tabela: {area['tabela_embedding']}")
        logger.info(f"     Status: {detalhes}")

if __name__ == "__main__":
    try:
        sucesso = implementar_integracao_assistentes()
        if sucesso:
            logger.info("✅ Integração assistentes-bases concluída com sucesso!")
            exit(0)
        else:
            logger.error("❌ Integração concluída com problemas")
            exit(1)
    except Exception as e:
        logger.error(f"❌ Erro durante integração: {str(e)}")
        exit(1)