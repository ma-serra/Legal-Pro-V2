#!/usr/bin/env python3
"""
Exemplo de uso completo da API do AssemblyAI.

Este script demonstra como utilizar a API do AssemblyAI para:
1. Fazer upload de um arquivo de áudio local
2. Iniciar uma transcrição com resumo em tópicos
3. Aguardar e recuperar os resultados da transcrição
"""

import os
import sys
import time
import logging
import requests
import argparse
from datetime import datetime

# Configurar logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Base URL da API AssemblyAI
BASE_URL = "https://api.assemblyai.com/v2"

def get_api_key():
    """
    Obtém a chave da API do AssemblyAI.
    
    Returns:
        str: Chave da API ou None se não estiver definida
    """
    # Primeiro tenta obter do ambiente
    api_key = os.environ.get('ASSEMBLYAI_API_KEY')
    
    # Se não encontrar, tenta o valor padrão
    if not api_key:
        api_key = "0b7ec13989ab444580f6dfa5c35292cc"
    
    return api_key

def upload_file(file_path, headers):
    """
    Faz upload de um arquivo de áudio para o AssemblyAI.
    
    Args:
        file_path: Caminho para o arquivo local
        headers: Cabeçalhos da requisição
        
    Returns:
        str: URL do arquivo no servidor do AssemblyAI
    """
    logger.info(f"Iniciando upload do arquivo: {file_path}")
    
    try:
        with open(file_path, 'rb') as audio_file:
            response = requests.post(
                f"{BASE_URL}/upload",
                headers=headers,
                data=audio_file
            )
            
        if response.status_code != 200:
            raise Exception(f"Erro no upload: {response.status_code} - {response.text}")
            
        upload_url = response.json()["upload_url"]
        logger.info(f"Upload concluído com sucesso: {upload_url}")
        return upload_url
        
    except Exception as e:
        logger.error(f"Erro durante o upload: {str(e)}")
        raise

