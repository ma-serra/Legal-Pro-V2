#!/usr/bin/env python3
"""
Sincronização da Estrutura Híbrida
Cria collections Qdrant correspondentes às 19 tabelas PostgreSQL
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

def criar_collections_qdrant():
    """Cria collections Qdrant correspondentes às tabelas PostgreSQL"""
    
    qdrant_url = os.environ.get('QDRANT_URL')
    qdrant_key = os.environ.get('QDRANT_API_KEY')
    
    if not qdrant_url or not qdrant_key:
        logger.error("Credenciais Qdrant não configuradas")
        return
    
    headers = {
        'api-key': qdrant_key,
        'Content-Type': 'application/json'
    }
    
    # Collections correspondentes às tabelas PostgreSQL
    collections = [
        'juridico_base_universal',
        'juridico_direito_administrativo',
        'juridico_direito_agrario', 
        'juridico_direito_ambiental',
        'juridico_direito_civil',
        'juridico_direito_constitucional',
        'juridico_direito_consumidor',
        'juridico_direito_digital',
        'juridico_direito_empresarial',
        'juridico_direito_familia',
        'juridico_direito_imobiliario',
        'juridico_direito_penal',
        'juridico_direito_previdenciario',
        'juridico_direito_sucessorio',
        'juridico_direito_trabalhista',
        'juridico_direito_tributario',
        'juridico_analise_riscos',
        'juridico_conflitos_mediacao',
        'juridico_seguros'
    ]
    
    criadas = 0
    existentes = 0
    
    for collection_name in collections:
        try:
            # Verificar se collection existe
            response = requests.get(
                f"{qdrant_url}/collections/{collection_name}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                existentes += 1
                logger.info(f"Collection já existe: {collection_name}")
                continue
            
            # Criar collection
            collection_config = {
                "vectors": {
                    "size": 1536,  # OpenAI text-embedding-3-small
                    "distance": "Cosine"
                },
                "optimizers_config": {
                    "default_segment_number": 2
                },
                "replication_factor": 1
            }
            
            create_response = requests.put(
                f"{qdrant_url}/collections/{collection_name}",
                headers=headers,
                json=collection_config,
                timeout=30
            )
            
            if create_response.status_code in [200, 201]:
                criadas += 1
                logger.info(f"✅ Collection criada: {collection_name}")
            else:
                logger.error(f"❌ Erro ao criar {collection_name}: {create_response.text}")
                
        except Exception as e:
            logger.error(f"Erro ao criar collection {collection_name}: {e}")
    
    logger.info(f"Collections Qdrant: {criadas} criadas, {existentes} já existiam")
    return criadas + existentes

def popular_base_universal():
    """Popula a base universal com dados existentes"""
    
    conn = conectar_postgresql()
    cursor = conn.cursor()
    
    qdrant_url = os.environ.get('QDRANT_URL')
    qdrant_key = os.environ.get('QDRANT_API_KEY')
    
    headers = {
        'api-key': qdrant_key,
        'Content-Type': 'application/json'
    }
    
    try:
        # Buscar chunks da base universal que já possuem embedding
        cursor.execute("""
            SELECT chunk_id, titulo, conteudo, area_especializada,
                   documento_pai_id, chunk_numero, is_chunk_filho,
                   embedding_vetor
            FROM base_vetorial_universal
            WHERE embedding_vetor IS NOT NULL
            ORDER BY created_at DESC
            LIMIT 50
        """)
        
        chunks = cursor.fetchall()
        logger.info(f"Sincronizando {len(chunks)} chunks para Qdrant")
        
        sucesso = 0
        erro = 0
        
        for chunk in chunks:
            try:
                chunk_id, titulo, conteudo, area, documento_pai_id, chunk_numero, is_filho, embedding_json = chunk
                
                if not embedding_json:
                    continue
                
                embedding = json.loads(embedding_json)
                
                # Upload para collection universal
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
                
                response = requests.put(
                    f"{qdrant_url}/collections/juridico_base_universal/points",
                    headers=headers,
                    json=payload,
                    timeout=20
                )
                
                if response.status_code in [200, 201]:
                    sucesso += 1
                else:
                    erro += 1
                    
            except Exception as e:
                erro += 1
                logger.error(f"Erro no chunk {chunk_id}: {e}")
        
        logger.info(f"Base universal sincronizada: {sucesso} sucessos, {erro} erros")
        return sucesso
        
    finally:
        cursor.close()
        conn.close()

def verificar_status_hibrido():
    """Verifica status do sistema híbrido"""
    
    # PostgreSQL
    conn = conectar_postgresql()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                COUNT(*) as total_universal,
                COUNT(embedding_vetor) as com_embedding
            FROM base_vetorial_universal
        """)
        
        universal_total, universal_embedding = cursor.fetchone()
        
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public' 
            AND table_name LIKE 'embeddings_%'
            ORDER BY table_name
        """)
        
        tabelas_especificas = cursor.fetchall()
        
    finally:
        cursor.close()
        conn.close()
    
    # Qdrant
    qdrant_url = os.environ.get('QDRANT_URL')
    qdrant_key = os.environ.get('QDRANT_API_KEY')
    
    headers = {
        'api-key': qdrant_key,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            f"{qdrant_url}/collections",
            headers=headers,
            timeout=10
        )
        
        collections_qdrant = 0
        if response.status_code == 200:
            data = response.json()
            collections = data.get('result', {}).get('collections', [])
            collections_qdrant = len([c for c in collections if c.get('name', '').startswith('juridico_')])
    
    except Exception as e:
        logger.error(f"Erro ao verificar Qdrant: {e}")
        collections_qdrant = 0
    
    # Relatório
    logger.info("="*60)
    logger.info("STATUS DO SISTEMA HÍBRIDO")
    logger.info("="*60)
    logger.info(f"PostgreSQL:")
    logger.info(f"  - Base universal: {universal_total} chunks ({universal_embedding} com embedding)")
    logger.info(f"  - Tabelas específicas: {len(tabelas_especificas)}")
    logger.info(f"Qdrant Cloud:")
    logger.info(f"  - Collections jurídicas: {collections_qdrant}")
    
    return {
        'postgresql_universal': universal_total,
        'postgresql_especificas': len(tabelas_especificas),
        'qdrant_collections': collections_qdrant
    }

def main():
    """Função principal"""
    logger.info("🔄 Sincronizando estrutura híbrida PostgreSQL + Qdrant")
    
    # Criar collections Qdrant
    total_collections = criar_collections_qdrant()
    
    # Popular base universal
    chunks_sincronizados = popular_base_universal()
    
    # Verificar status final
    status = verificar_status_hibrido()
    
    logger.info("✅ Sincronização da estrutura híbrida concluída")
    logger.info(f"📊 {total_collections} collections Qdrant, {chunks_sincronizados} chunks sincronizados")

if __name__ == "__main__":
    main()