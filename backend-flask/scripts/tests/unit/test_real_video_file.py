#!/usr/bin/env python3
"""
Teste específico com o arquivo de vídeo real enviado pelo usuário
"""

import os
import requests
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_user_video_file():
    """Testa o arquivo de vídeo real do usuário"""
    
    video_path = "attached_assets/341_VÍDEO4.mp4"
    
    if not os.path.exists(video_path):
        logger.error(f"Arquivo não encontrado: {video_path}")
        return False
    
    file_size = os.path.getsize(video_path)
    logger.info(f"Arquivo encontrado: {video_path} ({file_size} bytes)")
    
    # Fazer upload via sistema
    with open(video_path, 'rb') as f:
        files = {'file': f}
        data = {
            'sentiment_analysis': 'on',
            'speaker_detection': 'on'
        }
        
        logger.info("Enviando arquivo real para transcrição...")
        response = requests.post(
            'http://localhost:5000/video/upload', 
            files=files, 
            data=data,
            timeout=60
        )
    
    if response.status_code != 200:
        logger.error(f"Erro no upload: {response.status_code} - {response.text}")
        return False
    
    try:
        upload_result = response.json()
    except:
        logger.error(f"Resposta inválida: {response.text}")
        return False
    
    if not upload_result.get('success'):
        logger.error(f"Upload falhou: {upload_result}")
        return False
    
    transcript_id = upload_result.get('transcript_id')
    logger.info(f"Upload realizado com sucesso, ID: {transcript_id}")
    
    # Monitorar progresso
    max_wait = 300  # 5 minutos para arquivo real
    wait_time = 0
    
    while wait_time < max_wait:
        try:
            response = requests.get(f'http://localhost:5000/video/status/{transcript_id}')
            
            if response.status_code == 200:
                status_data = response.json()
                status = status_data.get('status')
                
                logger.info(f"Status: {status} (aguardando {wait_time}s)")
                
                if status == 'completed':
                    results = status_data.get('results', {})
                    
                    # Verificar se é conteúdo real
                    text = results.get('text', '')
                    confidence = results.get('confidence', 0)
                    duration = results.get('audio_duration', 0)
                    
                    logger.info("=== RESULTADO DA TRANSCRIÇÃO REAL ===")
                    logger.info(f"Texto: {text[:200]}...")
                    logger.info(f"Confiança: {confidence}")
                    logger.info(f"Duração: {duration}ms")
                    
                    # Verificar se não contém dados fake
                    fake_phrases = [
                        "Este áudio contém uma reunião",
                        "resultados trimestrais",
                        "conquistas positivas"
                    ]
                    
                    is_fake = any(phrase in text for phrase in fake_phrases)
                    
                    if is_fake:
                        logger.error("❌ SISTEMA AINDA GERANDO DADOS FAKE")
                        return False
                    else:
                        logger.info("✅ TRANSCRIÇÃO REAL PROCESSADA COM SUCESSO")
                        return True
                
                elif status == 'error':
                    error = status_data.get('error', 'Erro desconhecido')
                    logger.error(f"Erro na transcrição: {error}")
                    return False
            
            else:
                logger.warning(f"Erro ao verificar status: {response.status_code}")
        
        except Exception as e:
            logger.warning(f"Erro na requisição: {e}")
        
        time.sleep(10)
        wait_time += 10
    
    logger.error("Timeout aguardando transcrição")
    return False

if __name__ == "__main__":
    print("🎥 Testando arquivo de vídeo real do usuário")
    print("=" * 50)
    
    if test_user_video_file():
        print("\n✅ SUCESSO: Arquivo real processado corretamente")
    else:
        print("\n❌ FALHA: Problema no processamento do arquivo real")