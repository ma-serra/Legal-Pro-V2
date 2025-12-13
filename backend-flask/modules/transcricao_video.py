"""
Módulo de Transcrição de Vídeo com AssemblyAI
Sistema completo com diarização, timestamps, entidades e análise de sentimentos
"""
import os
import json
import time
import requests
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, send_file, current_app
from sqlalchemy import text
import tempfile
from io import BytesIO

# Configurar logging específico para transcrição
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint
transcricao_video = Blueprint('transcricao_video', __name__, url_prefix='/transcricao-video')

# Configuração da AssemblyAI - Corrigida conforme exemplos
ASSEMBLYAI_CONFIG = {
    "api_key": os.environ.get("ASSEMBLYAI_API_KEY"),
    "base_url": "https://api.assemblyai.com",
    "chunk_size": 5 * 1024 * 1024,  # 5MB por chunk
    "max_file_size": 200 * 1024 * 1024,  # 200MB máximo
    "supported_formats": [".mp4", ".mp3", ".wav", ".m4a", ".ogg", ".mov", ".avi", ".wmv", ".aac", ".opus"]
}

class AssemblyAITranscriber:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.assemblyai.com"
        self.headers = {"authorization": api_key}
    
    def upload_file_direct(self, file_path):
        """Upload arquivo direto para AssemblyAI (arquivo completo)"""
        try:
            with open(file_path, "rb") as f:
                response = requests.post(
                    f"{self.base_url}/v2/upload",
                    headers=self.headers,
                    data=f,
                    timeout=300
                )
                response.raise_for_status()
                return response.json()["upload_url"]
        except Exception as e:
            logger.error(f"Erro no upload direto para AssemblyAI: {str(e)}")
            raise e
    
    def submit_transcription(self, audio_url):
        """Submeter transcrição com configurações otimizadas para identificação de falantes em português"""
        data = {
            "audio_url": audio_url,
            "speech_model": "best",       # Modelo 'best' tem melhor identificação de falantes
            "speaker_labels": True,
            "punctuate": True,
            "format_text": True,
            "dual_channel": False,
            "entity_detection": True,
            "language_code": "pt",
            "boost_param": "default",
            "filter_profanity": False,
            "speaker_options": {
                "min_speakers": 1,
                "max_speakers": 15        # Ampliado para capturar todas as vozes
            },
            "multichannel": False,
            "speed_boost": False          # Prioriza qualidade sobre velocidade
        }
        
        response = None
        try:
            response = requests.post(
                f"{self.base_url}/v2/transcript",
                json=data,
                headers=self.headers,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao submeter transcrição: {str(e)}")
            try:
                if response is not None and hasattr(response, 'text'):
                    logger.error(f"Resposta da API: {response.text}")
            except:
                pass
            raise e
    
    def get_transcript_status(self, transcript_id):
        """Verificar status da transcrição"""
        try:
            response = requests.get(
                f"{self.base_url}/v2/transcript/{transcript_id}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao verificar status: {str(e)}")
            raise e

def create_database_tables():
    """Criar tabelas necessárias para o módulo de transcrição"""
    try:
        from main import db
        # Tabela principal de transcrições
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS transcricoes_video (
                id SERIAL PRIMARY KEY,
                filename VARCHAR(255),
                file_size INTEGER,
                file_type VARCHAR(50),
                transcript_id VARCHAR(100),
                status VARCHAR(50),
                text TEXT,
                confidence FLOAT,
                duration INTEGER,
                audio_duration FLOAT,
                speaker_count INTEGER,
                word_count INTEGER,
                utterance_count INTEGER,
                summary TEXT,
                summary_type VARCHAR(50),
                config JSONB,
                audio_url VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                error_message TEXT,
                retry_count INTEGER DEFAULT 0
            )
        """))
        
        # Segmentos por falante
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS speaker_segments (
                id SERIAL PRIMARY KEY,
                transcricao_id INTEGER REFERENCES transcricoes_video(id),
                speaker VARCHAR(50),
                speaker_confidence FLOAT,
                text TEXT,
                start_time INTEGER,
                end_time INTEGER,
                confidence FLOAT,
                words_count INTEGER,
                channel INTEGER
            )
        """))
        
        # Palavras individuais
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS transcript_words (
                id SERIAL PRIMARY KEY,
                transcricao_id INTEGER REFERENCES transcricoes_video(id),
                speaker_segment_id INTEGER REFERENCES speaker_segments(id),
                word VARCHAR(255),
                start_time INTEGER,
                end_time INTEGER,
                confidence FLOAT,
                speaker VARCHAR(50),
                punctuated_word VARCHAR(255)
            )
        """))
        
        # Entidades detectadas
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS entities (
                id SERIAL PRIMARY KEY,
                transcricao_id INTEGER REFERENCES transcricoes_video(id),
                entity_type VARCHAR(100),
                text VARCHAR(255),
                start_time INTEGER,
                end_time INTEGER,
                confidence FLOAT
            )
        """))
        
        # Análise de sentimentos removida conforme solicitado
        
        # Capítulos automáticos
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS auto_chapters (
                id SERIAL PRIMARY KEY,
                transcricao_id INTEGER REFERENCES transcricoes_video(id),
                gist VARCHAR(500),
                headline VARCHAR(255),
                summary TEXT,
                start_time INTEGER,
                end_time INTEGER
            )
        """))
        
        # Destaques automáticos
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS auto_highlights (
                id SERIAL PRIMARY KEY,
                transcricao_id INTEGER REFERENCES transcricoes_video(id),
                text TEXT,
                count INTEGER,
                rank FLOAT,
                timestamps JSONB
            )
        """))
        
        # Categorização IAB
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS iab_categories (
                id SERIAL PRIMARY KEY,
                transcricao_id INTEGER REFERENCES transcricoes_video(id),
                label VARCHAR(255),
                relevance FLOAT,
                timestamp INTEGER
            )
        """))
        
        # Detecção de conteúdo sensível
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS content_safety (
                id SERIAL PRIMARY KEY,
                transcricao_id INTEGER REFERENCES transcricoes_video(id),
                text TEXT,
                label VARCHAR(100),
                confidence FLOAT,
                severity FLOAT,
                start_time INTEGER,
                end_time INTEGER
            )
        """))
        
        db.session.commit()
        logger.info("✅ Tabelas do módulo de transcrição criadas com sucesso")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Erro ao criar tabelas: {str(e)}")
        raise e

def allowed_file(filename):
    """Verificar se o arquivo é de um tipo permitido"""
    return any(filename.lower().endswith(ext) for ext in ASSEMBLYAI_CONFIG["supported_formats"])

def format_timestamp(milliseconds):
    """Converter milissegundos para formato MM:SS"""
    if not milliseconds or milliseconds == 0:
        return "00:00"
    
    # Se já está em segundos (não milissegundos), usar diretamente
    if milliseconds < 10000:  # Provavelmente já em segundos
        seconds = int(milliseconds)
    else:
        seconds = int(milliseconds / 1000)
    
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"

