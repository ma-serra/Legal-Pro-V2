"""
Pipeline RAG (Retrieval Augmented Generation) para consulta ao banco de conhecimento
"""
import os
import logging
from typing import List, Optional
import requests
from assistente.db import search_pgvector

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_context(user_query: str, top_k: int = 4) -> list[str]:
    """
    Obtém contexto do banco de dados para uma query do usuário
    
    Args:
        user_query: Consulta do usuário
        top_k: Número de resultados a retornar
        
    Returns:
        Lista de chunks de texto relevantes para a consulta
    """
    try:
        return search_pgvector(user_query, top_k)
    except Exception as e:
        logger.error(f"Erro ao buscar contexto na base de conhecimento: {e}")
        return []

def get_web_search_results(query: str, max_results: int = 3) -> Optional[List[str]]:
    """
    Realiza busca na web para obter informações atualizadas
    
    Args:
        query: Consulta para busca na web
        max_results: Número máximo de resultados
        
    Returns:
        Lista de snippets dos resultados ou None se a busca estiver desativada
    """
    # Verifica se a busca na web está habilitada
    if os.getenv("ENABLE_WEB_SEARCH", "true").lower() != "true":
        return None
        
    try:
        # Esta função simula o uso de um serviço de busca como SerpAPI ou Browserless
        # Em um ambiente de produção, seria utilizada uma API real
        # Exemplo de implementação com SerpAPI:
        """
        serp_api_key = os.getenv("SERP_API_KEY")
        if not serp_api_key:
            logger.warning("Chave da SerpAPI não configurada")
            return None
            
        params = {
            "q": query,
            "api_key": serp_api_key,
            "num": max_results
        }
        
        response = requests.get("https://serpapi.com/search", params=params)
        if response.status_code == 200:
            data = response.json()
            results = []
            for result in data.get("organic_results", [])[:max_results]:
                results.append(f"Título: {result.get('title')}\nDescrição: {result.get('snippet')}\nLink: {result.get('link')}")
            return results
        """
        
        # Implementação mínima para simulação
        logger.info(f"Simulando busca na web para: {query}")
        return [
            "Este é um resultado simulado de busca na web. Em um ambiente de produção, este texto seria substituído por resultados reais de API de busca.",
            "Para implementar a busca na web real, integre com SerpAPI, Browserless ou outra API similar e configure a chave de API correspondente."
        ]
    
    except Exception as e:
        logger.error(f"Erro na busca web: {e}")
        return None

def enrich_query_with_context(query: str, use_db: bool = True, use_web: bool = False) -> tuple[str, List[str]]:
    """
    Enriquece a consulta do usuário com contexto do banco de dados e/ou da web
    
    Args:
        query: Consulta original do usuário
        use_db: Se deve usar o contexto do banco de dados
        use_web: Se deve usar o contexto da web
        
    Returns:
        Tupla com a consulta original e lista de chunks de contexto
    """
    context_chunks = []
    
    # Adiciona contexto do banco de dados
    if use_db:
        db_chunks = get_db_context(query)
        if db_chunks:
            context_chunks.extend([f"[DB] {chunk}" for chunk in db_chunks])
    
    # Adiciona contexto da web
    if use_web:
        web_chunks = get_web_search_results(query)
        if web_chunks:
            context_chunks.extend([f"[WEB] {chunk}" for chunk in web_chunks])
    
    return query, context_chunks