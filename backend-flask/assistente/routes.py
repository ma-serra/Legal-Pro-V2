"""
Rotas do módulo Assistente.
Este arquivo contém as rotas para o gerenciamento de prompts e outras 
funcionalidades relacionadas ao assistente.
"""
import os
import json
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, current_app, session
from flask_login import login_required, current_user

from .prompts import (
    obter_todos_prompts, 
    obter_prompt_por_modelo, 
    salvar_prompt, 
    excluir_prompt,
    obter_sistema_prompt
)

# Configurar logging
logger = logging.getLogger(__name__)

# Criar blueprint
bp = Blueprint('assistente_admin', __name__, url_prefix='/assistente/admin')


@bp.route('/prompts')
@login_required
def admin_prompts():
    """
    Página de gerenciamento de prompts do assistente.
    """
    return render_template('admin/prompts_novo.html')


@bp.route('/api/prompts/listar', methods=['GET'])
@login_required
def api_prompts_listar():
    """
    API para listar todos os prompts do assistente.
    """
    prompts = obter_todos_prompts()
    return jsonify({'success': True, 'prompts': prompts})


@bp.route('/api/prompts/salvar', methods=['POST'])
@login_required
def api_prompts_salvar():
    """
    API para salvar um prompt do assistente.
    """
    dados = request.json
    
    # Adicionar nome do usuário atual
    if current_user:
        dados['criado_por'] = current_user.username
    
    # Salvar prompt
    prompt_id = salvar_prompt(dados)
    
    if prompt_id:
        return jsonify({'success': True, 'id': prompt_id})
    else:
        return jsonify({'success': False, 'message': 'Erro ao salvar prompt'}), 500


@bp.route('/api/prompts/excluir/<int:prompt_id>', methods=['DELETE'])
@login_required
def api_prompts_excluir(prompt_id):
    """
    API para excluir um prompt do assistente.
    """
    sucesso = excluir_prompt(prompt_id)
    
    if sucesso:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Erro ao excluir prompt'}), 500


def init_app(app):
    """
    Registra o blueprint no aplicativo Flask.
    """
    logger.info("Configurando rotas de gerenciamento de prompts")
    app.register_blueprint(bp)
    
    # Também adiciona rotas diretamente no aplicativo principal para compatibilidade
    @app.route('/admin/prompts')
    @login_required
    def admin_prompts_main():
        """Redirecionamento para a página de gerenciamento de prompts"""
        return render_template('admin/prompts.html')
    
    @app.route('/api/admin/prompts/listar', methods=['GET'])
    @login_required
    def api_prompts_listar_main():
        """API para listar todos os prompts do assistente"""
        prompts = obter_todos_prompts()
        return jsonify({'success': True, 'prompts': prompts})

    @app.route('/api/admin/prompts/salvar', methods=['POST'])
    @login_required
    def api_prompts_salvar_main():
        """API para salvar um prompt do assistente"""
        dados = request.json
        
        # Adicionar nome do usuário atual
        if current_user:
            dados['criado_por'] = current_user.username
        
        # Salvar prompt
        prompt_id = salvar_prompt(dados)
        
        if prompt_id:
            return jsonify({'success': True, 'id': prompt_id})
        else:
            return jsonify({'success': False, 'message': 'Erro ao salvar prompt'}), 500

    @app.route('/api/admin/prompts/excluir/<int:prompt_id>', methods=['DELETE'])
    @login_required
    def api_prompts_excluir_main(prompt_id):
        """API para excluir um prompt do assistente"""
        sucesso = excluir_prompt(prompt_id)
        
        if sucesso:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Erro ao excluir prompt'}), 500