"""
Controlador para funções administrativas do sistema.
"""
import json
import os
from datetime import datetime
from flask import Blueprint, render_template, jsonify, request, abort, current_app
from werkzeug.utils import secure_filename
from typing import Dict, List, Any, Optional, Tuple

import logging
# Configurando o logger temporário até que o sistema de logs esteja pronto
logger = logging.getLogger("admin_controller")

# Criando o blueprint para rotas administrativas
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# Rotas de visualização (páginas HTML)
# Importações adiadas para evitar importação circular
def get_system_monitor():
    from multiagent.utils import get_system_monitor as _get_system_monitor
    return _get_system_monitor()

def get_log_manager():
    from multiagent.utils import get_log_manager as _get_log_manager
    return _get_log_manager()

@admin_bp.route('/')
def admin_dashboard():
    """Página principal do painel administrativo."""
    try:
        system_monitor = get_system_monitor()
        log_manager = get_log_manager()
    
        # Obtém informações do sistema e do processo
        system_info = system_monitor.get_system_info()
        system_info["cpu"] = system_monitor.get_cpu_info()
        system_info["memory"] = system_monitor.get_memory_info()
        system_info["disk"] = system_monitor.get_disk_info()
        
        process_info = system_monitor.get_process_info()
        
        # Obtém entradas recentes de log
        latest_entries = log_manager.get_latest_log_entries(count=15)
        
        # Obtém lista de arquivos de log
        log_files = log_manager.list_log_files()[:5]  # Limita a 5 arquivos
        
        # Verifica se o modo de debug está ativado
        debug_enabled = log_manager.debug_mode
        
        return render_template(
            'admin/dashboard.html',
            title='Dashboard',
            system_info=system_info,
            process_info=process_info,
            latest_entries=latest_entries,
            log_files=log_files,
            debug_enabled=debug_enabled
        )
    except Exception as e:
        logger.error(f"Erro ao carregar dashboard administrativo: {str(e)}")
        return render_template(
            'admin/error.html',
            title='Erro',
            error=str(e)
        )


@admin_bp.route('/sistema')
def admin_system():
    """Página de informações do sistema."""
    try:
        system_monitor = get_system_monitor()
        log_manager = get_log_manager()
        
        # Obtém informações do sistema e do processo
        system_info = system_monitor.get_system_info()
        system_info["cpu"] = system_monitor.get_cpu_info()
        system_info["memory"] = system_monitor.get_memory_info()
        system_info["disk"] = system_monitor.get_disk_info()
        
        process_info = system_monitor.get_process_info()
        
        # Obtém lista de módulos instalados
        modules = system_monitor.get_installed_python_modules()
        
        # Verifica se o modo de debug está ativado
        debug_enabled = log_manager.debug_mode
        
        return render_template(
            'admin/sistema.html',
            title='Sistema',
            system_info=system_info,
            process_info=process_info,
            modules=modules,
            debug_enabled=debug_enabled
        )
    except Exception as e:
        logger.error(f"Erro ao carregar informações do sistema: {str(e)}")
        return render_template(
            'admin/error.html',
            title='Erro',
            error=str(e)
        )


@admin_bp.route('/logs')
def admin_logs():
    """Página de visualização de logs."""
    try:
        log_manager = get_log_manager()
        
        # Obtém nome do log selecionado (se houver)
        selected_log = request.args.get('log')
        
        # Obtém lista de arquivos de log
        log_files = log_manager.list_log_files()
        
        # Obtém conteúdo do log selecionado
        log_content = log_manager.read_log_file(selected_log) if selected_log else None
        
        # Obtém configuração de log atual
        log_config = log_manager.get_config()
        
        # Verifica se o modo de debug está ativado
        debug_enabled = log_manager.debug_mode
        
        return render_template(
            'admin/logs.html',
            title='Logs',
            log_files=log_files,
            selected_log=selected_log,
            log_content=log_content,
            log_config=log_config,
            debug_enabled=debug_enabled
        )
    except Exception as e:
        logger.error(f"Erro ao carregar página de logs: {str(e)}")
        return render_template(
            'admin/error.html',
            title='Erro',
            error=str(e)
        )