def start_transcription(upload_url, headers, options=None):
    """
    Inicia a transcrição de um áudio.
    
    Args:
        upload_url: URL do áudio no servidor do AssemblyAI
        headers: Cabeçalhos da requisição
        options: Opções adicionais para a transcrição
        
    Returns:
        str: ID da transcrição criada
    """
    logger.info(f"Iniciando transcrição para o áudio: {upload_url}")
    
    # Configurações padrão
    data = {
        "audio_url": upload_url,
        "summarization": True,
        "summary_model": "informative",
        "summary_type": "bullets"
    }
    
    # Adicionar opções adicionais, se fornecidas
    if options:
        data.update(options)
    
    try:
        response = requests.post(
            f"{BASE_URL}/transcript",
            json=data,
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Erro ao iniciar transcrição: {response.status_code} - {response.text}")
            
        transcript_id = response.json()['id']
        logger.info(f"Transcrição iniciada com ID: {transcript_id}")
        return transcript_id
        
    except Exception as e:
        logger.error(f"Erro ao iniciar transcrição: {str(e)}")
        raise

def get_transcription_result(transcript_id, headers, max_wait=300):
    """
    Recupera o resultado de uma transcrição, aguardando sua conclusão.
    
    Args:
        transcript_id: ID da transcrição
        headers: Cabeçalhos da requisição
        max_wait: Tempo máximo de espera em segundos
        
    Returns:
        dict: Resultado da transcrição
    """
    logger.info(f"Verificando status da transcrição: {transcript_id}")
    polling_endpoint = f"{BASE_URL}/transcript/{transcript_id}"
    
    start_time = time.time()
    
    while True:
        # Verificar timeout
        elapsed_time = time.time() - start_time
        if elapsed_time > max_wait:
            logger.warning(f"Tempo limite de {max_wait}s excedido para a transcrição {transcript_id}")
            return {
                "warning": "Tempo limite excedido. A transcrição pode continuar em segundo plano.",
                "transcript_id": transcript_id,
                "status": "processing",
                "polling_endpoint": polling_endpoint
            }
        
        try:
            response = requests.get(polling_endpoint, headers=headers)
            
            if response.status_code != 200:
                raise Exception(f"Erro ao verificar status: {response.status_code} - {response.text}")
                
            transcription_result = response.json()
            status = transcription_result['status']
            
            if status == 'completed':
                logger.info(f"Transcrição concluída: {transcript_id}")
                return transcription_result
                
            elif status == 'error':
                error_msg = transcription_result.get('error', 'Erro desconhecido')
                logger.error(f"Erro na transcrição: {error_msg}")
                raise Exception(f"Transcrição falhou: {error_msg}")
                
            else:
                # Ainda em processamento, verificar novamente após intervalo
                elapsed = time.time() - start_time
                logger.info(f"Status atual: {status}. Aguardando... ({int(elapsed)}s)")
                time.sleep(3)
                
        except Exception as e:
            logger.error(f"Erro ao verificar status da transcrição: {str(e)}")
            raise

def display_transcription_result(result):
    """
    Exibe os resultados da transcrição formatados.
    
    Args:
        result: Resultado da transcrição
    """
    print("\n" + "="*80)
    print(f"RESULTADO DA TRANSCRIÇÃO (ID: {result.get('id', 'N/A')})")
    print("="*80)
    
    # Status e informações básicas
    print(f"Status: {result.get('status', 'N/A')}")
    print(f"Duração: {result.get('audio_duration', 0):.2f} segundos")
    print(f"Idioma: {result.get('language_code', 'N/A')}")
    print(f"Criado em: {result.get('created', 'N/A')}")
    
    # Texto completo
    print("\n" + "-"*80)
    print("TEXTO COMPLETO:")
    print("-"*80)
    print(result.get('text', 'Nenhum texto disponível'))
    
    # Resumo em tópicos
    if 'summary' in result or 'summary_bullets' in result:
        print("\n" + "-"*80)
        print("RESUMO:")
        print("-"*80)
        
        if 'summary' in result:
            print(result.get('summary', 'Nenhum resumo disponível'))
        
        if 'summary_bullets' in result:
            print("\nTÓPICOS PRINCIPAIS:")
            for i, bullet in enumerate(result.get('summary_bullets', []), 1):
                print(f"{i}. {bullet}")
    
    # Informações adicionais
    if 'sentiment_analysis_results' in result:
        print("\n" + "-"*80)
        print("ANÁLISE DE SENTIMENTO:")
        print("-"*80)
        for item in result.get('sentiment_analysis_results', []):
            sentiment = item.get('sentiment', '')
            text = item.get('text', '')
            confidence = item.get('confidence', 0)
            print(f"[{sentiment} ({confidence:.2f})] {text}")
    
    # Estatísticas
    print("\n" + "-"*80)
    print("ESTATÍSTICAS:")
    print("-"*80)
    print(f"Palavras: {result.get('words_count', 0)}")
    print(f"Confiança média: {result.get('confidence', 0):.2f}")
    
    print("\n" + "="*80)

def main():
    """
    Função principal que processa o arquivo de áudio.
    """
    parser = argparse.ArgumentParser(description='Demonstração da API AssemblyAI')
    parser.add_argument('arquivo', help='Caminho para o arquivo de áudio a ser transcrito')
    parser.add_argument('--idioma', default='pt', help='Código do idioma (pt, en, es, etc.)')
    parser.add_argument('--falantes', action='store_true', help='Ativar identificação de falantes')
    parser.add_argument('--sentimento', action='store_true', help='Ativar análise de sentimento')
    parser.add_argument('--timeout', type=int, default=120, help='Tempo máximo de espera em segundos')
    
    args = parser.parse_args()
    
    try:
        # Obter a chave da API
        api_key = get_api_key()
        if not api_key:
            logger.error("Chave da API não encontrada. Defina a variável ASSEMBLYAI_API_KEY.")
            sys.exit(1)
            
        # Configurar cabeçalhos
        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
        
        # 1. Fazer upload do arquivo
        upload_url = upload_file(args.arquivo, headers)
        
        # 2. Iniciar transcrição
        options = {
            "language_code": args.idioma,
            "speaker_labels": args.falantes,
            "sentiment_analysis": args.sentimento
        }
        transcript_id = start_transcription(upload_url, headers, options)
        
        # 3. Obter resultado
        result = get_transcription_result(transcript_id, headers, max_wait=args.timeout)
        
        # 4. Exibir resultado
        display_transcription_result(result)
        
    except Exception as e:
        logger.error(f"Erro na execução: {str(e)}")
        sys.exit(1)
        
    logger.info("Processamento concluído com sucesso!")

if __name__ == "__main__":
    main()