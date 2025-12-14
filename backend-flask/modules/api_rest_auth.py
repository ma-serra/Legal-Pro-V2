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
    Login - Validação REAL contra PostgreSQL
    Aceita email e senha, valida contra tabela 'user'
    """
    try:
        from models import User
        from main import db
        
        data = request.get_json() or {}
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email e senha são obrigatórios'
            }), 400
        
        # Buscar usuário por email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            logger.warning(f"Tentativa de login com email não encontrado: {email}")
            return jsonify({
                'success': False,
                'message': 'Usuário ou senha inválidos'
            }), 401
        
        # Verificar senha
        if not user.check_password(password):
            logger.warning(f"Senha incorreta para usuário: {email}")
            return jsonify({
                'success': False,
                'message': 'Usuário ou senha inválidos'
            }), 401
        
        # Verificar se usuário está ativo
        if not user.active:
            logger.warning(f"Tentativa de login com usuário inativo: {email}")
            return jsonify({
                'success': False,
                'message': 'Usuário inativo. Entre em contato com o administrador.'
            }), 403
        
        # Criar token JWT válido
        token_data = {
            'user_id': user.id,
            'email': user.email,
            'username': user.username,
            'is_admin': user.is_admin,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        token = jwt.encode(
            token_data,
            current_app.config.get('SECRET_KEY', 'dev-secret-key-123'),
            algorithm='HS256'
        )
        
        # Atualizar último login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"✅ Login bem-sucedido: {user.email} (ID: {user.id})")
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'nome': f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_admin': user.is_admin,
                'role': 'admin' if user.is_admin else 'user'
            },
            'message': '✅ Login realizado com sucesso!'
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Erro no login: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': 'Erro interno no servidor. Tente novamente.'
        }), 500

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
    print("✅ API REST de Autenticação registrada (validação PostgreSQL)")
    logger.info("✅ API REST de Autenticação registrada (validação PostgreSQL)")
