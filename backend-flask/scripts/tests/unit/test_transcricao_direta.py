"""
Script para testar o processo de transcrição completo diretamente.
"""

import os
import logging
import time
import json
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_transcricao_direta():
    """
    Testa o processo de transcrição diretamente com um arquivo de exemplo.
    """
    # Importar as classes necessárias
    from multiagent.integrations.assemblyai.client import AssemblyAIClient
    from multiagent.agentes.transcricao import AgenteTranscricao
    
    # Caminho para o arquivo de exemplo
    audio_path = os.path.join(os.getcwd(), "audio_exemplo.mp3")
    
    if not os.path.exists(audio_path):
        logger.error(f"Arquivo de exemplo não encontrado: {audio_path}")
        return False
        
    logger.info(f"Usando arquivo de áudio: {audio_path}")
    
    # 1. Testar cliente direto
    try:
        cliente = AssemblyAIClient()
        logger.info("Usando cliente AssemblyAI diretamente")
        
        # Fazer upload do arquivo
        logger.info("Fazendo upload do arquivo...")
        upload_url = cliente.upload_file(audio_path)
        logger.info(f"Upload concluído. URL: {upload_url}")
        
        # Iniciar transcrição com tempo de espera maior
        logger.info("Iniciando transcrição...")
        # Removidas todas as opções avançadas (summarization e sentiment_analysis) 
        # pois não estão disponíveis para o idioma português
        transcript_id = cliente.start_transcription(
            audio_url=upload_url,
            language_code="pt",
            summarization=False,
            sentiment_analysis=False,
            speaker_labels=False
        )
        logger.info(f"Transcrição iniciada. ID: {transcript_id}")
        
        # Verificar resultado com tempo de espera maior (3 minutos)
        logger.info("Aguardando resultado (até 3 minutos)...")
        resultado = cliente.wait_for_completion(transcript_id, max_wait_time=180)
        
        # Salvar resultado em arquivo para análise
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"transcricao_resultado_{timestamp}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Resultado salvo em: {output_file}")
        
        # Verificar status final
        status = resultado.get("status", "desconhecido")
        logger.info(f"Status final: {status}")
        
        if status == "completed":
            texto = resultado.get("text", "")
            logger.info(f"Transcrição concluída com sucesso. Texto: {texto[:100]}...")
            return True
        else:
            logger.error(f"Transcrição não concluída. Status: {status}")
            return False
            
    except Exception as e:
        logger.exception(f"Erro durante teste direto: {str(e)}")
        return False
        
if __name__ == "__main__":
    logger.info("Iniciando teste de transcrição direta...")
    result = test_transcricao_direta()
    logger.info(f"Resultado final: {'Sucesso' if result else 'Falha'}")