"""
Conclusão Simples da Transcrição
Usando OpenAI Whisper API para finalizar transcrição interrompida
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def complete_transcription_with_openai():
    """Completar transcrição usando OpenAI Whisper API"""
    
    session_id = "97ba0bfc-af98-449d-bdec-22970b2dfa06"
    
    # Configurar cliente OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    # Encontrar arquivo de áudio
    temp_dir = Path("temp")
    audio_files = list(temp_dir.glob(f"*{session_id}*.wav"))
    
    if not audio_files:
        logger.error("Arquivo de áudio não encontrado")
        return False
    
    # Usar arquivo enhanced se disponível
    audio_file = None
    for file in audio_files:
        if "enhanced" in file.name:
            audio_file = file
            break
    
    if not audio_file:
        audio_file = audio_files[0]
    
    logger.info(f"Transcrevendo arquivo: {audio_file.name}")
    logger.info(f"Tamanho: {audio_file.stat().st_size / 1024 / 1024:.1f} MB")
    
    try:
        # Transcrever usando OpenAI Whisper API
        with open(audio_file, "rb") as audio:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                language="pt"
            )
        
        # Salvar resultado
        timestamp = datetime.now()
        
        # Arquivo JSON
        json_file = f"temp/transcricao_openai_{session_id}.json"
        json_data = {
            "session_id": session_id,
            "arquivo_original": "341_VIDEO4.mp4",
            "arquivo_audio": audio_file.name,
            "timestamp": timestamp.isoformat(),
            "texto_completo": transcript.text,
            "metodo": "openai_whisper_api",
            "modelo": "whisper-1",
            "status": "concluida"
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        # Arquivo de texto limpo
        txt_file = f"temp/transcricao_completa_{session_id}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write("TRANSCRIÇÃO CONCLUÍDA COM OPENAI WHISPER\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Arquivo: 341_VIDEO4.mp4\n")
            f.write(f"Data: {timestamp.strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Modelo: OpenAI Whisper-1\n")
            f.write(f"Idioma: Português\n")
            f.write(f"Caracteres: {len(transcript.text)}\n\n")
            f.write("TEXTO TRANSCRITO:\n")
            f.write("-" * 30 + "\n\n")
            f.write(transcript.text)
        
        logger.info("Transcrição concluída com sucesso!")
        logger.info(f"Arquivo JSON: {json_file}")
        logger.info(f"Arquivo TXT: {txt_file}")
        logger.info(f"Texto extraído: {len(transcript.text)} caracteres")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro na transcrição: {e}")
        return False

if __name__ == "__main__":
    success = complete_transcription_with_openai()
    if success:
        print("Transcrição concluída com OpenAI Whisper!")
    else:
        print("Erro na transcrição")