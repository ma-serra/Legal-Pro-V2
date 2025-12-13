"""
Configuração de banco de dados para jurimetria
Suporta PostgreSQL (produção) e SQLite (desenvolvimento)
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)

# Configurações do banco
DATABASE_CONFIG = {
    'development': {
        'url': 'sqlite:///jurimetria.db',
        'echo': True,
        'pool_size': 5,
        'max_overflow': 10
    },
    'production': {
        'url': os.getenv('DATABASE_URL'),
        'echo': False,
        'pool_size': 20,
        'max_overflow': 30,
        'pool_timeout': 30,
        'pool_recycle': 3600
    }
}

# Forçar uso do PostgreSQL sempre
ENVIRONMENT = 'production'
config = DATABASE_CONFIG[ENVIRONMENT]

# Engine do SQLAlchemy
engine = create_engine(
    config['url'],
    echo=config['echo'],
    pool_size=config.get('pool_size', 5),
    max_overflow=config.get('max_overflow', 10),
    pool_timeout=config.get('pool_timeout', 30),
    pool_recycle=config.get('pool_recycle', 3600) if ENVIRONMENT == 'production' else -1
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

# Dependency para FastAPI/Flask
def get_db():
    """Generator para sessões de banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Inicializa banco de dados criando todas as tabelas"""
    logger.info(f"Inicializando banco de dados: {config['url']}")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Banco de dados inicializado")

def drop_db():
    """Remove todas as tabelas (CUIDADO!)"""
    logger.warning("Removendo todas as tabelas do banco")
    Base.metadata.drop_all(bind=engine)
    logger.info("✅ Tabelas removidas")

# Context manager para transações
class DatabaseSession:
    def __init__(self):
        self.db = SessionLocal()
    
    def __enter__(self):
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.db.rollback()
        else:
            self.db.commit()
        self.db.close()

def get_engine():
    """Retorna engine do SQLAlchemy"""
    return engine

def test_connection():
    """Testa conexão com banco"""
    try:
        with engine.connect() as conn:
            conn.execute('SELECT 1')
        logger.info("✅ Conexão com banco de dados OK")
        return True
    except Exception as e:
        logger.error(f"❌ Erro na conexão: {e}")
        return False