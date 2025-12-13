import logging
import time
import traceback
import json
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Classe base para todos os agentes do sistema multiagente.
    
    Todos os agentes devem herdar desta classe e implementar o método `_processar`.
    """
    
    def __init__(self, config):
        """
        Inicializa o agente com configuração.
        
        Args:
            config: Dicionário de configuração com parâmetros para o agente
        """
        self.config = config
        self.nome = self.__class__.__name__
        self.logger = logging.getLogger(f"agent.{self.nome}")
        self.debug = config.get("modo_debug", False)
        
        # Inicializa configurações específicas do agente
        self._inicializar()
        
    def _inicializar(self):
        """
        Método para inicialização específica do agente.
        Sobrescreva este método para configurações específicas.
        """
        pass
        
    def should_run(self, data):
        """
        Determina se o agente deve ser executado com base nos dados recebidos.
        
        Args:
            data: Dados recebidos do agente anterior ou entrada inicial
            
        Returns:
            bool: True se o agente deve ser executado, False caso contrário
        """
        return True
        
    def run(self, data):
        """
        Executa o agente e mede o tempo de execução.
        
        Args:
            data: Dados recebidos do agente anterior ou entrada inicial
            
        Returns:
            Dados processados para o próximo agente
        """
        self.logger.info(f"Iniciando execução do agente {self.nome}")
        inicio = time.time()
        
        try:
            if self.debug:
                self.logger.debug(f"Entrada: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
            # Executa o processamento real
            resultado = self._processar(data)
            
            if self.debug:
                self.logger.debug(f"Saída: {json.dumps(resultado, indent=2, ensure_ascii=False)}")
                
            # Captura métricas
            tempo_execucao = round(time.time() - inicio, 3)
            self.logger.info(f"Agente {self.nome} concluído em {tempo_execucao}s")
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro no processamento: {str(e)}", exc_info=True)
            raise
    
    @abstractmethod
    def _processar(self, data):
        """
        Método abstrato que deve ser implementado pelos agentes concretos.
        
        Args:
            data: Dados recebidos do agente anterior
            
        Returns:
            Dados processados para o próximo agente
        """
        pass
