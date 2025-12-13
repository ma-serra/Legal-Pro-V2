"""
Classe base para integrações com provedores de IA.
"""
import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union

# Configuração de logging
logger = logging.getLogger(__name__)

class BaseIntegration(ABC):
    """
    Classe base para integrações com provedores de IA.
    Define a interface comum para todas as integrações.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Inicializa a integração.
        
        Args:
            api_key: Chave de API opcional (se não fornecida, busca da variável de ambiente)
            model: Modelo a ser usado como padrão (pode ser alterado a cada chamada)
        """
        self.api_key = api_key
        self.model = model
        self.client = None
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self) -> None:
        """
        Inicializa o cliente da API.
        Deve ser implementado por cada integração.
        """
        pass
    
    @abstractmethod
    def generate_text(self, 
                     prompt: str, 
                     system_prompt: Optional[str] = None,
                     temperature: float = 0.7,
                     max_tokens: Optional[int] = None,
                     model: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera texto baseado no prompt fornecido.
        
        Args:
            prompt: Texto de entrada para gerar a resposta
            system_prompt: Instruções de sistema opcional
            temperature: Controle de aleatoriedade (0.0 a 1.0)
            max_tokens: Número máximo de tokens a serem gerados
            model: Modelo a ser usado (sobreescreve o padrão)
            
        Returns:
            Dicionário com resultados da geração
        """
        pass
    
    @abstractmethod
    def generate_chat(self, 
                     messages: List[Dict[str, str]], 
                     temperature: float = 0.7,
                     max_tokens: Optional[int] = None,
                     model: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera uma resposta de chat baseado em uma lista de mensagens.
        
        Args:
            messages: Lista de mensagens no formato {"role": "...", "content": "..."}
            temperature: Controle de aleatoriedade (0.0 a 1.0)
            max_tokens: Número máximo de tokens a serem gerados
            model: Modelo a ser usado (sobreescreve o padrão)
            
        Returns:
            Dicionário com resultados da geração
        """
        pass
    
    @abstractmethod
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
        pass
    
    def validate_api_key(self) -> bool:
        """
        Verifica se a API key é válida.
        
        Returns:
            True se a chave for válida, False caso contrário
        """
        try:
            if not self.api_key or len(self.api_key.strip()) == 0:
                logger.warning("Chave de API vazia ou não fornecida")
                return False
                
            # Fazemos uma chamada muito simples para validar
            # Em vez de gerar texto (que pode ser caro), usamos uma chamada mais leve
            # quando disponível na implementação específica
            result = self._validate_key_implementation()
            return result
        except Exception as e:
            logger.error(f"Erro ao validar API key: {str(e)}")
            return False
            
    def _validate_key_implementation(self) -> bool:
        """
        Implementação específica para validação da chave.
        Pode ser sobrescrita pelas subclasses para validação mais eficiente.
        
        Por padrão, faz uma chamada simples para generate_text.
        
        Returns:
            True se a chave for válida, False caso contrário
        """
        try:
            result = self.generate_text("Teste de validação", max_tokens=5)
            return True
        except Exception as e:
            logger.error(f"Erro na validação padrão: {str(e)}")
            return False