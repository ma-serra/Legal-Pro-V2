"""
Módulo de Templates de Documentos Jurídicos
Migração dos 42 templates jurídicos existentes da rota /juridico/especialistas
"""

from .routes import templates_documentos_bp
from .models import TemplateDocumento, CategoriaDocumento, HistoricoDocumento

__all__ = ['templates_documentos_bp', 'TemplateDocumento', 'CategoriaDocumento', 'HistoricoDocumento']