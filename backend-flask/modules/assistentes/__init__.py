"""
Sistema de Assistentes Jurídicos Especializados
Cada área jurídica possui seu assistente exclusivo e altamente especializado
"""

from .assistente_agrario import AssistenteAgrario
from .assistente_bancario import AssistenteBancario
from .assistente_criminal import AssistenteCriminal
from .assistente_empresarial import AssistenteEmpresarial
from .assistente_recuperacao import AssistenteRecuperacao
from .assistente_trabalhista import AssistenteTrabalhista
from .assistente_consumidor import AssistenteConsumidor

# Mapeamento de assistentes por área
ASSISTENTES_JURIDICOS = {
    'agrario': AssistenteAgrario,
    'bancario': AssistenteBancario,
    'criminal': AssistenteCriminal,
    'empresarial': AssistenteEmpresarial,
    'recuperacao': AssistenteRecuperacao,
    'trabalhista': AssistenteTrabalhista,
    'consumidor': AssistenteConsumidor
}

def obter_assistente(area_juridica: str):
    """Retorna o assistente especializado para a área jurídica."""
    assistente_class = ASSISTENTES_JURIDICOS.get(area_juridica)
    if assistente_class:
        return assistente_class()
    else:
        # Retorna assistente genérico se área não encontrada
        from .assistente_base import AssistenteBase
        return AssistenteBase(area_juridica)