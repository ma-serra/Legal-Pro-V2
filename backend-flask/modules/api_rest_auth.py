"""
API REST para Autenticação - MODO DESENVOLVIMENTO (sem senha)
"""
from flask import Blueprint, jsonify, request, current_app
import jwt
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

auth_api = Blueprint('auth_api', __name__, url_prefix='/api/auth')

@auth_api.route('/login', methods=['POST'])
def login():
    """
    Login - MODO DESENVOLVIMENTO (sem autenticação)
    Qualquer email/senha aceito - retorna token válido
    """
    try:
        data = request.get_json() or {}
        
        # Modo desenvolvimento - sempre retorna sucesso
        email = data.get('email', 'dev@legal.pro')
        
        # Criar token mockado (válido por 24h)
        token_data = {
            'user_id': 1,
            'email': email,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        token = jwt.encode(
            token_data,
            current_app.config.get('SECRET_KEY', 'dev-secret-key-123'),
            algorithm='HS256'
        )
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': 1,
                'email': email,
                'nome': 'Desenvolvedor',
                'role': 'admin'
            },
            'message': '✅ Login automático - Modo Desenvolvimento (senha desabilitada)'
        }), 200
        
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        # Mesmo com erro, retorna sucesso em modo dev
        return jsonify({
            'success': True,
            'token': 'dev-token-123',
            'user': {
                'id': 1,
                'email': 'dev@legal.pro',
                'nome': 'Desenvolvedor',
                'role': 'admin'
            },
            'message': '✅ Login automático - Modo Desenvolvimento (fallback)'
        }), 200

@auth_api.route('/logout', methods=['POST'])
def logout():
    """
    Logout (mockado)
    """
    return jsonify({'success': True, 'message': 'Logout realizado'}), 200

@auth_api.route('/verify', methods=['GET'])
def verify_token():
    """
    Verifica token JWT - MODO DESENVOLVIMENTO (sempre válido)
    """
    # Modo desenvolvimento - sempre retorna válido
    return jsonify({
        'valid': True,
        'user': {
            'id': 1,
            'email': 'dev@legal.pro',
            'nome': 'Desenvolvedor',
            'role': 'admin'
        }
    }), 200

def register_auth_api(app):
    """Registra o blueprint de autenticação no app"""
    app.register_blueprint(auth_api)
    print("✅ API REST de Autenticação registrada (MODO DEV - SEM SENHA)")
    logger.info("✅ API REST de Autenticação registrada (MODO DEV - SEM SENHA)")
