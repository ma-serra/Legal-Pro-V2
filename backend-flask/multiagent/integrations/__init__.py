"""
Módulo de integrações do sistema multi-agente com provedores de IA.
"""
import logging
from typing import Optional, Dict, Any

# Configuração de logging
logger = logging.getLogger(__name__)

def get_integration(provider: str, api_key: Optional[str] = None, model: Optional[str] = None):
    """
    Função para obter a integração correta baseada no provedor.
    
    Args:
        provider: Nome do provedor (openai, anthropic, google, perplexity, etc.)
        api_key: Chave de API opcional
        model: Modelo opcional
        
    Returns:
        Objeto de integração com o provedor solicitado
    """
    try:
        if provider.lower() == 'openai':
            from multiagent.integrations.openai_integration import OpenAIIntegration
            return OpenAIIntegration(api_key=api_key, model=model)
        
        elif provider.lower() == 'anthropic':
            from multiagent.integrations.anthropic_integration import AnthropicIntegration
            return AnthropicIntegration(api_key=api_key, model=model)
        
        elif provider.lower() == 'google':
            from multiagent.integrations.google_integration import GoogleIntegration
            return GoogleIntegration(api_key=api_key, model=model)
        
        elif provider.lower() == 'perplexity':
            from multiagent.integrations.perplexity_integration import PerplexityIntegration
            return PerplexityIntegration(api_key=api_key, model=model)
        
        elif provider.lower() == 'deepseek':
            from multiagent.integrations.deepseek_integration import DeepseekIntegration
            return DeepseekIntegration(api_key=api_key, model=model)
        
        else:
            logger.error(f"Provedor não suportado: {provider}")
            raise ValueError(f"Provedor não suportado: {provider}")
    
    except Exception as e:
        logger.error(f"Erro ao criar integração para {provider}: {str(e)}")
        raise