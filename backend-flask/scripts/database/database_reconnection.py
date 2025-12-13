"""
Sistema de reconexão robusta para PostgreSQL
Resolve problemas de conexão SSL e timeout
"""
import os
import time
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, DisconnectionError
import logging

logger = logging.getLogger(__name__)

def create_robust_engine():
    """Cria engine PostgreSQL com configurações robustas"""
    database_url = os.environ.get('DATABASE_URL')
    
    engine_options = {
        'pool_size': 5,
        'max_overflow': 10,
        'pool_timeout': 30,
        'pool_recycle': 280,
        'pool_pre_ping': True,
        'connect_args': {
            'connect_timeout': 10,
            'application_name': 'juridico_multiagente',
            'options': '-c statement_timeout=30000'
        }
    }
    
    return create_engine(database_url, **engine_options)

def execute_with_retry(engine, query, params=None, max_retries=3):
    """Executa query com retry automático em caso de falha de conexão"""
    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                if params:
                    result = conn.execute(text(query), params)
                else:
                    result = conn.execute(text(query))
                conn.commit()
                return result
        except (OperationalError, DisconnectionError) as e:
            logger.warning(f"Tentativa {attempt + 1} falhou: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Backoff exponencial

def verify_database_connection():
    """Verifica se a conexão com o banco está funcionando"""
    try:
        engine = create_robust_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Conexão com banco de dados verificada com sucesso")
        return True
    except Exception as e:
        logger.error(f"Erro na conexão com banco: {e}")
        return False

if __name__ == "__main__":
    verify_database_connection()