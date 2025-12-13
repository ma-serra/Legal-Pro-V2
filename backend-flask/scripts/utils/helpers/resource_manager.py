"""
Gerenciador Avançado de Recursos
Otimizações de CPU, memória e I/O para transcrições
"""

import os
import gc
import psutil
import logging
import threading
import time
from pathlib import Path
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResourceManager:
    """Gerenciador avançado de recursos do sistema"""
    
    def __init__(self):
        self.monitoring_active = False
        self.monitor_thread = None
        
    def optimize_system(self):
        """Aplicar otimizações completas do sistema"""
        logger.info("Aplicando otimizações avançadas de recursos")
        
        # Configurações de ambiente para máxima eficiência
        env_settings = {
            "OMP_NUM_THREADS": "2",
            "MKL_NUM_THREADS": "2", 
            "OPENBLAS_NUM_THREADS": "2",
            "TOKENIZERS_PARALLELISM": "false",
            "WHISPER_CACHE_DIR": "temp/.whisper_cache",
            "TRANSFORMERS_CACHE": "temp/.transformers_cache"
        }
        
        for key, value in env_settings.items():
            os.environ[key] = value
        
        # Criar diretórios de cache
        for cache_dir in ["temp/.whisper_cache", "temp/.transformers_cache"]:
            Path(cache_dir).mkdir(parents=True, exist_ok=True)
            
        # Limpeza de memória
        self.cleanup_memory()
        
        # Configurar processo
        self.configure_process()
        
        logger.info("Otimizações aplicadas com sucesso")
    
    def cleanup_memory(self):
        """Limpeza agressiva de memória"""
        gc.collect()
        
        # Limpar arquivos temporários antigos
        temp_dir = Path("temp")
        current_time = time.time()
        
        for file_path in temp_dir.glob("*"):
            if file_path.is_file():
                try:
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > 7200:  # 2 horas
                        file_path.unlink()
                        logger.info(f"Arquivo antigo removido: {file_path.name}")
                except:
                    pass
    
    def configure_process(self):
        """Configurar processo para eficiência"""
        try:
            process = psutil.Process()
            
            # Reduzir prioridade se necessário
            if hasattr(os, 'nice'):
                try:
                    os.nice(5)
                    logger.info("Prioridade do processo ajustada")
                except:
                    pass
            
            # Configurar afinidade se possível
            cpu_count = psutil.cpu_count()
            if cpu_count > 1:
                try:
                    available_cores = list(range(min(2, cpu_count)))
                    process.cpu_affinity(available_cores)
                    logger.info(f"CPU afinidade configurada: {available_cores}")
                except:
                    pass
                    
        except Exception as e:
            logger.warning(f"Aviso na configuração: {e}")
    
    def start_monitoring(self):
        """Iniciar monitoramento de recursos"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("Monitoramento de recursos iniciado")
    
    def stop_monitoring(self):
        """Parar monitoramento"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
    
    def _monitor_loop(self):
        """Loop de monitoramento"""
        while self.monitoring_active:
            try:
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                cpu_percent = process.cpu_percent()
                
                if memory_mb > 800:  # > 800MB
                    logger.warning(f"Alto uso de memória: {memory_mb:.1f}MB")
                    gc.collect()
                
                time.sleep(60)  # Verificar a cada minuto
            except:
                break
    
    def get_system_status(self):
        """Obter status atual do sistema"""
        try:
            process = psutil.Process()
            return {
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "cpu_percent": process.cpu_percent(),
                "pid": process.pid,
                "num_threads": process.num_threads(),
                "status": "optimized"
            }
        except Exception as e:
            return {"error": str(e), "status": "error"}

# Instância global
resource_manager = ResourceManager()

def apply_optimizations():
    """Aplicar todas as otimizações"""
    resource_manager.optimize_system()
    resource_manager.start_monitoring()
    return resource_manager.get_system_status()

def get_status():
    """Obter status dos recursos"""
    return resource_manager.get_system_status()

if __name__ == "__main__":
    status = apply_optimizations()
    print(f"Sistema otimizado: {status}")