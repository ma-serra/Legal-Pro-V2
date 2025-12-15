"""
Módulo Cível - Processos e Prognósticos
Fase 3 - Módulos Específicos
"""
from .services import CivelService, PrognosticoCivelService
from .routes import civel_bp

__all__ = [
    'CivelService',
    'PrognosticoCivelService',
    'civel_bp'
]
