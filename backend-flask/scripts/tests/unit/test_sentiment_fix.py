#!/usr/bin/env python3
"""
Teste específico para verificar se o erro de sentiment_analysis foi corrigido
"""

import os
import assemblyai as aai
from dotenv import load_dotenv

load_dotenv()

def test_sentiment_processing():
    """Testa o processamento de análise de sentimento corrigido"""
    
    api_key = os.getenv('ASSEMBLYAI_API_KEY')
    aai.settings.api_key = api_key
    
    config = aai.TranscriptionConfig(sentiment_analysis=True)
    transcriber = aai.Transcriber(config=config)
    
    # URL de teste
    audio_url = "https://storage.googleapis.com/aai-docs-samples/sports_injuries.mp3"
    
    print("Testando processamento de sentimento...")
    transcript = transcriber.transcribe(audio_url)
    
    # Simular o código do main.py
    results = {'sentiment_analysis': []}
    
    if hasattr(transcript, 'sentiment_analysis') and transcript.sentiment_analysis:
        for result in transcript.sentiment_analysis:
            sentiment_data = {
                'text': result.text,
                'sentiment': result.sentiment.value if hasattr(result.sentiment, 'value') else str(result.sentiment),
                'confidence': result.confidence,
                'start': result.start,
                'end': result.end
            }
            results['sentiment_analysis'].append(sentiment_data)
            print(f"✅ Processado: {sentiment_data['sentiment']} ({sentiment_data['confidence']:.2f})")
    
    print(f"\n📊 Total de segmentos processados: {len(results['sentiment_analysis'])}")
    
    if results['sentiment_analysis']:
        print("✅ Análise de sentimento funcionando corretamente!")
        return True
    else:
        print("❌ Erro no processamento de sentimento")
        return False

if __name__ == "__main__":
    test_sentiment_processing()