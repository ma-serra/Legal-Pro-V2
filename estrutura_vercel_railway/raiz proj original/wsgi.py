"""
Ponto de entrada WSGI para o servidor gunicorn.
Otimizado com health check rápido e inicialização diferida.
"""
import logging

# Configurar logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar gerenciador de inicialização PRIMEIRO (não carrega o app completo)
from startup_optimizer import initialization_manager, HealthCheckMiddleware

logger.info("🚀 Iniciando WSGI application com health checks otimizados...")

# Importar e criar app (isso vai disparar create_app em main.py)
from main import app

# Envolver o app Flask com middleware de health check
# Isso permite que /health e /healthz respondam imediatamente
application = HealthCheckMiddleware(app, initialization_manager)

logger.info("✅ WSGI application pronta com health check middleware")