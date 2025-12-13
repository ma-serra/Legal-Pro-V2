#!/usr/bin/env python3
"""
Script para demonstrar a análise de sentimento usando a API do AssemblyAI.

Este script:
1. Faz upload de um arquivo de áudio
2. Inicia uma transcrição com análise de sentimento
3. Aguarda o resultado
4. Exibe o resultado com análise de sentimento formatada
"""

import os
import sys
import time
import requests
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constantes
BASE_URL = "https://api.assemblyai.com/v2"
API_KEY = os.environ.get("ASSEMBLYAI_API_KEY") or "0b7ec13989ab444580f6dfa5c35292cc"

def upload_arquivo(arquivo_path):
    """Faz upload de um arquivo de áudio para a API AssemblyAI."""
    logger.info(f"Fazendo upload do arquivo: {arquivo_path}")
    
    headers = {
        "Authorization": API_KEY
    }
    
    with open(arquivo_path, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/upload",
            headers=headers,
            data=f
        )
    
    if response.status_code != 200:
        logger.error(f"Erro no upload: {response.status_code} - {response.text}")
        raise Exception(f"Erro no upload: {response.status_code} - {response.text}")
    
    upload_url = response.json()["upload_url"]
    logger.info(f"Upload concluído com sucesso: {upload_url}")
    return upload_url

def iniciar_transcricao(audio_url, idioma="pt"):
    """Inicia uma transcrição com análise de sentimento."""
    logger.info(f"Iniciando transcrição com análise de sentimento para URL: {audio_url}")
    
    headers = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }
    
    data = {
        "audio_url": audio_url,
        "sentiment_analysis": True,
        "language_code": idioma
    }
    
    url = f"{BASE_URL}/transcript"
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code != 200:
        logger.error(f"Erro ao iniciar transcrição: {response.status_code} - {response.text}")
        raise Exception(f"Erro ao iniciar transcrição: {response.status_code} - {response.text}")
    
    transcript_id = response.json()['id']
    logger.info(f"Transcrição iniciada com ID: {transcript_id}")
    return transcript_id

def aguardar_resultado(transcript_id, max_wait_secs=180):
    """Aguarda a conclusão da transcrição."""
    headers = {
        "Authorization": API_KEY
    }
    
    polling_endpoint = f"{BASE_URL}/transcript/{transcript_id}"
    start_time = time.time()
    
    while True:
        # Verificar timeout
        elapsed = time.time() - start_time
        if elapsed > max_wait_secs:
            logger.warning(f"Atingido tempo limite de {max_wait_secs} segundos")
            return {"status": "timeout", "transcript_id": transcript_id}
        
        # Obter status
        response = requests.get(polling_endpoint, headers=headers)
        if response.status_code != 200:
            logger.error(f"Erro ao verificar status: {response.status_code} - {response.text}")
            time.sleep(5)
            continue
            
        transcription_result = response.json()
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
            time.sleep(5)

def traduzir_sentimento(sentimento):
    """Traduz o sentimento do inglês para português."""
    traducoes = {
        "POSITIVE": "POSITIVO",
        "NEGATIVE": "NEGATIVO",
        "NEUTRAL": "NEUTRO"
    }
    return traducoes.get(sentimento, sentimento)

def cor_sentimento(sentimento):
    """Retorna uma representação de cor para o sentimento."""
    cores = {
        "POSITIVE": "\033[92m",  # Verde
        "NEGATIVE": "\033[91m",  # Vermelho
        "NEUTRAL": "\033[94m",   # Azul
        "RESET": "\033[0m"       # Reset
    }
    return cores.get(sentimento, "") + sentimento + cores.get("RESET", "")

