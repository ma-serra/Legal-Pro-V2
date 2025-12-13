#!/usr/bin/env python3
"""
Teste para verificar os atributos corretos do objeto Transcript da AssemblyAI
"""

import os
import assemblyai as aai
from dotenv import load_dotenv

load_dotenv()

def test_transcript_attributes():
    """Testa e lista todos os atributos disponíveis no objeto Transcript"""
    
    api_key = os.getenv('ASSEMBLYAI_API_KEY')
    aai.settings.api_key = api_key
    
    # Configurar transcrição com análise de sentimento
    config = aai.TranscriptionConfig(
        sentiment_analysis=True,
        speaker_labels=True
    )
    
    transcriber = aai.Transcriber(config=config)
    
    # URL de teste
    audio_url = "https://storage.googleapis.com/aai-docs-samples/sports_injuries.mp3"
    
    print("Iniciando transcrição para análise de atributos...")
    transcript = transcriber.transcribe(audio_url)
    
    print("\n=== ATRIBUTOS DO OBJETO TRANSCRIPT ===")
    for attr in dir(transcript):
        if not attr.startswith('_'):
            try:
                value = getattr(transcript, attr)
                if callable(value):
                    print(f"{attr}: <método>")
                else:
                    print(f"{attr}: {type(value)} - {value if len(str(value)) < 100 else str(value)[:100]+'...'}")
            except Exception as e:
                print(f"{attr}: Erro ao acessar - {e}")
    
    print("\n=== VERIFICANDO ANÁLISE DE SENTIMENTO ===")
    sentiment_attrs = ['sentiment_analysis', 'sentiment_analysis_results', 'sentiments']
    for attr in sentiment_attrs:
        if hasattr(transcript, attr):
            value = getattr(transcript, attr)
            print(f"✅ {attr}: {type(value)} - {len(value) if hasattr(value, '__len__') else 'N/A'} items")
            if hasattr(value, '__len__') and len(value) > 0:
                print(f"   Primeiro item: {value[0] if hasattr(value, '__getitem__') else 'N/A'}")
        else:
            print(f"❌ {attr}: Não encontrado")

if __name__ == "__main__":
    test_transcript_attributes()