"""
Interface de Gestão do Papel Master
Permite atribuir e remover papel Master de usuários
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required
from utils.permission_decorators import admin_required
from models import db, User, Role
import logging

logger = logging.getLogger(__name__)

master_management_bp = Blueprint('master_management', __name__)

@master_management_bp.route('/admin/master-users')
@login_required
@admin_required
def admin_master_users():
    """Página de gestão de usuários Master"""
    try:
        # Buscar papel Master
        master_role = Role.query.filter_by(name='Master').first()
        
        # Buscar todos os usuários
        users = User.query.all()
        
        # Separar usuários Master e outros
        master_users = []
        other_users = []
        
        for user in users:
            if user.role and user.role.name == 'Master':
                master_users.append(user)
            elif not (user.role and user.role.name == 'Administrador'):
                other_users.append(user)
        
        return render_template('admin/master_users.html', 
                             master_users=master_users, 
                             other_users=other_users,
                             master_role=master_role)
        
    except Exception as e:
        logger.error(f"Erro ao carregar gestão Master: {e}")
        flash('Erro ao carregar gestão de usuários Master', 'error')
        return redirect(url_for('admin_dashboard'))

@master_management_bp.route('/admin/master-users/assign', methods=['POST'])
@login_required
@admin_required
def assign_master_role():
    """Atribui papel Master a um usuário"""
    try:
        user_id = request.form.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': 'ID do usuário não fornecido'})
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'})
        
        master_role = Role.query.filter_by(name='Master').first()
        if not master_role:
            return jsonify({'success': False, 'message': 'Papel Master não encontrado'})
        
        # Verificar se já é admin
        if user.role and user.role.name == 'Administrador':
            return jsonify({'success': False, 'message': 'Usuário já é Administrador'})
        
        # Atribuir papel Master
        user.role_id = master_role.id
        db.session.commit()
        
        logger.info(f"Papel Master atribuído ao usuário {user.username}")
        return jsonify({'success': True, 'message': f'Papel Master atribuído a {user.username}'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao atribuir papel Master: {e}")
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})

@master_management_bp.route('/admin/master-users/remove', methods=['POST'])
@login_required
@admin_required
def remove_master_role():
    """Remove papel Master de um usuário"""
    try:
        user_id = request.form.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': 'ID do usuário não fornecido'})
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'})
        
        # Remover papel Master
        user.role_id = None
        db.session.commit()
        
        logger.info(f"Papel Master removido do usuário {user.username}")
        return jsonify({'success': True, 'message': f'Papel Master removido de {user.username}'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao remover papel Master: {e}")
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})

def register_master_management(app):
    """Registra blueprint de gestão Master"""
    app.register_blueprint(master_management_bp)
