#!/usr/bin/env python3
"""
Exemplo simplificado da API AssemblyAI baseado no modelo de código fornecido.

Este script demonstra como utilizar a API do AssemblyAI para:
1. Fazer upload de um arquivo de áudio local
2. Iniciar uma transcrição com resumo em tópicos (bullets)
3. Aguardar pelo resultado da transcrição
4. Exibir o resumo

Baseado diretamente no exemplo:
```python
import requests
import time

base_url = "https://api.assemblyai.com"

headers = {
    "authorization": "0b7ec13989ab444580f6dfa5c35292cc"
}

with open("./my-audio.mp3", "rb") as f:
  response = requests.post(base_url + "/v2/upload",
                          headers=headers,
                          data=f)

upload_url = response.json()["upload_url"]

data = {
    "audio_url": upload_url, # You can also use a URL to an audio or video file on the web
    "summarization": True,
    "summary_model": "informative",
    "summary_type": "bullets"
}

url = base_url + "/v2/transcript"
response = requests.post(url, json=data, headers=headers)

transcript_id = response.json()['id']
polling_endpoint = base_url + "/v2/transcript/" + transcript_id

while True:
  transcription_result = requests.get(polling_endpoint, headers=headers).json()

  if transcription_result['status'] == 'completed':
    print(f"Transcript ID: ", transcript_id)
    print(transcription_result['summary'])
    break

  elif transcription_result['status'] == 'error':
    raise RuntimeError(f"Transcription failed: {transcription_result['error']}")

  else:
    time.sleep(3)
```
"""

import os
import sys
import time
import requests
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constantes
BASE_URL = "https://api.assemblyai.com"
API_KEY = os.environ.get("ASSEMBLYAI_API_KEY") or "0b7ec13989ab444580f6dfa5c35292cc"

def upload_file(file_path):
    """Faz upload de um arquivo para a API AssemblyAI."""
    logger.info(f"Fazendo upload do arquivo: {file_path}")
    
    headers = {
        "Authorization": API_KEY
    }
    
    with open(file_path, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/v2/upload",
            headers=headers,
            data=f
        )
    
    if response.status_code != 200:
        raise Exception(f"Erro no upload: {response.status_code} - {response.text}")
    
    upload_url = response.json()["upload_url"]
    logger.info(f"Upload concluído com sucesso: {upload_url}")
    return upload_url

def transcribe_audio(audio_url):
    """Inicia uma transcrição com resumo em tópicos."""
    logger.info(f"Iniciando transcrição para URL: {audio_url}")
    
    headers = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }
    
    data = {
        "audio_url": audio_url,
        "summarization": True,
        "summary_model": "informative",
        "summary_type": "bullets"
    }
    
    url = f"{BASE_URL}/v2/transcript"
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Erro ao iniciar transcrição: {response.status_code} - {response.text}")
    
    transcript_id = response.json()['id']
    logger.info(f"Transcrição iniciada com ID: {transcript_id}")
    return transcript_id

def wait_for_completion(transcript_id, max_wait_secs=120):
    """Aguarda a conclusão da transcrição."""
    headers = {
        "Authorization": API_KEY
    }
    
    polling_endpoint = f"{BASE_URL}/v2/transcript/{transcript_id}"
    start_time = time.time()
    
    while True:
        # Verificar timeout
        elapsed = time.time() - start_time
        if elapsed > max_wait_secs:
            logger.info(f"Atingido tempo limite de {max_wait_secs} segundos")
            return {"status": "timeout", "transcript_id": transcript_id}
        
        # Obter status
        transcription_result = requests.get(polling_endpoint, headers=headers).json()
        status = transcription_result.get('status')
        
        if status == 'completed':
            logger.info(f"Transcrição concluída em {int(elapsed)} segundos")
            return transcription_result
            
        elif status == 'error':
            error = transcription_result.get('error', 'Erro desconhecido')
            logger.error(f"Transcrição falhou: {error}")
            raise RuntimeError(f"Transcription failed: {error}")
            
        else:
            logger.info(f"Status: {status} - Aguardando... ({int(elapsed)}s)")
            time.sleep(3)

def display_summary(result):
    """Exibe o resumo da transcrição."""
    print("\n" + "="*70)
    print(f"TRANSCRIÇÃO CONCLUÍDA - ID: {result.get('id')}")
    print("="*70)
    
    # Mostrar resumo
    if 'summary' in result:
        print("\nRESUMO:")
        print(result.get('summary', 'Nenhum resumo disponível'))
    
    # Mostrar tópicos
    if 'summary_bullets' in result:
        print("\nPRINCIPAIS TÓPICOS:")
        for i, bullet in enumerate(result.get('summary_bullets', []), 1):
            print(f"{i}. {bullet}")
    
    # Se for timeout
    if result.get('status') == 'timeout':
        print("\nA transcrição continua em andamento, mas excedeu o tempo de espera.")
        print(f"Você pode verificar o status posteriormente com o ID: {result.get('transcript_id')}")
    
    print("\n" + "="*70)

def main():
    # Verificar argumentos
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]} <arquivo_audio>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Arquivo não encontrado: {file_path}")
        sys.exit(1)
    
    try:
        # Etapa 1: Upload do arquivo
        upload_url = upload_file(file_path)
        
        # Etapa 2: Iniciar transcrição
        transcript_id = transcribe_audio(upload_url)
        
        # Etapa 3: Aguardar conclusão
        result = wait_for_completion(transcript_id)
        
        # Etapa 4: Exibir resumo
        display_summary(result)
        
    except Exception as e:
        logger.error(f"Erro: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()