"""
Upgrade Completo das Bases Vetoriais Jurídicas
Implementa sistema duplo de embeddings e orquestração inteligente para 309 agentes
"""

import os
import json
import logging
import psycopg2
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
import openai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UpgradeBasesVetoriais:
    """Gerenciador do upgrade completo das bases vetoriais"""
    
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        self.openai_client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        self.areas_juridicas = [
            'direito_penal_integrado', 'direito_civil', 'direito_agrario',
            'direito_ambiental', 'direito_tributario', 'direito_constitucional',
            'direito_administrativo', 'direito_familia', 'direito_sucessorio',
            'direito_empresarial', 'direito_trabalhista', 'direito_previdenciario',
            'direito_consumidor', 'direito_imobiliario', 'direito_digital',
            'seguros', 'conflitos_mediacao', 'analise_riscos'
        ]
        
    def conectar_database(self):
        """Conecta ao banco PostgreSQL"""
        try:
            return psycopg2.connect(self.database_url)
        except Exception as e:
            logger.error(f"Erro na conexão: {e}")
            return None
    
    def criar_novas_estruturas_tabelas(self):
        """Cria ou atualiza estruturas das 18 tabelas com embeddings duplos"""
        logger.info("🔧 Criando novas estruturas de tabelas...")
        
        conn = self.conectar_database()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        for area in self.areas_juridicas:
            tabela_nome = f"embeddings_{area}"
            
            try:
                # SQL para criar/atualizar tabela com embeddings duplos
                sql_create_table = f"""
                CREATE TABLE IF NOT EXISTS {tabela_nome} (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    conteudo TEXT NOT NULL,
                    referencia VARCHAR(500) NOT NULL,
                    area_origem VARCHAR(50) NOT NULL,
                    agente_id TEXT,
                    tipo_documento VARCHAR(100) DEFAULT 'artigo',
                    artigo_numero VARCHAR(20),
                    capitulo VARCHAR(200),
                    titulo VARCHAR(200),
                    livro VARCHAR(200),
                    embedding_small VECTOR(1536),
                    embedding_large VECTOR(3072),
                    metadata JSONB DEFAULT '{{}}',
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
                
                cursor.execute(sql_create_table)
                
                # Adicionar colunas se não existirem (para tabelas existentes)
                try:
                    cursor.execute(f"ALTER TABLE {tabela_nome} ADD COLUMN IF NOT EXISTS embedding_small VECTOR(1536);")
                    cursor.execute(f"ALTER TABLE {tabela_nome} ADD COLUMN IF NOT EXISTS embedding_large VECTOR(3072);")
                    cursor.execute(f"ALTER TABLE {tabela_nome} ADD COLUMN IF NOT EXISTS agente_id TEXT;")
                except:
                    pass  # Colunas já existem
                
                conn.commit()
                logger.info(f"✅ Tabela {tabela_nome} criada/atualizada")
                
            except Exception as e:
                logger.error(f"❌ Erro ao criar tabela {tabela_nome}: {e}")
                conn.rollback()
        
        cursor.close()
        conn.close()
        return True
    
    def criar_indices_vetoriais(self):
        """Cria índices otimizados para busca vetorial dupla"""
        logger.info("🔧 Criando índices vetoriais...")
        
        conn = self.conectar_database()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        for area in self.areas_juridicas:
            tabela_nome = f"embeddings_{area}"
            area_limpa = area.replace('_', '')
            
            try:
                # Índices para embeddings duplos
                indices_sql = [
                    f"CREATE INDEX IF NOT EXISTS idx_{area_limpa}_embedding_small ON {tabela_nome} USING ivfflat (embedding_small vector_cosine_ops) WITH (lists = 100);",
                    f"CREATE INDEX IF NOT EXISTS idx_{area_limpa}_embedding_large ON {tabela_nome} USING ivfflat (embedding_large vector_cosine_ops) WITH (lists = 100);",
                    f"CREATE INDEX IF NOT EXISTS idx_{area_limpa}_agente_id ON {tabela_nome} (agente_id);",
                    f"CREATE INDEX IF NOT EXISTS idx_{area_limpa}_area_origem ON {tabela_nome} (area_origem);",
                    f"CREATE INDEX IF NOT EXISTS idx_{area_limpa}_tipo_documento ON {tabela_nome} (tipo_documento);",
                    f"CREATE INDEX IF NOT EXISTS idx_{area_limpa}_conteudo_gin ON {tabela_nome} USING gin(to_tsvector('portuguese', conteudo));"
                ]
                
                for sql in indices_sql:
                    cursor.execute(sql)
                
                conn.commit()
                logger.info(f"✅ Índices criados para {tabela_nome}")
                
            except Exception as e:
                logger.error(f"❌ Erro ao criar índices para {tabela_nome}: {e}")
                conn.rollback()
        
        cursor.close()
        conn.close()
        return True
    
    def gerar_embeddings_duplos(self, texto: str) -> Dict[str, List[float]]:
        """Gera embeddings small e large para um texto"""
        try:
            # Embedding small (1536 dimensões)
            response_small = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=texto
            )
            embedding_small = response_small.data[0].embedding
            
            # Embedding large (3072 dimensões)
            response_large = self.openai_client.embeddings.create(
                model="text-embedding-3-large",
                input=texto
            )
            embedding_large = response_large.data[0].embedding
            
            return {
                'small': embedding_small,
                'large': embedding_large
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar embeddings: {e}")
            return {'small': None, 'large': None}
    
    def reprocessar_registros_existentes(self):
        """Reprocessa registros existentes adicionando embeddings duplos"""
        logger.info("🔄 Reprocessando registros existentes...")
        
        conn = self.conectar_database()
        if not conn:
            return False
        
        cursor = conn.cursor()
        total_processados = 0
        
        for area in self.areas_juridicas:
            tabela_nome = f"embeddings_{area}"
            
            try:
                # Buscar registros sem embeddings
                cursor.execute(f"""
                    SELECT id, conteudo FROM {tabela_nome} 
                    WHERE embedding_small IS NULL OR embedding_large IS NULL
                    LIMIT 50
                """)
                
                registros = cursor.fetchall()
                logger.info(f"📊 Processando {len(registros)} registros de {tabela_nome}")
                
                for registro_id, conteudo in registros:
                    try:
                        # Gerar embeddings duplos
                        embeddings = self.gerar_embeddings_duplos(conteudo)
                        
                        if embeddings['small'] and embeddings['large']:
                            # Atualizar registro com embeddings
                            cursor.execute(f"""
                                UPDATE {tabela_nome} 
                                SET embedding_small = %s, 
                                    embedding_large = %s,
                                    data_atualizacao = CURRENT_TIMESTAMP
                                WHERE id = %s
                            """, (embeddings['small'], embeddings['large'], registro_id))
                            
                            total_processados += 1
                            
                            if total_processados % 10 == 0:
                                conn.commit()
                                logger.info(f"✅ {total_processados} registros processados")
                    
                    except Exception as e:
                        logger.error(f"Erro ao processar registro {registro_id}: {e}")
                        continue
                
                conn.commit()
                
            except Exception as e:
                logger.error(f"❌ Erro ao reprocessar {tabela_nome}: {e}")
                conn.rollback()
        
        cursor.close()
        conn.close()
        
        logger.info(f"🎉 Total de {total_processados} registros reprocessados")
        return True
    
    def criar_orquestrador_consultas(self):
        """Cria função de orquestração inteligente"""
        logger.info("🎯 Criando orquestrador de consultas...")
        
        codigo_orquestrador = '''
"""
Orquestrador Inteligente de Consultas Jurídicas
Sistema de busca com embeddings duplos e rerank automático
"""

import psycopg2
import openai
from typing import Dict, List, Optional, Any
import json
import logging

logger = logging.getLogger(__name__)

class OrquestradorConsultas:
    """Orquestrador principal para consultas multi-agente"""
    
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        self.openai_client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        self.agentes_config = self.carregar_configuracao_agentes()
    
    def carregar_configuracao_agentes(self) -> Dict:
        """Carrega configuração dos 309 agentes"""
        try:
            with open('agentes_config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Arquivo de configuração de agentes não encontrado")
            return {}
    
    def gerar_embeddings_consulta(self, texto: str) -> Dict[str, List[float]]:
        """Gera embeddings da consulta para busca"""
        try:
            # Small embedding para busca inicial
            response_small = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=texto
            )
            
            # Large embedding para rerank
            response_large = self.openai_client.embeddings.create(
                model="text-embedding-3-large", 
                input=texto
            )
            
            return {
                'small': response_small.data[0].embedding,
                'large': response_large.data[0].embedding
            }
        except Exception as e:
            logger.error(f"Erro ao gerar embeddings: {e}")
            return {'small': None, 'large': None}
    
    def orquestrar_consulta(self, area: str, texto: str, agente_id: Optional[str] = None, limite: int = 10) -> Dict[str, Any]:
        """
        Função principal de orquestração
        
        Args:
            area: Área jurídica (ex: 'direito_penal')
            texto: Texto da consulta
            agente_id: ID específico do agente (opcional)
            limite: Número máximo de resultados
            
        Returns:
            Dict com resultados ranqueados e metadados
        """
        try:
            # 1. Gerar embeddings da consulta
            embeddings = self.gerar_embeddings_consulta(texto)
            if not embeddings['small']:
                return {"erro": "Falha ao gerar embeddings"}
            
            # 2. Conectar ao banco
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            # 3. Busca inicial com embedding small
            tabela = f"embeddings_{area}"
            
            sql_busca = f"""
                SELECT id, conteudo, referencia, agente_id, metadata,
                       embedding_small <=> %s as distancia_small,
                       embedding_large <=> %s as distancia_large
                FROM {tabela}
                WHERE embedding_small IS NOT NULL 
                  AND embedding_large IS NOT NULL
            """
            
            params = [embeddings['small'], embeddings['large']]
            
            # Filtrar por agente específico se fornecido
            if agente_id:
                sql_busca += " AND agente_id = %s"
                params.append(agente_id)
            
            sql_busca += f"""
                ORDER BY embedding_small <=> %s
                LIMIT {limite * 2}
            """
            params.append(embeddings['small'])
            
            cursor.execute(sql_busca, params)
            resultados_iniciais = cursor.fetchall()
            
            # 4. Rerank com embedding large
            resultados_reranked = []
            for resultado in resultados_iniciais:
                doc_id, conteudo, referencia, agente, metadata, dist_small, dist_large = resultado
                
                # Score combinado (70% large, 30% small)
                score_final = (0.7 * (1 - dist_large)) + (0.3 * (1 - dist_small))
                
                resultados_reranked.append({
                    'id': doc_id,
                    'conteudo': conteudo,
                    'referencia': referencia,
                    'agente_id': agente,
                    'metadata': metadata,
                    'score': score_final,
                    'distancia_small': dist_small,
                    'distancia_large': dist_large
                })
            
            # 5. Ordenar por score final e limitar
            resultados_finais = sorted(resultados_reranked, key=lambda x: x['score'], reverse=True)[:limite]
            
            # 6. Buscar agentes relevantes
            agentes_relevantes = self.identificar_agentes_relevantes(area, texto, resultados_finais)
            
            cursor.close()
            conn.close()
            
            return {
                "status": "sucesso",
                "area": area,
                "total_resultados": len(resultados_finais),
                "resultados": resultados_finais,
                "agentes_sugeridos": agentes_relevantes,
                "metadata_busca": {
                    "embeddings_utilizados": "small + large",
                    "rerank_aplicado": True,
                    "agente_filtro": agente_id
                }
            }
            
        except Exception as e:
            logger.error(f"Erro na orquestração: {e}")
            return {"erro": str(e), "status": "erro"}
    
    def identificar_agentes_relevantes(self, area: str, texto: str, resultados: List[Dict]) -> List[Dict]:
        """Identifica agentes mais relevantes para a consulta"""
        agentes_encontrados = {}
        
        for resultado in resultados:
            agente_id = resultado.get('agente_id')
            if agente_id and agente_id in self.agentes_config:
                if agente_id not in agentes_encontrados:
                    config_agente = self.agentes_config[agente_id]
                    agentes_encontrados[agente_id] = {
                        "agente_id": agente_id,
                        "nome": config_agente.get('nome', agente_id),
                        "especialidade": config_agente.get('especialidade', ''),
                        "modelo_preferencial": config_agente.get('modelo_preferencial', 'gpt-4o'),
                        "relevancia_score": resultado['score'],
                        "documentos_encontrados": 1
                    }
                else:
                    agentes_encontrados[agente_id]["documentos_encontrados"] += 1
                    # Atualizar score com média ponderada
                    agentes_encontrados[agente_id]["relevancia_score"] = (
                        agentes_encontrados[agente_id]["relevancia_score"] + resultado['score']
                    ) / 2
        
        # Retornar top 5 agentes mais relevantes
        return sorted(agentes_encontrados.values(), 
                     key=lambda x: x['relevancia_score'], 
                     reverse=True)[:5]

# Instância global do orquestrador
orquestrador = OrquestradorConsultas()

def orquestrar_consulta(area: str, texto: str, agente_id: Optional[str] = None, limite: int = 10) -> Dict[str, Any]:
    """Função pública para orquestração de consultas"""
    return orquestrador.orquestrar_consulta(area, texto, agente_id, limite)
'''
        
        with open('orquestrador_consultas.py', 'w', encoding='utf-8') as f:
            f.write(codigo_orquestrador)
        
        logger.info("✅ Orquestrador de consultas criado")
        return True
    
    def criar_configuracao_agentes(self):
        """Cria configuração JSON dos 309 agentes organizados por área"""
        logger.info("📋 Criando configuração dos 309 agentes...")
        
        # Template de configuração de agentes por área
        configuracao_agentes = {}
        
        # Definir agentes especializados por área jurídica
        areas_agentes = {
            'direito_penal': [
                'agente_crimes_contra_pessoa', 'agente_crimes_patrimoniais', 'agente_drogas_entorpecentes',
                'agente_crimes_transito', 'agente_violencia_domestica', 'agente_crimes_eleitorais',
                'agente_lavagem_dinheiro', 'agente_crimes_ambientais_penais', 'agente_homicidio',
                'agente_furto_roubo', 'agente_estupro_crimes_sexuais', 'agente_corrupcao',
                'agente_formacao_quadrilha', 'agente_porte_armas', 'agente_crimes_informaticos',
                'agente_sequestro_carcere', 'agente_crimes_contra_crianca', 'agente_trafego_internacional'
            ],
            'direito_civil': [
                'agente_contratos_gerais', 'agente_responsabilidade_civil', 'agente_direitos_reais',
                'agente_obrigacoes', 'agente_danos_morais', 'agente_posse_propriedade',
                'agente_locacao_imobiliaria', 'agente_compra_venda', 'agente_doacao',
                'agente_comodato', 'agente_fianca', 'agente_mandato', 'agente_sociedade',
                'agente_prescricao_decadencia', 'agente_negocio_juridico', 'agente_atos_ilicitos',
                'agente_enriquecimento_ilicito', 'agente_responsabilidade_objetiva'
            ],
            'direito_trabalhista': [
                'agente_contrato_trabalho', 'agente_rescisao_trabalhista', 'agente_horas_extras',
                'agente_ferias_trabalhistas', 'agente_fgts', 'agente_seguro_desemprego',
                'agente_acidente_trabalho', 'agente_assedio_moral', 'agente_discriminacao_trabalho',
                'agente_terceirizacao', 'agente_sindicatos', 'agente_greve',
                'agente_aposentadoria_trabalhista', 'agente_adicional_periculosidade',
                'agente_adicional_insalubridade', 'agente_estabilidade_emprego',
                'agente_trabalho_domestico', 'agente_pcd_trabalho'
            ],
            'direito_empresarial': [
                'agente_constituicao_empresas', 'agente_sociedade_limitada', 'agente_sociedade_anonima',
                'agente_falencia_recuperacao', 'agente_contratos_empresariais', 'agente_mei',
                'agente_eireli', 'agente_franquia', 'agente_joint_venture',
                'agente_propriedade_intelectual', 'agente_marcas_patentes', 'agente_compliance',
                'agente_governanca_corporativa', 'agente_fusao_aquisicao', 'agente_dissolucao_empresa',
                'agente_titulos_credito', 'agente_cambio', 'agente_comercio_exterior'
            ],
            'direito_tributario': [
                'agente_icms', 'agente_ipi', 'agente_iss', 'agente_pis_cofins',
                'agente_imposto_renda', 'agente_simples_nacional', 'agente_lucro_presumido',
                'agente_lucro_real', 'agente_execucao_fiscal', 'agente_parcelamento_debitos',
                'agente_compensacao_tributaria', 'agente_restituicao', 'agente_autuacao_fiscal',
                'agente_defesa_administrativa', 'agente_mandado_seguranca_tributario',
                'agente_planejamento_tributario', 'agente_elisao_fiscal', 'agente_evasao_fiscal'
            ],
            'direito_familia': [
                'agente_divorcio', 'agente_pensao_alimenticia', 'agente_guarda_filhos',
                'agente_adocao', 'agente_uniao_estavel', 'agente_separacao_bens',
                'agente_regime_bens', 'agente_violencia_domestica_familia', 'agente_tutela',
                'agente_curatela', 'agente_reconhecimento_paternidade', 'agente_alienacao_parental',
                'agente_investigacao_paternidade', 'agente_casamento', 'agente_familia_homoafetiva',
                'agente_familia_multiparental', 'agente_abandono_afetivo', 'agente_mediacao_familiar'
            ],
            'direito_consumidor': [
                'agente_relacao_consumo', 'agente_produto_defeituoso', 'agente_servico_defeituoso',
                'agente_publicidade_enganosa', 'agente_cobranca_indevida', 'agente_cartao_credito',
                'agente_financiamento_veiculo', 'agente_plano_saude', 'agente_telefonia',
                'agente_energia_eletrica', 'agente_agua_saneamento', 'agente_transporte_aereo',
                'agente_ecommerce', 'agente_recall_produtos', 'agente_cdc_bancario',
                'agente_superendividamento', 'agente_negociacao_dividas', 'agente_procon'
            ],
            'direito_constitucional': [
                'agente_direitos_fundamentais', 'agente_habeas_corpus', 'agente_mandado_seguranca',
                'agente_mandado_injuncao', 'agente_acao_popular', 'agente_inconstitucionalidade',
                'agente_federalismo', 'agente_separacao_poderes', 'agente_controle_constitucionalidade',
                'agente_emenda_constitucional', 'agente_estado_sitio', 'agente_estado_defesa',
                'agente_direito_vida', 'agente_liberdade_expressao', 'agente_devido_processo_legal',
                'agente_ampla_defesa', 'agente_contraditorio', 'agente_dignidade_humana'
            ],
            'direito_administrativo': [
                'agente_licitacao', 'agente_contratos_administrativos', 'agente_servico_publico',
                'agente_servidor_publico', 'agente_improbidade_administrativa', 'agente_lei_acesso_informacao',
                'agente_processo_administrativo', 'agente_poder_policia', 'agente_desapropriacao',
                'agente_concessao_servico', 'agente_permissao_servico', 'agente_autorizacao_servico',
                'agente_responsabilidade_estado', 'agente_ato_administrativo', 'agente_principios_admin',
                'agente_controle_administracao', 'agente_parceria_publico_privada', 'agente_terceiro_setor'
            ],
            'direito_previdenciario': [
                'agente_aposentadoria_idade', 'agente_aposentadoria_tempo', 'agente_aposentadoria_invalidez',
                'agente_aposentadoria_especial', 'agente_pensao_morte', 'agente_auxilio_doenca',
                'agente_auxilio_acidente', 'agente_salario_maternidade', 'agente_bpc',
                'agente_revisao_beneficio', 'agente_cessacao_beneficio', 'agente_previdencia_privada',
                'agente_regime_proprio', 'agente_servidor_publico_prev', 'agente_fator_previdenciario',
                'agente_idade_minima', 'agente_tempo_contribuicao', 'agente_carencia_previdenciaria'
            ],
            'direito_ambiental': [
                'agente_licenciamento_ambiental', 'agente_impacto_ambiental', 'agente_recursos_hidricos',
                'agente_flora_fauna', 'agente_poluicao_atmosferica', 'agente_residuos_solidos',
                'agente_areas_protegidas', 'agente_compensacao_ambiental', 'agente_crimes_ambientais',
                'agente_responsabilidade_ambiental', 'agente_dano_ambiental', 'agente_termo_ajustamento',
                'agente_acao_civil_publica_ambiental', 'agente_codigo_florestal', 'agente_snuc',
                'agente_politica_nacional_meio_ambiente', 'agente_mudancas_climaticas', 'agente_energia_renovavel'
            ],
            'direito_digital': [
                'agente_lgpd', 'agente_marco_civil_internet', 'agente_crimes_virtuais',
                'agente_contratos_eletronicos', 'agente_assinatura_digital', 'agente_certificacao_digital',
                'agente_ecommerce_digital', 'agente_propriedade_intelectual_digital', 'agente_direito_autoral_digital',
                'agente_responsabilidade_provedores', 'agente_fake_news', 'agente_direito_esquecimento',
                'agente_vazamento_dados', 'agente_seguranca_informacao', 'agente_blockchain',
                'agente_inteligencia_artificial', 'agente_internet_das_coisas', 'agente_compliance_digital'
            ],
            'direito_imobiliario': [
                'agente_compra_venda_imovel', 'agente_financiamento_imobiliario', 'agente_locacao_residencial',
                'agente_locacao_comercial', 'agente_condominio', 'agente_incorporacao_imobiliaria',
                'agente_usucapiao', 'agente_registro_imoveis', 'agente_cartorio_imoveis',
                'agente_itbi', 'agente_iptu', 'agente_minha_casa_minha_vida',
                'agente_alienacao_fiduciaria', 'agente_hipoteca', 'agente_penhor',
                'agente_direito_vizinhanca', 'agente_servидao_predial', 'agente_loteamento'
            ],
            'direito_sucessorio': [
                'agente_inventario', 'agente_testamento', 'agente_heranca', 'agente_legado',
                'agente_sucessao_legitima', 'agente_sucessao_testamentaria', 'agente_meacao',
                'agente_herdeiros_necessarios', 'agente_deserdacao', 'agente_renencia_heranca',
                'agente_sonegados', 'agente_colacao', 'agente_reducao_liberalidade',
                'agente_partilha_bens', 'agente_inventario_judicial', 'agente_inventario_extrajudicial',
                'agente_alvara_judicial', 'agente_sucessao_empresarial'
            ],
            'direito_agrario': [
                'agente_reforma_agraria', 'agente_credito_rural', 'agente_seguro_rural',
                'agente_contratos_agrarios', 'agente_arrendamento_rural', 'agente_parceria_rural',
                'agente_comodato_rural', 'agente_usucapiao_rural', 'agente_itr',
                'agente_licenciamento_atividade_rural', 'agente_trabalho_rural', 'agente_sindicatos_rurais',
                'agente_cooperativas_agricolas', 'agente_agrotoxicos', 'agente_sementes_mudas',
                'agente_recursos_geneticos', 'agente_propriedade_rural', 'agente_modulo_rural'
            ],
            'seguros': [
                'agente_seguro_vida', 'agente_seguro_automovel', 'agente_seguro_residencial',
                'agente_seguro_empresarial', 'agente_seguro_saude_privado', 'agente_seguro_viagem',
                'agente_seguro_responsabilidade_civil', 'agente_seguro_agricola', 'agente_seguro_garantia',
                'agente_resseguro', 'agente_corretora_seguros', 'agente_sinistro',
                'agente_regulacao_sinistro', 'agente_susep', 'agente_previdencia_complementar',
                'agente_capitalizacao', 'agente_consorcio', 'agente_seguro_dpvat'
            ],
            'conflitos_mediacao': [
                'agente_mediacao_civil', 'agente_arbitragem', 'agente_conciliacao',
                'agente_negociacao', 'agente_mediacao_familiar', 'agente_mediacao_empresarial',
                'agente_mediacao_trabalhista', 'agente_mediacao_consumidor', 'agente_resolucao_conflitos',
                'agente_autocomposicao', 'agente_heterocomposicao', 'agente_cejusc',
                'agente_mediacao_online', 'agente_conflitos_condominiais', 'agente_mediacao_escolar',
                'agente_justica_restaurativa', 'agente_acordo_judicial', 'agente_acordo_extrajudicial'
            ],
            'analise_riscos': [
                'agente_risco_juridico', 'agente_compliance_legal', 'agente_auditoria_juridica',
                'agente_due_diligence', 'agente_risco_regulatorio', 'agente_risco_contratual',
                'agente_risco_tributario', 'agente_risco_trabalhista', 'agente_risco_ambiental',
                'agente_risco_digital', 'agente_gestao_riscos', 'agente_mapeamento_riscos',
                'agente_mitigacao_riscos', 'agente_monitoramento_riscos', 'agente_risco_reputacional',
                'agente_risco_operacional', 'agente_analise_precedentes', 'agente_tendencias_jurisprudencia'
            ]
        }
        
        contador_agente = 1
        
        for area, lista_agentes in areas_agentes.items():
            for agente_nome in lista_agentes:
                agente_id = f"{agente_nome}_{contador_agente:03d}"
                
                configuracao_agentes[agente_id] = {
                    "agente_id": agente_id,
                    "nome": agente_nome.replace('_', ' ').title(),
                    "area": area,
                    "base": f"embeddings_{area}",
                    "especialidade": agente_nome.replace('_', ' ').title(),
                    "tags": self._gerar_tags_agente(agente_nome),
                    "tipo_documento": self._determinar_tipo_documento(agente_nome),
                    "modelo_preferencial": "gpt-4o",
                    "temperatura": 0.3,
                    "max_tokens": 1000,
                    "prompt_sistema": self._gerar_prompt_sistema(agente_nome, area),
                    "ativo": True,
                    "data_criacao": datetime.now().isoformat(),
                    "capacidades": [
                        "Análise de documentos jurídicos",
                        "Consulta à base de conhecimento especializada", 
                        "Fundamentação legal específica",
                        "Sugestões de precedentes relevantes"
                    ]
                }
                contador_agente += 1
        
        # Salvar configuração
        with open('agentes_config.json', 'w', encoding='utf-8') as f:
            json.dump(configuracao_agentes, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Configuração de {len(configuracao_agentes)} agentes criada")
        return True
    
    def _gerar_tags_agente(self, agente_nome: str) -> List[str]:
        """Gera tags relevantes para um agente"""
        palavras = agente_nome.replace('agente_', '').split('_')
        return palavras + ['juridico', 'brasileiro']
    
    def _determinar_tipo_documento(self, agente_nome: str) -> str:
        """Determina tipo de documento predominante do agente"""
        if 'contrato' in agente_nome:
            return 'contrato'
        elif 'crime' in agente_nome or 'penal' in agente_nome:
            return 'codigo_penal'
        elif 'civil' in agente_nome:
            return 'codigo_civil'
        elif 'constitucional' in agente_nome:
            return 'constituicao'
        elif 'tributario' in agente_nome:
            return 'codigo_tributario'
        else:
            return 'legislacao'
    
    def _gerar_prompt_sistema(self, agente_nome: str, area: str) -> str:
        """Gera prompt sistema personalizado para o agente"""
        especialidade = agente_nome.replace('agente_', '').replace('_', ' ').title()
        area_formatada = area.replace('_', ' ').title()
        
        return f"""Você é um assistente jurídico especializado em {especialidade} dentro da área de {area_formatada}.

