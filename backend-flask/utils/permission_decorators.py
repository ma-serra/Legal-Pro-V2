"""
Decoradores de permissão para o sistema jurídico
Inclui verificações para papéis Master e Admin
"""

from functools import wraps
from flask import redirect, url_for, flash, abort
from flask_login import current_user
import logging

logger = logging.getLogger(__name__)

def master_required(f):
    """
    Decorador que exige papel Master ou superior para acessar a rota.
    
    Args:
        f: Função da rota a ser protegida
        
    Returns:
        Função decorada com verificação de permissão Master
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        
        from utils.permission_filter import is_master_user, is_admin_user
        
        # Admin tem acesso automático
        if is_admin_user():
            return f(*args, **kwargs)
        
        # Verificar se é Master
        if not is_master_user():
            flash('Acesso negado. Necessário papel Master ou superior.', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """
    Decorador que exige papel de Administrador para acessar a rota.
    
    Args:
        f: Função da rota a ser protegida
        
    Returns:
        Função decorada com verificação de permissão Admin
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        
        from utils.permission_filter import is_admin_user
        
        # Verificar se é Admin
        if not is_admin_user():
            flash('Acesso negado. Necessário papel de Administrador.', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    
    return decorated_function

def no_master_access(f):
    """
    Decorador que BLOQUEIA acesso para usuários Master e Advogado (apenas Admin).
    Usado para páginas de administração.
    
    Args:
        f: Função da rota a ser protegida
        
    Returns:
        Função decorada que bloqueia Masters e Advogados
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        
        from utils.permission_filter import is_admin_user, is_master_user, is_advogado_user
        
        # Apenas Admin pode acessar
        if not is_admin_user():
            if is_master_user():
                flash('Acesso negado. Esta área é restrita aos Administradores.', 'error')
            elif is_advogado_user():
                flash('Acesso negado. Advogados não têm acesso às rotas administrativas.', 'error')
            else:
                flash('Acesso negado. Necessário papel de Administrador.', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    
    return decorated_function

def advogado_or_admin_required(f):
    """
    Decorador que exige papel de Advogado ou Administrador para acessar a rota.
    
    Args:
        f: Função da rota a ser protegida
        
    Returns:
        Função decorada com verificação de permissão Advogado ou Admin
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        
        from utils.permission_filter import is_admin_user, is_advogado_user
        
        # Verificar se é Admin ou Advogado
        if not (is_admin_user() or is_advogado_user()):
            flash('Acesso negado. Necessário papel de Advogado ou Administrador.', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    
    return decorated_function
