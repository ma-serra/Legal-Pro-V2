"""
Módulo de rotas para integração com a API do Zoom
"""

# Importar functions explicitamente para evitar erros de importação
from zoom_api.routes.zoom_routes import dashboard
from zoom_api.routes.zoom_routes import auth
from zoom_api.routes.zoom_routes import callback
from zoom_api.routes.zoom_routes import webhook
from zoom_api.routes.zoom_routes import create_meeting
from zoom_api.routes.zoom_routes import list_meetings
from zoom_api.routes.zoom_routes import list_recordings
from zoom_api.routes.zoom_routes import join_meeting
from zoom_api.routes.zoom_routes import list_webinars
from zoom_api.routes.zoom_routes import manage_webinar
from zoom_api.routes.zoom_routes import send_message
from zoom_api.routes.zoom_routes import get_user
from zoom_api.routes.zoom_routes import manage_meeting
from zoom_api.routes.zoom_routes import update_meeting_status
from zoom_api.routes.zoom_routes import manage_registrants

# Lista de funções exportadas
__all__ = [
    'dashboard',
    'auth',
    'callback',
    'webhook',
    'create_meeting',
    'list_meetings',
    'list_recordings',
    'join_meeting',
    'list_webinars',
    'manage_webinar',
    'send_message',
    'get_user',
    'manage_meeting', 
    'update_meeting_status',
    'manage_registrants'
]