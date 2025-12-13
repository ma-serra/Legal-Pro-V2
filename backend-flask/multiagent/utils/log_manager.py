"""
Gerenciador de logs para o sistema multi-agente.
"""
import os
import logging
import datetime
from typing import Dict, Any, Optional, List, Union

# Configuração padrão de logs
DEFAULT_LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(name)s: %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "save_to_file": True,
    "log_dir": "logs",
    "max_file_size_mb": 10,
    "max_files": 5
}

class LogManager:
    """
    Gerenciador de logs para o sistema multi-agente.
    
    Fornece funções para configurar, gerenciar e acessar logs
    de forma centralizada para todo o sistema.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa o gerenciador de logs.
        
        Args:
            config: Configuração de logs (opcional)
        """
        self.config = config or DEFAULT_LOG_CONFIG.copy()
        self.initialized = False
        self.root_logger = logging.getLogger("multiagent")
        self.logs_path = os.path.join(os.getcwd(), self.config["log_dir"])
        
        # Inicialização imediata
        self._setup_logging()
        
    def _setup_logging(self):
        """Configura o sistema de logs"""
        if self.initialized:
            return
            
        # Cria diretório de logs se não existir
        if self.config["save_to_file"] and not os.path.exists(self.logs_path):
            try:
                os.makedirs(self.logs_path)
            except Exception as e:
                print(f"Erro ao criar diretório de logs: {str(e)}")
                self.config["save_to_file"] = False
        
        # Configura logger root
        level = getattr(logging, self.config["level"])
        self.root_logger.setLevel(level)
        
        # Impede propagação para evitar duplicação
        self.root_logger.propagate = False
        
        # Remove handlers existentes para evitar duplicação
        if self.root_logger.handlers:
            for handler in self.root_logger.handlers:
                self.root_logger.removeHandler(handler)
        
        # Cria formatador
        formatter = logging.Formatter(
            fmt=self.config["format"],
            datefmt=self.config["date_format"]
        )
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.root_logger.addHandler(console_handler)
        
        # Handler para arquivo se configurado
        if self.config["save_to_file"]:
            try:
                log_file = os.path.join(
                    self.logs_path, 
                    f"multiagent_{datetime.datetime.now().strftime('%Y%m%d')}.log"
                )
                
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(formatter)
                self.root_logger.addHandler(file_handler)
            except Exception as e:
                self.root_logger.error(f"Não foi possível configurar log em arquivo: {str(e)}")
        
        self.initialized = True
        self.root_logger.info("Gerenciador de logs inicializado para multiagent")
        
    def get_logger(self, name: str):
        """
        Obtém um logger para um componente específico.
        
        Args:
            name: Nome do componente (será prefixado com 'multiagent.')
            
        Returns:
            Logger configurado
        """
        if not name.startswith("multiagent."):
            name = f"multiagent.{name}"
            
        return logging.getLogger(name)
        
    def update_config(self, new_config: Dict[str, Any]):
        """
        Atualiza a configuração de logs.
        
        Args:
            new_config: Nova configuração (será mesclada com a atual)
            
        Returns:
            True se a atualização foi bem-sucedida
        """
        self.config.update(new_config)
        self.initialized = False
        self._setup_logging()
        return True
        
    def list_log_files(self) -> List[Dict[str, Any]]:
        """
        Lista os arquivos de log disponíveis.
        
        Returns:
            Lista de dicionários com informações dos arquivos
        """
        if not os.path.exists(self.logs_path):
            return []
            
        files = []
        for filename in os.listdir(self.logs_path):
            if filename.endswith(".log"):
                file_path = os.path.join(self.logs_path, filename)
                stat = os.stat(file_path)
                
                files.append({
                    "name": filename,
                    "path": file_path,
                    "size": stat.st_size,
                    "created": datetime.datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
                
        # Ordena por data de modificação (mais recente primeiro)
        return sorted(files, key=lambda x: x["modified"], reverse=True)
        
    def get_log_content(self, filename: str, max_lines: int = 1000) -> Optional[str]:
        """
        Obtém o conteúdo de um arquivo de log.
        
        Args:
            filename: Nome do arquivo (sem caminho)
            max_lines: Número máximo de linhas a retornar
            
        Returns:
            Conteúdo do arquivo ou None se não encontrado
        """
        file_path = os.path.join(self.logs_path, filename)
        
        if not os.path.exists(file_path) or not filename.endswith(".log"):
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Lê as últimas linhas do arquivo
                lines = f.readlines()
                if len(lines) > max_lines:
                    lines = lines[-max_lines:]
                return ''.join(lines)
        except Exception as e:
            self.root_logger.error(f"Erro ao ler arquivo de log {filename}: {str(e)}")
            return None
            
    def clear_logs(self) -> bool:
        """
        Limpa os arquivos de log antigos.
        
        Returns:
            True se a operação foi bem-sucedida
        """
        if not os.path.exists(self.logs_path):
            return True
            
        try:
            # Mantém apenas o arquivo de log atual
            current_date = datetime.datetime.now().strftime('%Y%m%d')
            current_log = f"multiagent_{current_date}.log"
            
            for filename in os.listdir(self.logs_path):
                if filename.endswith(".log") and filename != current_log:
                    os.remove(os.path.join(self.logs_path, filename))
                    
            return True
        except Exception as e:
            self.root_logger.error(f"Erro ao limpar logs: {str(e)}")
            return False
            
    def get_config(self) -> Dict[str, Any]:
        """
        Obtém a configuração atual de logs.
        
        Returns:
            Dicionário com a configuração atual
        """
        return self.config.copy()

# Instância global do gerenciador de logs
_log_manager = LogManager()

def get_log_manager() -> LogManager:
    """
    Obtém a instância global do gerenciador de logs.
    
    Returns:
        Instância global do LogManager
    """
    return _log_manager