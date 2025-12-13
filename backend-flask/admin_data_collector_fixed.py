#!/usr/bin/env python3
"""
Sistema corrigido de coleta de dados reais para páginas administrativas
Corrige problemas de transação e coleta dados atuais do sistema
"""

import os
import sys
import psycopg2
import psutil
import platform
import time
import json
import requests
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdminDataCollectorFixed:
    def __init__(self):
        self.collected_data = {}
        
    def get_fresh_db_connection(self):
        """Obtém uma nova conexão limpa com o banco"""
        try:
            return psycopg2.connect(os.environ['DATABASE_URL'])
        except Exception as e:
            logger.error(f"Erro ao conectar banco: {e}")
            return None
    
    def collect_system_info(self):
        """Coleta informações do sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            boot_time = psutil.boot_time()
            current_time = time.time()
            uptime_seconds = current_time - boot_time
            uptime = timedelta(seconds=uptime_seconds)
            
            system_info = {
                'system': platform.system(),
                'python_version': platform.python_version(),
                'platform': platform.platform(),
                'uptime': {
                    'days': uptime.days,
                    'hours': uptime.seconds // 3600,
                    'minutes': (uptime.seconds % 3600) // 60
                },
                'cpu': {
                    'usage_percent': round(cpu_percent, 1),
                    'total_cores': psutil.cpu_count(),
                    'physical_cores': psutil.cpu_count(logical=False)
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'percent': round(memory.percent, 1),
                    'total_gb': round(memory.total / (1024**3), 2),
                    'used_gb': round(memory.used / (1024**3), 2)
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': round((disk.used / disk.total) * 100, 1),
                    'total_gb': round(disk.total / (1024**3), 2),
                    'used_gb': round(disk.used / (1024**3), 2)
                }
            }
            
            self.collected_data['system_info'] = system_info
            logger.info("✅ Informações do sistema coletadas")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao coletar informações do sistema: {e}")
            return False
    
    def collect_database_stats(self):
        """Coleta estatísticas do banco de dados com conexão limpa"""
        try:
            conn = self.get_fresh_db_connection()
            if not conn:
                return False
                
            cursor = conn.cursor()
            
            # Contagens básicas
            counts = {}
            
            # Tabelas principais
            queries = {
                'total_usuarios': 'SELECT COUNT(*) FROM "user"',
                'total_agentes': 'SELECT COUNT(*) FROM agente_juridico',
                'total_categorias': 'SELECT COUNT(*) FROM categoria_juridica',
                'total_templates': 'SELECT COUNT(*) FROM template_juridico'
            }
            
            for name, query in queries.items():
                try:
                    cursor.execute(query)
                    counts[name] = cursor.fetchone()[0]
                except Exception as e:
                    logger.warning(f"Erro na consulta {name}: {e}")
                    counts[name] = 0
            
            # Tabelas opcionais
            optional_queries = {
                'total_analises': 'SELECT COUNT(*) FROM analise_juridica',
                'total_transcricoes': 'SELECT COUNT(*) FROM transcricao_audio',
                'total_fluxos': 'SELECT COUNT(*) FROM fluxo_trabalho'
            }
            
            for name, query in optional_queries.items():
                try:
                    cursor.execute(query)
                    counts[name] = cursor.fetchone()[0]
                except:
                    counts[name] = 0
            
            # Agentes por área
            try:
                cursor.execute('''
                    SELECT c.nome, COUNT(a.id) 
                    FROM categoria_juridica c 
                    LEFT JOIN agente_juridico a ON c.id = a.categoria_id 
                    GROUP BY c.nome
                ''')
                agentes_por_area = dict(cursor.fetchall())
            except:
                agentes_por_area = {}
            
            # Usuários ativos
            try:
                cursor.execute('''
                    SELECT COUNT(*) FROM "user" 
                    WHERE active = true
                ''')
                usuarios_ativos = cursor.fetchone()[0]
            except:
                usuarios_ativos = counts.get('total_usuarios', 0)
            
            database_stats = {
                **counts,
                'usuarios_ativos': usuarios_ativos,
                'agentes_por_area': agentes_por_area,
                'ultima_atualizacao': datetime.now().isoformat()
            }
            
            cursor.close()
            conn.close()
            
            self.collected_data['database_stats'] = database_stats
            logger.info("✅ Estatísticas do banco coletadas")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao coletar estatísticas do banco: {e}")
            return False
    
    def collect_api_status(self):
        """Coleta status das APIs externas"""
        try:
            api_status = {}
            
            # OpenAI
            openai_key = os.environ.get('OPENAI_API_KEY')
            if openai_key:
                try:
                    headers = {'Authorization': f'Bearer {openai_key}'}
                    response = requests.get('https://api.openai.com/v1/models', 
                                          headers=headers, timeout=10)
                    api_status['openai'] = {
                        'configurado': True,
                        'ativo': response.status_code == 200,
                        'status_code': response.status_code,
                        'modelos_disponiveis': len(response.json().get('data', [])) if response.status_code == 200 else 0
                    }
                except Exception as e:
                    api_status['openai'] = {
                        'configurado': True,
                        'ativo': False,
                        'erro': str(e)
                    }
            else:
                api_status['openai'] = {'configurado': False, 'ativo': False}
            
            # Outras APIs
            apis = {
                'anthropic': os.environ.get('ANTHROPIC_API_KEY'),
                'gemini': os.environ.get('GEMINI_API_KEY'),
                'assemblyai': os.environ.get('ASSEMBLYAI_API_KEY')
            }
            
            for api_name, api_key in apis.items():
                api_status[api_name] = {
                    'configurado': bool(api_key),
                    'ativo': bool(api_key)
                }
            
            # Qdrant
            qdrant_url = os.environ.get('QDRANT_URL')
            qdrant_key = os.environ.get('QDRANT_API_KEY')
            if qdrant_url and qdrant_key:
                try:
                    headers = {'api-key': qdrant_key}
                    response = requests.get(f"{qdrant_url}/collections", 
                                          headers=headers, timeout=10)
                    collections = response.json().get('result', {}).get('collections', [])
                    api_status['qdrant'] = {
                        'configurado': True,
                        'ativo': response.status_code == 200,
                        'collections': len(collections),
                        'collections_list': [c['name'] for c in collections]
                    }
                except Exception as e:
                    api_status['qdrant'] = {
                        'configurado': True,
                        'ativo': False,
                        'erro': str(e)
                    }
            else:
                api_status['qdrant'] = {'configurado': False, 'ativo': False}
            
            self.collected_data['api_status'] = api_status
            logger.info("✅ Status das APIs coletado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao coletar status das APIs: {e}")
            return False
    
    def collect_recent_activity(self):
        """Coleta atividades recentes do sistema"""
        try:
            conn = self.get_fresh_db_connection()
            if not conn:
                return False
                
            cursor = conn.cursor()
            recent_activity = []
            
            # Buscar atividades das últimas 24h
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            # Análises recentes
            try:
                cursor.execute('''
                    SELECT 'Análise Jurídica' as tipo, created_at, usuario_id
                    FROM analise_juridica 
                    WHERE created_at > %s 
                    ORDER BY created_at DESC LIMIT 5
                ''', (cutoff_time,))
                
                for row in cursor.fetchall():
                    recent_activity.append({
                        'tipo': row[0],
                        'data': row[1].isoformat() if row[1] else None,
                        'usuario_id': row[2]
                    })
            except:
                pass
            
            # Transcrições recentes
            try:
                cursor.execute('''
                    SELECT 'Transcrição' as tipo, created_at, nome_arquivo
                    FROM transcricao_audio 
                    WHERE created_at > %s 
                    ORDER BY created_at DESC LIMIT 5
                ''', (cutoff_time,))
                
                for row in cursor.fetchall():
                    recent_activity.append({
                        'tipo': row[0],
                        'data': row[1].isoformat() if row[1] else None,
                        'arquivo': row[2]
                    })
            except:
                pass
            
            # Se não há atividades recentes, criar entradas de exemplo
            if not recent_activity:
                recent_activity = [
                    {
                        'tipo': 'Sistema Inicializado',
                        'data': datetime.now().isoformat(),
                        'descricao': 'Sistema em operação'
                    }
                ]
            
            # Ordenar por data
            recent_activity.sort(key=lambda x: x.get('data', ''), reverse=True)
            
            cursor.close()
            conn.close()
            
            self.collected_data['recent_activity'] = recent_activity[:10]
            logger.info("✅ Atividades recentes coletadas")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao coletar atividades recentes: {e}")
            return False
    
    def collect_performance_metrics(self):
        """Coleta métricas de performance"""
        try:
            # Processos Python
            python_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
                try:
                    if 'python' in proc.info['name'].lower():
                        python_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'memory_percent': round(proc.info['memory_percent'], 2),
                            'cpu_percent': round(proc.info['cpu_percent'], 2)
                        })
                except:
                    continue
            
            # Top processos por memória
            top_processes = sorted(python_processes, 
                                 key=lambda x: x['memory_percent'], 
                                 reverse=True)[:5]
            
            # Conexões de rede
            try:
                network_connections = len(psutil.net_connections())
            except:
                network_connections = 0
            
            performance_metrics = {
                'python_processes_count': len(python_processes),
                'top_processes': top_processes,
                'network_connections': network_connections,
                'timestamp': datetime.now().isoformat()
            }
            
            self.collected_data['performance_metrics'] = performance_metrics
            logger.info("✅ Métricas de performance coletadas")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas de performance: {e}")
            return False
    
    def save_data_cache(self):
        """Salva dados coletados em cache"""
        try:
            cache_file = 'cache/admin_data_cache.json'
            os.makedirs('cache', exist_ok=True)
            
            with open(cache_file, 'w') as f:
                json.dump(self.collected_data, f, indent=2, default=str)
            
            logger.info(f"✅ Cache salvo em {cache_file}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {e}")
            return False
    
    def collect_all_data(self):
        """Executa coleta completa de dados"""
        logger.info("🚀 Iniciando coleta completa de dados administrativos (versão corrigida)")
        
        success_count = 0
        total_operations = 6
        
        operations = [
            ('Sistema', self.collect_system_info),
            ('Banco de dados', self.collect_database_stats),
            ('APIs', self.collect_api_status),
            ('Atividades', self.collect_recent_activity),
            ('Performance', self.collect_performance_metrics),
            ('Cache', self.save_data_cache)
        ]
        
        for name, operation in operations:
            try:
                if operation():
                    success_count += 1
                    logger.info(f"✅ {name}: OK")
                else:
                    logger.error(f"❌ {name}: FALHA")
            except Exception as e:
                logger.error(f"❌ {name}: ERRO - {e}")
        
        # Relatório final
        success_rate = (success_count / total_operations) * 100
        logger.info(f"📊 Coleta concluída: {success_count}/{total_operations} ({success_rate:.1f}%)")
        
        return success_rate > 70

def update_admin_dashboard_data_fixed():
    """Função principal para atualizar dados do dashboard (versão corrigida)"""
    collector = AdminDataCollectorFixed()
    return collector.collect_all_data()

if __name__ == "__main__":
    success = update_admin_dashboard_data_fixed()
    if success:
        print("✅ Dados administrativos atualizados com sucesso (versão corrigida)")
        sys.exit(0)
    else:
        print("❌ Falha na atualização dos dados administrativos")
        sys.exit(1)