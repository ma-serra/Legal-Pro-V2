"""
Script para aplicar proteções do papel Master às rotas administrativas
"""

import os
import sys
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def conectar_database():
    """Conecta ao banco PostgreSQL"""
    import psycopg2
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise Exception("DATABASE_URL não configurada")
    return psycopg2.connect(database_url)

def atribuir_papel_master_usuario(username):
    """Atribui papel Master a um usuário específico"""
    conn = conectar_database()
    cursor = conn.cursor()
    
    try:
        # Buscar usuário
        cursor.execute("SELECT id FROM user WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if not user:
            logger.error(f"Usuário {username} não encontrado")
            return False
        
        user_id = user[0]
        
        # Buscar papel Master
        cursor.execute("SELECT id FROM role WHERE name = 'Master'")
        master_role = cursor.fetchone()
        
        if not master_role:
            logger.error("Papel Master não encontrado")
            return False
        
        master_role_id = master_role[0]
        
        # Atribuir papel ao usuário
        cursor.execute("""
            UPDATE user SET role_id = %s WHERE id = %s
        """, (master_role_id, user_id))
        
        conn.commit()
        logger.info(f"✅ Papel Master atribuído ao usuário {username}")
        return True
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Erro ao atribuir papel Master: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def atualizar_main_py():
    """Atualiza main.py com proteções Master"""
    
    # Ler arquivo atual
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Adicionar import dos decoradores se não existir
    if 'from utils.permission_decorators import' not in content:
        # Encontrar linha de imports
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'from flask_login import' in line:
                lines.insert(i+1, 'from utils.permission_decorators import master_required, admin_required, no_master_access')
                break
        content = '\n'.join(lines)
    
    # Aplicar proteção @no_master_access às rotas admin específicas
    admin_routes_to_protect = [
        '@app.route(\'/admin/dashboard\')',
        '@app.route(\'/admin/usuarios\')',
        '@app.route(\'/admin/roles\')',
        '@app.route(\'/admin/permissoes\')',
        '@app.route(\'/admin/config\')',
        '@app.route(\'/admin/apis\')',
        '@app.route(\'/admin/agentes\')',
        '@app.route(\'/admin/monitoring\')'
    ]
    
    lines = content.split('\n')
    new_lines = []
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # Verificar se é uma rota admin que precisa de proteção
        for route in admin_routes_to_protect:
            if route in line:
                # Verificar se já tem decorador de proteção
                if i > 0 and ('@admin_required' in lines[i-1] or '@no_master_access' in lines[i-1]):
                    continue
                
                # Adicionar proteção @no_master_access antes da definição da função
                next_func_line = i + 1
                while next_func_line < len(lines) and not lines[next_func_line].strip().startswith('def '):
                    next_func_line += 1
                
                if next_func_line < len(lines):
                    # Inserir decorador antes da função
                    new_lines.insert(-1, '@no_master_access')
                break
    
    # Escrever arquivo atualizado
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    logger.info("✅ main.py atualizado com proteções Master")

def criar_interface_gestao_master():
    """Cria interface para gestão do papel Master"""
    
    interface_content = '''"""
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
'''
    
    # Criar arquivo da interface
    with open('master_management.py', 'w', encoding='utf-8') as f:
        f.write(interface_content)
    
    logger.info("✅ Interface de gestão Master criada")

def criar_template_master_users():
    """Cria template para gestão de usuários Master"""
    
    template_content = '''{% extends "admin/layout_admin.html" %}

{% block title %}Gestão de Usuários Master{% endblock %}

{% block content %}
<div class="container-fluid mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h1 class="text-white">Gestão de Usuários Master</h1>
        <a href="{{ url_for('admin_dashboard') }}" class="btn btn-secondary">
            <i class="fas fa-arrow-left me-2"></i>Voltar ao Dashboard
        </a>
    </div>
    
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    <div class="row">
        <!-- Usuários Master Atuais -->
        <div class="col-md-6">
            <div class="card bg-dark text-white">
                <div class="card-header">
                    <h5 class="mb-0"><i class="fas fa-crown me-2"></i>Usuários Master</h5>
                </div>
                <div class="card-body">
                    {% if master_users %}
                        <div class="list-group">
                            {% for user in master_users %}
                                <div class="list-group-item bg-secondary text-white d-flex justify-content-between align-items-center">
                                    <div>
                                        <strong>{{ user.username }}</strong>
                                        <small class="d-block text-muted">{{ user.email }}</small>
                                    </div>
                                    <button class="btn btn-sm btn-outline-danger" 
                                            onclick="removeMasterRole({{ user.id }}, '{{ user.username }}')">
                                        <i class="fas fa-minus"></i>
                                    </button>
                                </div>
                            {% endfor %}
                        </div>
                    {% else %}
                        <p class="text-muted">Nenhum usuário com papel Master encontrado.</p>
                    {% endif %}
                </div>
            </div>
        </div>
        
        <!-- Outros Usuários -->
        <div class="col-md-6">
            <div class="card bg-dark text-white">
                <div class="card-header">
                    <h5 class="mb-0"><i class="fas fa-users me-2"></i>Outros Usuários</h5>
                </div>
                <div class="card-body">
                    {% if other_users %}
                        <div class="list-group">
                            {% for user in other_users %}
                                <div class="list-group-item bg-secondary text-white d-flex justify-content-between align-items-center">
                                    <div>
                                        <strong>{{ user.username }}</strong>
                                        <small class="d-block text-muted">{{ user.email }}</small>
                                        {% if user.role %}
                                            <span class="badge bg-info">{{ user.role.name }}</span>
                                        {% else %}
                                            <span class="badge bg-secondary">Sem papel</span>
                                        {% endif %}
                                    </div>
                                    <button class="btn btn-sm btn-outline-success" 
                                            onclick="assignMasterRole({{ user.id }}, '{{ user.username }}')">
                                        <i class="fas fa-plus"></i>
                                    </button>
                                </div>
                            {% endfor %}
                        </div>
                    {% else %}
                        <p class="text-muted">Nenhum usuário disponível para atribuir papel Master.</p>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
    
    <!-- Informações sobre o Papel Master -->
    <div class="row mt-4">
        <div class="col-12">
            <div class="card bg-dark text-white">
                <div class="card-header">
                    <h5 class="mb-0"><i class="fas fa-info-circle me-2"></i>Sobre o Papel Master</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6 class="text-success">Permissões Incluídas:</h6>
                            <ul class="list-unstyled">
                                <li><i class="fas fa-check text-success me-2"></i>Acesso a todas as áreas jurídicas</li>
                                <li><i class="fas fa-check text-success me-2"></i>Uso de todos os agentes especializados</li>
                                <li><i class="fas fa-check text-success me-2"></i>Criação e gestão de fluxos</li>
                                <li><i class="fas fa-check text-success me-2"></i>Exportação de dados</li>
                                <li><i class="fas fa-check text-success me-2"></i>Busca avançada</li>
                            </ul>
                        </div>
                        <div class="col-md-6">
                            <h6 class="text-danger">Restrições:</h6>
                            <ul class="list-unstyled">
                                <li><i class="fas fa-times text-danger me-2"></i>Sem acesso às páginas de administração</li>
                                <li><i class="fas fa-times text-danger me-2"></i>Não pode gerenciar usuários</li>
                                <li><i class="fas fa-times text-danger me-2"></i>Não pode alterar configurações do sistema</li>
                                <li><i class="fas fa-times text-danger me-2"></i>Não pode gerenciar papéis e permissões</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function assignMasterRole(userId, username) {
    if (confirm(`Deseja atribuir papel Master ao usuário ${username}?`)) {
        fetch('/admin/master-users/assign', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `user_id=${userId}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Erro: ' + data.message);
            }
        })
        .catch(error => {
            alert('Erro na requisição: ' + error);
        });
    }
}

function removeMasterRole(userId, username) {
    if (confirm(`Deseja remover papel Master do usuário ${username}?`)) {
        fetch('/admin/master-users/remove', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `user_id=${userId}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Erro: ' + data.message);
            }
        })
        .catch(error => {
            alert('Erro na requisição: ' + error);
        });
    }
}
</script>
{% endblock %}'''
    
    # Criar diretório se não existir
    os.makedirs('templates/admin', exist_ok=True)
    
    # Criar template
    with open('templates/admin/master_users.html', 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    logger.info("✅ Template de gestão Master criado")

def main():
    """Função principal"""
    try:
        logger.info("🚀 Aplicando proteções do papel Master...")
        
        # Atualizar main.py com proteções
        atualizar_main_py()
        
        # Criar interface de gestão
        criar_interface_gestao_master()
        
        # Criar template
        criar_template_master_users()
        
        # Atribuir papel Master ao usuário dmay
        if atribuir_papel_master_usuario('dmay'):
            logger.info("✅ Papel Master atribuído ao usuário dmay")
        
        logger.info("✅ Proteções Master aplicadas com sucesso!")
        
        print("\n" + "="*60)
        print("✅ PROTEÇÕES MASTER APLICADAS COM SUCESSO!")
        print("="*60)
        print("📋 Alterações realizadas:")
        print("   • main.py atualizado com decoradores @no_master_access")
        print("   • Interface de gestão Master criada")
        print("   • Template admin/master_users.html criado")
        print("   • Usuário 'dmay' recebeu papel Master")
        print("   • Rotas administrativas protegidas contra acesso Master")
        print("="*60)
        print("🔗 Nova rota disponível: /admin/master-users")
        print("="*60)
        
    except Exception as e:
        logger.error(f"❌ Erro ao aplicar proteções Master: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()