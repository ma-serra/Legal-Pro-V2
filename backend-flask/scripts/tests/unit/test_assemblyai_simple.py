#!/usr/bin/env python3
"""
Teste simplificado da integração AssemblyAI com áudio sintético
"""

import os
import json
import logging
from datetime import datetime
import requests
import time

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_simple_test_audio():
    """Cria um arquivo de áudio de teste muito simples"""
    import wave
    import struct
    import math
    
    # Parâmetros do áudio
    sample_rate = 44100
    duration = 5  # 5 segundos
    frequency1 = 440  # Nota A
    frequency2 = 880  # Nota A uma oitava acima
    
    # Gerar dados de áudio
    frames = []
    for i in range(int(sample_rate * duration)):
        # Primeiro tom por 2 segundos
        if i < sample_rate * 2:
            value = int(32767 * math.sin(2 * math.pi * frequency1 * i / sample_rate))
        # Silêncio por 1 segundo
        elif i < sample_rate * 3:
            value = 0
        # Segundo tom por 2 segundos
        else:
            value = int(32767 * math.sin(2 * math.pi * frequency2 * i / sample_rate))
        
        frames.append(struct.pack('<h', value))
    
    # Salvar arquivo WAV
    filename = 'test_audio_simple.wav'
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join(frames))
    
    return filename

