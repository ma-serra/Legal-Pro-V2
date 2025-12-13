"""
Otimizador Avançado do Sistema
Implementa otimizações de memória, CPU e configurações para melhor desempenho
"""

import os
import gc
import sys
import psutil
import logging
import threading
import time
from pathlib import Path
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemOptimizer:
    """Otimizador avançado do sistema para melhor desempenho"""
    
    def __init__(self):
        self.original_settings = {}
        self.cleanup_threads = []
        
    def optimize_memory(self):
        """Otimizar uso de memória"""
        logger.info("🔧 Aplicando otimizações de memória...")
        
        # Limpeza agressiva de garbage collection
        gc.collect()
        gc.disable()  # Desabilitar GC automático para controle manual
        
        # Configurar limite de memória para processos
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            logger.info(f"💾 Memória atual: {memory_info.rss / 1024 / 1024:.1f} MB")
            
            # Limitar uso de memória se necessário
            if memory_info.rss > 1024 * 1024 * 1024:  # > 1GB
                gc.enable()
                gc.collect()
                logger.info("🧹 Limpeza de memória executada")
                
        except Exception as e:
            logger.warning(f"Aviso na otimização de memória: {e}")
    
    def optimize_cpu(self):
        """Otimizar uso de CPU"""
        logger.info("⚡ Aplicando otimizações de CPU...")
        
        try:
            # Definir prioridade do processo
            process = psutil.Process()
            
            # Reduzir prioridade para não sobrecarregar sistema
            if hasattr(os, 'nice'):
                os.nice(5)
                logger.info("📉 Prioridade do processo reduzida")
            
            # Configurar afinidade de CPU se disponível
            cpu_count = psutil.cpu_count()
            if cpu_count > 1:
                # Usar apenas metade dos cores disponíveis
                available_cores = list(range(min(2, cpu_count)))
                try:
                    process.cpu_affinity(available_cores)
                    logger.info(f"🎯 CPU afinidade definida para cores: {available_cores}")
                except:
                    logger.info("ℹ️ Afinidade de CPU não configurável neste sistema")
                    
        except Exception as e:
            logger.warning(f"Aviso na otimização de CPU: {e}")
    
    def optimize_io(self):
        """Otimizar operações de I/O"""
        logger.info("💿 Aplicando otimizações de I/O...")
        
        try:
            # Configurar diretório temporário otimizado
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)
            
            # Limpar arquivos antigos (mais de 1 hora)
            current_time = time.time()
            for file_path in temp_dir.glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > 3600:  # 1 hora
                        try:
                            file_path.unlink()
                            logger.info(f"🗑️ Arquivo antigo removido: {file_path.name}")
                        except:
                            pass
            
            # Configurar buffer de I/O
            sys.stderr.reconfigure(line_buffering=True)
            sys.stdout.reconfigure(line_buffering=True)
            
        except Exception as e:
            logger.warning(f"Aviso na otimização de I/O: {e}")
    
    def optimize_whisper_settings(self):
        """Configurações específicas para Whisper"""
        logger.info("🎤 Aplicando otimizações específicas do Whisper...")
        
        # Configurar variáveis de ambiente para Whisper
        os.environ["WHISPER_CACHE_DIR"] = str(Path("temp/.whisper_cache"))
        os.environ["TRANSFORMERS_CACHE"] = str(Path("temp/.transformers_cache"))
        
        # Limitar threads do PyTorch
        os.environ["OMP_NUM_THREADS"] = "2"
        os.environ["MKL_NUM_THREADS"] = "2"
        os.environ["OPENBLAS_NUM_THREADS"] = "2"
        
        # Configurar modo de baixo consumo
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"
        
        logger.info("⚙️ Variáveis de ambiente do Whisper configuradas")
    
    def start_memory_monitor(self):
        """Iniciar monitoramento contínuo de memória"""
        def monitor_memory():
            while True:
                try:
                    process = psutil.Process()
                    memory_mb = process.memory_info().rss / 1024 / 1024
                    
                    if memory_mb > 800:  # Limite de 800MB
                        logger.warning(f"⚠️ Alto uso de memória: {memory_mb:.1f} MB")
                        gc.collect()
                        
                    time.sleep(30)  # Verificar a cada 30 segundos
                except:
                    break
        
        monitor_thread = threading.Thread(target=monitor_memory, daemon=True)
        monitor_thread.start()
        self.cleanup_threads.append(monitor_thread)
        logger.info("👁️ Monitor de memória iniciado")
    
    def apply_all_optimizations(self):
        """Aplicar todas as otimizações"""
        logger.info("🚀 Iniciando otimizações avançadas do sistema...")
        
        self.optimize_memory()
        self.optimize_cpu()
        self.optimize_io()
        self.optimize_whisper_settings()
        self.start_memory_monitor()
        
        # Criar diretórios necessários
        for dir_name in [".whisper_cache", ".transformers_cache"]:
            Path(f"temp/{dir_name}").mkdir(parents=True, exist_ok=True)
        
        logger.info("✅ Todas as otimizações aplicadas com sucesso!")
        
        # Mostrar status do sistema
        self.show_system_status()
    
    def show_system_status(self):
        """Mostrar status atual do sistema"""
        try:
            process = psutil.Process()
            cpu_percent = process.cpu_percent()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            logger.info("📊 Status do Sistema:")
            logger.info(f"   💾 Memória: {memory_mb:.1f} MB")
            logger.info(f"   ⚡ CPU: {cpu_percent:.1f}%")
            logger.info(f"   🏷️ PID: {process.pid}")
            
        except Exception as e:
            logger.warning(f"Erro ao obter status: {e}")

def main():
    """Função principal para aplicar otimizações"""
    optimizer = SystemOptimizer()
    optimizer.apply_all_optimizations()
    return optimizer

if __name__ == "__main__":
    main()