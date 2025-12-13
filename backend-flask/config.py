import os

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get("SESSION_SECRET", os.urandom(24))
    # DEBUG será definido dinamicamente pelo app.py com base nas configurações do banco de dados
    debug=False
    TESTING = True
    
    # Configuração de idioma e codificação
    BABEL_DEFAULT_LOCALE = 'pt_BR'
    JSON_AS_ASCII = False  # Garantir que o JSON seja codificado em UTF-8
    
    # Database configuration - Sistema de alternância Local/Nuvem
    # Suporta: SQLite local, PostgreSQL local, PostgreSQL Neon
    USE_LOCAL_DB = os.environ.get("USE_LOCAL_DB", "false").lower() == "true"
    
    if USE_LOCAL_DB:
        # Banco de Dados Local - SQLite ou PostgreSQL
        LOCAL_DB_TYPE = os.environ.get("LOCAL_DB_TYPE", "sqlite").lower()
        
        if LOCAL_DB_TYPE == "postgres" or LOCAL_DB_TYPE == "postgresql":
            # PostgreSQL Local (Docker ou instalação local)
            LOCAL_PG_URL = os.environ.get("LOCAL_DATABASE_URL")
            
            if LOCAL_PG_URL:
                # URL completa fornecida - extrair informações para logging
                import re
                match = re.search(r'@([^:]+):(\d+)/([^?]+)', LOCAL_PG_URL)
                if match:
                    pg_host_display = match.group(1)
                    pg_port_display = match.group(2)
                    pg_db_display = match.group(3).split('?')[0]  # Remover query params
                else:
                    pg_host_display = "PostgreSQL"
                    pg_port_display = ""
                    pg_db_display = ""
            else:
                # Valores padrão para PostgreSQL local
                PG_USER = os.environ.get("LOCAL_PG_USER", "postgres")
                PG_PASSWORD = os.environ.get("LOCAL_PG_PASSWORD", "postgres")
                PG_HOST = os.environ.get("LOCAL_PG_HOST", "localhost")
                PG_PORT = os.environ.get("LOCAL_PG_PORT", "5432")
                PG_DATABASE = os.environ.get("LOCAL_PG_DATABASE", "legal_pro_local")
                
                LOCAL_PG_URL = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"
                pg_host_display = PG_HOST
                pg_port_display = PG_PORT
                pg_db_display = PG_DATABASE
            
            SQLALCHEMY_DATABASE_URI = LOCAL_PG_URL
            SQLALCHEMY_ENGINE_OPTIONS = {
                "pool_recycle": 300,
                "pool_pre_ping": True,
            }
            DB_TYPE = "postgres_local"
            print("🐘 Usando BANCO DE DADOS LOCAL (PostgreSQL)")
            if pg_port_display and pg_db_display:
                print(f"   📍 Conexão: {pg_host_display}:{pg_port_display}/{pg_db_display}")
            else:
                print(f"   📍 Conexão: {pg_host_display}")
        
        else:
            # SQLite Local (padrão)
            LOCAL_DB_PATH = os.environ.get("LOCAL_DB_PATH", "local_legal_pro.db")
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{LOCAL_DB_PATH}"
            SQLALCHEMY_ENGINE_OPTIONS = {
                "pool_pre_ping": True,
            }
            DB_TYPE = "sqlite_local"
            print("🔧 Usando BANCO DE DADOS LOCAL (SQLite)")
            print(f"   📁 Arquivo: {LOCAL_DB_PATH}")
    
    else:
        # Banco de Dados Neon (PostgreSQL na Nuvem)
        SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
        
        # Validação crítica: DATABASE_URL deve estar definida
        if not SQLALCHEMY_DATABASE_URI:
            raise ValueError(
                "❌ ERRO: DATABASE_URL não está configurada!\n"
                "Configure DATABASE_URL nas variáveis de ambiente ou use USE_LOCAL_DB=true para banco local.\n"
                "Exemplo: export DATABASE_URL=postgresql://..."
            )
        
        # ⚡ OTIMIZAÇÕES DE PERFORMANCE - Connection Pool
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_size": 10,              # Pool inicial de 10 conexões
            "max_overflow": 20,            # Até 30 conexões no total (10 + 20)
            "pool_recycle": 300,           # Reciclar conexões a cada 5 minutos
            "pool_pre_ping": True,         # Verificar conexão antes de usar
            "pool_timeout": 30,            # Timeout de 30s para obter conexão
            "connect_args": {
                "connect_timeout": 10,     # Timeout de conexão inicial
                "options": "-c statement_timeout=30000"  # Timeout de queries (30s)
            }
        }
        DB_TYPE = "neon"
        print("☁️ Usando BANCO DE DADOS NEON (PostgreSQL na Nuvem)")
        print("   ⚡ Connection Pool: 10-30 conexões | Query Timeout: 30s")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API keys
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    D4SIGN_API_KEY = os.environ.get("D4SIGN_API_KEY")
    CLICKSIGN_API_KEY = os.environ.get("CLICKSIGN_API_KEY")
    JITSI_API_KEY = os.environ.get("JITSI_API_KEY")
    
    # Zoom API config
    ZOOM_API_KEY = os.environ.get("ZOOM_API_KEY") or os.environ.get("ZOOM_CLIENT_ID")
    ZOOM_API_SECRET = os.environ.get("ZOOM_API_SECRET") or os.environ.get("ZOOM_CLIENT_SECRET")
    ZOOM_ACCOUNT_ID = os.environ.get("ZOOM_ACCOUNT_ID")
    ZOOM_API_BASE_URL = os.environ.get("ZOOM_API_BASE_URL", "https://api.zoom.us/v2")
    ZOOM_REDIRECT_URI = os.environ.get("ZOOM_REDIRECT_URI", "https://localhost:5000/zoom/callback")
    
    JUDIT_API_KEY = os.environ.get("JUDIT_API_KEY")
    
    # Celery configuration
    CELERY_BROKER_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CELERY_CONFIG = {
        'broker_url': CELERY_BROKER_URL,
        'result_backend': CELERY_RESULT_BACKEND,
        'task_serializer': 'json',
        'accept_content': ['json'],
        'result_serializer': 'json',
        'enable_utc': True,
    }
    
    # File upload configuration
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200MB max upload size
    
    # Vector DB configuration
    QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY")
    QDRANT_COLLECTION = "legal_documents"
    
    # Security configuration
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # CSRF Protection - desativado para ambiente de produção
    WTF_CSRF_ENABLED = False  # Desabilitar proteção CSRF
    WTF_CSRF_CHECK_DEFAULT = False  # Desabilitar verificação CSRF
    WTF_CSRF_SECRET_KEY = os.environ.get("CSRF_SECRET_KEY", os.urandom(24))
    WTF_CSRF_TIME_LIMIT = 604800  # 7 dias em segundos (86400 * 7)
    WTF_CSRF_SSL_STRICT = False  # Desabilitar verificação SSL estrita para CSRF
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    WTF_CSRF_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']  # Métodos que normalmente teriam proteção
