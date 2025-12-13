"""
Celery tasks para operações de banco de dados.
Executa operações longas de forma assíncrona com rastreamento de progresso.
"""
import os
import time
import datetime
import subprocess
from pathlib import Path

# Configuração do Celery (importar de onde estiver configurado no projeto)
try:
    from celery import Celery, current_task
    
    # Celery deve estar configurado em outro lugar do projeto
    # Vamos apenas criar uma instância simples ou importar a existente
    celery_app = Celery('legal_pro', broker='redis://localhost:6379/0')
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    celery_app = None


def update_job_progress(job_id, progress, message, level='info'):
    """
    Atualiza o progresso de um DatabaseJob.
    Thread-safe para uso em tasks assíncronas.
    """
    from main import db
    from models import DatabaseJob
    
    try:
        job = DatabaseJob.query.get(job_id)
        if job:
            job.progress = progress
            job.add_log(message, level)
            
            # Se chegou a 100%, marcar como concluído
            if progress >= 100:
                job.status = 'success'
                job.completed_at = datetime.datetime.now()
                if job.started_at:
                    duration = (job.completed_at - job.started_at).total_seconds()
                    job.duration_seconds = int(duration)
            
            db.session.commit()
    except Exception as e:
        print(f"Erro ao atualizar progresso do job {job_id}: {e}")


def set_job_error(job_id, error_message):
    """Define um job como failed com mensagem de erro"""
    from main import db
    from models import DatabaseJob
    
    try:
        job = DatabaseJob.query.get(job_id)
        if job:
            job.status = 'failed'
            job.error_message = error_message
            job.completed_at = datetime.datetime.now()
            job.add_log(f"Erro: {error_message}", 'error')
            
            if job.started_at:
                duration = (job.completed_at - job.started_at).total_seconds()
                job.duration_seconds = int(duration)
            
            db.session.commit()
    except Exception as e:
        print(f"Erro ao marcar job {job_id} como failed: {e}")