def save_transcription_to_database(transcript_data):
    """Salvar dados completos da transcrição no banco"""
    try:
        from main import db
        # Inserir transcrição principal
        insert_query = text("""
            INSERT INTO transcricoes_video 
            (filename, file_size, file_type, transcript_id, status, text, confidence, 
             duration, audio_duration, speaker_count, word_count, utterance_count,
             summary, summary_type, config, audio_url, started_at, completed_at)
            VALUES (:filename, :file_size, :file_type, :transcript_id, :status, 
                    :text, :confidence, :duration, :audio_duration, :speaker_count, 
                    :word_count, :utterance_count, :summary, :summary_type, 
                    :config, :audio_url, :started_at, :completed_at)
            RETURNING id
        """)
        
        # Preservar dados do arquivo original se não estiverem em transcript_data
        existing_data = {}
        try:
            existing_result = db.session.execute(text("""
                SELECT filename, file_size, file_type FROM transcricoes_video 
                WHERE transcript_id = :transcript_id
            """), {'transcript_id': transcript_data.get('id', '')}).fetchone()
            
            if existing_result:
                existing_data = {
                    'filename': existing_result[0],
                    'file_size': existing_result[1],
                    'file_type': existing_result[2]
                }
        except:
            pass
        
        # Extrair file_type do filename se não estiver definido
        filename = transcript_data.get('filename', existing_data.get('filename', ''))
        file_type = transcript_data.get('file_type', existing_data.get('file_type', ''))
        
        # Se file_type estiver vazio, extrair do filename
        if not file_type and filename and '.' in filename:
            file_type = os.path.splitext(filename)[1].lower()
        
        result = db.session.execute(insert_query, {
            'filename': filename,
            'file_size': transcript_data.get('file_size', existing_data.get('file_size', 0)),
            'file_type': file_type,
            'transcript_id': transcript_data.get('id', ''),
            'status': transcript_data.get('status', 'completed'),
            'text': transcript_data.get('text', ''),
            'confidence': transcript_data.get('confidence', 0.0),
            'duration': transcript_data.get('audio_duration', 0),
            'audio_duration': transcript_data.get('audio_duration', 0.0),
            'speaker_count': len(transcript_data.get('utterances', [])),
            'word_count': len(transcript_data.get('words', [])),
            'utterance_count': len(transcript_data.get('utterances', [])),
            'summary': transcript_data.get('summary', ''),
            'summary_type': 'bullets',
            'config': json.dumps({'assemblyai': 'v2', 'speech_model': 'universal'}),
            'audio_url': transcript_data.get('audio_url', ''),
            'started_at': datetime.now(),
            'completed_at': datetime.now()
        })
        
        transcricao_result = result.fetchone()
        if transcricao_result:
            transcricao_id = transcricao_result[0]
        else:
            raise Exception("Erro ao inserir transcrição no banco")
        
        # Salvar segmentos por falante (validação robusta)
        if 'utterances' in transcript_data and transcript_data['utterances'] is not None:
            utterances = transcript_data['utterances']
            if isinstance(utterances, list):
                for utterance in utterances:
                    if utterance and isinstance(utterance, dict):
                        words = utterance.get('words', [])
                        words_count = len(words) if isinstance(words, list) else 0
                        
                        db.session.execute(text("""
                            INSERT INTO speaker_segments 
                            (transcricao_id, speaker, speaker_confidence, text, start_time, 
                             end_time, confidence, words_count, channel)
                            VALUES (:transcricao_id, :speaker, :speaker_confidence, :text, 
                                    :start_time, :end_time, :confidence, :words_count, :channel)
                        """), {
                            'transcricao_id': transcricao_id,
                            'speaker': utterance.get('speaker', 'Speaker'),
                            'speaker_confidence': utterance.get('confidence', 0.0),
                            'text': utterance.get('text', ''),
                            'start_time': utterance.get('start', 0),
                            'end_time': utterance.get('end', 0),
                            'confidence': utterance.get('confidence', 0.0),
                            'words_count': words_count,
                            'channel': utterance.get('channel', 0)
                        })
        
        # Salvar entidades (validação robusta)
        if 'entities' in transcript_data and transcript_data['entities'] is not None:
            entities = transcript_data['entities']
            if isinstance(entities, list):
                for entity in entities:
                    if entity and isinstance(entity, dict):
                        db.session.execute(text("""
                            INSERT INTO entities 
                            (transcricao_id, entity_type, text, start_time, end_time, confidence)
                            VALUES (:transcricao_id, :entity_type, :text, :start_time, :end_time, :confidence)
                        """), {
                            'transcricao_id': transcricao_id,
                            'entity_type': entity.get('entity_type', ''),
                            'text': entity.get('text', ''),
                            'start_time': entity.get('start', 0),
                            'end_time': entity.get('end', 0),
                            'confidence': entity.get('confidence', 0.0)
                        })
        
        # Análise de sentimentos removida conforme solicitado
        
        # Salvar capítulos automáticos (validação robusta)
        if 'chapters' in transcript_data and transcript_data['chapters'] is not None:
            chapters = transcript_data['chapters']
            if isinstance(chapters, list):
                for chapter in chapters:
                    if chapter and isinstance(chapter, dict):
                        db.session.execute(text("""
                            INSERT INTO auto_chapters 
                            (transcricao_id, gist, headline, summary, start_time, end_time)
                            VALUES (:transcricao_id, :gist, :headline, :summary, :start_time, :end_time)
                        """), {
                            'transcricao_id': transcricao_id,
                            'gist': chapter.get('gist', ''),
                            'headline': chapter.get('headline', ''),
                            'summary': chapter.get('summary', ''),
                            'start_time': chapter.get('start', 0),
                            'end_time': chapter.get('end', 0)
                        })
        
        # Salvar destaques (validação robusta)
        if 'auto_highlights_result' in transcript_data and transcript_data['auto_highlights_result'] is not None:
            highlights = transcript_data['auto_highlights_result']
            if isinstance(highlights, dict) and 'results' in highlights and highlights['results'] is not None:
                results = highlights['results']
                if isinstance(results, list):
                    for highlight in results:
                        if highlight and isinstance(highlight, dict):
                            db.session.execute(text("""
                                INSERT INTO auto_highlights 
                                (transcricao_id, text, count, rank, timestamps)
                                VALUES (:transcricao_id, :text, :count, :rank, :timestamps)
                            """), {
                                'transcricao_id': transcricao_id,
                                'text': highlight.get('text', ''),
                                'count': highlight.get('count', 0),
                                'rank': highlight.get('rank', 0.0),
                                'timestamps': json.dumps(highlight.get('timestamps', []))
                            })
        
        db.session.commit()
        logger.info(f"✅ Transcrição {transcricao_id} salva no banco com sucesso")
        return transcricao_id
        
    except Exception as e:
        try:
            db.session.rollback()
        except:
            pass
        logger.error(f"❌ Erro ao salvar no banco: {str(e)}")
        raise e

# ROTAS DO BLUEPRINT

@transcricao_video.route('/')
def index():
    """Página principal de transcrição"""
    return render_template('transcricao_video/index.html')

