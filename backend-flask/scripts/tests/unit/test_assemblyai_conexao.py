"""
Script para testar a conexão com a API do AssemblyAI.
"""

import os
import logging
import sys
import requests

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_api_connection():
    """
    Testa a conexão com a API do AssemblyAI.
    """
    from multiagent.integrations.assemblyai.client import AssemblyAIClient
    
    # Criar cliente
    cliente = AssemblyAIClient()
    
    # Mostrar informações da API key (parcialmente ofuscada)
    api_key = cliente.api_key
    masked_key = f"{api_key[:5]}...{api_key[-5:]}"
    logger.info(f"Usando API key: {masked_key}")
    
    # Testar requisição simples para a API
    try:
        logger.info("Fazendo solicitação de teste para a API...")
        response = requests.get(
            "https://api.assemblyai.com/v2/transcript/teste",
            headers={"Authorization": cliente.api_key}
        )
        
        logger.info(f"Status da resposta: {response.status_code}")
        logger.info(f"Resposta: {response.text}")
        
        if response.status_code == 401:
            logger.error("Falha na autenticação. Verifique a chave de API.")
            return False
        elif response.status_code == 404:
            # É esperado um 404 para um ID inexistente, mas a API deve responder
            # isso significa que a chave está funcionando
            logger.info("API respondeu corretamente. Conexão funcionando.")
            return True
        else:
            logger.warning(f"Resposta inesperada (código {response.status_code})")
            return True
            
    except Exception as e:
        logger.error(f"Erro ao conectar com a API: {str(e)}")
        return False
        
if __name__ == "__main__":
    result = test_api_connection()
    print(f"Teste de conexão: {'Sucesso' if result else 'Falha'}")
    sys.exit(0 if result else 1)