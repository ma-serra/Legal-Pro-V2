"""
Utilitários de autenticação e autorização.
"""
import logging
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

# Configuração do módulo de logs
logger = logging.getLogger(__name__)

def admin_required(f):
    """
    Decorador para rotas que exigem acesso de administrador.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Acesso negado. Você precisa ter permissões de administrador.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def permission_required(permission_code):
    """
    Decorador para rotas que exigem uma permissão específica.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Acesso negado. Você precisa estar autenticado.', 'danger')
                return redirect(url_for('login'))
                
            if not current_user.has_permission(permission_code) and not current_user.is_admin:
                flash(f'Acesso negado. Você não tem a permissão necessária: {permission_code}.', 'danger')
                return redirect(url_for('index'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator