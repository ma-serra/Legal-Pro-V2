"""
Script para testar a transcrição usando o SDK oficial do AssemblyAI.
"""

import os
import sys
import logging
import time
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

def test_transcricao_sdk():
    """
    Testa o processo de transcrição usando o SDK AssemblyAI.
    """
    try:
        # Importar o SDK - verificar se está disponível
        try:
            import assemblyai as aai
            logger.info("SDK do AssemblyAI importado com sucesso")
        except ImportError:
            logger.error("SDK AssemblyAI não está instalado. Execute: pip install assemblyai")
            return False
            
        # Verificar API key
        api_key = os.environ.get("ASSEMBLYAI_API_KEY", "0b7ec13989ab444580f6dfa5c35292cc")
        if not api_key:
            logger.error("API key não encontrada no ambiente (ASSEMBLYAI_API_KEY)")
            return False
        logger.info("Usando API key: " + api_key[:5] + "..." + api_key[-5:])
            
        # Configurar API key
        aai.settings.api_key = api_key
        logger.info("API key configurada com sucesso")
        
        # Definir arquivo de áudio para teste
        audio_path = "./audio_exemplo.mp3"
        if not os.path.exists(audio_path):
            logger.error(f"Arquivo de áudio não encontrado: {audio_path}")
            return False
            
        logger.info(f"Usando arquivo de áudio: {audio_path}")
        
        # Criar configuração - apenas transcrição básica sem recursos avançados
        config = aai.TranscriptionConfig(
            language_code="pt",  # Português
        )
        
        # Iniciar transcrição
        logger.info("Iniciando transcrição...")
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_path, config)
        
        # Verificar resultado
        if transcript.status.value == "error":
            logger.error(f"Erro na transcrição: {transcript.error}")
            return False
            
        logger.info("Transcrição concluída com sucesso!")
        logger.info(f"ID da transcrição: {transcript.id}")
        logger.info(f"Texto: {transcript.text[:150]}...")  # Mostrar primeiros 150 caracteres
        
        return True
        
    except Exception as e:
        logger.exception(f"Erro durante teste: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Iniciando teste de transcrição com SDK...")
    success = test_transcricao_sdk()
    logger.info(f"Resultado final: {'Sucesso' if success else 'Falha'}")
    sys.exit(0 if success else 1)