#!/usr/bin/env python3
"""
Debug do problema de upload - arquivo de 13 minutos sendo processado como 1 segundo
"""

import os
import requests
import time

def debug_upload_issue():
    """Debug completo do problema de upload"""
    
    video_path = "attached_assets/341_VÍDEO4.mp4"
    
    # Verificar arquivo
    if not os.path.exists(video_path):
        print(f"❌ Arquivo não encontrado: {video_path}")
        return
    
    file_size = os.path.getsize(video_path)
    print(f"📁 Arquivo: {video_path}")
    print(f"📊 Tamanho: {file_size} bytes ({file_size/1024/1024:.1f}MB)")
    
    # Verificar chave API
    api_key = os.getenv('ASSEMBLYAI_API_KEY')
    if not api_key:
        print("❌ Chave API não configurada")
        return
    
    print(f"🔑 API Key configurada: {api_key[:10]}...")
    
    # Teste de upload direto
    base_url = "https://api.assemblyai.com"
    headers = {"authorization": api_key}
    
    print("\n🔄 Iniciando upload direto...")
    
    try:
        with open(video_path, "rb") as f:
            # Ler todo o arquivo para verificar se está correto
            file_content = f.read()
            print(f"📖 Bytes lidos do arquivo: {len(file_content)}")
            
            # Resetar ponteiro do arquivo
            f.seek(0)
            
            # Upload
            response = requests.post(
                base_url + "/v2/upload",
                headers=headers,
                data=f,
                timeout=300
            )
            
            print(f"📤 Status do upload: {response.status_code}")
            
            if response.status_code == 200:
                upload_data = response.json()
                upload_url = upload_data["upload_url"]
                print(f"✅ Upload URL: {upload_url}")
                
                # Submeter transcrição
                transcript_data = {
                    "audio_url": upload_url,
                    "speaker_labels": True,
                    "sentiment_analysis": True
                }
                
                print("🎬 Submetendo para transcrição...")
                transcript_response = requests.post(
                    base_url + "/v2/transcript",
                    json=transcript_data,
                    headers=headers
                )
                
                print(f"📝 Status da transcrição: {transcript_response.status_code}")
                
                if transcript_response.status_code == 200:
                    transcript_info = transcript_response.json()
                    transcript_id = transcript_info["id"]
                    print(f"🆔 Transcript ID: {transcript_id}")
                    
                    # Aguardar um pouco e verificar status
                    print("⏳ Aguardando processamento inicial...")
                    time.sleep(10)
                    
                    status_response = requests.get(
                        f"{base_url}/v2/transcript/{transcript_id}",
                        headers=headers
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"📊 Status: {status_data.get('status')}")
                        print(f"🎵 Duração detectada: {status_data.get('audio_duration')}ms")
                        
                        if status_data.get('status') == 'completed':
                            print(f"📝 Texto: {status_data.get('text', '')[:100]}...")
                        
                        return transcript_id
                    else:
                        print(f"❌ Erro ao verificar status: {status_response.text}")
                else:
                    print(f"❌ Erro na transcrição: {transcript_response.text}")
            else:
                print(f"❌ Erro no upload: {response.text}")
                
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 DEBUG DO PROBLEMA DE UPLOAD")
    print("=" * 50)
    debug_upload_issue()