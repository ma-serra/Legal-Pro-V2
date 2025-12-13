"""
Configuração de autenticação para o sistema multi-agente.
"""
import datetime
import logging
from functools import wraps
from flask import request, session, redirect, url_for, flash, abort, current_app
from flask_login import current_user, login_required
from main import db, login_manager
from models import User, AuditLog

logger = logging.getLogger(__name__)

@login_manager.user_loader
def load_user(user_id):
    """
    Carrega um usuário a partir do ID.
    
    Args:
        user_id: ID do usuário
        
    Returns:
        User: Objeto do usuário ou None
    """
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        logger.error(f"Erro ao carregar usuário {user_id}: {e}")
        db.session.rollback()
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

def admin_required(f):
    """
    Decorador para rotas que exigem permissão de administrador.
    
    Args:
        f: Função a ser decorada
        
    Returns:
        Função decorada
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        
        if not current_user.is_admin:
            flash('Você não tem permissão para acessar esta página.', 'danger')
            return abort(403)
            
        return f(*args, **kwargs)
    return decorated_function

def permission_required(permission_code):
    """
    Decorador para rotas que exigem uma permissão específica.
    
    Args:
        permission_code: Código da permissão necessária
        
    Returns:
        Decorator para a função
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Por favor, faça login para acessar esta página.', 'warning')
                return redirect(url_for('login'))
            
            if not current_user.has_permission(permission_code):
                flash('Você não tem permissão para acessar esta página.', 'danger')
                return abort(403)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_audit(action, entity_type=None, entity_id=None, details=None):
    """
    Registra uma ação para auditoria.
    
    Args:
        action: Ação realizada
        entity_type: Tipo da entidade afetada
        entity_id: ID da entidade afetada
        details: Detalhes adicionais
    """
    try:
        audit = AuditLog()
        audit.action = action
        audit.entity_type = entity_type
        audit.entity_id = entity_id
        audit.details = details
        
        # Registra o usuário se estiver autenticado
        if current_user.is_authenticated:
            audit.user_id = current_user.id
            
        # Registra o IP do cliente
        if request:
            audit.ip_address = request.remote_addr
            
        db.session.add(audit)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Erro ao registrar auditoria: {str(e)}")
        db.session.rollback()