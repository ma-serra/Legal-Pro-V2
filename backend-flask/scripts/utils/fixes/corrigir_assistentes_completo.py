"""
Script para corrigir completamente os assistentes jurídicos
Adiciona método processar_consulta_completa e atualiza templates
"""

import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def adicionar_metodo_processar_consulta(arquivo_assistente):
    """Adiciona método processar_consulta_completa se não existir"""
    try:
        with open(arquivo_assistente, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Verificar se método já existe
        if 'def processar_consulta_completa(' in conteudo:
            logger.info(f"Método já existe em {arquivo_assistente}")
            return True
        
        # Adicionar método ao final da classe, antes do último fechamento
        metodo_processar = '''
    def processar_consulta_completa(self, pergunta: str, api_escolhida: str = "openai", 
                                  estilo: str = "juridico_tecnico", 
                                  usar_base_vetorial: bool = True):
        """Processa consulta completa usando assistente base"""
        try:
            # Usar o método da classe base
            return super().processar_consulta_completa(pergunta, api_escolhida, estilo, usar_base_vetorial)
        except Exception as e:
            logger.error(f"Erro ao processar consulta: {e}")
            return {
                'resposta': f"Erro ao processar consulta: {str(e)}",
                'contexto_usado': False,
                'resultados_busca': [],
                'api_utilizada': api_escolhida,
                'status': 'erro'
            }
'''
        
        # Encontrar a posição para inserir o método
        lines = conteudo.split('\n')
        insert_position = -1
        
        # Procurar pela última linha da classe (antes do último bloco de código)
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip() and not lines[i].startswith(' ') and not lines[i].startswith('\t'):
                insert_position = i
                break
        
        if insert_position > 0:
            lines.insert(insert_position, metodo_processar)
            conteudo_atualizado = '\n'.join(lines)
            
            with open(arquivo_assistente, 'w', encoding='utf-8') as f:
                f.write(conteudo_atualizado)
            
            logger.info(f"✅ Método adicionado em {arquivo_assistente}")
            return True
        else:
            logger.error(f"Não foi possível localizar posição para inserir método em {arquivo_assistente}")
            return False
            
    except Exception as e:
        logger.error(f"Erro ao atualizar {arquivo_assistente}: {e}")
        return False

def corrigir_todos_assistentes():
    """Corrige todos os assistentes especializados"""
    
    assistentes = [
        'modules/assistentes/assistente_analise_riscos.py',
        'modules/assistentes/assistente_recuperacao.py',
        'modules/assistentes/assistente_empresarial.py',
        'modules/assistentes/assistente_agrario.py'
    ]
    
    sucesso_total = True
    
    for assistente in assistentes:
        if os.path.exists(assistente):
            if not adicionar_metodo_processar_consulta(assistente):
                sucesso_total = False
        else:
            logger.warning(f"Arquivo não encontrado: {assistente}")
    
    return sucesso_total

def atualizar_config_api_providers():
    """Corrige config/api_providers.py para incluir api_manager"""
    try:
        config_content = '''"""
Configuração de provedores de IA para o sistema jurídico
Apenas provedores validados e funcionais
"""

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
        'enabled': True
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
        'enabled': True
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
        'enabled': True
    },
    'deepseek': {
        'name': 'DeepSeek',
        'models': [
            'deepseek-chat',
            'deepseek-coder'
        ],
        'default_model': 'deepseek-chat',
        'api_key_env': 'DEEPSEEK_API_KEY',
        'enabled': True
    }
}

def get_available_providers():
    """Retorna lista de provedores disponíveis"""
    return [key for key, config in PROVIDERS_CONFIG.items() if config['enabled']]

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
    
    def is_provider_enabled(self, provider):
        return is_provider_enabled(provider)

# Instância global para compatibilidade
api_manager = APIManager()
'''

        with open('config/api_providers.py', 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        logger.info("✅ config/api_providers.py atualizado com api_manager")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao atualizar config/api_providers.py: {e}")
        return False

def main():
    """Função principal"""
    logger.info("🚀 Iniciando correção completa dos assistentes...")
    
    sucesso = True
    
    # Corrigir configuração de API
    if not atualizar_config_api_providers():
        sucesso = False
    
    # Corrigir assistentes
    if not corrigir_todos_assistentes():
        sucesso = False
    
    if sucesso:
        logger.info("🎉 Correção completa dos assistentes finalizada com sucesso!")
    else:
        logger.error("❌ Correção finalizada com alguns problemas")
    
    return sucesso

if __name__ == "__main__":
    main()