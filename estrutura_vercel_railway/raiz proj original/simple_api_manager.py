"""
Sistema simplificado de gerenciamento de APIs sem validações em tempo real
para evitar rate limiting e garantir funcionamento estável
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

class SimpleAPIManager:
    """Gerenciador simplificado de chaves de API"""
    
    def __init__(self):
        self.config_file = "config/simple_api_keys.json"
        self.providers = {
            "openai": {
                "name": "OpenAI (GPT-5 / GPT-4.1)",
                "description": "API da OpenAI para acesso aos modelos GPT",
                "env_var": "OPENAI_API_KEY"
            },
            "anthropic": {
                "name": "Anthropic (Claude 4.5)",
                "description": "API da Anthropic para acesso ao Claude",
                "env_var": "ANTHROPIC_API_KEY"
            },
            "google": {
                "name": "Google (Gemini 2.5)",
                "description": "API da Google para acesso ao Gemini",
                "env_var": "GOOGLE_API_KEY"
            },
            "deepseek": {
                "name": "DeepSeek (R1 / V3)",
                "description": "API da DeepSeek para modelos especializados",
                "env_var": "DEEPSEEK_API_KEY"
            },
            "grok": {
                "name": "Grok X.AI (Grok 4)",
                "description": "API do Grok X.AI para acesso aos modelos Grok",
                "env_var": "XAI_API_KEY"
            },
            "assemblyai": {
                "name": "AssemblyAI",
                "description": "API da AssemblyAI para transcrição de áudio",
                "env_var": "ASSEMBLYAI_API_KEY"
            }
        }
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Obtém o status de cada provedor baseado em variáveis de ambiente"""
        status = {}
        
        for provider_id, provider_info in self.providers.items():
            env_var = provider_info["env_var"]
            api_key = os.getenv(env_var)
            
            has_key = bool(api_key and len(api_key.strip()) > 0)
            is_valid = has_key  # Assumimos válido se existe
            
            status[provider_id] = {
                "name": provider_info["name"],
                "description": provider_info["description"],
                "has_key": has_key,
                "is_valid": is_valid,
                "env_var": env_var
            }
        
        return status
    
    def save_api_key(self, provider: str, api_key: str) -> bool:
        """Salva uma chave de API nas variáveis de ambiente"""
        try:
            if provider not in self.providers:
                return False
            
            env_var = self.providers[provider]["env_var"]
            
            # Salvar na variável de ambiente (temporário)
            os.environ[env_var] = api_key
            
            # Salvar em arquivo para persistência
            self._save_to_file(provider, api_key)
            
            return True
            
        except Exception as e:
            print(f"Erro ao salvar chave de API: {e}")
            return False
    
    def _save_to_file(self, provider: str, api_key: str):
        """Salva chave em arquivo de configuração"""
        try:
            # Criar diretório se não existir
            config_dir = Path(self.config_file).parent
            config_dir.mkdir(exist_ok=True)
            
            # Carregar configuração existente
            config = {}
            if Path(self.config_file).exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            
            # Atualizar com nova chave
            config[provider] = api_key
            
            # Salvar arquivo
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            print(f"Erro ao salvar em arquivo: {e}")

if __name__ == "__main__":
    manager = SimpleAPIManager()
    status = manager.get_provider_status()
    
    print("Status dos provedores de API:")
    for provider_id, info in status.items():
        status_text = "✓ Configurado" if info["has_key"] else "✗ Não configurado"
        print(f"- {info['name']}: {status_text}")