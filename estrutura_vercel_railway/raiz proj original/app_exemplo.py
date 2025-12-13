"""
Exemplo de integração do módulo de comparação de documentos
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def create_app():
    app = Flask(__name__)
    
    # Configurações básicas
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Inicializar extensões
    db.init_app(app)
    
    # Registrar módulo de comparação
    from modules.comparacao_documentos import init_app as init_comparacao
    init_comparacao(app)
    
    with app.app_context():
        # Importar modelos
        from models_comparacao import ComparacaoDocumento
        
        # Criar tabelas
        db.create_all()
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