@transcricao_video.route('/upload-chunk', methods=['POST'])
def upload_chunk():
    """Receber chunk de arquivo para upload em produção"""
    try:
        chunk = request.files.get('chunk')
        chunk_index = int(request.form.get('chunkIndex', 0))
        total_chunks = int(request.form.get('totalChunks', 1))
        session_id = request.form.get('sessionId')
        filename = request.form.get('filename', 'file')
        
        if not chunk or not session_id:
            return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
        
        # Criar diretório temporário para chunks
        temp_dir = f"temp/chunks/{session_id}"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Salvar chunk
        chunk_path = os.path.join(temp_dir, f"chunk_{chunk_index}")
        chunk.save(chunk_path)
        
        logger.info(f"✅ Chunk {chunk_index + 1}/{total_chunks} salvo: {chunk_path}")
        
        return jsonify({
            'success': True,
            'chunk_index': chunk_index,
            'total_chunks': total_chunks,
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao salvar chunk: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@transcricao_video.route('/finalize-upload', methods=['POST'])
def finalize_upload():
    """Finalizar upload reunindo chunks e processando arquivo"""
    temp_dir = None
    final_path = None
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Dados JSON inválidos'}), 400
            
        session_id = data.get('sessionId')
        filename = data.get('filename', 'file')
        
        if not session_id:
            return jsonify({'success': False, 'error': 'Session ID inválido'}), 400
        
        logger.info(f"🎯 Finalizando upload para sessão: {session_id}")
        
        # Diretório dos chunks
        temp_dir = f"temp/chunks/{session_id}"
        if not os.path.exists(temp_dir):
            logger.error(f"❌ Diretório de chunks não encontrado: {temp_dir}")
            return jsonify({'success': False, 'error': 'Chunks não encontrados'}), 404
        
        # Verificar se há chunks no diretório
        chunk_files = [f for f in os.listdir(temp_dir) if f.startswith('chunk_')]
        if not chunk_files:
            logger.error(f"❌ Nenhum chunk encontrado em: {temp_dir}")
            return jsonify({'success': False, 'error': 'Nenhum chunk encontrado'}), 404
        
        # Reunir chunks em arquivo final
        uploads_dir = "uploads"
        os.makedirs(uploads_dir, exist_ok=True)
        
        final_filename = secure_filename(filename)
        final_path = os.path.join(uploads_dir, final_filename)
        
        # Combinar chunks na ordem correta
        chunk_files_sorted = sorted(chunk_files, key=lambda x: int(x.split('_')[1]))
        
        logger.info(f"📦 Reunindo {len(chunk_files_sorted)} chunks em: {final_path}")
        
        total_size = 0
        with open(final_path, 'wb') as final_file:
            for chunk_file in chunk_files_sorted:
                chunk_path = os.path.join(temp_dir, chunk_file)
                if os.path.exists(chunk_path):
                    with open(chunk_path, 'rb') as chunk:
                        chunk_data = chunk.read()
                        final_file.write(chunk_data)
                        total_size += len(chunk_data)
                    os.remove(chunk_path)  # Limpar chunk
                else:
                    logger.warning(f"⚠️ Chunk não encontrado: {chunk_path}")
        
        # Remover diretório temporário se estiver vazio
        try:
            os.rmdir(temp_dir)
        except OSError:
            logger.warning(f"⚠️ Não foi possível remover diretório: {temp_dir}")
        
        if total_size == 0:
            logger.error("❌ Arquivo final está vazio")
            return jsonify({'success': False, 'error': 'Arquivo reunido está vazio'}), 400
        
        logger.info(f"✅ Arquivo reunido: {final_path} ({total_size} bytes)")
        
        # Processar arquivo reunido usando o sistema existente
        result = process_assembled_file(final_path, final_filename, total_size)
        
        return jsonify({
            'success': True,
            'filename': final_filename,
            'transcript_id': result.get('transcript_id'),
            'file_size': total_size,
            'message': 'Upload em chunks concluído com sucesso'
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao finalizar upload: {str(e)}")
        logger.error(f"❌ Detalhes do erro: {type(e).__name__}")
        
        # Limpar recursos em caso de erro
        if final_path and os.path.exists(final_path):
            try:
                os.remove(final_path)
                logger.info(f"🧹 Arquivo temporário removido: {final_path}")
            except:
                pass
        
        if temp_dir and os.path.exists(temp_dir):
            try:
                # Limpar chunks restantes
                for file in os.listdir(temp_dir):
                    os.remove(os.path.join(temp_dir, file))
                os.rmdir(temp_dir)
                logger.info(f"🧹 Diretório temporário limpo: {temp_dir}")
            except:
                pass
        
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500

def process_assembled_file(file_path, filename, file_size):
    """Processar arquivo reunido dos chunks usando AssemblyAI"""
    try:
        # Importar database dentro da função para evitar problemas de contexto
        try:
            from main import db
        except ImportError:
            logger.error("❌ Erro ao importar db - app não disponível")
            raise Exception("Sistema de banco de dados não disponível")
        
        logger.info(f"🎯 Processando arquivo reunido: {filename} ({file_size} bytes)")
        
        # Verificar se arquivo existe e não está vazio
        if not os.path.exists(file_path):
            raise Exception(f"Arquivo não encontrado: {file_path}")
            
        if file_size == 0:
            raise Exception("Arquivo está vazio")
        
        # Inicializar AssemblyAI
        transcriber = AssemblyAITranscriber(ASSEMBLYAI_CONFIG["api_key"])
        
        # Upload do arquivo reunido para AssemblyAI
        logger.info(f"📤 Enviando arquivo para AssemblyAI: {file_path}")
        audio_url = transcriber.upload_file_direct(file_path)
        logger.info(f"✅ Upload para AssemblyAI concluído: {audio_url}")
        
        # Submeter transcrição
        logger.info("🚀 Submetendo transcrição...")
        transcript_data = transcriber.submit_transcription(audio_url)
        transcript_id = transcript_data['id']
        logger.info(f"✅ Transcrição submetida: {transcript_id}")
        
        # Obter extensão do arquivo
        file_extension = os.path.splitext(filename)[1].lower()
        
        # Salvar informações iniciais no banco
        logger.info(f"💾 Salvando no banco de dados...")
        db.session.execute(text("""
            INSERT INTO transcricoes_video 
            (filename, file_size, file_type, transcript_id, status, config, audio_url, started_at)
            VALUES (:filename, :file_size, :file_type, :transcript_id, 'processing', :config, :audio_url, :started_at)
        """), {
            'filename': filename,
            'file_size': file_size,
            'file_type': file_extension,
            'transcript_id': transcript_id,
            'config': json.dumps({
                'assemblyai': 'v2', 
                'speech_model': 'best',
                'speaker_detection': True,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'upload_method': 'chunks'
            }),
            'audio_url': audio_url,
            'started_at': datetime.now()
        })
        db.session.commit()
        logger.info("✅ Dados salvos no banco")
        
        # Limpar arquivo temporário
        try:
            os.remove(file_path)
            logger.info(f"🧹 Arquivo temporário removido: {file_path}")
        except OSError as e:
            logger.warning(f"⚠️ Não foi possível remover arquivo temporário: {e}")
        
        # Salvar na sessão
        session['transcript_id'] = transcript_id
        session['filename'] = filename
        
        logger.info(f"🎉 Transcrição iniciada com sucesso: {transcript_id}")
        
        return {'transcript_id': transcript_id, 'audio_url': audio_url}
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar arquivo reunido: {str(e)}")
        logger.error(f"❌ Tipo do erro: {type(e).__name__}")
        
        # Tentar limpar arquivo em caso de erro
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"🧹 Arquivo de erro removido: {file_path}")
        except:
            pass
            
        raise e

@transcricao_video.route('/upload', methods=['POST'])
def upload():
    """Upload direto (fallback para arquivos pequenos)"""
    try:
        from main import db
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Nenhum arquivo enviado'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Arquivo não selecionado'})
        
        # Verificar extensão do arquivo
        if file.filename:
            ext = os.path.splitext(file.filename.lower())[1]
            if ext not in ASSEMBLYAI_CONFIG["supported_formats"]:
                return jsonify({'success': False, 'error': f'Formato {ext} não suportado. Use: {", ".join(ASSEMBLYAI_CONFIG["supported_formats"])}'})
        
        # Salvar arquivo temporariamente
        filename = secure_filename(file.filename or 'arquivo')
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, filename)
        file.save(temp_path)
        
        file_size = os.path.getsize(temp_path)
        if file_size > ASSEMBLYAI_CONFIG["max_file_size"]:
            os.remove(temp_path)
            return jsonify({'success': False, 'error': f'Arquivo muito grande (máximo {ASSEMBLYAI_CONFIG["max_file_size"] // (1024*1024)}MB)'})
        
        # Inicializar AssemblyAI
        transcriber = AssemblyAITranscriber(ASSEMBLYAI_CONFIG["api_key"])
        
        # Upload do arquivo
        audio_url = transcriber.upload_file_direct(temp_path)
        
        # Submeter transcrição (configuração feita dentro da função)
        transcript_data = transcriber.submit_transcription(audio_url)
        transcript_id = transcript_data['id']
        
        # Obter extensão do arquivo
        file_extension = os.path.splitext(filename)[1]
        
        # Salvar informações iniciais no banco com dados corretos
        db.session.execute(text("""
            INSERT INTO transcricoes_video 
            (filename, file_size, file_type, transcript_id, status, config, audio_url, started_at)
            VALUES (:filename, :file_size, :file_type, :transcript_id, 'processing', :config, :audio_url, :started_at)
        """), {
            'filename': filename,
            'file_size': file_size,  # Tamanho real do arquivo
            'file_type': file_extension,  # Extensão com ponto (.mp4)
            'transcript_id': transcript_id,
            'config': json.dumps({
                'assemblyai': 'v2', 
                'speech_model': 'best',
                'speaker_detection': True,
                'file_size_mb': round(file_size / (1024 * 1024), 2)
            }),
            'audio_url': audio_url,
            'started_at': datetime.now()
        })
        db.session.commit()
        
        # Limpar arquivo temporário
        os.remove(temp_path)
        os.rmdir(temp_dir)
        
        # Salvar na sessão
        session['transcript_id'] = transcript_id
        session['filename'] = filename
        
        return jsonify({
            'success': True,
            'transcript_id': transcript_id,
            'message': 'Upload realizado com sucesso. Processando...'
        })
        
    except Exception as e:
        logger.error(f"Erro no upload: {str(e)}")
        # Limpeza em caso de erro
        try:
            if 'temp_path' in locals() and temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            if 'temp_dir' in locals() and temp_dir and os.path.exists(temp_dir):
                os.rmdir(temp_dir)
        except:
            pass
        return jsonify({'success': False, 'error': str(e)})

