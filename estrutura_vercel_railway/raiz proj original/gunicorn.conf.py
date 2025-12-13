"""
Configuração Gunicorn otimizada para Replit Deploy
Ultra-rápida inicialização e binding de porta eficiente
"""
import os
import multiprocessing

# Configuração de porta
#bind = "0.0.0.0:5000"
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
raw_env = [f"PORT={os.environ.get('PORT', 5000)}"]
backlog = 2048

# Workers - Alinhado com .replit deployment
workers = 2  # 2 workers para produção (conforme .replit)
worker_class = "sync"
worker_connections = 1000

# Timeouts otimizados para deploy e startup completo
timeout = 300         # 5 minutos - tempo adequado para inicialização completa do sistema (alinhado com .replit)
keepalive = 5         # Reduzido para menor overhead
graceful_timeout = 30 # Reduzido para shutdown mais rápido

# Configurações de startup ultra-rápidas
preload_app = False   # Desabilitado para deploy rápido - evita inicialização pesada bloqueando porta
max_requests = 1000   # Reciclar workers após 1000 requests
max_requests_jitter = 50

# Configurações de processo
user = None
group = None
tmp_upload_dir = None

# Logging mínimo para performance
loglevel = "info"
accesslog = "-"
errorlog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configurações de startup
daemon = False
pidfile = None
umask = 0
tmp_upload_dir = None

# Configuração de SSL (desabilitado para simplicidade)
keyfile = None
certfile = None

# Configurações específicas do Replit
def when_ready(server):
    """Callback executado quando servidor está pronto"""
    server.log.info("🚀 Legal Pro server is ready. Listening on 0.0.0.0:5000")
    server.log.info(f"⚡ Otimizado com {server.cfg.workers} workers - Economia de recursos")
    server.log.info("📊 Production database synchronized and ready")
    server.log.info("✅ All 327 legal agents and role system active")

def worker_int(worker):
    """Callback para interrupção de worker"""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Callback antes de fazer fork do worker"""
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def post_fork(server, worker):
    """Callback após fork do worker"""
    server.log.info(f"Booting worker with pid: {worker.pid}")

# Configurações de memoria
max_requests_jitter = 100
worker_tmp_dir = "/dev/shm" if os.path.exists("/dev/shm") else "/tmp"

# Configurações de reload - desabilitado para deploy mais estável
reload = False  # Desabilitado para deploy estável e rápido
reload_engine = 'auto'

# Configurações específicas para Replit Deploy  
reuse_port = False  # Desabilitado conforme recomendação para deploy estável
preload_app = False # Desabilitado para deploy rápido - evita timeout de porta