def exibir_resultado(result):
    """Exibe o resultado da transcrição com análise de sentimento."""
    if result.get('status') == 'timeout':
        print("\n" + "="*70)
        print(f"TEMPO LIMITE EXCEDIDO - ID: {result.get('transcript_id')}")
        print("="*70)
        print("\nA transcrição continua em andamento, mas excedeu o tempo de espera.")
        print(f"Você pode verificar o status posteriormente com o ID: {result.get('transcript_id')}")
        return
    
    print("\n" + "="*70)
    print(f"TRANSCRIÇÃO COM ANÁLISE DE SENTIMENTO - ID: {result.get('id')}")
    print("="*70)
    
    # Informações básicas
    print(f"\nIdioma: {result.get('language_code', 'N/A')}")
    print(f"Duração: {result.get('audio_duration', 0):.2f} segundos")
    print(f"Confiança: {result.get('confidence', 0):.2f}")
    
    # Texto completo
    print("\n" + "-"*70)
    print("TEXTO COMPLETO:")
    print("-"*70)
    print(result.get('text', 'Texto não disponível'))
    
    # Análise de sentimento
    sentiment_results = result.get('sentiment_analysis_results', [])
    if sentiment_results:
        print("\n" + "-"*70)
        print("ANÁLISE DE SENTIMENTO:")
        print("-"*70)
        
        # Contagem de sentimentos
        positive_count = sum(1 for item in sentiment_results if item.get('sentiment') == 'POSITIVE')
        negative_count = sum(1 for item in sentiment_results if item.get('sentiment') == 'NEGATIVE')
        neutral_count = sum(1 for item in sentiment_results if item.get('sentiment') == 'NEUTRAL')
        
        total = len(sentiment_results)
        if total > 0:
            print(f"Distribuição de sentimentos:")
            print(f"- Positivo: {positive_count} ({positive_count/total*100:.1f}%)")
            print(f"- Negativo: {negative_count} ({negative_count/total*100:.1f}%)")
            print(f"- Neutro: {neutral_count} ({neutral_count/total*100:.1f}%)")
            
            # Determinar sentimento predominante
            if positive_count > negative_count and positive_count > neutral_count:
                predominante = "POSITIVO"
            elif negative_count > positive_count and negative_count > neutral_count:
                predominante = "NEGATIVO"
            else:
                predominante = "NEUTRO"
                
            print(f"\nSentimento predominante: {predominante}")
        
        print("\nDetalhes da análise de sentimento:")
        for item in sentiment_results:
            sentimento = item.get('sentiment', '')
            texto = item.get('text', '')
            confianca = item.get('confidence', 0)
            
            # Traduzir o sentimento para português
            sentimento_pt = traduzir_sentimento(sentimento)
            
            print(f"[{sentimento_pt} ({confianca:.2f})] {texto}")
    else:
        print("\nNenhum resultado de análise de sentimento disponível.")
    
    print("\n" + "="*70)

def salvar_resultado(result, saida=None):
    """Salva o resultado da transcrição em um arquivo JSON."""
    if not saida:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saida = f"transcricao_sentimento_{timestamp}.json"
    
    import json
    with open(saida, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        
    logger.info(f"Resultado salvo em: {saida}")
    print(f"\nResultado completo salvo em: {saida}")

def main():
    parser = argparse.ArgumentParser(description='Análise de sentimento usando AssemblyAI')
    parser.add_argument('arquivo', help='Caminho para o arquivo de áudio')
    parser.add_argument('--idioma', default='pt', help='Código do idioma (pt, en, es, etc.)')
    parser.add_argument('--timeout', type=int, default=180, help='Tempo máximo de espera em segundos')
    parser.add_argument('--salvar', action='store_true', help='Salvar resultado em arquivo JSON')
    parser.add_argument('--saida', help='Caminho para o arquivo de saída (JSON)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.arquivo):
        print(f"Arquivo não encontrado: {args.arquivo}")
        sys.exit(1)
    
    try:
        # 1. Upload do arquivo
        audio_url = upload_arquivo(args.arquivo)
        
        # 2. Iniciar transcrição com análise de sentimento
        transcript_id = iniciar_transcricao(audio_url, args.idioma)
        
        # 3. Aguardar resultado
        resultado = aguardar_resultado(transcript_id, args.timeout)
        
        # 4. Exibir resultado
        exibir_resultado(resultado)
        
        # 5. Salvar resultado (se solicitado)
        if args.salvar or args.saida:
            salvar_resultado(resultado, args.saida)
            
    except Exception as e:
        logger.error(f"Erro: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()