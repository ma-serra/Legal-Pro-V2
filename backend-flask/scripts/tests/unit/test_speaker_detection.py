#!/usr/bin/env python3
"""
Teste de detecção de falantes com arquivo completo
"""

import os
import requests
import time
import json

def test_speaker_detection():
    """Testa detecção de falantes com o arquivo de 13 minutos"""
    
    video_path = "attached_assets/341_VÍDEO4.mp4"
    api_key = os.getenv('ASSEMBLYAI_API_KEY')
    
    if not api_key:
        print("❌ Chave API não configurada")
        return
    
    base_url = "https://api.assemblyai.com"
    headers = {"authorization": api_key}
    
    print("🔄 Fazendo upload do arquivo...")
    
    with open(video_path, "rb") as f:
        response = requests.post(
            base_url + "/v2/upload",
            headers=headers, 
            data=f,
            timeout=300
        )
    
    if response.status_code != 200:
        print(f"❌ Erro no upload: {response.text}")
        return
    
    upload_url = response.json()["upload_url"]
    print(f"✅ Upload concluído")
    
    # Submeter com detecção de falantes
    transcript_data = {
        "audio_url": upload_url,
        "speaker_labels": True,
        "sentiment_analysis": True,
        "auto_highlights": True,
        "summary_model": "informative",
        "summary_type": "bullets"
    }
    
    print("🎬 Submetendo para transcrição com detecção de falantes...")
    transcript_response = requests.post(
        base_url + "/v2/transcript",
        json=transcript_data,
        headers=headers
    )
    
    if transcript_response.status_code != 200:
        print(f"❌ Erro na transcrição: {transcript_response.text}")
        return
    
    transcript_id = transcript_response.json()["id"]
    print(f"🆔 ID da transcrição: {transcript_id}")
    
    # Aguardar processamento
    print("⏳ Aguardando processamento (pode demorar alguns minutos)...")
    
    while True:
        status_response = requests.get(
            f"{base_url}/v2/transcript/{transcript_id}",
            headers=headers
        )
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            status = status_data.get('status')
            print(f"📊 Status: {status}")
            
            if status == 'completed':
                # Testar via nosso endpoint local
                print("\n🔍 Testando via endpoint local...")
                local_response = requests.get(f"http://localhost:5000/video/status/{transcript_id}")
                
                if local_response.status_code == 200:
                    local_data = local_response.json()
                    results = local_data.get('results', {})
                    
                    duration_ms = results.get('audio_duration', 0)
                    duration_min = duration_ms / 1000 / 60
                    
                    print(f"⏱️  Duração processada: {duration_ms}ms ({duration_min:.1f} minutos)")
                    print(f"📝 Texto (primeiros 200 chars): {results.get('text', '')[:200]}...")
                    print(f"🎭 Segmentos de falantes: {len(results.get('speaker_segments', []))}")
                    print(f"😊 Análises de sentimento: {len(results.get('sentiment_analysis', []))}")
                    
                    # Mostrar alguns segmentos de falantes
                    speaker_segments = results.get('speaker_segments', [])
                    if speaker_segments:
                        print("\n👥 Primeiros segmentos de falantes:")
                        for i, segment in enumerate(speaker_segments[:5]):
                            start_sec = segment['start'] / 1000
                            end_sec = segment['end'] / 1000
                            print(f"   {segment['speaker']}: {segment['text'][:100]}... ({start_sec:.1f}s-{end_sec:.1f}s)")
                    
                    return transcript_id
                else:
                    print(f"❌ Erro no endpoint local: {local_response.text}")
                break
            elif status == 'error':
                print(f"❌ Erro na transcrição: {status_data.get('error', 'Erro desconhecido')}")
                break
        
        time.sleep(10)  # Aguardar 10 segundos antes de verificar novamente

if __name__ == "__main__":
    print("🎯 TESTE DE DETECÇÃO DE FALANTES - ARQUIVO COMPLETO")
    print("=" * 60)
    test_speaker_detection()