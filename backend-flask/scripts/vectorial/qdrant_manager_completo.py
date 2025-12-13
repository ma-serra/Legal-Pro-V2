#!/usr/bin/env python3
"""
Gerenciador Completo Qdrant - 19 Bases Vetoriais Jurídicas
Conecta e gerencia todas as áreas jurídicas no Qdrant Cloud
"""

import os
import json
import logging
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import openai
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, 
    FieldCondition, MatchValue, SearchRequest
)
from qdrant_client.http.exceptions import ResponseHandlingException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QdrantManagerCompleto:
    """Gerenciador completo para 19 bases vetoriais jurídicas"""
    
    # Configuração das 19 áreas jurídicas
    AREAS_JURIDICAS = {
        'criminal': {
            'collection': 'direito_criminal',
            'description': 'Direito Criminal e Penal',
            'vector_size': 1536,
            'distance': Distance.COSINE
        },
        'civil': {
            'collection': 'direito_civil',
            'description': 'Direito Civil',
            'vector_size': 1536,
            'distance': Distance.COSINE
        },
        'trabalhista': {
            'collection': 'direito_trabalhista',
            'description': 'Direito Trabalhista',
            'vector_size': 1536,
            'distance': Distance.COSINE
        },
        'tributario': {
            'collection': 'direito_tributario',
            'description': 'Direito Tributário',
            'vector_size': 1536,
            'distance': Distance.COSINE
        },
        'administrativo': {
            'collection': 'direito_administrativo',
            'description': 'Direito Administrativo',
            'vector_size': 1536,
            'distance': Distance.COSINE
        },
        'constitucional': {
            'collection': 'direito_constitucional',
            'description': 'Direito Constitucional',
            'vector_size': 1536,
            'distance': Distance.COSINE
        },
        'empresarial': {
            'collection': 'direito_empresarial',
            'description': 'Direito Empresarial',
            'vector_size': 1536,
            'distance': Distance.COSINE
        },
        'consumidor': {
            'collection': 'direito_consumidor',
            'description': 'Direito do Consumidor',
            'vector_size': 1536,
            'distance': Distance.COSINE
        },
        'familia': {
            'collection': 'direito_familia',
            'description': 'Direito de Família',
            'vector_size': 1536,
            'distance': Distance.COSINE
        },
        'previdenciario': {
            'collection': 'direito_previdenciario',
            'description': 'Direito Previdenciário',
            'vector_size': 1536,
            'distance': Distance.COSINE
        },
        'ambiental': {
            'collection': 'direito_ambiental',
            'description': 'Direito Ambiental',
            'vector_size': 1536,
            'distance': Distance.COSINE
        },
        'agrario': {
            'collection': 'direito_agrario',
            'description': 'Direito Agrário',
            'vector_size': 1536,
            'distance': Distance.COSINE
        },
        'imobiliario': {
            'collection': 'direito_imobiliario',
            'description': 'Direito Imobiliário',
            'vector_size': 1536,
            'distance': Distance.COSINE
        },
        'digital': {
            'collection': 'direito_digital',
            'description': 'Direito Digital',
            'vector_size': 1536,
            'distance': Distance.COSINE
        },
        'bancario': {
            'collection': 'direito_bancario',
            'description': 'Direito Bancário',
            'vector_size': 1536,
            'distance': Distance.COSINE
        },
        'seguros': {
            'collection': 'direito_seguros',
            'description': 'Direito de Seguros',
            'vector_size': 1536,
            'distance': Distance.COSINE
        },
        'conflitos': {
            'collection': 'conflitos_mediacao',
            'description': 'Negociação e Conflitos',
            'vector_size': 1536,
            'distance': Distance.COSINE
        },
        'riscos': {
            'collection': 'analise_riscos',
            'description': 'Análise de Riscos Jurídicos',
            'vector_size': 1536,
            'distance': Distance.COSINE
        },
        'sucessorio': {
            'collection': 'direito_sucessorio',
            'description': 'Direito Sucessório',
            'vector_size': 1536,
            'distance': Distance.COSINE
        }
    }
    
    def __init__(self):
        """Inicializa o gerenciador Qdrant"""
        self.client = None
        self.openai_client = None
        self._init_clients()
        self.status_conexoes = {}
    
    def _init_clients(self):
        """Inicializa clientes Qdrant e OpenAI"""
        try:
            # Cliente Qdrant
            qdrant_url = os.environ.get('QDRANT_URL')
            qdrant_api_key = os.environ.get('QDRANT_API_KEY')
            
            if qdrant_url and qdrant_api_key:
                self.client = QdrantClient(
                    url=qdrant_url,
                    api_key=qdrant_api_key
                )
                logger.info(f"✅ Qdrant conectado: {qdrant_url}")
            else:
                self.client = QdrantClient(":memory:")
                logger.warning("⚠️ Qdrant em memória (credenciais não encontradas)")
            
            # Cliente OpenAI
            openai_api_key = os.environ.get('OPENAI_API_KEY')
            if openai_api_key:
                self.openai_client = openai.OpenAI(api_key=openai_api_key)
                logger.info("✅ OpenAI conectado")
            else:
                logger.error("❌ OpenAI API key não encontrada")
                
        except Exception as e:
            logger.error(f"❌ Erro na inicialização: {e}")
            self.client = QdrantClient(":memory:")
    
    def criar_todas_colecoes(self) -> Dict[str, bool]:
        """Cria todas as 19 coleções no Qdrant"""
        resultados = {}
        
        for area, config in self.AREAS_JURIDICAS.items():
            try:
                collection_name = config['collection']
                
                # Verificar se já existe
                try:
                    self.client.get_collection(collection_name)
                    logger.info(f"✅ Coleção {collection_name} já existe")
                    resultados[area] = True
                    continue
                except:
                    pass
                
                # Criar coleção
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=config['vector_size'],
                        distance=config['distance']
                    )
                )
                
                logger.info(f"✅ Coleção {collection_name} criada")
                resultados[area] = True
                
            except Exception as e:
                logger.error(f"❌ Erro ao criar coleção {area}: {e}")
                resultados[area] = False
        
        return resultados
    
    def gerar_embedding(self, texto: str) -> List[float]:
        """Gera embedding usando OpenAI"""
        try:
            if not self.openai_client:
                raise Exception("Cliente OpenAI não inicializado")
            
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=texto
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            # Retornar embedding zero como fallback
            return [0.0] * 1536
    
    def inserir_documento(
        self, 
        area: str, 
        texto: str, 
        metadata: Optional[Dict] = None
    ) -> bool:
        """Insere documento em uma área específica"""
        try:
            if area not in self.AREAS_JURIDICAS:
                raise ValueError(f"Área {area} não reconhecida")
            
            collection_name = self.AREAS_JURIDICAS[area]['collection']
            
            # Gerar embedding
            embedding = self.gerar_embedding(texto)
            
            # Preparar payload
            payload = {
                'area': area,
                'texto': texto,
                'timestamp': datetime.now().isoformat(),
                **(metadata or {})
            }
            
            # Inserir no Qdrant
            point_id = str(uuid.uuid4())
            
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
            
            logger.info(f"✅ Documento inserido em {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inserir documento: {e}")
            return False
    
    def buscar_documentos(
        self, 
        area: str, 
        consulta: str, 
        limite: int = 10,
        filtros: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Busca documentos em uma área específica"""
        try:
            if area not in self.AREAS_JURIDICAS:
                return {
                    'erro': f'Área {area} não reconhecida',
                    'areas_disponiveis': list(self.AREAS_JURIDICAS.keys())
                }
            
            collection_name = self.AREAS_JURIDICAS[area]['collection']
            
            # Gerar embedding da consulta
            embedding_consulta = self.gerar_embedding(consulta)
            
            # Preparar filtros
            query_filter = None
            if filtros:
                conditions = []
                for key, value in filtros.items():
                    conditions.append(
                        FieldCondition(key=key, match=MatchValue(value=value))
                    )
                if conditions:
                    query_filter = Filter(must=conditions)
            
            # Realizar busca
            resultados = self.client.search(
                collection_name=collection_name,
                query_vector=embedding_consulta,
                limit=limite,
                query_filter=query_filter,
                with_payload=True,
                with_vectors=False
            )
            
            # Processar resultados
            documentos = []
            for hit in resultados:
                documentos.append({
                    'id': hit.id,
                    'score': hit.score,
                    'texto': hit.payload.get('texto', ''),
                    'area': hit.payload.get('area', area),
                    'metadata': {k: v for k, v in hit.payload.items() 
                               if k not in ['texto', 'area']}
                })
            
            return {
                'status': 'sucesso',
                'area': area,
                'consulta': consulta,
                'total_encontrados': len(documentos),
                'documentos': documentos
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na busca: {e}")
            return {
                'status': 'erro',
                'erro': str(e),
                'area': area,
                'consulta': consulta
            }
    
    def buscar_multiplas_areas(
        self, 
        areas: List[str], 
        consulta: str, 
        limite_por_area: int = 5
    ) -> Dict[str, Any]:
        """Busca em múltiplas áreas simultaneamente"""
        resultados = {}
        
        for area in areas:
            if area in self.AREAS_JURIDICAS:
                resultado = self.buscar_documentos(area, consulta, limite_por_area)
                resultados[area] = resultado
            else:
                resultados[area] = {
                    'status': 'erro',
                    'erro': f'Área {area} não reconhecida'
                }
        
        return {
            'status': 'sucesso',
            'consulta': consulta,
            'areas_pesquisadas': areas,
            'resultados': resultados,
            'total_areas': len(resultados)
        }
    
    def obter_status_sistema(self) -> Dict[str, Any]:
        """Obtém status completo do sistema"""
        try:
            collections = self.client.get_collections()
            
            status_colecoes = {}
            total_documentos = 0
            
            for area, config in self.AREAS_JURIDICAS.items():
                collection_name = config['collection']
                try:
                    info = self.client.get_collection(collection_name)
                    count = info.points_count if hasattr(info, 'points_count') else 0
                    status_colecoes[area] = {
                        'collection': collection_name,
                        'documentos': count,
                        'status': 'ativa'
                    }
                    total_documentos += count
                except:
                    status_colecoes[area] = {
                        'collection': collection_name,
                        'documentos': 0,
                        'status': 'não_encontrada'
                    }
            
            return {
                'status': 'operacional',
                'total_colecoes': len(collections.collections),
                'areas_configuradas': len(self.AREAS_JURIDICAS),
                'total_documentos': total_documentos,
                'colecoes': status_colecoes,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'erro',
                'erro': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def popular_com_dados_exemplo(self) -> Dict[str, int]:
        """Popula cada área com dados de exemplo"""
        contadores = {}
        
        # Dados de exemplo por área
        dados_exemplo = {
            'criminal': [
                "Art. 121. Matar alguém: Pena - reclusão, de seis a vinte anos.",
                "Art. 155. Subtrair, para si ou para outrem, coisa alheia móvel.",
                "Art. 171. Obter, para si ou para outrem, vantagem ilícita, em prejuízo alheio."
            ],
            'civil': [
                "Art. 186. Aquele que, por ação ou omissão voluntária, negligência ou imprudência, violar direito e causar dano a outrem, ainda que exclusivamente moral, comete ato ilícito.",
                "Art. 927. Aquele que, por ato ilícito, causar dano a outrem, fica obrigado a repará-lo.",
                "Art. 1.228. O proprietário tem a faculdade de usar, gozar e dispor da coisa, e o direito de reavê-la do poder de quem quer que injustamente a possua ou detenha."
            ]
        }
        
        for area, textos in dados_exemplo.items():
            contador = 0
            for texto in textos:
                if self.inserir_documento(area, texto, {'tipo': 'exemplo', 'fonte': 'codigo'}):
                    contador += 1
            contadores[area] = contador
            logger.info(f"✅ {contador} documentos inseridos em {area}")
        
        return contadores

# Instância global
qdrant_manager = QdrantManagerCompleto()

def obter_manager() -> QdrantManagerCompleto:
    """Retorna instância do gerenciador Qdrant"""
    return qdrant_manager

if __name__ == "__main__":
    # Teste do sistema
    manager = QdrantManagerCompleto()
    
    # Criar coleções
    print("Criando coleções...")
    resultados = manager.criar_todas_colecoes()
    print(f"Coleções criadas: {sum(resultados.values())}/{len(resultados)}")
    
    # Popular com dados exemplo
    print("Populando com dados exemplo...")
    contadores = manager.popular_com_dados_exemplo()
    print(f"Documentos inseridos: {contadores}")
    
    # Status do sistema
    print("Status do sistema:")
    status = manager.obter_status_sistema()
    print(json.dumps(status, indent=2, ensure_ascii=False))