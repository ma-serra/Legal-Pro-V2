"""
Módulo de Transcrição de Vídeo - Sistema completo compatível
Baseado no módulo transcricao_video.py mas com nome correto para o sistema
"""
import os
import json
import time
import requests
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required
from sqlalchemy import text
import tempfile

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint
video_transcription = Blueprint('video_transcription', __name__, url_prefix='/video-transcription')

# Configuração da AssemblyAI
ASSEMBLYAI_CONFIG = {
    "api_key": os.environ.get("ASSEMBLYAI_API_KEY"),
    "base_url": "https://api.assemblyai.com",
    "chunk_size": 5 * 1024 * 1024,  # 5MB por chunk
    "max_file_size": 200 * 1024 * 1024,  # 200MB máximo
    "supported_formats": [".mp4", ".mp3", ".wav", ".m4a", ".ogg", ".mov", ".avi", ".wmv", ".aac", ".opus"]
}

class VideoTranscriber:
    """Classe principal para transcrição de vídeo"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or ASSEMBLYAI_CONFIG["api_key"]
        self.base_url = ASSEMBLYAI_CONFIG["base_url"]
        self.headers = {"authorization": self.api_key}
    
    def upload_file_direct(self, file_path):
        """Upload arquivo direto para AssemblyAI"""
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
            logger.error(f"Erro no upload para AssemblyAI: {str(e)}")
            raise e
    
    def submit_transcription(self, audio_url):
        """Submeter transcrição com configurações otimizadas"""
        data = {
            "audio_url": audio_url,
            "speech_model": "best",
            "speaker_labels": True,
            "punctuate": True,
            "format_text": True,
            "entity_detection": True,
            "language_code": "pt",
            "filter_profanity": False,
            "speaker_options": {
                "min_speakers": 1,
                "max_speakers": 15
            },
            "speed_boost": False
        }
        
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

def allowed_file(filename):
    """Verificar se o arquivo é de um tipo permitido"""
    return any(filename.lower().endswith(ext) for ext in ASSEMBLYAI_CONFIG["supported_formats"])

def format_timestamp(milliseconds):
    """Converter milissegundos para formato MM:SS"""
    if not milliseconds or milliseconds == 0:
        return "00:00"
    
    if milliseconds < 10000:
        seconds = int(milliseconds)
    else:
        seconds = int(milliseconds / 1000)
    
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"

def create_transcription_tables():
    """Criar tabelas necessárias para transcrição"""
    try:
        from main import db
        
        # Tabela principal de transcrições
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS video_transcriptions (
                id SERIAL PRIMARY KEY,
                filename VARCHAR(255),
                file_size INTEGER,
                file_type VARCHAR(50),
                transcript_id VARCHAR(100),
                status VARCHAR(50),
                text TEXT,
                confidence FLOAT,
                duration INTEGER,
                speaker_count INTEGER,
                word_count INTEGER,
                summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP,
                error_message TEXT
            )
        """))
        
        db.session.commit()
        logger.info("✅ Tabelas de transcrição de vídeo criadas")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {str(e)}")
        return False