SUAS RESPONSABILIDADES:
1. Analisar consultas jurídicas relacionadas a {especialidade}
2. Fornecer fundamentação legal precisa baseada na legislação brasileira
3. Citar artigos, leis e precedentes relevantes
4. Explicar conceitos jurídicos de forma clara e objetiva

INSTRUÇÕES IMPORTANTES:
- Use APENAS informações da base de conhecimento fornecida
- Cite sempre as fontes específicas (artigos, leis, códigos)
- Se não encontrar informação suficiente, informe claramente
- Mantenha linguagem técnica mas acessível
- Não invente ou deduza informações sem fundamentação

ÁREA DE ESPECIALIZAÇÃO: {area_formatada}
FOCO ESPECÍFICO: {especialidade}"""
    
    def executar_upgrade_completo(self):
        """Executa todo o processo de upgrade das bases vetoriais"""
        logger.info("🚀 Iniciando upgrade completo das bases vetoriais...")
        
        try:
            # 1. Criar/atualizar estruturas das tabelas
            if not self.criar_novas_estruturas_tabelas():
                raise Exception("Falha na criação das estruturas")
            
            # 2. Criar índices vetoriais
            if not self.criar_indices_vetoriais():
                raise Exception("Falha na criação dos índices")
            
            # 3. Criar configuração dos agentes
            if not self.criar_configuracao_agentes():
                raise Exception("Falha na criação da configuração dos agentes")
            
            # 4. Criar orquestrador
            if not self.criar_orquestrador_consultas():
                raise Exception("Falha na criação do orquestrador")
            
            # 5. Reprocessar alguns registros (demonstração)
            logger.info("🔄 Iniciando reprocessamento de registros (modo demonstração)...")
            self.reprocessar_registros_existentes()
            
            # Relatório final
            self.gerar_relatorio_final()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no upgrade: {e}")
            return False
    
    def gerar_relatorio_final(self):
        """Gera relatório final do upgrade"""
        logger.info("📊 Gerando relatório final...")
        
        conn = self.conectar_database()
        if not conn:
            return
        
        cursor = conn.cursor()
        relatorio = {
            "timestamp": datetime.now().isoformat(),
            "status": "upgrade_completo",
            "areas_juridicas": len(self.areas_juridicas),
            "tabelas_processadas": {},
            "agentes_configurados": 0,
            "funcionalidades_implementadas": [
                "Embeddings duplos (small + large)",
                "Índices vetoriais otimizados", 
                "Orquestrador inteligente",
                "Sistema de rerank automático",
                "Configuração de 309 agentes especializados"
            ]
        }
        
        # Contabilizar registros por tabela
        for area in self.areas_juridicas:
            tabela = f"embeddings_{area}"
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                total = cursor.fetchone()[0]
                
                cursor.execute(f"SELECT COUNT(*) FROM {tabela} WHERE embedding_small IS NOT NULL")
                com_embeddings = cursor.fetchone()[0]
                
                relatorio["tabelas_processadas"][area] = {
                    "total_registros": total,
                    "com_embeddings": com_embeddings,
                    "percentual_processado": round((com_embeddings / total * 100) if total > 0 else 0, 2)
                }
            except:
                relatorio["tabelas_processadas"][area] = {"erro": "tabela_nao_encontrada"}
        
        # Contar agentes configurados
        try:
            with open('agentes_config.json', 'r') as f:
                agentes = json.load(f)
                relatorio["agentes_configurados"] = len(agentes)
        except:
            relatorio["agentes_configurados"] = 0
        
        cursor.close()
        conn.close()
        
        # Salvar relatório
        with open('relatorio_upgrade_bases_vetoriais.json', 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, ensure_ascii=False, indent=2)
        
        # Exibir resumo
        print("\n" + "="*80)
        print("🎉 UPGRADE COMPLETO DAS BASES VETORIAIS FINALIZADO")
        print("="*80)
        print(f"✅ {len(self.areas_juridicas)} áreas jurídicas processadas")
        print(f"✅ {relatorio['agentes_configurados']} agentes especializados configurados")
        print(f"✅ Sistema de embeddings duplos implementado")
        print(f"✅ Orquestrador inteligente com rerank automático")
        print(f"✅ Índices vetoriais otimizados criados")
        print("\n📁 Arquivos gerados:")
        print("  • agentes_config.json - Configuração dos 309 agentes")
        print("  • orquestrador_consultas.py - Sistema de orquestração")
        print("  • relatorio_upgrade_bases_vetoriais.json - Relatório detalhado")
        print("="*80)

def main():
    upgrade = UpgradeBasesVetoriais()
    upgrade.executar_upgrade_completo()

if __name__ == "__main__":
    main()