"""
Sistema de fallback robusto para o sistema multi-agente.

Este módulo fornece mecanismos para lidar com falhas durante o processamento
de agentes, permitindo recuperação, continuidade e degradação graciosa.
"""
import logging
import traceback
from typing import Dict, Any, Optional, List, Union, Callable, Tuple

logger = logging.getLogger(__name__)

class FallbackManager:
    """
    Gerenciador de fallback para o sistema multi-agente.
    
    Fornece mecanismos para registrar estratégias de fallback,
    detectar falhas e aplicar estratégias de recuperação.
    """
    
    def __init__(self):
        """Inicializa o gerenciador de fallback."""
        self.strategies = {}
        self.global_handlers = []
        self.error_history = {}
        
    def register_strategy(self, agent_type: str, strategy_func: Callable):
        """
        Registra uma estratégia de fallback para um tipo específico de agente.
        
        Args:
            agent_type: Tipo de agente para associar a estratégia
            strategy_func: Função de estratégia que será chamada em caso de falha
        """
        self.strategies[agent_type] = strategy_func
        logger.debug(f"Estratégia de fallback registrada para agente tipo '{agent_type}'")
        
    def register_global_handler(self, handler_func: Callable):
        """
        Registra um manipulador global para falhas.
        
        Args:
            handler_func: Função de manipulação que será chamada para qualquer falha
        """
        self.global_handlers.append(handler_func)
        logger.debug(f"Manipulador global de fallback registrado")
        
    def handle_error(self, agent_type: str, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manipula um erro ocorrido durante processamento de um agente.
        
        Args:
            agent_type: Tipo do agente que apresentou falha
            error: Exceção capturada
            context: Contexto da execução (dados, configurações, etc.)
            
        Returns:
            Resultado do processamento de fallback
        """
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc()
        }
        
        # Registra o erro no histórico
        if agent_type not in self.error_history:
            self.error_history[agent_type] = []
            
        self.error_history[agent_type].append(error_info)
        
        # Executa manipuladores globais
        for handler in self.global_handlers:
            try:
                handler(agent_type, error, context)
            except Exception as e:
                logger.error(f"Erro ao executar manipulador global: {str(e)}")
        
        # Verifica se existe estratégia específica para o tipo de agente
        if agent_type in self.strategies:
            try:
                strategy_func = self.strategies[agent_type]
                return strategy_func(error, context)
            except Exception as e:
                logger.error(f"Erro ao executar estratégia de fallback para '{agent_type}': {str(e)}")
        
        # Se não há estratégia específica ou ela falhou, usa estratégia padrão
        return self._default_fallback_strategy(agent_type, error, context)
        
    def _default_fallback_strategy(self, agent_type: str, error: Exception, 
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estratégia de fallback padrão aplicada quando não há estratégia específica.
        
        Args:
            agent_type: Tipo do agente que apresentou falha
            error: Exceção capturada
            context: Contexto da execução
            
        Returns:
            Resultado com informações mínimas essenciais
        """
        logger.warning(f"Usando estratégia de fallback padrão para agente '{agent_type}'")
        
        # Recupera o texto original de entrada
        original_text = context.get("texto", "")
        
        # Prepara resultados mínimos para continuar o fluxo
        result = {
            "fallback_aplicado": True,
            "erro": str(error),
            "tipo_erro": type(error).__name__,
            "resultado_generico": f"Não foi possível processar o conteúdo com o agente do tipo '{agent_type}'.",
            "texto": original_text  # Mantém o texto original para próximos agentes
        }
        
        # Se houver dados parciais no contexto, preserva-os
        if "resultados_parciais" in context:
            result["resultados_parciais"] = context["resultados_parciais"]
            
        # Se houver memória compartilhada, preserva-a
        if "memoria_compartilhada" in context:
            result["memoria_compartilhada"] = context["memoria_compartilhada"]
            
        return result
        
    def get_error_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas de erros ocorridos.
        
        Returns:
            Dicionário com estatísticas de erros por tipo de agente
        """
        stats = {}
        
        for agent_type, errors in self.error_history.items():
            error_types = {}
            
            for error in errors:
                error_type = error["error_type"]
                if error_type not in error_types:
                    error_types[error_type] = 0
                error_types[error_type] += 1
                
            stats[agent_type] = {
                "total_errors": len(errors),
                "error_types": error_types
            }
            
        return stats
        
    def clear_history(self, agent_type: Optional[str] = None):
        """
        Limpa o histórico de erros.
        
        Args:
            agent_type: Se fornecido, limpa apenas o histórico deste tipo de agente
        """
        if agent_type:
            self.error_history.pop(agent_type, None)
        else:
            self.error_history = {}

# Instância global do gerenciador de fallback
_fallback_manager = FallbackManager()

def get_fallback_manager() -> FallbackManager:
    """
    Obtém a instância global do gerenciador de fallback.
    
    Returns:
        Instância global do FallbackManager
    """
    return _fallback_manager

# Exemplos de estratégias específicas para tipos comuns de agentes
def estrategia_extrator(error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
    """Estratégia de fallback para o ExtratorAgent."""
    texto = context.get("texto", "")
    
    return {
        "fallback_aplicado": True,
        "erro": str(error),
        "entidades": [],
        "estrutura_identificada": "desconhecida",
        "confianca_extracao": 0.0,
        "texto": texto  # Retorna o texto original para próximos agentes
    }
    
def estrategia_classificador(error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
    """Estratégia de fallback para o ClassificadorAgent."""
    return {
        "fallback_aplicado": True,
        "erro": str(error),
        "classificacao": "indefinida",
        "categorias": [],
        "confianca_classificacao": 0.0,
        "memoria_compartilhada": context.get("memoria_compartilhada", {})
    }
    
def estrategia_analisador(error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
    """Estratégia de fallback para o AnalisadorAgent."""
    return {
        "fallback_aplicado": True,
        "erro": str(error),
        "analises": [],
        "insights": [],
        "confianca_analise": 0.0,
        "memoria_compartilhada": context.get("memoria_compartilhada", {})
    }
    
def estrategia_sintetizador(error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
    """Estratégia de fallback para o SintetizadorAgent."""
    return {
        "fallback_aplicado": True,
        "erro": str(error),
        "sintese": "Não foi possível sintetizar o conteúdo devido a um erro no processamento.",
        "memoria_compartilhada": context.get("memoria_compartilhada", {})
    }
    
def estrategia_formatador(error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
    """Estratégia de fallback para o FormatadorAgent."""
    sintese = context.get("sintese", "Conteúdo não disponível devido a um erro no processamento.")
    
    return {
        "fallback_aplicado": True,
        "erro": str(error),
        "conteudo_formatado": f"<div class='alert alert-warning'>Sistema encontrou um erro na formatação. " 
                          f"Conteúdo recuperado: {sintese}</div>",
        "formato": "html"
    }

# Registra estratégias padrão no gerenciador
_fallback_manager.register_strategy("extrator", estrategia_extrator)
_fallback_manager.register_strategy("classificador", estrategia_classificador)
_fallback_manager.register_strategy("analisador", estrategia_analisador)
_fallback_manager.register_strategy("sintetizador", estrategia_sintetizador)
_fallback_manager.register_strategy("formatador", estrategia_formatador)