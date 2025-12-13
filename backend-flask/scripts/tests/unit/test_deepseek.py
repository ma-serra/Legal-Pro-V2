"""
Teste de integração com a API do Deepseek.
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
# Tentando com o endpoint padrão (mais comum nas APIs)
API_URL = "https://api.deepseek.com/v1/chat/completions"

def test_deepseek():
    """
    Testa a integração com a API do Deepseek usando diretamente requests.
    """
    try:
        # Obter a chave da API
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        
        if not api_key:
            logger.error("DEEPSEEK_API_KEY não está definida nas variáveis de ambiente.")
            return False
        
        # Montar o payload da requisição
        payload = {
            "model": "deepseek-coder",  # Modelo da API Deepseek (versão mais recente)
            "messages": [
                {"role": "system", "content": "Você é um assistente jurídico especializado. Seja breve."},
                {"role": "user", "content": "Me dê 1 ideia de tema para redação sobre direito contratual. Limite a 10 palavras."}
            ],
            "temperature": 0.7,
            "max_tokens": 20  # Reduzido para resposta mais rápida
        }
        
        # Montar os cabeçalhos
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Fazer a requisição com timeout de 5 segundos
        start_time = time.time()
        logger.info("Enviando requisição para a API do Deepseek...")
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=5  # timeout reduzido para 5 segundos
        )
        
        logger.info(f"Resposta recebida em {time.time() - start_time:.2f} segundos")
        logger.info(f"Status code: {response.status_code}")
        
        # Verificar se a requisição foi bem-sucedida
        response.raise_for_status()
        
        # Processar a resposta
        response_data = response.json()
        
        elapsed = time.time() - start_time
        
        # Mostrar os resultados
        logger.info(f"Deepseek response: {response_data['choices'][0]['message']['content']}")
        logger.info(f"Model: {response_data['model']}")
        logger.info(f"Total tokens: {response_data['usage']['total_tokens']}")
        logger.info(f"Elapsed time: {elapsed:.2f} seconds")
        
        return True
        
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout ao conectar com a API do Deepseek: {str(e)}")
        logger.error("A requisição excedeu o limite de tempo de 5 segundos")
        return False
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Erro de conexão com a API do Deepseek: {str(e)}")
        logger.error("Verifique se a URL da API está correta e se há conexão com a internet")
        return False
    except requests.exceptions.HTTPError as e:
        logger.error(f"Erro HTTP ao acessar a API do Deepseek: {str(e)}")
        try:
            error_details = e.response.json()
            logger.error(f"API error details: {json.dumps(error_details, indent=2)}")
        except:
            logger.error(f"Response status: {e.response.status_code}")
            logger.error(f"Response text: {e.response.text}")
        return False
    except ValueError as e:
        logger.error(f"Erro ao processar resposta JSON do Deepseek: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Erro inesperado ao testar API do Deepseek: {str(e)}")
        logger.error(f"Tipo de erro: {type(e).__name__}")
        return False

if __name__ == "__main__":
    logger.info("Iniciando teste da API do Deepseek...")
    success = test_deepseek()
    logger.info(f"Teste concluído: {'SUCESSO' if success else 'FALHA'}")