"""
Calculadora de preços precisa baseada na documentação oficial de cada provedor
Inclui conversão para Real brasileiro (R$) com taxa de câmbio atualizada
"""

import json
import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PricingCalculator:
    """Calculadora de custos baseada em preços oficiais dos provedores"""
    
    def __init__(self):
        self.pricing_data = self._load_official_pricing()
        self.last_updated = datetime.now()
        self.usd_to_brl_rate = 5.25  # Taxa padrão, será atualizada dinamicamente
        self.exchange_rate_updated = None
        self._update_exchange_rate()
    
    def _load_official_pricing(self) -> Dict[str, Any]:
        """Carrega preços oficiais atualizados dos provedores"""
        
        # Preços baseados na documentação oficial (em USD por token)
        return {
            "openai": {
                "models": {
                    "gpt-4o": {
                        "input_cost_per_1k": 0.005,   # $5.00 per 1M tokens
                        "output_cost_per_1k": 0.015,  # $15.00 per 1M tokens
                        "context_window": 128000,
                        "updated": "2024-12-01"
                    },
                    "gpt-4o-mini": {
                        "input_cost_per_1k": 0.00015, # $0.15 per 1M tokens
                        "output_cost_per_1k": 0.0006, # $0.60 per 1M tokens
                        "context_window": 128000,
                        "updated": "2024-12-01"
                    },
                    "gpt-4": {
                        "input_cost_per_1k": 0.03,    # $30.00 per 1M tokens
                        "output_cost_per_1k": 0.06,   # $60.00 per 1M tokens
                        "context_window": 8192,
                        "updated": "2024-12-01"
                    },
                    "gpt-3.5-turbo": {
                        "input_cost_per_1k": 0.0005,  # $0.50 per 1M tokens
                        "output_cost_per_1k": 0.0015, # $1.50 per 1M tokens
                        "context_window": 16385,
                        "updated": "2024-12-01"
                    }
                },
                "audio": {
                    "whisper-1": {
                        "cost_per_minute": 0.006,     # $0.006 per minute
                        "updated": "2024-12-01"
                    }
                },
                "images": {
                    "dall-e-3": {
                        "1024x1024": 0.040,           # $0.040 per image
                        "1792x1024": 0.080,           # $0.080 per image
                        "1024x1792": 0.080,           # $0.080 per image
                        "updated": "2024-12-01"
                    }
                }
            },
            "anthropic": {
                "models": {
                    "claude-3-5-sonnet-20241022": {
                        "input_cost_per_1k": 0.003,   # $3.00 per 1M tokens
                        "output_cost_per_1k": 0.015,  # $15.00 per 1M tokens
                        "context_window": 200000,
                        "updated": "2024-12-01"
                    },
                    "claude-3-opus-20240229": {
                        "input_cost_per_1k": 0.015,   # $15.00 per 1M tokens
                        "output_cost_per_1k": 0.075,  # $75.00 per 1M tokens
                        "context_window": 200000,
                        "updated": "2024-12-01"
                    },
                    "claude-3-sonnet-20240229": {
                        "input_cost_per_1k": 0.003,   # $3.00 per 1M tokens
                        "output_cost_per_1k": 0.015,  # $15.00 per 1M tokens
                        "context_window": 200000,
                        "updated": "2024-12-01"
                    },
                    "claude-3-haiku-20240307": {
                        "input_cost_per_1k": 0.00025, # $0.25 per 1M tokens
                        "output_cost_per_1k": 0.00125,# $1.25 per 1M tokens
                        "context_window": 200000,
                        "updated": "2024-12-01"
                    }
                }
            },
            "google": {
                "models": {
                    "gemini-1.5-pro": {
                        "input_cost_per_1k": 0.0035,  # $3.50 per 1M tokens
                        "output_cost_per_1k": 0.0105, # $10.50 per 1M tokens
                        "context_window": 2000000,
                        "updated": "2024-12-01"
                    },
                    "gemini-1.5-flash": {
                        "input_cost_per_1k": 0.00015, # $0.15 per 1M tokens
                        "output_cost_per_1k": 0.0006, # $0.60 per 1M tokens
                        "context_window": 1000000,
                        "updated": "2024-12-01"
                    },
                    "gemini-pro": {
                        "input_cost_per_1k": 0.0005,  # $0.50 per 1M tokens
                        "output_cost_per_1k": 0.0015, # $1.50 per 1M tokens
                        "context_window": 32768,
                        "updated": "2024-12-01"
                    }
                }
            },
            "deepseek": {
                "models": {
                    "deepseek-chat": {
                        "input_cost_per_1k": 0.00014, # $0.14 per 1M tokens
                        "output_cost_per_1k": 0.00028,# $0.28 per 1M tokens
                        "context_window": 32768,
                        "updated": "2024-12-01"
                    },
                    "deepseek-coder": {
                        "input_cost_per_1k": 0.00014, # $0.14 per 1M tokens
                        "output_cost_per_1k": 0.00028,# $0.28 per 1M tokens
                        "context_window": 16384,
                        "updated": "2024-12-01"
                    }
                }
            },
            "assemblyai": {
                "transcription": {
                    "core": {
                        "cost_per_hour": 0.37,        # $0.37 per audio hour
                        "features": ["basic_transcription"],
                        "updated": "2024-12-01"
                    },
                    "speaker_diarization": {
                        "cost_per_hour": 0.10,        # Additional $0.10 per hour
                        "updated": "2024-12-01"
                    },
                    "sentiment_analysis": {
                        "cost_per_hour": 0.035,       # Additional $0.035 per hour
                        "updated": "2024-12-01"
                    },
                    "auto_chapters": {
                        "cost_per_hour": 0.055,       # Additional $0.055 per hour
                        "updated": "2024-12-01"
                    },
                    "entity_detection": {
                        "cost_per_hour": 0.035,       # Additional $0.035 per hour
                        "updated": "2024-12-01"
                    },
                    "auto_highlights": {
                        "cost_per_hour": 0.055,       # Additional $0.055 per hour
                        "updated": "2024-12-01"
                    }
                }
            }
        }
    
    def _update_exchange_rate(self):
        """Atualiza a taxa de câmbio USD para BRL"""
        try:
            # Usar API gratuita para obter taxa de câmbio atual
            response = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.usd_to_brl_rate = data['rates'].get('BRL', 5.25)
                self.exchange_rate_updated = datetime.now()
                logger.info(f"Taxa USD/BRL atualizada: {self.usd_to_brl_rate}")
            else:
                logger.warning("Falha ao obter taxa de câmbio, usando valor padrão")
        except Exception as e:
            logger.warning(f"Erro ao atualizar taxa de câmbio: {e}, usando valor padrão")
            if not self.exchange_rate_updated:
                self.exchange_rate_updated = datetime.now()
    
    def _convert_to_brl(self, usd_amount: float) -> float:
        """Converte valor em USD para BRL"""
        # Atualizar taxa se necessário (a cada 6 horas)
        if (not self.exchange_rate_updated or 
            datetime.now() - self.exchange_rate_updated > timedelta(hours=6)):
            self._update_exchange_rate()
        
        return round(usd_amount * self.usd_to_brl_rate, 4)
    
    def _add_brl_conversion(self, cost_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adiciona conversão BRL aos dados de custo"""
        if 'error' in cost_data:
            return cost_data
        
        # Converter custos individuais
        if 'total_cost' in cost_data:
            cost_data['total_cost_brl'] = self._convert_to_brl(cost_data['total_cost'])
        
        if 'input_cost' in cost_data:
            cost_data['input_cost_brl'] = self._convert_to_brl(cost_data['input_cost'])
        
        if 'output_cost' in cost_data:
            cost_data['output_cost_brl'] = self._convert_to_brl(cost_data['output_cost'])
        
        if 'base_cost' in cost_data:
            cost_data['base_cost_brl'] = self._convert_to_brl(cost_data['base_cost'])
        
        if 'total_feature_cost' in cost_data:
            cost_data['total_feature_cost_brl'] = self._convert_to_brl(cost_data['total_feature_cost'])
        
        # Converter custos de features
        if 'feature_costs' in cost_data:
            cost_data['feature_costs_brl'] = {
                feature: self._convert_to_brl(cost)
                for feature, cost in cost_data['feature_costs'].items()
            }
        
        # Adicionar informações da taxa de câmbio
        cost_data['exchange_rate'] = {
            'usd_to_brl': self.usd_to_brl_rate,
            'updated_at': self.exchange_rate_updated.isoformat() if self.exchange_rate_updated else None
        }
        
        return cost_data
    
    def calculate_text_cost(self, provider: str, model: str, 
                          input_tokens: int, output_tokens: int = 0) -> Dict[str, Any]:
        """Calcula custo para geração de texto"""
        try:
            provider_data = self.pricing_data.get(provider.lower())
            if not provider_data or 'models' not in provider_data:
                return {'error': f'Provedor {provider} não encontrado'}
            
            model_data = provider_data['models'].get(model)
            if not model_data:
                return {'error': f'Modelo {model} não encontrado para {provider}'}
            
            input_cost = (input_tokens / 1000) * model_data['input_cost_per_1k']
            output_cost = (output_tokens / 1000) * model_data['output_cost_per_1k']
            total_cost = input_cost + output_cost
            
            result = {
                'provider': provider,
                'model': model,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'total_tokens': input_tokens + output_tokens,
                'input_cost': round(input_cost, 6),
                'output_cost': round(output_cost, 6),
                'total_cost': round(total_cost, 6),
                'cost_per_1k_input': model_data['input_cost_per_1k'],
                'cost_per_1k_output': model_data['output_cost_per_1k'],
                'context_window': model_data['context_window'],
                'calculated_at': datetime.now().isoformat()
            }
            
            return self._add_brl_conversion(result)
            
        except Exception as e:
            logger.error(f"Erro ao calcular custo de texto: {e}")
            return {'error': str(e)}
    
    def calculate_audio_cost(self, provider: str, duration_minutes: float, 
                           features: list = None) -> Dict[str, Any]:
        """Calcula custo para transcrição de áudio"""
        try:
            if provider.lower() == 'openai':
                model_data = self.pricing_data['openai']['audio']['whisper-1']
                total_cost = duration_minutes * model_data['cost_per_minute']
                
                return {
                    'provider': provider,
                    'service': 'whisper-1',
                    'duration_minutes': duration_minutes,
                    'cost_per_minute': model_data['cost_per_minute'],
                    'total_cost': round(total_cost, 6),
                    'features': ['transcription'],
                    'calculated_at': datetime.now().isoformat()
                }
            
            elif provider.lower() == 'assemblyai':
                duration_hours = duration_minutes / 60
                pricing = self.pricing_data['assemblyai']['transcription']
                
                # Custo base
                base_cost = duration_hours * pricing['core']['cost_per_hour']
                feature_costs = {}
                total_feature_cost = 0
                
                # Adicionar custos de features
                if features:
                    for feature in features:
                        if feature in pricing and feature != 'core':
                            feature_cost = duration_hours * pricing[feature]['cost_per_hour']
                            feature_costs[feature] = round(feature_cost, 6)
                            total_feature_cost += feature_cost
                
                total_cost = base_cost + total_feature_cost
                
                result = {
                    'provider': provider,
                    'service': 'transcription',
                    'duration_minutes': duration_minutes,
                    'duration_hours': round(duration_hours, 3),
                    'base_cost': round(base_cost, 6),
                    'feature_costs': feature_costs,
                    'total_feature_cost': round(total_feature_cost, 6),
                    'total_cost': round(total_cost, 6),
                    'features': features or ['core'],
                    'calculated_at': datetime.now().isoformat()
                }
                
                return self._add_brl_conversion(result)
            
            else:
                return {'error': f'Provedor de áudio {provider} não suportado'}
                
        except Exception as e:
            logger.error(f"Erro ao calcular custo de áudio: {e}")
            return {'error': str(e)}
    
    def calculate_image_cost(self, provider: str, model: str, size: str, 
                           count: int = 1) -> Dict[str, Any]:
        """Calcula custo para geração de imagens"""
        try:
            if provider.lower() != 'openai':
                return {'error': f'Geração de imagem não suportada para {provider}'}
            
            image_data = self.pricing_data['openai']['images'].get(model)
            if not image_data:
                return {'error': f'Modelo de imagem {model} não encontrado'}
            
            cost_per_image = image_data.get(size)
            if cost_per_image is None:
                return {'error': f'Tamanho {size} não suportado para {model}'}
            
            total_cost = cost_per_image * count
            
            return {
                'provider': provider,
                'model': model,
                'size': size,
                'count': count,
                'cost_per_image': cost_per_image,
                'total_cost': round(total_cost, 6),
                'calculated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular custo de imagem: {e}")
            return {'error': str(e)}
    
    def estimate_component_cost(self, component: str, usage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Estima custo para um componente específico do sistema"""
        try:
            estimates = {}
            
            # Mapeamento de componentes para tipos de uso típicos
            component_patterns = {
                'assistentes_juridicos': {
                    'avg_input_tokens': 1500,
                    'avg_output_tokens': 800,
                    'requests_per_day': 50
                },
                'agentes_multiagent': {
                    'avg_input_tokens': 2000,
                    'avg_output_tokens': 1200,
                    'requests_per_day': 30
                },
                'transcricao_audio': {
                    'avg_duration_minutes': 15,
                    'sessions_per_day': 20,
                    'features': ['speaker_diarization', 'sentiment_analysis', 'entity_detection']
                },
                'transcricao_video': {
                    'avg_duration_minutes': 25,
                    'sessions_per_day': 10,
                    'features': ['speaker_diarization', 'auto_chapters', 'entity_detection']
                },
                'analise_sentimento': {
                    'avg_input_tokens': 800,
                    'avg_output_tokens': 200,
                    'requests_per_day': 40
                },
                'chat_juridico': {
                    'avg_input_tokens': 1200,
                    'avg_output_tokens': 600,
                    'requests_per_day': 100
                }
            }
            
            pattern = component_patterns.get(component, {})
            if not pattern:
                return {'error': f'Padrão não definido para componente {component}'}
            
            # Calcular custos por provedor
            if 'transcricao' in component:
                # Componentes de transcrição
                duration = pattern['avg_duration_minutes']
                sessions = pattern['sessions_per_day']
                features = pattern['features']
                
                # OpenAI Whisper
                openai_cost = self.calculate_audio_cost('openai', duration)
                if 'error' not in openai_cost:
                    estimates['openai_whisper'] = {
                        'daily_cost': openai_cost['total_cost'] * sessions,
                        'monthly_cost': openai_cost['total_cost'] * sessions * 30,
                        'cost_per_session': openai_cost['total_cost']
                    }
                
                # AssemblyAI
                assemblyai_cost = self.calculate_audio_cost('assemblyai', duration, features)
                if 'error' not in assemblyai_cost:
                    estimates['assemblyai'] = {
                        'daily_cost': assemblyai_cost['total_cost'] * sessions,
                        'monthly_cost': assemblyai_cost['total_cost'] * sessions * 30,
                        'cost_per_session': assemblyai_cost['total_cost']
                    }
            
            else:
                # Componentes de texto
                input_tokens = pattern['avg_input_tokens']
                output_tokens = pattern['avg_output_tokens']
                requests = pattern['requests_per_day']
                
                # Calcular para cada provedor
                providers_models = [
                    ('openai', 'gpt-4o'),
                    ('openai', 'gpt-4o-mini'),
                    ('anthropic', 'claude-3-5-sonnet-20241022'),
                    ('anthropic', 'claude-3-haiku-20240307'),
                    ('google', 'gemini-1.5-pro'),
                    ('google', 'gemini-1.5-flash'),
                    ('deepseek', 'deepseek-chat')
                ]
                
                for provider, model in providers_models:
                    cost_calc = self.calculate_text_cost(provider, model, input_tokens, output_tokens)
                    if 'error' not in cost_calc:
                        key = f"{provider}_{model.replace('-', '_').replace('.', '_')}"
                        estimates[key] = {
                            'daily_cost': cost_calc['total_cost'] * requests,
                            'monthly_cost': cost_calc['total_cost'] * requests * 30,
                            'cost_per_request': cost_calc['total_cost']
                        }
            
            return {
                'component': component,
                'estimates': estimates,
                'usage_pattern': pattern,
                'calculated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao estimar custo do componente: {e}")
            return {'error': str(e)}
    
    def get_pricing_info(self, provider: str = None, model: str = None) -> Dict[str, Any]:
        """Retorna informações de preços atualizadas"""
        try:
            if provider and model:
                provider_data = self.pricing_data.get(provider.lower(), {})
                if 'models' in provider_data:
                    model_data = provider_data['models'].get(model)
                    if model_data:
                        return {
                            'provider': provider,
                            'model': model,
                            'pricing': model_data,
                            'last_updated': self.last_updated.isoformat()
                        }
                return {'error': f'Modelo {model} não encontrado para {provider}'}
            
            elif provider:
                provider_data = self.pricing_data.get(provider.lower())
                if provider_data:
                    return {
                        'provider': provider,
                        'pricing': provider_data,
                        'last_updated': self.last_updated.isoformat()
                    }
                return {'error': f'Provedor {provider} não encontrado'}
            
            else:
                return {
                    'all_providers': list(self.pricing_data.keys()),
                    'pricing_data': self.pricing_data,
                    'last_updated': self.last_updated.isoformat()
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter informações de preços: {e}")
            return {'error': str(e)}
    
    def compare_providers(self, input_tokens: int, output_tokens: int = 0, 
                         service_type: str = 'text') -> Dict[str, Any]:
        """Compara custos entre todos os provedores disponíveis"""
        try:
            comparisons = []
            
            if service_type == 'text':
                providers_models = [
                    ('openai', 'gpt-4o'),
                    ('openai', 'gpt-4o-mini'),
                    ('openai', 'gpt-3.5-turbo'),
                    ('anthropic', 'claude-3-5-sonnet-20241022'),
                    ('anthropic', 'claude-3-haiku-20240307'),
                    ('google', 'gemini-1.5-pro'),
                    ('google', 'gemini-1.5-flash'),
                    ('deepseek', 'deepseek-chat')
                ]
                
                for provider, model in providers_models:
                    cost_calc = self.calculate_text_cost(provider, model, input_tokens, output_tokens)
                    if 'error' not in cost_calc:
                        comparisons.append(cost_calc)
                
                # Ordenar por custo total
                comparisons.sort(key=lambda x: x['total_cost'])
                
                return {
                    'service_type': service_type,
                    'input_tokens': input_tokens,
                    'output_tokens': output_tokens,
                    'comparisons': comparisons,
                    'cheapest': comparisons[0] if comparisons else None,
                    'most_expensive': comparisons[-1] if comparisons else None,
                    'calculated_at': datetime.now().isoformat()
                }
            
            else:
                return {'error': f'Tipo de serviço {service_type} não suportado para comparação'}
                
        except Exception as e:
            logger.error(f"Erro na comparação de provedores: {e}")
            return {'error': str(e)}

# Instância global da calculadora
pricing_calculator = PricingCalculator()