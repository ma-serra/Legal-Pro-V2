"""
Base para agentes jurídicos no sistema multi-agente.
"""

import logging
import time
import os
import json

logger = logging.getLogger('multiagent.agents.juridicos.base')

try:
    from multiagent.core.base_agent import BaseAgent
except ImportError:
    logger.warning("Classe BaseAgent não encontrada. Usando implementação padrão.")
    class BaseAgent:
        def __init__(self, config):
            self.config = config
            self.nome = config.get('nome', self.__class__.__name__)
            self.debug = config.get('modo_debug', False)
            self.logger = logging.getLogger(f'multiagent.agents.{self.nome}')
        
        def _inicializar(self):
            """Método para inicialização específica do agente."""
            pass
            
        def should_run(self, data):
            """Determina se o agente deve ser executado com base nos dados recebidos."""
            return True
            
        def run(self, data):
            """Interface pública para execução do agente."""
            inicio = time.time()
            try:
                resultado = self._processar(data)
                tempo_execucao = round(time.time() - inicio, 3)
                self.logger.info(f"Agente {self.nome} concluído em {tempo_execucao}s")
                return resultado
            except Exception as e:
                self.logger.error(f"Erro no processamento: {str(e)}")
                raise
                
        def _processar(self, data):
            raise NotImplementedError("Método abstrato que deve ser implementado pelos agentes concretos")

class BaseJuridicoAgent(BaseAgent):
    """
    Classe base específica para agentes jurídicos.
    Adiciona funcionalidades específicas para o domínio jurídico,
    mantendo a compatibilidade com o framework de agentes.
    """
    
    def __init__(self, config):
        """Inicializa o agente jurídico com configuração."""
        super().__init__(config)
        # Inicialização específica para agentes jurídicos
        self._inicializar_juridico()
    
    def _inicializar_juridico(self):
        """Inicialização específica para agentes jurídicos."""
        pass
    
    def processar(self, data):
        """Interface pública para compatibilidade com executor de workflow."""
        return self.run(data)
    
    def should_run(self, data):
        """
        Determina se o agente jurídico deve ser executado com base nos dados recebidos.
        """
        # Por padrão, agentes jurídicos sempre executam se receberem dados válidos
        if not data:
            return False
        return True