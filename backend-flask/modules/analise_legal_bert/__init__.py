"""
Módulo de Análise Legal com BERTimbau
=====================================
Sistema de análise de documentos jurídicos utilizando processamento de linguagem natural
otimizado para textos jurídicos brasileiros.
"""

from flask import Blueprint, redirect, url_for

# Blueprint principal do módulo com suporte a URL com e sem barra final
analise_legal_bert_bp = Blueprint(
    'analise_legal_bert',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/analise-legal-bert'
)

# Configurar o blueprint para aceitar URLs com e sem barra final
# analise_legal_bert_bp.url_map.strict_slashes = False  # Blueprints não têm url_map

# Importar rotas após criação do blueprint
from . import routes

def init_app(app):
    """Inicializar módulo na aplicação Flask"""
    try:
        # Configurar Flask para não ser rígido com barras finais
        app.url_map.strict_slashes = False
        
        # Registrar blueprint principal
        if 'analise_legal_bert' not in app.blueprints:
            app.register_blueprint(analise_legal_bert_bp)
            app.logger.info("✅ Blueprint analise_legal_bert registrado com sucesso")
        else:
            app.logger.info("⚠️ Blueprint analise_legal_bert já estava registrado")

        # Adicionar rota global para capturar /analise-legal-bert sem barra
        @app.route('/analise-legal-bert')
        def analise_legal_bert_redirect():
            """Rota global para capturar URL sem barra final"""
            return redirect(url_for('analise_legal_bert.index'))
        
        # NOTA: db.create_all() foi movido para deferred_heavy_initialization
        # para evitar criar tabelas durante o startup que bloqueia health checks
        # As tabelas serão criadas em background após o health check responder
        app.logger.info("✅ Módulo analise_legal_bert configurado (tabelas serão criadas em background)")
        
        # Verificar rotas registradas
        with app.app_context():
            analise_routes = [str(rule.rule) for rule in app.url_map.iter_rules() if 'analise-legal-bert' in str(rule.rule)]
            app.logger.info(f"✅ Rotas analise-legal-bert registradas: {len(analise_routes)}")
            for route in analise_routes[:3]:
                app.logger.info(f"  - {route}")
                
    except Exception as e:
        app.logger.error(f"❌ Erro ao inicializar módulo analise_legal_bert: {e}")
        raise e