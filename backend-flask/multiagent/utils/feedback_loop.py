"""
Sistema de feedback loop para o sistema multi-agente.

Este módulo fornece mecanismos para coletar, analisar e aplicar feedback
dos usuários e do próprio sistema para melhorar a qualidade dos resultados.
"""
import logging
import time
import datetime
import json
from typing import Dict, Any, Optional, List, Union, Callable

logger = logging.getLogger(__name__)

class FeedbackManager:
    """
    Gerenciador de feedback para o sistema multi-agente.
    
    Fornece mecanismos para registrar feedback, avaliar métricas
    de desempenho e ajustar parâmetros dos agentes dinamicamente.
    """
    
    def __init__(self):
        """Inicializa o gerenciador de feedback."""
        self.feedback_items = []
        self.metrics = {
            "executados": 0,
            "sucessos": 0,
            "falhas": 0,
            "tempo_medio": 0.0,
            "pontuacao_media": 0.0,
            "agentes": {}
        }
        self.callbacks = {}
        
    def register_feedback(self, item: Dict[str, Any]) -> int:
        """
        Registra um item de feedback no sistema.
        
        Args:
            item: Dicionário com dados do feedback
                Deve conter pelo menos: execucao_id, usuario_id, comentario, avaliacao
                
        Returns:
            ID do feedback registrado
        """
        if not isinstance(item, dict):
            raise ValueError("Item de feedback deve ser um dicionário")
            
        # Adiciona campos obrigatórios se não existirem
        if "timestamp" not in item:
            item["timestamp"] = datetime.datetime.now().isoformat()
            
        if "id" not in item:
            item["id"] = len(self.feedback_items) + 1
            
        required_fields = ["execucao_id", "avaliacao"]
        for field in required_fields:
            if field not in item:
                raise ValueError(f"Item de feedback deve conter o campo '{field}'")
        
        # Registra o feedback
        self.feedback_items.append(item)
        
        # Atualiza métricas
        self._update_metrics(item)
        
        # Notifica callbacks registrados
        self._notify_callbacks(item)
        
        return item["id"]
        
    def _update_metrics(self, feedback_item: Dict[str, Any]):
        """
        Atualiza métricas baseadas no feedback recebido.
        
        Args:
            feedback_item: Item de feedback registrado
        """
        # Incrementa contador de execuções
        self.metrics["executados"] += 1
        
        # Verifica se a execução foi bem-sucedida
        avaliacao = feedback_item.get("avaliacao", 0)
        passou_limiar = avaliacao >= 3  # Consideramos sucesso acima de 3 (escala 1-5)
        
        if passou_limiar:
            self.metrics["sucessos"] += 1
        else:
            self.metrics["falhas"] += 1
            
        # Atualiza pontuação média
        n = self.metrics["executados"]
        avg_old = self.metrics["pontuacao_media"]
        self.metrics["pontuacao_media"] = ((n - 1) * avg_old + avaliacao) / n
        
        # Atualiza métricas por agente
        if "agentes_avaliados" in feedback_item:
            for agente_info in feedback_item["agentes_avaliados"]:
                nome_agente = agente_info.get("nome", "desconhecido")
                tipo_agente = agente_info.get("tipo", "desconhecido")
                avaliacao_agente = agente_info.get("avaliacao", 0)
                tempo_agente = agente_info.get("tempo", 0.0)
                
                # Cria entrada para o agente se não existir
                agente_key = f"{tipo_agente}:{nome_agente}"
                if agente_key not in self.metrics["agentes"]:
                    self.metrics["agentes"][agente_key] = {
                        "tipo": tipo_agente,
                        "nome": nome_agente,
                        "executados": 0,
                        "sucessos": 0,
                        "falhas": 0,
                        "tempo_medio": 0.0,
                        "pontuacao_media": 0.0
                    }
                    
                # Atualiza métricas do agente
                agent_metrics = self.metrics["agentes"][agente_key]
                agent_metrics["executados"] += 1
                
                if avaliacao_agente >= 3:
                    agent_metrics["sucessos"] += 1
                else:
                    agent_metrics["falhas"] += 1
                    
                # Atualiza tempo médio
                n_agent = agent_metrics["executados"]
                avg_time_old = agent_metrics["tempo_medio"]
                agent_metrics["tempo_medio"] = ((n_agent - 1) * avg_time_old + tempo_agente) / n_agent
                
                # Atualiza pontuação média
                avg_score_old = agent_metrics["pontuacao_media"]
                agent_metrics["pontuacao_media"] = ((n_agent - 1) * avg_score_old + avaliacao_agente) / n_agent
                
    def _notify_callbacks(self, feedback_item: Dict[str, Any]):
        """
        Notifica callbacks registrados sobre novo feedback.
        
        Args:
            feedback_item: Item de feedback registrado
        """
        execucao_id = feedback_item.get("execucao_id")
        
        # Notifica callbacks gerais
        if "global" in self.callbacks:
            for callback in self.callbacks["global"]:
                try:
                    callback(feedback_item)
                except Exception as e:
                    logger.error(f"Erro ao executar callback de feedback: {str(e)}")
                    
        # Notifica callbacks específicos para a execução
        if execucao_id and execucao_id in self.callbacks:
            for callback in self.callbacks[execucao_id]:
                try:
                    callback(feedback_item)
                except Exception as e:
                    logger.error(f"Erro ao executar callback para execução {execucao_id}: {str(e)}")
                    
    def register_callback(self, callback: Callable, execucao_id: Optional[str] = None):
        """
        Registra uma função de callback para notificação de feedback.
        
        Args:
            callback: Função a ser chamada quando um feedback for registrado
            execucao_id: ID da execução específica ou None para callback global
        """
        key = execucao_id if execucao_id else "global"
        
        if key not in self.callbacks:
            self.callbacks[key] = []
            
        self.callbacks[key].append(callback)
        
    def get_metrics(self) -> Dict[str, Any]:
        """
        Obtém métricas atuais de feedback.
        
        Returns:
            Dicionário com métricas atualizadas
        """
        # Calcula taxa de sucesso
        total = self.metrics["executados"]
        if total > 0:
            taxa_sucesso = self.metrics["sucessos"] / total * 100
        else:
            taxa_sucesso = 0.0
            
        # Adiciona timestamp e taxa de sucesso
        metrics = self.metrics.copy()
        metrics["timestamp"] = datetime.datetime.now().isoformat()
        metrics["taxa_sucesso"] = taxa_sucesso
        
        return metrics
        
    def get_feedback_for_execution(self, execucao_id: str) -> List[Dict[str, Any]]:
        """
        Obtém todos os feedbacks para uma execução específica.
        
        Args:
            execucao_id: ID da execução
            
        Returns:
            Lista de feedbacks para a execução
        """
        return [item for item in self.feedback_items if item.get("execucao_id") == execucao_id]
        
    def get_agent_recommendations(self, tipo_agente: str) -> Dict[str, Any]:
        """
        Obtém recomendações para ajuste de parâmetros de um tipo de agente.
        
        Args:
            tipo_agente: Tipo de agente para obter recomendações
            
        Returns:
            Dicionário com recomendações de ajustes
        """
        # Filtra métricas apenas para o tipo de agente solicitado
        agent_metrics = {}
        
        for key, metrics in self.metrics["agentes"].items():
            if metrics["tipo"] == tipo_agente:
                agent_metrics[key] = metrics
                
        # Se não houver dados suficientes, retorna recomendação default
        if not agent_metrics or all(m["executados"] < 5 for m in agent_metrics.values()):
            return {
                "tipo_agente": tipo_agente,
                "recomendacoes": [
                    {
                        "parametro": "temperatura",
                        "valor_recomendado": 0.7,
                        "confianca": 0.5,
                        "motivo": "Valor default sem dados suficientes"
                    }
                ],
                "confianca_geral": 0.5,
                "dados_suficientes": False
            }
            
        # Analisa métricas e gera recomendações
        # Este é um exemplo simplificado - em produção, usaria algoritmos mais sofisticados
        recomendacoes = []
        
        # Exemplo: se pontuação média baixa, recomenda diminuir temperatura
        avg_score = sum(m["pontuacao_media"] for m in agent_metrics.values()) / len(agent_metrics)
        
        if avg_score < 3.0:
            recomendacoes.append({
                "parametro": "temperatura",
                "valor_recomendado": 0.5,  # Mais determinístico
                "confianca": 0.7,
                "motivo": "Pontuação média baixa sugere resultados inconsistentes"
            })
        elif avg_score > 4.0:
            recomendacoes.append({
                "parametro": "temperatura",
                "valor_recomendado": 0.7,  # Mais criativo
                "confianca": 0.6,
                "motivo": "Pontuação média alta permite mais criatividade"
            })
            
        # Exemplo: se tempo médio alto, recomenda otimizações
        avg_time = sum(m["tempo_medio"] for m in agent_metrics.values()) / len(agent_metrics)
        
        if avg_time > 5.0:  # segundos
            recomendacoes.append({
                "parametro": "max_tokens",
                "valor_recomendado": 1000,
                "confianca": 0.6,
                "motivo": "Tempo de execução elevado sugere limitar tamanho da resposta"
            })
            
        # Calcula confiança geral
        confianca_geral = min(0.8, sum(r["confianca"] for r in recomendacoes) / len(recomendacoes) if recomendacoes else 0.5)
            
        return {
            "tipo_agente": tipo_agente,
            "recomendacoes": recomendacoes,
            "confianca_geral": confianca_geral,
            "dados_suficientes": True
        }
        
    def clear_feedback_history(self, older_than_days: Optional[int] = None):
        """
        Limpa o histórico de feedback.
        
        Args:
            older_than_days: Se fornecido, limpa apenas feedbacks mais antigos que este número de dias
        """
        if older_than_days is None:
            self.feedback_items = []
            return
            
        # Calcula a data limite
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=older_than_days)
        cutoff_str = cutoff_date.isoformat()
        
        # Filtra apenas itens mais recentes que o limite
        self.feedback_items = [
            item for item in self.feedback_items 
            if item.get("timestamp", "9999") > cutoff_str
        ]
        
    def export_feedback_data(self) -> Dict[str, Any]:
        """
        Exporta todos os dados de feedback.
        
        Returns:
            Dicionário com todos os dados de feedback
        """
        return {
            "metrics": self.get_metrics(),
            "feedback_items": self.feedback_items,
            "exported_at": datetime.datetime.now().isoformat()
        }
        
    def import_feedback_data(self, data: Dict[str, Any]) -> bool:
        """
        Importa dados de feedback.
        
        Args:
            data: Dados de feedback exportados anteriormente
            
        Returns:
            True se a importação foi bem-sucedida
        """
        try:
            if "feedback_items" in data:
                # Adiciona apenas itens novos
                existing_ids = {item["id"] for item in self.feedback_items if "id" in item}
                
                for item in data["feedback_items"]:
                    if "id" in item and item["id"] not in existing_ids:
                        self.feedback_items.append(item)
                        
            # Recalcula métricas para dados importados
            self._recalculate_metrics()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao importar dados de feedback: {str(e)}")
            return False
            
    def _recalculate_metrics(self):
        """Recalcula todas as métricas com base nos feedbacks registrados."""
        # Reinicia métricas
        self.metrics = {
            "executados": 0,
            "sucessos": 0,
            "falhas": 0,
            "tempo_medio": 0.0,
            "pontuacao_media": 0.0,
            "agentes": {}
        }
        
        # Recalcula com base em todos os feedbacks
        for item in self.feedback_items:
            self._update_metrics(item)
        
# Instância global do gerenciador de feedback
_feedback_manager = FeedbackManager()

def get_feedback_manager() -> FeedbackManager:
    """
    Obtém a instância global do gerenciador de feedback.
    
    Returns:
        Instância global do FeedbackManager
    """
    return _feedback_manager