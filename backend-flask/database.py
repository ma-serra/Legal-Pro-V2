"""
Módulo de Banco de Dados
Configuração centralizada do banco de dados para evitar circular imports
"""
from flask_sqlalchemy import SQLAlchemy

# Instância global do banco de dados
db = SQLAlchemy()

# Base para todos os modelos (SQLAlchemy)
Base = db.Model

class DatabaseConfig:
    """Configuração do banco de dados"""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    @staticmethod
    def init_db(app):
        """Inicializa o banco de dados com a aplicação Flask"""
        db.init_app(app)
        with app.app_context():
            db.create_all()
            return db
    
    @staticmethod
    def session():
        """Retorna a sessão atual do banco de dados"""
        return db.session
    
    @staticmethod
    def commit():
        """Commit da sessão"""
        db.session.commit()
    
    @staticmethod
    def rollback():
        """Rollback da sessão"""
        db.session.rollback()
    
    @staticmethod
    def close():
        """Fecha a sessão"""
        db.session.close()

# Exportar para uso em modelos
__all__ = ['db', 'Base', 'DatabaseConfig']
