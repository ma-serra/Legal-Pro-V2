"""
Sistema de execução de tarefas em background usando threads não bloqueantes.
Alternativa leve ao Celery que não bloqueia workers do Gunicorn.
"""
import threading
import time
from flask import current_app
from functools import wraps


def with_flask_context(f):
    """Decorator para executar função com contexto Flask"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        app = current_app._get_current_object()
        with app.app_context():
            return f(*args, **kwargs)
    return wrapper


class BackgroundExecutor:
    """
    Executa tarefas em threads separadas de forma não bloqueante.
    Mantém acesso ao contexto Flask mas não bloqueia o worker.
    """
    
    # Registro de threads ativas
    _active_threads = {}
    _lock = threading.Lock()
    
    @classmethod
    def run_task_in_background(cls, task_module, task_function, *args):
        """
        Executa uma task em thread separada COM contexto Flask.
        
        Args:
            task_module: Nome do módulo (ex: 'tasks.database_ops')
            task_function: Nome da função (ex: 'sync_postgres_to_postgres_task')
            *args: Argumentos para a função
            
        Returns:
            threading.Thread: Thread em background
        """
        # Importar a função dinamicamente
        module = __import__(task_module, fromlist=[task_function])
        func = getattr(module, task_function)
        
        # Capturar contexto Flask atual
        app = current_app._get_current_object()
        
        # Wrapper que executa função com contexto Flask
        def task_with_context():
            with app.app_context():
                try:
                    func(*args)
                finally:
                    # Limpar sessão após execução
                    from main import db
                    db.session.remove()
        
        # Criar e iniciar thread
        thread = threading.Thread(
            target=task_with_context,
            daemon=True,  # Não bloqueia o shutdown
            name=f'{task_function}_thread'
        )
        thread.start()
        
        # Registrar thread ativa
        job_id = args[0] if args else None
        if job_id:
            with cls._lock:
                cls._active_threads[job_id] = thread
        
        return thread
    
    @classmethod
    def is_running(cls, thread_or_job_id):
        """Verifica se uma thread ainda está rodando"""
        if thread_or_job_id is None:
            return False
        
        # Se for job_id (int), buscar thread
        if isinstance(thread_or_job_id, int):
            with cls._lock:
                thread = cls._active_threads.get(thread_or_job_id)
                if thread is None:
                    return False
                return thread.is_alive()
        
        # Se for thread diretamente
        return thread_or_job_id.is_alive()
    
    @classmethod
    def cleanup_finished_threads(cls):
        """Remove threads finalizadas do registro"""
        with cls._lock:
            finished = [job_id for job_id, thread in cls._active_threads.items() 
                       if not thread.is_alive()]
            for job_id in finished:
                del cls._active_threads[job_id]
