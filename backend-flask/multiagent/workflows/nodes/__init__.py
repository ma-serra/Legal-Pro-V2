"""
Nós especiais para fluxos de trabalho.

Este módulo define nós de controle de fluxo como condicionais, switches e merge,
para criar fluxos de trabalho avançados.
"""

from .condicional import CondicionalNode
from .switch import SwitchNode
from .merge import MergeNode

__all__ = ['CondicionalNode', 'SwitchNode', 'MergeNode']