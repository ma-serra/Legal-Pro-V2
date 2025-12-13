#!/usr/bin/env python3
"""
Limpeza das Collections Qdrant
Remove collections específicas dos agentes, mantém apenas a estrutura universal
"""

import os
import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def limpar_collections_qdrant():
    """Remove collections específicas do Qdrant"""
    
    qdrant_url = os.environ.get('QDRANT_URL')
    qdrant_key = os.environ.get('QDRANT_API_KEY')
    
    if not qdrant_url or not qdrant_key:
        logger.error("Credenciais Qdrant não configuradas")
        return
    
    headers = {
        'api-key': qdrant_key,
        'Content-Type': 'application/json'
    }
    
    try:
        # Listar todas as collections
        response = requests.get(
            f"{qdrant_url}/collections",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            collections = data.get('result', {}).get('collections', [])
            
            logger.info(f"Encontradas {len(collections)} collections")
            
            # Collections para manter (base universal)
            manter = ['juridico_base_universal']
            
            # Remover collections específicas
            removidas = 0
            for collection in collections:
                nome = collection.get('name', '')
                
                if nome not in manter:
                    logger.info(f"Removendo collection: {nome}")
                    
                    delete_response = requests.delete(
                        f"{qdrant_url}/collections/{nome}",
                        headers=headers,
                        timeout=15
                    )
                    
                    if delete_response.status_code in [200, 404]:
                        removidas += 1
                        logger.info(f"✅ Removida: {nome}")
                    else:
                        logger.error(f"❌ Erro ao remover {nome}: {delete_response.text}")
                else:
                    logger.info(f"Mantendo collection: {nome}")
            
            logger.info(f"Limpeza concluída: {removidas} collections removidas")
            
        else:
            logger.error(f"Erro ao listar collections: {response.text}")
            
    except Exception as e:
        logger.error(f"Erro na limpeza: {e}")

def main():
    logger.info("Iniciando limpeza das collections Qdrant")
    limpar_collections_qdrant()

if __name__ == "__main__":
    main()