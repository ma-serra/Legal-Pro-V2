"""
API REST para Transcrição de Áudio e Vídeo
"""
from flask import Blueprint, jsonify, request
from main import db
from models import ArquivoTranscricao, User
import logging
from datetime import datetime
import os
import uuid

logger = logging.getLogger(__name__)

transcricao_api = Blueprint('transcricao_api', __name__, url_prefix='/api/transcricao')

ALLOWED_AUDIO = {'mp3', 'wav', 'ogg', 'flac', 'm4a'}
ALLOWED_VIDEO = {'mp4', 'mov', 'avi', 'mkv', 'webm'}

def allowed_file(filename, file_type='audio'):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    if file_type == 'audio':
        return ext in ALLOWED_AUDIO
    elif file_type == 'video':
        return ext in ALLOWED_VIDEO
    return False

@transcricao_api.route('/audio', methods=['POST'])
def transcrever_audio():
    """
    Upload e transcrição de arquivo de áudio
    Form-data: file (audio)
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Arquivo não fornecido'}), 400
        
        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename, 'audio'):
            return jsonify({'error': 'Arquivo de áudio inválido'}), 400
        
        # Gerar ID único
        arquivo_id = str(uuid.uuid4())
        
        # TODO: Salvar arquivo no sistema
        # TODO: Processar com Whisper/AssemblyAI
        
        # Mock: criar registro
        arquivo = ArquivoTranscricao(
            id=arquivo_id,
            usuario_id=1,  # Mock
            arquivo_nome=file.filename,
            arquivo_path=f"/uploads/{arquivo_id}_{file.filename}",
            arquivo_tipo=file.content_type or 'audio/mpeg',
            arquivo_tamanho=1024,  # Mock
            status='em_processamento'
        )
        db.session.add(arquivo)
        db.session.commit()
        
        return jsonify({
            'transcricao_id': arquivo_id,
            'arquivo': file.filename,
            'status': 'em_processamento',
            'message': 'Áudio enviado. Transcrição em andamento...',
            'estimativa': '2-3 minutos'
        }), 202
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao transcrever áudio: {e}")
        return jsonify({'error': 'Erro ao processar áudio'}), 500

@transcricao_api.route('/video', methods=['POST'])
def transcrever_video():
    """
    Upload e transcrição de arquivo de vídeo
    Form-data: file (video)
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Arquivo não fornecido'}), 400
        
        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename, 'video'):
            return jsonify({'error': 'Arquivo de vídeo inválido'}), 400
        
        # Gerar ID único
        arquivo_id = str(uuid.uuid4())
        
        # Mock: criar registro
        arquivo = ArquivoTranscricao(
            id=arquivo_id,
            usuario_id=1,  # Mock
            arquivo_nome=file.filename,
            arquivo_path=f"/uploads/{arquivo_id}_{file.filename}",
            arquivo_tipo=file.content_type or 'video/mp4',
            arquivo_tamanho=2048,  # Mock
            status='em_processamento'
        )
        db.session.add(arquivo)
        db.session.commit()
        
        return jsonify({
            'transcricao_id': arquivo_id,
            'arquivo': file.filename,
            'status': 'em_processamento',
            'message': 'Vídeo enviado. Extração de áudio e transcrição em andamento...',
            'estimativa': '5-10 minutos'
        }), 202
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao transcrever vídeo: {e}")
        return jsonify({'error': 'Erro ao processar vídeo'}), 500

@transcricao_api.route('/<string:transcricao_id>', methods=['GET'])
def status_transcricao(transcricao_id):
    """
    Verifica status de uma transcrição
    """
    try:
        arquivo = ArquivoTranscricao.query.get_or_404(transcricao_id)
        
        return jsonify({
            'transcricao_id': arquivo.id,
            'arquivo': arquivo.arquivo_nome,
            'tipo': arquivo.arquivo_tipo,
            'status': arquivo.status,
            'tamanho': arquivo.arquivo_tamanho,
            'data_upload': arquivo.data_upload.isoformat() if arquivo.data_upload else None
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar transcrição {transcricao_id}: {e}")
        return jsonify({'error': 'Transcrição não encontrada'}), 404

@transcricao_api.route('/<string:transcricao_id>/resultado', methods=['GET'])
def resultado_transcricao(transcricao_id):
    """
    Retorna resultado da transcrição (quando concluída)
    """
    try:
        arquivo = ArquivoTranscricao.query.get_or_404(transcricao_id)
        
        if arquivo.status != 'processado':
            return jsonify({
                'transcricao_id': arquivo.id,
                'status': arquivo.status,
                'message': 'Transcrição ainda não concluída'
            }), 202
        
        # Mock: resultado de transcrição
        resultado_mock = {
            'transcricao_id': arquivo.id,
            'arquivo': arquivo.arquivo_nome,
            'status': 'concluido',
            'texto': """
Transcrição Completa

[00:00:00] Olá, este é um sistema de transcrição automática de áudio para texto.
[00:00:15] O sistema utiliza modelos de IA avançados para reconhecimento de fala.
[00:00:30] Esta é uma transcrição mockada para demonstração.
[00:00:45] Em produção, utilizaremos Whisper OpenAI ou AssemblyAI.
[00:01:00] Fim da transcrição.
""",
            'duracao_segundos': 60,
            'confianca_media': 0.94,
            'idioma_detectado': 'pt-BR',
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(resultado_mock), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter resultado {transcricao_id}: {e}")
        return jsonify({'error': 'Erro ao obter resultado'}), 500

@transcricao_api.route('/formatos', methods=['GET'])
def formatos_suportados():
    """
    Lista formatos de arquivo suportados
    """
    return jsonify({
        'audio': list(ALLOWED_AUDIO),
        'video': list(ALLOWED_VIDEO)
    }), 200

def register_transcricao_api(app):
    """Registra o blueprint de transcrição no app"""
    app.register_blueprint(transcricao_api)
    print("✅ API REST de Transcrição registrada")
    logger.info("✅ API REST de Transcrição registrada com sucesso")
