#!/usr/bin/env python3
"""
Validação completa do AssemblyAI integrado ao sistema
"""

import os
import json
import requests
import time
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_assemblyai_integration():
    """Valida a integração completa do AssemblyAI"""
    
    api_key = os.environ.get('ASSEMBLYAI_API_KEY')
    if not api_key:
        logger.error("ASSEMBLYAI_API_KEY não encontrada")
        return False
    
    # URL de áudio de exemplo (sample público)
    audio_url = "https://github.com/AssemblyAI-Examples/audio-examples/raw/main/20220101_0000_WCBS880_77.mp3"
    
    logger.info("Iniciando validação do AssemblyAI...")
    
    headers = {'authorization': api_key}
    transcript_url = 'https://api.assemblyai.com/v2/transcript'
    
    # Configuração completa com todas as funcionalidades
    config = {
        'audio_url': audio_url,
        'speaker_labels': True,
        'sentiment_analysis': True,
        'auto_chapters': True,
        'auto_highlights': True,
        'entity_detection': True,
        'language_detection': True,
        'punctuate': True,
        'format_text': True,
        'word_boost': ['legal', 'contract', 'law', 'court'],
        'boost_param': 'high'
    }
    
    # Enviar solicitação
    response = requests.post(transcript_url, headers=headers, json=config)
    
    if response.status_code != 200:
        logger.error(f"Erro na solicitação: {response.text}")
        return False
    
    transcript_data = response.json()
    transcript_id = transcript_data['id']
    logger.info(f"Transcrição iniciada: {transcript_id}")
    
    # Aguardar conclusão
    get_url = f'https://api.assemblyai.com/v2/transcript/{transcript_id}'
    
    for attempt in range(60):  # 5 minutos máximo
        response = requests.get(get_url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Erro ao verificar status: {response.text}")
            return False
        
        data = response.json()
        status = data['status']
        
        if status == 'completed':
            logger.info("Transcrição concluída com sucesso!")
            break
        elif status == 'error':
            logger.error(f"Erro na transcrição: {data.get('error')}")
            return False
        else:
            logger.info(f"Status: {status} (tentativa {attempt+1}/60)")
            time.sleep(5)
    
    if status != 'completed':
        logger.error("Timeout na transcrição")
        return False
    
    # Processar e validar resultados
    validation_report = {
        'test_metadata': {
            'timestamp': datetime.now().isoformat(),
            'transcript_id': transcript_id,
            'audio_source': audio_url,
            'api_key_present': bool(api_key),
            'test_status': 'SUCCESS'
        },
        'transcription_results': {
            'status': data.get('status'),
            'text_length': len(data.get('text', '')),
            'confidence': data.get('confidence'),
            'language_detected': data.get('language_code'),
            'audio_duration_ms': data.get('audio_duration'),
            'full_text': data.get('text', '')[:500] + '...' if len(data.get('text', '')) > 500 else data.get('text', '')
        },
        'features_validation': {
            'basic_transcription': bool(data.get('text')),
            'speaker_identification': bool(data.get('utterances')),
            'sentiment_analysis': bool(data.get('sentiment_analysis_results')),
            'auto_chapters': bool(data.get('chapters')),
            'auto_highlights': bool(data.get('auto_highlights_result')),
            'entity_detection': bool(data.get('entities')),
            'word_timestamps': bool(data.get('words')),
            'language_detection': bool(data.get('language_code'))
        },
        'detailed_results': {}
    }
    
    # Processar falantes
    if data.get('utterances'):
        speakers = []
        unique_speakers = set()
        for utterance in data['utterances']:
            speakers.append({
                'speaker': utterance.get('speaker'),
                'text': utterance.get('text')[:100] + '...' if len(utterance.get('text', '')) > 100 else utterance.get('text'),
                'start_ms': utterance.get('start'),
                'end_ms': utterance.get('end'),
                'confidence': utterance.get('confidence')
            })
            unique_speakers.add(utterance.get('speaker'))
        
        validation_report['detailed_results']['speakers'] = {
            'total_utterances': len(speakers),
            'unique_speakers': list(unique_speakers),
            'sample_utterances': speakers[:5]
        }
    
    # Processar sentimentos
    if data.get('sentiment_analysis_results'):
        sentiments = []
        sentiment_counts = {'POSITIVE': 0, 'NEGATIVE': 0, 'NEUTRAL': 0}
        
        for sentiment in data['sentiment_analysis_results']:
            sentiment_type = sentiment.get('sentiment', 'NEUTRAL')
            sentiment_counts[sentiment_type] = sentiment_counts.get(sentiment_type, 0) + 1
            
            sentiments.append({
                'sentiment': sentiment_type,
                'text': sentiment.get('text')[:100] + '...' if len(sentiment.get('text', '')) > 100 else sentiment.get('text'),
                'confidence': sentiment.get('confidence'),
                'start_ms': sentiment.get('start'),
                'end_ms': sentiment.get('end')
            })
        
        validation_report['detailed_results']['sentiment_analysis'] = {
            'total_segments': len(sentiments),
            'sentiment_distribution': sentiment_counts,
            'sample_segments': sentiments[:5]
        }
    
    # Processar capítulos
    if data.get('chapters'):
        chapters = []
        for chapter in data['chapters']:
            chapters.append({
                'gist': chapter.get('gist'),
                'headline': chapter.get('headline'),
                'summary': chapter.get('summary')[:200] + '...' if len(chapter.get('summary', '')) > 200 else chapter.get('summary'),
                'start_ms': chapter.get('start'),
                'end_ms': chapter.get('end')
            })
        
        validation_report['detailed_results']['chapters'] = {
            'total_chapters': len(chapters),
            'chapters': chapters
        }
    
    # Processar destaques
    if data.get('auto_highlights_result') and data['auto_highlights_result'].get('results'):
        highlights = []
        for highlight in data['auto_highlights_result']['results']:
            highlights.append({
                'text': highlight.get('text'),
                'count': highlight.get('count'),
                'rank': highlight.get('rank'),
                'timestamps_count': len(highlight.get('timestamps', []))
            })
        
        validation_report['detailed_results']['highlights'] = {
            'total_highlights': len(highlights),
            'top_highlights': highlights[:10]
        }
    
    # Processar entidades
    if data.get('entities'):
        entities = []
        entity_types = {}
        
        for entity in data['entities']:
            entity_type = entity.get('entity_type', 'unknown')
            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
            
            entities.append({
                'type': entity_type,
                'text': entity.get('text'),
                'start_ms': entity.get('start'),
                'end_ms': entity.get('end')
            })
        
        validation_report['detailed_results']['entities'] = {
            'total_entities': len(entities),
            'entity_types': entity_types,
            'sample_entities': entities[:10]
        }
    
    # Processar timestamps de palavras
    if data.get('words'):
        words_sample = []
        confidence_scores = []
        
        for word in data['words'][:20]:  # Primeiras 20 palavras
            words_sample.append({
                'text': word.get('text'),
                'start_ms': word.get('start'),
                'end_ms': word.get('end'),
                'confidence': word.get('confidence')
            })
            if word.get('confidence'):
                confidence_scores.append(word.get('confidence'))
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        validation_report['detailed_results']['word_timestamps'] = {
            'total_words': len(data['words']),
            'average_confidence': round(avg_confidence, 3),
            'sample_words': words_sample
        }
    
    # Adicionar análise com sistema multi-API
    try:
        logger.info("Gerando análise complementar com sistema multi-API...")
        from modules.multi_api_handler import MultiAPIHandler
        
        multi_api = MultiAPIHandler()
        
        # Análise de sentimento com nosso sistema
        sentiment_result = multi_api.analyze_sentiment(
            text=data.get('text', '')[:1000],  # Primeiros 1000 caracteres
            provider='openai'
        )
        
        if sentiment_result['success']:
            validation_report['multi_api_analysis'] = {
                'provider': sentiment_result['provider'],
                'sentiment_data': sentiment_result['sentiment_data'],
                'generated_at': datetime.now().isoformat()
            }
        
    except Exception as e:
        logger.warning(f"Erro na análise multi-API: {e}")
        validation_report['multi_api_analysis'] = {
            'error': str(e),
            'status': 'failed'
        }
    
    # Calcular score de validação
    features_tested = len(validation_report['features_validation'])
    features_working = sum(1 for v in validation_report['features_validation'].values() if v)
    validation_score = (features_working / features_tested) * 100
    
    validation_report['validation_summary'] = {
        'total_features_tested': features_tested,
        'features_working': features_working,
        'validation_score_percent': round(validation_score, 1),
        'status': 'PASS' if validation_score >= 75 else 'FAIL',
        'recommendations': []
    }
    
    # Adicionar recomendações
    if not validation_report['features_validation']['speaker_identification']:
        validation_report['validation_summary']['recommendations'].append("Verificar configuração de speaker_labels")
    if not validation_report['features_validation']['sentiment_analysis']:
        validation_report['validation_summary']['recommendations'].append("Verificar configuração de sentiment_analysis")
    if validation_score == 100:
        validation_report['validation_summary']['recommendations'].append("Todas as funcionalidades estão operacionais")
    
    # Salvar relatório
    output_file = f'relatorio_validacao_assemblyai_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(validation_report, f, indent=2, ensure_ascii=False)
    
    # Exibir relatório na tela
    print("\n" + "="*80)
    print("RELATÓRIO DE VALIDAÇÃO - ASSEMBLYAI")
    print("="*80)
    print(f"🎯 SCORE DE VALIDAÇÃO: {validation_score:.1f}%")
    print(f"📊 STATUS: {validation_report['validation_summary']['status']}")
    print(f"⏱️  DURAÇÃO DO ÁUDIO: {validation_report['transcription_results']['audio_duration_ms']}ms")
    print(f"🎯 CONFIANÇA: {validation_report['transcription_results']['confidence']}")
    print(f"🌍 IDIOMA: {validation_report['transcription_results']['language_detected']}")
    
    print(f"\n✅ FUNCIONALIDADES VALIDADAS:")
    for feature, status in validation_report['features_validation'].items():
        icon = "✅" if status else "❌"
        print(f"   {icon} {feature.replace('_', ' ').title()}")
    
    if validation_report['detailed_results'].get('speakers'):
        speakers_info = validation_report['detailed_results']['speakers']
        print(f"\n🎤 FALANTES IDENTIFICADOS: {len(speakers_info['unique_speakers'])}")
        print(f"   Total de segmentos: {speakers_info['total_utterances']}")
    
    if validation_report['detailed_results'].get('sentiment_analysis'):
        sentiment_info = validation_report['detailed_results']['sentiment_analysis']
        dist = sentiment_info['sentiment_distribution']
        print(f"\n😊 ANÁLISE DE SENTIMENTO:")
        print(f"   Positivo: {dist.get('POSITIVE', 0)} segmentos")
        print(f"   Negativo: {dist.get('NEGATIVE', 0)} segmentos")
        print(f"   Neutro: {dist.get('NEUTRAL', 0)} segmentos")
    
    if validation_report['detailed_results'].get('chapters'):
        chapters_info = validation_report['detailed_results']['chapters']
        print(f"\n📖 CAPÍTULOS: {chapters_info['total_chapters']} identificados")
    
    if validation_report['detailed_results'].get('highlights'):
        highlights_info = validation_report['detailed_results']['highlights']
        print(f"\n🔍 DESTAQUES: {highlights_info['total_highlights']} identificados")
    
    if validation_report['detailed_results'].get('entities'):
        entities_info = validation_report['detailed_results']['entities']
        print(f"\n🏷️  ENTIDADES: {entities_info['total_entities']} identificadas")
        print(f"   Tipos: {list(entities_info['entity_types'].keys())}")
    
    if validation_report['detailed_results'].get('word_timestamps'):
        words_info = validation_report['detailed_results']['word_timestamps']
        print(f"\n⏰ TIMESTAMPS: {words_info['total_words']} palavras")
        print(f"   Confiança média: {words_info['average_confidence']}")
    
    print(f"\n📄 TEXTO TRANSCRITO (amostra):")
    print(f"   {validation_report['transcription_results']['full_text']}")
    
    if validation_report.get('multi_api_analysis') and 'error' not in validation_report['multi_api_analysis']:
        multi_analysis = validation_report['multi_api_analysis']['sentiment_data']
        print(f"\n🤖 ANÁLISE MULTI-API:")
        print(f"   Sentimento: {multi_analysis.get('sentiment', 'N/A')}")
        print(f"   Confiança: {multi_analysis.get('confidence', 'N/A')}")
    
    print(f"\n📁 RELATÓRIO SALVO: {output_file}")
    print("="*80)
    
    return validation_score >= 75

if __name__ == "__main__":
    success = validate_assemblyai_integration()
    if success:
        print("\n✅ VALIDAÇÃO CONCLUÍDA COM SUCESSO!")
    else:
        print("\n❌ VALIDAÇÃO FALHOU!")