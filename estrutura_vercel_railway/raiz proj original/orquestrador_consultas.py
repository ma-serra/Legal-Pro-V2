
"""
Orquestrador Inteligente de Consultas Jurídicas
Sistema de busca com embeddings duplos e rerank automático
"""

import psycopg2
import openai
from typing import Dict, List, Optional, Any
import json
import logging

logger = logging.getLogger(__name__)

class OrquestradorConsultas:
    """Orquestrador principal para consultas multi-agente"""
    
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        self.openai_client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        self.agentes_config = self.carregar_configuracao_agentes()
    
    def carregar_configuracao_agentes(self) -> Dict:
        """Carrega configuração dos 309 agentes"""
        try:
            with open('agentes_config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Arquivo de configuração de agentes não encontrado")
            return {}
    
    def gerar_embeddings_consulta(self, texto: str) -> Dict[str, List[float]]:
        """Gera embeddings da consulta para busca"""
        try:
            # Small embedding para busca inicial
            response_small = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=texto
            )
            
            # Large embedding para rerank
            response_large = self.openai_client.embeddings.create(
                model="text-embedding-3-large", 
                input=texto
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
        Função principal de orquestração
        
        Args:
            area: Área jurídica (ex: 'direito_penal')
            texto: Texto da consulta
            agente_id: ID específico do agente (opcional)
            limite: Número máximo de resultados
            
        Returns:
            Dict com resultados ranqueados e metadados
        """
        try:
            # 1. Gerar embeddings da consulta
            embeddings = self.gerar_embeddings_consulta(texto)
            if not embeddings['small']:
                return {"erro": "Falha ao gerar embeddings"}
            
            # 2. Conectar ao banco
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            # 3. Busca inicial com embedding small
            tabela = f"embeddings_{area}"
            
            sql_busca = f"""
                SELECT id, conteudo, referencia, agente_id, metadata,
                       embedding_small <=> %s as distancia_small,
                       embedding_large <=> %s as distancia_large
                FROM {tabela}
                WHERE embedding_small IS NOT NULL 
                  AND embedding_large IS NOT NULL
            """
            
            params = [embeddings['small'], embeddings['large']]
            
            # Filtrar por agente específico se fornecido
            if agente_id:
                sql_busca += " AND agente_id = %s"
                params.append(agente_id)
            
            sql_busca += f"""
                ORDER BY embedding_small <=> %s
                LIMIT {limite * 2}
            """
            params.append(embeddings['small'])
            
            cursor.execute(sql_busca, params)
            resultados_iniciais = cursor.fetchall()
            
            # 4. Rerank com embedding large
            resultados_reranked = []
            for resultado in resultados_iniciais:
                doc_id, conteudo, referencia, agente, metadata, dist_small, dist_large = resultado
                
                # Score combinado (70% large, 30% small)
                score_final = (0.7 * (1 - dist_large)) + (0.3 * (1 - dist_small))
                
                resultados_reranked.append({
                    'id': doc_id,
                    'conteudo': conteudo,
                    'referencia': referencia,
                    'agente_id': agente,
                    'metadata': metadata,
                    'score': score_final,
                    'distancia_small': dist_small,
                    'distancia_large': dist_large
                })
            
            # 5. Ordenar por score final e limitar
            resultados_finais = sorted(resultados_reranked, key=lambda x: x['score'], reverse=True)[:limite]
            
            # 6. Buscar agentes relevantes
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
                    "embeddings_utilizados": "small + large",
                    "rerank_aplicado": True,
                    "agente_filtro": agente_id
                }
            }
            
        except Exception as e:
            logger.error(f"Erro na orquestração: {e}")
            return {"erro": str(e), "status": "erro"}
    
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

# Instância global do orquestrador
orquestrador = OrquestradorConsultas()

def orquestrar_consulta(area: str, texto: str, agente_id: Optional[str] = None, limite: int = 10) -> Dict[str, Any]:
    """Função pública para orquestração de consultas"""
    return orquestrador.orquestrar_consulta(area, texto, agente_id, limite)
