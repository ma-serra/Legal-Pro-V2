"""
Helpers para obter métricas e informações de bancos de dados.
Fornece estatísticas sobre tamanho, tabelas, registros, etc.
"""
import os
from pathlib import Path
from sqlalchemy import create_engine, inspect, text


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


def get_active_db_info():
    """
    Retorna informações sobre o banco de dados ativo.
    
    Returns:
        dict: Informações do banco ativo (tipo, host, status, etc)
    """
    db_type = get_db_type()
    
    info = {
        'type': db_type,
        'is_local': db_type in ('sqlite_local', 'postgres_local'),
        'is_cloud': db_type == 'neon'
    }
    
    if db_type == 'neon':
        db_url = os.environ.get('DATABASE_URL', '')
        if '@' in db_url:
            # Extrair host sem expor senha
            host_part = db_url.split('@')[1].split('/')[0]
            info['host'] = host_part
            info['connection_string'] = f"postgresql://***@{host_part}/***"
        else:
            info['host'] = 'Unknown'
            info['connection_string'] = 'Not configured'
    
    elif db_type == 'postgres_local':
        from init_local_db import get_postgres_connection_params
        params = get_postgres_connection_params()
        info['host'] = f"{params['host']}:{params['port']}"
        info['database'] = params['database']
        info['user'] = params['user']
        info['connection_string'] = f"postgresql://{params['user']}@{params['host']}:{params['port']}/{params['database']}"
    
    elif db_type == 'sqlite_local':
        db_path = os.environ.get('LOCAL_DB_PATH', 'local_legal_pro.db')
        info['path'] = db_path
        info['absolute_path'] = str(Path(db_path).absolute())
        info['connection_string'] = f"sqlite:///{db_path}"
    
    return info


