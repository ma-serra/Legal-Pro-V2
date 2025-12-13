#!/usr/bin/env python3
"""
Teste mínimo da API Multi-Agente sem dependências problemáticas
"""

import os
import sys
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def testar_api_raw():
    """Teste direto usando apenas requests"""
    
    try:
        import requests
        
        url = "http://localhost:5000/api/analise-3-agentes-identica"
        
        payload = {
            "texto": """CONTRATO DE PRESTAÇÃO DE SERVIÇOS DE MARKETING DIGITAL
            
CONTRATANTE: empresa com sede à Rua Porto Alegre/RS
CONTRATADA: MAYMIDIA, CNPJ 47.856.359/0001-29

OBJETO: Prestação de serviços de marketing digital

OBRIGAÇÕES DA CONTRATADA:
- Realizar reuniões presenciais ou virtuais
- Executar serviços com normas legais
- Criar site e blog otimizado para SEO

PREÇO: R$ 12.678,00 (entrada R$ 4.226,00 + duas parcelas R$ 4.226,00)

PRAZO: 1 mês ou até entrega total dos serviços

FORO: Porto Alegre/RS"""
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        logger.info("🚀 Testando API via requests...")
        logger.info(f"URL: {url}")
        logger.info(f"Payload: {len(payload['texto'])} caracteres")
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            resultado = response.json()
            logger.info("✅ API funcionou!")
            logger.info(f"Status: {resultado.get('status')}")
            
            if 'results' in resultado:
                results = resultado['results']
                if 'analise_openai' in results:
                    logger.info(f"OpenAI: {len(results['analise_openai'])} chars")
                if 'analise_gemini' in results:
                    logger.info(f"Gemini: {len(results['analise_gemini'])} chars")
                if 'analise_anthropic' in results:
                    logger.info(f"Anthropic: {len(results['analise_anthropic'])} chars")
                    
            return resultado
        else:
            logger.error(f"❌ Erro HTTP {response.status_code}")
            logger.error(f"Response: {response.text}")
            return {'status': 'erro', 'codigo': response.status_code, 'mensagem': response.text}
            
    except Exception as e:
        logger.error(f"❌ Erro no teste: {e}")
        return {'status': 'erro', 'mensagem': str(e)}

if __name__ == "__main__":
    resultado = testar_api_raw()
    
    if resultado.get('status') == 'sucesso':
        print("🎉 TESTE SUCESSO!")
        print(f"APIs funcionais: {resultado.get('meta', {}).get('apis_funcionais', 0)}")
    else:
        print("❌ TESTE FALHOU!")
        print(f"Erro: {resultado.get('mensagem', 'Desconhecido')}")