def test_assemblyai_api():
    """Testa a API AssemblyAI diretamente"""
    
    api_key = os.environ.get('ASSEMBLYAI_API_KEY')
    if not api_key:
        logger.error("ASSEMBLYAI_API_KEY não encontrada")
        return None
    
    # Criar áudio de teste
    audio_file = create_simple_test_audio()
    logger.info(f"Áudio de teste criado: {audio_file}")
    
    # Upload do arquivo
    logger.info("Fazendo upload para AssemblyAI...")
    
    upload_url = 'https://api.assemblyai.com/v2/upload'
    headers = {'authorization': api_key}
    
    with open(audio_file, 'rb') as f:
        response = requests.post(upload_url, headers=headers, files={'file': f})
    
    if response.status_code != 200:
        logger.error(f"Erro no upload: {response.text}")
        return None
    
    upload_data = response.json()
    audio_url = upload_data['upload_url']
    logger.info("Upload concluído com sucesso")
    
    # Solicitar transcrição
    logger.info("Solicitando transcrição...")
    
    transcript_url = 'https://api.assemblyai.com/v2/transcript'
    transcript_data = {
        'audio_url': audio_url,
        'speaker_labels': True,
        'sentiment_analysis': True,
        'auto_chapters': True,
        'auto_highlights': True,
        'entity_detection': True,
        'language_detection': True
    }
    
    response = requests.post(transcript_url, headers=headers, json=transcript_data)
    
    if response.status_code != 200:
        logger.error(f"Erro na solicitação de transcrição: {response.text}")
        return None
    
    transcript_response = response.json()
    transcript_id = transcript_response['id']
    logger.info(f"Transcrição iniciada com ID: {transcript_id}")
    
    # Aguardar conclusão
    get_url = f'https://api.assemblyai.com/v2/transcript/{transcript_id}'
    
    while True:
        response = requests.get(get_url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Erro ao verificar status: {response.text}")
            return None
        
        data = response.json()
        status = data['status']
        
        if status == 'completed':
            logger.info("Transcrição concluída!")
            break
        elif status == 'error':
            logger.error(f"Erro na transcrição: {data.get('error', 'Erro desconhecido')}")
            return None
        else:
            logger.info(f"Status: {status}... aguardando...")
            time.sleep(2)
    
    # Processar resultados
    results = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'transcript_id': transcript_id,
            'audio_file': audio_file,
            'audio_duration': data.get('audio_duration'),
            'status': status,
            'confidence': data.get('confidence'),
            'language_detected': data.get('language_code')
        },
        'transcription': {
            'text': data.get('text', 'Nenhum texto transcrito'),
            'summary': data.get('summary')
        },
        'speakers': [],
        'sentiment_analysis': [],
        'chapters': [],
        'highlights': [],
        'entities': [],
        'api_response': data  # Resposta completa para debug
    }
    
    # Processar falantes
    if 'utterances' in data and data['utterances']:
        for utterance in data['utterances']:
            results['speakers'].append({
                'speaker': utterance.get('speaker'),
                'text': utterance.get('text'),
                'start': utterance.get('start'),
                'end': utterance.get('end'),
                'confidence': utterance.get('confidence')
            })
    
    # Processar análise de sentimento
    if 'sentiment_analysis_results' in data and data['sentiment_analysis_results']:
        for sentiment in data['sentiment_analysis_results']:
            results['sentiment_analysis'].append({
                'text': sentiment.get('text'),
                'sentiment': sentiment.get('sentiment'),
                'confidence': sentiment.get('confidence'),
                'start': sentiment.get('start'),
                'end': sentiment.get('end')
            })
    
    # Processar capítulos
    if 'chapters' in data and data['chapters']:
        for chapter in data['chapters']:
            results['chapters'].append({
                'gist': chapter.get('gist'),
                'headline': chapter.get('headline'),
                'summary': chapter.get('summary'),
                'start': chapter.get('start'),
                'end': chapter.get('end')
            })
    
    # Processar destaques
    if 'auto_highlights_result' in data and data['auto_highlights_result']:
        highlights = data['auto_highlights_result'].get('results', [])
        for highlight in highlights:
            results['highlights'].append({
                'count': highlight.get('count'),
                'rank': highlight.get('rank'),
                'text': highlight.get('text'),
                'timestamps': highlight.get('timestamps', [])
            })
    
    # Processar entidades
    if 'entities' in data and data['entities']:
        for entity in data['entities']:
            results['entities'].append({
                'entity_type': entity.get('entity_type'),
                'text': entity.get('text'),
                'start': entity.get('start'),
                'end': entity.get('end')
            })
    
    # Gerar análise com OpenAI
    if results['transcription']['text'] and results['transcription']['text'] != 'Nenhum texto transcrito':
        try:
            logger.info("Gerando análise com OpenAI...")
            from modules.multi_api_handler import MultiAPIHandler
            
            multi_api = MultiAPIHandler()
            analysis_prompt = f"""
            Analise o seguinte áudio transcrito e forneça:
            1. Resumo do conteúdo
            2. Principais tópicos identificados
            3. Análise de sentimento geral
            4. Observações técnicas
            
            Transcrição: {results['transcription']['text']}
            Falantes identificados: {len(results['speakers'])}
            """
            
            analysis_result = multi_api.generate_response(
                prompt=analysis_prompt,
                provider='openai',
                temperature=0.3,
                max_tokens=300
            )
            
            if analysis_result['success']:
                results['ai_analysis'] = {
                    'provider': 'OpenAI',
                    'analysis': analysis_result['response']
                }
        except Exception as e:
            logger.warning(f"Erro na análise com OpenAI: {e}")
    
    # Salvar resultados
    output_file = f'resultado_teste_assemblyai_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Limpar arquivo temporário
    try:
        os.remove(audio_file)
    except:
        pass
    
    # Exibir resumo
    print("\n" + "="*60)
    print("TESTE ASSEMBLYAI - RESULTADOS")
    print("="*60)
    print(f"Status: {results['metadata']['status']}")
    print(f"Duração: {results['metadata']['audio_duration']}ms")
    print(f"Confiança: {results['metadata']['confidence']}")
    print(f"Idioma: {results['metadata']['language_detected']}")
    print(f"Texto transcrito: {results['transcription']['text'][:100]}...")
    print(f"Falantes: {len(results['speakers'])}")
    print(f"Segmentos de sentimento: {len(results['sentiment_analysis'])}")
    print(f"Capítulos: {len(results['chapters'])}")
    print(f"Destaques: {len(results['highlights'])}")
    print(f"Entidades: {len(results['entities'])}")
    print(f"\nArquivo salvo: {output_file}")
    print("="*60)
    
    return results

if __name__ == "__main__":
    test_assemblyai_api()