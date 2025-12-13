"""
Utilitário para gerenciamento de chaves de API.
"""
import os
import logging
from typing import Optional

# Configuração do módulo de logs
logger = logging.getLogger(__name__)

def obter_api_key(provedor: str, log_warning: bool = True) -> Optional[str]:
    """
    Obtém a chave de API para o provedor especificado.
    
    Args:
        provedor (str): Nome do provedor (openai, google, anthropic, etc)
        log_warning (bool): Se True, loga uma mensagem de warning se a chave não for encontrada
        
    Returns:
        Optional[str]: Chave de API ou None se não encontrada
    """
    mapeamento = {
        'openai': 'OPENAI_API_KEY',
        'google': 'GOOGLE_API_KEY',
        'anthropic': 'ANTHROPIC_API_KEY',
        'deepseek': 'DEEPSEEK_API_KEY',
        'taskade': 'TASKADE_API_TOKEN',
        'assemblyai': 'ASSEMBLYAI_API_KEY'
    }
    
    if provedor not in mapeamento:
        if log_warning:
            logger.warning(f"Provedor não suportado: {provedor}")
        return None
    
    env_var = mapeamento[provedor]
    api_key = os.environ.get(env_var)
    
    if not api_key and log_warning:
        logger.warning(f"Chave de API não encontrada para o provedor {provedor} (variável {env_var})")
    
    return api_key