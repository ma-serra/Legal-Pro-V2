#!/usr/bin/env python3
"""
Teste real da API AssemblyAI para verificar se a integração está funcionando corretamente
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_assemblyai_setup():
    """Testa se a API AssemblyAI está configurada corretamente"""
    
    try:
        import assemblyai as aai
        
        # Verificar se a chave da API está configurada
        api_key = os.getenv('ASSEMBLYAI_API_KEY')
        if not api_key:
            logger.error("❌ ASSEMBLYAI_API_KEY não está configurada nas variáveis de ambiente")
            return False
        
        # Configurar AssemblyAI
        aai.settings.api_key = api_key
        logger.info("✅ Chave API AssemblyAI configurada")
        
        # Testar conexão básica com uma URL de áudio de exemplo
        config = aai.TranscriptionConfig(
            sentiment_analysis=True,
            speaker_labels=True,
            auto_highlights=True,
            summary_model=aai.SummarizationModel.informative,
            summary_type=aai.SummarizationType.bullets
        )
        
        transcriber = aai.Transcriber(config=config)
        logger.info("✅ Transcriber configurado com sucesso")
        
        # URL de áudio de teste público da AssemblyAI
        audio_url = "https://storage.googleapis.com/aai-docs-samples/sports_injuries.mp3"
        
        logger.info("🔄 Iniciando transcrição de teste...")
        transcript = transcriber.transcribe(audio_url)
        
        if transcript.status == aai.TranscriptStatus.error:
            logger.error(f"❌ Erro na transcrição: {transcript.error}")
            return False
        
        logger.info("✅ Transcrição concluída com sucesso!")
        logger.info(f"📊 Confiança: {transcript.confidence}")
        logger.info(f"⏱️ Duração: {transcript.audio_duration}ms")
        logger.info(f"📝 Texto (primeiros 100 chars): {transcript.text[:100]}...")
        
        # Verificar análise de sentimento
        if hasattr(transcript, 'sentiment_analysis_results') and transcript.sentiment_analysis_results:
            logger.info(f"😊 Análise de sentimento: {len(transcript.sentiment_analysis_results)} segmentos")
        
        # Verificar detecção de falantes
        if hasattr(transcript, 'utterances') and transcript.utterances:
            logger.info(f"🗣️ Detecção de falantes: {len(transcript.utterances)} segmentos")
        
        # Verificar resumo
        if hasattr(transcript, 'summary') and transcript.summary:
            logger.info(f"📋 Resumo disponível: {len(transcript.summary)} caracteres")
        
        return True
        
    except ImportError:
        logger.error("❌ Biblioteca AssemblyAI não está instalada")
        return False
    except Exception as e:
        logger.error(f"❌ Erro durante teste: {str(e)}")
        return False

def test_upload_endpoint():
    """Testa se o endpoint de upload está funcionando"""
    
    try:
        import requests
        
        # Testar se o servidor está rodando
        response = requests.get('http://localhost:5000/video/')
        if response.status_code == 200:
            logger.info("✅ Endpoint de transcrição acessível")
            return True
        else:
            logger.error(f"❌ Endpoint retornou status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.error("❌ Servidor não está rodando ou não acessível")
        return False
    except Exception as e:
        logger.error(f"❌ Erro ao testar endpoint: {str(e)}")
        return False

def main():
    """Função principal de teste"""
    
    logger.info("🧪 Iniciando testes da integração AssemblyAI")
    logger.info("=" * 50)
    
    # Teste 1: Verificar configuração da API
    logger.info("1️⃣ Testando configuração da API AssemblyAI...")
    api_test = test_assemblyai_setup()
    
    if not api_test:
        logger.error("❌ Teste da API falhou. Verifique a configuração.")
        sys.exit(1)
    
    logger.info("=" * 50)
    
    # Teste 2: Verificar endpoint do servidor
    logger.info("2️⃣ Testando endpoint do servidor...")
    endpoint_test = test_upload_endpoint()
    
    if not endpoint_test:
        logger.warning("⚠️ Endpoint não acessível. Certifique-se de que o servidor está rodando.")
    
    logger.info("=" * 50)
    
    if api_test and endpoint_test:
        logger.info("🎉 Todos os testes passaram! Sistema pronto para transcrição real.")
    elif api_test:
        logger.info("✅ API AssemblyAI configurada. Inicie o servidor para usar a interface web.")
    else:
        logger.error("❌ Problemas detectados na configuração.")

if __name__ == "__main__":
    main()