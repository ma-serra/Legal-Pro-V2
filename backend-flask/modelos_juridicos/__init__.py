"""
Módulo de Modelos Jurídicos Estatísticos
========================================

Sistema completo de análise estatística e recomendações para processos jurídicos.
Implementa modelos de especificidade, defesa e recomendações baseados em dados reais.

Versão 2.0: Inclui melhorias de validação temporal, segmentação por área,
monitoramento de drift e auditabilidade, mantendo compatibilidade total com v1.
"""

from .modulo_modelos_juridicos import ModeloDefesa, ModeloEspecificidade
from .recomendador import RecomendadorDefesa
from .visualizador import VisualizadorModelos

# Novas funcionalidades v2.0
try:
    from .melhorias_v2 import (
        ModeloDefesaSegmentado,
        ValidacaoTemporal,
        MonitoramentoDrift,
        gerar_dashboard_metricas,
        inicializar_melhorias_v2
    )
    _v2_disponivel = True
except ImportError:
    _v2_disponivel = False

__version__ = "2.0.0"
__author__ = "Legal Pro AI System"

# Exportações v1 (compatibilidade)
__all__ = [
    'ModeloDefesa',
    'ModeloEspecificidade', 
    'RecomendadorDefesa',
    'VisualizadorModelos'
]

# Exportações v2 (se disponível)
if _v2_disponivel:
    __all__.extend([
        'ModeloDefesaSegmentado',
        'ValidacaoTemporal',
        'MonitoramentoDrift',
        'gerar_dashboard_metricas',
        'inicializar_melhorias_v2'
    ])