"""
Integração com Anthropic Claude API.
"""
import os
import logging
import time
from typing import Dict, List, Any, Optional, Union

import anthropic
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

from multiagent.integrations.base_integration import BaseIntegration

# Configuração de logging
logger = logging.getLogger(__name__)

class AnthropicIntegration(BaseIntegration):
    """
    Integração com a API da Anthropic (Claude).
    """

    DEFAULT_MODEL = "claude-sonnet-4-20250514"  # modelo mais recente do Claude
    
    # Lista completa de modelos disponíveis
    AVAILABLE_MODELS = [
        "claude-sonnet-4-20250514",    # Claude 4 Sonnet - Modelo mais recente
        "claude-3-7-sonnet-20250219",  # Claude 3.7 Sonnet - Intermediário
        "claude-3-5-sonnet-20241022",  # Claude 3.5 Sonnet - Anterior
        "claude-3-sonnet-20240229",
        "claude-3-opus-20240229",
        "claude-3-haiku-20240307",
        "claude-2.1",
        "claude-2.0",
        "claude-instant-1.2"
    ]
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Inicializa a integração com Anthropic.
        
        Args:
            api_key: Chave da API Anthropic (se não fornecida, busca em ANTHROPIC_API_KEY)
            model: Modelo do Claude a utilizar (padrão: claude-3-5-sonnet)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY não encontrada nas variáveis de ambiente.")
            self.model = None
            self.client = None
            return
            
        # Verificar se a chave tem formato esperado (sk-ant-)
        if not self.api_key.startswith("sk-ant-"):
            logger.warning("Formato da chave Anthropic possivelmente inválido. As chaves geralmente começam com 'sk-ant-'")
            
        self.model = model or self.DEFAULT_MODEL
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """
        Inicializa o cliente da API Anthropic.
        """
        try:
            if not self.api_key:
                logger.error("Não é possível inicializar o cliente Anthropic sem uma chave de API")
                self.client = None
                return
                
            self.client = Anthropic(api_key=self.api_key)
            logger.info(f"Cliente Anthropic inicializado com sucesso, usando modelo padrão: {self.model}")
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente Anthropic: {str(e)}")
            self.client = None
            
    def _validate_key_implementation(self) -> bool:
        """
        Implementação específica para validação da chave da Anthropic.
        Usa uma chamada simples para verificar se a chave é válida.
        
        Returns:
            True se a chave for válida, False caso contrário
        """
        try:
            # Verificação básica da chave
            if not self.api_key:
                logger.error("Chave da API Anthropic não fornecida")
                return False
                
            # Verificar formato da chave
            if not self.api_key.startswith("sk-ant-"):
                logger.warning("Formato da chave Anthropic possivelmente inválido (deve começar com 'sk-ant-')")
                # Continuamos mesmo assim, pois o formato pode mudar no futuro
            
            # Verificar se o cliente foi inicializado corretamente
            if not self.client:
                logger.error("Cliente Anthropic não inicializado corretamente")
                return False
                
            # Fazer uma chamada de API simples para verificar se a chave é válida
            try:
                # Usamos uma chamada simples ao Claude com uma mensagem curta
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=10,
                    messages=[
                        {"role": "user", "content": "Hello"}
                    ]
                )
                if response and hasattr(response, 'content') and len(response.content) > 0:
                    logger.info("Chave Anthropic validada com sucesso")
                    return True
                else:
                    logger.warning("Resposta da API Anthropic vazia ou inválida")
                    return False
            except Exception as api_error:
                # Mensagens de erro específicas da Anthropic que indicam problemas de autenticação
                error_msg = str(api_error).lower()
                if "unauthorized" in error_msg or "authentication" in error_msg or "invalid" in error_msg:
                    logger.error(f"Erro de autenticação na API Anthropic: {str(api_error)}")
                    return False
                else:
                    # Outros erros que não são de autenticação (pode ser problema de rede, etc.)
                    logger.warning(f"Erro não relacionado à autenticação na API Anthropic: {str(api_error)}")
                    return False
                
        except Exception as e:
            logger.error(f"Erro ao validar chave da Anthropic: {str(e)}")
            return False
            
        return False  # Não deveria chegar aqui, mas por segurança retornamos False
    
    def generate_text(self, 
                     prompt: str, 
                     system_prompt: Optional[str] = None,
                     temperature: float = 0.7,
                     max_tokens: Optional[int] = 1000,
                     model: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera texto usando o modelo Claude.
        
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
            start_time = time.time()
            
            # Converter em formato de mensagens para usar a API moderna
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
                
            messages.append({"role": "user", "content": prompt})
            
            # A partir do Claude 3, é recomendado usar a API de chat em vez da API de prompt
            response = self.client.messages.create(
                model=model_to_use,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            elapsed = time.time() - start_time
            
            result = {
                "text": response.content[0].text,
                "model": model_to_use,
                "elapsed_seconds": elapsed,
                "finish_reason": response.stop_reason,
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                },
                "raw_response": response
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na geração de texto com Claude: {str(e)}")
            raise
    
    def generate_chat(self, 
                     messages: List[Dict[str, str]], 
                     temperature: float = 0.7,
                     max_tokens: Optional[int] = 1000,
                     model: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera resposta de chat usando o modelo Claude.
        
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
            start_time = time.time()
            
            # A partir do Claude 3, é recomendado usar a API de chat
            response = self.client.messages.create(
                model=model_to_use,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            elapsed = time.time() - start_time
            
            result = {
                "text": response.content[0].text,
                "model": model_to_use,
                "elapsed_seconds": elapsed,
                "finish_reason": response.stop_reason,
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                },
                "raw_response": response
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na geração de chat com Claude: {str(e)}")
            raise
    
    def embed_text(self, 
                  text: Union[str, List[str]], 
                  model: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera embeddings para o texto fornecido.
        
        Args:
            text: Texto ou lista de textos para embeddings
            model: Modelo a ser usado (Claude ainda não suporta embeddings diretamente)
            
        Returns:
            Dicionário com embeddings gerados
        """
        # Claude não oferece embeddings nativamente. 
        # Podemos implementar com outro provedor ou usar a estrutura futura
        raise NotImplementedError("A API do Claude ainda não suporta embeddings nativamente.")
    
    def validate_api_key(self) -> bool:
        """
        Verifica se a API key da Anthropic é válida.
        
        Returns:
            True se a chave for válida, False caso contrário
        """
        try:
            result = self.generate_text("Olá, teste de validação da API.", max_tokens=10)
            return True
        except Exception as e:
            logger.error(f"Erro ao validar API key da Anthropic: {str(e)}")
            return False