"""
Endpoints adicionais para CRUD de conversas
Adicionar ao final de api_rest_assistentes.py
"""

# Adicionar import no topo do arquivo
from models import Conversa
from datetime import datetime
import json

# === NOVOS ENDPOINTS DE CONVERSAS ===

@assistentes_api.route('/<int:assistente_id>/conversas', methods=['POST'])
def criar_conversa(assistente_id):
    """
    Cria uma nova conversa para um assistente
    Body: { "titulo": str, "provider": str, "modelo": str }
    """
    try:
        from models import Conversa
        
        # Verificar se assistente existe
        assistente = AgenteJuridico.query.get_or_404(assistente_id)
        
        data = request.get_json()
        titulo = data.get('titulo', f'Conversa com {assistente.nome}')
        provider = data.get('provider')
        modelo = data.get('modelo')
        
        # Criar conversa
        conversa = Conversa(
            assistente_id=assistente_id,
            usuario_id=None,  # TODO: pegar do current_user quando tiver auth
           titulo=titulo,
            mensagens=[],
            provider_usado=provider,
            modelo_usado=modelo,
            arquivos_anexados=[]
        )
        
        db.session.add(conversa)
        db.session.commit()
        
        logger.info(f"Conversa criada: {conversa.id} para assistente {assistente_id}")
        
        return jsonify({
            'id': conversa.id,
            'titulo': conversa.titulo,
            'mensagens': [],
            'provider_usado': conversa.provider_usado,
            'modelo_usado': conversa.modelo_usado,
            'data_criacao': conversa.data_criacao.isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao criar conversa: {e}")
        return jsonify({'error': 'Erro ao criar conversa'}), 500

@assistentes_api.route('/<int:assistente_id>/conversas/<int:conversa_id>', methods=['GET'])
def obter_conversa(assistente_id, conversa_id):
    """
    Obtém detalhes completos de uma conversa
    """
    try:
        from models import Conversa
        
        conversa = Conversa.query.filter_by(
            id=conversa_id,
            assistente_id=assistente_id,
            ativa=True
        ).first_or_404()
        
        return jsonify({
            'id': conversa.id,
            'titulo': conversa.titulo,
            'mensagens': conversa.mensagens or [],
            'provider_usado': conversa.provider_usado,
            'modelo_usado': conversa.modelo_usado,
            'arquivos_anexados': conversa.arquivos_anexados or [],
            'data_criacao': conversa.data_criacao.isoformat() if conversa.data_criacao else None,
            'data_atualizacao': conversa.data_atualizacao.isoformat() if conversa.data_atualizacao else None
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter conversa {conversa_id}: {e}")
        return jsonify({'error': 'Conversa não encontrada'}), 404

@assistentes_api.route('/<int:assistente_id>/conversas/<int:conversa_id>', methods=['PUT'])
def atualizar_conversa(assistente_id, conversa_id):
    """
    Atualiza uma conversa (título, adiciona mensagem)
    Body: { "titulo": str, "mensagens": [], "provider": str, "modelo": str }
    """
    try:
        from models import Conversa
        
        conversa = Conversa.query.filter_by(
            id=conversa_id,
            assistente_id=assistente_id,
            ativa=True
        ).first_or_404()
        
        data = request.get_json()
        
        # Atualizar campos permitidos
        if 'titulo' in data:
            conversa.titulo = data['titulo']
        if 'mensagens' in data:
            conversa.mensagens = data['mensagens']
        if 'provider' in data:
            conversa.provider_usado = data['provider']
        if 'modelo' in data:
            conversa.modelo_usado = data['modelo']
        
        conversa.data_atualizacao = datetime.now()
        
        db.session.commit()
        
        logger.info(f"Conversa atualizada: {conversa_id}")
        
        return jsonify({'mensagem': 'Conversa atualizada com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao atualizar conversa {conversa_id}: {e}")
        return jsonify({'error': 'Erro ao atualizar conversa'}), 500

@assistentes_api.route('/<int:assistente_id>/conversas/<int:conversa_id>', methods=['DELETE'])
def deletar_conversa(assistente_id, conversa_id):
    """
    Deleta (soft delete) uma conversa
    """
    try:
        from models import Conversa
        
        conversa = Conversa.query.filter_by(
            id=conversa_id,
            assistente_id=assistente_id,
            ativa=True
        ).first_or_404()
        
        # Soft delete
        conversa.ativa = False
        conversa.data_atualizacao = datetime.now()
        
        db.session.commit()
        
        logger.info(f"Conversa deletada: {conversa_id}")
        
        return jsonify({'mensagem': 'Conversa deletada com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao deletar conversa {conversa_id}: {e}")
        return jsonify({'error': 'Erro ao deletar conversa'}), 500
