"""
Blueprint para administração de banco de dados.
Fornece interface completa para gerenciar bancos locais e Neon.
"""
import os
import datetime
from flask import Blueprint, request, jsonify, render_template, Response
from flask_login import current_user, login_required
from sqlalchemy import inspect, text
from main import db
from models import DatabaseJob, SystemSetting, AuditLog
from utils.permission_decorators import admin_required

# Criar Blueprint
admin_database_bp = Blueprint('admin_database', __name__, url_prefix='/admin/database')


def get_db_type():
    """Retorna o tipo de banco de dados ativo"""
    use_local = os.environ.get('USE_LOCAL_DB', 'false').lower() == 'true'
    
    if use_local:
        local_db_type = os.environ.get('LOCAL_DB_TYPE', 'sqlite').lower()
        if local_db_type in ('postgres', 'postgresql'):
            return 'postgres_local'
        else:
            return 'sqlite_local'
    else:
        return 'neon'


# ============================================================================
# ROTAS DE PÁGINA
# ============================================================================

@admin_database_bp.route('/')
@login_required
@admin_required
def index():
    """Página principal de administração de banco de dados"""
    return render_template('admin/database.html')


# ============================================================================
# API - STATUS
# ============================================================================

@admin_database_bp.route('/api/status', methods=['GET'])
@login_required
@admin_required
def get_status():
    """
    Retorna status completo de todos os bancos de dados.
    
    Returns:
        JSON com informações sobre bancos ativos, configurações e estatísticas
    """
    try:
        from utils.db_helpers import (
            get_active_db_info,
            get_neon_db_info,
            get_local_db_info,
            get_database_stats
        )
        
        # Banco ativo
        active_db = get_active_db_info()
        
        # Informações dos bancos
        neon_info = get_neon_db_info()
        local_info = get_local_db_info()
        
        # Estatísticas do banco ativo
        stats = get_database_stats()
        
        # Jobs recentes
        recent_jobs = DatabaseJob.query.order_by(
            DatabaseJob.started_at.desc()
        ).limit(10).all()
        
        return jsonify({
            'success': True,
            'active_db': active_db,
            'databases': {
                'neon': neon_info,
                'local': local_info
            },
            'stats': stats,
            'recent_jobs': [job.to_dict() for job in recent_jobs]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# API - CONFIGURAÇÃO
# ============================================================================

@admin_database_bp.route('/api/config', methods=['GET'])
@login_required
@admin_required
def get_config():
    """Retorna configurações atuais de banco de dados"""
    try:
        # Configurações do sistema
        config_keys = [
            'db_mode',
            'local_db_type',
            'local_db_path',
            'local_pg_host',
            'local_pg_port',
            'local_pg_database',
            'local_pg_user'
        ]
        
        configs = {}
        for key in config_keys:
            setting = SystemSetting.query.filter_by(key=key).first()
            if setting:
                configs[key] = setting.to_dict(mask_sensitive=True)
        
        # Variáveis de ambiente atuais
        env_vars = {
            'USE_LOCAL_DB': os.environ.get('USE_LOCAL_DB', 'false'),
            'LOCAL_DB_TYPE': os.environ.get('LOCAL_DB_TYPE', 'sqlite'),
            'DATABASE_URL_SET': bool(os.environ.get('DATABASE_URL')),
            'DB_TYPE': get_db_type()
        }
        
        return jsonify({
            'success': True,
            'config': configs,
            'env_vars': env_vars
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_database_bp.route('/api/config', methods=['PUT'])
@login_required
@admin_required
def update_config():
    """
    Atualiza configurações de banco de dados.
    Não aplica diretamente, apenas salva para próximo restart.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Nenhum dado fornecido'
            }), 400
        
        # Validar dados
        valid_keys = [
            'db_mode', 'local_db_type', 'local_db_path',
            'local_pg_host', 'local_pg_port', 'local_pg_database',
            'local_pg_user', 'local_pg_password'
        ]
        
        updated_settings = []
        
        for key, value in data.items():
            if key not in valid_keys:
                continue
            
            # Determinar se é sensível
            is_sensitive = 'password' in key.lower()
            
            # Salvar configuração
            setting = SystemSetting.set_value(
                key=key,
                value=value,
                user_id=current_user.id,
                category='database',
                description=f'Configuração de {key}',
            )
            
            if is_sensitive:
                setting.is_sensitive = True
                db.session.commit()
            
            updated_settings.append(key)
        
        # Log de auditoria
        audit = AuditLog(
            user_id=current_user.id,
            action='update_database_config',
            entity_type='system_setting',
            details=f'Configurações atualizadas: {", ".join(updated_settings)}',
            ip_address=request.remote_addr
        )
        db.session.add(audit)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'updated_settings': updated_settings,
            'message': 'Configurações salvas. Reinicie a aplicação para aplicar.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# API - SINCRONIZAÇÃO
# ============================================================================

@admin_database_bp.route('/api/sync', methods=['POST'])
@login_required
@admin_required
def sync_database():
    """
    Inicia sincronização orquestrada Neon → PostgreSQL → SQLite.
    Executa sequencialmente para evitar sobrecarga.
    """
    try:
        # Verificar se há sincronização em andamento (com timeout de 10 minutos)
        import datetime
        timeout_threshold = datetime.datetime.now() - datetime.timedelta(minutes=10)
        
        running_job = DatabaseJob.query.filter(
            DatabaseJob.type == 'sync',
            DatabaseJob.status == 'running',
            DatabaseJob.started_at > timeout_threshold  # Apenas jobs recentes
        ).first()
        
        if running_job:
            return jsonify({
                'success': False,
                'error': 'Já existe uma sincronização em andamento',
                'running_job_id': running_job.id
            }), 409
        
        # Limpar jobs travados (mais de 10 minutos em "running")
        stalled_jobs = DatabaseJob.query.filter(
            DatabaseJob.type == 'sync',
            DatabaseJob.status == 'running',
            DatabaseJob.started_at <= timeout_threshold
        ).all()
        
        for stalled_job in stalled_jobs:
            stalled_job.status = 'failed'
            stalled_job.error_message = 'Job timeout - travado por mais de 10 minutos'
            stalled_job.add_log('Job marcado como failed devido a timeout', 'error')
        
        if stalled_jobs:
            db.session.commit()
        
        data = request.get_json() or {}
        
        # URLs dos bancos
        neon_url = os.environ.get('DATABASE_URL')
        
        # PostgreSQL Local
        from init_local_db import get_postgres_connection_params
        params = get_postgres_connection_params()
        postgres_url = f"postgresql://{params['user']}:{params['password']}@{params['host']}:{params['port']}/{params['database']}"
        
        # SQLite Local
        sqlite_path = os.environ.get('LOCAL_DB_PATH', 'local_legal_pro.db')
        
        # Criar job orquestrado
        job = DatabaseJob(
            type='sync',
            source_db='neon',
            target_db='postgres_and_sqlite',
            created_by_id=current_user.id,
            logs=[]
        )
        db.session.add(job)
        db.session.commit()
        
        # Executar task orquestrada
        from tasks.background_executor import BackgroundExecutor
        
        thread = BackgroundExecutor.run_task_in_background(
            'tasks.database_ops',
            'sync_orchestrated_task',
            job.id, neon_url, postgres_url, sqlite_path
        )
        job.celery_task_id = f'bg_thread_{thread.ident}'
        db.session.commit()
        
        # Log de auditoria
        audit = AuditLog(
            user_id=current_user.id,
            action='start_database_sync',
            entity_type='database_job',
            entity_id=str(job.id),
            details='Iniciou sincronização orquestrada: Neon → PostgreSQL → SQLite',
            ip_address=request.remote_addr
        )
        db.session.add(audit)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'job_id': job.id,
            'message': 'Sincronização orquestrada iniciada (PostgreSQL primeiro, depois SQLite)'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_database_bp.route('/api/sync/<int:job_id>', methods=['GET'])
@login_required
@admin_required
def get_sync_status(job_id):
    """Consulta status de uma sincronização"""
    try:
        job = DatabaseJob.query.get(job_id)
        
        if not job:
            return jsonify({
                'success': False,
                'error': 'Job não encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'job': job.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# API - BACKUP/RESTORE
# ============================================================================

@admin_database_bp.route('/api/backup', methods=['POST'])
@login_required
@admin_required
def backup_database():
    """Cria backup do banco de dados"""
    try:
        data = request.get_json() or {}
        source_db = data.get('source_db', 'active')
        
        # Determinar qual banco fazer backup
        if source_db == 'active':
            active_db_type = get_db_type()
            if active_db_type == 'neon':
                db_url = os.environ.get('DATABASE_URL')
                db_type = 'neon'
            elif active_db_type == 'postgres_local':
                from init_local_db import get_postgres_connection_params
                params = get_postgres_connection_params()
                db_url = f"postgresql://{params['user']}:{params['password']}@{params['host']}:{params['port']}/{params['database']}"
                db_type = 'postgres_local'
            else:
                db_url = os.environ.get('LOCAL_DB_PATH', 'local_legal_pro.db')
                db_type = 'sqlite_local'
        
        # Criar job
        job = DatabaseJob(
            type='backup',
            source_db=db_type,
            created_by_id=current_user.id,
            logs=[]
        )
        db.session.add(job)
        db.session.commit()
        
        # Nome do arquivo de backup
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f'/tmp/legal_pro_backup_{db_type}_{timestamp}.sql'
        
        # Importar e executar task
        from tasks.database_ops import CELERY_AVAILABLE
        from tasks.background_executor import BackgroundExecutor
        
        if CELERY_AVAILABLE:
            from tasks.database_ops import backup_database as backup_task
            task = backup_task.delay(job.id, db_url, output_path)
            job.celery_task_id = task.id
        else:
            # Executar em thread separada (não bloqueia worker do Gunicorn)
            thread = BackgroundExecutor.run_task_in_background(
                'tasks.database_ops',
                'backup_database_task',
                job.id, db_url, output_path
            )
            job.celery_task_id = f'bg_thread_{thread.ident}'
        
        db.session.commit()
        
        # Log de auditoria
        audit = AuditLog(
            user_id=current_user.id,
            action='start_database_backup',
            entity_type='database_job',
            entity_id=str(job.id),
            details=f'Iniciou backup de {db_type}',
            ip_address=request.remote_addr
        )
        db.session.add(audit)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'job_id': job.id,
            'output_path': output_path,
            'message': 'Backup iniciado'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# API - INICIALIZAÇÃO
# ============================================================================

@admin_database_bp.route('/api/init', methods=['POST'])
@login_required
@admin_required
def init_database():
    """Inicializa banco de dados local"""
    try:
        data = request.get_json() or {}
        db_type = data.get('db_type', 'sqlite')
        
        # Criar job
        job = DatabaseJob(
            type='init',
            target_db=f'{db_type}_local',
            created_by_id=current_user.id,
            logs=[]
        )
        db.session.add(job)
        db.session.commit()
        
        # Importar e executar task
        from tasks.database_ops import CELERY_AVAILABLE
        from tasks.background_executor import BackgroundExecutor
        
        if CELERY_AVAILABLE:
            from tasks.database_ops import init_database as init_task
            task = init_task.delay(job.id, db_type)
            job.celery_task_id = task.id
        else:
            # Executar em thread separada (não bloqueia worker do Gunicorn)
            thread = BackgroundExecutor.run_task_in_background(
                'tasks.database_ops',
                'init_database_task',
                job.id, db_type
            )
            job.celery_task_id = f'bg_thread_{thread.ident}'
        
        db.session.commit()
        
        # Log de auditoria
        audit = AuditLog(
            user_id=current_user.id,
            action='init_local_database',
            entity_type='database_job',
            entity_id=str(job.id),
            details=f'Iniciou inicialização de banco {db_type}',
            ip_address=request.remote_addr
        )
        db.session.add(audit)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'job_id': job.id,
            'message': 'Inicialização iniciada'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# API - TESTE DE CONEXÃO
# ============================================================================

@admin_database_bp.route('/api/test-connection', methods=['POST'])
@login_required
@admin_required
def test_connection():
    """Testa conexão com banco de dados"""
    try:
        data = request.get_json()
        
        if not data or 'db_url' not in data:
            return jsonify({
                'success': False,
                'error': 'URL do banco não fornecida'
            }), 400
        
        db_url = data['db_url']
        db_type = data.get('db_type', 'unknown')
        
        # Criar job
        job = DatabaseJob(
            type='test',
            target_db=db_type,
            created_by_id=current_user.id,
            logs=[]
        )
        db.session.add(job)
        db.session.commit()
        
        # Importar e executar task
        from tasks.database_ops import CELERY_AVAILABLE
        from tasks.background_executor import BackgroundExecutor
        
        if CELERY_AVAILABLE:
            from tasks.database_ops import test_connection as test_task
            task = test_task.delay(job.id, db_url, db_type)
            job.celery_task_id = task.id
        else:
            # Executar em thread separada (não bloqueia worker do Gunicorn)
            thread = BackgroundExecutor.run_task_in_background(
                'tasks.database_ops',
                'test_connection_task',
                job.id, db_url, db_type
            )
            job.celery_task_id = f'bg_thread_{thread.ident}'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'job_id': job.id,
            'message': 'Teste de conexão iniciado'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# API - HISTÓRICO
# ============================================================================

@admin_database_bp.route('/api/history', methods=['GET'])
@login_required
@admin_required
def get_history():
    """Retorna histórico de operações"""
    try:
        # Parâmetros de paginação
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        job_type = request.args.get('type')
        
        # Query base
        query = DatabaseJob.query
        
        # Filtrar por tipo se fornecido
        if job_type:
            query = query.filter_by(type=job_type)
        
        # Ordenar por data (mais recentes primeiro)
        query = query.order_by(DatabaseJob.started_at.desc())
        
        # Paginar
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'jobs': [job.to_dict() for job in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# API - SERVER-SENT EVENTS (SSE) PARA PROGRESSO
# ============================================================================

@admin_database_bp.route('/api/events/<int:job_id>')
@login_required
@admin_required
def stream_job_progress(job_id):
    """
    Stream de eventos Server-Sent Events para acompanhar progresso.
    Cliente mantém conexão aberta e recebe atualizações em tempo real.
    """
    def generate():
        import time
        
        # Enviar header de SSE
        yield 'retry: 1000\n\n'
        
        last_progress = -1
        last_status = None
        max_attempts = 300  # 5 minutos (1 segundo por tentativa)
        attempts = 0
        
        while attempts < max_attempts:
            try:
                job = DatabaseJob.query.get(job_id)
                
                if not job:
                    yield f'event: error\ndata: {{"error": "Job não encontrado"}}\n\n'
                    break
                
                # Verificar se houve mudança
                if job.progress != last_progress or job.status != last_status:
                    data = job.to_dict()
                    yield f'event: progress\ndata: {jsonify(data).get_data(as_text=True)}\n\n'
                    
                    last_progress = job.progress
                    last_status = job.status
                
                # Se job terminou (success, failed, cancelled), encerrar stream
                if job.status in ('success', 'failed', 'cancelled'):
                    yield f'event: completed\ndata: {jsonify(data).get_data(as_text=True)}\n\n'
                    break
                
                time.sleep(1)
                attempts += 1
                
            except Exception as e:
                yield f'event: error\ndata: {{"error": "{str(e)}"}}\n\n'
                break
        
        # Timeout
        if attempts >= max_attempts:
            yield f'event: timeout\ndata: {{"message": "Timeout aguardando conclusão"}}\n\n'
    
    return Response(generate(), mimetype='text/event-stream')