def get_neon_db_info():
    """
    Retorna informações sobre o banco Neon (se configurado).
    
    Returns:
        dict: Informações do banco Neon
    """
    neon_url = os.environ.get('DATABASE_URL')
    
    if not neon_url:
        return {
            'configured': False,
            'status': 'not_configured'
        }
    
    info = {
        'configured': True,
        'type': 'neon',
        'provider': 'Neon PostgreSQL'
    }
    
    # Extrair host sem expor senha
    if '@' in neon_url:
        host_part = neon_url.split('@')[1].split('/')[0]
        info['host'] = host_part
    
    # Tentar testar conexão
    try:
        engine = create_engine(neon_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        info['status'] = 'online'
        info['connection_test'] = 'success'
        
    except Exception as e:
        info['status'] = 'error'
        info['connection_test'] = 'failed'
        info['error'] = str(e)
    
    return info


def get_local_db_info():
    """
    Retorna informações sobre o banco local (se configurado).
    
    Returns:
        dict: Informações do banco local
    """
    use_local = os.environ.get('USE_LOCAL_DB', 'false').lower() == 'true'
    
    if not use_local:
        return {
            'configured': False,
            'status': 'not_configured'
        }
    
    local_db_type = os.environ.get('LOCAL_DB_TYPE', 'sqlite').lower()
    
    info = {
        'configured': True,
        'type': local_db_type
    }
    
    if local_db_type in ('postgres', 'postgresql'):
        from init_local_db import get_postgres_connection_params
        params = get_postgres_connection_params()
        
        info['host'] = f"{params['host']}:{params['port']}"
        info['database'] = params['database']
        info['user'] = params['user']
        
        # Testar conexão
        try:
            db_url = f"postgresql://{params['user']}:{params['password']}@{params['host']}:{params['port']}/{params['database']}"
            engine = create_engine(db_url)
            
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            info['status'] = 'online'
            info['connection_test'] = 'success'
            
        except Exception as e:
            info['status'] = 'error'
            info['connection_test'] = 'failed'
            info['error'] = str(e)
    
    else:  # SQLite
        db_path = os.environ.get('LOCAL_DB_PATH', 'local_legal_pro.db')
        db_file = Path(db_path)
        
        info['path'] = db_path
        info['absolute_path'] = str(db_file.absolute())
        
        if db_file.exists():
            info['status'] = 'exists'
            info['size_mb'] = round(db_file.stat().st_size / (1024 * 1024), 2)
        else:
            info['status'] = 'not_exists'
            info['size_mb'] = 0
    
    return info


def get_database_stats():
    """
    Retorna estatísticas do banco de dados ativo.
    
    Returns:
        dict: Estatísticas (tabelas, registros, tamanho, etc)
    """
    try:
        from main import db
        
        # Inspector para obter informações do schema
        inspector = inspect(db.engine)
        
        # Listar tabelas
        table_names = inspector.get_table_names()
        
        stats = {
            'total_tables': len(table_names),
            'tables': []
        }
        
        # Contagem total de registros
        total_records = 0
        
        # Iterar sobre tabelas para obter contagens
        for table_name in table_names:
            try:
                # Executar COUNT
                result = db.session.execute(
                    text(f'SELECT COUNT(*) FROM "{table_name}"')
                )
                count = result.scalar()
                total_records += count
                
                stats['tables'].append({
                    'name': table_name,
                    'records': count
                })
                
            except Exception:
                # Tabela pode não ter permissão ou não existir mais
                stats['tables'].append({
                    'name': table_name,
                    'records': None,
                    'error': 'Unable to count'
                })
        
        stats['total_records'] = total_records
        
        # Tamanho do banco (se possível)
        db_type = get_db_type()
        
        if db_type == 'sqlite_local':
            db_path = os.environ.get('LOCAL_DB_PATH', 'local_legal_pro.db')
            db_file = Path(db_path)
            if db_file.exists():
                stats['size_mb'] = round(db_file.stat().st_size / (1024 * 1024), 2)
        
        elif 'postgres' in db_type.lower():
            try:
                # Query para tamanho do banco PostgreSQL
                result = db.session.execute(
                    text("SELECT pg_database_size(current_database())")
                )
                size_bytes = result.scalar()
                stats['size_mb'] = round(size_bytes / (1024 * 1024), 2)
            except Exception:
                stats['size_mb'] = None
        
        return stats
        
    except Exception as e:
        return {
            'error': str(e),
            'total_tables': 0,
            'total_records': 0,
            'tables': []
        }


def get_table_info(table_name):
    """
    Retorna informações detalhadas sobre uma tabela específica.
    
    Args:
        table_name: Nome da tabela
        
    Returns:
        dict: Informações da tabela (colunas, índices, tamanho, etc)
    """
    try:
        from main import db
        
        inspector = inspect(db.engine)
        
        # Verificar se tabela existe
        if table_name not in inspector.get_table_names():
            return {
                'error': f'Tabela {table_name} não encontrada'
            }
        
        # Colunas
        columns = inspector.get_columns(table_name)
        
        # Índices
        indexes = inspector.get_indexes(table_name)
        
        # Primary keys
        pk_constraint = inspector.get_pk_constraint(table_name)
        
        # Foreign keys
        foreign_keys = inspector.get_foreign_keys(table_name)
        
        # Contagem de registros
        result = db.session.execute(
            text(f'SELECT COUNT(*) FROM "{table_name}"')
        )
        record_count = result.scalar()
        
        info = {
            'name': table_name,
            'columns': columns,
            'indexes': indexes,
            'primary_key': pk_constraint,
            'foreign_keys': foreign_keys,
            'record_count': record_count
        }
        
        # Tamanho da tabela (PostgreSQL)
        if 'postgres' in get_db_type().lower():
            try:
                result = db.session.execute(
                    text(f"SELECT pg_total_relation_size('{table_name}')")
                )
                size_bytes = result.scalar()
                info['size_mb'] = round(size_bytes / (1024 * 1024), 2)
            except Exception:
                info['size_mb'] = None
        
        return info
        
    except Exception as e:
        return {
            'error': str(e)
        }


def test_database_connection(db_url, db_type='unknown'):
    """
    Testa conexão com um banco de dados.
    
    Args:
        db_url: URL de conexão do banco
        db_type: Tipo do banco (para logging)
        
    Returns:
        dict: Resultado do teste
    """
    try:
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            if 'postgresql' in db_url.lower():
                result = conn.execute(text("SELECT version()"))
                version = result.scalar()
            elif 'sqlite' in db_url.lower():
                result = conn.execute(text("SELECT sqlite_version()"))
                version = result.scalar()
            else:
                result = conn.execute(text("SELECT 1"))
                version = "Unknown"
        
        return {
            'success': True,
            'status': 'online',
            'message': 'Conexão bem-sucedida',
            'version': version
        }
        
    except Exception as e:
        return {
            'success': False,
            'status': 'error',
            'message': f'Erro ao conectar: {str(e)}',
            'error': str(e)
        }


def get_backup_list():
    """
    Lista backups disponíveis no diretório /tmp.
    
    Returns:
        list: Lista de backups encontrados
    """
    backups = []
    backup_dir = Path('/tmp')
    
    # Buscar arquivos de backup
    for backup_file in backup_dir.glob('legal_pro_backup_*.sql'):
        stat = backup_file.stat()
        
        backups.append({
            'filename': backup_file.name,
            'path': str(backup_file),
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'created_at': stat.st_ctime,
            'modified_at': stat.st_mtime
        })
    
    # Ordenar por data de criação (mais recente primeiro)
    backups.sort(key=lambda x: x['created_at'], reverse=True)
    
    return backups
