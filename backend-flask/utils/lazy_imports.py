"""
Sistema de Lazy Loading para otimizar inicialização
Carrega módulos apenas quando necessário, evitando erros de inicialização
"""

import logging
import os
from typing import Optional, Any, Dict

logger = logging.getLogger(__name__)

class LazyAPIClient:
    """Cliente lazy para APIs que inicializam apenas quando necessário"""
    
    def __init__(self, client_type: str, area_juridica: str = None):
        self.client_type = client_type
        self.area_juridica = area_juridica
        self._client = None
        self._initialized = False
        self._error = None
    
    def _initialize_client(self):
        """Inicializa o cliente apenas quando necessário"""
        if self._initialized:
            return self._client
            
        try:
            if self.client_type == 'openai':
                import openai
                api_key = os.environ.get('OPENAI_API_KEY')
                if api_key:
                    # Inicialização limpa sem parâmetros extras
                    self._client = openai.OpenAI(api_key=api_key)
                    logger.info(f"✅ OpenAI lazy-loaded para {self.area_juridica or 'sistema'}")
                else:
                    logger.warning(f"❌ OpenAI API key não encontrada para {self.area_juridica or 'sistema'}")
                    
            elif self.client_type == 'anthropic':
                import anthropic
                api_key = os.environ.get('ANTHROPIC_API_KEY')
                if api_key:
                    # Inicialização limpa sem parâmetros extras que podem causar erro
                    self._client = anthropic.Anthropic(
                        api_key=api_key
                    )
                    logger.info(f"✅ Anthropic lazy-loaded para {self.area_juridica or 'sistema'}")
                else:
                    logger.warning(f"❌ Anthropic API key não encontrada para {self.area_juridica or 'sistema'}")
                    
            elif self.client_type == 'gemini':
                import google.generativeai as genai
                # Priorizar GOOGLE_API_KEY que já existe no sistema
                api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY')
                if api_key:
                    genai.configure(api_key=api_key)
                    self._client = genai.GenerativeModel('gemini-pro')
                    logger.info(f"✅ Gemini lazy-loaded com GOOGLE_API_KEY para {self.area_juridica or 'sistema'}")
                else:
                    logger.warning(f"❌ Gemini/Google API key não encontrada para {self.area_juridica or 'sistema'}")
                    
            elif self.client_type == 'qdrant':
                from qdrant_client import QdrantClient
                qdrant_url = os.environ.get('QDRANT_URL')
                qdrant_api_key = os.environ.get('QDRANT_API_KEY')
                if qdrant_url and qdrant_api_key:
                    self._client = QdrantClient(
                        url=qdrant_url,
                        api_key=qdrant_api_key,
                        timeout=30
                    )
                    logger.info(f"✅ Qdrant lazy-loaded para {self.area_juridica or 'sistema'}")
                else:
                    logger.warning(f"❌ Qdrant credentials não encontradas para {self.area_juridica or 'sistema'}")
                    
        except Exception as e:
            self._error = str(e)
            logger.error(f"❌ Erro lazy-loading {self.client_type}: {e}")
            
        self._initialized = True
        return self._client
    
    def get_client(self):
        """Retorna o cliente, inicializando se necessário"""
        if not self._initialized:
            return self._initialize_client()
        return self._client
    
    def is_available(self) -> bool:
        """Verifica se o cliente está disponível"""
        client = self.get_client()
        return client is not None and self._error is None
    
    def get_error(self) -> Optional[str]:
        """Retorna erro de inicialização se houver"""
        if not self._initialized:
            self._initialize_client()
        return self._error
    
    def __getattr__(self, name):
        """Proxy para métodos do cliente real com retry automático"""
        client = self.get_client()
        if client is None:
            # Tentar reinicializar uma vez
            logger.warning(f"Cliente {self.client_type} não inicializado, tentando novamente...")
            self._initialized = False
            self._error = None
            client = self._initialize_client()
            
        if client is None:
            # Se ainda falhou, tentar fallback direto
            logger.error(f"Falha na inicialização lazy do {self.client_type}, tentando fallback direto")
            client = self._fallback_direct_init()
            
        if client is None:
            raise AttributeError(f"Cliente {self.client_type} não pôde ser inicializado após tentativas de retry")
            
        return getattr(client, name)
    
    def _fallback_direct_init(self):
        """Fallback para inicialização direta quando lazy loading falha"""
        try:
            if self.client_type == 'openai':
                import openai
                api_key = os.environ.get('OPENAI_API_KEY')
                if api_key and api_key.startswith('sk-'):
                    # Inicialização simples sem parâmetros problemáticos
                    client = openai.OpenAI(api_key=api_key)
                    logger.info(f"✅ {self.client_type} inicializado via fallback direto")
                    self._client = client
                    return client
                else:
                    logger.error(f"❌ OPENAI_API_KEY inválida ou não encontrada")
                    
            elif self.client_type == 'anthropic':
                import anthropic
                api_key = os.environ.get('ANTHROPIC_API_KEY')
                if api_key:
                    # Inicialização simples sem parâmetros que podem causar conflito
                    client = anthropic.Anthropic(
                        api_key=api_key
                    )
                    logger.info(f"✅ {self.client_type} inicializado via fallback direto")
                    self._client = client
                    return client
                    
        except Exception as e:
            logger.error(f"❌ Erro no fallback direto para {self.client_type}: {e}")
            
        return None

class LazyModuleManager:
    """Gerenciador de módulos com lazy loading"""
    
    def __init__(self):
        self._modules: Dict[str, Any] = {}
        self._errors: Dict[str, str] = {}
    
    def get_module(self, module_name: str, import_path: str = None):
        """Importa módulo apenas quando necessário"""
        if module_name in self._modules:
            return self._modules[module_name]
            
        try:
            if import_path:
                exec(f"import {import_path} as module")
                self._modules[module_name] = locals()['module']
            else:
                exec(f"import {module_name} as module")
                self._modules[module_name] = locals()['module']
                
            logger.info(f"✅ Módulo {module_name} lazy-loaded")
            return self._modules[module_name]
            
        except ImportError as e:
            self._errors[module_name] = str(e)
            logger.warning(f"❌ Módulo {module_name} não disponível: {e}")
            return None
        except Exception as e:
            self._errors[module_name] = str(e)
            logger.error(f"❌ Erro ao carregar {module_name}: {e}")
            return None
    
    def is_module_available(self, module_name: str) -> bool:
        """Verifica se módulo está disponível"""
        return module_name in self._modules or module_name not in self._errors
    
    def get_error(self, module_name: str) -> Optional[str]:
        """Retorna erro de importação se houver"""
        return self._errors.get(module_name)

# Instância global para reutilização
lazy_manager = LazyModuleManager()

def create_lazy_api_client(client_type: str, area_juridica: str = None) -> LazyAPIClient:
    """Factory function para criar clientes lazy"""
    return LazyAPIClient(client_type, area_juridica)

def safe_import(module_name: str, import_path: str = None):
    """Importação segura com lazy loading"""
    return lazy_manager.get_module(module_name, import_path)