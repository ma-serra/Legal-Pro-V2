#!/usr/bin/env python3
"""
Verificação rápida da conexão das 19 bases vetoriais
"""

import os
import psycopg2
import json
from qdrant_client import QdrantClient

def verificar_postgresql():
    """Verifica configuração dos agentes no PostgreSQL"""
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    cursor = conn.cursor()
    
    try:
        # Contar agentes com configuração vetorial
        cursor.execute("""
            SELECT 
                collection_qdrant,
                COUNT(*) as total_agentes
            FROM agente_juridico 
            WHERE ativo = true AND collection_qdrant IS NOT NULL
            GROUP BY collection_qdrant
            ORDER BY collection_qdrant
        """)
        
        results = cursor.fetchall()
        agentes_por_collection = dict(results)
        
        # Total de agentes configurados
        cursor.execute("""
            SELECT COUNT(*) FROM agente_juridico 
            WHERE ativo = true AND collection_qdrant IS NOT NULL
        """)
        total_configurados = cursor.fetchone()[0]
        
        return {
            'agentes_por_collection': agentes_por_collection,
            'total_configurados': total_configurados
        }
        
    finally:
        cursor.close()
        conn.close()

def verificar_qdrant():
    """Verifica status das coleções no Qdrant"""
    try:
        qdrant_url = os.environ.get('QDRANT_URL')
        qdrant_api_key = os.environ.get('QDRANT_API_KEY')
        
        if not qdrant_url or not qdrant_api_key:
            return {'erro': 'Credenciais Qdrant não configuradas'}
        
        client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        collections = client.get_collections()
        
        status_collections = {}
        for collection in collections.collections:
            try:
                info = client.get_collection(collection.name)
                status_collections[collection.name] = {
                    'status': 'ativa',
                    'points_count': info.points_count if hasattr(info, 'points_count') else 0
                }
            except Exception as e:
                status_collections[collection.name] = {
                    'status': 'erro',
                    'erro': str(e)
                }
        
        return {
            'total_collections': len(collections.collections),
            'collections': status_collections
        }
        
    except Exception as e:
        return {'erro': str(e)}

def main():
    print("🔍 Verificando conexão das 19 bases vetoriais...")
    
    # PostgreSQL
    print("\n📊 Status PostgreSQL:")
    pg_status = verificar_postgresql()
    print(f"   • Agentes configurados: {pg_status['total_configurados']}")
    print(f"   • Collections mapeadas: {len(pg_status['agentes_por_collection'])}")
    
    for collection, count in pg_status['agentes_por_collection'].items():
        print(f"     - {collection}: {count} agentes")
    
    # Qdrant
    print("\n🌐 Status Qdrant:")
    qdrant_status = verificar_qdrant()
    
    if 'erro' in qdrant_status:
        print(f"   ❌ Erro: {qdrant_status['erro']}")
    else:
        print(f"   • Total de coleções: {qdrant_status['total_collections']}")
        print(f"   • Coleções ativas: {len([c for c in qdrant_status['collections'].values() if c['status'] == 'ativa'])}")
        
        for name, info in qdrant_status['collections'].items():
            if info['status'] == 'ativa':
                print(f"     - {name}: {info.get('points_count', 0)} documentos")
            else:
                print(f"     - {name}: {info['status']}")
    
    # Resumo
    print("\n📈 RESUMO:")
    print(f"   ✅ Agentes configurados: {pg_status['total_configurados']}")
    print(f"   ✅ Collections PostgreSQL: {len(pg_status['agentes_por_collection'])}")
    
    if 'erro' not in qdrant_status:
        collections_ativas = len([c for c in qdrant_status['collections'].values() if c['status'] == 'ativa'])
        print(f"   ✅ Collections Qdrant ativas: {collections_ativas}")
        
        if collections_ativas >= 19 and pg_status['total_configurados'] > 0:
            print("\n🎉 SUCESSO: Todas as 19 bases vetoriais estão conectadas!")
        else:
            print("\n⚠️ PENDENTE: Conexão ainda em progresso...")
    else:
        print(f"   ❌ Qdrant: {qdrant_status['erro']}")

if __name__ == "__main__":
    main()