#!/usr/bin/env python3
"""
Teste completo da integração AssemblyAI
Gera áudio interno e executa todo o pipeline de transcrição
"""

import os
import json
import logging
from datetime import datetime
import assemblyai as aai
from pydub import AudioSegment
from pydub.generators import Sine
import tempfile

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_test_audio():
    """Gera um áudio de teste com múltiplos falantes simulados"""
    
    # Criar segmentos de áudio com diferentes frequências para simular falantes
    segment1 = Sine(400).to_audio_segment(duration=3000)  # Falante 1 - 3 segundos
    silence1 = AudioSegment.silent(duration=500)         # Pausa
    segment2 = Sine(600).to_audio_segment(duration=2500)  # Falante 2 - 2.5 segundos  
    silence2 = AudioSegment.silent(duration=500)         # Pausa
    segment3 = Sine(400).to_audio_segment(duration=2000)  # Falante 1 volta - 2 segundos
    silence3 = AudioSegment.silent(duration=500)         # Pausa
    segment4 = Sine(800).to_audio_segment(duration=2000)  # Falante 3 - 2 segundos
    
    # Combinar todos os segmentos
    combined = segment1 + silence1 + segment2 + silence2 + segment3 + silence3 + segment4
    
    # Salvar como arquivo temporário
    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    combined.export(temp_file.name, format="wav")
    
    return temp_file.name

