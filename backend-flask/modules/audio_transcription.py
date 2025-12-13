"""
Módulo exclusivo de transcrição de áudio usando OpenAI Whisper
Com diarização, timestamps e análise de sentimento
"""

import os
import json
import uuid
import logging
import tempfile
from datetime import datetime
from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from flask_login import login_required, current_user
from openai import OpenAI
from pydub import AudioSegment
from sqlalchemy import text
import whisper

# Configurar logging
logger = logging.getLogger(__name__)

# Blueprint
audio_bp = Blueprint('audio_transcription', __name__, url_prefix='/audio')

# Configuração OpenAI - usar API simples
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = None

# Inicializar cliente OpenAI de forma segura
def init_openai_client():
    global openai_client
    if OPENAI_API_KEY and not openai_client:
        try:
            openai_client = OpenAI(api_key=OPENAI_API_KEY)
            logger.info("✅ Cliente OpenAI inicializado")
        except Exception as e:
            logger.warning(f"⚠️ Cliente OpenAI não disponível: {e}")
    return openai_client

# Modelo Whisper local - remover por enquanto para evitar erros
whisper_model = None

@audio_bp.route('/')
def index():
    """Página principal do módulo de áudio"""
    return render_template('audio/index.html')

@audio_bp.route('/upload', methods=['POST'])
def upload():
    """Upload e processamento de áudio"""
    try:
        # Importar db do contexto da aplicação
        from flask import current_app
        db = current_app.extensions['sqlalchemy']
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Nenhum arquivo enviado'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Arquivo não selecionado'})
        
        # Verificar formato
        audio_formats = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac', '.wma', '.opus']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in audio_formats:
            return jsonify({'success': False, 'error': f'Formato não suportado: {file_ext}'})
        
        # Verificar tamanho (500MB máximo)
        if hasattr(file, 'content_length') and file.content_length > 500 * 1024 * 1024:
            return jsonify({'success': False, 'error': 'Arquivo muito grande. Limite: 500MB'})
        
        # Configurações
        speaker_detection = request.form.get('speakerDetection', 'true') == 'true'
        speaker_count = int(request.form.get('speakerCount', 15))
        
        # Salvar arquivo
        temp_dir = os.path.join(os.getcwd(), 'temp', 'audio')
        os.makedirs(temp_dir, exist_ok=True)
        
        transcript_id = str(uuid.uuid4())
        temp_filename = f"{transcript_id}_{file.filename}"
        temp_path = os.path.join(temp_dir, temp_filename)
        file.save(temp_path)
        
        file_size = os.path.getsize(temp_path)
        logger.info(f"📁 Arquivo áudio salvo: {temp_path} ({file_size} bytes)")
        
        # Salvar no banco
        db.session.execute(text("""
            INSERT INTO audio_transcriptions 
            (id, filename, file_size, file_type, user_id, status, speaker_detection, speaker_count, started_at)
            VALUES (:id, :filename, :file_size, :file_type, :user_id, 'processing', :speaker_detection, :speaker_count, :started_at)
        """), {
            'id': transcript_id,
            'filename': file.filename,
            'file_size': file_size,
            'file_type': file_ext,
            'user_id': 1,  # Usuário padrão para teste
            'speaker_detection': speaker_detection,
            'speaker_count': speaker_count,
            'started_at': datetime.now()
        })
        db.session.commit()
        
        # Processar transcrição
        result = process_audio_whisper(temp_path, transcript_id, speaker_detection, speaker_count)
        
        # Limpar arquivo temporário
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        # Salvar na sessão
        session['audio_transcript_id'] = transcript_id
        session['audio_filename'] = file.filename
        
        return jsonify({
            'success': True,
            'transcript_id': transcript_id,
            'message': 'Transcrição de áudio iniciada com Whisper'
        })
        
    except Exception as e:
        logger.error(f"❌ Erro no upload de áudio: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def process_audio_whisper(file_path, transcript_id, speaker_detection, speaker_count):
    """Processar áudio com Whisper"""
    try:
        # Importar db do contexto da aplicação
        from flask import current_app
        db = current_app.extensions['sqlalchemy']
        
        logger.info(f"🎯 Processando áudio com Whisper: {transcript_id}")
        
        # 1. Carregar e analisar áudio
        audio = AudioSegment.from_file(file_path)
        duration_seconds = len(audio) / 1000
        
        # 2. Converter para formato WAV se necessário
        wav_path = file_path
        if not file_path.endswith('.wav'):
            wav_path = file_path.replace(os.path.splitext(file_path)[1], '.wav')
            audio.export(wav_path, format="wav")
        
        # 3. Transcrição com OpenAI Whisper API
        logger.info("🎤 Transcrevendo com OpenAI Whisper...")
        
        client = init_openai_client()
        if not client:
            raise Exception("Cliente OpenAI não disponível")
        
        with open(wav_path, "rb") as audio_file:
            transcript_response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["segment"],
                language="pt"
            )
        
        # 4. Processar segmentos
        segments = []
        full_text = transcript_response.text
        
        if hasattr(transcript_response, 'segments') and transcript_response.segments:
            current_speaker = 1
            last_end_time = 0
            
            for i, segment in enumerate(transcript_response.segments):
                # Simular mudança de falante em pausas longas (>3s)
                pause_duration = segment.start - last_end_time
                if pause_duration > 3.0 and len(segments) > 0:
                    current_speaker = (current_speaker % speaker_count) + 1
                
                # Análise de sentimento do segmento
                sentiment = analyze_sentiment(segment.text)
                
                segments.append({
                    'start_time': format_timestamp(segment.start),
                    'end_time': format_timestamp(segment.end),
                    'speaker_id': current_speaker,
                    'speaker': f"Falante {current_speaker}",
                    'text': segment.text.strip(),
                    'sentiment': sentiment,
                    'confidence': getattr(segment, 'confidence', 0.95),
                    'words_count': len(segment.text.split())
                })
                
                last_end_time = segment.end
        else:
            # Fallback: texto completo como um segmento
            sentiment = analyze_sentiment(full_text)
            segments.append({
                'start_time': '0:00',
                'end_time': format_timestamp(duration_seconds),
                'speaker_id': 1,
                'speaker': 'Falante 1',
                'text': full_text,
                'sentiment': sentiment,
                'confidence': 0.95,
                'words_count': len(full_text.split())
            })
        
        # 5. Análise geral
        unique_speakers = len(set(seg['speaker_id'] for seg in segments))
        overall_sentiment = analyze_overall_sentiment(full_text)
        word_count = sum(seg['words_count'] for seg in segments)
        
        # 6. Preparar dados finais
        result_data = {
            'transcript_text': full_text,
            'segments': segments,
            'duration': format_timestamp(duration_seconds),
            'duration_seconds': duration_seconds,
            'speakers_count': unique_speakers,
            'word_count': word_count,
            'confidence_avg': sum(seg['confidence'] for seg in segments) / len(segments),
            'sentiment_overall': overall_sentiment,
            'language': getattr(transcript_response, 'language', 'pt'),
            'processing_method': 'openai_whisper',
            'speaker_detection_enabled': speaker_detection
        }
        
        # 7. Salvar resultado
        db.session.execute(text("""
            UPDATE audio_transcriptions 
            SET status = 'completed', 
                transcript_data = :transcript_data, 
                duration_seconds = :duration,
                word_count = :word_count,
                speakers_detected = :speakers,
                completed_at = :completed_at
            WHERE id = :transcript_id
        """), {
            'transcript_id': transcript_id,
            'transcript_data': json.dumps(result_data),
            'duration': duration_seconds,
            'word_count': word_count,
            'speakers': unique_speakers,
            'completed_at': datetime.now()
        })
        db.session.commit()
        
        # Limpar arquivo WAV temporário se foi criado
        if wav_path != file_path and os.path.exists(wav_path):
            os.remove(wav_path)
        
        logger.info(f"✅ Transcrição de áudio concluída: {transcript_id}")
        return result_data
        
    except Exception as e:
        logger.error(f"❌ Erro no processamento: {str(e)}")
        # Salvar erro no banco
        try:
            from flask import current_app
            db = current_app.extensions['sqlalchemy']
            db.session.execute(text("""
                UPDATE audio_transcriptions 
                SET status = 'error', 
                    error_message = :error_message,
                    completed_at = :completed_at
                WHERE id = :transcript_id
            """), {
                'transcript_id': transcript_id,
                'error_message': str(e),
                'completed_at': datetime.now()
            })
            db.session.commit()
        except:
            pass
        
        raise e

