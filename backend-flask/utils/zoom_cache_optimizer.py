"""
Otimizador de Cache para Zoom API
Reduz chamadas redundantes à API do Zoom
"""

import logging
from functools import lru_cache
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class ZoomCacheManager:
    """Gerenciador de cache para dados do Zoom"""
    
    def __init__(self):
        self._meetings_cache: Dict[str, Any] = {}
        self._users_cache: Dict[str, Any] = {}
        self._recordings_cache: Dict[str, Any] = {}
        self._cache_expiry: Dict[str, datetime] = {}
        self._default_ttl = timedelta(minutes=5)  # Cache padrão: 5 minutos
    
    def get_cached_meetings(self, user_id: str = 'me') -> Optional[List[Dict]]:
        """Retorna reuniões do cache se ainda válidas"""
        cache_key = f"meetings_{user_id}"
        
        if cache_key in self._meetings_cache:
            if cache_key in self._cache_expiry:
                if datetime.now() < self._cache_expiry[cache_key]:
                    logger.debug(f"✅ Reuniões retornadas do cache para {user_id}")
                    return self._meetings_cache[cache_key]
        
        return None
    
    def cache_meetings(self, meetings: List[Dict], user_id: str = 'me', ttl: timedelta = None):
        """Cachear lista de reuniões"""
        cache_key = f"meetings_{user_id}"
        ttl = ttl or self._default_ttl
        
        self._meetings_cache[cache_key] = meetings
        self._cache_expiry[cache_key] = datetime.now() + ttl
        logger.debug(f"💾 Cacheadas {len(meetings)} reuniões para {user_id} (TTL: {ttl.seconds}s)")
    
    def get_cached_user_info(self, user_id: str = 'me') -> Optional[Dict]:
        """Retorna informações do usuário do cache"""
        cache_key = f"user_{user_id}"
        
        if cache_key in self._users_cache:
            if cache_key in self._cache_expiry:
                if datetime.now() < self._cache_expiry[cache_key]:
                    logger.debug(f"✅ Info do usuário retornada do cache para {user_id}")
                    return self._users_cache[cache_key]
        
        return None
    
    def cache_user_info(self, user_info: Dict, user_id: str = 'me', ttl: timedelta = None):
        """Cachear informações do usuário"""
        cache_key = f"user_{user_id}"
        ttl = ttl or timedelta(minutes=30)  # Cache mais longo para info de usuário
        
        self._users_cache[cache_key] = user_info
        self._cache_expiry[cache_key] = datetime.now() + ttl
        logger.debug(f"💾 Info do usuário cacheada para {user_id} (TTL: {ttl.seconds}s)")
    
    def get_cached_recordings(self, from_date: str, to_date: str) -> Optional[List[Dict]]:
        """Retorna gravações do cache"""
        cache_key = f"recordings_{from_date}_{to_date}"
        
        if cache_key in self._recordings_cache:
            if cache_key in self._cache_expiry:
                if datetime.now() < self._cache_expiry[cache_key]:
                    logger.debug(f"✅ Gravações retornadas do cache ({from_date} a {to_date})")
                    return self._recordings_cache[cache_key]
        
        return None
    
    def cache_recordings(self, recordings: List[Dict], from_date: str, to_date: str, ttl: timedelta = None):
        """Cachear lista de gravações"""
        cache_key = f"recordings_{from_date}_{to_date}"
        ttl = ttl or timedelta(minutes=10)  # Cache médio para gravações
        
        self._recordings_cache[cache_key] = recordings
        self._cache_expiry[cache_key] = datetime.now() + ttl
        logger.debug(f"💾 Cacheadas {len(recordings)} gravações ({from_date} a {to_date})")
    
    def invalidate_cache(self, cache_type: str = None):
        """Invalida cache específico ou todo o cache"""
        if cache_type == 'meetings':
            self._meetings_cache.clear()
            logger.info("🗑️ Cache de reuniões invalidado")
        elif cache_type == 'users':
            self._users_cache.clear()
            logger.info("🗑️ Cache de usuários invalidado")
        elif cache_type == 'recordings':
            self._recordings_cache.clear()
            logger.info("🗑️ Cache de gravações invalidado")
        else:
            # Limpar todo o cache
            self._meetings_cache.clear()
            self._users_cache.clear()
            self._recordings_cache.clear()
            self._cache_expiry.clear()
            logger.info("🗑️ Todo o cache do Zoom invalidado")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        now = datetime.now()
        
        active_meetings = sum(1 for k, exp in self._cache_expiry.items() 
                            if k.startswith('meetings_') and exp > now)
        active_users = sum(1 for k, exp in self._cache_expiry.items() 
                         if k.startswith('user_') and exp > now)
        active_recordings = sum(1 for k, exp in self._cache_expiry.items() 
                              if k.startswith('recordings_') and exp > now)
        
        return {
            'total_cached_items': len(self._cache_expiry),
            'active_meetings_cache': active_meetings,
            'active_users_cache': active_users,
            'active_recordings_cache': active_recordings,
            'cache_hit_rate': self._calculate_hit_rate()
        }
    
    def _calculate_hit_rate(self) -> float:
        """Calcula taxa de acerto do cache (placeholder)"""
        # Implementação futura com contadores de hits/misses
        return 0.0

# Instância global do gerenciador de cache
zoom_cache = ZoomCacheManager()
