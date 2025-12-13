
"""
Sistema de Busca Avançado com Qdrant
Implementa busca vetorial sem limitações de dimensões
"""

import os
import logging
from typing import Dict, List, Optional, Any
import openai
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

logger = logging.getLogger(__name__)

class BuscaQdrantJuridica:
    """Sistema de busca jurídica com Qdrant"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        # Usar Qdrant em memória (em produção usar servidor dedicado)
        self.qdrant_client = QdrantClient(":memory:")
        
        self.areas_juridicas = [
            'direito_penal_integrado', 'direito_civil', 'direito_agrario',
            'direito_ambiental', 'direito_tributario', 'direito_constitucional',
            'direito_administrativo', 'direito_familia', 'direito_sucessorio',
            'direito_empresarial', 'direito_trabalhista', 'direito_previdenciario',
            'direito_consumidor', 'direito_imobiliario', 'direito_digital',
            'seguros', 'conflitos_mediacao', 'analise_riscos'
        ]
    
    def buscar_documentos_juridicos(self, area: str, consulta: str, 
                                   limite: int = 10, 
                                   filtros: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Busca avançada de documentos jurídicos com Qdrant
        
        Args:
            area: Área jurídica
            consulta: Texto da consulta
            limite: Número de resultados
            filtros: Filtros adicionais (tipo_documento, etc.)
        """
        try:
            collection_name = f"juridico_{area}"
            
            # Gerar embeddings da consulta
            embeddings = self.gerar_embeddings_consulta(consulta)
            if not embeddings['small']:
                return {"erro": "Falha ao gerar embeddings"}
            
            # Preparar filtros Qdrant
            qdrant_filter = None
            if filtros:
                conditions = []
                for campo, valor in filtros.items():
                    conditions.append(
                        FieldCondition(key=campo, match=MatchValue(value=valor))
                    )
                
                if conditions:
                    qdrant_filter = Filter(must=conditions)
            
            # Busca com embedding small (mais rápida)
            resultados_small = self.qdrant_client.search(
                collection_name=collection_name,
                query_vector=("small", embeddings['small']),
                query_filter=qdrant_filter,
                limit=limite * 2,
                with_payload=True
            )
            
            # Rerank com embedding large (mais preciso)
            resultados_reranked = []
            
            for result in resultados_small:
                # Segunda busca com embedding large para rerank
                resultado_large = self.qdrant_client.search(
                    collection_name=collection_name,
                    query_vector=("large", embeddings['large']),
                    query_filter=Filter(
                        must=[FieldCondition(key="id", match=MatchValue(value=result.id))]
                    ),
                    limit=1,
                    with_payload=True
                )
                
                if resultado_large:
                    # Score combinado (70% large, 30% small)
                    score_small = result.score
                    score_large = resultado_large[0].score
                    score_final = (0.7 * score_large) + (0.3 * score_small)
                    
                    resultados_reranked.append({
                        'id': result.id,
                        'score': round(score_final, 4),
                        'score_small': round(score_small, 4),
                        'score_large': round(score_large, 4),
                        'conteudo': result.payload.get('conteudo', '')[:500] + "...",
                        'referencia': result.payload.get('referencia', ''),
                        'area_origem': result.payload.get('area_origem', ''),
                        'tipo_documento': result.payload.get('tipo_documento', ''),
                        'artigo_numero': result.payload.get('artigo_numero', ''),
                        'metadata': result.payload.get('metadata', {})
                    })
            
            # Ordenar por score final e limitar
            resultados_finais = sorted(resultados_reranked, 
                                     key=lambda x: x['score'], 
                                     reverse=True)[:limite]
            
            return {
                "status": "sucesso",
                "area": area,
                "total_resultados": len(resultados_finais),
                "resultados": resultados_finais,
                "estrategia": "qdrant_embedding_duplo_rerank",
                "filtros_aplicados": filtros or {}
            }
            
        except Exception as e:
            logger.error(f"Erro na busca Qdrant: {e}")
            return {"erro": str(e), "status": "erro"}
    
    def gerar_embeddings_consulta(self, texto: str) -> Dict[str, List[float]]:
        """Gera embeddings para consulta"""
        try:
            # Small embedding
            response_small = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=texto[:8000]
            )
            
            # Large embedding (sem limitações de dimensão)
            response_large = self.openai_client.embeddings.create(
                model="text-embedding-3-large",
                input=texto[:8000]
            )
            
            return {
                'small': response_small.data[0].embedding,
                'large': response_large.data[0].embedding
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar embeddings: {e}")
            return {'small': None, 'large': None}
    
    def buscar_por_similaridade(self, area: str, texto_referencia: str, 
                               limite: int = 5) -> List[Dict]:
        """Busca documentos similares a um texto de referência"""
        try:
            collection_name = f"juridico_{area}"
            
            embeddings = self.gerar_embeddings_consulta(texto_referencia)
            if not embeddings['large']:
                return []
            
            # Usar embedding large para máxima precisão
            resultados = self.qdrant_client.search(
                collection_name=collection_name,
                query_vector=("large", embeddings['large']),
                limit=limite,
                with_payload=True
            )
            
            documentos_similares = []
            for result in resultados:
                documentos_similares.append({
                    'id': result.id,
                    'score': round(result.score, 4),
                    'conteudo': result.payload.get('conteudo', '')[:300] + "...",
                    'referencia': result.payload.get('referencia', ''),
                    'tipo_documento': result.payload.get('tipo_documento', '')
                })
            
            return documentos_similares
            
        except Exception as e:
            logger.error(f"Erro na busca por similaridade: {e}")
            return []
    
    def buscar_com_filtros_avancados(self, area: str, consulta: str,
                                   tipo_documento: Optional[str] = None,
                                   artigo_numero: Optional[str] = None,
                                   limite: int = 10) -> Dict[str, Any]:
        """Busca com filtros avançados específicos"""
        filtros = {}
        
        if tipo_documento:
            filtros['tipo_documento'] = tipo_documento
        
        if artigo_numero:
            filtros['artigo_numero'] = artigo_numero
        
        return self.buscar_documentos_juridicos(area, consulta, limite, filtros)
    
    def obter_estatisticas_colecao(self, area: str) -> Dict[str, Any]:
        """Obtém estatísticas de uma coleção"""
        try:
            collection_name = f"juridico_{area}"
            
            info = self.qdrant_client.get_collection(collection_name)
            
            return {
                "nome_colecao": collection_name,
                "total_pontos": info.points_count,
                "status": info.status,
                "config_vetores": str(info.config.params.vectors)
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {"erro": str(e)}

# Instância global
busca_qdrant = BuscaQdrantJuridica()

def buscar_juridico_qdrant(area: str, consulta: str, limite: int = 10, **filtros) -> Dict[str, Any]:
    """Função principal para busca jurídica com Qdrant"""
    return busca_qdrant.buscar_documentos_juridicos(area, consulta, limite, filtros)

def buscar_similaridade_qdrant(area: str, texto_referencia: str, limite: int = 5) -> List[Dict]:
    """Função para busca por similaridade"""
    return busca_qdrant.buscar_por_similaridade(area, texto_referencia, limite)
