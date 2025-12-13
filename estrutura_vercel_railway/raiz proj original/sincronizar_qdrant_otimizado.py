#!/usr/bin/env python3
"""
Sincronização Otimizada PostgreSQL -> Qdrant Cloud
Processa em lotes pequenos para evitar timeouts
"""

import os
import psycopg2
import requests
import json
import logging
import uuid
from datetime import datetime
import openai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def conectar_postgresql():
    """Conecta ao PostgreSQL"""
    return psycopg2.connect(os.environ['DATABASE_URL'])

def gerar_embedding(texto, modelo="text-embedding-3-small"):
    """Gera embedding usando OpenAI"""
    try:
        openai.api_key = os.environ.get('OPENAI_API_KEY')
        if not openai.api_key:
            raise Exception("OpenAI API key não configurada")
        
        response = openai.embeddings.create(
            input=texto,
            model=modelo
        )
        
        return response.data[0].embedding
        
    except Exception as e:
        logger.error(f"Erro ao gerar embedding: {e}")
        return None

def garantir_collection_existe(collection_name, headers):
    """Garante que a collection existe no Qdrant"""
    try:
        qdrant_url = os.environ.get('QDRANT_URL')
        
        # Verificar se collection existe
        response = requests.get(
            f"{qdrant_url}/collections/{collection_name}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return True
        
        # Criar collection
        collection_config = {
            "vectors": {
                "size": 1536,
                "distance": "Cosine"
            }
        }
        
        create_response = requests.put(
            f"{qdrant_url}/collections/{collection_name}",
            headers=headers,
            json=collection_config,
            timeout=20
        )
        
        if create_response.status_code in [200, 201]:
            logger.info(f"Collection criada: {collection_name}")
            return True
        else:
            logger.error(f"Erro ao criar collection: {create_response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Erro ao verificar/criar collection: {e}")
        return False

def sincronizar_lote_pequeno(limite=10):
    """Sincroniza lote pequeno de chunks"""
    
    # Verificar credenciais
    qdrant_url = os.environ.get('QDRANT_URL')
    qdrant_key = os.environ.get('QDRANT_API_KEY')
    
    if not qdrant_url or not qdrant_key:
        logger.error("Credenciais Qdrant não configuradas")
        return {'sucesso': 0, 'erro': 0}
    
    headers = {
        'api-key': qdrant_key,
        'Content-Type': 'application/json'
    }
    
    # Conectar ao PostgreSQL
    conn = conectar_postgresql()
    cursor = conn.cursor()
    
    sucesso = 0
    erro = 0
    
    try:
        # Buscar chunks sem embedding
        cursor.execute(f"""
            SELECT chunk_id, titulo, conteudo, area_especializada, 
                   documento_pai_id, chunk_numero, is_chunk_filho
            FROM base_vetorial_universal
            WHERE embedding_vetor IS NULL
            AND conteudo IS NOT NULL
            AND LENGTH(TRIM(conteudo)) > 10
            LIMIT {limite}
        """)
        
        chunks = cursor.fetchall()
        logger.info(f"Processando {len(chunks)} chunks sem embedding")
        
        for chunk in chunks:
            try:
                chunk_id, titulo, conteudo, area, documento_pai_id, chunk_numero, is_filho = chunk
                
                # Gerar embedding
                embedding = gerar_embedding(conteudo[:1000])  # Limitar texto
                if not embedding:
                    erro += 1
                    continue
                
                # Salvar embedding no PostgreSQL
                cursor.execute(
                    "UPDATE base_vetorial_universal SET embedding_vetor = %s WHERE chunk_id = %s",
                    (json.dumps(embedding), chunk_id)
                )
                
                # Nome da collection
                area_clean = area.replace(' ', '_').replace('-', '_').lower() if area else 'geral'
                collection_name = f"juridico_{area_clean}"
                
                # Garantir collection existe
                if not garantir_collection_existe(collection_name, headers):
                    erro += 1
                    continue
                
                # Preparar payload para Qdrant
                payload = {
                    "points": [{
                        "id": str(uuid.uuid4()),
                        "vector": embedding,
                        "payload": {
                            "chunk_id": chunk_id,
                            "titulo": titulo or "",
                            "area_especializada": area or "",
                            "documento_pai_id": documento_pai_id or "",
                            "chunk_numero": chunk_numero or 0,
                            "is_chunk_filho": bool(is_filho),
                            "conteudo_preview": conteudo[:200] + "..." if len(conteudo) > 200 else conteudo,
                            "created_at": datetime.now().isoformat()
                        }
                    }]
                }
                
                # Upload para Qdrant
                response = requests.put(
                    f"{qdrant_url}/collections/{collection_name}/points",
                    headers=headers,
                    json=payload,
                    timeout=20
                )
                
                if response.status_code in [200, 201]:
                    sucesso += 1
                    logger.info(f"Sincronizado: {chunk_id}")
                else:
                    erro += 1
                    logger.error(f"Erro upload Qdrant: {response.status_code}")
                
                # Commit após cada chunk
                conn.commit()
                
            except Exception as e:
                erro += 1
                logger.error(f"Erro no chunk {chunk_id}: {e}")
                conn.rollback()
    
    finally:
        cursor.close()
        conn.close()
    
    return {'sucesso': sucesso, 'erro': erro, 'total': len(chunks)}

def verificar_status_sincronizacao():
    """Verifica status da sincronização"""
    conn = conectar_postgresql()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                COUNT(*) as total_chunks,
                COUNT(embedding_vetor) as com_embedding,
                COUNT(DISTINCT area_especializada) as areas_distintas
            FROM base_vetorial_universal
            WHERE conteudo IS NOT NULL
            AND LENGTH(TRIM(conteudo)) > 10
        """)
        
        resultado = cursor.fetchone()
        total, com_embedding, areas = resultado
        
        percentual = (com_embedding / total * 100) if total > 0 else 0
        
        return {
            'total_chunks': total,
            'com_embedding': com_embedding,
            'sem_embedding': total - com_embedding,
            'areas_distintas': areas,
            'percentual_completo': percentual
        }
        
    finally:
        cursor.close()
        conn.close()

def main():
    """Função principal - processa um lote pequeno"""
    logger.info("Iniciando sincronização otimizada PostgreSQL -> Qdrant")
    
    # Verificar status inicial
    status_inicial = verificar_status_sincronizacao()
    logger.info(f"Status inicial: {status_inicial['com_embedding']}/{status_inicial['total_chunks']} chunks com embedding ({status_inicial['percentual_completo']:.1f}%)")
    
    if status_inicial['sem_embedding'] == 0:
        logger.info("Todos os chunks já possuem embedding!")
        return
    
    # Processar lote pequeno
    resultado = sincronizar_lote_pequeno(limite=20)
    
    # Verificar status final
    status_final = verificar_status_sincronizacao()
    
    # Relatório
    logger.info("="*50)
    logger.info("RELATÓRIO DE SINCRONIZAÇÃO")
    logger.info("="*50)
    logger.info(f"Processados neste lote: {resultado['total']}")
    logger.info(f"Sincronizados com sucesso: {resultado['sucesso']}")
    logger.info(f"Erros: {resultado['erro']}")
    logger.info(f"Status atual: {status_final['com_embedding']}/{status_final['total_chunks']} chunks ({status_final['percentual_completo']:.1f}%)")
    logger.info(f"Restam: {status_final['sem_embedding']} chunks")
    
    # Salvar progresso
    progresso = {
        'timestamp': datetime.now().isoformat(),
        'lote_atual': resultado,
        'status_geral': status_final
    }
    
    cache_dir = 'cache'
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    
    with open(os.path.join(cache_dir, 'progresso_sincronizacao.json'), 'w') as f:
        json.dump(progresso, f, indent=2, default=str)
    
    return progresso

if __name__ == "__main__":
    main()