def process_video_file(file_path, filename):
    """Processar arquivo de vídeo para transcrição"""
    try:
        if not os.path.exists(file_path):
            raise Exception("Arquivo não encontrado")
        
        if not allowed_file(filename):
            raise Exception("Tipo de arquivo não suportado")
        
        # Inicializar transcriber
        transcriber = VideoTranscriber()
        
        # Upload do arquivo
        logger.info(f"Fazendo upload do arquivo: {filename}")
        audio_url = transcriber.upload_file_direct(file_path)
        
        # Submeter para transcrição
        logger.info("Submetendo para transcrição...")
        transcript_result = transcriber.submit_transcription(audio_url)
        
        transcript_id = transcript_result.get("id")
        if not transcript_id:
            raise Exception("ID de transcrição não retornado")
        
        logger.info(f"Transcrição iniciada com ID: {transcript_id}")
        
        return {
            "success": True,
            "transcript_id": transcript_id,
            "audio_url": audio_url,
            "status": "queued"
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar vídeo: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# ROTAS DO BLUEPRINT

@video_transcription.route('/')
@login_required
def index():
    """Página principal de transcrição de vídeo"""
    try:
        return render_template('video_transcription/index.html')
    except:
        # Fallback se template não existir
        return jsonify({
            "message": "Video Transcription Module - Active",
            "status": "ready",
            "supported_formats": ASSEMBLYAI_CONFIG["supported_formats"]
        })

@video_transcription.route('/upload', methods=['POST'])
@login_required
def upload_video():
    """Upload de vídeo para transcrição"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nenhum arquivo selecionado'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False, 
                'error': f'Tipo de arquivo não suportado. Use: {", ".join(ASSEMBLYAI_CONFIG["supported_formats"])}'
            }), 400
        
        # Salvar arquivo temporariamente
        filename = secure_filename(file.filename)
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)
        file.save(file_path)
        
        # Processar arquivo
        result = process_video_file(file_path, filename)
        
        # Limpar arquivo temporário
        try:
            os.remove(file_path)
        except:
            pass
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro no upload: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@video_transcription.route('/status/<transcript_id>')
@login_required
def check_status(transcript_id):
    """Verificar status da transcrição"""
    try:
        transcriber = VideoTranscriber()
        status_data = transcriber.get_transcript_status(transcript_id)
        
        return jsonify({
            'success': True,
            'status': status_data.get('status'),
            'transcript_id': transcript_id,
            'data': status_data
        })
        
    except Exception as e:
        logger.error(f"Erro ao verificar status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@video_transcription.route('/result/<transcript_id>')
@login_required
def get_result(transcript_id):
    """Obter resultado da transcrição"""
    try:
        transcriber = VideoTranscriber()
        transcript_data = transcriber.get_transcript_status(transcript_id)
        
        if transcript_data.get('status') != 'completed':
            return jsonify({
                'success': False,
                'error': 'Transcrição ainda não completada',
                'status': transcript_data.get('status')
            })
        
        # Extrair texto principal
        text = transcript_data.get('text', '')
        confidence = transcript_data.get('confidence', 0.0)
        
        # Extrair informações de falantes
        speakers_info = []
        utterances = transcript_data.get('utterances', [])
        
        for utterance in utterances:
            speakers_info.append({
                'speaker': utterance.get('speaker', 'Unknown'),
                'text': utterance.get('text', ''),
                'start': format_timestamp(utterance.get('start', 0)),
                'end': format_timestamp(utterance.get('end', 0)),
                'confidence': utterance.get('confidence', 0.0)
            })
        
        return jsonify({
            'success': True,
            'transcript_id': transcript_id,
            'text': text,
            'confidence': confidence,
            'speakers': speakers_info,
            'word_count': len(text.split()) if text else 0,
            'speaker_count': len(set([s['speaker'] for s in speakers_info]))
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter resultado: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Função para registrar o blueprint
def register_video_transcription_routes(app):
    """Registrar rotas de transcrição de vídeo"""
    try:
        app.register_blueprint(video_transcription)
        create_transcription_tables()
        logger.info("✅ Módulo de transcrição de vídeo registrado com sucesso")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao registrar módulo de transcrição: {str(e)}")
        return False

# Funções auxiliares para compatibilidade
def transcribe_video_file(file_path, options=None):
    """Função helper para transcrição direta de arquivo"""
    try:
        filename = os.path.basename(file_path)
        return process_video_file(file_path, filename)
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_transcription_status(transcript_id):
    """Função helper para verificar status"""
    try:
        transcriber = VideoTranscriber()
        return transcriber.get_transcript_status(transcript_id)
    except Exception as e:
        return {"error": str(e)}