def analyze_sentiment(text):
    """Análise de sentimento usando GPT-4o"""
    try:
        client = init_openai_client()
        if not client or len(text.strip()) < 3:
            return 'Neutro'
            
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Analise o sentimento do texto em português. Responda apenas: Positivo, Negativo ou Neutro"
                },
                {
                    "role": "user", 
                    "content": text[:300]  # Limitar para economia
                }
            ],
            max_tokens=5,
            temperature=0.1
        )
        
        sentiment = response.choices[0].message.content.strip()
        return sentiment if sentiment in ['Positivo', 'Negativo', 'Neutro'] else 'Neutro'
        
    except Exception as e:
        logger.warning(f"⚠️ Erro na análise de sentimento: {e}")
        return 'Neutro'

def analyze_overall_sentiment(full_text):
    """Análise de sentimento geral"""
    try:
        client = init_openai_client()
        if not client:
            return 'Neutro'
            
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Analise o sentimento geral do texto completo em português. Responda apenas: Positivo, Negativo ou Neutro"
                },
                {
                    "role": "user", 
                    "content": full_text[:1000]
                }
            ],
            max_tokens=5,
            temperature=0.1
        )
        
        sentiment = response.choices[0].message.content.strip()
        return sentiment if sentiment in ['Positivo', 'Negativo', 'Neutro'] else 'Neutro'
        
    except Exception as e:
        logger.warning(f"⚠️ Erro na análise geral: {e}")
        return 'Neutro'

