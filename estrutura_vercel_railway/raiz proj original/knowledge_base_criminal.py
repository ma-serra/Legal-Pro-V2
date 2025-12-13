"""
Sistema de Base de Conhecimento Vetorial para Agentes de Direito Criminal
"""
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DocumentoJuridico:
    """Representa um documento jurídico para indexação vetorial."""
    id: str
    titulo: str
    conteudo: str
    tipo: str  # "jurisprudencia", "legislacao", "doutrina", "laudo", "modelo_peca"
    categoria_criminal: str  # "homicidio", "furto", "drogas", "transito", etc.
    agente_especializado: str  # Para qual agente este documento é mais relevante
    fonte: str
    data_publicacao: Optional[datetime] = None
    relevancia: int = 5  # Escala 1-10 de relevância para o agente
    tags: List[str] = None
    metadados: Dict[str, Any] = None

class BaseConhecimentoCriminal:
    """Gerenciador da base de conhecimento vetorial para agentes criminais."""
    
    def __init__(self):
        self.engine = create_engine(os.environ.get('DATABASE_URL'))
        self.session = sessionmaker(bind=self.engine)()
        
        # Mapeamento de agentes para suas especialidades
        self.agentes_especialidades = {
            "EspecialistaDireitoCriminalAgent": {
                "categorias": ["homicidio", "furto", "roubo", "estelionato", "lesao_corporal", "crimes_contra_honra"],
                "tipos_documento": ["legislacao", "jurisprudencia", "doutrina"],
                "collection_name": "criminal_geral"
            },
            "EspecialistaTribunalJuriAgent": {
                "categorias": ["homicidio", "latrocinio", "crimes_dolosos_contra_vida"],
                "tipos_documento": ["jurisprudencia", "modelo_peca", "tecnicas_oratoria"],
                "collection_name": "tribunal_juri"
            },
            "AnalistaEvidenciasCriminaisAgent": {
                "categorias": ["pericia", "laudos", "cadeia_custodia", "prova_tecnica"],
                "tipos_documento": ["laudo", "procedimento_pericial", "jurisprudencia_prova"],
                "collection_name": "evidencias_criminais"
            },
            "EspecialistaExecucaoPenalAgent": {
                "categorias": ["execucao_penal", "progressao_regime", "beneficios", "medidas_alternativas"],
                "tipos_documento": ["legislacao", "jurisprudencia", "parecer_tecnico"],
                "collection_name": "execucao_penal"
            },
            "AssessorSustentacaoJuriAgent": {
                "categorias": ["oratoria", "persuasao", "argumentacao", "retorica_juridica"],
                "tipos_documento": ["tecnicas_oratoria", "modelo_sustentacao", "estrategias"],
                "collection_name": "sustentacao_oral"
            },
            "RevisorDireitoPenalAgent": {
                "categorias": ["revisao", "segunda_opiniao", "analise_critica"],
                "tipos_documento": ["doutrina", "jurisprudencia", "comentarios"],
                "collection_name": "revisao_penal"
            }
        }
    
    def criar_estrutura_vetorial(self):
        """Cria a estrutura de tabelas para armazenamento vetorial especializado."""
        try:
            # Tabela principal para documentos criminais
            self.session.execute(text("""
                CREATE TABLE IF NOT EXISTS conhecimento_criminal (
                    id SERIAL PRIMARY KEY,
                    documento_id VARCHAR(100) UNIQUE NOT NULL,
                    agente_especializado VARCHAR(100) NOT NULL,
                    titulo TEXT NOT NULL,
                    conteudo TEXT NOT NULL,
                    tipo_documento VARCHAR(50) NOT NULL,
                    categoria_criminal VARCHAR(50) NOT NULL,
                    fonte VARCHAR(200),
                    data_publicacao TIMESTAMP,
                    relevancia INTEGER DEFAULT 5,
                    tags TEXT[], -- Array de tags
                    metadados JSONB,
                    embedding VECTOR(1536), -- Para embeddings OpenAI
                    data_indexacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ativo BOOLEAN DEFAULT TRUE
                );
            """))
            
            # Índices para otimização
            self.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_conhecimento_criminal_agente 
                ON conhecimento_criminal(agente_especializado);
            """))
            
            self.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_conhecimento_criminal_categoria 
                ON conhecimento_criminal(categoria_criminal);
            """))
            
            self.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_conhecimento_criminal_tipo 
                ON conhecimento_criminal(tipo_documento);
            """))
            
            # Índice vetorial HNSW para busca semântica
            self.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_conhecimento_criminal_embedding_hnsw
                ON conhecimento_criminal
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """))
            
            self.session.commit()
            logger.info("Estrutura vetorial para conhecimento criminal criada com sucesso!")
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Erro ao criar estrutura vetorial: {str(e)}")
            raise
    
    def indexar_documento(self, documento: DocumentoJuridico, embedding: List[float]):
        """Indexa um documento jurídico na base vetorial."""
        try:
            query = text("""
                INSERT INTO conhecimento_criminal 
                (documento_id, agente_especializado, titulo, conteudo, tipo_documento, 
                 categoria_criminal, fonte, data_publicacao, relevancia, tags, 
                 metadados, embedding)
                VALUES 
                (:doc_id, :agente, :titulo, :conteudo, :tipo, :categoria, :fonte, 
                 :data_pub, :relevancia, :tags, :metadados, :embedding)
                ON CONFLICT (documento_id) 
                DO UPDATE SET
                    titulo = EXCLUDED.titulo,
                    conteudo = EXCLUDED.conteudo,
                    embedding = EXCLUDED.embedding,
                    data_indexacao = CURRENT_TIMESTAMP
            """)
            
            self.session.execute(query, {
                'doc_id': documento.id,
                'agente': documento.agente_especializado,
                'titulo': documento.titulo,
                'conteudo': documento.conteudo,
                'tipo': documento.tipo,
                'categoria': documento.categoria_criminal,
                'fonte': documento.fonte,
                'data_pub': documento.data_publicacao,
                'relevancia': documento.relevancia,
                'tags': documento.tags or [],
                'metadados': json.dumps(documento.metadados or {}),
                'embedding': np.array(embedding)
            })
            
            self.session.commit()
            logger.info(f"Documento {documento.id} indexado para agente {documento.agente_especializado}")
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Erro ao indexar documento: {str(e)}")
            raise
    
    def buscar_conhecimento(self, agente: str, query: str, embedding_query: List[float], 
                          top_k: int = 5, filtro_categoria: str = None, threshold: float = 0.8) -> List[Dict]:
        """Busca conhecimento especializado com análise semântica avançada."""
        try:
            # Query híbrida: similaridade vetorial + busca textual + análise semântica
            base_query = """
                WITH similaridade_vetorial AS (
                    SELECT 
                        documento_id, titulo, conteudo, tipo_documento, 
                        categoria_criminal, fonte, relevancia, tags, metadados,
                        (1 - (embedding <-> :embedding)) as similaridade_coseno,
                        (embedding <=> :embedding) as distancia_euclidiana
                    FROM conhecimento_criminal 
                    WHERE agente_especializado = :agente 
                        AND ativo = TRUE
                        AND (embedding <-> :embedding) < :threshold
                ),
                busca_textual AS (
                    SELECT 
                        documento_id,
                        ts_rank(to_tsvector('portuguese', titulo || ' ' || conteudo), 
                                plainto_tsquery('portuguese', :query_text)) as rank_textual
                    FROM conhecimento_criminal 
                    WHERE agente_especializado = :agente 
                        AND ativo = TRUE
                        AND (to_tsvector('portuguese', titulo || ' ' || conteudo) @@ 
                             plainto_tsquery('portuguese', :query_text))
                ),
                score_combinado AS (
                    SELECT 
                        sv.*,
                        COALESCE(bt.rank_textual, 0) as rank_textual,
                        -- Score híbrido: 70% similaridade vetorial + 30% busca textual
                        (sv.similaridade_coseno * 0.7 + COALESCE(bt.rank_textual, 0) * 0.3) as score_final,
                        -- Boost por relevância do documento
                        (sv.similaridade_coseno * 0.7 + COALESCE(bt.rank_textual, 0) * 0.3) * 
                        (sv.relevancia / 10.0) as score_ajustado
                    FROM similaridade_vetorial sv
                    LEFT JOIN busca_textual bt ON sv.documento_id = bt.documento_id
                )
                SELECT * FROM score_combinado
            """
            
            params = {
                'agente': agente,
                'embedding': np.array(embedding_query),
                'query_text': query,
                'threshold': threshold,
                'limit': top_k
            }
            
            # Filtros adicionais
            if filtro_categoria:
                base_query += " WHERE categoria_criminal = :categoria"
                params['categoria'] = filtro_categoria
            
            base_query += " ORDER BY score_ajustado DESC LIMIT :limit"
            
            result = self.session.execute(text(base_query), params)
            
            documentos = []
            for row in result:
                documentos.append({
                    'id': row.documento_id,
                    'titulo': row.titulo,
                    'conteudo': row.conteudo,
                    'tipo': row.tipo_documento,
                    'categoria': row.categoria_criminal,
                    'fonte': row.fonte,
                    'relevancia': row.relevancia,
                    'tags': row.tags,
                    'metadados': json.loads(getattr(row, 'metadados', '{}')) if hasattr(row, 'metadados') else {},
                    'similaridade_coseno': getattr(row, 'similaridade_coseno', 0),
                    'rank_textual': getattr(row, 'rank_textual', 0),
                    'score_final': getattr(row, 'score_final', 0),
                    'score_ajustado': getattr(row, 'score_ajustado', 0),
                    'distancia_euclidiana': getattr(row, 'distancia_euclidiana', 0)
                })
            
            return documentos
            
        except Exception as e:
            logger.error(f"Erro na busca de conhecimento: {str(e)}")
            return []
    
    def buscar_conhecimento_semantico_avancado(self, agente: str, query: str, embedding_query: List[float], 
                                             contexto_adicional: str = None, top_k: int = 10, 
                                             threshold_min: float = 0.7) -> List[Dict]:
        """
        Busca semântica avançada com múltiplas estratégias e análise contextual.
        """
        try:
            # Query com análise semântica multi-dimensional
            query_avancada = """
                WITH analise_semantica AS (
                    SELECT 
                        documento_id, titulo, conteudo, tipo_documento, 
                        categoria_criminal, fonte, relevancia, tags, metadados,
                        embedding,
                        -- Similaridade cosseno (principal)
                        (1 - (embedding <-> :embedding)) as sim_coseno,
                        -- Distância euclidiana normalizada
                        1 / (1 + (embedding <=> :embedding)) as sim_euclidiana,
                        -- Produto interno (dot product)
                        (embedding <#> :embedding) as produto_interno
                    FROM conhecimento_criminal 
                    WHERE agente_especializado = :agente 
                        AND ativo = TRUE
                        AND (1 - (embedding <-> :embedding)) >= :threshold_min
                ),
                busca_textual_avancada AS (
                    SELECT 
                        documento_id,
                        -- Busca por termos individuais
                        ts_rank(to_tsvector('portuguese', titulo || ' ' || conteudo), 
                               plainto_tsquery('portuguese', :query_text)) as rank_termos
                    FROM conhecimento_criminal 
                    WHERE agente_especializado = :agente 
                        AND ativo = TRUE
                        AND to_tsvector('portuguese', titulo || ' ' || conteudo) @@ 
                            plainto_tsquery('portuguese', :query_text)
                ),
                score_final AS (
                    SELECT 
                        a.*,
                        COALESCE(b.rank_termos, 0) as rank_termos,
                        -- Score combinado com pesos otimizados
                        (
                            a.sim_coseno * 0.6 +              -- Similaridade vetorial principal
                            a.sim_euclidiana * 0.2 +         -- Similaridade euclidiana
                            COALESCE(b.rank_termos, 0) * 0.2  -- Busca por termos
                        ) as score_base,
                        -- Boost por relevância do documento e tipo
                        CASE tipo_documento
                            WHEN 'legislacao' THEN 1.2
                            WHEN 'jurisprudencia' THEN 1.1
                            WHEN 'doutrina' THEN 1.0
                            WHEN 'modelo_peca' THEN 0.9
                            ELSE 1.0
                        END as boost_tipo
                    FROM analise_semantica a
                    LEFT JOIN busca_textual_avancada b ON a.documento_id = b.documento_id
                )
                SELECT 
                    *,
                    (score_base * boost_tipo * (relevancia / 10.0)) as score_final_ajustado
                FROM score_final
                ORDER BY score_final_ajustado DESC
                LIMIT :limit
            """
            
            params = {
                'agente': agente,
                'embedding': np.array(embedding_query),
                'query_text': query,
                'threshold_min': threshold_min,
                'limit': top_k
            }
            
            result = self.session.execute(text(query_avancada), params)
            
            documentos_avancados = []
            for row in result:
                documentos_avancados.append({
                    'id': row.documento_id,
                    'titulo': row.titulo,
                    'conteudo': row.conteudo,
                    'tipo': row.tipo_documento,
                    'categoria': row.categoria_criminal,
                    'fonte': row.fonte,
                    'relevancia': row.relevancia,
                    'tags': row.tags,
                    'metadados': json.loads(row.metadados) if row.metadados else {},
                    'scores': {
                        'similaridade_coseno': float(row.sim_coseno),
                        'similaridade_euclidiana': float(row.sim_euclidiana),
                        'produto_interno': float(row.produto_interno),
                        'rank_termos': float(row.rank_termos),
                        'score_base': float(row.score_base),
                        'boost_tipo': float(row.boost_tipo),
                        'score_final': float(row.score_final_ajustado)
                    }
                })
            
            return documentos_avancados
            
        except Exception as e:
            logger.error(f"Erro na busca semântica avançada: {str(e)}")
            # Fallback para busca simples
            return self.buscar_conhecimento(agente, query, embedding_query, top_k, threshold=0.7)
    
    def obter_estatisticas_base(self) -> Dict[str, Any]:
        """Obtém estatísticas da base de conhecimento."""
        try:
            # Total de documentos por agente
            query = text("""
                SELECT 
                    agente_especializado,
                    COUNT(*) as total_documentos,
                    COUNT(DISTINCT categoria_criminal) as categorias_cobertas,
                    AVG(relevancia) as relevancia_media
                FROM conhecimento_criminal 
                WHERE ativo = TRUE
                GROUP BY agente_especializado
            """)
            
            result = self.session.execute(query)
            
            estatisticas = {
                'agentes': {},
                'total_geral': 0
            }
            
            for row in result:
                estatisticas['agentes'][row.agente_especializado] = {
                    'total_documentos': row.total_documentos,
                    'categorias_cobertas': row.categorias_cobertas,
                    'relevancia_media': float(row.relevancia_media)
                }
                estatisticas['total_geral'] += row.total_documentos
            
            return estatisticas
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {}

# Exemplos de documentos para cada agente
DOCUMENTOS_EXEMPLO = {
    "EspecialistaDireitoCriminalAgent": [
        {
            "titulo": "Código Penal - Crimes Contra o Patrimônio",
            "tipo": "legislacao",
            "categoria": "furto",
            "conteudo": "Art. 155 - Subtrair, para si ou para outrem, coisa alheia móvel..."
        }
    ],
    "EspecialistaTribunalJuriAgent": [
        {
            "titulo": "Estratégias de Sustentação Oral no Júri",
            "tipo": "tecnicas_oratoria",
            "categoria": "homicidio",
            "conteudo": "Técnicas para apresentação eficaz perante o corpo de jurados..."
        }
    ]
}

def main():
    """Função principal para demonstrar o uso da base de conhecimento."""
    base = BaseConhecimentoCriminal()
    
    # Criar estrutura
    base.criar_estrutura_vetorial()
    
    # Obter estatísticas
    stats = base.obter_estatisticas_base()
    print("Estatísticas da Base de Conhecimento Criminal:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()