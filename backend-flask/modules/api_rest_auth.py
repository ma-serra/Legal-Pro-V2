"""
API REST de Autenticação - Para integração com Frontend React
"""
from flask import Blueprint, request, jsonify
import json
import uuid
from datetime import datetime

auth_rest = Blueprint('auth_rest', __name__, url_prefix='/api/auth')

# Usuários de demo (em produção, usar banco de dados real)
DEMO_USERS = {
    'demo@legal.pro': {
        'password': 'demo123',
        'name': 'Demo User',
        'role': 'admin'
    }
}

@auth_rest.route('/login', methods=['POST'])
def login():
    """
    Endpoint de login para o frontend React
    Recebe: { "email": "demo@legal.pro", "password": "demo123" }
    Retorna: { "token": "token_string", "user": {...} }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Corpo da requisição vazio'}), 400
            
        email = data.get('email', '').lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        # Validar credenciais
        user = DEMO_USERS.get(email)
        if not user or user['password'] != password:
            return jsonify({'error': 'Email ou senha inválidos'}), 401
        
        # Criar token (simples string base64 com UUID)
        token = str(uuid.uuid4())
        
        return jsonify({
            'token': token,
            'user': {
                'email': email,
                'name': user['name'],
                'role': user['role']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao processar login: {str(e)}'}), 500

@auth_rest.route('/logout', methods=['POST'])
def logout():
    """
    Endpoint de logout - no frontend, remover token do localStorage
    """
    return jsonify({'message': 'Logout realizado com sucesso'}), 200

@auth_rest.route('/verify', methods=['GET'])
def verify():
    """
    Endpoint para verificar se o token é válido
    """
    try:
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token não encontrado'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Em produção, validar o token contra a base de dados
        # Por enquanto, qualquer token não-vazio é válido
        if token:
            return jsonify({
                'valid': True,
                'message': 'Token válido'
            }), 200
        
        return jsonify({'valid': False, 'error': 'Token inválido'}), 401
        
    except Exception as e:
        return jsonify({'error': f'Erro ao verificar token: {str(e)}'}), 500

def register_auth_rest_api(app):
    """Função para registrar o blueprint no app"""
    app.register_blueprint(auth_rest)
    print("✅ API REST de Autenticação registrada")
