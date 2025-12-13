"""
Configuração de provedores de IA para o sistema jurídico
Apenas provedores validados e funcionais
"""

import os

# Provedores disponíveis no sistema
PROVIDERS_CONFIG = {
    'openai': {
        'name': 'OpenAI',
        'models': [
            'gpt-4o',
            'gpt-4o-mini',
            'gpt-4-turbo',
            'gpt-4',
            'gpt-3.5-turbo'
        ],
        'default_model': 'gpt-4o',
        'api_key_env': 'OPENAI_API_KEY',
        'enabled': bool(os.environ.get('OPENAI_API_KEY'))
    },
    'anthropic': {
        'name': 'Anthropic Claude',
        'models': [
            'claude-3-5-sonnet-20241022',
            'claude-3-5-haiku-20241022',
            'claude-3-opus-20240229',
            'claude-3-sonnet-20240229',
            'claude-3-haiku-20240307'
        ],
        'default_model': 'claude-3-5-sonnet-20241022',
        'api_key_env': 'ANTHROPIC_API_KEY',
        'enabled': bool(os.environ.get('ANTHROPIC_API_KEY'))
    },
    'google': {
        'name': 'Google Gemini',
        'models': [
            'gemini-1.5-pro',
            'gemini-1.5-flash',
            'gemini-pro'
        ],
        'default_model': 'gemini-1.5-pro',
        'api_key_env': 'GOOGLE_API_KEY_APP',
        'enabled': bool(os.environ.get('GOOGLE_API_KEY_APP'))
    },
    'deepseek': {
        'name': 'DeepSeek',
        'models': [
            'deepseek-chat',
            'deepseek-coder'
        ],
        'default_model': 'deepseek-chat',
        'api_key_env': 'DEEPSEEK_API_KEY',
        'enabled': bool(os.environ.get('DEEPSEEK_API_KEY'))
    },
    'assemblyai': {
        'name': 'AssemblyAI',
        'models': ['best', 'nano'],
        'default_model': 'best',
        'api_key_env': 'ASSEMBLYAI_API_KEY',
        'enabled': bool(os.environ.get('ASSEMBLYAI_API_KEY')),
        'type': 'transcription'
    }
}

def get_available_providers():
    """Retorna lista de provedores disponíveis"""
    return [key for key, config in PROVIDERS_CONFIG.items() if config.get('enabled', False)]

def get_provider_models(provider):
    """Retorna modelos disponíveis para um provedor"""
    return PROVIDERS_CONFIG.get(provider, {}).get('models', [])

def get_default_model(provider):
    """Retorna modelo padrão para um provedor"""
    return PROVIDERS_CONFIG.get(provider, {}).get('default_model', '')

def is_provider_enabled(provider):
    """Verifica se um provedor está habilitado"""
    return PROVIDERS_CONFIG.get(provider, {}).get('enabled', False)

# Classe para compatibilidade com código existente
class APIManager:
    """Gerenciador de APIs para compatibilidade"""
    
    def __init__(self):
        self.providers = PROVIDERS_CONFIG
    
    def get_available_providers(self):
        return get_available_providers()
    
    def get_provider_models(self, provider):
        return get_provider_models(provider)
    
    def get_provider_config(self, provider):
        """Retorna configuração completa de um provedor"""
        return PROVIDERS_CONFIG.get(provider, {})
    
    def is_provider_enabled(self, provider):
        return is_provider_enabled(provider)
    
    def get_primary_provider(self):
        """Retorna provedor primário (primeiro disponível)"""
        available = self.get_available_providers()
        return available[0] if available else 'openai'
    
    def get_model_for_provider(self, provider):
        """Retorna modelo padrão para um provedor"""
        return get_default_model(provider)
    
    def get_fallback_providers(self, exclude=None):
        """Retorna lista de provedores de fallback"""
        available = self.get_available_providers()
        if exclude:
            available = [p for p in available if p != exclude]
        return available
    
    def get_provider_summary(self):
        """Retorna resumo de todos os provedores"""
        return {
            'total': len(self.providers),
            'enabled': len(self.get_available_providers()),
            'providers': {
                k: {
                    'name': v['name'],
                    'enabled': v.get('enabled', False),
                    'models_count': len(v.get('models', []))
                }
                for k, v in self.providers.items()
            }
        }

# Instância global para compatibilidade
api_manager = APIManager()
