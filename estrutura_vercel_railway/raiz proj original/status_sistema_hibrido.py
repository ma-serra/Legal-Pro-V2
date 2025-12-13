#!/usr/bin/env python3
"""
Status Completo do Sistema Híbrido PostgreSQL + Qdrant
Verifica integridade e sincronização das 19 estruturas de dados
"""

import os
import psycopg2
import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def conectar_postgresql():
    """Conecta ao PostgreSQL"""
    return psycopg2.connect(os.environ['DATABASE_URL'])

def verificar_postgresql():
    """Verifica estrutura PostgreSQL"""
    
    conn = conectar_postgresql()
    cursor = conn.cursor()
    
    try:
        # Verificar base universal
        cursor.execute("""
            SELECT 
                COUNT(*) as total_chunks,
                COUNT(embedding_vetor) as com_embedding,
                COUNT(DISTINCT area_especializada) as areas_distintas
            FROM base_vetorial_universal
        """)
        
        universal = cursor.fetchone()
        
        # Verificar tabelas específicas
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public' 
            AND table_name LIKE 'embeddings_%'
            ORDER BY table_name
        """)
        
        tabelas_especificas = cursor.fetchall()
        
        # Contar registros em cada tabela
        registros_por_tabela = {}
        for (tabela,) in tabelas_especificas:
            cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            registros_por_tabela[tabela] = cursor.fetchone()[0]
        
        return {
            'universal': {
                'total_chunks': universal[0],
                'com_embedding': universal[1],
                'areas_distintas': universal[2]
            },
            'especificas': {
                'total_tabelas': len(tabelas_especificas),
                'registros': registros_por_tabela
            }
        }
        
    finally:
        cursor.close()
        conn.close()

def verificar_qdrant():
    """Verifica estrutura Qdrant"""
    
    qdrant_url = os.environ.get('QDRANT_URL')
    qdrant_key = os.environ.get('QDRANT_API_KEY')
    
    if not qdrant_url or not qdrant_key:
        return {'erro': 'Credenciais não configuradas'}
    
    headers = {
        'api-key': qdrant_key,
        'Content-Type': 'application/json'
    }
    
    try:
        # Listar collections
        response = requests.get(
            f"{qdrant_url}/collections",
            headers=headers,
            timeout=15
        )
        
        if response.status_code != 200:
            return {'erro': f'Erro na API: {response.status_code}'}
        
        data = response.json()
        collections = data.get('result', {}).get('collections', [])
        
        # Filtrar collections jurídicas
        collections_juridicas = [c for c in collections if c.get('name', '').startswith('juridico_')]
        
        # Verificar status de cada collection
        detalhes_collections = {}
        for collection in collections_juridicas:
            nome = collection.get('name')
            
            # Obter informações detalhadas
            info_response = requests.get(
                f"{qdrant_url}/collections/{nome}",
                headers=headers,
                timeout=10
            )
            
            if info_response.status_code == 200:
                info_data = info_response.json()
                result = info_data.get('result', {})
                
                detalhes_collections[nome] = {
                    'status': result.get('status', 'unknown'),
                    'vectors_count': result.get('vectors_count', 0),
                    'points_count': result.get('points_count', 0)
                }
        
        return {
            'total_collections': len(collections_juridicas),
            'collections': detalhes_collections,
            'status': 'ativo'
        }
        
    except Exception as e:
        return {'erro': str(e)}

def gerar_relatorio_completo():
    """Gera relatório completo do sistema híbrido"""
    
    logger.info("Verificando PostgreSQL...")
    pg_status = verificar_postgresql()
    
    logger.info("Verificando Qdrant Cloud...")
    qdrant_status = verificar_qdrant()
    
    # Relatório detalhado
    logger.info("="*70)
    logger.info("RELATÓRIO DO SISTEMA HÍBRIDO POSTGRESQL + QDRANT")
    logger.info("="*70)
    
    # PostgreSQL
    logger.info("POSTGRESQL:")
    logger.info(f"  Base Universal:")
    logger.info(f"    • Total de chunks: {pg_status['universal']['total_chunks']}")
    logger.info(f"    • Com embedding: {pg_status['universal']['com_embedding']}")
    logger.info(f"    • Áreas distintas: {pg_status['universal']['areas_distintas']}")
    
    logger.info(f"  Tabelas Específicas: {pg_status['especificas']['total_tabelas']}")
    for tabela, registros in pg_status['especificas']['registros'].items():
        area = tabela.replace('embeddings_', '').replace('_', ' ').title()
        logger.info(f"    • {area}: {registros} registros")
    
    # Qdrant
    logger.info("QDRANT CLOUD:")
    if 'erro' in qdrant_status:
        logger.info(f"  ❌ Erro: {qdrant_status['erro']}")
    else:
        logger.info(f"  Collections: {qdrant_status['total_collections']}")
        for nome, info in qdrant_status['collections'].items():
            area = nome.replace('juridico_', '').replace('_', ' ').title()
            logger.info(f"    • {area}: {info['points_count']} pontos, status {info['status']}")
    
    # Análise de sincronização
    logger.info("ANÁLISE DE SINCRONIZAÇÃO:")
    if 'erro' not in qdrant_status:
        pg_tabelas = pg_status['especificas']['total_tabelas'] + 1  # +1 para base universal
        qdrant_collections = qdrant_status['total_collections']
        
        if pg_tabelas == qdrant_collections:
            logger.info("  ✅ Estruturas sincronizadas")
        else:
            logger.info(f"  ⚠️  Divergência: {pg_tabelas} tabelas PG vs {qdrant_collections} collections Qdrant")
        
        # Calcular taxa de preenchimento
        total_embeddings = pg_status['universal']['com_embedding']
        total_chunks = pg_status['universal']['total_chunks']
        taxa_embedding = (total_embeddings / total_chunks * 100) if total_chunks > 0 else 0
        
        logger.info(f"  Taxa de embeddings: {taxa_embedding:.1f}%")
        
        # Score geral
        score_estrutura = 50 if pg_tabelas == qdrant_collections else 25
        score_embeddings = int(taxa_embedding * 0.5)
        score_total = score_estrutura + score_embeddings
        
        logger.info(f"  Score do sistema: {score_total}/100")
    
    # Salvar relatório
    relatorio = {
        'timestamp': '2025-06-16T00:35:00Z',
        'postgresql': pg_status,
        'qdrant': qdrant_status,
        'sincronizacao': {
            'estruturas_alinhadas': pg_status['especificas']['total_tabelas'] + 1 == qdrant_status.get('total_collections', 0),
            'taxa_embeddings': (pg_status['universal']['com_embedding'] / pg_status['universal']['total_chunks'] * 100) if pg_status['universal']['total_chunks'] > 0 else 0
        }
    }
    
    cache_dir = 'cache'
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    
    with open(os.path.join(cache_dir, 'status_sistema_hibrido.json'), 'w') as f:
        json.dump(relatorio, f, indent=2, default=str)
    
    return relatorio

def main():
    """Função principal"""
    logger.info("Iniciando verificação do sistema híbrido")
    relatorio = gerar_relatorio_completo()
    logger.info("Relatório salvo em cache/status_sistema_hibrido.json")

if __name__ == "__main__":
    main()