"""
Otimizador de Cache para LegalBERTimbau
Reduz processamento redundante de documentos
"""

import logging
import hashlib
from functools import lru_cache
from datetime import datetime, timedelta
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class BERTCacheManager:
    """Gerenciador de cache para análises BERTimbau"""
    
    def __init__(self):
        self._analysis_cache: Dict[str, Any] = {}
        self._entity_cache: Dict[str, Any] = {}
        self._classification_cache: Dict[str, Any] = {}
        self._cache_expiry: Dict[str, datetime] = {}
        self._default_ttl = timedelta(hours=1)  # Cache padrão: 1 hora
    
    def _generate_content_hash(self, content: str) -> str:
        """Gera hash único para conteúdo do documento"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
    
    def get_cached_analysis(self, content: str, config: Dict) -> Optional[Dict]:
        """Retorna análise do cache se já processada"""
        content_hash = self._generate_content_hash(content)
        config_hash = self._generate_content_hash(str(sorted(config.items())))
        cache_key = f"analysis_{content_hash}_{config_hash}"
        
        if cache_key in self._analysis_cache:
            if cache_key in self._cache_expiry:
                if datetime.now() < self._cache_expiry[cache_key]:
                    logger.debug(f"✅ Análise retornada do cache (hash: {content_hash[:8]}...)")
                    return self._analysis_cache[cache_key]
        
        return None
    
    def cache_analysis(self, content: str, config: Dict, analysis_result: Dict, ttl: timedelta = None):
        """Cachear resultado de análise"""
        content_hash = self._generate_content_hash(content)
        config_hash = self._generate_content_hash(str(sorted(config.items())))
        cache_key = f"analysis_{content_hash}_{config_hash}"
        ttl = ttl or self._default_ttl
        
        self._analysis_cache[cache_key] = analysis_result
        self._cache_expiry[cache_key] = datetime.now() + ttl
        logger.debug(f"💾 Análise cacheada (hash: {content_hash[:8]}..., TTL: {ttl.seconds}s)")
    
    def get_cached_entities(self, content: str) -> Optional[list]:
        """Retorna entidades extraídas do cache"""
        content_hash = self._generate_content_hash(content)
        cache_key = f"entities_{content_hash}"
        
        if cache_key in self._entity_cache:
            if cache_key in self._cache_expiry:
                if datetime.now() < self._cache_expiry[cache_key]:
                    logger.debug(f"✅ Entidades retornadas do cache (hash: {content_hash[:8]}...)")
                    return self._entity_cache[cache_key]
        
        return None
    
    def cache_entities(self, content: str, entities: list, ttl: timedelta = None):
        """Cachear entidades extraídas"""
        content_hash = self._generate_content_hash(content)
        cache_key = f"entities_{content_hash}"
        ttl = ttl or self._default_ttl
        
        self._entity_cache[cache_key] = entities
        self._cache_expiry[cache_key] = datetime.now() + ttl
        logger.debug(f"💾 {len(entities)} entidades cacheadas (hash: {content_hash[:8]}...)")
    
    def get_cached_classification(self, content: str) -> Optional[Dict]:
        """Retorna classificação do documento do cache"""
        content_hash = self._generate_content_hash(content)
        cache_key = f"classification_{content_hash}"
        
        if cache_key in self._classification_cache:
            if cache_key in self._cache_expiry:
                if datetime.now() < self._cache_expiry[cache_key]:
                    logger.debug(f"✅ Classificação retornada do cache (hash: {content_hash[:8]}...)")
                    return self._classification_cache[cache_key]
        
        return None
    
    def cache_classification(self, content: str, classification: Dict, ttl: timedelta = None):
        """Cachear classificação do documento"""
        content_hash = self._generate_content_hash(content)
        cache_key = f"classification_{content_hash}"
        ttl = ttl or self._default_ttl
        
        self._classification_cache[cache_key] = classification
        self._cache_expiry[cache_key] = datetime.now() + ttl
        logger.debug(f"💾 Classificação cacheada (hash: {content_hash[:8]}...)")
    
    def invalidate_cache(self, cache_type: str = None):
        """Invalida cache específico ou todo o cache"""
        if cache_type == 'analysis':
            self._analysis_cache.clear()
            logger.info("🗑️ Cache de análises invalidado")
        elif cache_type == 'entities':
            self._entity_cache.clear()
            logger.info("🗑️ Cache de entidades invalidado")
        elif cache_type == 'classification':
            self._classification_cache.clear()
            logger.info("🗑️ Cache de classificações invalidado")
        else:
            # Limpar todo o cache
            self._analysis_cache.clear()
            self._entity_cache.clear()
            self._classification_cache.clear()
            self._cache_expiry.clear()
            logger.info("🗑️ Todo o cache do BERT invalidado")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        now = datetime.now()
        
        active_analyses = sum(1 for k, exp in self._cache_expiry.items() 
                            if k.startswith('analysis_') and exp > now)
        active_entities = sum(1 for k, exp in self._cache_expiry.items() 
                            if k.startswith('entities_') and exp > now)
        active_classifications = sum(1 for k, exp in self._cache_expiry.items() 
                                   if k.startswith('classification_') and exp > now)
        
        return {
            'total_cached_items': len(self._cache_expiry),
            'active_analyses_cache': active_analyses,
            'active_entities_cache': active_entities,
            'active_classifications_cache': active_classifications,
            'total_memory_items': len(self._analysis_cache) + len(self._entity_cache) + len(self._classification_cache)
        }
    
    def cleanup_expired(self):
        """Remove itens expirados do cache"""
        now = datetime.now()
        expired_keys = [k for k, exp in self._cache_expiry.items() if exp <= now]
        
        for key in expired_keys:
            if key.startswith('analysis_'):
                self._analysis_cache.pop(key, None)
            elif key.startswith('entities_'):
                self._entity_cache.pop(key, None)
            elif key.startswith('classification_'):
                self._classification_cache.pop(key, None)
            
            self._cache_expiry.pop(key, None)
        
        if expired_keys:
            logger.info(f"🗑️ Removidos {len(expired_keys)} itens expirados do cache BERT")

# Instância global do gerenciador de cache
bert_cache = BERTCacheManager()

# Decorator para cache automático de funções de análise
def cache_bert_analysis(ttl: timedelta = None):
    """Decorator para cachear análises BERT automaticamente"""
    def decorator(func):
        @lru_cache(maxsize=128)
        def wrapper(content: str, *args, **kwargs):
            # Tentar obter do cache customizado primeiro
            config = kwargs.get('config', {})
            cached = bert_cache.get_cached_analysis(content, config)
            if cached:
                return cached
            
            # Executar análise
            result = func(content, *args, **kwargs)
            
            # Cachear resultado
            bert_cache.cache_analysis(content, config, result, ttl)
            return result
        
        return wrapper
    return decorator
