"""
Utilitários para gerenciamento de chaves de API.

Este módulo fornece funções para gerenciar as chaves de API de diversos
provedores utilizados pelo sistema multi-agente.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

# Configurar logger
logger = logging.getLogger(__name__)

# Caminho para o arquivo de configuração
CONFIG_PATH = "./config/api_keys.json"

def _ensure_config_dir():
    """Garante que o diretório de configuração exista."""
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

def _load_api_keys() -> Dict[str, str]:
    """
    Carrega todas as chaves de API do arquivo de configuração.
    
    Returns:
        Dicionário com as chaves de API
    """
    _ensure_config_dir()
    
    if not os.path.exists(CONFIG_PATH):
        return {}
    
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar chaves de API: {str(e)}")
        return {}

def _save_api_keys(api_keys: Dict[str, str]) -> bool:
    """
    Salva as chaves de API no arquivo de configuração.
    
    Args:
        api_keys: Dicionário com as chaves de API
        
    Returns:
        True se salvou com sucesso, False caso contrário
    """
    _ensure_config_dir()
    
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(api_keys, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar chaves de API: {str(e)}")
        return False

def get_api_key(provider: str) -> Optional[str]:
    """
    Obtém a chave de API para um provedor específico.
    
    Args:
        provider: Nome do provedor
        
    Returns:
        A chave de API ou None se não existir
    """
    # Primeiro, tentar obter da variável de ambiente
    env_key = os.environ.get(f"{provider.upper()}_API_KEY")
    if env_key:
        return env_key
    
    # Caso não exista variável de ambiente, buscar do arquivo
    api_keys = _load_api_keys()
    return api_keys.get(provider)

def set_api_key(provider: str, key: str) -> bool:
    """
    Define a chave de API para um provedor específico.
    
    Args:
        provider: Nome do provedor
        key: Chave de API
        
    Returns:
        True se salvou com sucesso, False caso contrário
    """
    api_keys = _load_api_keys()
    api_keys[provider] = key
    return _save_api_keys(api_keys)

def delete_api_key(provider: str) -> bool:
    """
    Remove a chave de API para um provedor específico.
    
    Args:
        provider: Nome do provedor
        
    Returns:
        True se removeu com sucesso, False caso contrário
    """
    api_keys = _load_api_keys()
    
    if provider in api_keys:
        del api_keys[provider]
        return _save_api_keys(api_keys)
    
    return True  # Já não existia, consideramos como sucesso

def list_api_keys() -> Dict[str, str]:
    """
    Lista todas as chaves de API configuradas.
    
    Returns:
        Dicionário com as chaves de API
    """
    return _load_api_keys()

def check_api_key(provider: str) -> bool:
    """
    Verifica se existe uma chave de API configurada para o provedor.
    
    Args:
        provider: Nome do provedor
        
    Returns:
        True se existe, False caso contrário
    """
    return get_api_key(provider) is not None