"""
Sistema de Cache Semântico Inteligente
Implementa cache baseado em similaridade semântica para otimizar consultas
"""

import os
import json
import logging
import pickle
import hashlib
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import redis
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Entrada do cache semântico"""
    query: str
    query_embedding: List[float]
    response: str
    metadata: Dict[str, Any]
    legal_area: str
    confidence_score: float
    created_at: datetime
    accessed_count: int
    last_accessed: datetime
    expiry_date: Optional[datetime] = None

@dataclass
class CacheHit:
    """Resultado de acerto no cache"""
    entry: CacheEntry
    similarity_score: float
    is_exact_match: bool

class SemanticCacheSystem:
    """
    Sistema de cache semântico para otimização de consultas jurídicas
    Usa embeddings para encontrar consultas similares
    """
    
    def __init__(self):
        # Configurações do cache
        self.similarity_threshold = 0.92  # Muito similar
        self.max_cache_size = 10000
        self.default_ttl_hours = 24
        
        # TTL por tipo de conteúdo (em horas)
        self.ttl_by_content_type = {
            "basic_query": 168,      # 1 semana
            "complex_analysis": 720, # 30 dias
            "critical_case": 2160,   # 90 dias
            "legislation": 8760,     # 1 ano (legislação muda pouco)
            "jurisprudence": 2160    # 90 dias
        }
        
        # Cache em memória para acesso rápido
        self.memory_cache: Dict[str, CacheEntry] = {}
        
        # Índice de embeddings para busca eficiente
        self.embedding_index: List[Tuple[str, np.ndarray]] = []
        
        # Inicializar Redis para persistência
        self._initialize_redis()
        
        # Inicializar sistema de embeddings
        self._initialize_embedding_system()
        
        # Carregar cache existente
        self._load_cache_from_redis()
    
    def _initialize_redis(self):
        """Inicializa conexão Redis para persistência do cache"""
        try:
            # Tentar conectar ao Redis (se disponível)
            self.redis_client = redis.Redis(
                host=os.environ.get('REDIS_HOST', 'localhost'),
                port=int(os.environ.get('REDIS_PORT', 6379)),
                db=int(os.environ.get('REDIS_DB', 0)),
                decode_responses=False,  # Manter bytes para pickle
                socket_timeout=5
            )
            
            # Testar conexão
            self.redis_client.ping()
            self.redis_available = True
            logger.info("✅ Redis conectado para cache semântico")
            
        except Exception as e:
            logger.warning(f"⚠️ Redis não disponível: {e}. Usando cache em memória apenas.")
            self.redis_client = None
            self.redis_available = False
    
    def _initialize_embedding_system(self):
        """Inicializa sistema de embeddings para cache"""
        try:
            from .hybrid_embedding_system import HybridEmbeddingSystem
            self.embedding_system = HybridEmbeddingSystem()
            logger.info("✅ Sistema de embeddings inicializado para cache")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar sistema de embeddings: {e}")
            self.embedding_system = None
    
    def _load_cache_from_redis(self):
        """Carrega cache existente do Redis"""
        if not self.redis_available:
            return
        
        try:
            # Carregar todas as chaves do cache
            cache_keys = self.redis_client.keys("semantic_cache:*")
            
            for key in cache_keys[:1000]:  # Limitar para evitar sobrecarga
                try:
                    cached_data = self.redis_client.get(key)
                    if cached_data:
                        entry = pickle.loads(cached_data)
                        query_hash = key.decode().replace("semantic_cache:", "")
                        
                        # Verificar se não expirou
                        if not self._is_expired(entry):
                            self.memory_cache[query_hash] = entry
                            # Reconstruir índice de embeddings
                            if entry.query_embedding:
                                embedding_array = np.array(entry.query_embedding)
                                self.embedding_index.append((query_hash, embedding_array))
                
                except Exception as e:
                    logger.error(f"❌ Erro ao carregar entrada do cache: {e}")
            
            logger.info(f"📦 Cache carregado: {len(self.memory_cache)} entradas")
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar cache do Redis: {e}")
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Verifica se uma entrada do cache expirou"""
        if entry.expiry_date:
            return datetime.now() > entry.expiry_date
        return False
    
    def _generate_cache_key(self, query: str, legal_area: str) -> str:
        """Gera chave única para o cache"""
        content = f"{query}_{legal_area}".encode('utf-8')
        return hashlib.md5(content).hexdigest()
    
    def _classify_content_type(self, query: str, response: str) -> str:
        """Classifica o tipo de conteúdo para determinar TTL"""
        query_lower = query.lower()
        response_lower = response.lower()
        
        # Legislação - TTL longo
        if any(term in response_lower for term in ["art.", "lei n", "decreto", "constituição"]):
            return "legislation"
        
        # Jurisprudência - TTL médio
        if any(term in response_lower for term in ["súmula", "acórdão", "precedente", "tribunal"]):
            return "jurisprudence"
        
        # Casos críticos - TTL longo
        if any(term in query_lower for term in ["parecer", "recurso", "ação judicial"]):
            return "critical_case"
        
        # Análises complexas - TTL médio
        if any(term in query_lower for term in ["análise", "interpretação", "aplicação"]):
            return "complex_analysis"
        
        # Consultas básicas - TTL curto
        return "basic_query"
    
    def get_cached_response(self, query: str, legal_area: str) -> Optional[CacheHit]:
        """
        Busca resposta no cache baseado em similaridade semântica
        """
        if not self.embedding_system:
            return None
        
        try:
            # Gerar embedding da consulta
            query_embedding = self.embedding_system.get_embedding(query)
            if not query_embedding:
                return None
            
            query_vector = np.array(query_embedding)
            
            # Buscar similaridades no índice
            best_match = None
            best_similarity = 0.0
            
            for cache_key, cached_embedding in self.embedding_index:
                similarity = cosine_similarity([query_vector], [cached_embedding])[0][0]
                
                if similarity > best_similarity and cache_key in self.memory_cache:
                    entry = self.memory_cache[cache_key]
                    
                    # Verificar se não expirou e é da mesma área
                    if not self._is_expired(entry) and entry.legal_area == legal_area:
                        best_match = entry
                        best_similarity = similarity
            
            # Verificar se atende o threshold
            if best_similarity >= self.similarity_threshold:
                # Atualizar estatísticas de acesso
                best_match.accessed_count += 1
                best_match.last_accessed = datetime.now()
                
                # Persistir atualização
                self._persist_entry(best_match, legal_area)
                
                is_exact = best_similarity > 0.99
                
                logger.info(f"💾 Cache HIT - Similaridade: {best_similarity:.3f}")
                
                return CacheHit(
                    entry=best_match,
                    similarity_score=best_similarity,
                    is_exact_match=is_exact
                )
            
            logger.info(f"🔍 Cache MISS - Melhor similaridade: {best_similarity:.3f}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar no cache: {e}")
            return None
    
    def store_response(self, query: str, response: str, legal_area: str, 
                      metadata: Optional[Dict[str, Any]] = None, 
                      confidence_score: float = 0.8) -> bool:
        """
        Armazena resposta no cache semântico
        """
        if not self.embedding_system:
            return False
        
        try:
            # Gerar embedding da consulta
            query_embedding = self.embedding_system.get_embedding(query)
            if not query_embedding:
                return False
            
            # Classificar tipo de conteúdo
            content_type = self._classify_content_type(query, response)
            ttl_hours = self.ttl_by_content_type[content_type]
            
            # Criar entrada do cache
            cache_entry = CacheEntry(
                query=query,
                query_embedding=query_embedding,
                response=response,
                metadata=metadata or {},
                legal_area=legal_area,
                confidence_score=confidence_score,
                created_at=datetime.now(),
                accessed_count=1,
                last_accessed=datetime.now(),
                expiry_date=datetime.now() + timedelta(hours=ttl_hours)
            )
            
            # Gerar chave do cache
            cache_key = self._generate_cache_key(query, legal_area)
            
            # Armazenar em memória
            self.memory_cache[cache_key] = cache_entry
            
            # Adicionar ao índice de embeddings
            embedding_array = np.array(query_embedding)
            self.embedding_index.append((cache_key, embedding_array))
            
            # Persistir no Redis
            self._persist_entry(cache_entry, legal_area, cache_key)
            
            # Limpar cache se necessário
            self._cleanup_cache()
            
            logger.info(f"💾 Resposta armazenada no cache - Tipo: {content_type}, TTL: {ttl_hours}h")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao armazenar no cache: {e}")
            return False
    
    def _persist_entry(self, entry: CacheEntry, legal_area: str, cache_key: Optional[str] = None):
        """Persiste entrada no Redis"""
        if not self.redis_available:
            return
        
        try:
            if not cache_key:
                cache_key = self._generate_cache_key(entry.query, legal_area)
            
            redis_key = f"semantic_cache:{cache_key}"
            
            # Serializar entrada
            serialized_entry = pickle.dumps(entry)
            
            # Calcular TTL em segundos
            if entry.expiry_date:
                ttl_seconds = int((entry.expiry_date - datetime.now()).total_seconds())
                if ttl_seconds > 0:
                    self.redis_client.setex(redis_key, ttl_seconds, serialized_entry)
            else:
                self.redis_client.set(redis_key, serialized_entry)
            
        except Exception as e:
            logger.error(f"❌ Erro ao persistir entrada: {e}")
    
    def _cleanup_cache(self):
        """Limpa entradas antigas e expiradas do cache"""
        if len(self.memory_cache) <= self.max_cache_size:
            return
        
        try:
            # Remover entradas expiradas
            expired_keys = []
            for key, entry in self.memory_cache.items():
                if self._is_expired(entry):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.memory_cache[key]
                # Remover do índice de embeddings
                self.embedding_index = [(k, emb) for k, emb in self.embedding_index if k != key]
            
            # Se ainda exceder o limite, remover entradas menos acessadas
            if len(self.memory_cache) > self.max_cache_size:
                # Ordenar por frequência de acesso e data
                sorted_entries = sorted(
                    self.memory_cache.items(),
                    key=lambda x: (x[1].accessed_count, x[1].last_accessed)
                )
                
                # Remover 20% das entradas menos usadas
                remove_count = int(len(sorted_entries) * 0.2)
                for i in range(remove_count):
                    key = sorted_entries[i][0]
                    del self.memory_cache[key]
                    self.embedding_index = [(k, emb) for k, emb in self.embedding_index if k != key]
            
            logger.info(f"🧹 Cache limpo: {len(expired_keys)} expiradas, tamanho atual: {len(self.memory_cache)}")
            
        except Exception as e:
            logger.error(f"❌ Erro na limpeza do cache: {e}")
    
    def invalidate_by_legislation_change(self, changed_law: str):
        """
        Invalida cache relacionado à lei alterada
        """
        try:
            invalidated_count = 0
            keys_to_remove = []
            
            for key, entry in self.memory_cache.items():
                # Verificar se a entrada menciona a lei alterada
                if changed_law.lower() in entry.response.lower() or changed_law.lower() in entry.query.lower():
                    keys_to_remove.append(key)
                    invalidated_count += 1
            
            # Remover entradas invalidadas
            for key in keys_to_remove:
                del self.memory_cache[key]
                self.embedding_index = [(k, emb) for k, emb in self.embedding_index if k != key]
                
                # Remover do Redis
                if self.redis_available:
                    redis_key = f"semantic_cache:{key}"
                    self.redis_client.delete(redis_key)
            
            logger.info(f"⚖️ Cache invalidado por alteração legislativa: {invalidated_count} entradas removidas")
            
        except Exception as e:
            logger.error(f"❌ Erro na invalidação do cache: {e}")
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        try:
            total_entries = len(self.memory_cache)
            
            if total_entries == 0:
                return {
                    "total_entries": 0,
                    "redis_available": self.redis_available,
                    "embedding_system_available": self.embedding_system is not None
                }
            
            # Calcular estatísticas
            total_accesses = sum(entry.accessed_count for entry in self.memory_cache.values())
            avg_accesses = total_accesses / total_entries
            
            # Distribuição por área jurídica
            area_distribution = {}
            for entry in self.memory_cache.values():
                area = entry.legal_area
                area_distribution[area] = area_distribution.get(area, 0) + 1
            
            # Distribuição por tipo de conteúdo
            content_type_distribution = {}
            for entry in self.memory_cache.values():
                content_type = self._classify_content_type(entry.query, entry.response)
                content_type_distribution[content_type] = content_type_distribution.get(content_type, 0) + 1
            
            # Entradas que expiram em breve (próximas 24h)
            expiring_soon = sum(
                1 for entry in self.memory_cache.values()
                if entry.expiry_date and entry.expiry_date <= datetime.now() + timedelta(hours=24)
            )
            
            return {
                "total_entries": total_entries,
                "total_accesses": total_accesses,
                "average_accesses_per_entry": round(avg_accesses, 2),
                "area_distribution": area_distribution,
                "content_type_distribution": content_type_distribution,
                "expiring_soon_24h": expiring_soon,
                "similarity_threshold": self.similarity_threshold,
                "max_cache_size": self.max_cache_size,
                "redis_available": self.redis_available,
                "embedding_system_available": self.embedding_system is not None,
                "embedding_index_size": len(self.embedding_index),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular estatísticas: {e}")
            return {"error": str(e)}
    
    def clear_cache(self, legal_area: Optional[str] = None):
        """Limpa cache completamente ou por área jurídica"""
        try:
            if legal_area:
                # Limpar apenas área específica
                keys_to_remove = [
                    key for key, entry in self.memory_cache.items()
                    if entry.legal_area == legal_area
                ]
                
                for key in keys_to_remove:
                    del self.memory_cache[key]
                    self.embedding_index = [(k, emb) for k, emb in self.embedding_index if k != key]
                    
                    if self.redis_available:
                        redis_key = f"semantic_cache:{key}"
                        self.redis_client.delete(redis_key)
                
                logger.info(f"🧹 Cache limpo para área {legal_area}: {len(keys_to_remove)} entradas")
                
            else:
                # Limpar todo o cache
                self.memory_cache.clear()
                self.embedding_index.clear()
                
                if self.redis_available:
                    cache_keys = self.redis_client.keys("semantic_cache:*")
                    if cache_keys:
                        self.redis_client.delete(*cache_keys)
                
                logger.info("🧹 Cache completamente limpo")
                
        except Exception as e:
            logger.error(f"❌ Erro ao limpar cache: {e}")