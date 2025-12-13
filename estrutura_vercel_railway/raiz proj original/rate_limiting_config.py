
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Configuração de Rate Limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Aplicar em rotas sensíveis
@app.route('/api/chat', methods=['POST'])
@limiter.limit("10 per minute")
def api_chat():
    # Implementação existente
    pass

@app.route('/transcricao', methods=['POST'])
@limiter.limit("5 per minute")
def transcricao():
    # Implementação existente
    pass

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # Implementação existente
    pass
