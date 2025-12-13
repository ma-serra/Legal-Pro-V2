"""
Sistema de Embedding Híbrido para Otimização de Agentes Jurídicos
Implementa roteamento inteligente baseado na complexidade da consulta
"""

import os
import re
import logging
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class QueryComplexity(Enum):
    """Enum para classificação de complexidade da consulta"""
    BASIC = "basic"
    COMPLEX = "complex" 
    CRITICAL = "critical"

@dataclass
class EmbeddingConfig:
    """Configuração para cada tipo de embedding"""
    model_name: str
    cost_per_token: float
    performance_score: float
    recommended_use: str

class HybridEmbeddingSystem:
    """
    Sistema de embedding híbrido com roteamento inteligente
    Seleciona automaticamente o melhor modelo baseado na complexidade
    """
    
    def __init__(self):
        self.embedding_configs = {
            QueryComplexity.BASIC: EmbeddingConfig(
                model_name="text-embedding-3-small",
                cost_per_token=0.00002,
                performance_score=0.85,
                recommended_use="Consultas simples, definições, conceitos básicos"
            ),
            QueryComplexity.COMPLEX: EmbeddingConfig(
                model_name="text-embedding-3-large", 
                cost_per_token=0.00013,
                performance_score=0.95,
                recommended_use="Análises complexas, precedentes, aplicação prática"
            ),
            QueryComplexity.CRITICAL: EmbeddingConfig(
                model_name="text-embedding-3-large",
                cost_per_token=0.00013,
                performance_score=0.98,
                recommended_use="Pareceres críticos, contenciosos, recursos"
            )
        }
        
        # Palavras-chave para classificação automática
        self.basic_keywords = [
            "o que é", "definição", "conceito", "significado", "explique",
            "defina", "entenda", "compreenda", "básico", "simples"
        ]
        
        self.complex_keywords = [
            "aplicação prática", "precedentes", "análise", "interpretação",
            "jurisprudência", "doutrinas", "casos práticos", "aplicar",
            "implementar", "estratégia", "abordagem", "metodologia"
        ]
        
        self.critical_keywords = [
            "parecer", "contencioso", "recurso", "ação judicial", "defesa",
            "petição", "sentença", "decisão", "tribunal", "supremo",
            "constitucional", "extraordinário", "especial", "urgente",
            "liminar", "mandado", "habeas corpus", "apelação"
        ]
        
        # Cache de classificações
        self.classification_cache = {}
        
        # Inicializar cliente OpenAI para embeddings
        self._initialize_openai_client()
    
    def _initialize_openai_client(self):
        """Inicializa cliente OpenAI para embeddings"""
        try:
            from openai import OpenAI
            self.openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
            logger.info("✅ Cliente OpenAI inicializado para embeddings híbridos")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar cliente OpenAI: {e}")
            self.openai_client = None
    
    def classify_query_complexity(self, query: str) -> QueryComplexity:
        """
        Classifica automaticamente a complexidade da consulta
        usando palavras-chave e análise semântica
        """
        if not query:
            return QueryComplexity.BASIC
        
        # Verificar cache primeiro
        query_hash = hashlib.md5(query.encode()).hexdigest()
        if query_hash in self.classification_cache:
            return self.classification_cache[query_hash]
        
        query_lower = query.lower()
        
        # Contadores de pontuação por complexidade
        basic_score = 0
        complex_score = 0
        critical_score = 0
        
        # Análise por palavras-chave
        for keyword in self.basic_keywords:
            if keyword in query_lower:
                basic_score += 1
        
        for keyword in self.complex_keywords:
            if keyword in query_lower:
                complex_score += 2  # Peso maior para complexidade média
        
        for keyword in self.critical_keywords:
            if keyword in query_lower:
                critical_score += 3  # Peso maior para complexidade crítica
        
        # Análise adicional por padrões
        # Perguntas simples (começam com "o que", "qual", "onde")
        if re.match(r'^(o que|qual|onde|quando|quem)\s', query_lower):
            basic_score += 1
        
        # Análises complexas (contêm "como", "porque", "análise")
        if re.search(r'(como|porque|por que|análise|avalie)', query_lower):
            complex_score += 1
        
        # Casos críticos (contêm números de processo, artigos de lei)
        if re.search(r'(\d+\.\d+\.\d+\.\d+\.\d+|\d+/\d+|art\.?\s*\d+)', query_lower):
            critical_score += 2
        
        # Determinar complexidade final
        if critical_score > max(basic_score, complex_score):
            complexity = QueryComplexity.CRITICAL
        elif complex_score > basic_score:
            complexity = QueryComplexity.COMPLEX
        else:
            complexity = QueryComplexity.BASIC
        
        # Armazenar no cache
        self.classification_cache[query_hash] = complexity
        
        logger.info(f"🎯 Consulta classificada como: {complexity.value}")
        logger.debug(f"Scores - Básica: {basic_score}, Complexa: {complex_score}, Crítica: {critical_score}")
        
        return complexity
    
    def select_embedding_model(self, query: str) -> Tuple[str, EmbeddingConfig]:
        """
        Seleciona o modelo de embedding ideal baseado na complexidade
        Retorna o nome do modelo e sua configuração
        """
        complexity = self.classify_query_complexity(query)
        config = self.embedding_configs[complexity]
        
        logger.info(f"📊 Modelo selecionado: {config.model_name} (Complexidade: {complexity.value})")
        
        return config.model_name, config
    
    def get_embedding(self, text: str, model_override: Optional[str] = None) -> Optional[List[float]]:
        """
        Gera embedding usando o modelo apropriado
        Permite override manual do modelo se necessário
        """
        if not self.openai_client:
            logger.error("❌ Cliente OpenAI não disponível para embeddings")
            return None
        
        try:
            # Selecionar modelo automaticamente ou usar override
            if model_override:
                model_name = model_override
                logger.info(f"🔧 Usando modelo override: {model_name}")
            else:
                model_name, config = self.select_embedding_model(text)
            
            # Gerar embedding
            response = self.openai_client.embeddings.create(
                model=model_name,
                input=text,
                encoding_format="float"
            )
            
            embedding = response.data[0].embedding
            
            logger.info(f"✅ Embedding gerado com sucesso - Modelo: {model_name}, Dimensões: {len(embedding)}")
            
            return embedding
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar embedding: {e}")
            return None
    
    def get_hybrid_embeddings(self, text: str) -> Dict[str, List[float]]:
        """
        Gera múltiplos embeddings para casos críticos
        Retorna embeddings de diferentes modelos para validação cruzada
        """
        complexity = self.classify_query_complexity(text)
        embeddings = {}
        
        if complexity == QueryComplexity.CRITICAL:
            # Para casos críticos, usar múltiplos modelos
            models = ["text-embedding-3-large", "text-embedding-ada-002"]
            
            for model in models:
                embedding = self.get_embedding(text, model_override=model)
                if embedding:
                    embeddings[model] = embedding
            
            logger.info(f"🎯 Embeddings híbridos gerados para caso crítico: {list(embeddings.keys())}")
        else:
            # Para casos normais, usar apenas o modelo recomendado
            model_name, config = self.select_embedding_model(text)
            embedding = self.get_embedding(text)
            if embedding:
                embeddings[model_name] = embedding
        
        return embeddings
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de performance do sistema"""
        return {
            "cache_size": len(self.classification_cache),
            "available_models": list(self.embedding_configs.keys()),
            "client_status": "active" if self.openai_client else "inactive",
            "last_updated": datetime.now().isoformat()
        }
    
    def clear_cache(self):
        """Limpa o cache de classificações"""
        self.classification_cache.clear()
        logger.info("🧹 Cache de classificações limpo")
    
    def get_cost_estimate(self, text: str, token_count: Optional[int] = None) -> Dict[str, float]:
        """
        Estima custo do embedding baseado no texto e modelo selecionado
        """
        model_name, config = self.select_embedding_model(text)
        
        # Estimar tokens se não fornecido (aproximadamente 1 token = 4 chars)
        if token_count is None:
            token_count = len(text) / 4
        
        cost = token_count * config.cost_per_token
        
        return {
            "model": model_name,
            "estimated_tokens": token_count,
            "cost_per_token": config.cost_per_token,
            "total_cost": cost,
            "currency": "USD"
        }