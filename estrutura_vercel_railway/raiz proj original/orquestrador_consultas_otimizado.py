
"""
Orquestrador Inteligente de Consultas Jurídicas - Versão Otimizada
Sistema de busca com embeddings duplos otimizado para pgvector
"""

import os
import psycopg2
import openai
from typing import Dict, List, Optional, Any
import json
import logging

logger = logging.getLogger(__name__)

class OrquestradorConsultasOtimizado:
    """Orquestrador otimizado para consultas multi-agente"""
    
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        self.openai_client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        self.agentes_config = self.carregar_configuracao_agentes()
    
    def carregar_configuracao_agentes(self) -> Dict:
        """Carrega configuração dos agentes"""
        try:
            with open('agentes_config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Arquivo de configuração de agentes não encontrado")
            return {}
    
    def gerar_embeddings_consulta(self, texto: str) -> Dict[str, List[float]]:
        """Gera embeddings da consulta para busca otimizada"""
        try:
            # Small embedding para busca inicial
            response_small = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=texto[:8000]
            )
            
            # Large embedding reduzido para rerank
            response_large = self.openai_client.embeddings.create(
                model="text-embedding-3-large", 
                input=texto[:8000],
                dimensions=1536  # Compatível com pgvector
            )
            
            return {
                'small': response_small.data[0].embedding,
                'large': response_large.data[0].embedding
            }
        except Exception as e:
            logger.error(f"Erro ao gerar embeddings: {e}")
            return {'small': None, 'large': None}
    
    def orquestrar_consulta(self, area: str, texto: str, agente_id: Optional[str] = None, limite: int = 10) -> Dict[str, Any]:
        """
        Função principal de orquestração otimizada
        
        Args:
            area: Área jurídica (ex: 'direito_penal')
            texto: Texto da consulta
            agente_id: ID específico do agente (opcional)
            limite: Número máximo de resultados
            
        Returns:
            Dict com resultados ranqueados e metadados
        """
        try:
            # 1. Validar área
            if not area.startswith('direito_') and area not in ['seguros', 'conflitos_mediacao', 'analise_riscos']:
                area = f"direito_{area}"
            
            # 2. Gerar embeddings da consulta
            embeddings = self.gerar_embeddings_consulta(texto)
            if not embeddings['small']:
                return {"erro": "Falha ao gerar embeddings da consulta"}
            
            # 3. Conectar ao banco
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            # 4. Busca inicial com embedding small (usando índice)
            tabela = f"embeddings_{area}"
            
            sql_busca = f"""
                SELECT id, conteudo, referencia, agente_id, metadata,
                       embedding_small <=> %s as distancia_small
                FROM {tabela}
                WHERE embedding_small IS NOT NULL 
            """
            
            params = [embeddings['small']]
            
            # Filtrar por agente específico se fornecido
            if agente_id:
                sql_busca += " AND agente_id = %s"
                params.append(agente_id)
            
            sql_busca += f"""
                ORDER BY embedding_small <=> %s
                LIMIT %s
            """
            params.extend([embeddings['small'], limite * 2])
            
            cursor.execute(sql_busca, params)
            resultados_iniciais = cursor.fetchall()
            
            # 5. Rerank com embedding large (cálculo manual de similaridade)
            resultados_reranked = []
            for resultado in resultados_iniciais:
                doc_id, conteudo, referencia, agente, metadata, dist_small = resultado
                
                # Buscar embedding large para este documento
                cursor.execute(f"""
                    SELECT embedding_large 
                    FROM {tabela} 
                    WHERE id = %s AND embedding_large IS NOT NULL
                """, (doc_id,))
                
                embedding_large_doc = cursor.fetchone()
                if embedding_large_doc and embedding_large_doc[0]:
                    # Calcular similaridade com embedding large
                    dist_large = self.calcular_similaridade_coseno(
                        embeddings['large'], 
                        embedding_large_doc[0]
                    )
                else:
                    dist_large = dist_small
                
                # Score combinado (70% large, 30% small)
                score_final = (0.7 * (1 - dist_large)) + (0.3 * (1 - dist_small))
                
                resultados_reranked.append({
                    'id': str(doc_id),
                    'conteudo': conteudo[:500] + "..." if len(conteudo) > 500 else conteudo,
                    'referencia': referencia,
                    'agente_id': agente,
                    'metadata': metadata if metadata else {},
                    'score': round(score_final, 4),
                    'distancia_small': round(dist_small, 4),
                    'distancia_large': round(dist_large, 4)
                })
            
            # 6. Ordenar por score final e limitar
            resultados_finais = sorted(resultados_reranked, key=lambda x: x['score'], reverse=True)[:limite]
            
            # 7. Buscar agentes relevantes
            agentes_relevantes = self.identificar_agentes_relevantes(area, texto, resultados_finais)
            
            cursor.close()
            conn.close()
            
            return {
                "status": "sucesso",
                "area": area,
                "total_resultados": len(resultados_finais),
                "resultados": resultados_finais,
                "agentes_sugeridos": agentes_relevantes,
                "metadata_busca": {
                    "embeddings_utilizados": "small + large otimizado",
                    "rerank_aplicado": True,
                    "agente_filtro": agente_id,
                    "estrategia": "busca_inicial_small_rerank_large"
                }
            }
            
        except Exception as e:
            logger.error(f"Erro na orquestração: {e}")
            return {"erro": str(e), "status": "erro"}
    
    def calcular_similaridade_coseno(self, vec1: List[float], vec2: List[float]) -> float:
        """Calcula similaridade coseno entre dois vetores"""
        try:
            import numpy as np
            vec1_np = np.array(vec1)
            vec2_np = np.array(vec2)
            
            dot_product = np.dot(vec1_np, vec2_np)
            norm1 = np.linalg.norm(vec1_np)
            norm2 = np.linalg.norm(vec2_np)
            
            if norm1 == 0 or norm2 == 0:
                return 1.0  # Máxima distância
            
            similarity = dot_product / (norm1 * norm2)
            distance = 1 - similarity
            return max(0, min(1, distance))  # Garantir entre 0 e 1
            
        except Exception as e:
            logger.error(f"Erro no cálculo de similaridade: {e}")
            return 1.0
    
    def identificar_agentes_relevantes(self, area: str, texto: str, resultados: List[Dict]) -> List[Dict]:
        """Identifica agentes mais relevantes para a consulta"""
        agentes_encontrados = {}
        
        for resultado in resultados:
            agente_id = resultado.get('agente_id')
            if agente_id and agente_id in self.agentes_config:
                if agente_id not in agentes_encontrados:
                    config_agente = self.agentes_config[agente_id]
                    agentes_encontrados[agente_id] = {
                        "agente_id": agente_id,
                        "nome": config_agente.get('nome', agente_id),
                        "especialidade": config_agente.get('especialidade', ''),
                        "modelo_preferencial": config_agente.get('modelo_preferencial', 'gpt-4o'),
                        "relevancia_score": resultado['score'],
                        "documentos_encontrados": 1
                    }
                else:
                    agentes_encontrados[agente_id]["documentos_encontrados"] += 1
                    # Atualizar score com média ponderada
                    agentes_encontrados[agente_id]["relevancia_score"] = (
                        agentes_encontrados[agente_id]["relevancia_score"] + resultado['score']
                    ) / 2
        
        # Retornar top 5 agentes mais relevantes
        return sorted(agentes_encontrados.values(), 
                     key=lambda x: x['relevancia_score'], 
                     reverse=True)[:5]
    
    def busca_simples_por_area(self, area: str, termo: str, limite: int = 5) -> List[Dict]:
        """Busca simples por texto sem usar embeddings"""
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            tabela = f"embeddings_{area}"
            
            cursor.execute(f"""
                SELECT id, conteudo, referencia, agente_id 
                FROM {tabela}
                WHERE conteudo ILIKE %s
                ORDER BY data_criacao DESC
                LIMIT %s
            """, (f'%{termo}%', limite))
            
            resultados = []
            for row in cursor.fetchall():
                resultados.append({
                    'id': str(row[0]),
                    'conteudo': row[1][:300] + "...",
                    'referencia': row[2],
                    'agente_id': row[3]
                })
            
            cursor.close()
            conn.close()
            return resultados
            
        except Exception as e:
            logger.error(f"Erro na busca simples: {e}")
            return []

# Instância global do orquestrador
orquestrador_otimizado = OrquestradorConsultasOtimizado()

def orquestrar_consulta(area: str, texto: str, agente_id: Optional[str] = None, limite: int = 10) -> Dict[str, Any]:
    """Função pública para orquestração de consultas"""
    return orquestrador_otimizado.orquestrar_consulta(area, texto, agente_id, limite)

def busca_simples(area: str, termo: str, limite: int = 5) -> List[Dict]:
    """Função pública para busca simples"""
    return orquestrador_otimizado.busca_simples_por_area(area, termo, limite)
