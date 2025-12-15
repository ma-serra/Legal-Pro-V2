"""
Módulo de Processos Dinâmicos
Backend Core - Fase 2
"""
from .services import ProcessoService
from .schemas import ProcessoSchema, ProcessoCreateSchema, ProcessoUpdateSchema
from .validators import CNJValidator, MonetaryValidator

__all__ = [
    'ProcessoService',
    'ProcessoSchema',
    'ProcessoCreateSchema', 
    'ProcessoUpdateSchema',
    'CNJValidator',
    'MonetaryValidator'
]
