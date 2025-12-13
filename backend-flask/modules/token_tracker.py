"""
Sistema de rastreamento de tokens para APIs de IA
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy import create_engine, text
from collections import defaultdict

logger = logging.getLogger(__name__)

class TokenTracker:
    """Rastreador de consumo de tokens por API e componente"""
    
    def __init__(self):
        self.engine = create_engine(os.environ.get('DATABASE_URL'))
        self.token_usage = defaultdict(lambda: defaultdict(int))
        self.session_tokens = defaultdict(lambda: defaultdict(int))
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """Garante que a tabela de rastreamento existe"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS token_usage (
                        id SERIAL PRIMARY KEY,
                        provider VARCHAR(50) NOT NULL,
                        component VARCHAR(100) NOT NULL,
                        tokens_used INTEGER NOT NULL,
                        cost_usd DECIMAL(10, 6),
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        session_id VARCHAR(100),
                        user_id VARCHAR(100),
                        request_type VARCHAR(50),
                        model_used VARCHAR(100)
                    )
                """))
                conn.commit()
        except Exception as e:
            logger.error(f"Erro ao criar tabela token_usage: {e}")
    
    def track_usage(self, provider: str, component: str, tokens: int, 
                   cost: float = 0.0, session_id: str = None, 
                   user_id: str = None, request_type: str = None,
                   model_used: str = None):
        """Registra uso de tokens"""
        try:
            # Atualizar contadores em memória
            self.token_usage[provider][component] += tokens
            self.session_tokens[provider][component] += tokens
            
            # Salvar no banco de dados
            with self.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO token_usage 
                    (provider, component, tokens_used, cost_usd, session_id, 
                     user_id, request_type, model_used)
                    VALUES (:provider, :component, :tokens, :cost, :session_id,
                            :user_id, :request_type, :model_used)
                """), {
                    'provider': provider,
                    'component': component,
                    'tokens': tokens,
                    'cost': cost,
                    'session_id': session_id,
                    'user_id': user_id,
                    'request_type': request_type,
                    'model_used': model_used
                })
                conn.commit()
                
        except Exception as e:
            logger.error(f"Erro ao rastrear tokens: {e}")
    
    def get_usage_summary(self, period: str = 'today') -> Dict[str, Any]:
        """Retorna resumo de uso de tokens"""
        try:
            # Definir período
            if period == 'today':
                start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == 'week':
                start_date = datetime.now() - timedelta(days=7)
            elif period == 'month':
                start_date = datetime.now() - timedelta(days=30)
            else:
                start_date = datetime.now() - timedelta(hours=24)
            
            with self.engine.connect() as conn:
                # Uso por provedor
                provider_usage = conn.execute(text("""
                    SELECT provider, SUM(tokens_used) as total_tokens, 
                           SUM(cost_usd) as total_cost, COUNT(*) as requests
                    FROM token_usage 
                    WHERE timestamp >= :start_date
                    GROUP BY provider
                    ORDER BY total_tokens DESC
                """), {'start_date': start_date}).fetchall()
                
                # Uso por componente
                component_usage = conn.execute(text("""
                    SELECT component, provider, SUM(tokens_used) as total_tokens,
                           SUM(cost_usd) as total_cost, COUNT(*) as requests
                    FROM token_usage 
                    WHERE timestamp >= :start_date
                    GROUP BY component, provider
                    ORDER BY total_tokens DESC
                """), {'start_date': start_date}).fetchall()
                
                # Uso por modelo
                model_usage = conn.execute(text("""
                    SELECT model_used, provider, SUM(tokens_used) as total_tokens,
                           COUNT(*) as requests
                    FROM token_usage 
                    WHERE timestamp >= :start_date AND model_used IS NOT NULL
                    GROUP BY model_used, provider
                    ORDER BY total_tokens DESC
                """), {'start_date': start_date}).fetchall()
                
                # Uso por hora (últimas 24h)
                hourly_usage = conn.execute(text("""
                    SELECT DATE_TRUNC('hour', timestamp) as hour,
                           provider, SUM(tokens_used) as tokens
                    FROM token_usage 
                    WHERE timestamp >= :start_date
                    GROUP BY DATE_TRUNC('hour', timestamp), provider
                    ORDER BY hour DESC
                """), {'start_date': datetime.now() - timedelta(hours=24)}).fetchall()
                
                # Total geral
                total_stats = conn.execute(text("""
                    SELECT SUM(tokens_used) as total_tokens,
                           SUM(cost_usd) as total_cost,
                           COUNT(*) as total_requests,
                           COUNT(DISTINCT provider) as active_providers
                    FROM token_usage 
                    WHERE timestamp >= :start_date
                """), {'start_date': start_date}).fetchone()
            
            return {
                'period': period,
                'start_date': start_date.isoformat(),
                'total_stats': {
                    'total_tokens': total_stats.total_tokens or 0,
                    'total_cost': float(total_stats.total_cost or 0),
                    'total_requests': total_stats.total_requests or 0,
                    'active_providers': total_stats.active_providers or 0
                },
                'by_provider': [
                    {
                        'provider': row.provider,
                        'tokens': row.total_tokens,
                        'cost': float(row.total_cost or 0),
                        'requests': row.requests
                    }
                    for row in provider_usage
                ],
                'by_component': [
                    {
                        'component': row.component,
                        'provider': row.provider,
                        'tokens': row.total_tokens,
                        'cost': float(row.total_cost or 0),
                        'requests': row.requests
                    }
                    for row in component_usage
                ],
                'by_model': [
                    {
                        'model': row.model_used,
                        'provider': row.provider,
                        'tokens': row.total_tokens,
                        'requests': row.requests
                    }
                    for row in model_usage
                ],
                'hourly_usage': [
                    {
                        'hour': row.hour.isoformat(),
                        'provider': row.provider,
                        'tokens': row.tokens
                    }
                    for row in hourly_usage
                ]
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter resumo de uso: {e}")
            return {
                'error': str(e),
                'period': period,
                'total_stats': {'total_tokens': 0, 'total_cost': 0, 'total_requests': 0}
            }
    
    def get_component_breakdown(self) -> Dict[str, Any]:
        """Retorna breakdown detalhado por componente do sistema"""
        components_map = {
            'assistentes_juridicos': 'Assistentes Jurídicos',
            'agentes_multiagent': 'Agentes Multi-Agent',
            'analise_sentimento': 'Análise de Sentimento',
            'transcricao_audio': 'Transcrição de Áudio',
            'transcricao_video': 'Transcrição de Vídeo',
            'chat_juridico': 'Chat Jurídico',
            'templates_documentos': 'Templates de Documentos',
            'api_dashboard': 'Dashboard de APIs',
            'sistema_geral': 'Sistema Geral'
        }
        
        try:
            with self.engine.connect() as conn:
                # Uso nas últimas 24 horas por componente
                usage_data = conn.execute(text("""
                    SELECT component, provider, 
                           SUM(tokens_used) as tokens,
                           SUM(cost_usd) as cost,
                           COUNT(*) as requests,
                           MAX(timestamp) as last_used
                    FROM token_usage 
                    WHERE timestamp >= :start_date
                    GROUP BY component, provider
                    ORDER BY tokens DESC
                """), {'start_date': datetime.now() - timedelta(hours=24)}).fetchall()
                
                breakdown = {}
                total_tokens = 0
                
                for row in usage_data:
                    component_name = components_map.get(row.component, row.component.replace('_', ' ').title())
                    
                    if component_name not in breakdown:
                        breakdown[component_name] = {
                            'total_tokens': 0,
                            'total_cost': 0.0,
                            'total_requests': 0,
                            'providers': {},
                            'last_used': None
                        }
                    
                    breakdown[component_name]['total_tokens'] += row.tokens
                    breakdown[component_name]['total_cost'] += float(row.cost or 0)
                    breakdown[component_name]['total_requests'] += row.requests
                    
                    breakdown[component_name]['providers'][row.provider] = {
                        'tokens': row.tokens,
                        'cost': float(row.cost or 0),
                        'requests': row.requests
                    }
                    
                    if not breakdown[component_name]['last_used'] or row.last_used > breakdown[component_name]['last_used']:
                        breakdown[component_name]['last_used'] = row.last_used.isoformat()
                    
                    total_tokens += row.tokens
                
                # Calcular percentuais
                for component in breakdown.values():
                    if total_tokens > 0:
                        component['percentage'] = round((component['total_tokens'] / total_tokens) * 100, 1)
                    else:
                        component['percentage'] = 0
                
                return {
                    'breakdown': breakdown,
                    'total_tokens': total_tokens,
                    'period': 'last_24h'
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter breakdown de componentes: {e}")
            return {'error': str(e), 'breakdown': {}, 'total_tokens': 0}
    
    def get_realtime_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas em tempo real"""
        try:
            with self.engine.connect() as conn:
                # Últimas requisições
                recent_requests = conn.execute(text("""
                    SELECT provider, component, tokens_used, cost_usd, 
                           timestamp, model_used, request_type
                    FROM token_usage 
                    WHERE timestamp >= :start_time
                    ORDER BY timestamp DESC
                    LIMIT 20
                """), {'start_time': datetime.now() - timedelta(minutes=30)}).fetchall()
                
                # Tokens por minuto (última hora)
                tokens_per_minute = conn.execute(text("""
                    SELECT DATE_TRUNC('minute', timestamp) as minute,
                           SUM(tokens_used) as tokens
                    FROM token_usage 
                    WHERE timestamp >= :start_time
                    GROUP BY DATE_TRUNC('minute', timestamp)
                    ORDER BY minute DESC
                    LIMIT 60
                """), {'start_time': datetime.now() - timedelta(hours=1)}).fetchall()
                
                return {
                    'recent_requests': [
                        {
                            'provider': req.provider,
                            'component': req.component,
                            'tokens': req.tokens_used,
                            'cost': float(req.cost_usd or 0),
                            'timestamp': req.timestamp.isoformat(),
                            'model': req.model_used,
                            'type': req.request_type
                        }
                        for req in recent_requests
                    ],
                    'tokens_per_minute': [
                        {
                            'minute': tpm.minute.isoformat(),
                            'tokens': tpm.tokens
                        }
                        for tpm in tokens_per_minute
                    ]
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter stats em tempo real: {e}")
            return {'error': str(e), 'recent_requests': [], 'tokens_per_minute': []}

# Instância global do tracker
token_tracker = TokenTracker()