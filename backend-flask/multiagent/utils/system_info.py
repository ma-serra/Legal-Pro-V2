"""
Utilitários para informações do sistema multi-agente.
"""

import os
import sys
import platform
import psutil
import datetime
import json
from typing import Dict, Any, List

def get_system_info() -> Dict[str, Any]:
    """
    Obtém informações sobre o sistema operacional e recursos.
    
    Returns:
        Dicionário com informações do sistema
    """
    info = {
        "sistema": {
            "sistema_operacional": platform.system(),
            "versao_os": platform.version(),
            "arquitetura": platform.machine(),
            "processador": platform.processor(),
            "python_versao": platform.python_version(),
            "hora_atual": datetime.datetime.now().isoformat()
        },
        "recursos": {
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memoria_total": psutil.virtual_memory().total,
            "memoria_disponivel": psutil.virtual_memory().available,
            "memoria_usada_percent": psutil.virtual_memory().percent,
            "disco_total": psutil.disk_usage('/').total,
            "disco_livre": psutil.disk_usage('/').free,
            "disco_usado_percent": psutil.disk_usage('/').percent
        },
        "ambiente": {
            "python_path": sys.executable,
            "diretorio_trabalho": os.getcwd(),
            "encoding": sys.getdefaultencoding(),
            "variaveis_ambiente": _get_safe_env_vars()
        }
    }
    
    return info

def get_process_info() -> Dict[str, Any]:
    """
    Obtém informações sobre o processo atual.
    
    Returns:
        Dicionário com informações do processo
    """
    process = psutil.Process()
    
    info = {
        "processo": {
            "pid": process.pid,
            "nome": process.name(),
            "status": process.status(),
            "criacao": datetime.datetime.fromtimestamp(process.create_time()).isoformat(),
            "cpu_percent": process.cpu_percent(interval=0.1),
            "memoria_rss": process.memory_info().rss,
            "memoria_vms": process.memory_info().vms,
            "memoria_percent": process.memory_percent(),
            "threads": process.num_threads(),
            "filhos": len(process.children())
        }
    }
    
    return info

def _get_safe_env_vars() -> Dict[str, str]:
    """
    Obtém variáveis de ambiente seguras (sem senhas ou chaves).
    
    Returns:
        Dicionário com variáveis de ambiente seguras
    """
    env_vars = {}
    
    # Lista de variáveis seguras para exibir
    safe_vars = [
        "PATH", "PYTHONPATH", "LANG", "USER", "HOME", 
        "SHELL", "PWD", "LOGNAME", "TZ"
    ]
    
    # Lista de prefixos a ignorar (potencialmente sensíveis)
    ignored_prefixes = [
        "API_KEY", "SECRET", "PASSWORD", "TOKEN", "KEY",
        "APIKEY", "AUTH", "ACCESS", "PRIVATE", "CREDENTIAL"
    ]
    
    for key, value in os.environ.items():
        # Verifica se é uma variável segura ou não contém dados sensíveis
        is_safe = key in safe_vars
        
        # Verifica prefixos para filtrar variáveis potencialmente sensíveis
        if not is_safe:
            is_sensitive = False
            
            for prefix in ignored_prefixes:
                if prefix in key.upper():
                    is_sensitive = True
                    break
                    
            is_safe = not is_sensitive
            
        if is_safe:
            env_vars[key] = value
    
    return env_vars

def get_multi_agent_status() -> Dict[str, Any]:
    """
    Obtém status dos diferentes componentes do sistema multi-agente.
    
    Returns:
        Dicionário com status dos componentes
    """
    from multiagent.utils import get_log_manager, get_fallback_manager, get_feedback_manager
    
    status = {
        "componentes": {
            "logger": {
                "status": "ativo",
                "configuracao": get_log_manager().get_config()
            },
            "fallback": {
                "status": "ativo",
                "estatisticas": get_fallback_manager().get_error_stats()
            },
            "feedback": {
                "status": "ativo",
                "metricas": get_feedback_manager().get_metrics()
            }
        },
        "metricas": {
            "timestamp": datetime.datetime.now().isoformat()
        }
    }
    
    return status

def format_size(size_bytes: float) -> str:
    """
    Formata um tamanho em bytes para uma string legível.
    
    Args:
        size_bytes: Tamanho em bytes
        
    Returns:
        String formatada (ex: "4.2 MB")
    """
    if size_bytes == 0:
        return "0 B"
        
    size_names = ("B", "KB", "MB", "GB", "TB")
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
        
    return f"{size_bytes:.2f} {size_names[i]}"