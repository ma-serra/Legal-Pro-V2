"""
Módulo de Busca Semântica Avançada para Direito Penal
Integra busca vetorial com conhecimento específico dos códigos penais
"""

import os
import json
import logging
import psycopg2
from typing import List, Dict, Any, Optional
from openai import OpenAI
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

logger = logging.getLogger(__name__)

class BuscaSemanticaPenal:
    """Sistema de busca semântica especializado em direito penal"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        self.db_url = os.environ.get('DATABASE_URL')
        
        # Configuração Qdrant
        qdrant_url = os.environ.get('QDRANT_URL')
        qdrant_key = os.environ.get('QDRANT_API_KEY')
        
        if qdrant_url and qdrant_key:
            self.qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_key)
        else:
            self.qdrant_client = None
            logger.warning("Qdrant não configurado, usando apenas busca PostgreSQL")
        
        # Padrões específicos do direito penal
        self.padroes_penais = {
            'crimes_vida': ['homicídio', 'feminicídio', 'infanticídio', 'suicídio'],
            'crimes_patrimonio': ['furto', 'roubo', 'estelionato', 'apropriação'],
            'crimes_pessoa': ['lesão corporal', 'sequestro', 'cárcere privado'],
            'procedimentos': ['prisão preventiva', 'liberdade provisória', 'medidas cautelares'],
            'tribunal_juri': ['pronúncia', 'quesitos', 'conselho sentença', 'plenário'],
            'penas': ['reclusão', 'detenção', 'multa', 'regime fechado', 'regime aberto']
        }
    
    def gerar_embedding(self, texto: str) -> List[float]:
        """Gera embedding para texto usando OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=texto
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            return []
    
    def identificar_contexto_penal(self, consulta: str) -> Dict[str, Any]:
        """Identifica contexto específico da consulta penal"""
        consulta_lower = consulta.lower()
        contexto = {
            'categoria_principal': 'geral',
            'subcategorias': [],
            'artigos_relevantes': [],
            'codigo_fonte': 'ambos',
            'urgencia': 'normal',
            'tipo_procedimento': None
        }
        
        # Identifica categoria principal
        for categoria, termos in self.padroes_penais.items():
            if any(termo in consulta_lower for termo in termos):
                contexto['categoria_principal'] = categoria
                contexto['subcategorias'].extend([t for t in termos if t in consulta_lower])
        
        # Identifica artigos mencionados
        import re
        artigos = re.findall(r'art\.?\s*(\d+)', consulta_lower)
        contexto['artigos_relevantes'] = artigos
        
        # Determina código fonte prioritário
        if any(termo in consulta_lower for termo in ['procedimento', 'processo', 'prisão', 'recurso']):
            contexto['codigo_fonte'] = 'cpp'
        elif any(termo in consulta_lower for termo in ['crime', 'pena', 'tipificação', 'dosimetria']):
            contexto['codigo_fonte'] = 'cp'
        
        # Identifica urgência
        if any(termo in consulta_lower for termo in ['urgente', 'flagrante', 'preventiva']):
            contexto['urgencia'] = 'alta'
        
        return contexto
    
    def busca_postgresql_otimizada(self, consulta: str, contexto: Dict[str, Any], limite: int = 10) -> List[Dict]:
        """Busca otimizada no PostgreSQL com base no contexto"""
        try:
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            
            # Constrói query baseada no contexto
            where_clauses = ["1=1"]
            params = []
            
            # Filtro por fonte (CP ou CPP)
            if contexto['codigo_fonte'] == 'cp':
                where_clauses.append("fonte = %s")
                params.append('Código Penal')
            elif contexto['codigo_fonte'] == 'cpp':
                where_clauses.append("fonte = %s")
                params.append('Código de Processo Penal')
            else:
                where_clauses.append("fonte IN (%s, %s)")
                params.extend(['Código Penal', 'Código de Processo Penal'])
            
            # Filtro por artigos específicos
            if contexto['artigos_relevantes']:
                placeholders = ','.join(['%s'] * len(contexto['artigos_relevantes']))
                where_clauses.append(f"artigo IN ({placeholders})")
                params.extend(contexto['artigos_relevantes'])
            
            # Busca por termos específicos
            termos_busca = contexto['subcategorias'] + [consulta]
            if termos_busca:
                busca_texto = ' | '.join([f"'{termo}'" for termo in termos_busca])
                where_clauses.append("to_tsvector('portuguese', conteudo) @@ plainto_tsquery('portuguese', %s)")
                params.append(' '.join(termos_busca))
            
            query = f"""
                SELECT 
                    documento, artigo, titulo, conteudo, categoria, fonte,
                    ts_rank(to_tsvector('portuguese', conteudo), plainto_tsquery('portuguese', %s)) as relevancia
                FROM base_vetorial_universal 
                WHERE {' AND '.join(where_clauses)}
                ORDER BY 
                    CASE WHEN artigo = ANY(%s) THEN 1 ELSE 2 END,
                    relevancia DESC,
                    CASE WHEN fonte = %s THEN 1 ELSE 2 END
                LIMIT %s
            """
            
            params_final = [' '.join(termos_busca)] + params + [contexto['artigos_relevantes'] or []] + [
                'Código Penal' if contexto['codigo_fonte'] == 'cp' else 'Código de Processo Penal'
            ] + [limite]
            
            cursor.execute(query, params_final)
            resultados = cursor.fetchall()
            
            docs = []
            for row in resultados:
                docs.append({
                    'documento': row[0],
                    'artigo': row[1],
                    'titulo': row[2],
                    'conteudo': row[3],
                    'categoria': row[4],
                    'fonte': row[5],
                    'relevancia': float(row[6]),
                    'tipo': 'postgresql'
                })
            
            cursor.close()
            conn.close()
            
            return docs
            
        except Exception as e:
            logger.error(f"Erro na busca PostgreSQL: {e}")
            return []
    
    def busca_qdrant_especializada(self, consulta: str, contexto: Dict[str, Any], limite: int = 10) -> List[Dict]:
        """Busca especializada no Qdrant para direito penal"""
        if not self.qdrant_client:
            return []
        
        try:
            # Gera embedding da consulta
            embedding = self.gerar_embedding(consulta)
            if not embedding:
                return []
            
            # Filtros baseados no contexto
            filtros = []
            
            # Filtro por fonte
            if contexto['codigo_fonte'] == 'cp':
                filtros.append(FieldCondition(key="fonte", match=MatchValue(value="Código Penal")))
            elif contexto['codigo_fonte'] == 'cpp':
                filtros.append(FieldCondition(key="fonte", match=MatchValue(value="Código de Processo Penal")))
            
            # Filtro por categoria
            if contexto['categoria_principal'] != 'geral':
                categoria_map = {
                    'crimes_vida': 'Crimes contra a Vida',
                    'crimes_patrimonio': 'Crimes contra o Patrimônio',
                    'crimes_pessoa': 'Crimes contra a Pessoa',
                    'procedimentos': 'Prisão e Medidas Cautelares',
                    'tribunal_juri': 'Tribunal do Júri'
                }
                categoria = categoria_map.get(contexto['categoria_principal'])
                if categoria:
                    filtros.append(FieldCondition(key="categoria", match=MatchValue(value=categoria)))
            
            # Executa busca
            filter_obj = Filter(must=filtros) if filtros else None
            
            resultados = self.qdrant_client.search(
                collection_name="direito_penal",
                query_vector=embedding,
                query_filter=filter_obj,
                limit=limite,
                score_threshold=0.7
            )
            
            docs = []
            for resultado in resultados:
                payload = resultado.payload
                docs.append({
                    'documento': payload.get('documento', ''),
                    'artigo': payload.get('artigo', ''),
                    'titulo': payload.get('titulo', ''),
                    'conteudo': payload.get('conteudo', ''),
                    'categoria': payload.get('categoria', ''),
                    'fonte': payload.get('fonte', ''),
                    'relevancia': resultado.score,
                    'tipo': 'qdrant'
                })
            
            return docs
            
        except Exception as e:
            logger.error(f"Erro na busca Qdrant: {e}")
            return []
    
    def fusao_resultados(self, resultados_pg: List[Dict], resultados_qdrant: List[Dict]) -> List[Dict]:
        """Fusiona e ranqueia resultados de ambas as fontes"""
        todos_resultados = []
        
        # Normaliza scores para comparação
        max_pg = max([r['relevancia'] for r in resultados_pg], default=1.0)
        max_qdrant = max([r['relevancia'] for r in resultados_qdrant], default=1.0)
        
        # Processa resultados PostgreSQL
        for doc in resultados_pg:
            doc['score_normalizado'] = doc['relevancia'] / max_pg
            doc['peso_fonte'] = 0.6  # PostgreSQL tem peso maior para busca textual
            todos_resultados.append(doc)
        
        # Processa resultados Qdrant
        for doc in resultados_qdrant:
            doc['score_normalizado'] = doc['relevancia'] / max_qdrant if max_qdrant > 0 else 0
            doc['peso_fonte'] = 0.8  # Qdrant tem peso maior para busca semântica
            todos_resultados.append(doc)
        
        # Remove duplicatas baseado em artigo
        docs_unicos = {}
        for doc in todos_resultados:
            chave = f"{doc['fonte']}_{doc['artigo']}"
            if chave not in docs_unicos or doc['score_normalizado'] > docs_unicos[chave]['score_normalizado']:
                docs_unicos[chave] = doc
        
        # Calcula score final e ordena
        resultados_finais = list(docs_unicos.values())
        for doc in resultados_finais:
            doc['score_final'] = doc['score_normalizado'] * doc['peso_fonte']
        
        return sorted(resultados_finais, key=lambda x: x['score_final'], reverse=True)
    
    def buscar(self, consulta: str, limite: int = 15) -> Dict[str, Any]:
        """Método principal de busca semântica avançada"""
        try:
            # Identifica contexto
            contexto = self.identificar_contexto_penal(consulta)
            
            # Executa buscas em paralelo
            resultados_pg = self.busca_postgresql_otimizada(consulta, contexto, limite)
            resultados_qdrant = self.busca_qdrant_especializada(consulta, contexto, limite//2)
            
            # Fusiona resultados
            resultados_finais = self.fusao_resultados(resultados_pg, resultados_qdrant)
            
            # Limita resultado final
            resultados_finais = resultados_finais[:limite]
            
            return {
                'resultados': resultados_finais,
                'contexto': contexto,
                'total_encontrados': len(resultados_finais),
                'fontes_consultadas': {
                    'postgresql': len(resultados_pg),
                    'qdrant': len(resultados_qdrant)
                },
                'sugestoes_refinamento': self._gerar_sugestoes(consulta, contexto, resultados_finais)
            }
            
        except Exception as e:
            logger.error(f"Erro na busca semântica: {e}")
            return {
                'resultados': [],
                'contexto': {'categoria_principal': 'erro'},
                'total_encontrados': 0,
                'erro': str(e)
            }
    
    def _gerar_sugestoes(self, consulta: str, contexto: Dict, resultados: List[Dict]) -> List[str]:
        """Gera sugestões para refinar a busca"""
        sugestoes = []
        
        if len(resultados) < 3:
            sugestoes.append("Tente usar termos mais genéricos ou sinônimos")
            
        if contexto['codigo_fonte'] == 'ambos':
            sugestoes.append("Especifique se busca por 'código penal' ou 'código processo penal'")
        
        if not contexto['artigos_relevantes']:
            sugestoes.append("Inclua números de artigos específicos se conhecer")
        
        if contexto['categoria_principal'] == 'geral':
            sugestoes.append("Use termos mais específicos da área penal")
        
        return sugestoes

def criar_api_busca_penal():
    """Cria endpoints da API para busca semântica penal"""
    from flask import Blueprint, request, jsonify
    
    bp = Blueprint('busca_penal', __name__, url_prefix='/api/busca-penal')
    busca_engine = BuscaSemanticaPenal()
    
    @bp.route('/buscar', methods=['POST'])
    def buscar():
        """Endpoint principal de busca"""
        try:
            data = request.get_json()
            consulta = data.get('consulta', '').strip()
            limite = min(data.get('limite', 15), 50)  # Máximo 50 resultados
            
            if not consulta:
                return jsonify({'erro': 'Consulta não pode estar vazia'}), 400
            
            resultado = busca_engine.buscar(consulta, limite)
            return jsonify(resultado)
            
        except Exception as e:
            logger.error(f"Erro no endpoint de busca: {e}")
            return jsonify({'erro': 'Erro interno do servidor'}), 500
    
    @bp.route('/contexto', methods=['POST'])
    def analisar_contexto():
        """Endpoint para análise de contexto"""
        try:
            data = request.get_json()
            consulta = data.get('consulta', '').strip()
            
            if not consulta:
                return jsonify({'erro': 'Consulta não pode estar vazia'}), 400
            
            contexto = busca_engine.identificar_contexto_penal(consulta)
            return jsonify({'contexto': contexto})
            
        except Exception as e:
            logger.error(f"Erro na análise de contexto: {e}")
            return jsonify({'erro': 'Erro interno do servidor'}), 500
    
    return bp