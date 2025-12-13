#!/usr/bin/env python3
"""
Rotas Administrativas para Qdrant Integrado
Novas rotas para monitoramento e upload da estrutura híbrida
"""

from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
import json
import os
from datetime import datetime
import subprocess
import logging

# Blueprint para rotas Qdrant
qdrant_admin_bp = Blueprint('qdrant_admin', __name__, url_prefix='/admin/qdrant')

logger = logging.getLogger(__name__)

@qdrant_admin_bp.route('/monitor')
def monitor_qdrant():
    """Página de monitoramento Qdrant"""
    try:
        # Carregar dados do cache
        cache_file = 'cache/monitoramento_qdrant_rapido.json'
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                dados = json.load(f)
        else:
            # Executar monitoramento se cache não existir
            subprocess.run(['python', 'monitoramento_qdrant_rapido.py'], check=True)
            with open(cache_file, 'r') as f:
                dados = json.load(f)
        
        return render_template('admin/qdrant_monitor.html', dados=dados)
        
    except Exception as e:
        logger.error(f"Erro no monitoramento Qdrant: {e}")
        flash('Erro ao carregar monitoramento Qdrant', 'error')
        return redirect(url_for('admin_dashboard'))

@qdrant_admin_bp.route('/upload')
def upload_qdrant():
    """Página de upload para Qdrant"""
    return render_template('admin/qdrant_upload.html')

@qdrant_admin_bp.route('/sincronizar', methods=['POST'])
def sincronizar_qdrant():
    """Sincroniza PostgreSQL com Qdrant"""
    try:
        # Executar sincronização usando o script de upload
        resultado = subprocess.run(
            ['python', '-c', """
from upload_qdrant_integrado import UploadQdrantIntegrado
uploader = UploadQdrantIntegrado()
resultado = uploader.sincronizar_postgresql_qdrant()
print(f"Sincronizados: {resultado['sincronizados']}, Erros: {resultado['erros']}")
"""],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if resultado.returncode == 0:
            flash('Sincronização iniciada com sucesso', 'success')
        else:
            flash(f'Erro na sincronização: {resultado.stderr}', 'error')
            
    except subprocess.TimeoutExpired:
        flash('Sincronização em andamento (processo longo)', 'info')
    except Exception as e:
        logger.error(f"Erro na sincronização: {e}")
        flash(f'Erro ao sincronizar: {str(e)}', 'error')
    
    return redirect(url_for('qdrant_admin.monitor_qdrant'))

@qdrant_admin_bp.route('/api/status')
def api_status_qdrant():
    """API para status em tempo real do Qdrant"""
    try:
        # Executar monitoramento rápido
        resultado = subprocess.run(
            ['python', 'monitoramento_qdrant_rapido.py'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if resultado.returncode == 0:
            # Carregar dados do cache
            cache_file = 'cache/monitoramento_qdrant_rapido.json'
            with open(cache_file, 'r') as f:
                dados = json.load(f)
            
            return jsonify({
                'success': True,
                'dados': dados,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Erro ao executar monitoramento'
            }), 500
            
    except Exception as e:
        logger.error(f"Erro na API de status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@qdrant_admin_bp.route('/api/upload', methods=['POST'])
def api_upload_qdrant():
    """API para upload de documento para Qdrant"""
    try:
        data = request.json
        titulo = data.get('titulo')
        conteudo = data.get('conteudo')
        area = data.get('area_especializada')
        
        if not all([titulo, conteudo, area]):
            return jsonify({
                'success': False,
                'error': 'Título, conteúdo e área são obrigatórios'
            }), 400
        
        # Executar upload usando script
        script_upload = f"""
from upload_qdrant_integrado import UploadQdrantIntegrado
uploader = UploadQdrantIntegrado()
resultado = uploader.upload_texto_direto(
    "{titulo}", 
    '''{conteudo}''', 
    "{area}"
)
print(f"Sucesso: {{resultado['sucesso']}}, Chunks: {{resultado['chunks_processados']}}")
"""
        
        resultado = subprocess.run(
            ['python', '-c', script_upload],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if resultado.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Upload concluído com sucesso',
                'output': resultado.stdout
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Erro no upload: {resultado.stderr}'
            }), 500
            
    except Exception as e:
        logger.error(f"Erro no upload API: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def registrar_rotas_qdrant_admin(app):
    """Registra as rotas Qdrant no app Flask"""
    app.register_blueprint(qdrant_admin_bp)
    
    # Adicionar rota de monitoramento vetorial atualizada
    @app.route('/admin/monitoring-vectorial-qdrant')
    def admin_monitoring_vectorial_qdrant():
        """Monitoramento vetorial com nova estrutura Qdrant"""
        try:
            # Carregar dados do monitoramento
            cache_file = 'cache/monitoramento_qdrant_rapido.json'
            
            dados = {}
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    dados = json.load(f)
            
            # Dados para compatibilidade com template existente
            vectorial_data = {
                'total_documents': dados.get('postgresql', {}).get('chunks_universal', 0),
                'total_embeddings': dados.get('qdrant', {}).get('vectors', 0),
                'vector_health': dados.get('score_saude', 0),
                'system_status': dados.get('status_geral', 'desconhecido'),
                'qdrant_status': dados.get('qdrant', {}).get('status', 'não_configurado'),
                'sync_percentage': dados.get('sincronizacao', {}).get('percentual', 0),
                'areas_distribution': dados.get('postgresql', {}).get('top_areas', {}),
                'last_update': dados.get('timestamp', datetime.now().isoformat())
            }
            
            return render_template('admin/monitoring_vectorial.html', data=vectorial_data)
            
        except Exception as e:
            logger.error(f"Erro no monitoramento vetorial: {e}")
            flash('Erro ao carregar monitoramento vetorial', 'error')
            return redirect(url_for('admin_dashboard'))
    
    # Atualizar rota de upload manager
    @app.route('/admin/upload-manager')
    def admin_upload_manager_qdrant():
        """Gerenciador de upload com suporte Qdrant"""
        try:
            # Estatísticas para o dashboard
            stats = {
                'total_uploads': 0,
                'recent_uploads': [],
                'storage_usage': 0,
                'vector_health': 0
            }
            
            # Carregar dados do cache se disponível
            cache_file = 'cache/monitoramento_qdrant_rapido.json'
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    dados = json.load(f)
                
                stats.update({
                    'total_uploads': dados.get('postgresql', {}).get('chunks_universal', 0),
                    'vector_health': dados.get('score_saude', 0),
                    'qdrant_status': dados.get('qdrant', {}).get('status', 'não_configurado')
                })
            
            return render_template('admin/upload_manager.html', stats=stats)
            
        except Exception as e:
            logger.error(f"Erro no upload manager: {e}")
            flash('Erro ao carregar gerenciador de upload', 'error')
            return redirect(url_for('admin_dashboard'))

if __name__ == "__main__":
    print("Rotas Qdrant Admin configuradas")
    print("Endpoints disponíveis:")
    print("- /admin/qdrant/monitor")
    print("- /admin/qdrant/upload") 
    print("- /admin/qdrant/sincronizar")
    print("- /admin/qdrant/api/status")
    print("- /admin/qdrant/api/upload")