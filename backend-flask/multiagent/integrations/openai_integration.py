"""
Integração com OpenAI API.
"""
import os
import logging
import time
from typing import Dict, List, Any, Optional, Union

from openai import OpenAI

from multiagent.integrations.base_integration import BaseIntegration

# Configuração de logging
logger = logging.getLogger(__name__)

class OpenAIIntegration(BaseIntegration):
    """
    Integração com a API da OpenAI.
    """

    DEFAULT_MODEL = "gpt-4o"  # o modelo mais recente da OpenAI
    DEFAULT_EMBEDDING_MODEL = "text-embedding-3-large"  # modelo de embeddings mais recente
    
    # Lista completa de modelos disponíveis
    AVAILABLE_MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4-0125-preview",
        "gpt-4-1106-preview",
        "gpt-4-vision-preview",
        "gpt-4",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-0125",
        "gpt-3.5-turbo-1106",
        "gpt-3.5-turbo-instruct"
    ]
    
    # Lista de modelos de embeddings
    AVAILABLE_EMBEDDING_MODELS = [
        "text-embedding-3-large",
        "text-embedding-3-small",
        "text-embedding-ada-002"
    ]
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Inicializa a integração com OpenAI.
        
        Args:
            api_key: Chave da API OpenAI (se não fornecida, busca em OPENAI_API_KEY)
            model: Modelo da OpenAI a utilizar (padrão: gpt-4o)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("OPENAI_API_KEY não encontrada nas variáveis de ambiente.")
            raise ValueError("Chave de API da OpenAI não fornecida.")
            
        self.model = model or self.DEFAULT_MODEL
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """
        Inicializa o cliente da API OpenAI.
        """
        try:
            self.client = OpenAI(api_key=self.api_key)
            logger.info(f"Cliente OpenAI inicializado com sucesso, usando modelo padrão: {self.model}")
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente OpenAI: {str(e)}")
            raise
            
    def _validate_key_implementation(self) -> bool:
        """
        Implementação específica para validação da chave da OpenAI.
        Usa validação baseada em formato e cache para evitar rate limiting.
        
        Returns:
            True se a chave for válida, False caso contrário
        """
        try:
            # Verificar se o cliente foi inicializado corretamente
            if not self.client:
                logger.error("Cliente OpenAI não inicializado corretamente")
                return False
            
            # Verificar formato básico da chave - mais rigoroso
            if not self.api_key or not isinstance(self.api_key, str):
                logger.error("Chave da API OpenAI não fornecida ou inválida")
                return False
                
            if not self.api_key.startswith('sk-'):
                logger.error("Formato da chave da API OpenAI inválido (deve começar com 'sk-')")
                return False
                
            # Verificar se a chave tem tamanho adequado
            if len(self.api_key) < 20:
                logger.error("Chave da API OpenAI muito curta")
                return False
                
            # Se chegou até aqui, a chave tem formato válido
            # Para evitar rate limiting, consideramos válida se o formato estiver correto
            # e o cliente foi inicializado sem erro
            logger.info("Chave OpenAI validada com sucesso (formato correto)")
            return True
                
        except Exception as e:
            logger.error(f"Erro ao validar chave da OpenAI: {str(e)}")
            return False
    
    def generate_text(self, 
                     prompt: str, 
                     system_prompt: Optional[str] = None,
                     temperature: float = 0.7,
                     max_tokens: Optional[int] = None,
                     model: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera texto usando o modelo da OpenAI.
        
        Args:
            prompt: Texto de entrada para gerar a resposta
            system_prompt: Instruções de sistema opcional
            temperature: Controle de aleatoriedade (0.0 a 1.0)
            max_tokens: Número máximo de tokens a serem gerados
            model: Modelo a ser usado (sobreescreve o padrão)
            
        Returns:
            Dicionário com resultados da geração
        """
        model_to_use = model or self.model
        
        try:
            start_time = time.time()
            
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
                
            messages.append({"role": "user", "content": prompt})
            
            params = {
                "model": model_to_use,
                "messages": messages,
                "temperature": temperature,
            }
            
            if max_tokens:
                params["max_tokens"] = max_tokens
            
            response = self.client.chat.completions.create(**params)
            
            elapsed = time.time() - start_time
            
            result = {
                "text": response.choices[0].message.content,
                "model": model_to_use,
                "elapsed_seconds": elapsed,
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "raw_response": response
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na geração de texto com OpenAI: {str(e)}")
            raise
    
    def generate_chat(self, 
                     messages: List[Dict[str, str]], 
                     temperature: float = 0.7,
                     max_tokens: Optional[int] = None,
                     model: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera uma resposta de chat usando o modelo da OpenAI.
        
        Args:
            messages: Lista de mensagens no formato {"role": "...", "content": "..."}
            temperature: Controle de aleatoriedade (0.0 a 1.0)
            max_tokens: Número máximo de tokens a serem gerados
            model: Modelo a ser usado (sobreescreve o padrão)
            
        Returns:
            Dicionário com resultados da geração
        """
        model_to_use = model or self.model
        
        try:
            start_time = time.time()
            
            params = {
                "model": model_to_use,
                "messages": messages,
                "temperature": temperature,
            }
            
            if max_tokens:
                params["max_tokens"] = max_tokens
            
            response = self.client.chat.completions.create(**params)
            
            elapsed = time.time() - start_time
            
            result = {
                "text": response.choices[0].message.content,
                "model": model_to_use,
                "elapsed_seconds": elapsed,
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "raw_response": response
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na geração de chat com OpenAI: {str(e)}")
            raise
    
    def embed_text(self, 
                  text: Union[str, List[str]], 
                  model: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera embeddings para o texto fornecido.
        
        Args:
            text: Texto ou lista de textos para embeddings
            model: Modelo a ser usado (sobreescreve o padrão)
            
        Returns:
            Dicionário com embeddings gerados
        """
        embedding_model = model or self.DEFAULT_EMBEDDING_MODEL
        
        try:
            start_time = time.time()
            
            response = self.client.embeddings.create(
                model=embedding_model,
                input=text,
                encoding_format="float"
            )
            
            elapsed = time.time() - start_time
            
            # Se for um único texto, retornar um único embedding
            if isinstance(text, str):
                embeddings = response.data[0].embedding
            else:
                embeddings = [item.embedding for item in response.data]
            
            result = {
                "embeddings": embeddings,
                "model": embedding_model,
                "elapsed_seconds": elapsed,
                "dimensions": len(embeddings[0]) if isinstance(embeddings, list) and embeddings else len(embeddings),
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "total_tokens": response.usage.total_tokens
                },
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao gerar embeddings com OpenAI: {str(e)}")
            raise
    
    def validate_api_key(self) -> bool:
        """
        Verifica se a API key da OpenAI é válida.
        
        Returns:
            True se a chave for válida, False caso contrário
        """
        try:
            result = self.generate_text("Olá, teste de validação da API.", max_tokens=10)
            return True
        except Exception as e:
            logger.error(f"Erro ao validar API key da OpenAI: {str(e)}")
            return False