"""
Otimizações específicas para deploy no Replit
"""
import os
import sys
import logging
from main import app, db

def optimize_for_replit_deploy():
    """Aplica otimizações específicas para o deploy no Replit"""
    
    with app.app_context():
        # 1. Limpar todas as transações SQL pendentes
        try:
            db.session.rollback()
            db.session.close()
            db.session.remove()
            logging.info("✅ Transações SQL limpas para deploy")
        except Exception as e:
            logging.warning(f"Limpeza de transações: {e}")
            
        # 2. Configurar timeout otimizado para Replit
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            "pool_recycle": 200,  # Reduzido para Replit
            "pool_pre_ping": True,
            "pool_size": 3,       # Menor pool para Replit
            "max_overflow": 1,
            "pool_timeout": 30,
            "connect_args": {
                "connect_timeout": 10,
                "server_settings": {
                    "jit": "off"  # Desabilita JIT para startup mais rápido
                }
            }
        }
        
        # 3. Desabilitar logs verbosos que atrasam o startup
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.ERROR)
        logging.getLogger('requests').setLevel(logging.ERROR)
        
        # 4. Configurar para modo de produção
        app.config['ENV'] = 'production'
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
        
        # 5. Otimizar configurações de sessão
        app.config['SESSION_COOKIE_SECURE'] = False  # HTTP no Replit
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # Cache estático
        
        logging.info("✅ Otimizações aplicadas para deploy no Replit")
    
    return app

if __name__ == "__main__":
    # Aplicar otimizações
    optimized_app = optimize_for_replit_deploy()
    
    # Iniciar servidor otimizado
    port = int(os.environ.get('PORT', 5000))
    
    logging.info(f"🚀 Iniciando Legal Pro otimizado na porta {port}")
    
    optimized_app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True,
        use_reloader=False
    )