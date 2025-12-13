#!/usr/bin/env python3
"""
Script para upload da Legislação Tributária Brasileira no Qdrant
74 documentos com metadados detalhados (CF/88, CTN, LC 214/2025, etc.)
"""

import json
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from openai import OpenAI
from tqdm import tqdm
import time

# Configuração Qdrant
QDRANT_URL = "https://c21e6a5b-298d-483b-82f4-00aeff5edabe.us-east4-0.gcp.cloud.qdrant.io:6333"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.tr20ppnyxa1Zrz5cyaLAVyEvfMGBIeFbTvSKB4q25FE"
COLLECTION_NAME = "legislacao_tributaria_brasileira"

# Configuração OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client_openai = OpenAI(api_key=OPENAI_API_KEY)

# Inicializar cliente Qdrant
print("🔌 Conectando ao Qdrant Cloud...")
client_qdrant = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=120
)

# Verificar se collection existe
try:
    collections = client_qdrant.get_collections().collections
    collection_exists = any(c.name == COLLECTION_NAME for c in collections)
    
    if collection_exists:
        print(f"⚠️  Collection '{COLLECTION_NAME}' já existe. Deletando para recriar...")
        client_qdrant.delete_collection(collection_name=COLLECTION_NAME)
        time.sleep(2)
except Exception as e:
    print(f"⚠️  Aviso ao verificar collection: {e}")
    collection_exists = False

# Criar collection
print(f"🔨 Criando collection '{COLLECTION_NAME}'...")
client_qdrant.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(
        size=1536,  # text-embedding-3-small
        distance=Distance.COSINE
    )
)
print("✅ Collection criada com sucesso!")

# Carregar dados do JSON
print("\n📂 Carregando arquivo JSON...")
with open('attached_assets/Pasted--collection-name-legislacao-tributaria-brasileira-vectors-config-size-1536-1761709201228_1761709201229.txt', 'r', encoding='utf-8') as f:
    data = json.load(f)

documents = data['documents']
print(f"📊 Total de documentos: {len(documents)}")

# Processar e inserir documentos
print("\n🚀 Processando documentos e gerando embeddings...")
points = []
batch_size = 10

for i, doc in enumerate(tqdm(documents, desc="Gerando embeddings")):
    try:
        # Gerar embedding usando OpenAI text-embedding-3-small
        response = client_openai.embeddings.create(
            model="text-embedding-3-small",
            input=doc['text'],
            encoding_format="float"
        )
        vector = response.data[0].embedding
        
        # Criar ponto com ID único
        point_id = i + 1  # IDs numéricos sequenciais
        
        # Preparar payload (metadata + text)
        payload = {
            'text': doc['text'],
            'doc_id': doc['id'],  # ID original do documento
            **doc['metadata']
        }
        
        # Criar ponto
        point = PointStruct(
            id=point_id,
            vector=vector,
            payload=payload
        )
        points.append(point)
        
        # Upload em lotes
        if len(points) >= batch_size:
            client_qdrant.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )
            print(f"  ✓ Batch {(i+1)//batch_size} inserido ({len(points)} documentos)")
            points = []
        
        # Rate limiting (OpenAI)
        time.sleep(0.1)
        
    except Exception as e:
        print(f"❌ Erro no documento {i+1} (ID: {doc['id']}): {e}")
        continue

# Upload do último lote
if points:
    client_qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    print(f"  ✓ Último batch inserido ({len(points)} documentos)")

# Verificar collection
print("\n🔍 Verificando collection...")
collection_info = client_qdrant.get_collection(collection_name=COLLECTION_NAME)
print(f"✅ Upload completo!")
print(f"📊 Documentos na collection: {collection_info.points_count}")
print(f"📐 Dimensões dos vetores: {collection_info.config.params.vectors.size}")
print(f"📏 Distância: {collection_info.config.params.vectors.distance}")

# Teste de busca
print("\n🔎 Testando busca semântica...")
test_query = "Quais são os princípios constitucionais tributários?"
test_response = client_openai.embeddings.create(
    model="text-embedding-3-small",
    input=test_query,
    encoding_format="float"
)
test_vector = test_response.data[0].embedding

search_result = client_qdrant.search(
    collection_name=COLLECTION_NAME,
    query_vector=test_vector,
    limit=3
)

print(f"\nQuery: '{test_query}'")
print("\nTop 3 resultados:")
for idx, hit in enumerate(search_result, 1):
    print(f"\n{idx}. Score: {hit.score:.4f}")
    print(f"   ID: {hit.payload['doc_id']}")
    print(f"   Texto: {hit.payload['text'][:150]}...")
    if 'categoria' in hit.payload:
        print(f"   Categoria: {hit.payload['categoria']}")
    if 'artigos' in hit.payload:
        print(f"   Artigos: {hit.payload['artigos']}")

print("\n" + "="*80)
print("✅ PROCESSO CONCLUÍDO COM SUCESSO!")
print(f"📚 Collection: {COLLECTION_NAME}")
print(f"📊 Total documentos: {collection_info.points_count}")
print(f"🔗 URL: {QDRANT_URL}")
print("="*80)
