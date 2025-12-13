#!/usr/bin/env python3
"""
Script para baixar um áudio de exemplo para testar a API AssemblyAI.
"""

import os
import sys
import logging
import requests

# Configurar logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# URL de áudio do exemplo da AssemblyAI
EXEMPLO_URL = "https://storage.googleapis.com/aai-web-samples/5_common_sports_injuries.mp3"
SAIDA_LOCAL = "audio_exemplo.mp3"

def baixar_arquivo(url, local_path):
    """
    Baixa um arquivo de uma URL.
    
    Args:
        url: URL do arquivo
        local_path: Caminho local para salvar o arquivo
    """
    try:
        if os.path.exists(local_path):
            logger.info(f"Arquivo já existe: {local_path}")
            return
        
        logger.info(f"Baixando arquivo de {url} para {local_path}")
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        logger.info(f"Download concluído: {local_path}")
        
    except Exception as e:
        logger.error(f"Erro ao baixar arquivo: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Determinar o caminho completo no diretório atual
    diretorio_atual = os.getcwd()
    caminho_saida = os.path.join(diretorio_atual, SAIDA_LOCAL)
    
    # Baixar o arquivo
    baixar_arquivo(EXEMPLO_URL, caminho_saida)
    
    # Instruções
    print("\nArquivo de áudio de exemplo baixado com sucesso.")
    print(f"Caminho: {caminho_saida}")
    print("\nPara testar a transcrição, execute:")
    print(f"python exemplos/assemblyai_exemplo_completo.py {caminho_saida} --idioma=en --timeout=180\n")