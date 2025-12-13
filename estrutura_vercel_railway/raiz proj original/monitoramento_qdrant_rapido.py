#!/usr/bin/env python3
"""
Monitoramento Qdrant Rápido - Versão otimizada para execução veloz
"""

import os
import psycopg2
import requests
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def conectar_postgresql():
    """Conecta ao PostgreSQL"""
    return psycopg2.connect(os.environ['DATABASE_URL'])

def verificar_qdrant_basico():
    """Verificação básica do Qdrant"""
    try:
        qdrant_url = os.environ.get('QDRANT_URL')
        qdrant_key = os.environ.get('QDRANT_API_KEY')
        
        if not qdrant_url or not qdrant_key:
            return {'status': 'não_configurado', 'collections': 0, 'vectors': 0}
        
        headers = {'api-key': qdrant_key}
        response = requests.get(f"{qdrant_url}/collections", headers=headers, timeout=5)
        
        if response.status_code == 200:
            collections = response.json().get('result', {}).get('collections', [])
            return {
                'status': 'ativo',
                'collections': len(collections),
                'vectors': sum(c.get('vectors_count', 0) for c in collections)
            }
        else:
            return {'status': 'erro', 'collections': 0, 'vectors': 0}
            
    except Exception as e:
        logger.error(f"Erro Qdrant: {e}")
        return {'status': 'erro', 'collections': 0, 'vectors': 0}

def coletar_stats_postgresql():
    """Coleta estatísticas rápidas do PostgreSQL"""
    conn = conectar_postgresql()
    cursor = conn.cursor()
    
    try:
        stats = {}
        
        # Base universal
        cursor.execute("SELECT COUNT(*) FROM base_vetorial_universal")
        stats['chunks_universal'] = cursor.fetchone()[0]
        
        # Documentos mestres
        cursor.execute("SELECT COUNT(*) FROM documentos_mestres")
        stats['documentos_mestres'] = cursor.fetchone()[0]
        
        # Agentes ativos
        cursor.execute("SELECT COUNT(*) FROM agente_juridico")
        stats['agentes_total'] = cursor.fetchone()[0]
        
        # Áreas com mais chunks
        cursor.execute("""
            SELECT area_especializada, COUNT(*) 
            FROM base_vetorial_universal 
            WHERE area_especializada IS NOT NULL
            GROUP BY area_especializada
            ORDER BY COUNT(*) DESC
            LIMIT 5
        """)
        stats['top_areas'] = dict(cursor.fetchall())
        
        return stats
        
    except Exception as e:
        logger.error(f"Erro PostgreSQL: {e}")
        return {}
    finally:
        cursor.close()
        conn.close()

def executar_monitoramento_rapido():
    """Executa monitoramento rápido"""
    logger.info("Iniciando monitoramento rápido Qdrant")
    
    # Coletar dados
    qdrant_stats = verificar_qdrant_basico()
    pg_stats = coletar_stats_postgresql()
    
    # Calcular sincronização
    pg_chunks = pg_stats.get('chunks_universal', 0)
    qdrant_vectors = qdrant_stats.get('vectors', 0)
    
    if pg_chunks > 0:
        sync_percent = min(100, (qdrant_vectors / pg_chunks) * 100)
    else:
        sync_percent = 0
    
    # Score de saúde
    score = 0
    if pg_chunks > 0:
        score += 40
    if qdrant_stats['status'] == 'ativo':
        score += 30
    if sync_percent > 80:
        score += 30
    
    relatorio = {
        'timestamp': datetime.now().isoformat(),
        'score_saude': score,
        'status_geral': 'bom' if score >= 70 else 'atencao' if score >= 40 else 'critico',
        'postgresql': {
            'chunks_universal': pg_chunks,
            'documentos_mestres': pg_stats.get('documentos_mestres', 0),
            'agentes_total': pg_stats.get('agentes_total', 0),
            'top_areas': pg_stats.get('top_areas', {})
        },
        'qdrant': qdrant_stats,
        'sincronizacao': {
            'percentual': round(sync_percent, 1),
            'diferenca': abs(pg_chunks - qdrant_vectors)
        }
    }
    
    # Salvar cache
    cache_dir = 'cache'
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    
    with open(os.path.join(cache_dir, 'monitoramento_qdrant_rapido.json'), 'w') as f:
        json.dump(relatorio, f, indent=2, default=str)
    
    logger.info(f"Monitoramento concluído - Score: {score}/100")
    print(f"Score de Saúde: {score}/100")
    print(f"Status: {relatorio['status_geral']}")
    print(f"PostgreSQL: {pg_chunks} chunks")
    print(f"Qdrant: {qdrant_stats['status']} - {qdrant_vectors} vectors")
    print(f"Sincronização: {sync_percent:.1f}%")
    
    return relatorio

if __name__ == "__main__":
    executar_monitoramento_rapido()