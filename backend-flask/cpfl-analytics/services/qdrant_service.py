"""
Serviço de integração com Qdrant para o sistema CPFL
Gerencia embeddings e busca semântica de processos jurídicos
"""

import os
from typing import List, Dict, Optional, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, Range
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

class QdrantService:
    """Serviço para interação com Qdrant Cloud"""
    
    COLLECTION_NAME = "cpfl_processos"
    EMBEDDING_MODEL = "text-embedding-3-large"
    VECTOR_SIZE = 3072
    
    def __init__(self):
        """Inicializa cliente Qdrant e OpenAI"""
        qdrant_url = os.getenv('QDRANT_URL', 'http://localhost:6333')
        qdrant_api_key = os.getenv('QDRANT_API_KEY')
        
        self.client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
            timeout=60
        )
        
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        logger.info(f"✅ Qdrant Service inicializado: {qdrant_url}")
    
    def initialize_collection(self) -> bool:
        """Cria collection no Qdrant se não existir"""
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.COLLECTION_NAME for c in collections)
            
            if exists:
                logger.info(f"✅ Collection '{self.COLLECTION_NAME}' já existe")
                return True
            
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=Distance.COSINE
                )
            )
            
            logger.info(f"✅ Collection '{self.COLLECTION_NAME}' criada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar collection: {e}")
            return False
    
    def generate_embedding(self, text: str) -> List[float]:
        """Gera embedding usando OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                model=self.EMBEDDING_MODEL,
                input=text,
                encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"❌ Erro ao gerar embedding: {e}")
            raise
    
    def index_processos(self, processos: List[Dict[str, Any]], batch_size: int = 50) -> int:
        """Indexa processos no Qdrant em batches"""
        total_indexed = 0
        
        try:
            for i in range(0, len(processos), batch_size):
                batch = processos[i:i + batch_size]
                
                points = []
                for processo in batch:
                    embedding = self.generate_embedding(processo['texto'])
                    
                    point = PointStruct(
                        id=processo['id'],
                        vector=embedding,
                        payload={
                            'texto': processo['texto'],
                            **processo['metadata']
                        }
                    )
                    points.append(point)
                
                self.client.upsert(
                    collection_name=self.COLLECTION_NAME,
                    points=points,
                    wait=True
                )
                
                total_indexed += len(batch)
                logger.info(f"✅ Indexados {total_indexed}/{len(processos)} processos")
            
            return total_indexed
            
        except Exception as e:
            logger.error(f"❌ Erro ao indexar processos: {e}")
            raise
    
    def search_similar_processos(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Busca processos similares usando RAG"""
        try:
            query_embedding = self.generate_embedding(query)
            
            qdrant_filter = self._build_filter(filters) if filters else None
            
            results = self.client.search(
                collection_name=self.COLLECTION_NAME,
                query_vector=query_embedding,
                limit=limit,
                query_filter=qdrant_filter,
                with_payload=True
            )
            
            return [
                {
                    'id': result.id,
                    'score': result.score,
                    'processo': result.payload
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"❌ Erro na busca semântica: {e}")
            return []
    
    def _build_filter(self, filters: Dict[str, Any]) -> Optional[Filter]:
        """Constrói filtros para Qdrant"""
        must_conditions = []
        
        if filters.get('causa_raiz'):
            must_conditions.append(
                FieldCondition(
                    key="causa_raiz",
                    match=MatchValue(value=filters['causa_raiz'])
                )
            )
        
        if filters.get('comarca'):
            must_conditions.append(
                FieldCondition(
                    key="comarca",
                    match=MatchValue(value=filters['comarca'])
                )
            )
        
        if filters.get('fase'):
            must_conditions.append(
                FieldCondition(
                    key="fase",
                    match=MatchValue(value=filters['fase'])
                )
            )
        
        if filters.get('apenas_favoraveis_cpfl'):
            must_conditions.append(
                FieldCondition(
                    key="favoravel_cpfl",
                    match=MatchValue(value=True)
                )
            )
        
        if filters.get('valor_minimo'):
            must_conditions.append(
                FieldCondition(
                    key="valor_envolvido",
                    range=Range(gte=float(filters['valor_minimo']))
                )
            )
        
        return Filter(must=must_conditions) if must_conditions else None
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da collection"""
        try:
            info = self.client.get_collection(self.COLLECTION_NAME)
            return {
                'total_pontos': info.points_count,
                'vector_size': info.config.params.vectors.size,
                'distancia': info.config.params.vectors.distance.value
            }
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {}

qdrant_service = QdrantService()
