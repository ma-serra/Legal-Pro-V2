"""
Sistema de Validação Cruzada Multi-Modelo
Implementa consenso entre diferentes modelos de IA para maior precisão
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

@dataclass
class ModelResponse:
    """Resposta de um modelo específico"""
    model_name: str
    provider: str
    response: str
    confidence: float
    tokens_used: int
    response_time: float
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class ConsensusResult:
    """Resultado do consenso entre modelos"""
    consensus_score: float
    final_response: str
    contributing_models: List[str]
    disagreement_points: List[str]
    confidence_level: str
    requires_review: bool
    individual_responses: List[ModelResponse]

class MultiModelValidation:
    """
    Sistema de consenso entre múltiplos modelos de IA
    Garante maior precisão através de validação cruzada
    """
    
    def __init__(self):
        # Configuração dos modelos disponíveis
        self.available_models = {
            "openai": {
                "gpt-4o": {"weight": 0.4, "specialty": "general_analysis"},
                "gpt-4.1": {"weight": 0.35, "specialty": "detailed_reasoning"},
                "gpt-4o-mini": {"weight": 0.25, "specialty": "quick_responses"}
            },
            "anthropic": {
                "claude-sonnet-4-20250514": {"weight": 0.4, "specialty": "legal_analysis"},
                "claude-3-7-sonnet-20250219": {"weight": 0.35, "specialty": "comprehensive_review"},
                "claude-3-5-sonnet-20241022": {"weight": 0.25, "specialty": "structured_analysis"}
            },
            "google": {
                "gemini-1.5-pro": {"weight": 0.35, "specialty": "long_context"},
                "gemini-2.0-flash-experimental": {"weight": 0.35, "specialty": "fast_processing"},
                "gemini-2.5-pro": {"weight": 0.3, "specialty": "advanced_reasoning"}
            },
            "deepseek": {
                "deepseek-chat": {"weight": 0.3, "specialty": "general_chat"},
                "deepseek-reasoner": {"weight": 0.4, "specialty": "logical_reasoning"},
                "deepseek-coder": {"weight": 0.3, "specialty": "structured_analysis"}
            }
        }
        
        # Limites de consenso
        self.consensus_thresholds = {
            "high": 0.9,      # Alta confiança - usar resposta diretamente
            "medium": 0.75,   # Média confiança - combinar respostas
            "low": 0.6,       # Baixa confiança - sinalizar para revisão
            "critical": 0.5   # Crítica - necessária intervenção manual
        }
        
        # Inicializar clientes das APIs
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Inicializa clientes das APIs disponíveis"""
        self.clients = {}
        
        # OpenAI
        try:
            from openai import OpenAI
            if os.environ.get('OPENAI_API_KEY'):
                self.clients['openai'] = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
                logger.info("✅ Cliente OpenAI inicializado para validação")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar OpenAI: {e}")
        
        # Anthropic
        try:
            from anthropic import Anthropic
            if os.environ.get('ANTHROPIC_API_KEY'):
                self.clients['anthropic'] = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
                logger.info("✅ Cliente Anthropic inicializado para validação")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Anthropic: {e}")
        
        # Google Gemini
        try:
            import google.generativeai as genai
            if os.environ.get('GOOGLE_API_KEY'):
                genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
                self.clients['google'] = genai
                logger.info("✅ Cliente Google inicializado para validação")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Google: {e}")
    
    async def call_model_async(self, provider: str, model: str, query: str, context: str) -> Optional[ModelResponse]:
        """
        Chama um modelo específico de forma assíncrona
        """
        start_time = datetime.now()
        
        try:
            if provider == "openai" and provider in self.clients:
                response = await self._call_openai_model(model, query, context)
            elif provider == "anthropic" and provider in self.clients:
                response = await self._call_anthropic_model(model, query, context)
            elif provider == "google" and provider in self.clients:
                response = await self._call_google_model(model, query, context)
            else:
                logger.warning(f"⚠️ Provedor {provider} não disponível")
                return None
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            return ModelResponse(
                model_name=model,
                provider=provider,
                response=response.get("content", ""),
                confidence=response.get("confidence", 0.5),
                tokens_used=response.get("tokens", 0),
                response_time=response_time,
                timestamp=datetime.now(),
                metadata=response.get("metadata", {})
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao chamar {provider}/{model}: {e}")
            return None
    
    async def _call_openai_model(self, model: str, query: str, context: str) -> Dict[str, Any]:
        """Chama modelo OpenAI"""
        try:
            response = self.clients['openai'].chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": f"Contexto jurídico: {context}"},
                    {"role": "user", "content": query}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            return {
                "content": response.choices[0].message.content,
                "tokens": response.usage.total_tokens,
                "confidence": 0.8,  # OpenAI não fornece score de confiança
                "metadata": {"model": model, "provider": "openai"}
            }
        except Exception as e:
            logger.error(f"❌ Erro na chamada OpenAI: {e}")
            return {}
    
    async def _call_anthropic_model(self, model: str, query: str, context: str) -> Dict[str, Any]:
        """Chama modelo Anthropic"""
        try:
            message = self.clients['anthropic'].messages.create(
                model=model,
                max_tokens=2000,
                temperature=0.2,
                messages=[
                    {
                        "role": "user", 
                        "content": f"Contexto jurídico: {context}\n\nConsulta: {query}"
                    }
                ]
            )
            
            return {
                "content": message.content[0].text,
                "tokens": message.usage.input_tokens + message.usage.output_tokens,
                "confidence": 0.85,  # Anthropic geralmente mais confiável para análise jurídica
                "metadata": {"model": model, "provider": "anthropic"}
            }
        except Exception as e:
            logger.error(f"❌ Erro na chamada Anthropic: {e}")
            return {}
    
    async def _call_google_model(self, model: str, query: str, context: str) -> Dict[str, Any]:
        """Chama modelo Google Gemini"""
        try:
            model_instance = self.clients['google'].GenerativeModel(model)
            response = model_instance.generate_content(
                f"Contexto jurídico: {context}\n\nConsulta: {query}",
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 2000,
                }
            )
            
            return {
                "content": response.text,
                "tokens": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0,
                "confidence": 0.75,
                "metadata": {"model": model, "provider": "google"}
            }
        except Exception as e:
            logger.error(f"❌ Erro na chamada Google: {e}")
            return {}
    
    def calculate_consensus_score(self, responses: List[ModelResponse]) -> float:
        """
        Calcula score de consenso baseado na similaridade das respostas
        """
        if len(responses) < 2:
            return 0.0
        
        # Extrair apenas o conteúdo das respostas
        contents = [resp.response for resp in responses if resp.response]
        
        if len(contents) < 2:
            return 0.0
        
        # Calcular similaridade par a par
        similarities = []
        
        for i in range(len(contents)):
            for j in range(i + 1, len(contents)):
                similarity = SequenceMatcher(None, contents[i], contents[j]).ratio()
                similarities.append(similarity)
        
        # Média das similaridades com peso pelos modelos
        weighted_similarities = []
        weight_sum = 0
        
        for i, resp in enumerate(responses):
            if resp.provider in self.available_models:
                models_config = self.available_models[resp.provider]
                if resp.model_name in models_config:
                    weight = models_config[resp.model_name]["weight"]
                    if i < len(similarities):
                        weighted_similarities.append(similarities[i] * weight)
                        weight_sum += weight
        
        if weight_sum > 0:
            consensus_score = sum(weighted_similarities) / weight_sum
        else:
            consensus_score = np.mean(similarities) if similarities else 0.0
        
        logger.info(f"📊 Score de consenso calculado: {consensus_score:.3f}")
        return consensus_score
    
    def identify_disagreement_points(self, responses: List[ModelResponse]) -> List[str]:
        """
        Identifica pontos de discordância entre as respostas
        """
        disagreements = []
        
        if len(responses) < 2:
            return disagreements
        
        # Análise simples de palavras-chave divergentes
        key_terms = {}
        
        for resp in responses:
            words = resp.response.lower().split()
            for word in words:
                if len(word) > 5:  # Palavras significativas
                    if word not in key_terms:
                        key_terms[word] = []
                    key_terms[word].append(resp.model_name)
        
        # Identificar termos que não aparecem em todas as respostas
        total_models = len(responses)
        for term, models in key_terms.items():
            if len(models) < total_models * 0.6:  # Termo em menos de 60% das respostas
                disagreements.append(f"Divergência no termo '{term}': presente apenas em {models}")
        
        return disagreements[:5]  # Limitar a 5 principais divergências
    
    def merge_responses(self, responses: List[ModelResponse]) -> str:
        """
        Combina respostas em uma resposta final consolidada
        """
        if not responses:
            return ""
        
        if len(responses) == 1:
            return responses[0].response
        
        # Ordenar por confiança e peso do modelo
        weighted_responses = []
        
        for resp in responses:
            weight = 0.5  # Peso padrão
            if resp.provider in self.available_models:
                models_config = self.available_models[resp.provider]
                if resp.model_name in models_config:
                    weight = models_config[resp.model_name]["weight"]
            
            total_score = (resp.confidence * 0.6) + (weight * 0.4)
            weighted_responses.append((total_score, resp))
        
        # Ordenar por score total
        weighted_responses.sort(key=lambda x: x[0], reverse=True)
        
        # Usar a resposta com maior score como base
        primary_response = weighted_responses[0][1].response
        
        # Adicionar informações complementares das outras respostas
        additional_info = []
        for score, resp in weighted_responses[1:3]:  # Máximo 2 respostas adicionais
            # Extrair informações únicas
            unique_sentences = []
            primary_sentences = primary_response.split('.')
            resp_sentences = resp.response.split('.')
            
            for sentence in resp_sentences:
                sentence = sentence.strip()
                if len(sentence) > 20:  # Frases significativas
                    is_unique = True
                    for primary_sentence in primary_sentences:
                        if SequenceMatcher(None, sentence, primary_sentence).ratio() > 0.7:
                            is_unique = False
                            break
                    
                    if is_unique:
                        unique_sentences.append(sentence)
            
            if unique_sentences:
                additional_info.extend(unique_sentences[:2])  # Máximo 2 frases por resposta
        
        # Construir resposta final
        final_response = primary_response
        
        if additional_info:
            final_response += "\n\nInformações complementares:\n"
            for info in additional_info[:3]:  # Máximo 3 informações adicionais
                final_response += f"• {info.strip()}\n"
        
        return final_response
    
    async def get_consensus_response(self, query: str, context: str, selected_models: Optional[List[Tuple[str, str]]] = None) -> ConsensusResult:
        """
        Obtém resposta com consenso entre múltiplos modelos
        """
        # Modelos padrão se não especificado
        if not selected_models:
            selected_models = [
                ("openai", "gpt-4o"),
                ("anthropic", "claude-sonnet-4-20250514"),
                ("google", "gemini-1.5-pro")
            ]
        
        logger.info(f"🔍 Iniciando validação cruzada com {len(selected_models)} modelos")
        
        # Chamar todos os modelos em paralelo
        tasks = []
        for provider, model in selected_models:
            if provider in self.clients:
                task = self.call_model_async(provider, model, query, context)
                tasks.append(task)
        
        # Aguardar todas as respostas
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrar respostas válidas
        valid_responses = [resp for resp in responses if isinstance(resp, ModelResponse)]
        
        if not valid_responses:
            logger.error("❌ Nenhuma resposta válida obtida")
            return ConsensusResult(
                consensus_score=0.0,
                final_response="Erro: Não foi possível obter respostas dos modelos",
                contributing_models=[],
                disagreement_points=[],
                confidence_level="critical",
                requires_review=True,
                individual_responses=[]
            )
        
        # Calcular consenso
        consensus_score = self.calculate_consensus_score(valid_responses)
        disagreement_points = self.identify_disagreement_points(valid_responses)
        
        # Determinar nível de confiança
        if consensus_score >= self.consensus_thresholds["high"]:
            confidence_level = "high"
            requires_review = False
        elif consensus_score >= self.consensus_thresholds["medium"]:
            confidence_level = "medium"
            requires_review = False
        elif consensus_score >= self.consensus_thresholds["low"]:
            confidence_level = "low"
            requires_review = True
        else:
            confidence_level = "critical"
            requires_review = True
        
        # Gerar resposta final
        final_response = self.merge_responses(valid_responses)
        
        # Adicionar metadata de consenso
        if requires_review:
            final_response += f"\n\n⚠️ **Atenção**: Esta resposta possui baixo consenso ({consensus_score:.2f}) e requer revisão manual."
        
        contributing_models = [f"{resp.provider}/{resp.model_name}" for resp in valid_responses]
        
        result = ConsensusResult(
            consensus_score=consensus_score,
            final_response=final_response,
            contributing_models=contributing_models,
            disagreement_points=disagreement_points,
            confidence_level=confidence_level,
            requires_review=requires_review,
            individual_responses=valid_responses
        )
        
        logger.info(f"✅ Consenso concluído - Score: {consensus_score:.3f}, Confiança: {confidence_level}")
        
        return result
    
    def get_validation_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do sistema de validação"""
        return {
            "available_providers": list(self.clients.keys()),
            "available_models": self.available_models,
            "consensus_thresholds": self.consensus_thresholds,
            "status": "active"
        }