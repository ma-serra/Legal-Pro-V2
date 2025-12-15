"""
Módulo de Atualização Monetária Automática
Fase 4 - Importação de Índices e Scheduler
"""
from .importador import ImportadorIndices
from .scheduler import AtualizacaoScheduler
from .routes import atualizacao_bp

__all__ = [
    'ImportadorIndices',
    'AtualizacaoScheduler',
    'atualizacao_bp'
]
