"""
Sistema de bypass de autenticação para administradores
Permite acesso irrestrito ao sistema para usuários admin
"""

import os
import time
from functools import wraps
from flask import session, request, g
from flask_login import current_user
import logging

logger = logging.getLogger(__name__)

# Lista de usuários admin com acesso irrestrito
ADMIN_USERS = [
    'admin',
    'dmay', 
    'administrador',
    'root',
    'sistema'
]

def is_admin_user():
    """Verifica se o usuário atual é um administrador com acesso irrestrito"""
    try:
        # Verificar se há usuário logado
        if hasattr(current_user, 'username') and current_user.username:
            return current_user.username.lower() in [u.lower() for u in ADMIN_USERS]
        
        # Verificar parâmetros de URL para bypass de desenvolvimento
        if request.args.get('admin_bypass') == 'true':
            logger.info("Admin bypass ativado via parâmetro URL")
            return True
            
        # Verificar header especial para admin
        if request.headers.get('X-Admin-Access') == 'unrestricted':
            logger.info("Admin bypass ativado via header")
            return True
            
        # Verificar variável de ambiente para desenvolvimento
        if os.environ.get('ADMIN_BYPASS_MODE') == 'true':
            logger.info("Admin bypass ativado via variável de ambiente")
            return True
            
        return False
        
    except Exception as e:
        logger.error(f"Erro ao verificar admin: {e}")
        return False

def admin_bypass_required(f):
    """Decorator que permite acesso irrestrito para administradores"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if is_admin_user():
            # Admin tem acesso irrestrito - criar contexto simulado se necessário
            if not hasattr(g, 'admin_access'):
                g.admin_access = True
                logger.info(f"Acesso admin autorizado para {request.endpoint}")
            return f(*args, **kwargs)
        else:
            # Usuário comum - aplicar autenticação normal
            from flask_login import login_required
            return login_required(f)(*args, **kwargs)
    return decorated_function

def bypass_all_restrictions():
    """Ativa bypass completo de autenticação para desenvolvimento"""
    session['admin_bypass_active'] = True
    session['bypass_timestamp'] = str(int(time.time()))
    logger.warning("BYPASS COMPLETO DE AUTENTICAÇÃO ATIVADO - USE APENAS EM DESENVOLVIMENTO")

def setup_admin_bypass(app):
    """Configura o sistema de bypass para a aplicação"""
    
    @app.before_request
    def setup_admin_context():
        """Configura contexto admin antes de cada requisição"""
        if is_admin_user():
            g.is_admin = True
            g.unrestricted_access = True
            
            # Log de acesso admin para auditoria
            logger.info(f"Acesso admin detectado: {request.endpoint} - {request.method}")
        else:
            g.is_admin = False
            g.unrestricted_access = False
    
    logger.info("Sistema de bypass admin configurado com sucesso")

# Função para criar usuário admin automaticamente
def create_admin_user():
    """Cria usuário admin padrão se não existir"""
    try:
        from models import User, Role
        from app import db
        from werkzeug.security import generate_password_hash
        
        # Verificar se admin já existe
        admin_user = User.query.filter_by(username='dmay').first()
        if not admin_user:
            
            # Criar role admin se não existir
            admin_role = Role.query.filter_by(name='admin').first()
            if not admin_role:
                admin_role = Role(
                    name='admin',
                    description='Administrador do sistema com acesso irrestrito'
                )
                db.session.add(admin_role)
                db.session.commit()
            
            # Criar usuário admin
            admin_user = User(
                username='dmay',
                email='admin@sistema.com',
                first_name='Admin',
                last_name='Sistema',
                is_admin=True,
                active=True,
                role_id=admin_role.id
            )
            admin_user.password_hash = generate_password_hash('admin123')
            
            db.session.add(admin_user)
            db.session.commit()
            
            logger.info("✅ Usuário admin 'dmay' criado com sucesso")
            return True
        else:
            logger.info("Usuário admin 'dmay' já existe")
            return True
            
    except Exception as e:
        logger.error(f"Erro ao criar usuário admin: {e}")
        return False