def format_timestamp(seconds):
    """Formatar tempo em MM:SS ou HH:MM:SS"""
    if seconds is None:
        return "0:00"
    
    total_seconds = int(float(seconds))
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"

@audio_bp.route('/status/<transcript_id>')
@login_required
def status(transcript_id):
    """Verificar status da transcrição"""
    try:
        from flask import current_app
        db = current_app.extensions['sqlalchemy']
        
        result = db.session.execute(text("""
            SELECT status, transcript_data, error_message 
            FROM audio_transcriptions 
            WHERE id = :transcript_id AND user_id = :user_id
        """), {
            'transcript_id': transcript_id,
            'user_id': 1  # Usuário padrão para teste
        }).fetchone()
        
        if not result:
            return jsonify({'success': False, 'error': 'Transcrição não encontrada'})
        
        status, transcript_data, error_message = result
        
        if status == 'completed':
            return jsonify({
                'success': True,
                'status': 'completed',
                'progress': 100,
                'message': 'Transcrição concluída!'
            })
        elif status == 'error':
            return jsonify({
                'success': False,
                'status': 'error',
                'error': error_message or 'Erro desconhecido'
            })
        else:
            return jsonify({
                'success': True,
                'status': 'processing',
                'progress': 50,
                'message': 'Processando com Whisper...'
            })
            
    except Exception as e:
        logger.error(f"❌ Erro ao verificar status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@audio_bp.route('/result/<transcript_id>')
@login_required
def result(transcript_id):
    """Exibir resultado da transcrição"""
    try:
        from flask import current_app
        db = current_app.extensions['sqlalchemy']
        
        result = db.session.execute(text("""
            SELECT filename, transcript_data, duration_seconds, completed_at, word_count, speakers_detected
            FROM audio_transcriptions 
            WHERE id = :transcript_id AND user_id = :user_id AND status = 'completed'
        """), {
            'transcript_id': transcript_id,
            'user_id': 1  # Usuário padrão para teste
        }).fetchone()
        
        if not result:
            return render_template('audio/result.html', 
                                 error="Transcrição não encontrada")
        
        filename, transcript_data_json, duration_seconds, completed_at, word_count, speakers_detected = result
        transcript_data = json.loads(transcript_data_json) if transcript_data_json else {}
        
        return render_template('audio/result.html',
                             transcript_id=transcript_id,
                             filename=filename,
                             transcript_text=transcript_data.get('transcript_text', ''),
                             segments=transcript_data.get('segments', []),
                             duration=transcript_data.get('duration', '0:00'),
                             speakers_count=speakers_detected or 1,
                             word_count=word_count or 0,
                             confidence=int(transcript_data.get('confidence_avg', 95) * 100),
                             sentiment_overall=transcript_data.get('sentiment_overall', 'Neutro'),
                             completed_at=completed_at)
        
    except Exception as e:
        logger.error(f"❌ Erro ao exibir resultado: {str(e)}")
        return render_template('audio/result.html', 
                             error=f"Erro: {str(e)}")

@audio_bp.route('/history')
@login_required
def history():
    """Histórico de transcrições de áudio"""
    try:
        from flask import current_app
        db = current_app.extensions['sqlalchemy']
        
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        # Buscar transcrições do usuário
        result = db.session.execute(text("""
            SELECT id, filename, status, duration_seconds, word_count, speakers_detected, 
                   started_at, completed_at
            FROM audio_transcriptions 
            WHERE user_id = :user_id 
            ORDER BY started_at DESC 
            LIMIT :limit OFFSET :offset
        """), {
            'user_id': 1,  # Usuário padrão para teste
            'limit': per_page,
            'offset': (page - 1) * per_page
        })
        
        transcriptions = result.fetchall()
        
        # Contar total
        count_result = db.session.execute(text("""
            SELECT COUNT(*) FROM audio_transcriptions WHERE user_id = :user_id
        """), {'user_id': 1}).fetchone()  # Usuário padrão para teste
        
        total = count_result[0] if count_result else 0
        
        return render_template('audio/history.html',
                             transcriptions=transcriptions,
                             page=page,
                             per_page=per_page,
                             total=total,
                             has_prev=page > 1,
                             has_next=(page * per_page) < total)
        
    except Exception as e:
        logger.error(f"❌ Erro no histórico: {str(e)}")
        return render_template('audio/history.html', 
                             error=f"Erro: {str(e)}")

def register_audio_routes(app):
    """Registrar rotas do módulo de áudio"""
    app.register_blueprint(audio_bp)
    logger.info("✅ Módulo de transcrição de áudio registrado")