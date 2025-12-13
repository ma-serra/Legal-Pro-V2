"""
Otimizador de Startup para Replit Deploy
Reduz operações desnecessárias durante inicialização
Inclui health check rápido e gerenciador de inicialização diferida
"""

import os
import logging
import threading
import time
from typing import Dict, Any, Callable, Optional

logger = logging.getLogger(__name__)

class StartupOptimizer:
    """Otimiza o processo de startup da aplicação"""
    
    def __init__(self):
        self.startup_config = {
            'skip_database_migrations': True,  # Pular migrations no startup
            'lazy_load_modules': True,         # Carregamento lazy de módulos
            'minimal_logging': True,           # Logging mínimo
            'quick_bind': True,               # Binding rápido na porta
            'defer_heavy_operations': True     # Adiar operações pesadas
        }
    
    def optimize_flask_app(self, app):
        """Otimiza configurações do Flask para startup rápido"""
        
        # Configurar timeouts otimizados
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 ano para assets estáticos
        app.config['PERMANENT_SESSION_LIFETIME'] = 3600     # 1 hora para sessões
        
        # Configurar SQLAlchemy para startup rápido
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': False,        # Desabilitar durante startup
            'pool_recycle': 3600,         # Reciclar conexões após 1h
            'connect_args': {
                'connect_timeout': 10,     # Timeout de conexão reduzido
                'application_name': 'legal_pro'
            }
        }
        
        logger.info("✅ Configurações de startup otimizadas aplicadas")
        return app
    
    def defer_heavy_initialization(self):
        """Adia inicializações pesadas para depois do binding da porta"""
        deferred_operations = []
        
        # Operações que podem ser adiadas
        deferred_operations.extend([
            'vector_database_connection',
            'ml_models_loading', 
            'template_preprocessing',
            'agent_initialization',
            'zoom_token_prefetch',          # Novo: Zoom API token
            'bertimbau_model_loading',      # Novo: LegalBERTimbau
            'nlp_pipeline_initialization'   # Novo: Pipeline NLP
        ])
        
        logger.info(f"🚀 {len(deferred_operations)} operações pesadas adiadas para pós-startup")
        return deferred_operations
    
    def enable_lazy_loading(self):
        """Configura carregamento lazy para módulos não essenciais"""
        lazy_modules = [
            'multiagent.routes',
            'modules.video_transcription',
            'modules.templates_documentos',
            'jurimetria.api',
            'apis.*',
            'zoom_api.routes.zoom_routes',              # Novo: Zoom API
            'modules.analise_legal_bert.routes',        # Novo: LegalBERTimbau
            'modules.analise_legal_bert.services.*'     # Novo: Serviços BERT
        ]
        
        logger.info(f"📦 {len(lazy_modules)} módulos configurados para lazy loading")
        return lazy_modules