def test_assemblyai_transcription():
    """Executa teste completo do AssemblyAI"""
    
    try:
        # Configurar AssemblyAI
        api_key = os.environ.get('ASSEMBLYAI_API_KEY')
        if not api_key:
            raise Exception("ASSEMBLYAI_API_KEY não encontrada")
        
        aai.settings.api_key = api_key
        
        # Gerar áudio de teste
        logger.info("Gerando áudio de teste...")
        audio_file = generate_test_audio()
        logger.info(f"Áudio gerado: {audio_file}")
        
        # Configurar transcrição com todas as funcionalidades
        config = aai.TranscriptionConfig(
            speaker_labels=True,           # Identificação de falantes
            auto_chapters=True,            # Capítulos automáticos
            sentiment_analysis=True,       # Análise de sentimento
            auto_highlights=True,          # Destaques automáticos
            entity_detection=True,        # Detecção de entidades
            iab_categories=True,          # Categorização IAB
            language_detection=True,      # Detecção de idioma
            punctuate=True,               # Pontuação automática
            format_text=True              # Formatação de texto
        )
        
        # Iniciar transcrição
        logger.info("Iniciando transcrição com AssemblyAI...")
        transcriber = aai.Transcriber(config=config)
        
        transcript = transcriber.transcribe(audio_file)
        
        # Aguardar conclusão
        if transcript.status == aai.TranscriptStatus.error:
            raise Exception(f"Erro na transcrição: {transcript.error}")
        
        # Processar resultados
        results = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'audio_file': audio_file,
                'duration_ms': transcript.audio_duration,
                'status': str(transcript.status),
                'language_detected': transcript.language_code if hasattr(transcript, 'language_code') else 'unknown'
            },
            'transcription': {
                'full_text': transcript.text,
                'confidence': transcript.confidence if hasattr(transcript, 'confidence') else 0.0
            },
            'speakers': [],
            'timestamps': [],
            'sentiment_analysis': {
                'overall_sentiment': 'neutral',
                'sentiment_segments': []
            },
            'chapters': [],
            'highlights': [],
            'entities': [],
            'categories': []
        }
        
        # Processar identificação de falantes
        if hasattr(transcript, 'utterances') and transcript.utterances:
            logger.info("Processando identificação de falantes...")
            for utterance in transcript.utterances:
                speaker_info = {
                    'speaker': utterance.speaker,
                    'text': utterance.text,
                    'start_time': utterance.start,
                    'end_time': utterance.end,
                    'confidence': utterance.confidence
                }
                results['speakers'].append(speaker_info)
        
        # Processar timestamps de palavras
        if hasattr(transcript, 'words') and transcript.words:
            logger.info("Processando timestamps de palavras...")
            for word in transcript.words[:20]:  # Primeiras 20 palavras
                word_info = {
                    'text': word.text,
                    'start_time': word.start,
                    'end_time': word.end,
                    'confidence': word.confidence
                }
                results['timestamps'].append(word_info)
        
        # Processar análise de sentimento
        if hasattr(transcript, 'sentiment_analysis_results') and transcript.sentiment_analysis_results:
            logger.info("Processando análise de sentimento...")
            for sentiment in transcript.sentiment_analysis_results:
                sentiment_info = {
                    'text': sentiment.text,
                    'sentiment': sentiment.sentiment.value,
                    'confidence': sentiment.confidence,
                    'start_time': sentiment.start,
                    'end_time': sentiment.end
                }
                results['sentiment_analysis']['sentiment_segments'].append(sentiment_info)
        
        # Processar capítulos
        if hasattr(transcript, 'chapters') and transcript.chapters:
            logger.info("Processando capítulos...")
            for chapter in transcript.chapters:
                chapter_info = {
                    'gist': chapter.gist,
                    'headline': chapter.headline,
                    'summary': chapter.summary,
                    'start_time': chapter.start,
                    'end_time': chapter.end
                }
                results['chapters'].append(chapter_info)
        
        # Processar destaques
        if hasattr(transcript, 'auto_highlights_result') and transcript.auto_highlights_result:
            logger.info("Processando destaques...")
            if hasattr(transcript.auto_highlights_result, 'results'):
                for highlight in transcript.auto_highlights_result.results:
                    highlight_info = {
                        'count': highlight.count,
                        'rank': highlight.rank,
                        'text': highlight.text,
                        'timestamps': [{'start': ts.start, 'end': ts.end} for ts in highlight.timestamps]
                    }
                    results['highlights'].append(highlight_info)
        
        # Processar entidades
        if hasattr(transcript, 'entities') and transcript.entities:
            logger.info("Processando entidades...")
            for entity in transcript.entities:
                entity_info = {
                    'entity_type': entity.entity_type.value,
                    'text': entity.text,
                    'start_time': entity.start,
                    'end_time': entity.end
                }
                results['entities'].append(entity_info)
        
        # Processar categorias IAB
        if hasattr(transcript, 'iab_categories_result') and transcript.iab_categories_result:
            logger.info("Processando categorias IAB...")
            if hasattr(transcript.iab_categories_result, 'results'):
                for category in transcript.iab_categories_result.results:
                    category_info = {
                        'text': category.text,
                        'labels': [{'label': label.label, 'relevance': label.relevance} 
                                 for label in category.labels],
                        'timestamp': {
                            'start': category.timestamp.start,
                            'end': category.timestamp.end
                        }
                    }
                    results['categories'].append(category_info)
        
        # Gerar sumarização usando OpenAI
        logger.info("Gerando sumarização...")
        from modules.multi_api_handler import MultiAPIHandler
        
        multi_api = MultiAPIHandler()
        summary_prompt = f"""
        Analise a seguinte transcrição e forneça:
        1. Resumo executivo
        2. Pontos principais
        3. Conclusões
        
        Transcrição: {transcript.text}
        """
        
        summary_result = multi_api.generate_response(
            prompt=summary_prompt,
            provider='openai',
            temperature=0.3,
            max_tokens=500
        )
        
        if summary_result['success']:
            results['summary'] = {
                'generated_by': 'OpenAI',
                'content': summary_result['response']
            }
        
        # Salvar resultados em arquivo
        output_file = f'teste_assemblyai_completo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Teste concluído! Resultados salvos em: {output_file}")
        
        # Limpar arquivo de áudio temporário
        try:
            os.unlink(audio_file)
        except:
            pass
        
        # Exibir resumo dos resultados
        print("\n" + "="*60)
        print("TESTE ASSEMBLYAI - RESUMO DOS RESULTADOS")
        print("="*60)
        print(f"Status: {results['metadata']['status']}")
        print(f"Duração: {results['metadata']['duration_ms']}ms")
        print(f"Falantes identificados: {len(results['speakers'])}")
        print(f"Palavras com timestamp: {len(results['timestamps'])}")
        print(f"Segmentos de sentimento: {len(results['sentiment_analysis']['sentiment_segments'])}")
        print(f"Capítulos: {len(results['chapters'])}")
        print(f"Destaques: {len(results['highlights'])}")
        print(f"Entidades: {len(results['entities'])}")
        print(f"Categorias: {len(results['categories'])}")
        print(f"\nArquivo de resultados: {output_file}")
        print("="*60)
        
        return results
        
    except Exception as e:
        logger.error(f"Erro no teste AssemblyAI: {e}")
        return None

if __name__ == "__main__":
    test_assemblyai_transcription()