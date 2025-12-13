"""
Conexão com o PostgreSQL e funções para pgvector 
"""
import os
import numpy as np
from sqlalchemy import create_engine, text
import logging
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()

# Inicializa a conexão com o PostgreSQL
pg_uri = os.getenv("DATABASE_URL")  # Usa DATABASE_URL que é o padrão do Replit
pg = create_engine(pg_uri, pool_pre_ping=True, pool_recycle=300)

# Função para verificar se a extensão pgvector já está instalada
def check_pgvector_extension():
    try:
        with pg.connect() as conn:
            result = conn.execute(text("SELECT * FROM pg_extension WHERE extname = 'vector'"))
            if result.fetchone() is None:
                logger.info("Extensão pgvector não encontrada. Instalando...")
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                logger.info("Extensão pgvector instalada com sucesso")
            else:
                logger.info("Extensão pgvector já está instalada")
    except Exception as e:
        logger.error(f"Erro ao verificar/instalar extensão pgvector: {e}")
        raise

# Função para verificar e criar a tabela de conhecimento
def check_knowledge_table():
    try:
        with pg.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'knowledge'
                )
            """))
            
            if not result.fetchone()[0]:
                logger.info("Tabela de conhecimento não encontrada. Criando...")
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS knowledge (
                        id SERIAL PRIMARY KEY,
                        source_id TEXT,
                        chunk TEXT,
                        embedding VECTOR(1536)
                    )
                """))
                
                # Criar índice HNSW
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS knowledge_embedding_hnsw
                    ON knowledge
                    USING hnsw (embedding vector_cosine_ops)
                """))
                
                logger.info("Tabela de conhecimento e índice criados com sucesso")
            else:
                logger.info("Tabela de conhecimento já existe")
    
    except Exception as e:
        logger.error(f"Erro ao verificar/criar tabela de conhecimento: {e}")
        raise

# Função para obter embeddings usando o modelo configurado
def embed(texts: list[str]) -> list[list[float]]:
    """
    Gera embeddings para os textos fornecidos usando o modelo configurado
    
    Args:
        texts: Lista de textos para gerar embeddings
    
    Returns:
        Lista de embeddings (vetores de floats)
    """
    embedding_model = os.getenv("EMBEDDING_MODEL", "openai")
    
    try:
        # OpenAI (modelo padrão)
        if embedding_model == "openai":
            import openai
            openai.api_key = os.getenv("OPENAI_API_KEY")
            response = openai.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            return [data.embedding for data in response.data]
        
        # Anthropic
        elif embedding_model == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            embeddings = []
            for text in texts:
                response = client.embeddings.create(
                    model="claude-3-5-sonnet-20241022-embeddings",
                    input=text
                )
                embeddings.append(response.embedding)
            return embeddings
        
        # Google Gemini
        elif embedding_model == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            embeddings = []
            for text in texts:
                response = genai.embed_content(
                    model="embedding-001",
                    content=text
                )
                embeddings.append(response.embedding)
            return embeddings
        
        # Outros modelos podem ser adicionados aqui
        else:
            raise ValueError(f"Modelo de embedding não suportado: {embedding_model}")
    
    except Exception as e:
        logger.error(f"Erro ao gerar embeddings: {e}")
        # Fallback para um modelo local simples em caso de erro
        from sklearn.feature_extraction.text import TfidfVectorizer
        logger.warning("Usando modelo de fallback TF-IDF para embeddings")
        vectorizer = TfidfVectorizer(max_features=1536)
        tfidf_matrix = vectorizer.fit_transform(texts)
        return [vector.toarray()[0].tolist() for vector in tfidf_matrix]

# Função para buscar informações no pgvector
def search_pgvector(query: str, top_k: int = 4) -> list[str]:
    """
    Busca os chunks mais relevantes para a query usando pgvector
    
    Args:
        query: Texto da consulta
        top_k: Número de resultados a retornar
    
    Returns:
        Lista de chunks de texto relevantes
    """
    try:
        # Gerar embedding para a query
        q_emb = embed([query])[0]
        
        # Executar busca vetorial no PostgreSQL
        sql = text("""
            SELECT chunk
            FROM knowledge
            ORDER BY embedding <-> :q_emb
            LIMIT :k
        """)
        
        with pg.connect() as conn:
            rows = conn.execute(sql, {"q_emb": np.array(q_emb), "k": top_k})
            return [row[0] for row in rows]
    
    except Exception as e:
        logger.error(f"Erro na busca vetorial: {e}")
        return []

# Inicializa o banco de dados
def init_db():
    """Inicializa o banco de dados e cria estruturas necessárias"""
    try:
        logger.info("Inicializando banco de dados para o Assistente...")
        check_pgvector_extension()
        check_knowledge_table()
        logger.info("Banco de dados inicializado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {e}")