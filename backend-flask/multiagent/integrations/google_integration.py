"""
Integração com Google Gemini API.
"""
import os
import logging
import time
from typing import Dict, List, Any, Optional, Union

import google.generativeai as genai

from multiagent.integrations.base_integration import BaseIntegration

# Configuração de logging
logger = logging.getLogger(__name__)

class GoogleIntegration(BaseIntegration):
    """
    Integração com a API do Google Gemini.
    """

    DEFAULT_MODEL = "gemini-1.5-pro"  # modelo mais recente do Gemini
    DEFAULT_EMBEDDING_MODEL = "embedding-001"  # modelo de embeddings do Google
    
    # Lista completa de modelos disponíveis
    AVAILABLE_MODELS = [
        "gemini-1.5-pro",  # O mais recente e potente
        "gemini-1.5-flash",
        "gemini-1.0-pro",
        "gemini-1.0-pro-vision",
        "gemini-1.0-ultra",
        "gemini-1.0-ultra-vision"
    ]
    
    # Lista de modelos de embeddings
    AVAILABLE_EMBEDDING_MODELS = [
        "embedding-001",
        "text-embedding-004"
    ]
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Inicializa a integração com Google Gemini.
        
        Args:
            api_key: Chave da API Google (se não fornecida, busca em GOOGLE_API_KEY)
            model: Modelo do Gemini a utilizar (padrão: gemini-1.5-pro)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.error("GEMINI_API_KEY não encontrada nas variáveis de ambiente.")
            raise ValueError("Chave de API do Gemini não fornecida.")
            
        self.model = model or self.DEFAULT_MODEL
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """
        Inicializa o cliente da API Google Gemini.
        """
        try:
            genai.configure(api_key=self.api_key)
            self.client = genai
            logger.info(f"Cliente Google Gemini inicializado com sucesso, usando modelo padrão: {self.model}")
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente Google Gemini: {str(e)}")
            raise
    
    def generate_text(self, 
                     prompt: str, 
                     system_prompt: Optional[str] = None,
                     temperature: float = 0.7,
                     max_tokens: Optional[int] = None,
                     model: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera texto usando o modelo Gemini.
        
        Args:
            prompt: Texto de entrada para gerar a resposta
            system_prompt: Instruções de sistema
            temperature: Controle de aleatoriedade (0.0 a 1.0)
            max_tokens: Número máximo de tokens a serem gerados
            model: Modelo a ser usado (sobreescreve o padrão)
            
        Returns:
            Dicionário com resultado da geração
        """
        model_to_use = model or self.model
        
        try:
            start_time = time.time()
            
            # Configurar o modelo
            model = self.client.GenerativeModel(model_name=model_to_use)
            
            # Preparar as configurações de geração
            generation_config = {
                "temperature": temperature,
            }
            
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            # Construir o contexto de chat
            chat = model.start_chat()
            
            # Se houver instruções de sistema, adicionar primeiro
            if system_prompt:
                chat.send_message(system_prompt, role="system")
            
            # Enviar o prompt principal
            response = chat.send_message(prompt, generation_config=generation_config)
            
            elapsed = time.time() - start_time
            
            # Construir a resposta no formato esperado
            result = {
                "text": response.text,
                "model": model_to_use,
                "elapsed_seconds": elapsed,
                "finish_reason": "stop",  # O Gemini não retorna explicitamente o motivo, assumimos stop
                "usage": {
                    # Gemini não retorna contagem de tokens diretamente
                    "prompt_tokens": None,
                    "completion_tokens": None,
                    "total_tokens": None
                },
                "raw_response": response
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na geração de texto com Gemini: {str(e)}")
            raise
    
    def generate_chat(self, 
                     messages: List[Dict[str, str]], 
                     temperature: float = 0.7,
                     max_tokens: Optional[int] = None,
                     model: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera resposta de chat usando o modelo Gemini.
        
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
            
            # Configurar o modelo
            model = self.client.GenerativeModel(model_name=model_to_use)
            
            # Preparar as configurações de geração
            generation_config = {
                "temperature": temperature,
            }
            
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            # Iniciar uma sessão de chat
            chat = model.start_chat()
            
            # Processar todas as mensagens na ordem
            system_content = None
            
            # Verificar se há uma mensagem de sistema e extraí-la
            for i, message in enumerate(messages):
                if message["role"] == "system":
                    system_content = message["content"]
                    messages.pop(i)
                    break
            
            # Se houver instruções de sistema, adicionar primeiro
            if system_content:
                chat.send_message(system_content, role="system")
            
            # Enviar todas as mensagens mantendo a ordem correta
            for message in messages[:-1]:
                role = message["role"]
                content = message["content"]
                chat.send_message(content, role=role)
            
            # Enviar a última mensagem e obter a resposta
            last_message = messages[-1]
            response = chat.send_message(
                last_message["content"], 
                role=last_message["role"],
                generation_config=generation_config
            )
            
            elapsed = time.time() - start_time
            
            # Construir a resposta no formato esperado
            result = {
                "text": response.text,
                "model": model_to_use,
                "elapsed_seconds": elapsed,
                "finish_reason": "stop",  # O Gemini não retorna explicitamente o motivo, assumimos stop
                "usage": {
                    # Gemini não retorna contagem de tokens diretamente
                    "prompt_tokens": None,
                    "completion_tokens": None,
                    "total_tokens": None
                },
                "raw_response": response
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na geração de chat com Gemini: {str(e)}")
            raise
    
    def embed_text(self, 
                  text: Union[str, List[str]], 
                  model: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera embeddings para o texto fornecido usando o modelo Gemini.
        
        Args:
            text: Texto ou lista de textos para embeddings
            model: Modelo de embedding a ser usado
            
        Returns:
            Dicionário com embeddings gerados
        """
        embedding_model = model or self.DEFAULT_EMBEDDING_MODEL
        
        try:
            start_time = time.time()
            
            # Transformar texto único em lista para processamento consistente
            if isinstance(text, str):
                texts = [text]
            else:
                texts = text
            
            # Obter embeddings
            result_embeddings = []
            for t in texts:
                embedding_result = self.client.embed_content(
                    model=embedding_model,
                    content=t,
                    task_type="RETRIEVAL_QUERY"
                )
                result_embeddings.append(embedding_result.embedding)
            
            elapsed = time.time() - start_time
            
            # Se era só um texto, retornar só um embedding
            if isinstance(text, str):
                embeddings = result_embeddings[0]
            else:
                embeddings = result_embeddings
            
            result = {
                "embeddings": embeddings,
                "model": embedding_model,
                "elapsed_seconds": elapsed,
                "dimensions": len(embeddings[0]) if embeddings else 0
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao gerar embeddings com Google: {str(e)}")
            raise
    
    def validate_api_key(self) -> bool:
        """
        Verifica se a API key do Google é válida.
        
        Returns:
            True se a chave for válida, False caso contrário
        """
        try:
            result = self.generate_text("Olá, teste de validação da API.", max_tokens=10)
            return True
        except Exception as e:
            logger.error(f"Erro ao validar API key do Google: {str(e)}")
            return False