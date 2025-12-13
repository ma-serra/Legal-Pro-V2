"""
Módulo de Comparação de Versões de Documentos com Classificação por Área e Cliente
"""

import logging
import os
from flask import Flask, Blueprint

logger = logging.getLogger(__name__)

# Criar o blueprint
bp = Blueprint('comparacao_documentos', __name__, url_prefix='/comparacao-documentos')

# Importar as rotas
from modules.comparacao_documentos.routes import views

def init_app(app: Flask):
    """
    Inicializa o módulo e registra o blueprint na aplicação Flask
    """
    try:
        # Registrar blueprint
        app.register_blueprint(bp)
        
        # Criar diretório para arquivos temporários se não existir
        upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
        temp_dir = os.path.join(upload_folder, 'comparacao_docs')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir, exist_ok=True)
        
        # Registrar no app
        app.logger.info("Módulo de Comparação de Documentos inicializado com sucesso.")
        
    except Exception as e:
        app.logger.error(f"Erro ao inicializar módulo de Comparação de Documentos: {e}")