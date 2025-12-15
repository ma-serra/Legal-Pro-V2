"""
Módulo Trabalhista - Processos e Prognósticos
Fase 3 - Módulos Específicos
"""
from .services import TrabalhistaService, PrognosticoTrabalhistaService
from .routes import trabalhista_bp

__all__ = [
    'TrabalhistaService',
    'PrognosticoTrabalhistaService',
    'trabalhista_bp'
]
