"""
API de Integração Qdrant para Sistema Jurídico
Endpoints completos para busca vetorial avançada
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from flask import Blueprint, request, jsonify
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, SearchRequest
import openai

logger = logging.getLogger(__name__)

class QdrantJuridicoAPI:
    """API completa para integração Qdrant com sistema jurídico"""
    
    def __init__(self):
        # Cliente Qdrant compartilhado (usando instância global)
        self.qdrant_client = None
        self.openai_client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        
        # Áreas jurídicas disponíveis
        self.areas_disponiveis = [
            'direito_penal_integrado', 'direito_civil', 'direito_agrario',
            'direito_ambiental', 'direito_tributario', 'direito_constitucional',
            'direito_administrativo', 'direito_familia', 'direito_sucessorio',
            'direito_empresarial', 'direito_trabalhista', 'direito_previdenciario',
            'direito_consumidor', 'direito_imobiliario', 'direito_digital',
            'seguros', 'conflitos_mediacao', 'analise_riscos'
        ]
        
        self._init_qdrant_client()
    
    def _init_qdrant_client(self):
        """Inicializa cliente Qdrant com dados jurídicos brasileiros"""
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams, PointStruct
            import uuid
            
            # Configuração do cluster Qdrant
            qdrant_url = os.environ.get('QDRANT_URL', ':memory:')
            qdrant_api_key = os.environ.get('QDRANT_API_KEY')
            
            if qdrant_url == ':memory:':
                self.qdrant_client = QdrantClient(":memory:")
                logger.info("✅ Cliente Qdrant inicializado em memória")
            else:
                if qdrant_api_key:
                    self.qdrant_client = QdrantClient(
                        url=qdrant_url,
                        api_key=qdrant_api_key
                    )
                    logger.info(f"✅ Cliente Qdrant conectado ao cluster: {qdrant_url}")
                else:
                    self.qdrant_client = QdrantClient(url=qdrant_url)
                    logger.info(f"✅ Cliente Qdrant conectado sem API key: {qdrant_url}")
            
            # Inicializar com dados jurídicos brasileiros reais
            self._popular_dados_juridicos()
            
        except Exception as e:
            logger.error(f"Erro ao inicializar Qdrant: {e}")
            # Fallback para memória se cluster falhar
            try:
                self.qdrant_client = QdrantClient(":memory:")
                self._popular_dados_juridicos()
                logger.warning("Usando Qdrant em memória como fallback")
            except Exception as fallback_error:
                logger.error(f"Erro no fallback: {fallback_error}")
                self.qdrant_client = None
    
    def _popular_dados_juridicos(self):
        """Popula Qdrant com dados jurídicos brasileiros autênticos"""
        from qdrant_client.models import Distance, VectorParams, PointStruct
        import uuid
        
        # Dados do Código Penal e Civil brasileiro
        dados_juridicos = {
            'direito_penal_integrado': [
                {
                    'conteudo': 'Art. 121. Matar alguém: Pena - reclusão, de seis a vinte anos. § 1º Se o agente comete o crime impelido por motivo de relevante valor social ou moral, ou sob o domínio de violenta emoção, logo em seguida a injusta provocação da vítima, o juiz pode reduzir a pena de um sexto a um terço.',
                    'referencia': 'Código Penal - Art. 121',
                    'tipo_documento': 'artigo_lei',
                    'artigo_numero': '121',
                    'titulo': 'Dos Crimes Contra a Vida'
                },
                {
                    'conteudo': 'Art. 155. Subtrair, para si ou para outrem, coisa alheia móvel: Pena - reclusão, de um a quatro anos, e multa. § 1º A pena aumenta-se de um terço, se o crime é praticado durante o repouso noturno.',
                    'referencia': 'Código Penal - Art. 155',
                    'tipo_documento': 'artigo_lei',
                    'artigo_numero': '155',
                    'titulo': 'Dos Crimes Contra o Patrimônio'
                }
            ],
            'direito_civil': [
                {
                    'conteudo': 'Art. 186. Aquele que, por ação ou omissão voluntária, negligência ou imprudência, violar direito e causar dano a outrem, ainda que exclusivamente moral, comete ato ilícito.',
                    'referencia': 'Código Civil - Art. 186',
                    'tipo_documento': 'artigo_lei',
                    'artigo_numero': '186',
                    'titulo': 'Dos Atos Ilícitos'
                },
                {
                    'conteudo': 'Art. 927. Aquele que, por ato ilícito (arts. 186 e 187), causar dano a outrem, fica obrigado a repará-lo. Parágrafo único. Haverá obrigação de reparar o dano, independentemente de culpa, nos casos especificados em lei.',
                    'referencia': 'Código Civil - Art. 927',
                    'tipo_documento': 'artigo_lei',
                    'artigo_numero': '927',
                    'titulo': 'Da Obrigação de Indenizar'
                }
            ]
        }
        
        try:
            for area, documentos in dados_juridicos.items():
                collection_name = f"juridico_{area}"
                
                # Criar coleção
                self.qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config={
                        "small": VectorParams(size=1536, distance=Distance.COSINE),
                        "large": VectorParams(size=3072, distance=Distance.COSINE)
                    }
                )
                
                # Inserir documentos
                pontos = []
                for doc in documentos:
                    try:
                        # Gerar embeddings
                        embeddings = self.gerar_embedding_duplo(doc['conteudo'])
                        
                        if embeddings['small'] and embeddings['large']:
                            ponto = PointStruct(
                                id=str(uuid.uuid4()),
                                vector={
                                    "small": embeddings['small'],
                                    "large": embeddings['large']
                                },
                                payload={
                                    "conteudo": doc['conteudo'],
                                    "referencia": doc['referencia'],
                                    "tipo_documento": doc['tipo_documento'],
                                    "artigo_numero": doc['artigo_numero'],
                                    "titulo": doc['titulo'],
                                    "area_origem": area
                                }
                            )
                            pontos.append(ponto)
                    except Exception as e:
                        logger.warning(f"Erro ao processar documento: {e}")
                
                if pontos:
                    self.qdrant_client.upsert(collection_name=collection_name, points=pontos)
                    logger.info(f"✅ {len(pontos)} documentos inseridos em {collection_name}")
                    
        except Exception as e:
            logger.error(f"Erro ao popular dados jurídicos: {e}")
    
    def gerar_embedding_duplo(self, texto: str) -> Dict[str, List[float]]:
        """Gera embeddings small e large"""
        try:
            texto_limitado = texto[:8000]
            
            # Small embedding
            response_small = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=texto_limitado
            )
            
            # Large embedding  
            response_large = self.openai_client.embeddings.create(
                model="text-embedding-3-large",
                input=texto_limitado
            )
            
            return {
                'small': response_small.data[0].embedding,
                'large': response_large.data[0].embedding
            }
        except Exception as e:
            logger.error(f"Erro ao gerar embeddings: {e}")
            return {'small': None, 'large': None}
    
    def gerar_embedding_busca(self, texto: str, modelo: str = "text-embedding-3-small") -> List[float]:
        """Gera embedding para busca com modelo específico"""
        try:
            response = self.openai_client.embeddings.create(
                model=modelo,
                input=texto[:8000]  # Limitar texto
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            return []
    
    def buscar_documentos(self, area: str, consulta: str, limite: int = 10, 
                         filtros: Optional[Dict] = None, usar_rerank: bool = True) -> Dict[str, Any]:
        """Busca avançada com rerank automático"""
        try:
            collection_name = f"juridico_{area}"
            
            # Verificar se área existe
            if area not in self.areas_disponiveis:
                return {
                    "erro": f"Área '{area}' não disponível",
                    "areas_disponiveis": self.areas_disponiveis
                }
            
            # Gerar embeddings para busca (small para velocidade)
            embedding_busca = self.gerar_embedding_busca(consulta)
            if not embedding_busca:
                return {"erro": "Falha ao gerar embedding da consulta"}
            
            # Preparar filtros Qdrant
            filtro_qdrant = None
            if filtros:
                condicoes = []
                for campo, valor in filtros.items():
                    condicoes.append(FieldCondition(key=campo, match=MatchValue(value=valor)))
                if condicoes:
                    filtro_qdrant = Filter(must=condicoes)
            
            # Busca inicial (mais resultados para rerank)
            limite_inicial = limite * 3 if usar_rerank else limite
            
            resultados_iniciais = self.qdrant_client.query_points(
                collection_name=collection_name,
                query=embedding_busca,
                query_filter=filtro_qdrant,
                limit=limite_inicial,
                with_payload=True
            ).points
            
            if not resultados_iniciais:
                return {
                    "resultados": [],
                    "total_resultados": 0,
                    "area": area,
                    "consulta": consulta,
                    "metodo": "busca_inicial"
                }
            
            # Aplicar rerank se solicitado
            if usar_rerank and len(resultados_iniciais) > limite:
                embedding_large = self.gerar_embedding_busca(consulta, "text-embedding-3-large")
                if embedding_large:
                    # Rerank com embedding large para precisão máxima
                    resultados_rerank = self.qdrant_client.query_points(
                        collection_name=collection_name,
                        query=embedding_large,
                        query_filter=filtro_qdrant,
                        limit=limite,
                        with_payload=True
                    ).points
                    resultados_finais = resultados_rerank
                    metodo = "busca_com_rerank"
                else:
                    resultados_finais = resultados_iniciais[:limite]
                    metodo = "busca_inicial_limitada"
            else:
                resultados_finais = resultados_iniciais[:limite]
                metodo = "busca_inicial"
            
            # Formatar resultados
            documentos = []
            for resultado in resultados_finais:
                doc = {
                    "id": resultado.id,
                    "score": round(resultado.score, 4),
                    "conteudo": resultado.payload.get("conteudo", ""),
                    "referencia": resultado.payload.get("referencia", ""),
                    "tipo_documento": resultado.payload.get("tipo_documento", ""),
                    "artigo_numero": resultado.payload.get("artigo_numero", ""),
                    "capitulo": resultado.payload.get("capitulo", ""),
                    "titulo": resultado.payload.get("titulo", ""),
                    "metadata": resultado.payload.get("metadata", {}),
                    "area_origem": resultado.payload.get("area_origem", area)
                }
                documentos.append(doc)
            
            return {
                "resultados": documentos,
                "total_resultados": len(documentos),
                "area": area,
                "consulta": consulta,
                "metodo": metodo,
                "filtros_aplicados": filtros or {},
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro na busca Qdrant: {e}")
            return {
                "erro": str(e),
                "area": area,
                "consulta": consulta
            }
    
    def buscar_similaridade(self, area: str, texto_referencia: str, limite: int = 5) -> Dict[str, Any]:
        """Busca por similaridade com texto de referência"""
        try:
            collection_name = f"juridico_{area}"
            
            # Gerar embedding do texto de referência
            embedding_ref = self.gerar_embedding_busca(texto_referencia, "text-embedding-3-large")
            if not embedding_ref:
                return {"erro": "Falha ao gerar embedding de referência"}
            
            # Buscar documentos similares
            resultados = self.qdrant_client.query_points(
                collection_name=collection_name,
                query=embedding_ref,
                limit=limite,
                with_payload=True
            ).points
            
            # Formatar resultados com índice de similaridade
            documentos_similares = []
            for resultado in resultados:
                similaridade = round(resultado.score * 100, 2)  # Converter para percentual
                doc = {
                    "id": resultado.id,
                    "similaridade_percentual": similaridade,
                    "conteudo": resultado.payload.get("conteudo", "")[:500] + "...",  # Resumo
                    "referencia": resultado.payload.get("referencia", ""),
                    "tipo_documento": resultado.payload.get("tipo_documento", ""),
                    "artigo_numero": resultado.payload.get("artigo_numero", "")
                }
                documentos_similares.append(doc)
            
            return {
                "documentos_similares": documentos_similares,
                "total_encontrados": len(documentos_similares),
                "area": area,
                "texto_referencia": texto_referencia[:200] + "...",
                "modelo_embedding": "text-embedding-3-large"
            }
            
        except Exception as e:
            logger.error(f"Erro na busca de similaridade: {e}")
            return {"erro": str(e)}
    
    def obter_status_sistema(self) -> Dict[str, Any]:
        """Retorna status completo do sistema Qdrant"""
        try:
            status_colecoes = {}
            
            for area in self.areas_disponiveis:
                collection_name = f"juridico_{area}"
                try:
                    info = self.qdrant_client.get_collection(collection_name)
                    status_colecoes[area] = {
                        "pontos_total": info.points_count,
                        "status": info.status.value,
                        "configuracao_vetores": len(info.config.params.vectors),
                        "disponivel": True
                    }
                except:
                    status_colecoes[area] = {
                        "disponivel": False,
                        "erro": "Coleção não encontrada"
                    }
            
            # Calcular estatísticas gerais
            total_documentos = sum(
                col.get("pontos_total", 0) for col in status_colecoes.values() 
                if col.get("disponivel", False)
            )
            
            areas_ativas = sum(
                1 for col in status_colecoes.values() 
                if col.get("disponivel", False)
            )
            
            return {
                "status_geral": "operacional",
                "total_documentos": total_documentos,
                "areas_ativas": areas_ativas,
                "total_areas": len(self.areas_disponiveis),
                "colecoes": status_colecoes,
                "versao_embedding": "text-embedding-3-large",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status_geral": "erro",
                "erro": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Instância global da API (será inicializada quando necessário)
qdrant_api = None

def get_qdrant_api():
    """Obtém instância da API Qdrant, criando se necessário"""
    global qdrant_api
    if qdrant_api is None:
        qdrant_api = QdrantJuridicoAPI()
    return qdrant_api

# Blueprint Flask
api_qdrant_bp = Blueprint('api_qdrant', __name__)

@api_qdrant_bp.route('/api/qdrant/buscar', methods=['POST'])
def endpoint_buscar():
    """Endpoint para busca avançada"""
    try:
        dados = request.get_json()
        
        area = dados.get('area', '').lower()
        consulta = dados.get('consulta', '')
        limite = dados.get('limite', 10)
        filtros = dados.get('filtros', {})
        usar_rerank = dados.get('usar_rerank', True)
        
        if not area or not consulta:
            return jsonify({
                "erro": "Parâmetros 'area' e 'consulta' são obrigatórios"
            }), 400
        
        resultado = get_qdrant_api().buscar_documentos(
            area=area,
            consulta=consulta,
            limite=limite,
            filtros=filtros,
            usar_rerank=usar_rerank
        )
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@api_qdrant_bp.route('/api/qdrant/similaridade', methods=['POST'])
def endpoint_similaridade():
    """Endpoint para busca por similaridade"""
    try:
        dados = request.get_json()
        
        area = dados.get('area', '').lower()
        texto_referencia = dados.get('texto_referencia', '')
        limite = dados.get('limite', 5)
        
        if not area or not texto_referencia:
            return jsonify({
                "erro": "Parâmetros 'area' e 'texto_referencia' são obrigatórios"
            }), 400
        
        resultado = get_qdrant_api().buscar_similaridade(
            area=area,
            texto_referencia=texto_referencia,
            limite=limite
        )
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@api_qdrant_bp.route('/api/qdrant/areas', methods=['GET'])
def endpoint_areas():
    """Lista todas as áreas jurídicas disponíveis"""
    return jsonify({
        "areas_disponiveis": get_qdrant_api().areas_disponiveis,
        "total": len(get_qdrant_api().areas_disponiveis),
        "formato_collection": "juridico_{area}"
    })

@api_qdrant_bp.route('/api/qdrant/status', methods=['GET'])
def endpoint_status():
    """Status completo do sistema Qdrant"""
    return jsonify(get_qdrant_api().obter_status_sistema())

@api_qdrant_bp.route('/api/qdrant/health', methods=['GET'])
def endpoint_health():
    """Health check rápido"""
    try:
        # Teste rápido de conectividade
        collections = get_qdrant_api().qdrant_client.get_collections()
        return jsonify({
            "status": "healthy",
            "collections_count": len(collections.collections),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "erro": str(e),
            "timestamp": datetime.now().isoformat()
        }), 503

def registrar_api_qdrant(app):
    """Registra a API Qdrant na aplicação Flask"""
    app.register_blueprint(api_qdrant_bp)
    logger.info("✅ API Qdrant registrada com endpoints:")
    logger.info("   • POST /api/qdrant/buscar")
    logger.info("   • POST /api/qdrant/similaridade")
    logger.info("   • GET /api/qdrant/areas")
    logger.info("   • GET /api/qdrant/status")
    logger.info("   • GET /api/qdrant/health")