def sync_orchestrated_task(job_id, neon_url, local_postgres_url, local_sqlite_path):
    """
    Task orquestrada: Sincroniza Neon → PostgreSQL primeiro, depois Neon → SQLite.
    Evita sobrecarga do sistema executando sequencialmente.
    
    Progresso mapeado:
    - 0-60%: PostgreSQL sync
    - 60-100%: SQLite sync
    """
    from main import db
    from models import DatabaseJob
    from sqlalchemy import create_engine, inspect, text
    import json
    
    try:
        # Marcar job como running
        job = DatabaseJob.query.get(job_id)
        if job:
            job.status = 'running'
            job.started_at = datetime.datetime.now()
            db.session.commit()
        
        update_job_progress(job_id, 0, "Iniciando sincronização orquestrada Neon → PostgreSQL → SQLite")
        
        # ETAPA 1: Sincronizar Neon → PostgreSQL (0-60%)
        update_job_progress(job_id, 5, "ETAPA 1/2: Sincronizando Neon → PostgreSQL Local...")
        
        # Executar sync PostgreSQL
        dump_file = f'/tmp/legal_pro_sync_{job_id}.sql'
        
        update_job_progress(job_id, 10, "Criando dump do banco Neon...")
        
        # pg_dump do Neon
        dump_cmd = [
            'pg_dump',
            '--clean',
            '--if-exists',
            '--no-owner',
            '--no-acl',
            '-f', dump_file,
            neon_url
        ]
        
        result = subprocess.run(dump_cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            set_job_error(job_id, f"Erro ao criar dump PostgreSQL: {result.stderr}")
            return
        
        dump_size_mb = Path(dump_file).stat().st_size / (1024 * 1024)
        update_job_progress(job_id, 30, f"Dump PostgreSQL criado ({dump_size_mb:.2f} MB)")
        
        update_job_progress(job_id, 40, "Restaurando dump no PostgreSQL local...")
        
        # Restaurar no PostgreSQL local
        restore_cmd = [
            'psql',
            '-v', 'ON_ERROR_STOP=0',
            '-f', dump_file,
            local_postgres_url
        ]
        
        result = subprocess.run(restore_cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0 and 'ERROR' in result.stderr:
            update_job_progress(job_id, 50, f"Avisos durante restore PostgreSQL: {result.stderr[:200]}", 'warning')
        
        # Limpar dump
        try:
            os.remove(dump_file)
        except:
            pass
        
        update_job_progress(job_id, 60, "✅ ETAPA 1/2 CONCLUÍDA: PostgreSQL sincronizado com sucesso!")
        
        # ETAPA 2: Sincronizar Neon → SQLite (60-100%)
        update_job_progress(job_id, 62, "ETAPA 2/2: Sincronizando Neon → SQLite Local...")
        
        # Usar modelos ORM do projeto (compatíveis com SQLite)
        from main import app
        
        # Criar engines
        neon_engine = create_engine(neon_url)
        sqlite_engine = create_engine(f'sqlite:///{local_sqlite_path}')
        
        # Criar tabelas no SQLite usando modelos ORM do projeto
        with app.app_context():
            # Importar Base do SQLAlchemy
            from models import db
            
            # Criar todas as tabelas usando metadata do ORM
            db.metadata.create_all(sqlite_engine)
        
        # Obter lista de tabelas
        inspector = inspect(neon_engine)
        tables = inspector.get_table_names()
        total_tables = len(tables)
        
        update_job_progress(job_id, 65, f"Sincronizando {total_tables} tabelas para SQLite...")
        
        for i, table_name in enumerate(tables):
            # Mapear progresso de 65% a 95%
            progress = 65 + int((i / total_tables) * 30)
            
            try:
                # Ler dados do Neon via SQL puro
                with neon_engine.connect() as neon_conn:
                    # Obter colunas da tabela
                    columns = inspector.get_columns(table_name)
                    col_names = [col['name'] for col in columns]
                    
                    # Query simples
                    query = f"SELECT * FROM {table_name}"
                    result = neon_conn.execute(text(query))
                    rows = result.fetchall()
                
                if rows:
                    # Preparar dados para SQLite (converter tipos incompatíveis)
                    processed_rows = []
                    for row in rows:
                        row_dict = {}
                        for idx, col_name in enumerate(col_names):
                            value = row[idx]
                            # Converter arrays PostgreSQL para JSON strings
                            if isinstance(value, list):
                                value = json.dumps(value)
                            row_dict[col_name] = value
                        processed_rows.append(row_dict)
                    
                    # Inserir no SQLite com transação
                    with sqlite_engine.begin() as sqlite_conn:
                        # Limpar tabela
                        sqlite_conn.execute(text(f"DELETE FROM {table_name}"))
                        
                        # Inserir dados
                        if processed_rows:
                            # Construir insert statement
                            placeholders = ', '.join([f":{col}" for col in col_names])
                            insert_sql = f"INSERT INTO {table_name} ({', '.join(col_names)}) VALUES ({placeholders})"
                            
                            for row_data in processed_rows:
                                sqlite_conn.execute(text(insert_sql), row_data)
                    
                    update_job_progress(job_id, progress, f"✓ Tabela '{table_name}' sincronizada ({len(rows)} registros)")
                else:
                    update_job_progress(job_id, progress, f"Tabela '{table_name}' vazia")
                    
            except Exception as e:
                # Log erro mas continua
                update_job_progress(job_id, progress, f"⚠️ Erro em '{table_name}': {str(e)[:100]}", 'warning')
        
        update_job_progress(job_id, 100, "✅ SINCRONIZAÇÃO COMPLETA: PostgreSQL e SQLite atualizados!")
        
    except Exception as e:
        set_job_error(job_id, f"Erro na sincronização orquestrada: {str(e)}")
        raise


def sync_postgres_to_postgres_task(job_id, neon_url, local_url):
    """
    Task para sincronizar PostgreSQL → PostgreSQL usando pg_dump/restore.
    Altamente eficiente.
    """
    from main import db
    from models import DatabaseJob
    
    try:
        # Marcar como running
        job = DatabaseJob.query.get(job_id)
        if job:
            job.status = 'running'
            job.started_at = datetime.datetime.now()
            if current_task:
                job.celery_task_id = current_task.request.id
            db.session.commit()
        
        update_job_progress(job_id, 10, "Iniciando sincronização PostgreSQL → PostgreSQL")
        
        # Arquivo temporário para dump
        dump_file = f'/tmp/legal_pro_sync_{job_id}.sql'
        
        update_job_progress(job_id, 20, "Criando dump do banco Neon...")
        
        # pg_dump do Neon
        dump_cmd = [
            'pg_dump',
            '--clean',  # Incluir comandos DROP
            '--if-exists',  # Evitar erros se tabelas não existirem
            '--no-owner',  # Não incluir comandos de ownership
            '--no-acl',  # Não incluir comandos de privilégios
            '-f', dump_file,
            neon_url
        ]
        
        result = subprocess.run(dump_cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            set_job_error(job_id, f"Erro ao criar dump: {result.stderr}")
            return
        
        # Verificar tamanho do dump
        dump_size_mb = Path(dump_file).stat().st_size / (1024 * 1024)
        update_job_progress(job_id, 50, f"Dump criado com sucesso ({dump_size_mb:.2f} MB)")
        
        update_job_progress(job_id, 60, "Restaurando dump no banco local...")
        
        # psql para restaurar
        restore_cmd = [
            'psql',
            '-v', 'ON_ERROR_STOP=0',  # Continuar em caso de erros não-críticos
            '-f', dump_file,
            local_url
        ]
        
        result = subprocess.run(restore_cmd, capture_output=True, text=True, timeout=300)
        
        update_job_progress(job_id, 90, "Restauração concluída")
        
        # Remover arquivo temporário
        if Path(dump_file).exists():
            os.remove(dump_file)
        
        # Dados do resultado
        job = DatabaseJob.query.get(job_id)
        if job:
            job.result_data = {
                'dump_size_mb': round(dump_size_mb, 2),
                'method': 'pg_dump/psql',
                'warnings': result.stderr if result.stderr else None
            }
            db.session.commit()
        
        update_job_progress(job_id, 100, "Sincronização PostgreSQL concluída com sucesso!")
        
    except subprocess.TimeoutExpired:
        set_job_error(job_id, "Timeout durante sincronização (limite: 5 minutos)")
    except FileNotFoundError:
        set_job_error(job_id, "pg_dump ou psql não encontrado. Instale PostgreSQL client tools.")
    except Exception as e:
        set_job_error(job_id, f"Erro inesperado: {str(e)}")


def sync_neon_to_sqlite_task(job_id, neon_url, local_db_path):
    """
    Task para sincronizar Neon → SQLite usando sincronização linha por linha.
    Menos eficiente, mas funcional para SQLite.
    """
    from main import db
    from models import DatabaseJob
    from sqlalchemy import create_engine, MetaData, select
    
    try:
        # Marcar como running
        job = DatabaseJob.query.get(job_id)
        if job:
            job.status = 'running'
            if current_task:
                job.celery_task_id = current_task.request.id
            db.session.commit()
        
        update_job_progress(job_id, 10, "Iniciando sincronização Neon → SQLite")
        
        # Engines
        neon_engine = create_engine(neon_url)
        local_url = f"sqlite:///{local_db_path}"
        local_engine = create_engine(local_url)
        
        neon_meta = MetaData()
        neon_meta.reflect(bind=neon_engine)
        
        local_meta = MetaData()
        local_meta.reflect(bind=local_engine)
        
        # Tabelas a sincronizar
        tables_to_sync = [
            'role',
            'categoria_assistente',
            'user',
            'assistente_juridico',
            'template_juridico'
        ]
        
        total_tables = len(tables_to_sync)
        total_synced = 0
        
        update_job_progress(job_id, 20, f"Sincronizando {total_tables} tabelas...")
        
        with local_engine.begin() as local_conn:
            for idx, table_name in enumerate(tables_to_sync):
                progress = 20 + int((idx / total_tables) * 70)
                
                if table_name not in neon_meta.tables or table_name not in local_meta.tables:
                    update_job_progress(job_id, progress, f"Pulando {table_name} (não existe)", 'warning')
                    continue
                
                update_job_progress(job_id, progress, f"Sincronizando {table_name}...")
                
                table = neon_meta.tables[table_name]
                
                # Buscar dados do Neon
                with neon_engine.connect() as neon_conn:
                    neon_result = neon_conn.execute(select(table))
                    neon_rows = neon_result.fetchall()
                
                if not neon_rows:
                    update_job_progress(job_id, progress, f"{table_name}: Nenhum registro", 'info')
                    continue
                
                # Limpar tabela local
                local_conn.execute(local_meta.tables[table_name].delete())
                
                # Inserir dados
                column_names = table.columns.keys()
                data_to_insert = []
                
                for row in neon_rows:
                    row_dict = {col: row[i] for i, col in enumerate(column_names)}
                    data_to_insert.append(row_dict)
                
                if data_to_insert:
                    local_conn.execute(
                        local_meta.tables[table_name].insert(),
                        data_to_insert
                    )
                    total_synced += len(data_to_insert)
                    update_job_progress(job_id, progress, f"{table_name}: {len(data_to_insert)} registros sincronizados")
        
        # Dados do resultado
        job = DatabaseJob.query.get(job_id)
        if job:
            job.result_data = {
                'total_records': total_synced,
                'tables_synced': total_tables,
                'method': 'row-by-row'
            }
            db.session.commit()
        
        update_job_progress(job_id, 100, f"Sincronização concluída! {total_synced} registros sincronizados")
        
    except Exception as e:
        set_job_error(job_id, f"Erro durante sincronização: {str(e)}")


def init_database_task(job_id, db_type):
    """
    Task para inicializar banco de dados local.
    """
    from main import create_app, db as flask_db
    from models import DatabaseJob, User
    from werkzeug.security import generate_password_hash
    
    try:
        # Marcar como running
        job = DatabaseJob.query.get(job_id)
        if job:
            job.status = 'running'
            if current_task:
                job.celery_task_id = current_task.request.id
            flask_db.session.commit()
        
        update_job_progress(job_id, 10, f"Inicializando banco de dados {db_type}...")
        
        # Configurar variável de ambiente
        os.environ['USE_LOCAL_DB'] = 'true'
        if db_type == 'postgres':
            os.environ['LOCAL_DB_TYPE'] = 'postgres'
        else:
            os.environ['LOCAL_DB_TYPE'] = 'sqlite'
        
        update_job_progress(job_id, 30, "Criando estrutura do banco de dados...")
        
        # Criar app context
        app = create_app()
        
        with app.app_context():
            # Criar todas as tabelas
            flask_db.create_all()
            
            update_job_progress(job_id, 60, "Estrutura criada. Verificando usuário admin...")
            
            # Verificar usuário admin
            admin_user = User.query.filter_by(username='admin').first()
            
            if not admin_user:
                update_job_progress(job_id, 70, "Criando usuário admin padrão...")
                
                admin = User(
                    username='admin',
                    email='admin@legalpro.com',
                    password_hash=generate_password_hash('admin123'),
                    is_admin=True,
                    active=True
                )
                flask_db.session.add(admin)
                flask_db.session.commit()
                
                update_job_progress(job_id, 80, "Usuário admin criado (username: admin, senha: admin123)")
            else:
                update_job_progress(job_id, 80, "Usuário admin já existe")
            
            # Estatísticas
            total_users = User.query.count()
            
            # Dados do resultado
            job = DatabaseJob.query.get(job_id)
            if job:
                job.result_data = {
                    'db_type': db_type,
                    'total_users': total_users,
                    'admin_created': not bool(admin_user)
                }
                flask_db.session.commit()
            
            update_job_progress(job_id, 100, f"Banco de dados inicializado com sucesso! {total_users} usuários")
        
    except Exception as e:
        set_job_error(job_id, f"Erro durante inicialização: {str(e)}")


def backup_database_task(job_id, source_db, output_path):
    """
    Task para criar backup de banco de dados.
    """
    from main import db
    from models import DatabaseJob
    
    try:
        # Marcar como running
        job = DatabaseJob.query.get(job_id)
        if job:
            job.status = 'running'
            if current_task:
                job.celery_task_id = current_task.request.id
            db.session.commit()
        
        update_job_progress(job_id, 10, f"Criando backup de {source_db}...")
        
        if 'postgresql' in source_db.lower():
            # Backup PostgreSQL
            update_job_progress(job_id, 30, "Executando pg_dump...")
            
            dump_cmd = [
                'pg_dump',
                '--clean',
                '--if-exists',
                '--no-owner',
                '--no-acl',
                '-f', output_path,
                source_db
            ]
            
            result = subprocess.run(dump_cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                set_job_error(job_id, f"Erro ao criar backup: {result.stderr}")
                return
            
            backup_size_mb = Path(output_path).stat().st_size / (1024 * 1024)
            
            # Dados do resultado
            job = DatabaseJob.query.get(job_id)
            if job:
                job.result_data = {
                    'backup_file': output_path,
                    'backup_size_mb': round(backup_size_mb, 2),
                    'method': 'pg_dump'
                }
                db.session.commit()
            
            update_job_progress(job_id, 100, f"Backup criado com sucesso ({backup_size_mb:.2f} MB)")
        
        elif 'sqlite' in source_db.lower():
            # Backup SQLite (copiar arquivo)
            import shutil
            
            update_job_progress(job_id, 50, "Copiando arquivo SQLite...")
            
            shutil.copy2(source_db, output_path)
            
            backup_size_mb = Path(output_path).stat().st_size / (1024 * 1024)
            
            # Dados do resultado
            job = DatabaseJob.query.get(job_id)
            if job:
                job.result_data = {
                    'backup_file': output_path,
                    'backup_size_mb': round(backup_size_mb, 2),
                    'method': 'file_copy'
                }
                db.session.commit()
            
            update_job_progress(job_id, 100, f"Backup SQLite criado ({backup_size_mb:.2f} MB)")
        
        else:
            set_job_error(job_id, f"Tipo de banco não suportado: {source_db}")
        
    except subprocess.TimeoutExpired:
        set_job_error(job_id, "Timeout durante backup (limite: 5 minutos)")
    except FileNotFoundError:
        set_job_error(job_id, "Comando de backup não encontrado (pg_dump)")
    except Exception as e:
        set_job_error(job_id, f"Erro inesperado: {str(e)}")


def test_connection_task(job_id, db_url, db_type):
    """
    Task para testar conexão com banco de dados.
    """
    from main import db
    from models import DatabaseJob
    from sqlalchemy import create_engine, text
    
    try:
        # Marcar como running
        job = DatabaseJob.query.get(job_id)
        if job:
            job.status = 'running'
            if current_task:
                job.celery_task_id = current_task.request.id
            db.session.commit()
        
        update_job_progress(job_id, 20, f"Testando conexão com {db_type}...")
        
        # Criar engine
        engine = create_engine(db_url)
        
        update_job_progress(job_id, 50, "Executando teste de conexão...")
        
        # Testar conexão
        with engine.connect() as conn:
            if 'postgresql' in db_type.lower():
                result = conn.execute(text("SELECT version()"))
                version = result.scalar()
                update_job_progress(job_id, 70, f"PostgreSQL versão: {version[:50]}...")
            elif 'sqlite' in db_type.lower():
                result = conn.execute(text("SELECT sqlite_version()"))
                version = result.scalar()
                update_job_progress(job_id, 70, f"SQLite versão: {version}")
        
        # Dados do resultado
        job = DatabaseJob.query.get(job_id)
        if job:
            job.result_data = {
                'db_type': db_type,
                'connection_successful': True,
                'version': version if 'version' in locals() else None
            }
            db.session.commit()
        
        update_job_progress(job_id, 100, "Conexão testada com sucesso!")
        
    except Exception as e:
        set_job_error(job_id, f"Erro ao testar conexão: {str(e)}")


# Wrappers Celery (se disponível)
if CELERY_AVAILABLE and celery_app:
    sync_postgres_to_postgres = celery_app.task(sync_postgres_to_postgres_task)
    sync_neon_to_sqlite = celery_app.task(sync_neon_to_sqlite_task)
    init_database = celery_app.task(init_database_task)
    backup_database = celery_app.task(backup_database_task)
    test_connection = celery_app.task(test_connection_task)
else:
    # Fallback sem Celery - execução síncrona
    sync_postgres_to_postgres = sync_postgres_to_postgres_task
    sync_neon_to_sqlite = sync_neon_to_sqlite_task
    init_database = init_database_task
    backup_database = backup_database_task
    test_connection = test_connection_task
