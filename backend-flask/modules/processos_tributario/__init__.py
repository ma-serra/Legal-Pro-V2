"""
Módulo Tributário - Processos e Teses
Fase 3 - Módulos Específicos
"""
from .services import TeseTributariaService, PrognosticoTributarioService
from .routes import tributario_bp

__all__ = [
    'TeseTributariaService',
    'PrognosticoTributarioService',
    'tributario_bp'
]
