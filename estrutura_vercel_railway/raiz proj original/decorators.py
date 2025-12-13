from functools import wraps
from flask import flash, redirect, url_for, request, abort
from flask_login import current_user

def admin_required(f):
    """Verifica se o usuário tem o papel de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
            
        if not current_user.has_role('admin'):
            flash('Você não tem permissão para acessar esta página.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def mediator_required(f):
    """Verifica se o usuário tem o papel de mediador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
            
        if not (current_user.has_role('admin') or current_user.has_role('mediator')):
            flash('Você não tem permissão para acessar esta página.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def permission_required(permission_code):
    """
    Verifica se o usuário tem a permissão específica
    Uso: @permission_required('user.create')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Por favor, faça login para acessar esta página.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            if not current_user.has_permission(permission_code):
                flash(f'Acesso negado. Você não tem permissão para realizar esta ação.', 'danger')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def role_or_permission_required(role_name, permission_code):
    """
    Verifica se o usuário tem o papel OU a permissão específica
    Uso: @role_or_permission_required('admin', 'user.view')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Por favor, faça login para acessar esta página.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            if not (current_user.has_role(role_name) or current_user.has_permission(permission_code)):
                flash('Acesso negado. Você não tem permissão para acessar esta página.', 'danger')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def any_permission_required(permission_codes):
    """
    Verifica se o usuário tem pelo menos uma das permissões especificadas
    Uso: @any_permission_required(['user.create', 'user.edit'])
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Por favor, faça login para acessar esta página.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            if not current_user.has_any_permission(permission_codes):
                flash('Acesso negado. Você não tem permissão para acessar esta página.', 'danger')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def check_permission_json(permission_code):
    """
    Verifica permissão para rotas que retornam JSON
    Uso: check_permission_json('user.edit')
    """
    if not current_user.is_authenticated:
        return abort(401)  # Unauthorized
    
    if not current_user.has_permission(permission_code):
        return abort(403)  # Forbidden