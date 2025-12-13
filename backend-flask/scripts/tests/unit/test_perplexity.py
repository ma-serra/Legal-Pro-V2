"""
Teste de integração com a API do Perplexity.
"""
import os
import logging
import requests
import json
import time

# Configuração de logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# URL da API
API_URL = "https://api.perplexity.ai/chat/completions"

def test_perplexity():
    """
    Testa a integração com a API do Perplexity usando diretamente requests.
    """
    try:
        # Obter a chave da API
        api_key = os.environ.get("PERPLEXITY_API_KEY")
        
        if not api_key:
            logger.error("PERPLEXITY_API_KEY não está definida nas variáveis de ambiente.")
            return False
        
        # Montar o payload da requisição
        payload = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {"role": "system", "content": "Você é um assistente jurídico especializado."},
                {"role": "user", "content": "Me dê 3 ideias de temas para redação sobre direito empresarial."}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        # Montar os cabeçalhos
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Fazer a requisição
        start_time = time.time()
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload
        )
        
        # Verificar se a requisição foi bem-sucedida
        response.raise_for_status()
        
        # Processar a resposta
        response_data = response.json()
        
        elapsed = time.time() - start_time
        
        # Mostrar os resultados
        logger.info(f"Perplexity response: {response_data['choices'][0]['message']['content']}")
        logger.info(f"Model: {response_data['model']}")
        logger.info(f"Total tokens: {response_data['usage']['total_tokens']}")
        logger.info(f"Elapsed time: {elapsed:.2f} seconds")
        
        # Mostrar informações adicionais
        if "citations" in response_data:
            logger.info(f"Citations: {response_data['citations']}")
        
        return True
        
    except Exception as e:
        logger.error(f"Perplexity test failed: {str(e)}")
        # Se for um erro HTTP, mostrar mais detalhes
        if isinstance(e, requests.exceptions.HTTPError):
            try:
                error_details = e.response.json()
                logger.error(f"API error details: {json.dumps(error_details, indent=2)}")
            except:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response text: {e.response.text}")
        return False

if __name__ == "__main__":
    logger.info("Iniciando teste da API do Perplexity...")
    success = test_perplexity()
    logger.info(f"Teste concluído: {'SUCESSO' if success else 'FALHA'}")