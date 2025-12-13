"""
Sistema de Monitoramento e Métricas para Agentes Jurídicos
Implementa tracking de performance, qualidade e custos
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics
import psutil

logger = logging.getLogger(__name__)

@dataclass
class QueryMetrics:
    """Métricas de uma consulta específica"""
    query_id: str
    legal_area: str
    query_text: str
    response_time: float
    tokens_used: int
    cost: float
    accuracy_score: float
    user_satisfaction: Optional[float]
    model_used: str
    cache_hit: bool
    hallucination_detected: bool
    consensus_score: Optional[float]
    timestamp: datetime

@dataclass
class AgentPerformance:
    """Performance de um agente específico"""
    agent_id: str
    legal_area: str
    total_queries: int
    avg_response_time: float
    avg_accuracy: float
    avg_satisfaction: float
    total_cost: float
    cache_hit_rate: float
    hallucination_rate: float
    uptime_percentage: float
    last_active: datetime

class AgentMonitoringSystem:
    """
    Sistema de monitoramento avançado para agentes jurídicos
    Coleta e analisa métricas de performance, qualidade e custos
    """
    
    def __init__(self):
        # Armazenamento de métricas (últimos 30 dias)
        self.query_metrics: deque = deque(maxlen=10000)
        self.agent_performance: Dict[str, AgentPerformance] = {}
        
        # Métricas agregadas por período
        self.daily_metrics: Dict[str, Dict] = defaultdict(dict)
        self.weekly_metrics: Dict[str, Dict] = defaultdict(dict)
        self.monthly_metrics: Dict[str, Dict] = defaultdict(dict)
        
        # Alertas e thresholds
        self.alert_thresholds = {
            "response_time": 30.0,      # segundos
            "accuracy_drop": 0.8,       # abaixo de 80%
            "satisfaction_drop": 0.7,   # abaixo de 70%
            "hallucination_rate": 0.1,  # acima de 10%
            "cost_spike": 2.0,          # 2x do custo médio
            "uptime": 0.95              # abaixo de 95%
        }
        
        # Histórico de alertas
        self.active_alerts: List[Dict] = []
        
        # Sistema de custos
        self.cost_tracker = {
            "daily_budget": 100.0,      # USD por dia
            "monthly_budget": 3000.0,   # USD por mês
            "current_daily_cost": 0.0,
            "current_monthly_cost": 0.0
        }
        
        logger.info("📊 Sistema de monitoramento inicializado")
    
    def record_query(self, query_id: str, legal_area: str, query_text: str,
                    response_time: float, tokens_used: int, cost: float,
                    accuracy_score: float, model_used: str, cache_hit: bool = False,
                    hallucination_detected: bool = False, consensus_score: Optional[float] = None,
                    user_satisfaction: Optional[float] = None):
        """
        Registra métricas de uma consulta
        """
        try:
            metrics = QueryMetrics(
                query_id=query_id,
                legal_area=legal_area,
                query_text=query_text,
                response_time=response_time,
                tokens_used=tokens_used,
                cost=cost,
                accuracy_score=accuracy_score,
                user_satisfaction=user_satisfaction,
                model_used=model_used,
                cache_hit=cache_hit,
                hallucination_detected=hallucination_detected,
                consensus_score=consensus_score,
                timestamp=datetime.now()
            )
            
            # Adicionar às métricas
            self.query_metrics.append(metrics)
            
            # Atualizar métricas agregadas
            self._update_aggregated_metrics(metrics)
            
            # Atualizar performance do agente
            self._update_agent_performance(legal_area, metrics)
            
            # Verificar alertas
            self._check_alerts(metrics)
            
            # Atualizar custos
            self._update_cost_tracking(cost)
            
            logger.debug(f"📈 Métricas registradas para consulta {query_id}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar métricas: {e}")
    
    def _update_aggregated_metrics(self, metrics: QueryMetrics):
        """Atualiza métricas agregadas por período"""
        try:
            today = metrics.timestamp.date().isoformat()
            week = f"{metrics.timestamp.year}-W{metrics.timestamp.isocalendar()[1]}"
            month = f"{metrics.timestamp.year}-{metrics.timestamp.month:02d}"
            
            # Métricas diárias
            if today not in self.daily_metrics:
                self.daily_metrics[today] = {
                    "total_queries": 0,
                    "total_cost": 0.0,
                    "total_tokens": 0,
                    "response_times": [],
                    "accuracy_scores": [],
                    "legal_areas": defaultdict(int),
                    "models_used": defaultdict(int),
                    "cache_hits": 0,
                    "hallucinations": 0
                }
            
            daily = self.daily_metrics[today]
            daily["total_queries"] += 1
            daily["total_cost"] += metrics.cost
            daily["total_tokens"] += metrics.tokens_used
            daily["response_times"].append(metrics.response_time)
            daily["accuracy_scores"].append(metrics.accuracy_score)
            daily["legal_areas"][metrics.legal_area] += 1
            daily["models_used"][metrics.model_used] += 1
            
            if metrics.cache_hit:
                daily["cache_hits"] += 1
            if metrics.hallucination_detected:
                daily["hallucinations"] += 1
            
            # Replicar para métricas semanais e mensais
            for period_dict, period_key in [(self.weekly_metrics, week), (self.monthly_metrics, month)]:
                if period_key not in period_dict:
                    period_dict[period_key] = {
                        "total_queries": 0,
                        "total_cost": 0.0,
                        "total_tokens": 0,
                        "response_times": [],
                        "accuracy_scores": [],
                        "legal_areas": defaultdict(int),
                        "models_used": defaultdict(int),
                        "cache_hits": 0,
                        "hallucinations": 0
                    }
                
                period = period_dict[period_key]
                period["total_queries"] += 1
                period["total_cost"] += metrics.cost
                period["total_tokens"] += metrics.tokens_used
                period["response_times"].append(metrics.response_time)
                period["accuracy_scores"].append(metrics.accuracy_score)
                period["legal_areas"][metrics.legal_area] += 1
                period["models_used"][metrics.model_used] += 1
                
                if metrics.cache_hit:
                    period["cache_hits"] += 1
                if metrics.hallucination_detected:
                    period["hallucinations"] += 1
                    
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar métricas agregadas: {e}")
    
    def _update_agent_performance(self, legal_area: str, metrics: QueryMetrics):
        """Atualiza performance de um agente específico"""
        try:
            if legal_area not in self.agent_performance:
                self.agent_performance[legal_area] = AgentPerformance(
                    agent_id=legal_area,
                    legal_area=legal_area,
                    total_queries=0,
                    avg_response_time=0.0,
                    avg_accuracy=0.0,
                    avg_satisfaction=0.0,
                    total_cost=0.0,
                    cache_hit_rate=0.0,
                    hallucination_rate=0.0,
                    uptime_percentage=100.0,
                    last_active=datetime.now()
                )
            
            agent = self.agent_performance[legal_area]
            
            # Atualizar métricas incrementalmente
            total_queries = agent.total_queries + 1
            
            # Média móvel para response time
            agent.avg_response_time = (agent.avg_response_time * agent.total_queries + metrics.response_time) / total_queries
            
            # Média móvel para accuracy
            agent.avg_accuracy = (agent.avg_accuracy * agent.total_queries + metrics.accuracy_score) / total_queries
            
            # Média móvel para satisfaction (se disponível)
            if metrics.user_satisfaction is not None:
                current_satisfaction = agent.avg_satisfaction or 0.0
                agent.avg_satisfaction = (current_satisfaction * agent.total_queries + metrics.user_satisfaction) / total_queries
            
            # Atualizar contadores
            agent.total_queries = total_queries
            agent.total_cost += metrics.cost
            agent.last_active = metrics.timestamp
            
            # Calcular taxas
            recent_queries = [m for m in self.query_metrics if m.legal_area == legal_area and 
                            m.timestamp >= datetime.now() - timedelta(days=7)]
            
            if recent_queries:
                cache_hits = sum(1 for m in recent_queries if m.cache_hit)
                hallucinations = sum(1 for m in recent_queries if m.hallucination_detected)
                
                agent.cache_hit_rate = cache_hits / len(recent_queries)
                agent.hallucination_rate = hallucinations / len(recent_queries)
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar performance do agente: {e}")
    
    def _check_alerts(self, metrics: QueryMetrics):
        """Verifica se algum threshold foi ultrapassado"""
        try:
            alerts = []
            
            # Alert por tempo de resposta alto
            if metrics.response_time > self.alert_thresholds["response_time"]:
                alerts.append({
                    "type": "high_response_time",
                    "message": f"Tempo de resposta alto: {metrics.response_time:.2f}s",
                    "legal_area": metrics.legal_area,
                    "severity": "warning",
                    "timestamp": datetime.now()
                })
            
            # Alert por baixa accuracy
            if metrics.accuracy_score < self.alert_thresholds["accuracy_drop"]:
                alerts.append({
                    "type": "low_accuracy",
                    "message": f"Accuracy baixa: {metrics.accuracy_score:.2f}",
                    "legal_area": metrics.legal_area,
                    "severity": "error",
                    "timestamp": datetime.now()
                })
            
            # Alert por alucinação detectada
            if metrics.hallucination_detected:
                alerts.append({
                    "type": "hallucination_detected",
                    "message": "Alucinação detectada na resposta",
                    "legal_area": metrics.legal_area,
                    "severity": "critical",
                    "timestamp": datetime.now()
                })
            
            # Alert por custo alto
            avg_cost = self._get_average_cost(metrics.legal_area)
            if avg_cost and metrics.cost > avg_cost * self.alert_thresholds["cost_spike"]:
                alerts.append({
                    "type": "high_cost",
                    "message": f"Custo anômalo: ${metrics.cost:.4f} (média: ${avg_cost:.4f})",
                    "legal_area": metrics.legal_area,
                    "severity": "warning",
                    "timestamp": datetime.now()
                })
            
            # Adicionar aos alertas ativos
            self.active_alerts.extend(alerts)
            
            # Manter apenas últimos 100 alertas
            if len(self.active_alerts) > 100:
                self.active_alerts = self.active_alerts[-100:]
            
            if alerts:
                logger.warning(f"⚠️ {len(alerts)} alertas gerados para consulta {metrics.query_id}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao verificar alertas: {e}")
    
    def _get_average_cost(self, legal_area: str) -> Optional[float]:
        """Calcula custo médio para uma área jurídica"""
        try:
            recent_queries = [m for m in self.query_metrics if m.legal_area == legal_area and 
                            m.timestamp >= datetime.now() - timedelta(days=7)]
            
            if recent_queries:
                return statistics.mean(m.cost for m in recent_queries)
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular custo médio: {e}")
            return None
    
    def _update_cost_tracking(self, cost: float):
        """Atualiza tracking de custos"""
        try:
            today = datetime.now().date()
            month = datetime.now().replace(day=1).date()
            
            # Resetar custos diários se necessário
            last_update_key = "last_daily_reset"
            if not hasattr(self, last_update_key) or getattr(self, last_update_key) != today:
                self.cost_tracker["current_daily_cost"] = 0.0
                setattr(self, last_update_key, today)
            
            # Resetar custos mensais se necessário
            last_monthly_key = "last_monthly_reset"
            if not hasattr(self, last_monthly_key) or getattr(self, last_monthly_key) != month:
                self.cost_tracker["current_monthly_cost"] = 0.0
                setattr(self, last_monthly_key, month)
            
            # Atualizar custos
            self.cost_tracker["current_daily_cost"] += cost
            self.cost_tracker["current_monthly_cost"] += cost
            
            # Verificar se ultrapassou orçamento
            if self.cost_tracker["current_daily_cost"] > self.cost_tracker["daily_budget"]:
                self.active_alerts.append({
                    "type": "budget_exceeded",
                    "message": f"Orçamento diário excedido: ${self.cost_tracker['current_daily_cost']:.2f}",
                    "severity": "critical",
                    "timestamp": datetime.now()
                })
                
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar custos: {e}")
    
    def get_performance_summary(self, period: str = "today") -> Dict[str, Any]:
        """
        Retorna resumo de performance para o período especificado
        """
        try:
            if period == "today":
                today = datetime.now().date().isoformat()
                metrics_data = self.daily_metrics.get(today, {})
            elif period == "week":
                week = f"{datetime.now().year}-W{datetime.now().isocalendar()[1]}"
                metrics_data = self.weekly_metrics.get(week, {})
            elif period == "month":
                month = f"{datetime.now().year}-{datetime.now().month:02d}"
                metrics_data = self.monthly_metrics.get(month, {})
            else:
                metrics_data = {}
            
            if not metrics_data:
                return {"error": "Sem dados para o período especificado"}
            
            # Calcular médias
            avg_response_time = statistics.mean(metrics_data.get("response_times", [0]))
            avg_accuracy = statistics.mean(metrics_data.get("accuracy_scores", [0]))
            
            cache_hit_rate = (metrics_data.get("cache_hits", 0) / 
                             max(metrics_data.get("total_queries", 1), 1))
            
            hallucination_rate = (metrics_data.get("hallucinations", 0) / 
                                 max(metrics_data.get("total_queries", 1), 1))
            
            return {
                "period": period,
                "total_queries": metrics_data.get("total_queries", 0),
                "total_cost": round(metrics_data.get("total_cost", 0), 4),
                "total_tokens": metrics_data.get("total_tokens", 0),
                "avg_response_time": round(avg_response_time, 2),
                "avg_accuracy": round(avg_accuracy, 3),
                "cache_hit_rate": round(cache_hit_rate, 3),
                "hallucination_rate": round(hallucination_rate, 3),
                "top_legal_areas": dict(list(metrics_data.get("legal_areas", {}).items())[:5]),
                "models_usage": dict(metrics_data.get("models_used", {})),
                "active_alerts": len([a for a in self.active_alerts if 
                                    a["timestamp"] >= datetime.now() - timedelta(hours=24)])
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resumo: {e}")
            return {"error": str(e)}
    
    def get_agent_performance_report(self, legal_area: Optional[str] = None) -> Dict[str, Any]:
        """
        Retorna relatório detalhado de performance dos agentes
        """
        try:
            if legal_area and legal_area in self.agent_performance:
                # Relatório específico do agente
                agent = self.agent_performance[legal_area]
                return asdict(agent)
            
            else:
                # Relatório de todos os agentes
                agents_report = {}
                
                for area, agent in self.agent_performance.items():
                    agents_report[area] = {
                        "total_queries": agent.total_queries,
                        "avg_response_time": round(agent.avg_response_time, 2),
                        "avg_accuracy": round(agent.avg_accuracy, 3),
                        "avg_satisfaction": round(agent.avg_satisfaction, 3),
                        "total_cost": round(agent.total_cost, 4),
                        "cache_hit_rate": round(agent.cache_hit_rate, 3),
                        "hallucination_rate": round(agent.hallucination_rate, 3),
                        "uptime_percentage": round(agent.uptime_percentage, 1),
                        "last_active": agent.last_active.isoformat(),
                        "status": self._get_agent_status(agent)
                    }
                
                # Ordenar por performance geral
                sorted_agents = sorted(
                    agents_report.items(),
                    key=lambda x: (x[1]["avg_accuracy"] * 0.4 + 
                                  (1 - x[1]["avg_response_time"] / 30) * 0.3 +
                                  x[1]["avg_satisfaction"] * 0.3),
                    reverse=True
                )
                
                return {
                    "total_agents": len(agents_report),
                    "agents": dict(sorted_agents),
                    "top_performer": sorted_agents[0][0] if sorted_agents else None,
                    "system_health": self._get_system_health()
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório de agentes: {e}")
            return {"error": str(e)}
    
    def _get_agent_status(self, agent: AgentPerformance) -> str:
        """Determina status de saúde de um agente"""
        try:
            # Verificar se está ativo recentemente
            if agent.last_active < datetime.now() - timedelta(hours=24):
                return "inactive"
            
            # Verificar métricas críticas
            if agent.hallucination_rate > self.alert_thresholds["hallucination_rate"]:
                return "critical"
            
            if agent.avg_accuracy < self.alert_thresholds["accuracy_drop"]:
                return "degraded"
            
            if agent.avg_response_time > self.alert_thresholds["response_time"]:
                return "slow"
            
            return "healthy"
            
        except Exception:
            return "unknown"
    
    def _get_system_health(self) -> Dict[str, Any]:
        """Calcula saúde geral do sistema"""
        try:
            healthy_agents = sum(1 for agent in self.agent_performance.values() 
                               if self._get_agent_status(agent) == "healthy")
            
            total_agents = len(self.agent_performance)
            health_percentage = (healthy_agents / max(total_agents, 1)) * 100
            
            # Verificar recursos do sistema
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent
            
            return {
                "health_percentage": round(health_percentage, 1),
                "healthy_agents": healthy_agents,
                "total_agents": total_agents,
                "active_alerts": len(self.active_alerts),
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "cost_status": {
                    "daily_used": self.cost_tracker["current_daily_cost"],
                    "daily_budget": self.cost_tracker["daily_budget"],
                    "monthly_used": self.cost_tracker["current_monthly_cost"],
                    "monthly_budget": self.cost_tracker["monthly_budget"]
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular saúde do sistema: {e}")
            return {"error": str(e)}
    
    def get_active_alerts(self, severity: Optional[str] = None) -> List[Dict]:
        """Retorna alertas ativos, opcionalmente filtrados por severidade"""
        try:
            recent_alerts = [alert for alert in self.active_alerts 
                           if alert["timestamp"] >= datetime.now() - timedelta(hours=24)]
            
            if severity:
                recent_alerts = [alert for alert in recent_alerts 
                               if alert["severity"] == severity]
            
            return sorted(recent_alerts, key=lambda x: x["timestamp"], reverse=True)
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter alertas: {e}")
            return []