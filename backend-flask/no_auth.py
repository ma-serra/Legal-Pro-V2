"""
Configuração para desabilitar autenticação (modo desenvolvimento)
"""

from functools import wraps
from flask import session, g
from flask_login import current_user

# Mock user para bypass de autenticação
class MockUser:
    """Usuário mockado para bypass de login"""
    def __init__(self):
        self.id = 1
        self.username = 'admin'
        self.email = 'admin@legal.pro'
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
        self.is_admin = True
        self.is_master = True
    
    def get_id(self):
        return str(self.id)

# Decorator substituto para @login_required que não exige login
def no_login_required(f):
    """Decorator que não exige login - apenas seta um usuário mock"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Setar usuário mock na sessão
        if not hasattr(g, 'user'):
            g.user = MockUser()
        return f(*args, **kwargs)
    return decorated_function

# Função para aplicar bypass global
def disable_authentication(app):
    """Desabilita autenticação globalmente"""
    
    @app.before_request
    def inject_mock_user():
        """Injeta usuário mock em todas as requisições"""
        from flask_login import login_user
        from flask import g
        
        # Criar usuário mock
        if not hasattr(g, 'mock_user'):
            g.mock_user = MockUser()
            
        # Tentar fazer auto-login
        if not current_user.is_authenticated:
            try:
                # Buscar primeiro usuário do banco
                from models import User
                first_user = User.query.first()
                
                if first_user:
                    login_user(first_user, remember=True)
                    session.permanent = True
                    
            except:
                # Se falhar, usar mock user
                pass
    
    print("🔓 Autenticação DESABILITADA - Modo desenvolvimento ativo")

# Aplicar desabilitar autenticação
def init_no_auth(app):
    """Inicializa modo sem autenticação"""
    disable_authentication(app)
    return True
