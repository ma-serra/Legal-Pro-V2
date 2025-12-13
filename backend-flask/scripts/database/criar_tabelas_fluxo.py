"""
Script para criar as tabelas do módulo de fluxos no banco de dados.
"""
import os
import sys
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Adicionar o diretório raiz ao PATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar modelos
from models import db, FluxoModel, ExecucaoFluxo

def criar_tabelas_fluxo():
    """
    Cria as tabelas relacionadas aos fluxos no banco de dados.
    """
    try:
        # Criar tabelas
        logger.info("Criando tabelas de fluxos...")
        db.create_all()
        logger.info("Tabelas criadas com sucesso!")
        
        return True
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {str(e)}")
        return False

if __name__ == "__main__":
    # Criar uma aplicação Flask mínima para o contexto
    app = Flask(__name__)
    
    # Configurar banco de dados
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Inicializar extensão
    db.init_app(app)
    
    # Criar tabelas no contexto da aplicação
    with app.app_context():
        sucesso = criar_tabelas_fluxo()
        
    if sucesso:
        logger.info("Script concluído com sucesso!")
        sys.exit(0)
    else:
        logger.error("Falha ao executar o script.")
        sys.exit(1)