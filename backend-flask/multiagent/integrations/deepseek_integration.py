"""
Integração com DeepSeek AI API.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union

import requests
from .base_integration import BaseIntegration

# Configuração de logging
logger = logging.getLogger(__name__)

class DeepseekIntegration(BaseIntegration):
    """
    Integração com a API da DeepSeek.
    """
    
    DEFAULT_MODEL = "deepseek-chat"
    
    AVAILABLE_MODELS = [
        "deepseek-chat",
        "deepseek-coder"
    ]
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Inicializa a integração com DeepSeek.
        
        Args:
            api_key: Chave da API DeepSeek (se não fornecida, busca em DEEPSEEK_API_KEY)
            model: Modelo da DeepSeek a utilizar (padrão: deepseek-chat)
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            logger.warning("DEEPSEEK_API_KEY não encontrada nas variáveis de ambiente.")
            self.client = None
            self.model = None
            return
            
        # Verificar se a chave tem formato esperado (sk-)
        if not self.api_key.startswith("sk-"):
            logger.warning("Formato da chave DeepSeek possivelmente inválido. As chaves geralmente começam com 'sk-'")
            
        self.model = model or self.DEFAULT_MODEL
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """
        Inicializa o cliente da API DeepSeek.
        Como a DeepSeek não tem um cliente Python oficial,
        vamos usar requisições HTTP diretas.
        """
        self.api_url = "https://api.deepseek.com/v1"
        logger.info(f"Cliente DeepSeek configurado, usando modelo padrão: {self.model}")
            
    def _validate_key_implementation(self) -> bool:
        """
        Implementação específica para validação da chave da DeepSeek.
        Usa uma chamada simples para verificar se a chave é válida.
        
        Returns:
            True se a chave for válida, False caso contrário
        """
        try:
            # Verificação básica da chave
            if not self.api_key:
                logger.error("Chave da API DeepSeek não fornecida")
                return False
                
            # Verificar formato da chave
            if not self.api_key.startswith("sk-"):
                logger.warning("Formato da chave DeepSeek possivelmente inválido (deve começar com 'sk-')")
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
                logger.info("Chave DeepSeek validada com sucesso")
                return True
                
            except requests.exceptions.RequestException as e:
                error_msg = str(e).lower()
                if "unauthorized" in error_msg or "authentication" in error_msg or "401" in error_msg:
                    logger.error(f"Erro de autenticação na API DeepSeek: {str(e)}")
                    return False
                else:
                    logger.error(f"Erro na chamada da API DeepSeek: {str(e)}")
                    return False
                
        except Exception as e:
            logger.error(f"Erro ao validar chave da DeepSeek: {str(e)}")
            return False
            
        return False  # Não deveria chegar aqui, mas por segurança retornamos False
    
    def generate_text(self, 
                     prompt: str, 
                     system_prompt: Optional[str] = None,
                     temperature: float = 0.7,
                     max_tokens: Optional[int] = 1000,
                     model: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera texto usando o modelo da DeepSeek.
        
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
                "max_tokens": max_tokens or 1000
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
                "provider": "deepseek",
                "raw_response": result
            }
            
        except Exception as e:
            logger.error(f"Erro na geração de texto com DeepSeek: {str(e)}")
            return {
                "error": str(e),
                "success": False,
                "provider": "deepseek"
            }
    
    def generate_chat(self, 
                     messages: List[Dict[str, str]], 
                     temperature: float = 0.7,
                     max_tokens: Optional[int] = 1000,
                     model: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera resposta de chat usando o modelo da DeepSeek.
        
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
                "max_tokens": max_tokens or 1000
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
                "provider": "deepseek",
                "raw_response": result
            }
            
        except Exception as e:
            logger.error(f"Erro na geração de chat com DeepSeek: {str(e)}")
            return {
                "error": str(e),
                "success": False,
                "provider": "deepseek"
            }
    
    def embed_text(self, 
                  text: Union[str, List[str]], 
                  model: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera embeddings para o texto fornecido.
        DeepSeek suporta embeddings via endpoint específico.
        
        Args:
            text: Texto ou lista de textos para embeddings
            model: Modelo a ser usado
            
        Returns:
            Dicionário com embeddings gerados
        """
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
            
            # Se for uma string, converter para lista
            input_texts = [text] if isinstance(text, str) else text
            
            data = {
                "model": "deepseek-embedding",
                "input": input_texts
            }
            
            url = f"{self.api_url}/embeddings"
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            
            # Extrair os embeddings da resposta
            embeddings = [item["embedding"] for item in result.get("data", [])]
            
            return {
                "embeddings": embeddings,
                "model": "deepseek-embedding",
                "success": True,
                "provider": "deepseek",
                "raw_response": result
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar embeddings com DeepSeek: {str(e)}")
            return {
                "error": str(e),
                "success": False,
                "provider": "deepseek"
            }
    
    def validate_api_key(self) -> bool:
        """
        Verifica se a API key da DeepSeek é válida.
        
        Returns:
            True se a chave for válida, False caso contrário
        """
        return self._validate_key_implementation()