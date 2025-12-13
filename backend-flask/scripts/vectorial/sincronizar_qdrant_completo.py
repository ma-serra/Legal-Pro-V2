#!/usr/bin/env python3
"""
Sincronização Completa PostgreSQL -> Qdrant Cloud
Migra todos os chunks da base_vetorial_universal para Qdrant Cloud
"""

import os
import psycopg2
import requests
import json
import logging
import uuid
from datetime import datetime
from tqdm import tqdm
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
            return  # Collection já existe
        
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
            logger.info(f"Collection criada: {collection_name}")
        else:
            logger.error(f"Erro ao criar collection: {create_response.text}")
            
    except Exception as e:
        logger.error(f"Erro ao verificar/criar collection: {e}")

def upload_chunk_para_qdrant(chunk_data, headers):
    """Faz upload de um chunk para Qdrant"""
    try:
        qdrant_url = os.environ.get('QDRANT_URL')
        chunk_id, titulo, conteudo, area, documento_pai_id, chunk_numero, is_filho, embedding_json = chunk_data
        
        # Verificar se já tem embedding
        if not embedding_json:
            logger.info(f"Gerando embedding para chunk {chunk_id}")
            embedding = gerar_embedding(conteudo)
            if not embedding:
                return False, f"Falha ao gerar embedding para {chunk_id}"
            
            # Salvar embedding no PostgreSQL
            conn = conectar_postgresql()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "UPDATE base_vetorial_universal SET embedding_vetor = %s WHERE chunk_id = %s",
                    (json.dumps(embedding), chunk_id)
                )
                conn.commit()
            except Exception as e:
                logger.error(f"Erro ao salvar embedding no PostgreSQL: {e}")
            finally:
                cursor.close()
                conn.close()
        else:
            embedding = json.loads(embedding_json)
        
        # Nome da collection baseado na área
        area_clean = area.replace(' ', '_').replace('-', '_').lower() if area else 'geral'
        collection_name = f"juridico_{area_clean}"
        
        # Verificar/criar collection
        garantir_collection_existe(collection_name, headers)
        
        # Gerar UUID válido para Qdrant
        qdrant_id = str(uuid.uuid4())
        
        # Preparar payload
        payload = {
            "points": [{
                "id": qdrant_id,
                "vector": embedding,
                "payload": {
                    "chunk_id": chunk_id,
                    "titulo": titulo,
                    "area_especializada": area,
                    "documento_pai_id": documento_pai_id,
                    "chunk_numero": chunk_numero,
                    "is_chunk_filho": is_filho,
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
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            return True, f"Upload bem-sucedido: {chunk_id}"
        else:
            return False, f"Erro no upload: {response.status_code} - {response.text}"
            
    except Exception as e:
        return False, f"Erro ao fazer upload: {e}"

def sincronizar_postgresql_qdrant():
    """Sincroniza todos os chunks do PostgreSQL para Qdrant"""
    
    # Verificar credenciais
    qdrant_url = os.environ.get('QDRANT_URL')
    qdrant_key = os.environ.get('QDRANT_API_KEY')
    
    if not qdrant_url or not qdrant_key:
        logger.error("Credenciais Qdrant não configuradas")
        return
    
    headers = {
        'api-key': qdrant_key,
        'Content-Type': 'application/json'
    }
    
    # Conectar ao PostgreSQL
    conn = conectar_postgresql()
    cursor = conn.cursor()
    
    try:
        # Buscar todos os chunks
        cursor.execute("""
            SELECT chunk_id, titulo, conteudo, area_especializada, 
                   documento_pai_id, chunk_numero, is_chunk_filho,
                   embedding_vetor
            FROM base_vetorial_universal
            ORDER BY created_at DESC
        """)
        
        chunks = cursor.fetchall()
        logger.info(f"Encontrados {len(chunks)} chunks para sincronizar")
        
        # Contadores
        sucesso = 0
        erro = 0
        pular = 0
        
        # Progress bar
        for chunk in tqdm(chunks, desc="Sincronizando chunks"):
            try:
                # Verificar se conteúdo existe
                if not chunk[2] or len(chunk[2].strip()) < 10:
                    pular += 1
                    continue
                
                # Upload para Qdrant
                resultado, mensagem = upload_chunk_para_qdrant(chunk, headers)
                
                if resultado:
                    sucesso += 1
                else:
                    erro += 1
                    logger.error(f"Erro no chunk {chunk[0]}: {mensagem}")
                
                # Pausa para evitar rate limiting
                if (sucesso + erro) % 10 == 0:
                    import time
                    time.sleep(1)
                    
            except Exception as e:
                erro += 1
                logger.error(f"Erro geral no chunk {chunk[0]}: {e}")
        
        # Relatório final
        logger.info("="*50)
        logger.info("RELATÓRIO DE SINCRONIZAÇÃO")
        logger.info("="*50)
        logger.info(f"Total de chunks: {len(chunks)}")
        logger.info(f"Sincronizados com sucesso: {sucesso}")
        logger.info(f"Erros: {erro}")
        logger.info(f"Pulados (conteúdo inválido): {pular}")
        logger.info(f"Taxa de sucesso: {(sucesso/(len(chunks)-pular)*100):.1f}%")
        
        # Salvar relatório
        relatorio = {
            'timestamp': datetime.now().isoformat(),
            'total_chunks': len(chunks),
            'sincronizados': sucesso,
            'erros': erro,
            'pulados': pular,
            'taxa_sucesso': (sucesso/(len(chunks)-pular)*100) if (len(chunks)-pular) > 0 else 0
        }
        
        cache_dir = 'cache'
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        
        with open(os.path.join(cache_dir, 'sincronizacao_qdrant.json'), 'w') as f:
            json.dump(relatorio, f, indent=2, default=str)
        
        return relatorio
        
    except Exception as e:
        logger.error(f"Erro na sincronização: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def verificar_status_pos_sincronizacao():
    """Verifica status após sincronização"""
    try:
        # Executar monitoramento
        import subprocess
        resultado = subprocess.run(
            ['python', 'monitoramento_qdrant_rapido.py'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if resultado.returncode == 0:
            logger.info("Status pós-sincronização:")
            print(resultado.stdout)
        else:
            logger.error("Erro ao verificar status")
            
    except Exception as e:
        logger.error(f"Erro ao verificar status: {e}")

def main():
    """Função principal"""
    logger.info("🚀 Iniciando sincronização completa PostgreSQL -> Qdrant Cloud")
    
    # Sincronizar
    relatorio = sincronizar_postgresql_qdrant()
    
    if relatorio:
        print(f"\n✅ Sincronização concluída!")
        print(f"📊 {relatorio['sincronizados']}/{relatorio['total_chunks']} chunks sincronizados")
        print(f"📈 Taxa de sucesso: {relatorio['taxa_sucesso']:.1f}%")
        
        # Verificar status
        print("\n🔍 Verificando status...")
        verificar_status_pos_sincronizacao()
    else:
        print("\n❌ Erro na sincronização")

if __name__ == "__main__":
    main()