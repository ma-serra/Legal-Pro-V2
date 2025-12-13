"""
Testes para as integrações de API.
"""
import os
import logging
import argparse

# Configuração de logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

def test_openai():
    """
    Testa a integração com OpenAI.
    """
    try:
        from multiagent.integrations import OpenAIIntegration
        
        # Usar a variável de ambiente para a chave
        integration = OpenAIIntegration()
        
        # Testar geração de texto
        prompt = "Me dê 3 ideias de temas para redação sobre direito constitucional."
        result = integration.generate_text(prompt, temperature=0.7, max_tokens=150)
        
        logger.info(f"OpenAI response: {result['text']}")
        logger.info(f"Model: {result['model']}")
        logger.info(f"Tokens: {result['usage']['total_tokens']}")
        
        return True
    except Exception as e:
        logger.error(f"OpenAI test failed: {str(e)}")
        return False

def test_anthropic():
    """
    Testa a integração com Anthropic.
    """
    try:
        from multiagent.integrations import AnthropicIntegration
        
        # Usar a variável de ambiente para a chave
        integration = AnthropicIntegration()
        
        # Testar geração de texto
        prompt = "Me dê 3 ideias de temas para redação sobre direito ambiental."
        result = integration.generate_text(prompt, temperature=0.7, max_tokens=150)
        
        logger.info(f"Anthropic response: {result['text']}")
        logger.info(f"Model: {result['model']}")
        logger.info(f"Tokens: {result['usage']['total_tokens']}")
        
        return True
    except Exception as e:
        logger.error(f"Anthropic test failed: {str(e)}")
        return False

def test_google():
    """
    Testa a integração com Google Gemini.
    """
    try:
        from multiagent.integrations import GoogleIntegration
        
        # Usar a variável de ambiente para a chave
        integration = GoogleIntegration()
        
        # Testar geração de texto
        prompt = "Me dê 3 ideias de temas para redação sobre direito digital."
        result = integration.generate_text(prompt, temperature=0.7, max_tokens=150)
        
        logger.info(f"Google response: {result['text']}")
        logger.info(f"Model: {result['model']}")
        
        return True
    except Exception as e:
        logger.error(f"Google test failed: {str(e)}")
        return False

def test_perplexity():
    """
    Testa a integração com Perplexity.
    """
    try:
        from multiagent.integrations import PerplexityIntegration
        
        # Usar a variável de ambiente para a chave
        integration = PerplexityIntegration()
        
        # Testar geração de texto
        prompt = "Me dê 3 ideias de temas para redação sobre direito empresarial."
        result = integration.generate_text(prompt, temperature=0.7, max_tokens=150)
        
        logger.info(f"Perplexity response: {result['text']}")
        logger.info(f"Model: {result['model']}")
        logger.info(f"Tokens: {result['usage']['total_tokens']}")
        
        return True
    except Exception as e:
        logger.error(f"Perplexity test failed: {str(e)}")
        return False

def test_deepseek():
    """
    Testa a integração com Deepseek.
    """
    try:
        from multiagent.integrations import DeepseekIntegration
        
        # Usar a variável de ambiente para a chave
        integration = DeepseekIntegration()
        
        # Testar geração de texto
        prompt = "Me dê 3 ideias de temas para redação sobre direito contratual."
        result = integration.generate_text(prompt, temperature=0.7, max_tokens=150)
        
        logger.info(f"Deepseek response: {result['text']}")
        logger.info(f"Model: {result['model']}")
        logger.info(f"Tokens: {result['usage']['total_tokens']}")
        
        return True
    except Exception as e:
        logger.error(f"Deepseek test failed: {str(e)}")
        return False

def test_all():
    """
    Testa todas as integrações.
    """
    results = {
        "openai": test_openai(),
        "anthropic": test_anthropic(),
        "google": test_google(),
        "perplexity": test_perplexity(),
        "deepseek": test_deepseek()
    }
    
    # Resumo dos resultados
    logger.info("API Integration Test Results:")
    for provider, success in results.items():
        logger.info(f"  {provider}: {'SUCCESS' if success else 'FAILED'}")
    
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test API integrations")
    parser.add_argument("--provider", choices=["openai", "anthropic", "google", "perplexity", "deepseek", "all"], 
                       default="all", help="Which provider to test")
    
    args = parser.parse_args()
    
    if args.provider == "all":
        test_all()
    elif args.provider == "openai":
        test_openai()
    elif args.provider == "anthropic":
        test_anthropic()
    elif args.provider == "google":
        test_google()
    elif args.provider == "perplexity":
        test_perplexity()
    elif args.provider == "deepseek":
        test_deepseek()