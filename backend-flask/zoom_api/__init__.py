"""
Módulo de integração com a API do Zoom
-------------------------------------------
Este módulo implementa a integração com a API do Zoom para videoconferências,
permitindo criar e gerenciar reuniões, webinars, gravações e outros recursos do Zoom.
"""

import os
import logging
from flask import Blueprint

# Criar o blueprint principal do módulo com nome único
zoom_api_bp = Blueprint('zoom_api', __name__, 
                       url_prefix='/zoom_api',
                       template_folder='templates/zoom')

# Verificar credenciais no startup
logger = logging.getLogger(__name__)
_missing_credentials = []
if not os.environ.get('ZOOM_CLIENT_ID'):
    _missing_credentials.append('ZOOM_CLIENT_ID')
if not os.environ.get('ZOOM_CLIENT_SECRET'):
    _missing_credentials.append('ZOOM_CLIENT_SECRET')
if not os.environ.get('ZOOM_ACCOUNT_ID'):
    _missing_credentials.append('ZOOM_ACCOUNT_ID')

if _missing_credentials:
    logger.warning(
        f"⚠️ Módulo Zoom API: Credenciais não configuradas: {', '.join(_missing_credentials)}. "
        "As rotas do Zoom retornarão erro 503 até que as credenciais sejam configuradas."
    )

# Importar as rotas após definir o blueprint para evitar importações circulares
from zoom_api.routes import *

def init_app(app):
    """Inicializa o módulo do Zoom dentro da aplicação Flask"""
    
    try:
        # Registrar o blueprint principal
        app.register_blueprint(zoom_api_bp)
        app.logger.info("Módulo Zoom API inicializado com sucesso.")
    except Exception as e:
        app.logger.error(f"Erro ao registrar blueprint Zoom API: {str(e)}")
    
    return app