# Rotas de API (JSON)
@admin_bp.route('/debug', methods=['POST'])
def admin_toggle_debug():
    """API para ativar/desativar modo de debug."""
    enabled = request.form.get('enabled') in ('true', 'True', '1', True)
    
    try:
        log_manager = get_log_manager()
        result = log_manager.toggle_debug_mode(enabled)
        
        message = 'Modo de debug ativado' if result else 'Modo de debug desativado'
        logger.info(message)
        
        return jsonify({
            'success': True,
            'debug_enabled': result,
            'message': message
        })
    except Exception as e:
        logger.error(f"Erro ao alternar modo de debug: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })


@admin_bp.route('/logs/config', methods=['POST'])
def admin_update_log_config():
    """API para atualizar configuração de logs."""
    try:
        log_manager = get_log_manager()
        
        # Obtém os parâmetros do form
        config = {
            'log_level': request.form.get('log_level'),
            'log_format': request.form.get('log_format'),
            'log_to_console': request.form.get('log_to_console') in ('true', 'True', '1', True),
            'log_to_file': request.form.get('log_to_file') in ('true', 'True', '1', True)
        }
        
        # Atualiza a configuração
        result = log_manager.update_log_config(config)
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Configuração de logs atualizada com sucesso'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Erro ao atualizar configuração de logs'
            })
    except Exception as e:
        logger.error(f"Erro ao atualizar configuração de logs: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })


@admin_bp.route('/logs/clear', methods=['POST'])
def admin_clear_logs():
    """API para limpar logs."""
    try:
        log_manager = get_log_manager()
        
        # Verifica se deve manter o arquivo atual
        keep_current = request.form.get('keep_current') in ('true', 'True', '1', True)
        
        # Limpa os logs
        success, count = log_manager.clear_logs(keep_current=keep_current)
        
        if success:
            return jsonify({
                'success': True,
                'count': count,
                'message': f'{count} arquivos de log removidos com sucesso'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Erro ao limpar logs'
            })
    except Exception as e:
        logger.error(f"Erro ao limpar logs: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })


@admin_bp.route('/api/system')
def admin_api_system_info():
    """API para obter informações do sistema."""
    try:
        system_monitor = get_system_monitor()
        
        # Obtém informações do sistema
        system_info = system_monitor.get_system_info()
        system_info["cpu"] = system_monitor.get_cpu_info()
        system_info["memory"] = system_monitor.get_memory_info()
        system_info["disk"] = system_monitor.get_disk_info()
        
        return jsonify({
            'success': True,
            'system_info': system_info
        })
    except Exception as e:
        logger.error(f"Erro ao obter informações do sistema: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })


@admin_bp.route('/api/process')
def admin_api_process_info():
    """API para obter informações do processo."""
    try:
        system_monitor = get_system_monitor()
        
        # Obtém informações do processo
        process_info = system_monitor.get_process_info()
        
        return jsonify({
            'success': True,
            'process_info': process_info
        })
    except Exception as e:
        logger.error(f"Erro ao obter informações do processo: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })


@admin_bp.route('/api/logs')
def admin_api_logs_list():
    """API para obter lista de logs."""
    try:
        log_manager = get_log_manager()
        
        # Obtém lista de arquivos de log
        log_files = log_manager.list_log_files()
        
        return jsonify({
            'success': True,
            'log_files': [log.to_dict() for log in log_files]
        })
    except Exception as e:
        logger.error(f"Erro ao listar logs: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })


@admin_bp.route('/api/logs/<filename>')
def admin_api_log_content(filename):
    """API para obter conteúdo de um log."""
    try:
        log_manager = get_log_manager()
        
        # Protege contra path traversal
        filename = secure_filename(filename)
        
        # Obtém conteúdo do log
        log_content = log_manager.read_log_file(filename)
        
        if log_content:
            return jsonify({
                'success': True,
                'log_content': log_content.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Log não encontrado: {filename}'
            })
    except Exception as e:
        logger.error(f"Erro ao obter conteúdo do log: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })