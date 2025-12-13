"""
Teste para a integração com a API Deepseek usando a classe DeepseekIntegration.
"""
import os
import time
import logging
from multiagent.integrations.deepseek_integration import DeepseekIntegration

# Configuração de logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_deepseek_integration():
    """
    Testa a integração com a API do Deepseek usando a classe DeepseekIntegration.
    """
    try:
        logger.info("Inicializando integração com Deepseek...")
        
        # Tentar inicializar a integração
        integration = DeepseekIntegration()
        
        logger.info(f"Integração inicializada. Usando modelo padrão: {integration.model}")
        
        # Testar uma geração de texto simples
        logger.info("Testando geração de texto...")
        start_time = time.time()
        
        result = integration.generate_text(
            prompt="Me dê 1 ideia de tema para redação sobre direito contratual. Limite a 10 palavras.",
            system_prompt="Você é um assistente jurídico especializado. Seja breve.",
            max_tokens=20
        )
        
        elapsed = time.time() - start_time
        
        # Mostrar os resultados
        logger.info(f"Resposta recebida: {result['text']}")
        logger.info(f"Modelo usado: {result['model']}")
        logger.info(f"Tokens usados: {result['usage']['total_tokens']}")
        logger.info(f"Tempo total: {elapsed:.2f} segundos")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro ao testar integração com Deepseek: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("Iniciando teste da integração com Deepseek...")
    success = test_deepseek_integration()
    logger.info(f"Teste concluído: {'SUCESSO' if success else 'FALHA'}")