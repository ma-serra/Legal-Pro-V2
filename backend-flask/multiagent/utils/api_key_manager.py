"""
Gerenciador de chaves de API.

Este módulo é responsável por gerenciar as chaves de API para os provedores
de IA integrados ao sistema.
"""

import os
import json
import logging
import datetime
from pathlib import Path
from typing import Dict, Optional, List, Any, Union

# Configuração de logging
logger = logging.getLogger(__name__)

# Caminho para o arquivo de chaves
API_KEYS_FILE = "config/api_keys.json"

class APIKeyManager:
    """
    Classe para gerenciar chaves de API e realizar validações.
    """
    
    def __init__(self):
        """
        Inicializa o gerenciador de chaves de API.
        """
        # Lista padrão de provedores
        self.providers = ["openai", "anthropic", "google", "perplexity", "deepseek"]
        
        # Informações descritivas sobre cada provedor
        self.provider_info = {
            "openai": {
                "nome_exibicao": "OpenAI (GPT-4o)",
                "descricao": "API da OpenAI para acesso aos modelos GPT-4o, GPT-4 e outros modelos de linguagem",
                "formato_chave": "sk-...",
                "url_doc": "https://platform.openai.com/docs/api-reference"
            },
            "anthropic": {
                "nome_exibicao": "Anthropic (Claude)",
                "descricao": "API da Anthropic para acesso ao Claude 3.5 Sonnet e outros modelos Claude",
                "formato_chave": "sk-ant-...",
                "url_doc": "https://docs.anthropic.com/claude/reference"
            },
            "google": {
                "nome_exibicao": "Google (Gemini)",
                "descricao": "API da Google para acesso aos modelos Gemini e serviços de IA da Google",
                "formato_chave": "AIza...",
                "url_doc": "https://ai.google.dev/docs"
            },
            "perplexity": {
                "nome_exibicao": "Perplexity AI",
                "descricao": "API da Perplexity para acesso a modelos de linguagem com pesquisa em tempo real",
                "formato_chave": "pplx-...",
                "url_doc": "https://docs.perplexity.ai/"
            },
            "deepseek": {
                "nome_exibicao": "DeepSeek",
                "descricao": "API da DeepSeek para acesso a modelos de linguagem especialistas em código e análise",
                "formato_chave": "sk-...",
                "url_doc": "https://platform.deepseek.com/docs"
            }
        }
        
        # Ordem de fallback quando um provedor não está disponível
        # Formato: {provedor_primário: [lista de provedores alternativos em ordem de preferência]}
        self.fallback_order = {
            "openai": ["anthropic", "google", "deepseek", "perplexity"],  # fallback padrão para OpenAI
            "anthropic": ["google", "deepseek", "openai", "perplexity"],  # fallback específico para Anthropic
            "google": ["anthropic", "deepseek", "openai", "perplexity"],  # fallback para Google/Gemini
            "perplexity": ["anthropic", "google", "deepseek", "openai"],  # fallback para Perplexity
            "deepseek": ["anthropic", "google", "openai", "perplexity"]   # fallback para Deepseek
        }
        
        # Carregar as chaves de API
        self.keys = self.load_api_keys()
    
    def load_api_keys(self) -> Dict[str, str]:
        """
        Carrega as chaves de API do arquivo de configuração.
        
        Returns:
            Dict[str, str]: Dicionário com as chaves de API
        """
        try:
            # Verificar se o arquivo existe
            if not Path(API_KEYS_FILE).exists():
                # Criar o arquivo com um dicionário vazio
                self.save_api_keys({})
                logger.info(f"Arquivo de configuração de chaves de API criado: {API_KEYS_FILE}")
            
            # Carregar o arquivo
            with open(API_KEYS_FILE, 'r') as f:
                keys = json.load(f)
            
            # Substituir variáveis de ambiente nas chaves
            for provider, value in keys.items():
                if isinstance(value, str) and value.startswith('$'):
                    env_var = value[1:]  # Remover o $ inicial
                    env_value = os.getenv(env_var)
                    if env_value:
                        keys[provider] = env_value
                        logger.info(f"Substituída variável de ambiente {env_var} para o provedor {provider}")
            
            logger.info(f"Chaves de API carregadas de {API_KEYS_FILE}")
            return keys
        
        except Exception as e:
            logger.error(f"Erro ao carregar chaves de API: {str(e)}")
            return {}

    def save_api_keys(self, keys: Dict[str, str]) -> bool:
        """
        Salva as chaves de API no arquivo de configuração.
        
        Args:
            keys: Dicionário com as chaves de API
            
        Returns:
            bool: True se as chaves foram salvas com sucesso, False caso contrário
        """
        try:
            # Garantir que o diretório existe
            Path(API_KEYS_FILE).parent.mkdir(parents=True, exist_ok=True)
            
            # Salvar o arquivo
            with open(API_KEYS_FILE, 'w') as f:
                json.dump(keys, f, indent=2)
            
            # Atualizar as chaves em memória
            self.keys = keys
            
            logger.info(f"Chaves de API salvas em {API_KEYS_FILE}")
            return True
        
        except Exception as e:
            logger.error(f"Erro ao salvar chaves de API: {str(e)}")
            return False

    def get_api_key(self, provider: str) -> Optional[str]:
        """
        Obtém a chave de API para um provedor específico.
        
        Args:
            provider: Nome do provedor (openai, anthropic, google, perplexity, deepseek)
            
        Returns:
            str: Chave de API ou None se não encontrada
        """
        try:
            # Primeiro, verificar na variável de ambiente
            env_key = os.getenv(f"{provider.upper()}_API_KEY")
            if env_key:
                return env_key
            
            # Se não encontrada, buscar no arquivo
            return self.keys.get(provider.lower())
        
        except Exception as e:
            logger.error(f"Erro ao obter chave de API para {provider}: {str(e)}")
            return None

    def set_api_key(self, provider: str, key: str) -> bool:
        """
        Define a chave de API para um provedor específico.
        
        Args:
            provider: Nome do provedor (openai, anthropic, google, perplexity, deepseek)
            key: Chave de API
            
        Returns:
            bool: True se a chave foi definida com sucesso, False caso contrário
        """
        try:
            self.keys[provider.lower()] = key
            return self.save_api_keys(self.keys)
        
        except Exception as e:
            logger.error(f"Erro ao definir chave de API para {provider}: {str(e)}")
            return False

    def delete_api_key(self, provider: str) -> bool:
        """
        Remove a chave de API para um provedor específico.
        
        Args:
            provider: Nome do provedor (openai, anthropic, google, perplexity, deepseek)
            
        Returns:
            bool: True se a chave foi removida com sucesso, False caso contrário
        """
        try:
            if provider.lower() in self.keys:
                del self.keys[provider.lower()]
                return self.save_api_keys(self.keys)
            return True
        
        except Exception as e:
            logger.error(f"Erro ao remover chave de API para {provider}: {str(e)}")
            return False

    def get_all_providers(self) -> List[str]:
        """
        Obtém a lista de todos os provedores suportados.
        
        Returns:
            List[str]: Lista de provedores
        """
        return self.providers

    def validate_api_key(self, provider: str, key: Optional[str] = None) -> bool:
        """
        Valida se uma chave de API está funcionando.
        
        Args:
            provider: Nome do provedor (openai, anthropic, google, perplexity, deepseek)
            key: Chave de API a ser validada (opcional, usa a armazenada se não fornecida)
            
        Returns:
            bool: True se a chave é válida, False caso contrário
        """
        try:
            from multiagent.integrations import get_integration
            
            # Usar a chave fornecida ou buscar a armazenada
            api_key = key or self.get_api_key(provider)
            if not api_key:
                logger.warning(f"Chave de API não encontrada para {provider}")
                return False
            
            # Obter a integração e validar a chave
            integration = get_integration(provider, api_key=api_key)
            result = integration.validate_api_key()
            
            return result
        
        except Exception as e:
            logger.error(f"Erro ao validar chave de API para {provider}: {str(e)}")
            return False
    
    def get_fallback_provider(self, provider: str) -> Optional[str]:
        """
        Obtém o próximo provedor de fallback disponível e válido para o provedor especificado.
        
        Args:
            provider: Nome do provedor principal para o qual se busca um fallback
            
        Returns:
            Optional[str]: Nome do provedor de fallback disponível ou None se nenhum for encontrado
        """
        if provider not in self.fallback_order:
            logger.warning(f"Provedor {provider} não possui configuração de fallback.")
            return None
        
        # Verificar cada provedor alternativo na ordem definida
        for fallback_provider in self.fallback_order[provider]:
            # Verificar se o provedor tem chave configurada
            api_key = self.get_api_key(fallback_provider)
            if not api_key:
                logger.debug(f"Provedor de fallback {fallback_provider} não possui chave configurada.")
                continue
            
            # Verificar se a chave é válida
            if self.validate_api_key(fallback_provider, api_key):
                logger.info(f"Usando {fallback_provider} como fallback para {provider}.")
                return fallback_provider
        
        logger.warning(f"Nenhum provedor de fallback disponível para {provider}.")
        return None
    
    def get_provider_info(self, provider: str) -> Dict[str, Any]:
        """
        Obtém informações descritivas sobre um provedor específico.
        
        Args:
            provider: Nome do provedor (openai, anthropic, google, perplexity, deepseek)
            
        Returns:
            Dict[str, Any]: Dicionário com informações do provedor ou dicionário vazio se não encontrado
        """
        try:
            provider_lower = provider.lower()
            if provider_lower in self.provider_info:
                return self.provider_info[provider_lower]
            else:
                return {
                    "nome_exibicao": provider.capitalize(),
                    "descricao": f"API do provedor {provider}",
                    "formato_chave": "Desconhecido",
                    "url_doc": "#"
                }
        except Exception as e:
            logger.error(f"Erro ao obter informações do provedor {provider}: {str(e)}")
            return {}
            
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtém o status de cada provedor de API.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dicionário com o status de cada provedor
        """
        results = {}
        
        for provider in self.get_all_providers():
            try:
                # Verificar se tem chave ambiente ou arquivo
                env_key = os.getenv(f"{provider.upper()}_API_KEY")
                file_key = self.keys.get(provider.lower())
                
                has_key = bool(env_key or file_key)
                origin = "env" if env_key else ("file" if file_key else "none")
                
                # Validar chave se existir
                is_valid = False
                if has_key:
                    is_valid = self.validate_api_key(provider)
                
                # Obter informações do provedor
                provider_info = self.get_provider_info(provider)
                
                # Informações adicionais específicas do provedor
                model_info = {
                    "models": [],
                    "default_model": "",
                    "capabilities": []
                }
                
                results[provider] = {
                    "has_key": has_key,
                    "is_valid": is_valid,
                    "origin": origin,
                    "key_preview": "************" if has_key else "",
                    "display_name": provider_info.get("nome_exibicao", provider.capitalize()),
                    "description": provider_info.get("descricao", ""),
                    "key_format": provider_info.get("formato_chave", ""),
                    "documentation_url": provider_info.get("url_doc", ""),
                    "models": model_info.get("models", []),
                    "default_model": model_info.get("default_model", ""),
                    "last_validated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "capabilities": model_info.get("capabilities", [])
                }
                
            except Exception as e:
                logger.error(f"Erro ao verificar status de {provider}: {str(e)}")
                results[provider] = {
                    "has_key": False,
                    "is_valid": False,
                    "origin": "error",
                    "key_preview": "",
                    "display_name": provider.capitalize(),
                    "description": f"API do provedor {provider}",
                    "error": str(e)
                }
        
        return results


# Funções de compatibilidade para código legado que ainda use as funções individuais

def load_api_keys() -> Dict[str, str]:
    """Função de compatibilidade para o código legado"""
    return APIKeyManager().load_api_keys()

def save_api_keys(keys: Dict[str, str]) -> bool:
    """Função de compatibilidade para o código legado"""
    return APIKeyManager().save_api_keys(keys)

def get_api_key(provider: str) -> Optional[str]:
    """Função de compatibilidade para o código legado"""
    return APIKeyManager().get_api_key(provider)

def set_api_key(provider: str, key: str) -> bool:
    """Função de compatibilidade para o código legado"""
    return APIKeyManager().set_api_key(provider, key)

def delete_api_key(provider: str) -> bool:
    """Função de compatibilidade para o código legado"""
    return APIKeyManager().delete_api_key(provider)

def get_all_providers() -> List[str]:
    """Função de compatibilidade para o código legado"""
    return APIKeyManager().get_all_providers()

def validate_api_key(provider: str, key: Optional[str] = None) -> bool:
    """Função de compatibilidade para o código legado"""
    return APIKeyManager().validate_api_key(provider, key)

def get_fallback_provider(provider: str) -> Optional[str]:
    """Função de compatibilidade para o código legado"""
    return APIKeyManager().get_fallback_provider(provider)