@transcricao_video.route('/status/<transcript_id>')
def status(transcript_id):
    """Verificar status da transcrição"""
    try:
        from main import db
        transcriber = AssemblyAITranscriber(ASSEMBLYAI_CONFIG["api_key"])
        result = transcriber.get_transcript_status(transcript_id)
        
        # Atualizar status no banco
        if result['status'] in ['completed', 'error']:
            if result['status'] == 'completed':
                # Buscar dados completos da API para salvar
                transcriber_full = AssemblyAITranscriber(ASSEMBLYAI_CONFIG["api_key"])
                full_data = transcriber_full.get_transcript_status(transcript_id)
                
                # Buscar dados originais do banco antes de deletar
                original_data = db.session.execute(text("""
                    SELECT filename, file_size, file_type FROM transcricoes_video 
                    WHERE transcript_id = :transcript_id
                """), {'transcript_id': transcript_id}).fetchone()
                
                # Adicionar dados de contexto preservando informações originais
                if original_data:
                    full_data['filename'] = original_data[0] or session.get('filename', '')
                    full_data['file_size'] = original_data[1] or 0  # Preservar file_size original
                    full_data['file_type'] = original_data[2] or ''
                else:
                    full_data['filename'] = session.get('filename', '')
                    full_data['file_size'] = 0
                    full_data['file_type'] = ''
                
                # Remover registro existente se houver (para substituir por dados reais)
                db.session.execute(text("""
                    DELETE FROM transcricoes_video WHERE transcript_id = :transcript_id
                """), {'transcript_id': transcript_id})
                
                # Salvar dados reais completos
                save_transcription_to_database(full_data)
                db.session.commit()
            else:
                # Para outros status, apenas atualizar
                db.session.execute(text("""
                    UPDATE transcricoes_video 
                    SET status = :status, processed_at = :processed_at, error_message = :error
                    WHERE transcript_id = :transcript_id
                """), {
                    'status': result['status'],
                    'processed_at': datetime.now(),
                    'error': result.get('error', ''),
                    'transcript_id': transcript_id
                })
                db.session.commit()
        
        return jsonify({
            'success': True,
            'status': result['status'],
            'progress': 100 if result['status'] == 'completed' else 50 if result['status'] == 'processing' else 0,
            'confidence': result.get('confidence', 0),
            'message': 'Processamento concluído' if result['status'] == 'completed' else 'Processando...'
        })
        
    except Exception as e:
        logger.error(f"Erro ao verificar status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

# Removida a rota /reprocess - não mais necessária

@transcricao_video.route('/result/<transcript_id>')
def result(transcript_id):
    """Visualizar resultado da transcrição"""
    try:
        from main import db
        # Buscar dados do banco
        query = text("""
            SELECT t.id, t.filename, t.file_size, t.file_type, t.transcript_id, t.status, 
                   t.text, t.confidence, t.duration, t.audio_duration, t.speaker_count, 
                   t.word_count, t.utterance_count, t.summary, t.summary_type, t.config, 
                   t.audio_url, t.created_at, t.processed_at, t.started_at, t.completed_at, 
                   t.error_message, t.retry_count,
                   COUNT(DISTINCT s.id) as segment_count,
                   COUNT(DISTINCT e.id) as entity_count
            FROM transcricoes_video t
            LEFT JOIN speaker_segments s ON t.id = s.transcricao_id
            LEFT JOIN entities e ON t.id = e.transcricao_id
            WHERE t.transcript_id = :transcript_id
            GROUP BY t.id, t.filename, t.file_size, t.file_type, t.transcript_id, t.status, 
                     t.text, t.confidence, t.duration, t.audio_duration, t.speaker_count, 
                     t.word_count, t.utterance_count, t.summary, t.summary_type, t.config, 
                     t.audio_url, t.created_at, t.processed_at, t.started_at, t.completed_at, 
                     t.error_message, t.retry_count
        """)
        result = db.session.execute(query, {'transcript_id': transcript_id}).fetchone()
        
        if not result:
            return redirect(url_for('transcricao_video.index'))
        
        # Buscar segmentos
        segments = db.session.execute(text("""
            SELECT * FROM speaker_segments 
            WHERE transcricao_id = :transcricao_id 
            ORDER BY start_time
        """), {'transcricao_id': result.id}).fetchall()
        
        # Buscar entidades
        entities = db.session.execute(text("""
            SELECT * FROM entities 
            WHERE transcricao_id = :transcricao_id 
            ORDER BY start_time
        """), {'transcricao_id': result.id}).fetchall()
        
        # Buscar capítulos
        chapters = db.session.execute(text("""
            SELECT * FROM auto_chapters 
            WHERE transcricao_id = :transcricao_id 
            ORDER BY start_time
        """), {'transcricao_id': result.id}).fetchall()
        
        # Buscar destaques
        highlights = db.session.execute(text("""
            SELECT * FROM auto_highlights 
            WHERE transcricao_id = :transcricao_id 
            ORDER BY rank DESC
        """), {'transcricao_id': result.id}).fetchall()
        
        # Calcular número de palavras do texto
        word_count = len(result.text.split()) if result.text else 0
        
        # Consolidação inteligente de falantes - análise de timbre e sequência lógica
        def consolidate_speakers_advanced(segments):
            """Consolidar falantes usando análise de timbre, padrões e sequência pergunta-resposta"""
            import re
            
            speaker_stats = {}
            
            # Primeira passada: analisar características básicas
            for idx, s in enumerate(segments):
                if not s.speaker or not s.speaker.strip():
                    continue
                    
                speaker = s.speaker.strip()
                if speaker not in speaker_stats:
                    speaker_stats[speaker] = {
                        'segments': [],
                        'total_time': 0,
                        'avg_confidence': 0,
                        'word_patterns': set(),
                        'question_count': 0,
                        'answer_count': 0,
                        'speech_patterns': [],
                        'temporal_distribution': [],
                        'avg_segment_length': 0
                    }
                
                segment_duration = (s.end_time - s.start_time) if s.end_time and s.start_time else 0
                speaker_stats[speaker]['segments'].append((idx, s))
                speaker_stats[speaker]['total_time'] += segment_duration
                speaker_stats[speaker]['temporal_distribution'].append(s.start_time)
                
                if s.text:
                    text = s.text.lower().strip()
                    words = text.split()
                    speaker_stats[speaker]['word_patterns'].update(words[:8])
                    
                    # Detectar perguntas e respostas
                    if any(marker in text for marker in ['?', 'você', 'tu', 'qual', 'como', 'quando', 'onde', 'por que', 'quem']):
                        speaker_stats[speaker]['question_count'] += 1
                    
                    # Detectar padrões de resposta
                    if any(marker in text for marker in ['sim', 'não', 'é', 'foi', 'então', 'bom', 'certo', 'ok']):
                        speaker_stats[speaker]['answer_count'] += 1
                    
                    # Analisar padrões de fala (comprimento médio das sentenças)
                    speaker_stats[speaker]['speech_patterns'].append(len(words))
            
            # Calcular métricas avançadas
            for speaker, stats in speaker_stats.items():
                if stats['segments']:
                    stats['avg_confidence'] = sum(seg[1].confidence for seg in stats['segments']) / len(stats['segments'])
                    stats['avg_segment_length'] = sum(stats['speech_patterns']) / len(stats['speech_patterns']) if stats['speech_patterns'] else 0
                    stats['question_ratio'] = stats['question_count'] / len(stats['segments']) if stats['segments'] else 0
                    stats['answer_ratio'] = stats['answer_count'] / len(stats['segments']) if stats['segments'] else 0
            
            # Identificar falantes significativos com critérios mais rigorosos
            significant_speakers = {}
            for speaker, stats in speaker_stats.items():
                segment_count = len(stats['segments'])
                
                # Critérios múltiplos para falante significativo
                is_significant = (
                    segment_count >= 3 or  # Pelo menos 3 segmentos
                    stats['total_time'] > 20000 or  # Mais de 20 segundos
                    (stats['question_count'] + stats['answer_count']) >= 2  # Pelo menos 2 interações
                )
                
                if is_significant:
                    significant_speakers[speaker] = stats
            
            # Análise de contexto conversacional - detectar pergunta-resposta
            def analyze_conversational_context(segments):
                """Analisa sequências pergunta-resposta para identificar falantes"""
                question_response_pairs = []
                
                for i in range(len(segments) - 1):
                    current = segments[i]
                    next_segment = segments[i + 1]
                    
                    if not current.text or not next_segment.text:
                        continue
                    
                    current_text = current.text.lower().strip()
                    next_text = next_segment.text.lower().strip()
                    
                    # Detectar perguntas diretas
                    is_question = (
                        '?' in current_text or
                        any(marker in current_text for marker in [
                            'tu me diz', 'você me diz', 'qual', 'como', 'quando', 
                            'onde', 'por que', 'quem', 'me fala', 'me conta'
                        ])
                    )
                    
                    # Detectar respostas diretas
                    is_response = (
                        # Resposta com nome próprio após pergunta de identificação
                        ('nome' in current_text and any(word.istitle() for word in next_text.split())) or
                        # Confirmações simples
                        next_text in ['sim', 'não', 'é', 'foi', 'certo', 'ok'] or
                        # Resposta após "tu me diz"
                        ('tu me diz' in current_text and len(next_text.split()) <= 5)
                    )
                    
                    if is_question and is_response:
                        # Gap temporal pequeno indica diálogo direto
                        time_gap = next_segment.start_time - current.end_time if current.end_time and next_segment.start_time else float('inf')
                        
                        if time_gap < 5000:  # Menos de 5 segundos
                            question_response_pairs.append({
                                'question_speaker': current.speaker,
                                'response_speaker': next_segment.speaker,
                                'question_text': current_text,
                                'response_text': next_text,
                                'confidence': 0.9  # Alta confiança para pares pergunta-resposta
                            })
                
                return question_response_pairs
            
            # Análise de similaridade avançada com contexto conversacional
            def calculate_speaker_similarity(stats1, stats2, conversational_pairs):
                # 1. Similaridade de vocabulário
                common_words = stats1['word_patterns'].intersection(stats2['word_patterns'])
                vocab_similarity = len(common_words) / max(len(stats1['word_patterns']), len(stats2['word_patterns']), 1)
                
                # 2. Similaridade de padrões de fala
                avg_len_diff = abs(stats1['avg_segment_length'] - stats2['avg_segment_length'])
                length_similarity = max(0, 1 - (avg_len_diff / 20))  # Normalizar por 20 palavras
                
                # 3. Análise de papéis (quem pergunta vs quem responde)
                role_diff = abs(stats1['question_ratio'] - stats2['question_ratio'])
                role_similarity = max(0, 1 - (role_diff * 2))
                
                # 4. Distribuição temporal (evitar consolidar falantes que falam simultaneamente)
                times1 = set(stats1['temporal_distribution'])
                times2 = set(stats2['temporal_distribution'])
                temporal_overlap = len(times1.intersection(times2)) / max(len(times1), len(times2), 1)
                temporal_similarity = 1 - temporal_overlap  # Menos overlap = mais similar (mesmo falante)
                
                # 5. NOVA: Análise conversacional - penalizar se são pergunta-resposta
                conversational_penalty = 0
                speaker1_names = [seg[0] for seg in stats1['segments'] if seg[1].speaker]
                speaker2_names = [seg[0] for seg in stats2['segments'] if seg[1].speaker]
                
                if speaker1_names and speaker2_names:
                    speaker1_name = segments[speaker1_names[0]].speaker if speaker1_names else None
                    speaker2_name = segments[speaker2_names[0]].speaker if speaker2_names else None
                    
                    # Verificar se estes falantes aparecem em pares pergunta-resposta
                    for pair in conversational_pairs:
                        if ((pair['question_speaker'] == speaker1_name and pair['response_speaker'] == speaker2_name) or
                            (pair['question_speaker'] == speaker2_name and pair['response_speaker'] == speaker1_name)):
                            conversational_penalty = 0.8  # Grande penalidade - são pessoas diferentes
                            break
                
                # Peso combinado das métricas
                base_similarity = (
                    vocab_similarity * 0.3 +      # 30% vocabulário
                    length_similarity * 0.2 +     # 20% padrão de fala
                    role_similarity * 0.2 +       # 20% papel na conversa
                    temporal_similarity * 0.3     # 30% distribuição temporal
                )
                
                # Aplicar penalidade conversacional
                final_similarity = base_similarity * (1 - conversational_penalty)
                
                return final_similarity
            
            # Analisar contexto conversacional primeiro
            conversational_pairs = analyze_conversational_context(segments)
            
            # Consolidação baseada em similaridade multifatorial com contexto
            consolidated = {}
            speaker_mapping = {}
            next_speaker_num = 1
            
            for speaker, stats in significant_speakers.items():
                merged = False
                best_match = None
                best_similarity = 0
                
                # Encontrar o melhor match entre falantes já consolidados
                for existing_speaker, existing_stats in consolidated.items():
                    similarity = calculate_speaker_similarity(stats, existing_stats, conversational_pairs)
                    
                    # Threshold ajustado (70%) considerando contexto conversacional
                    if similarity > 0.70 and similarity > best_similarity:
                        best_match = existing_speaker
                        best_similarity = similarity
                
                if best_match:
                    # Consolidar com o melhor match
                    consolidated[best_match]['segments'].extend(stats['segments'])
                    consolidated[best_match]['total_time'] += stats['total_time']
                    consolidated[best_match]['word_patterns'].update(stats['word_patterns'])
                    speaker_mapping[speaker] = best_match
                    merged = True
                
                if not merged:
                    # Criar novo falante
                    new_name = f"Falante {next_speaker_num}"
                    consolidated[new_name] = stats
                    speaker_mapping[speaker] = new_name
                    next_speaker_num += 1
            
            return len(consolidated), speaker_mapping
        
        # Aplicar consolidação avançada
        speaker_count, speaker_mapping = consolidate_speakers_advanced(segments)
        
        # Atualizar segmentos com nomes consolidados (criar novos objetos)
        updated_segments = []
        for segment in segments:
            # Criar um dicionário com os dados do segmento
            segment_dict = dict(segment._mapping) if hasattr(segment, '_mapping') else dict(segment)
            
            # Atualizar o speaker se necessário
            if segment.speaker in speaker_mapping:
                segment_dict['speaker'] = speaker_mapping[segment.speaker]
            
            # Criar objeto com os dados atualizados
            updated_segments.append(type('obj', (object,), segment_dict))
        
        segments = updated_segments
        
        # Adicionar dados calculados ao resultado
        transcricao_data = dict(result._mapping)
        transcricao_data['word_count'] = word_count
        transcricao_data['speaker_count'] = speaker_count
        transcricao_data['segment_count'] = len(segments)
        
        # Função para traduzir tipos de entidades
        def translate_entity_type(entity_type):
            translations = {
                'person': 'Pessoas',
                'person_name': 'Nomes de Pessoas',
                'location': 'Locais',
                'location_name': 'Nomes de Locais',
                'organization': 'Organizações',
                'organization_name': 'Nomes de Organizações',
                'date': 'Datas',
                'time': 'Horários',
                'duration': 'Duração',
                'money': 'Valor Monetário',
                'money_amount': 'Valor Monetário',
                'percentage': 'Porcentagens',
                'number': 'Números',
                'number_sequence': 'Dados Numéricos',
                'phone_number': 'Números de Telefone',
                'email': 'E-mails',
                'url': 'URLs',
                'medical_condition': 'Condições Médicas',
                'drug': 'Substâncias',
                'nationality': 'Nacionalidades',
                'political_affiliation': 'Afiliações Políticas',
                'occupation': 'Profissões',
                'language': 'Idiomas',
                'event': 'Eventos',
                'facility': 'Instalações',
                'product': 'Produtos',
                'title': 'Títulos',
                'quantity': 'Quantidades',
                'ordinal': 'Ordinais',
                'cardinal': 'Cardinais',
                'misc': 'Diversos',
                'law': 'Leis',
                'legal_document': 'Documentos Legais',
                'court': 'Tribunais',
                'crime': 'Crimes',
                'legal_procedure': 'Procedimentos Legais'
            }
            
            # Tentar traduzir, caso contrário usar o original formatado
            return translations.get(entity_type.lower(), entity_type.replace('_', ' ').title())
        
        return render_template('transcricao_video/result.html',
                             transcricao=type('obj', (object,), transcricao_data),
                             segments=segments,
                             entities=entities,
                             chapters=chapters,
                             highlights=highlights,
                             format_timestamp=format_timestamp,
                             translate_entity_type=translate_entity_type)
        
    except Exception as e:
        logger.error(f"Erro ao carregar resultado: {str(e)}")
        return redirect(url_for('transcricao_video.index'))

@transcricao_video.route('/history')
def history():
    """Histórico de transcrições"""
    try:
        from main import db
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        search = request.args.get('search', '')
        status_filter = request.args.get('status', '')
        
        query = """
            SELECT t.id, t.filename, t.file_size, t.file_type, t.transcript_id, t.status, 
                   t.text, t.confidence, t.duration, t.audio_duration, t.speaker_count, 
                   t.word_count, t.utterance_count, t.summary, t.summary_type, t.config, 
                   t.audio_url, t.created_at, t.processed_at, t.started_at, t.completed_at, 
                   t.error_message, t.retry_count,
                   COUNT(DISTINCT s.id) as segment_count,
                   COUNT(DISTINCT e.id) as entity_count
            FROM transcricoes_video t
            LEFT JOIN speaker_segments s ON t.id = s.transcricao_id
            LEFT JOIN entities e ON t.id = e.transcricao_id
            WHERE 1=1
        """
        params = {}
        
        if search:
            query += " AND t.filename ILIKE :search"
            params['search'] = f"%{search}%"
        
        if status_filter:
            query += " AND t.status = :status"
            params['status'] = status_filter
        
        query += """ GROUP BY t.id, t.filename, t.file_size, t.file_type, t.transcript_id, t.status, 
                     t.text, t.confidence, t.duration, t.audio_duration, t.speaker_count, 
                     t.word_count, t.utterance_count, t.summary, t.summary_type, t.config, 
                     t.audio_url, t.created_at, t.processed_at, t.started_at, t.completed_at, 
                     t.error_message, t.retry_count ORDER BY t.created_at DESC"""
        query += f" LIMIT {per_page} OFFSET {(page-1) * per_page}"
        
        transcricoes = db.session.execute(text(query), params).fetchall()
        
        # Contar total
        count_query = "SELECT COUNT(*) FROM transcricoes_video t WHERE 1=1"
        if search:
            count_query += " AND t.filename ILIKE :search"
        if status_filter:
            count_query += " AND t.status = :status"
        
        total = db.session.execute(text(count_query), params).scalar()
        
        return render_template('transcricao_video/history.html',
                             transcricoes=transcricoes,
                             page=page,
                             per_page=per_page,
                             total=total,
                             search=search,
                             status_filter=status_filter,
                             format_timestamp=format_timestamp)
        
    except Exception as e:
        logger.error(f"Erro ao carregar histórico: {str(e)}")
        return render_template('transcricao_video/history.html', transcricoes=[], total=0)

@transcricao_video.route('/export/<transcript_id>/transcricao-only/<format>')
def export_transcription_only(transcript_id, format):
    """Exportar apenas a transcrição"""
    return redirect(url_for('transcricao_video.export', transcript_id=transcript_id, format=format, mode='transcription'))

@transcricao_video.route('/export/<transcript_id>/com-falantes/<format>')
def export_with_speakers(transcript_id, format):
    """Exportar transcrição com análise por falante"""
    return redirect(url_for('transcricao_video.export', transcript_id=transcript_id, format=format, mode='speakers'))

@transcricao_video.route('/export/<transcript_id>/completo/<format>')
def export_complete(transcript_id, format):
    """Exportar transcrição completa com falantes e entidades"""
    return redirect(url_for('transcricao_video.export', transcript_id=transcript_id, format=format, mode='complete'))

@transcricao_video.route('/export/<transcript_id>/<format>')
def export(transcript_id, format):
    """Exportar transcrição em diferentes formatos"""
    try:
        from flask import request
        from main import db
        
        # Obter modo de exportação (para JSON)
        mode = request.args.get('mode', 'complete')
        # Buscar dados
        result = db.session.execute(text("""
            SELECT * FROM transcricoes_video WHERE transcript_id = :transcript_id
        """), {'transcript_id': transcript_id}).fetchone()
        
        if not result:
            return jsonify({'error': 'Transcrição não encontrada'}), 404
        
        segments = db.session.execute(text("""
            SELECT * FROM speaker_segments 
            WHERE transcricao_id = :transcricao_id 
            ORDER BY start_time
        """), {'transcricao_id': result.id}).fetchall()
        
        # Buscar entidades detectadas
        entities = db.session.execute(text("""
            SELECT * FROM entities 
            WHERE transcricao_id = :transcricao_id 
            ORDER BY entity_type, text
        """), {'transcricao_id': result.id}).fetchall()
        
        if format == 'txt':
            # Exportar como texto simples
            content = f"Transcrição: {result.filename}\n"
            content += f"Data: {result.created_at}\n"
            content += f"Duração: {format_timestamp(result.duration)}\n"
            content += f"Confiança: {result.confidence:.2%}\n\n"
            
            for segment in segments:
                timestamp = format_timestamp(segment.start_time)
                content += f"[{timestamp}] {segment.speaker}: {segment.text}\n"
            
            buffer = BytesIO()
            buffer.write(content.encode('utf-8'))
            buffer.seek(0)
            
            return send_file(
                buffer,
                as_attachment=True,
                download_name=f"transcricao_{result.filename}.txt",
                mimetype='text/plain'
            )
        
        elif format == 'json':
            # Exportar como JSON
            if mode == 'transcription':
                # Apenas Transcrição
                data = {
                    'tipo': 'Apenas Transcrição',
                    'arquivo': {
                        'nome': result.filename,
                        'data_criacao': result.created_at.isoformat() if result.created_at else None,
                        'duracao_segundos': result.duration,
                        'confianca': result.confidence
                    },
                    'transcricao': {
                        'texto_completo': result.text,
                        'total_palavras': result.word_count,
                        'segmentos': []
                    }
                }
                
                for segment in segments:
                    data['transcricao']['segmentos'].append({
                        'falante': segment.speaker,
                        'texto': segment.text,
                        'inicio': segment.start_time,
                        'fim': segment.end_time,
                        'confianca': segment.confidence
                    })
                
                filename_suffix = "transcricao"
                
            elif mode == 'speakers':
                # Transcrição com análise por falante (sem entidades)
                from collections import defaultdict
                
                speaker_stats = defaultdict(lambda: {'intervencoes': 0, 'total_palavras': 0})
                for segment in segments:
                    speaker = segment.speaker or 'Speaker'
                    words = len(segment.text.split()) if segment.text else 0
                    speaker_stats[speaker]['intervencoes'] += 1
                    speaker_stats[speaker]['total_palavras'] += words
                
                data = {
                    'tipo': 'Transcrição com Análise por Falante',
                    'arquivo': {
                        'nome': result.filename,
                        'data_criacao': result.created_at.isoformat() if result.created_at else None,
                        'duracao_segundos': result.duration,
                        'confianca': result.confidence
                    },
                    'transcricao': {
                        'texto_completo': result.text,
                        'total_palavras': result.word_count,
                        'segmentos': []
                    },
                    'analise_falantes': {
                        'total_falantes': len(speaker_stats),
                        'estatisticas': {
                            speaker: {
                                'intervencoes': stats['intervencoes'],
                                'total_palavras': stats['total_palavras'],
                                'media_palavras_por_intervencao': round(stats['total_palavras'] / stats['intervencoes'], 1) if stats['intervencoes'] > 0 else 0
                            }
                            for speaker, stats in speaker_stats.items()
                        }
                    }
                }
                
                for segment in segments:
                    data['transcricao']['segmentos'].append({
                        'falante': segment.speaker,
                        'texto': segment.text,
                        'inicio': segment.start_time,
                        'fim': segment.end_time,
                        'confianca': segment.confidence
                    })
                
                filename_suffix = "transcricao_com_falantes"
                
            else:
                # Análise Completa
                from collections import defaultdict
                
                # Função para traduzir tipos de entidades
                def translate_entity_type(entity_type):
                    translations = {
                        'person': 'Pessoas', 'location': 'Locais', 'organization': 'Organizações',
                        'date': 'Datas', 'time': 'Horários', 'duration': 'Duração',
                        'money': 'Valor Monetário', 'money_amount': 'Valor Monetário',
                        'number': 'Números', 'number_sequence': 'Dados Numéricos',
                        'drug': 'Substâncias', 'phone_number': 'Números de Telefone',
                        'email': 'E-mails', 'percentage': 'Porcentagens'
                    }
                    return translations.get(entity_type.lower(), entity_type.replace('_', ' ').title())
                
                # Análise de falantes
                speaker_stats = defaultdict(lambda: {'intervencoes': 0, 'total_palavras': 0})
                for segment in segments:
                    speaker = segment.speaker or 'Speaker'
                    words = len(segment.text.split()) if segment.text else 0
                    speaker_stats[speaker]['intervencoes'] += 1
                    speaker_stats[speaker]['total_palavras'] += words
                
                # Agrupar entidades
                entity_groups = defaultdict(list)
                for entity in entities:
                    entity_groups[entity.entity_type].append(entity.text)
                
                # Preparar dados de entidades
                entidades_processadas = {}
                for entity_type, entity_list in entity_groups.items():
                    unique_entities = {}
                    for entity_text in entity_list:
                        if entity_text not in unique_entities:
                            unique_entities[entity_text] = 0
                        unique_entities[entity_text] += 1
                    
                    entidades_processadas[translate_entity_type(entity_type)] = [
                        {'texto': texto, 'ocorrencias': count} 
                        for texto, count in unique_entities.items()
                    ]
                
                data = {
                    'tipo': 'Análise Completa',
                    'arquivo': {
                        'nome': result.filename,
                        'data_criacao': result.created_at.isoformat() if result.created_at else None,
                        'duracao_segundos': result.duration,
                        'confianca': result.confidence
                    },
                    'transcricao': {
                        'texto_completo': result.text,
                        'total_palavras': result.word_count,
                        'segmentos': []
                    },
                    'analise_falantes': {
                        'total_falantes': len(speaker_stats),
                        'estatisticas': {
                            speaker: {
                                'intervencoes': stats['intervencoes'],
                                'total_palavras': stats['total_palavras'],
                                'media_palavras_por_intervencao': round(stats['total_palavras'] / stats['intervencoes'], 1) if stats['intervencoes'] > 0 else 0
                            }
                            for speaker, stats in speaker_stats.items()
                        }
                    },
                    'entidades_detectadas': {
                        'total_categorias': len(entidades_processadas),
                        'categorias': entidades_processadas
                    }
                }
                
                for segment in segments:
                    data['transcricao']['segmentos'].append({
                        'falante': segment.speaker,
                        'texto': segment.text,
                        'inicio': segment.start_time,
                        'fim': segment.end_time,
                        'confianca': segment.confidence
                    })
                
                filename_suffix = "analise_completa"
            
            buffer = BytesIO()
            buffer.write(json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8'))
            buffer.seek(0)
            
            return send_file(
                buffer,
                as_attachment=True,
                download_name=f"{filename_suffix}_{result.filename}.json",
                mimetype='application/json'
            )
        
        elif format == 'docx':
            # Exportar como DOCX
            from docx import Document
            from docx.shared import Inches, Pt, RGBColor
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            from docx.oxml.shared import OxmlElement, qn
            
            doc = Document()
            
            # Configurar estilos
            title = doc.add_heading('Transcrição de Áudio/Vídeo', 0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # Informações do arquivo
            info_table = doc.add_table(rows=5, cols=2)
            info_table.style = 'Table Grid'
            
            # Preencher tabela de informações
            info_data = [
                ('Arquivo:', result.filename or 'N/A'),
                ('Data:', result.created_at.strftime('%d/%m/%Y %H:%M:%S') if result.created_at else 'N/A'),
                ('Duração:', format_timestamp(result.audio_duration) if result.audio_duration else 'N/A'),
                ('Confiança:', f"{result.confidence:.1%}" if result.confidence else 'N/A'),
                ('Palavras:', str(result.word_count or len(result.text.split()) if result.text else 0))
            ]
            
            for i, (label, value) in enumerate(info_data):
                info_table.cell(i, 0).text = label
                info_table.cell(i, 1).text = str(value)
                
                # Estilizar células
                for j in range(2):
                    cell = info_table.cell(i, j)
                    if j == 0:
                        # Célula de rótulo - negrito
                        cell.paragraphs[0].runs[0].bold = True
                    cell.paragraphs[0].runs[0].font.size = Pt(11)
            
            # Adicionar espaço
            doc.add_paragraph()
            
            # Título da transcrição
            doc.add_heading('Transcrição Completa', level=1)
            
            if segments:
                # Transcrição por segmentos
                for segment in segments:
                    if segment.text and segment.text.strip():
                        # Timestamp e speaker
                        timestamp = format_timestamp(segment.start_time) if segment.start_time else '00:00:00'
                        speaker = segment.speaker or 'Speaker'
                        
                        # Parágrafo com timestamp e speaker
                        p = doc.add_paragraph()
                        
                        # Timestamp em negrito e azul
                        timestamp_run = p.add_run(f"[{timestamp}] ")
                        timestamp_run.bold = True
                        timestamp_run.font.color.rgb = RGBColor(0, 102, 204)
                        
                        # Speaker em negrito
                        speaker_run = p.add_run(f"{speaker}: ")
                        speaker_run.bold = True
                        
                        # Texto da fala
                        text_run = p.add_run(segment.text)
                        text_run.font.size = Pt(11)
                        
                        # Espaçamento entre parágrafos
                        p.space_after = Pt(6)
            else:
                # Texto completo se não houver segmentos
                if result.text:
                    doc.add_paragraph(result.text)
                else:
                    doc.add_paragraph("Nenhum texto de transcrição disponível.")
            
            # Função para traduzir tipos de entidades
            def translate_entity_type(entity_type):
                translations = {
                    'person': 'Pessoas',
                    'person_name': 'Nomes de Pessoas',
                    'location': 'Locais',
                    'location_name': 'Nomes de Locais',
                    'organization': 'Organizações',
                    'organization_name': 'Nomes de Organizações',
                    'date': 'Datas',
                    'time': 'Horários',
                    'duration': 'Duração',
                    'money': 'Valor Monetário',
                    'money_amount': 'Valor Monetário',
                    'percentage': 'Porcentagens',
                    'number': 'Números',
                    'number_sequence': 'Dados Numéricos',
                    'phone_number': 'Números de Telefone',
                    'email': 'E-mails',
                    'url': 'URLs',
                    'medical_condition': 'Condições Médicas',
                    'drug': 'Substâncias',
                    'nationality': 'Nacionalidades',
                    'political_affiliation': 'Afiliações Políticas',
                    'occupation': 'Profissões',
                    'language': 'Idiomas',
                    'event': 'Eventos',
                    'facility': 'Instalações',
                    'product': 'Produtos',
                    'title': 'Títulos',
                    'quantity': 'Quantidades',
                    'ordinal': 'Ordinais',
                    'cardinal': 'Cardinais',
                    'misc': 'Diversos',
                    'law': 'Leis',
                    'legal_document': 'Documentos Legais',
                    'court': 'Tribunais',
                    'crime': 'Crimes',
                    'legal_procedure': 'Procedimentos Legais'
                }
                return translations.get(entity_type.lower(), entity_type.replace('_', ' ').title())
            
            # Adicionar quebra de página (apenas se houver mais seções)
            if mode in ['speakers', 'complete']:
                doc.add_page_break()
            
            # Seção: Análise por Falantes (apenas para modos speakers e complete)
            if mode in ['speakers', 'complete']:
                doc.add_heading('Análise por Falantes', level=1)
            
            if mode in ['speakers', 'complete']:
                if segments:
                    # Agrupar segmentos por falante
                    from collections import defaultdict
                    speaker_stats = defaultdict(lambda: {'count': 0, 'total_words': 0, 'texts': []})
                    
                    for segment in segments:
                        speaker = segment.speaker or 'Speaker'
                        words = len(segment.text.split()) if segment.text else 0
                        speaker_stats[speaker]['count'] += 1
                        speaker_stats[speaker]['total_words'] += words
                        speaker_stats[speaker]['texts'].append(segment.text)
                    
                    # Criar tabela de estatísticas por falante
                    if speaker_stats:
                        speaker_table = doc.add_table(rows=1, cols=4)
                        speaker_table.style = 'Table Grid'
                        
                        # Cabeçalho da tabela
                        hdr_cells = speaker_table.rows[0].cells
                        hdr_cells[0].text = 'Falante'
                        hdr_cells[1].text = 'Intervenções'
                        hdr_cells[2].text = 'Palavras'
                        hdr_cells[3].text = 'Média por Intervenção'
                        
                        # Estilizar cabeçalho
                        for cell in hdr_cells:
                            cell.paragraphs[0].runs[0].bold = True
                            cell.paragraphs[0].runs[0].font.size = Pt(11)
                        
                        # Adicionar dados dos falantes
                        for speaker, stats in speaker_stats.items():
                            row_cells = speaker_table.add_row().cells
                            row_cells[0].text = speaker
                            row_cells[1].text = str(stats['count'])
                            row_cells[2].text = str(stats['total_words'])
                            avg_words = stats['total_words'] / stats['count'] if stats['count'] > 0 else 0
                            row_cells[3].text = f"{avg_words:.1f}"
                            
                            # Estilizar células
                            for cell in row_cells:
                                cell.paragraphs[0].runs[0].font.size = Pt(10)
                    
                    doc.add_paragraph()
                else:
                    doc.add_paragraph("Nenhuma análise de falantes disponível.")
            
            # Seção: Entidades Detectadas (apenas para modo complete)
            if mode == 'complete':
                doc.add_heading('Entidades Detectadas', level=1)
                
            if entities and mode == 'complete':
                # Agrupar entidades por tipo
                from collections import defaultdict
                entity_groups = defaultdict(list)
                
                for entity in entities:
                    entity_groups[entity.entity_type].append(entity.text)
                
                # Criar lista de entidades por categoria
                for entity_type, entity_list in entity_groups.items():
                    # Título da categoria
                    category_heading = doc.add_heading(translate_entity_type(entity_type), level=2)
                    category_heading.style.font.size = Pt(14)
                    
                    # Remover duplicatas e ordenar
                    unique_entities = list(set(entity_list))
                    unique_entities.sort()
                    
                    # Criar lista de entidades
                    for entity_text in unique_entities:
                        count = entity_list.count(entity_text)
                        if count > 1:
                            p = doc.add_paragraph(f"• {entity_text} ({count}x)")
                        else:
                            p = doc.add_paragraph(f"• {entity_text}")
                        p.style.font.size = Pt(10)
                    
                    doc.add_paragraph()  # Espaço entre categorias
            elif mode == 'complete':
                doc.add_paragraph("Nenhuma entidade detectada.")
            
            # Salvar em buffer
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            
            return send_file(
                buffer,
                as_attachment=True,
                download_name=f"transcricao_{result.filename}.docx",
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
        
        else:
            return jsonify({'error': 'Formato não suportado'}), 400
            
    except Exception as e:
        logger.error(f"Erro na exportação: {str(e)}")
        return jsonify({'error': str(e)}), 500

@transcricao_video.route('/delete/<transcript_id>', methods=['DELETE'])
def delete(transcript_id):
    """Deletar transcrição"""
    try:
        from main import db
        # Buscar ID interno
        result = db.session.execute(text("""
            SELECT id FROM transcricoes_video WHERE transcript_id = :transcript_id
        """), {'transcript_id': transcript_id}).fetchone()
        
        if not result:
            return jsonify({'error': 'Transcrição não encontrada'}), 404
        
        transcricao_id = result.id
        
        # Deletar dados relacionados (sem sentiment_analysis que foi removido)
        db.session.execute(text("DELETE FROM content_safety WHERE transcricao_id = :id"), {'id': transcricao_id})
        db.session.execute(text("DELETE FROM iab_categories WHERE transcricao_id = :id"), {'id': transcricao_id})
        db.session.execute(text("DELETE FROM auto_highlights WHERE transcricao_id = :id"), {'id': transcricao_id})
        db.session.execute(text("DELETE FROM auto_chapters WHERE transcricao_id = :id"), {'id': transcricao_id})
        db.session.execute(text("DELETE FROM entities WHERE transcricao_id = :id"), {'id': transcricao_id})
        db.session.execute(text("DELETE FROM transcript_words WHERE transcricao_id = :id"), {'id': transcricao_id})
        db.session.execute(text("DELETE FROM speaker_segments WHERE transcricao_id = :id"), {'id': transcricao_id})
        db.session.execute(text("DELETE FROM transcricoes_video WHERE id = :id"), {'id': transcricao_id})
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Transcrição deletada com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao deletar: {str(e)}")
        return jsonify({'error': str(e)}), 500

@transcricao_video.route('/queue-status')
def queue_status():
    """Status da fila de processamento"""
    try:
        from main import db
        stats = db.session.execute(text("""
            SELECT 
                status,
                COUNT(*) as count
            FROM transcricoes_video 
            WHERE created_at >= NOW() - INTERVAL '24 hours'
            GROUP BY status
        """)).fetchall()
        
        status_counts = {stat.status: stat.count for stat in stats}
        
        return jsonify({
            'success': True,
            'queue': {
                'processing': status_counts.get('processing', 0),
                'completed': status_counts.get('completed', 0),
                'error': status_counts.get('error', 0),
                'pending': status_counts.get('pending', 0)
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao verificar fila: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

# Inicializar tabelas quando o módulo for importado
def init_transcricao_video():
    """Inicializar módulo de transcrição"""
    try:
        with current_app.app_context():
            create_database_tables()
            logger.info("✅ Módulo de transcrição de vídeo inicializado com sucesso")
            return True
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar módulo de transcrição: {str(e)}")
        return False