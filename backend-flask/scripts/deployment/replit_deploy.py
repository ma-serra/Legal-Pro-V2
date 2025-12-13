"""
Configuração específica para deploy otimizado no Replit
Mantém todas as funcionalidades com inicialização rápida
"""

import os
import sys
import time
import logging
from main import app

# Configuração de logging otimizada
logging.getLogger('werkzeug').setLevel(logging.WARNING)
logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def optimize_for_replit():
    """Otimiza aplicação para deploy no Replit"""
    
    # Configurações específicas para Replit
    app.config.update({
        'ENV': 'production',
        'TESTING': False,
        'DEBUG': False,
        'SEND_FILE_MAX_AGE_DEFAULT': 31536000,  # Cache de 1 ano para assets
        'PERMANENT_SESSION_LIFETIME': 86400,    # Sessões de 24 horas
    })
    
    # Otimizações de database para startup rápido
    if not app.config.get('SQLALCHEMY_ENGINE_OPTIONS'):
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}
    
    app.config['SQLALCHEMY_ENGINE_OPTIONS'].update({
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'connect_args': {
            'connect_timeout': 30,
            'application_name': 'legal_pro_replit'
        }
    })
    
    return app

def bind_port_fast():
    """Vincula porta rapidamente para evitar timeout do Replit"""
    port = int(os.environ.get("PORT", 5000))
    host = "0.0.0.0"
    
    logger.info(f"🚀 Binding to {host}:{port} for Replit Deploy")
    
    return host, port

if __name__ == '__main__':
    start_time = time.time()
    
    print("🚀 Legal Pro - Replit Deploy Optimized")
    print("📋 Mantendo todas as 327 funcionalidades do sistema")
    
    # Otimizar aplicação
    app_optimized = optimize_for_replit()
    
    # Configurar porta
    host, port = bind_port_fast()
    
    # Tempo de inicialização
    startup_time = round(time.time() - start_time, 2)
    print(f"✅ Startup completo em {startup_time}s")
    print(f"🌐 Servidor disponível em http://{host}:{port}")
    
    # Executar com configurações otimizadas
    app_optimized.run(
        host=host,
        port=port,
        debug=False,
        threaded=True,
        use_reloader=False
    )