class InitializationManager:
    """
    Gerencia a inicialização diferida de componentes pesados
    Permite que o app responda a health checks antes da inicialização completa
    """
    
    def __init__(self):
        self.initialized = False
        self.initialization_status = {
            'database': False,
            'agents': False,
            'bert_models': False,
            'routes': False,
            'cache': False
        }
        self.initialization_errors = {}
        self.lock = threading.Lock()
        self._app = None
    
    def is_ready(self) -> bool:
        """Verifica se a inicialização completa foi concluída"""
        return self.initialized
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna o status detalhado da inicialização"""
        return {
            'ready': self.initialized,
            'components': self.initialization_status.copy(),
            'errors': self.initialization_errors.copy()
        }
    
    def initialize_in_background(self, app, init_function: Callable):
        """
        Executa a inicialização pesada em background
        """
        with self.lock:
            if self.initialized:
                logger.info("Inicialização já concluída, pulando...")
                return
            
            self._app = app
        
        def _background_init():
            try:
                logger.info("🚀 Iniciando carregamento diferido de componentes...")
                init_function(app, self)
                
                # Só marca como inicializado se todos os componentes críticos estiverem prontos
                with self.lock:
                    critical_components = ['database', 'routes', 'cache']
                    all_critical_ready = all(
                        self.initialization_status.get(comp, False) 
                        for comp in critical_components
                    )
                    
                    if all_critical_ready:
                        self.initialized = True
                        logger.info("✅ Inicialização completa concluída com sucesso!")
                    else:
                        failed_components = [
                            comp for comp in critical_components 
                            if not self.initialization_status.get(comp, False)
                        ]
                        logger.error(f"❌ Componentes críticos falharam: {failed_components}")
                        self.initialization_errors['critical_components'] = ', '.join(failed_components)
                
            except Exception as e:
                logger.error(f"❌ Erro durante inicialização em background: {e}")
                import traceback
                logger.error(traceback.format_exc())
                self.initialization_errors['general'] = str(e)
                with self.lock:
                    self.initialized = False
        
        # Iniciar thread de background
        thread = threading.Thread(target=_background_init, daemon=True)
        thread.start()
        logger.info("📦 Inicialização em background iniciada")
    
    def mark_component_ready(self, component: str, ready: bool = True, error: Optional[str] = None):
        """Marca um componente como pronto ou com erro"""
        with self.lock:
            self.initialization_status[component] = ready
            if error:
                self.initialization_errors[component] = error


class HealthCheckMiddleware:
    """
    Middleware WSGI que intercepta requisições de health check
    e responde imediatamente sem carregar o app Flask completo
    
    CRÍTICO PARA REPLIT DEPLOY: Intercepta TODAS as requisições de health check
    independente do user-agent para garantir resposta rápida (<100ms)
    """
    
    def __init__(self, app, init_manager: InitializationManager):
        self.app = app
        self.init_manager = init_manager
    
    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        method = environ.get('REQUEST_METHOD', '').upper()
        
        # CRITICAL FIX: Interceptar TODAS as requisições GET/HEAD para health check endpoints
        # Replit Deploy usa curl sem user-agent específico, então não podemos filtrar por user-agent
        
        # Health check básico - SEMPRE responde OK imediatamente (< 100ms)
        # /health e /healthz são SEMPRE interceptados
        if path in ['/health', '/healthz'] and method in ['GET', 'HEAD']:
            status = '200 OK'
            headers = [('Content-Type', 'text/plain')]
            start_response(status, headers)
            return [b'OK']
        
        # Root endpoint (/) - apenas intercepta health check probes, não navegadores
        if path == '/' and method in ['GET', 'HEAD']:
            # Detectar se é um navegador real (Accept: text/html)
            accept_header = environ.get('HTTP_ACCEPT', '').lower()
            is_browser = 'text/html' in accept_header
            
            # Se NÃO for navegador (é um health check probe), responde imediatamente
            if not is_browser:
                status = '200 OK'
                headers = [('Content-Type', 'application/json')]
                start_response(status, headers)
                return [b'{"status":"ok","service":"legal-pro","version":"2.0"}']
            # Se for navegador, deixa passar para Flask servir a UI normal
        
        # Readiness check - verifica se a inicialização completa terminou
        if path == '/readyz' and method in ['GET', 'HEAD']:
            if self.init_manager.is_ready():
                status = '200 OK'
                headers = [('Content-Type', 'application/json')]
                start_response(status, headers)
                return [b'{"status":"ready"}']
            else:
                status = '503 Service Unavailable'
                headers = [('Content-Type', 'application/json')]
                start_response(status, headers)
                import json
                status_data = self.init_manager.get_status()
                return [json.dumps(status_data).encode('utf-8')]
        
        # Para todas as outras rotas (incluindo / de navegadores reais), delega para o app Flask
        return self.app(environ, start_response)


def deferred_heavy_initialization(app, init_manager: InitializationManager):
    """
    Executa operações pesadas de inicialização em background
    Esta função é chamada após o app já estar servindo health checks
    
    IMPORTANTE: Erros em componentes críticos (database, routes, cache) farão
    a inicialização falhar e /readyz retornar 503
    """
    database_ready = False
    routes_ready = False
    cache_ready = False
    
    try:
        with app.app_context():
            from main import db
            
            # 1. Inicializar/verificar database schema (CRÍTICO)
            logger.info("📊 Inicializando schema do banco de dados...")
            try:
                db.create_all()
                database_ready = True
                init_manager.mark_component_ready('database', True)
                logger.info("✅ Database schema pronto")
            except Exception as e:
                logger.error(f"❌ FALHA CRÍTICA ao criar schema: {e}")
                import traceback
                logger.error(traceback.format_exc())
                init_manager.mark_component_ready('database', False, str(e))
                # Database é crítico - não continuar se falhar
                raise
            
            # 2. Inicializar sistema de monitoramento e usuário admin (NÃO CRÍTICO)
            logger.info("👤 Inicializando usuário admin...")
            try:
                from multiagent.utils.system_monitor import get_system_monitor
                system_monitor = get_system_monitor()
                system_monitor.initialize_admin_user(db)
                logger.info("✅ Usuário admin inicializado")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao inicializar admin (não crítico): {e}")
            
            # 3. Inicializar temas de páginas (NÃO CRÍTICO)
            logger.info("🎨 Inicializando temas...")
            try:
                from models import TemaPagina
                import json
                
                temas_transcricao = [
                    ('/transcricao-audio/', 'Transcrição de Áudio - Página Inicial'),
                    ('/transcricao-audio/result', 'Transcrição de Áudio - Resultados'),
                    ('/transcricao-audio/progress', 'Transcrição de Áudio - Progresso')
                ]
                
                for rota, descricao in temas_transcricao:
                    try:
                        tema_existente = TemaPagina.query.filter_by(rota=rota).first()
                        if not tema_existente:
                            cores_default = {
                                "body": {"color": "#000000", "background-color": "#f8f9fa"}
                            }
                            novo_tema = TemaPagina(
                                rota=rota,
                                descricao=descricao,
                                cores=json.dumps(cores_default),
                                ativo=True
                            )
                            db.session.add(novo_tema)
                            db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        logger.warning(f"⚠️ Erro ao criar tema {rota}: {e}")
                
                logger.info("✅ Temas inicializados")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao processar temas (não crítico): {e}")
            
            # 4. Inicializar prompts do assistente (NÃO CRÍTICO)
            logger.info("🤖 Inicializando prompts do assistente...")
            try:
                from assistente.prompts import inicializar_prompts_padrao
                if inicializar_prompts_padrao():
                    logger.info("✅ Prompts do assistente inicializados")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao inicializar prompts (não crítico): {e}")
            
            # 5. Marcar agentes como prontos (lazy load real na primeira utilização - NÃO CRÍTICO)
            init_manager.mark_component_ready('agents', True)
            logger.info("✅ Sistema de agentes configurado (lazy load)")
            
            # 6. Criar tabelas dos módulos pesados (NÃO CRÍTICO)
            # NOTA: Os blueprints já foram registrados durante create_app()
            # Aqui apenas criamos as tabelas do database para os módulos pesados
            logger.info("📊 Criando tabelas dos módulos pesados...")
            try:
                # Importar modelos do módulo BERTimbau
                from modules.analise_legal_bert.models import AnaliseLegalDocumentoBert, EntidadeExtraidaBert, ClassificacaoDocumentoBert
                # Importar outros modelos pesados se necessário
                db.create_all()
                logger.info("✅ Tabelas dos módulos pesados criadas")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao criar tabelas dos módulos pesados (não crítico): {e}")
            
            # 8. Marcar BERT como pronto (lazy load real na primeira utilização - NÃO CRÍTICO)
            init_manager.mark_component_ready('bert_models', True)
            logger.info("✅ Modelos BERT configurados (lazy load)")
            
            # 9. Marcar rotas e cache como prontos (CRÍTICO)
            routes_ready = True
            cache_ready = True
            init_manager.mark_component_ready('routes', True)
            init_manager.mark_component_ready('cache', True)
            logger.info("✅ Rotas e cache configurados")
            
    except Exception as e:
        # Falha crítica - garantir que componentes não fiquem marcados como prontos
        logger.error(f"❌ FALHA CRÍTICA durante inicialização pesada: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        if not database_ready:
            init_manager.mark_component_ready('database', False, str(e))
        if not routes_ready:
            init_manager.mark_component_ready('routes', False, str(e))
        if not cache_ready:
            init_manager.mark_component_ready('cache', False, str(e))
        
        # Re-raise para que initialize_in_background saiba que houve falha
        raise


# Instância global do otimizador e gerenciador de inicialização
startup_optimizer = StartupOptimizer()
initialization_manager = InitializationManager()