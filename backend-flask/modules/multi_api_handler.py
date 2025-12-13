"""
Handler unificado para múltiplas APIs de IA
Gerencia OpenAI, Anthropic, DeepSeek e Gemini de forma inteligente
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import aiohttp

# Importações das APIs
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from config.api_providers import api_manager

logger = logging.getLogger(__name__)

class MultiAPIHandler:
    """Handler inteligente para múltiplas APIs de IA"""
    
    def __init__(self):
        self.clients = {}
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Inicializa clientes das APIs disponíveis"""
        
        # OpenAI - Sem parâmetro proxies
        if OPENAI_AVAILABLE:
            try:
                self.clients['openai'] = OpenAI(
                    api_key=os.environ.get('OPENAI_API_KEY')
                )
                logger.info("✅ Cliente OpenAI inicializado")
            except Exception as e:
                logger.error(f"❌ Erro ao inicializar OpenAI: {e}")
        
        # Anthropic - Sem parâmetro proxies
        if ANTHROPIC_AVAILABLE:
            try:
                self.clients['anthropic'] = anthropic.Anthropic(
                    api_key=os.environ.get('ANTHROPIC_API_KEY')
                )
                logger.info("✅ Cliente Anthropic inicializado")
            except Exception as e:
                logger.error(f"❌ Erro ao inicializar Anthropic: {e}")
        
        # Gemini - Sem parâmetro proxies
        if GEMINI_AVAILABLE:
            try:
                import google.generativeai as genai
                genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
                self.clients['gemini'] = genai.GenerativeModel('gemini-1.5-pro')
                logger.info("✅ Cliente Gemini inicializado")
            except Exception as e:
                logger.error(f"❌ Erro ao inicializar Gemini: {e}")
        
        # DeepSeek (via OpenAI-compatible API) - Sem parâmetro proxies
        if OPENAI_AVAILABLE:
            try:
                self.clients['deepseek'] = OpenAI(
                    api_key=os.environ.get('DEEPSEEK_API_KEY'),
                    base_url="https://api.deepseek.com"
                )
                logger.info("✅ Cliente DeepSeek inicializado")
            except Exception as e:
                logger.error(f"❌ Erro ao inicializar DeepSeek: {e}")
    
    def generate_response(self, 
                         prompt: str, 
                         provider: Optional[str] = None,
                         model: Optional[str] = None,
                         max_tokens: int = 2000,
                         temperature: float = 0.7,
                         context: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera resposta usando o provedor especificado ou o melhor disponível
        """
        
        # Determinar provedor
        if not provider or provider not in self.clients:
            provider = api_manager.get_primary_provider()
            if not provider:
                return {
                    'success': False,
                    'error': 'Nenhum provedor de IA disponível',
                    'provider': None
                }
        
        # Determinar modelo
        if not model:
            model = api_manager.get_model_for_provider(provider)
        
        # Tentar gerar resposta
        try:
            return self._call_provider(provider, model, prompt, max_tokens, temperature, context)
        except Exception as e:
            logger.error(f"Erro com {provider}: {e}")
            
            # Tentar fallback
            fallback_providers = api_manager.get_fallback_providers(exclude=provider)
            for fallback_provider in fallback_providers:
                try:
                    fallback_model = api_manager.get_model_for_provider(fallback_provider)
                    logger.info(f"Tentando fallback: {fallback_provider}")
                    return self._call_provider(fallback_provider, fallback_model, prompt, max_tokens, temperature, context)
                except Exception as fallback_e:
                    logger.error(f"Erro no fallback {fallback_provider}: {fallback_e}")
                    continue
            
            return {
                'success': False,
                'error': f'Todos os provedores falharam. Último erro: {str(e)}',
                'provider': provider
            }
    
    def _call_provider(self, provider: str, model: str, prompt: str, 
                      max_tokens: int, temperature: float, context: Optional[str]) -> Dict[str, Any]:
        """Chama um provedor específico"""
        
        start_time = datetime.now()
        
        if provider == 'openai':
            return self._call_openai(model, prompt, max_tokens, temperature, context, start_time)
        elif provider == 'anthropic':
            return self._call_anthropic(model, prompt, max_tokens, temperature, context, start_time)
        elif provider == 'gemini':
            return self._call_gemini(model, prompt, max_tokens, temperature, context, start_time)
        elif provider == 'deepseek':
            return self._call_deepseek(model, prompt, max_tokens, temperature, context, start_time)
        else:
            raise ValueError(f"Provedor não suportado: {provider}")
    
    def _call_openai(self, model: str, prompt: str, max_tokens: int, 
                    temperature: float, context: Optional[str], start_time: datetime) -> Dict[str, Any]:
        """Chama API OpenAI"""
        client = self.clients['openai']
        
        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        end_time = datetime.now()
        
        return {
            'success': True,
            'response': response.choices[0].message.content,
            'provider': 'OpenAI',
            'model': model,
            'tokens_used': response.usage.total_tokens if response.usage else 0,
            'response_time': (end_time - start_time).total_seconds(),
            'timestamp': end_time.isoformat()
        }
    
    def _call_anthropic(self, model: str, prompt: str, max_tokens: int, 
                       temperature: float, context: Optional[str], start_time: datetime) -> Dict[str, Any]:
        """Chama API Anthropic"""
        client = self.clients['anthropic']
        
        full_prompt = prompt
        if context:
            full_prompt = f"{context}\n\nHuman: {prompt}\n\nAssistant:"
        
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": full_prompt}]
        )
        
        end_time = datetime.now()
        
        return {
            'success': True,
            'response': response.content[0].text,
            'provider': 'Anthropic',
            'model': model,
            'tokens_used': response.usage.input_tokens + response.usage.output_tokens,
            'response_time': (end_time - start_time).total_seconds(),
            'timestamp': end_time.isoformat()
        }
    
    def _call_gemini(self, model: str, prompt: str, max_tokens: int, 
                    temperature: float, context: Optional[str], start_time: datetime) -> Dict[str, Any]:
        """Chama API Gemini"""
        client = self.clients['gemini']
        
        full_prompt = prompt
        if context:
            full_prompt = f"{context}\n\n{prompt}"
        
        response = client.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature
            )
        )
        
        end_time = datetime.now()
        
        return {
            'success': True,
            'response': response.text,
            'provider': 'Gemini',
            'model': model,
            'tokens_used': 0,  # Gemini não retorna contagem de tokens
            'response_time': (end_time - start_time).total_seconds(),
            'timestamp': end_time.isoformat()
        }
    
    def _call_deepseek(self, model: str, prompt: str, max_tokens: int, 
                      temperature: float, context: Optional[str], start_time: datetime) -> Dict[str, Any]:
        """Chama API DeepSeek"""
        client = self.clients['deepseek']
        
        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        end_time = datetime.now()
        
        return {
            'success': True,
            'response': response.choices[0].message.content,
            'provider': 'DeepSeek',
            'model': model,
            'tokens_used': response.usage.total_tokens if response.usage else 0,
            'response_time': (end_time - start_time).total_seconds(),
            'timestamp': end_time.isoformat()
        }
    
    def analyze_sentiment(self, text: str, provider: Optional[str] = None) -> Dict[str, Any]:
        """Analisa sentimento usando IA"""
        
        prompt = f"""
        Analise o sentimento do seguinte texto e retorne APENAS um JSON válido com esta estrutura:
        {{
            "sentiment": "positive|negative|neutral",
            "confidence": 0.0-1.0,
            "emotions": ["emotion1", "emotion2"],
            "summary": "breve resumo da análise"
        }}
        
        Texto para análise: {text}
        """
        
        result = self.generate_response(
            prompt=prompt,
            provider=provider,
            temperature=0.3,
            max_tokens=500,
            context="Você é um especialista em análise de sentimentos. Responda apenas com JSON válido."
        )
        
        if result['success']:
            try:
                # Limpar resposta para extrair apenas o JSON
                response_text = result['response'].strip()
                if response_text.startswith('```json'):
                    response_text = response_text.replace('```json', '').replace('```', '').strip()
                elif response_text.startswith('```'):
                    response_text = response_text.replace('```', '').strip()
                
                sentiment_data = json.loads(response_text)
                return {
                    'success': True,
                    'sentiment_data': sentiment_data,
                    'provider': result['provider']
                }
            except json.JSONDecodeError as e:
                logger.error(f"Erro ao decodificar JSON: {e}, Resposta: {result['response']}")
                # Criar resposta estruturada baseada na análise textual
                response_lower = result['response'].lower()
                
                # Determinar sentimento básico
                if any(word in response_lower for word in ['positiv', 'alegr', 'feliz', 'bom', 'ótimo']):
                    sentiment = 'positive'
                    confidence = 0.8
                elif any(word in response_lower for word in ['negativ', 'trist', 'ruim', 'péssimo', 'problem']):
                    sentiment = 'negative'
                    confidence = 0.8
                else:
                    sentiment = 'neutral'
                    confidence = 0.6
                
                return {
                    'success': True,
                    'sentiment_data': {
                        'sentiment': sentiment,
                        'confidence': confidence,
                        'emotions': ['analyzed'],
                        'summary': f'Análise processada via {result["provider"]}'
                    },
                    'provider': result['provider']
                }
        
        return result
    
    def get_available_providers(self) -> List[str]:
        """Retorna lista de provedores disponíveis"""
        return list(self.clients.keys())
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status de todos os provedores"""
        status = {
            'total_providers': len(api_manager.providers),
            'available_providers': len(self.clients),
            'providers': {}
        }
        
        for provider_id, config in api_manager.providers.items():
            status['providers'][provider_id] = {
                'name': config['name'],
                'enabled': config['enabled'],
                'available': provider_id in self.clients,
                'default_model': config['default_model']
            }
        
        return status

# Instância global
multi_api = MultiAPIHandler()