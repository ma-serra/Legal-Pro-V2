"""
Endpoint de upload de arquivos para conversas
Adicionar ao api_rest_assistentes.py
"""

import os
from werkzeug.utils import secure_filename
from flask import send_from_directory
import uuid

# Configuração de upload
UPLOAD_FOLDER = 'uploads/conversas'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xlsx', 'csv'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@assistentes_api.route('/<int:assistente_id>/conversas/<int:conversa_id>/upload', methods=['POST'])
def upload_arquivo_conversa(assistente_id, conversa_id):
    """
    Upload de arquivo para uma conversa
    """
    try:
        from models import Conversa
        from datetime import datetime
        
        # Verificar se conversa existe
        conversa = Conversa.query.filter_by(
            id=conversa_id,
            assistente_id=assistente_id,
            ativa=True
        ).first_or_404()
        
        # Verificar se há arquivo no request
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Arquivo vazio'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'Tipo de arquivo não permitido. Permitidos: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Verificar tamanho (Flask já limita, mas vamos validar)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': f'Arquivo muito grande. Máximo: {MAX_FILE_SIZE / 1024 / 1024}MB'}), 400
        
        # Gerar nome único
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Criar diretório se não existir
        upload_path = os.path.join(UPLOAD_FOLDER, str(conversa_id))
        os.makedirs(upload_path, exist_ok=True)
        
        # Salvar arquivo
        filepath = os.path.join(upload_path, unique_filename)
        file.save(filepath)
        
        # Adicionar à lista de arquivos da conversa
        arquivo_info = {
            'id': uuid.uuid4().hex,
            'nome': filename,
            'nome_unico': unique_filename,
            'tipo': file.content_type or 'application/octet-stream',
            'tamanho': file_size,
            'url': f'/api/assistentes/{assistente_id}/conversas/{conversa_id}/files/{unique_filename}',
            'data_upload': datetime.now().isoformat()
        }
        
        arquivos_atuais = conversa.arquivos_anexados or []
        arquivos_atuais.append(arquivo_info)
        conversa.arquivos_anexados = arquivos_atuais
        conversa.data_atualizacao = datetime.now()
        
        db.session.commit()
        
        logger.info(f"Arquivo {filename} enviado para conversa {conversa_id}")
        
        return jsonify({
            'mensagem': 'Arquivo enviado com sucesso',
            'arquivo': arquivo_info
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao fazer upload: {e}", exc_info=True)
        return jsonify({'error': 'Erro ao fazer upload do arquivo'}), 500

@assistentes_api.route('/<int:assistente_id>/conversas/<int:conversa_id>/files/<filename>', methods=['GET'])
def download_arquivo_conversa(assistente_id, conversa_id, filename):
    """
    Download de arquivo de uma conversa
    """
    try:
        from models import Conversa
        
        # Verificar se conversa existe
        conversa = Conversa.query.filter_by(
            id=conversa_id,
            assistente_id=assistente_id,
            ativa=True
        ).first_or_404()
        
        # Verificar se arquivo existe na conversa
        arquivos = conversa.arquivos_anexados or []
        arquivo = next((a for a in arquivos if a['nome_unico'] == filename), None)
        
        if not arquivo:
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        # Servir arquivo
        upload_path = os.path.join(UPLOAD_FOLDER, str(conversa_id))
        return send_from_directory(upload_path, filename, as_attachment=True, download_name=arquivo['nome'])
        
    except Exception as e:
        logger.error(f"Erro ao baixar arquivo: {e}")
        return jsonify({'error': 'Erro ao baixar arquivo'}), 500

@assistentes_api.route('/<int:assistente_id>/conversas/<int:conversa_id>/files/<arquivo_id>', methods=['DELETE'])
def deletar_arquivo_conversa(assistente_id, conversa_id, arquivo_id):
    """
    Deletar arquivo de uma conversa
    """
    try:
        from models import Conversa
        from datetime import datetime
        
        conversa = Conversa.query.filter_by(
            id=conversa_id,
            assistente_id=assistente_id,
            ativa=True
        ).first_or_404()
        
        arquivos = conversa.arquivos_anexados or []
        arquivo = next((a for a in arquivos if a['id'] == arquivo_id), None)
        
        if not arquivo:
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        # Remover arquivo do filesystem
        filepath = os.path.join(UPLOAD_FOLDER, str(conversa_id), arquivo['nome_unico'])
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # Remover da lista
        arquivos = [a for a in arquivos if a['id'] != arquivo_id]
        conversa.arquivos_anexados = arquivos
        conversa.data_atualizacao = datetime.now()
        
        db.session.commit()
        
        return jsonify({'mensagem': 'Arquivo deletado com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao deletar arquivo: {e}")
        return jsonify({'error': 'Erro ao deletar arquivo'}), 500
