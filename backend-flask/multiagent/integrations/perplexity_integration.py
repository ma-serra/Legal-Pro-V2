"""
Integração com Perplexity AI API.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union

import requests
from .base_integration import BaseIntegration

# Configuração de logging
logger = logging.getLogger(__name__)

class PerplexityIntegration(BaseIntegration):
    """
    Integração com a API da Perplexity.
    """
    
    DEFAULT_MODEL = "llama-3.1-sonar-small-128k-online"
    
    AVAILABLE_MODELS = [
        "llama-3.1-sonar-small-128k-online",
        "llama-3.1-sonar-large-128k-online",
        "llama-3.1-sonar-huge-128k-online"
    ]
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Inicializa a integração com Perplexity.
        
        Args:
            api_key: Chave da API Perplexity (se não fornecida, busca em PERPLEXITY_API_KEY)
            model: Modelo da Perplexity a utilizar (padrão: llama-3.1-sonar-small-128k-online)
        """
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            logger.warning("PERPLEXITY_API_KEY não encontrada nas variáveis de ambiente.")
            self.client = None
            self.model = None
            return
            
        # Verificar se a chave tem formato esperado (pplx-)
        if not self.api_key.startswith("pplx-"):
            logger.warning("Formato da chave Perplexity possivelmente inválido. As chaves geralmente começam com 'pplx-'")
            
        self.model = model or self.DEFAULT_MODEL
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """
        Inicializa o cliente da API Perplexity.
        Como a Perplexity não tem um cliente Python oficial,
        vamos usar requisições HTTP diretas.
        """
        self.api_url = "https://api.perplexity.ai"
        logger.info(f"Cliente Perplexity configurado, usando modelo padrão: {self.model}")
            
    def _validate_key_implementation(self) -> bool:
        """
        Implementação específica para validação da chave da Perplexity.
        Usa uma chamada simples para verificar se a chave é válida.
        
        Returns:
            True se a chave for válida, False caso contrário
        """
        try:
            # Verificação básica da chave
            if not self.api_key:
                logger.error("Chave da API Perplexity não fornecida")
                return False
                
            # Verificar formato da chave
            if not self.api_key.startswith("pplx-"):
                logger.warning("Formato da chave Perplexity possivelmente inválido (deve começar com 'pplx-')")
                # Continuamos mesmo assim, pois o formato pode mudar no futuro
            
            # Fazer uma chamada de API simples para verificar se a chave é válida
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "Be precise and concise."
                    },
                    {
                        "role": "user",
                        "content": "Hello"
                    }
                ],
                "max_tokens": 10
            }
            
            url = f"{self.api_url}/chat/completions"
            
            try:
                response = requests.post(url, headers=headers, json=data)
                response.raise_for_status()  # Levanta exceção para status codes de erro
                
                # Se chegou aqui, a requisição foi bem-sucedida
                logger.info("Chave Perplexity validada com sucesso")
                return True
                
            except requests.exceptions.RequestException as e:
                error_msg = str(e).lower()
                if "unauthorized" in error_msg or "authentication" in error_msg or "401" in error_msg:
                    logger.error(f"Erro de autenticação na API Perplexity: {str(e)}")
                    return False
                else:
                    logger.error(f"Erro na chamada da API Perplexity: {str(e)}")
                    return False
                
        except Exception as e:
            logger.error(f"Erro ao validar chave da Perplexity: {str(e)}")
            return False
            
        return False  # Não deveria chegar aqui, mas por segurança retornamos False
    
    def generate_text(self, 
                     prompt: str, 
                     system_prompt: Optional[str] = None,
                     temperature: float = 0.7,
                     max_tokens: Optional[int] = 1000,
                     model: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera texto usando o modelo da Perplexity.
        
        Args:
            prompt: Texto de entrada para gerar a resposta
            system_prompt: Instruções de sistema (equivalente a system message)
            temperature: Controle de aleatoriedade (0.0 a 1.0)
            max_tokens: Número máximo de tokens a serem gerados
            model: Modelo a ser usado (sobreescreve o padrão)
            
        Returns:
            Dicionário com resultado da geração
        """
        model_to_use = model or self.model
        
        try:
            if not self.api_key:
                return {
                    "error": "API key not provided",
                    "success": False
                }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Construir mensagens
            messages = []
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            data = {
                "model": model_to_use,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens or 1000,
                "stream": False
            }
            
            url = f"{self.api_url}/chat/completions"
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            
            # Formatar a resposta de forma semelhante às outras integrações
            return {
                "text": result.get("choices", [{}])[0].get("message", {}).get("content", ""),
                "model": model_to_use,
                "success": True,
                "provider": "perplexity",
                "raw_response": result
            }
            
        except Exception as e:
            logger.error(f"Erro na geração de texto com Perplexity: {str(e)}")
            return {
                "error": str(e),
                "success": False,
                "provider": "perplexity"
            }
    
    def generate_chat(self, 
                     messages: List[Dict[str, str]], 
                     temperature: float = 0.7,
                     max_tokens: Optional[int] = 1000,
                     model: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera resposta de chat usando o modelo da Perplexity.
        
        Args:
            messages: Lista de mensagens no formato {"role": "...", "content": "..."}
            temperature: Controle de aleatoriedade (0.0 a 1.0)
            max_tokens: Número máximo de tokens a serem gerados
            model: Modelo a ser usado (sobreescreve o padrão)
            
        Returns:
            Dicionário com resultado da geração
        """
        model_to_use = model or self.model
        
        try:
            if not self.api_key:
                return {
                    "error": "API key not provided",
                    "success": False
                }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model_to_use,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens or 1000,
                "stream": False
            }
            
            url = f"{self.api_url}/chat/completions"
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            
            # Formatar a resposta de forma semelhante às outras integrações
            return {
                "text": result.get("choices", [{}])[0].get("message", {}).get("content", ""),
                "model": model_to_use,
                "success": True,
                "provider": "perplexity",
                "raw_response": result
            }
            
        except Exception as e:
            logger.error(f"Erro na geração de chat com Perplexity: {str(e)}")
            return {
                "error": str(e),
                "success": False,
                "provider": "perplexity"
            }
    
    def embed_text(self, 
                  text: Union[str, List[str]], 
                  model: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera embeddings para o texto fornecido.
        Perplexity não suporta embeddings nativo, então este método retorna um erro.
        
        Args:
            text: Texto ou lista de textos para embeddings
            model: Modelo a ser usado
            
        Returns:
            Dicionário com embeddings gerados
        """
        return {
            "error": "Embeddings not supported by Perplexity API",
            "success": False,
            "provider": "perplexity"
        }
    
    def validate_api_key(self) -> bool:
        """
        Verifica se a API key da Perplexity é válida.
        
        Returns:
            True se a chave for válida, False caso contrário
        """
        return self._validate_key_implementation()