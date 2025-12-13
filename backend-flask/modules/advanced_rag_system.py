"""
Sistema RAG Avançado com Reranking Inteligente
Implementa busca vetorial otimizada com reranking por relevância jurídica
"""

import os
import json
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import re
from collections import Counter
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Resultado de busca vetorial"""
    content: str
    score: float
    source: str
    metadata: Dict[str, Any]
    legal_area: str
    document_type: str
    hierarchy_level: int

@dataclass
class RerankedResult:
    """Resultado após reranking"""
    original_result: SearchResult
    relevance_score: float
    legal_relevance: float
    court_hierarchy_score: float
    recency_score: float
    final_score: float
    ranking_factors: Dict[str, float]

class AdvancedRAGSystem:
    """
    Sistema RAG avançado com reranking inteligente para contexto jurídico
    Implementa busca híbrida, expansão de consultas e validação de citações
    """
    
    def __init__(self):
        # Hierarquia de tribunais (scores mais altos = maior autoridade)
        self.court_hierarchy = {
            "STF": 10.0,  # Supremo Tribunal Federal
            "STJ": 9.0,   # Superior Tribunal de Justiça
            "TST": 8.5,   # Tribunal Superior do Trabalho
            "TSE": 8.5,   # Tribunal Superior Eleitoral
            "STM": 8.0,   # Superior Tribunal Militar
            "TRF": 7.0,   # Tribunais Regionais Federais
            "TRT": 6.5,   # Tribunais Regionais do Trabalho
            "TRE": 6.0,   # Tribunais Regionais Eleitorais
            "TJSP": 5.5,  # Tribunal de Justiça de São Paulo
            "TJRJ": 5.5,  # Tribunal de Justiça do Rio de Janeiro
            "TJMG": 5.5,  # Tribunal de Justiça de Minas Gerais
            "TJ": 5.0,    # Tribunais de Justiça em geral
            "PRIMEIRA_INSTANCIA": 3.0,
            "ADMINISTRATIVA": 2.0,
            "DOUTRINA": 4.0,
            "LEGISLACAO": 8.0
        }
        
        # Tipos de documento e suas importâncias
        self.document_types = {
            "sumula_vinculante": 10.0,
            "sumula": 8.0,
            "acordao": 6.0,
            "decisao_monocratica": 5.0,
            "lei": 9.0,
            "constituicao": 10.0,
            "decreto": 7.0,
            "resolucao": 6.0,
            "doutrina": 4.0,
            "artigo_cientifico": 3.0
        }
        
        # Sinônimos jurídicos para expansão de consultas
        self.legal_synonyms = {
            "dano": ["prejuízo", "lesão", "detrimento"],
            "responsabilidade": ["obrigação", "dever", "encargo"],
            "contrato": ["acordo", "pacto", "convenção", "ajuste"],
            "crime": ["delito", "infração penal", "tipo penal"],
            "pena": ["sanção", "penalidade", "castigo"],
            "recurso": ["apelação", "agravo", "embargos"],
            "sentença": ["decisão", "julgamento", "veredicto"],
            "processo": ["ação", "demanda", "lide"],
            "competência": ["jurisdição", "atribuição"],
            "legitimidade": ["capacidade", "habilitação"]
        }
        
        # Cache de consultas
        self.query_cache = {}
        
        # Inicializar cliente Qdrant
        self._initialize_qdrant_client()
    
    def _initialize_qdrant_client(self):
        """Inicializa cliente Qdrant para busca vetorial"""
        try:
            from qdrant_client import QdrantClient
            
            # Usar credenciais secundárias conforme configurado no sistema
            self.qdrant_client = QdrantClient(
                url="https://c21e6a5b-298d-483b-82f4-00aeff5edabe.us-east4-0.gcp.cloud.qdrant.io:6333",
                api_key=os.environ.get("QDRANT_API_KEY_NOVA"),
                timeout=30
            )
            
            # Coleções disponíveis
            self.available_collections = [
                "direito_penal",
                "documentos_juridicos_completos", 
                "jurisprudencias"
            ]
            
            logger.info("✅ Cliente Qdrant inicializado para RAG avançado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Qdrant: {e}")
            self.qdrant_client = None
    
    def expand_query(self, original_query: str) -> List[str]:
        """
        Expande consulta com sinônimos jurídicos e termos relacionados
        """
        expanded_queries = [original_query]
        
        # Dividir consulta em palavras
        words = re.findall(r'\b\w+\b', original_query.lower())
        
        # Expandir com sinônimos
        for word in words:
            if word in self.legal_synonyms:
                for synonym in self.legal_synonyms[word]:
                    # Criar variação da consulta substituindo a palavra
                    expanded_query = original_query.lower().replace(word, synonym)
                    if expanded_query not in expanded_queries:
                        expanded_queries.append(expanded_query)
        
        # Adicionar termos jurídicos relacionados baseados na área
        legal_area_terms = self._get_related_legal_terms(original_query)
        for term in legal_area_terms:
            expanded_query = f"{original_query} {term}"
            expanded_queries.append(expanded_query)
        
        logger.info(f"🔍 Consulta expandida: {len(expanded_queries)} variações")
        return expanded_queries[:5]  # Limitar a 5 variações
    
    def _get_related_legal_terms(self, query: str) -> List[str]:
        """
        Identifica termos jurídicos relacionados baseado no contexto
        """
        query_lower = query.lower()
        related_terms = []
        
        # Mapeamento de contextos para termos relacionados
        context_terms = {
            "penal": ["tipicidade", "culpabilidade", "antijuridicidade", "punibilidade"],
            "civil": ["obrigação", "responsabilidade", "danos", "indenização"],
            "tributário": ["imposto", "taxa", "contribuição", "fisco"],
            "trabalhista": ["empregado", "empregador", "CLT", "sindicato"],
            "processual": ["competência", "petição", "sentença", "recurso"]
        }
        
        for context, terms in context_terms.items():
            if any(indicator in query_lower for indicator in [context, f"direito {context}"]):
                related_terms.extend(terms[:2])  # Máximo 2 termos por contexto
        
        return related_terms
    
    def enhanced_retrieval(self, query: str, k: int = 10, legal_area: Optional[str] = None) -> List[SearchResult]:
        """
        Busca vetorial aprimorada com múltiplas estratégias
        """
        if not self.qdrant_client:
            logger.error("❌ Cliente Qdrant não disponível")
            return []
        
        # Verificar cache
        query_hash = hashlib.md5(f"{query}_{k}_{legal_area}".encode()).hexdigest()
        if query_hash in self.query_cache:
            logger.info("💾 Resultado obtido do cache")
            return self.query_cache[query_hash]
        
        all_results = []
        
        # Expandir consulta
        expanded_queries = self.expand_query(query)
        
        # Buscar em cada coleção disponível
        for collection in self.available_collections:
            try:
                # Busca com consulta original
                results = self._search_collection(collection, query, k)
                all_results.extend(results)
                
                # Busca com consultas expandidas (menos resultados)
                for expanded_query in expanded_queries[1:3]:  # Máximo 2 expansões
                    expanded_results = self._search_collection(collection, expanded_query, k//2)
                    all_results.extend(expanded_results)
                
            except Exception as e:
                logger.error(f"❌ Erro na busca em {collection}: {e}")
        
        # Remover duplicatas
        unique_results = self._remove_duplicates(all_results)
        
        # Aplicar reranking
        reranked_results = self.legal_reranker(unique_results, query)
        
        # Filtrar por hierarquia de tribunais
        filtered_results = self.filter_by_court_hierarchy(reranked_results)
        
        # Validar citações legais
        validated_results = self.validate_legal_citations(filtered_results[:k*2])
        
        # Retornar top K resultados
        final_results = validated_results[:k]
        
        # Armazenar no cache
        self.query_cache[query_hash] = final_results
        
        logger.info(f"✅ RAG avançado concluído: {len(final_results)} resultados finais")
        
        return final_results
    
    def _search_collection(self, collection: str, query: str, limit: int) -> List[SearchResult]:
        """
        Busca em uma coleção específica do Qdrant
        """
        try:
            # Gerar embedding da consulta (usando sistema híbrido se disponível)
            from .hybrid_embedding_system import HybridEmbeddingSystem
            
            embedding_system = HybridEmbeddingSystem()
            query_embedding = embedding_system.get_embedding(query)
            
            if not query_embedding:
                logger.error("❌ Não foi possível gerar embedding da consulta")
                return []
            
            # Realizar busca no Qdrant
            search_result = self.qdrant_client.search(
                collection_name=collection,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=0.7  # Filtrar resultados com baixa similaridade
            )
            
            results = []
            for point in search_result:
                # Extrair metadados
                payload = point.payload or {}
                
                result = SearchResult(
                    content=payload.get("content", ""),
                    score=point.score,
                    source=payload.get("source", collection),
                    metadata=payload,
                    legal_area=payload.get("legal_area", "unknown"),
                    document_type=payload.get("document_type", "unknown"),
                    hierarchy_level=self._get_hierarchy_level(payload)
                )
                results.append(result)
            
            logger.info(f"📊 Busca em {collection}: {len(results)} resultados")
            return results
            
        except Exception as e:
            logger.error(f"❌ Erro na busca em {collection}: {e}")
            return []
    
    def _remove_duplicates(self, results: List[SearchResult]) -> List[SearchResult]:
        """
        Remove resultados duplicados baseado no conteúdo
        """
        seen_contents = set()
        unique_results = []
        
        for result in results:
            # Criar hash do conteúdo para comparação
            content_hash = hashlib.md5(result.content.encode()).hexdigest()
            
            if content_hash not in seen_contents:
                seen_contents.add(content_hash)
                unique_results.append(result)
        
        logger.info(f"🧹 Duplicatas removidas: {len(results)} -> {len(unique_results)}")
        return unique_results
    
    def legal_reranker(self, results: List[SearchResult], query: str) -> List[RerankedResult]:
        """
        Reranking inteligente baseado em relevância jurídica
        """
        reranked_results = []
        
        for result in results:
            # Calcular diferentes scores
            relevance_score = self._calculate_relevance_score(result, query)
            legal_relevance = self._calculate_legal_relevance(result, query)
            court_hierarchy_score = self._get_court_hierarchy_score(result)
            recency_score = self._calculate_recency_score(result)
            
            # Score final ponderado
            final_score = (
                relevance_score * 0.3 +
                legal_relevance * 0.35 +
                court_hierarchy_score * 0.2 +
                recency_score * 0.15
            )
            
            ranking_factors = {
                "relevance": relevance_score,
                "legal_relevance": legal_relevance,
                "court_hierarchy": court_hierarchy_score,
                "recency": recency_score
            }
            
            reranked_result = RerankedResult(
                original_result=result,
                relevance_score=relevance_score,
                legal_relevance=legal_relevance,
                court_hierarchy_score=court_hierarchy_score,
                recency_score=recency_score,
                final_score=final_score,
                ranking_factors=ranking_factors
            )
            
            reranked_results.append(reranked_result)
        
        # Ordenar por score final
        reranked_results.sort(key=lambda x: x.final_score, reverse=True)
        
        logger.info(f"📈 Reranking concluído: {len(reranked_results)} resultados reordenados")
        return reranked_results
    
    def _calculate_relevance_score(self, result: SearchResult, query: str) -> float:
        """
        Calcula score de relevância baseado na similaridade semântica
        """
        # Score base do resultado vetorial
        base_score = result.score
        
        # Ajustar baseado em correspondências de termos exatos
        query_terms = set(re.findall(r'\b\w+\b', query.lower()))
        content_terms = set(re.findall(r'\b\w+\b', result.content.lower()))
        
        exact_matches = len(query_terms.intersection(content_terms))
        total_query_terms = len(query_terms)
        
        if total_query_terms > 0:
            exact_match_bonus = exact_matches / total_query_terms * 0.2
        else:
            exact_match_bonus = 0
        
        return min(1.0, base_score + exact_match_bonus)
    
    def _calculate_legal_relevance(self, result: SearchResult, query: str) -> float:
        """
        Calcula relevância jurídica específica
        """
        score = 0.5  # Score base
        
        # Verificar presença de elementos jurídicos específicos
        legal_elements = [
            r"art\.?\s*\d+",  # Artigos de lei
            r"§\s*\d+",       # Parágrafos
            r"inciso\s+[IVX]+", # Incisos
            r"alínea\s+[a-z]",  # Alíneas
            r"súmula\s+\d+",    # Súmulas
            r"precedente",      # Precedentes
            r"jurisprudência"   # Jurisprudência
        ]
        
        content_lower = result.content.lower()
        for pattern in legal_elements:
            if re.search(pattern, content_lower):
                score += 0.1
        
        # Bonus para tipos de documento importantes
        doc_type = result.document_type.lower()
        if doc_type in ["sumula_vinculante", "lei", "constituicao"]:
            score += 0.2
        elif doc_type in ["sumula", "acordao", "decreto"]:
            score += 0.1
        
        return min(1.0, score)
    
    def _get_hierarchy_level(self, payload: Dict[str, Any]) -> int:
        """
        Determina nível hierárquico do tribunal
        """
        source = payload.get("source", "").upper()
        tribunal = payload.get("tribunal", "").upper()
        
        # Verificar por tribunal específico
        for court, level in self.court_hierarchy.items():
            if court in source or court in tribunal:
                return int(level)
        
        return 1  # Nível mais baixo por padrão
    
    def _get_court_hierarchy_score(self, result: SearchResult) -> float:
        """
        Score baseado na hierarquia do tribunal
        """
        hierarchy_level = result.hierarchy_level
        max_level = max(self.court_hierarchy.values())
        
        return hierarchy_level / max_level
    
    def _calculate_recency_score(self, result: SearchResult) -> float:
        """
        Score baseado na atualidade do documento
        """
        # Tentar extrair data do metadata
        date_str = result.metadata.get("date", "")
        
        if not date_str:
            return 0.5  # Score neutro se não há data
        
        try:
            # Assumir formato YYYY-MM-DD ou similar
            doc_year = int(date_str[:4]) if len(date_str) >= 4 else 2020
            current_year = datetime.now().year
            
            # Documentos mais recentes têm score maior
            years_diff = current_year - doc_year
            if years_diff <= 1:
                return 1.0
            elif years_diff <= 3:
                return 0.8
            elif years_diff <= 5:
                return 0.6
            else:
                return 0.4
                
        except:
            return 0.5
    
    def filter_by_court_hierarchy(self, results: List[RerankedResult]) -> List[SearchResult]:
        """
        Filtra resultados priorizando tribunais superiores
        """
        # Agrupar por nível hierárquico
        hierarchy_groups = {}
        for result in results:
            level = result.original_result.hierarchy_level
            if level not in hierarchy_groups:
                hierarchy_groups[level] = []
            hierarchy_groups[level].append(result)
        
        # Selecionar resultados priorizando níveis mais altos
        filtered_results = []
        for level in sorted(hierarchy_groups.keys(), reverse=True):
            group = hierarchy_groups[level]
            # Ordenar por score final dentro do grupo
            group.sort(key=lambda x: x.final_score, reverse=True)
            filtered_results.extend([r.original_result for r in group])
        
        return filtered_results
    
    def validate_legal_citations(self, results: List[SearchResult]) -> List[SearchResult]:
        """
        Valida citações legais nos resultados
        """
        validated_results = []
        
        for result in results:
            # Verificar presença de citações válidas
            has_valid_citations = self._has_valid_citations(result.content)
            
            if has_valid_citations:
                validated_results.append(result)
            else:
                # Manter resultado mas com score reduzido
                result.score *= 0.8
                validated_results.append(result)
        
        return validated_results
    
    def _has_valid_citations(self, content: str) -> bool:
        """
        Verifica se o conteúdo possui citações legais válidas
        """
        citation_patterns = [
            r"art\.?\s*\d+",           # Artigos
            r"lei\s+n[°º]?\s*[\d.,/]+", # Leis
            r"decreto\s+n[°º]?\s*[\d.,/]+", # Decretos
            r"súmula\s+n[°º]?\s*\d+",   # Súmulas
            r"CF/88|constituição",      # Constituição
            r"CC/02|código civil",      # Código Civil
            r"CP|código penal",         # Código Penal
        ]
        
        content_lower = content.lower()
        for pattern in citation_patterns:
            if re.search(pattern, content_lower):
                return True
        
        return False
    
    def get_rag_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do sistema RAG"""
        return {
            "available_collections": self.available_collections,
            "court_hierarchy_levels": len(self.court_hierarchy),
            "document_types": len(self.document_types),
            "legal_synonyms": len(self.legal_synonyms),
            "cache_size": len(self.query_cache),
            "qdrant_status": "active" if self.qdrant_client else "inactive",
            "last_updated": datetime.now().isoformat()
        }
    
    def clear_cache(self):
        """Limpa cache de consultas"""
        self.query_cache.clear()
        logger.info("🧹 Cache RAG limpo")