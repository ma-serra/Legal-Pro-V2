#!/usr/bin/env python3
"""
Sistema de Monitoramento Qdrant Integrado
Monitora a nova estrutura vetorial híbrida PostgreSQL + Qdrant Cloud
"""

import os
import psycopg2
import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class QdrantStats:
    collections_total: int
    vectors_total: int
    storage_size_mb: float
    status: str
    uptime: str

@dataclass
class PostgreSQLStats:
    base_universal_chunks: int
    documentos_mestres: int
    agentes_ativos: int
    templates_total: int
    usuarios_ativos: int

class MonitoramentoQdrantIntegrado:
    def __init__(self):
        self.db_url = os.environ['DATABASE_URL']
        self.qdrant_url = os.environ.get('QDRANT_URL')
        self.qdrant_key = os.environ.get('QDRANT_API_KEY')
        self.dados_monitoramento = {}
    
    def conectar_postgresql(self):
        """Conecta ao PostgreSQL"""
        return psycopg2.connect(self.db_url)
    
    def verificar_qdrant_status(self) -> QdrantStats:
        """Verifica status do Qdrant Cloud"""
        try:
            if not self.qdrant_url or not self.qdrant_key:
                return QdrantStats(0, 0, 0.0, "não_configurado", "0h")
            
            headers = {'api-key': self.qdrant_key}
            
            # Status geral
            response = requests.get(f"{self.qdrant_url}/", headers=headers, timeout=10)
            if response.status_code != 200:
                return QdrantStats(0, 0, 0.0, "erro_conexao", "0h")
            
            # Collections
            collections_response = requests.get(f"{self.qdrant_url}/collections", headers=headers, timeout=10)
            collections = collections_response.json().get('result', {}).get('collections', [])
            
            # Estatísticas detalhadas
            vectors_total = 0
            storage_size = 0.0
            
            for collection in collections:
                collection_name = collection.get('name', '')
                if collection_name:
                    # Info da collection
                    info_response = requests.get(
                        f"{self.qdrant_url}/collections/{collection_name}", 
                        headers=headers, timeout=10
                    )
                    
                    if info_response.status_code == 200:
                        info = info_response.json().get('result', {})
                        vectors_total += info.get('vectors_count', 0)
                        storage_size += info.get('points_count', 0) * 1536 * 4 / (1024 * 1024)  # Estimativa em MB
            
            return QdrantStats(
                collections_total=len(collections),
                vectors_total=vectors_total,
                storage_size_mb=round(storage_size, 2),
                status="ativo",
                uptime="operational"
            )
            
        except Exception as e:
            logger.error(f"Erro ao verificar Qdrant: {e}")
            return QdrantStats(0, 0, 0.0, "erro", "0h")
    
    def verificar_postgresql_stats(self) -> PostgreSQLStats:
        """Verifica estatísticas do PostgreSQL"""
        conn = self.conectar_postgresql()
        cursor = conn.cursor()
        
        try:
            # Base universal
            cursor.execute("SELECT COUNT(*) FROM base_vetorial_universal")
            chunks_universal = cursor.fetchone()[0]
            
            # Documentos mestres
            cursor.execute("SELECT COUNT(*) FROM documentos_mestres")
            documentos_mestres = cursor.fetchone()[0]
            
            # Agentes ativos
            cursor.execute("SELECT COUNT(*) FROM agente_juridico WHERE ativo = true")
            agentes_ativos = cursor.fetchone()[0]
            
            # Templates
            cursor.execute("SELECT COUNT(*) FROM template_juridico")
            templates_total = cursor.fetchone()[0]
            
            # Usuários ativos
            cursor.execute("SELECT COUNT(*) FROM \"user\"")
            usuarios_ativos = cursor.fetchone()[0]
            
            return PostgreSQLStats(
                base_universal_chunks=chunks_universal,
                documentos_mestres=documentos_mestres,
                agentes_ativos=agentes_ativos,
                templates_total=templates_total,
                usuarios_ativos=usuarios_ativos
            )
            
        except Exception as e:
            logger.error(f"Erro ao verificar PostgreSQL: {e}")
            return PostgreSQLStats(0, 0, 0, 0, 0)
        finally:
            cursor.close()
            conn.close()
    
    def analisar_distribuicao_areas(self) -> Dict[str, int]:
        """Analisa distribuição de documentos por área jurídica"""
        conn = self.conectar_postgresql()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT area_especializada, COUNT(*) 
                FROM base_vetorial_universal 
                WHERE area_especializada IS NOT NULL
                GROUP BY area_especializada
                ORDER BY COUNT(*) DESC
            """)
            
            return dict(cursor.fetchall())
            
        except Exception as e:
            logger.error(f"Erro ao analisar distribuição: {e}")
            return {}
        finally:
            cursor.close()
            conn.close()
    
    def verificar_integridade_hierarquia(self) -> Dict[str, Any]:
        """Verifica integridade da hierarquia pai-filhos"""
        conn = self.conectar_postgresql()
        cursor = conn.cursor()
        
        try:
            # Verificar documentos mestres vs chunks
            cursor.execute("""
                SELECT 
                    dm.nome_completo,
                    dm.documento_id,
                    COUNT(buv.chunk_id) as chunks_vinculados
                FROM documentos_mestres dm
                LEFT JOIN base_vetorial_universal buv ON dm.documento_id = buv.documento_pai_id
                GROUP BY dm.documento_id, dm.nome_completo
                ORDER BY COUNT(buv.chunk_id) DESC
            """)
            
            hierarquia = cursor.fetchall()
            
            # Verificar chunks órfãos
            cursor.execute("""
                SELECT COUNT(*) FROM base_vetorial_universal 
                WHERE documento_pai_id IS NULL OR documento_pai_id = ''
            """)
            
            chunks_orfaos = cursor.fetchone()[0]
            
            # Verificar consistência de IDs
            cursor.execute("""
                SELECT COUNT(*) FROM base_vetorial_universal buv
                LEFT JOIN documentos_mestres dm ON buv.documento_pai_id = dm.documento_id
                WHERE dm.documento_id IS NULL AND buv.documento_pai_id IS NOT NULL
            """)
            
            ids_inconsistentes = cursor.fetchone()[0]
            
            return {
                'hierarquia_documentos': [
                    {'nome': h[0], 'id': h[1], 'chunks': h[2]} 
                    for h in hierarquia
                ],
                'chunks_orfaos': chunks_orfaos,
                'ids_inconsistentes': ids_inconsistentes,
                'integridade_ok': chunks_orfaos == 0 and ids_inconsistentes == 0
            }
            
        except Exception as e:
            logger.error(f"Erro ao verificar integridade: {e}")
            return {'integridade_ok': False, 'erro': str(e)}
        finally:
            cursor.close()
            conn.close()
    
    def analisar_performance_busca(self) -> Dict[str, Any]:
        """Analisa performance das buscas vetoriais"""
        conn = self.conectar_postgresql()
        cursor = conn.cursor()
        
        try:
            # Tamanho médio dos chunks
            cursor.execute("""
                SELECT 
                    AVG(LENGTH(conteudo)) as tamanho_medio,
                    MIN(LENGTH(conteudo)) as tamanho_min,
                    MAX(LENGTH(conteudo)) as tamanho_max,
                    COUNT(*) as total_chunks
                FROM base_vetorial_universal
                WHERE conteudo IS NOT NULL
            """)
            
            stats_tamanho = cursor.fetchone()
            
            # Distribuição por tipo de chunk
            cursor.execute("""
                SELECT 
                    is_chunk_filho,
                    COUNT(*) as quantidade,
                    AVG(LENGTH(conteudo)) as tamanho_medio
                FROM base_vetorial_universal
                WHERE conteudo IS NOT NULL
                GROUP BY is_chunk_filho
            """)
            
            distribuicao_tipo = cursor.fetchall()
            
            # Verificar índices vetoriais (se existirem)
            cursor.execute("""
                SELECT indexname, indexdef 
                FROM pg_indexes 
                WHERE tablename = 'base_vetorial_universal'
                AND indexdef LIKE '%vector%'
            """)
            
            indices_vetoriais = cursor.fetchall()
            
            return {
                'tamanho_medio_chars': round(stats_tamanho[0] or 0, 2),
                'tamanho_min_chars': stats_tamanho[1] or 0,
                'tamanho_max_chars': stats_tamanho[2] or 0,
                'total_chunks': stats_tamanho[3] or 0,
                'distribuicao_tipo': [
                    {
                        'tipo': 'chunk_filho' if d[0] else 'documento_pai',
                        'quantidade': d[1],
                        'tamanho_medio': round(d[2] or 0, 2)
                    } for d in distribuicao_tipo
                ],
                'indices_vetoriais': len(indices_vetoriais),
                'performance_estimada': 'otima' if len(indices_vetoriais) > 0 else 'boa'
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar performance: {e}")
            return {'performance_estimada': 'erro', 'erro': str(e)}
        finally:
            cursor.close()
            conn.close()
    
    def verificar_sincronizacao_qdrant(self) -> Dict[str, Any]:
        """Verifica sincronização entre PostgreSQL e Qdrant"""
        try:
            # Stats PostgreSQL
            pg_stats = self.verificar_postgresql_stats()
            
            # Stats Qdrant
            qdrant_stats = self.verificar_qdrant_status()
            
            # Análise de sincronização
            diferenca_vetores = abs(pg_stats.base_universal_chunks - qdrant_stats.vectors_total)
            percentual_sincronizacao = 100 - (diferenca_vetores / max(pg_stats.base_universal_chunks, 1) * 100)
            
            status_sync = "perfeita" if diferenca_vetores == 0 else \
                         "boa" if diferenca_vetores < 10 else \
                         "atencao" if diferenca_vetores < 50 else "critica"
            
            return {
                'postgresql_chunks': pg_stats.base_universal_chunks,
                'qdrant_vectors': qdrant_stats.vectors_total,
                'diferenca': diferenca_vetores,
                'percentual_sincronizacao': round(percentual_sincronizacao, 2),
                'status_sincronizacao': status_sync,
                'qdrant_collections': qdrant_stats.collections_total,
                'qdrant_storage_mb': qdrant_stats.storage_size_mb,
                'qdrant_status': qdrant_stats.status
            }
            
        except Exception as e:
            logger.error(f"Erro ao verificar sincronização: {e}")
            return {'status_sincronizacao': 'erro', 'erro': str(e)}
    
    def gerar_relatorio_completo(self) -> Dict[str, Any]:
        """Gera relatório completo do monitoramento"""
        try:
            # Coletar todas as métricas
            pg_stats = self.verificar_postgresql_stats()
            qdrant_stats = self.verificar_qdrant_status()
            distribuicao_areas = self.analisar_distribuicao_areas()
            integridade = self.verificar_integridade_hierarquia()
            performance = self.analisar_performance_busca()
            sincronizacao = self.verificar_sincronizacao_qdrant()
            
            # Calcular score geral de saúde
            scores = []
            
            # Score PostgreSQL (0-25)
            if pg_stats.base_universal_chunks > 0:
                scores.append(25)
            else:
                scores.append(0)
            
            # Score Qdrant (0-25)
            if qdrant_stats.status == "ativo":
                scores.append(25)
            elif qdrant_stats.status == "não_configurado":
                scores.append(15)
            else:
                scores.append(0)
            
            # Score Integridade (0-25)
            if integridade.get('integridade_ok', False):
                scores.append(25)
            else:
                scores.append(10)
            
            # Score Sincronização (0-25)
            sync_score = sincronizacao.get('percentual_sincronizacao', 0) / 4
            scores.append(min(25, sync_score))
            
            score_geral = sum(scores)
            
            relatorio = {
                'timestamp': datetime.now().isoformat(),
                'score_geral': round(score_geral, 1),
                'status_geral': 'excelente' if score_geral >= 90 else 
                               'bom' if score_geral >= 70 else 
                               'atencao' if score_geral >= 50 else 'critico',
                'postgresql': {
                    'chunks_universal': pg_stats.base_universal_chunks,
                    'documentos_mestres': pg_stats.documentos_mestres,
                    'agentes_ativos': pg_stats.agentes_ativos,
                    'templates_total': pg_stats.templates_total,
                    'usuarios_ativos': pg_stats.usuarios_ativos
                },
                'qdrant': {
                    'status': qdrant_stats.status,
                    'collections': qdrant_stats.collections_total,
                    'vectors': qdrant_stats.vectors_total,
                    'storage_mb': qdrant_stats.storage_size_mb,
                    'uptime': qdrant_stats.uptime
                },
                'distribuicao_areas': distribuicao_areas,
                'integridade': integridade,
                'performance': performance,
                'sincronizacao': sincronizacao
            }
            
            # Salvar relatório
            self.salvar_relatorio(relatorio)
            
            logger.info(f"Relatório gerado - Score: {score_geral}/100")
            return relatorio
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")
            return {'erro': str(e), 'timestamp': datetime.now().isoformat()}
    
    def salvar_relatorio(self, relatorio: Dict[str, Any]):
        """Salva relatório em cache"""
        try:
            cache_dir = 'cache'
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
            
            # Relatório principal
            with open(os.path.join(cache_dir, 'monitoramento_qdrant.json'), 'w', encoding='utf-8') as f:
                json.dump(relatorio, f, indent=2, ensure_ascii=False, default=str)
            
            # Histórico de relatórios
            historico_file = os.path.join(cache_dir, 'historico_monitoramento.json')
            
            historico = []
            if os.path.exists(historico_file):
                with open(historico_file, 'r', encoding='utf-8') as f:
                    historico = json.load(f)
            
            # Manter apenas últimos 100 relatórios
            historico.append({
                'timestamp': relatorio['timestamp'],
                'score_geral': relatorio['score_geral'],
                'status_geral': relatorio['status_geral'],
                'postgresql_chunks': relatorio['postgresql']['chunks_universal'],
                'qdrant_vectors': relatorio['qdrant']['vectors']
            })
            
            historico = historico[-100:]  # Manter apenas últimos 100
            
            with open(historico_file, 'w', encoding='utf-8') as f:
                json.dump(historico, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info("Relatório salvo em cache")
            
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {e}")

def executar_monitoramento():
    """Executa monitoramento completo"""
    monitor = MonitoramentoQdrantIntegrado()
    relatorio = monitor.gerar_relatorio_completo()
    
    print(f"🔍 Monitoramento Qdrant Integrado")
    print(f"📊 Score Geral: {relatorio.get('score_geral', 0)}/100")
    print(f"🏥 Status: {relatorio.get('status_geral', 'erro')}")
    
    if 'postgresql' in relatorio:
        pg = relatorio['postgresql']
        print(f"🐘 PostgreSQL: {pg['chunks_universal']} chunks, {pg['documentos_mestres']} docs mestres")
    
    if 'qdrant' in relatorio:
        qd = relatorio['qdrant']
        print(f"☁️  Qdrant: {qd['status']}, {qd['collections']} collections, {qd['vectors']} vectors")
    
    if 'sincronizacao' in relatorio:
        sync = relatorio['sincronizacao']
        print(f"🔄 Sincronização: {sync.get('percentual_sincronizacao', 0):.1f}%")
    
    return relatorio

if __name__ == "__main__":
    executar_monitoramento()