#!/usr/bin/env python3
"""
Sistema completo de coleta de dados reais para páginas administrativas
Atualiza cards e estatísticas com dados atuais do sistema
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
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdminDataCollector:
    def __init__(self):
        self.db_conn = None
        self.qdrant_client = None
        self.collected_data = {}
        
    def connect_database(self):
        """Conecta ao PostgreSQL"""
        try:
            self.db_conn = psycopg2.connect(os.environ['DATABASE_URL'])
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar banco: {e}")
            return False
    
    def collect_system_info(self):
        """Coleta informações do sistema"""
        try:
            # Informações básicas do sistema
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Uptime do sistema
            boot_time = psutil.boot_time()
            current_time = time.time()
            uptime_seconds = current_time - boot_time
            uptime = timedelta(seconds=uptime_seconds)
            
            system_info = {
                'system': platform.system(),
                'python_version': platform.python_version(),
                'platform': platform.platform(),
                'processor': platform.processor(),
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
        """Coleta estatísticas do banco de dados"""
        try:
            if not self.db_conn:
                return False
            
            # Reiniciar conexão se necessário
            try:
                self.db_conn.rollback()
            except:
                self.db_conn = psycopg2.connect(os.environ['DATABASE_URL'])
                
            cursor = self.db_conn.cursor()
            
            # Contagem de usuários
            cursor.execute('SELECT COUNT(*) FROM "user"')
            total_usuarios = cursor.fetchone()[0]
            
            # Contagem de agentes jurídicos
            cursor.execute('SELECT COUNT(*) FROM agente_juridico')
            total_agentes = cursor.fetchone()[0]
            
            # Contagem de templates
            cursor.execute('SELECT COUNT(*) FROM template_juridico')
            total_templates = cursor.fetchone()[0]
            
            # Contagem de análises realizadas
            try:
                cursor.execute('SELECT COUNT(*) FROM analise_juridica')
                total_analises = cursor.fetchone()[0]
            except:
                total_analises = 0
            
            # Contagem de transcrições
            try:
                cursor.execute('SELECT COUNT(*) FROM transcricao_audio')
                total_transcricoes = cursor.fetchone()[0]
            except:
                total_transcricoes = 0
            
            # Contagem de fluxos
            try:
                cursor.execute('SELECT COUNT(*) FROM fluxo_trabalho')
                total_fluxos = cursor.fetchone()[0]
            except:
                total_fluxos = 0
            
            # Estatísticas por área jurídica
            cursor.execute('''
                SELECT categoria_juridica.nome, COUNT(agente_juridico.id) 
                FROM categoria_juridica 
                LEFT JOIN agente_juridico ON categoria_juridica.id = agente_juridico.categoria_id 
                GROUP BY categoria_juridica.nome
            ''')
            agentes_por_area = dict(cursor.fetchall())
            
            # Usuários ativos (logados nos últimos 30 dias)
            try:
                cursor.execute('''
                    SELECT COUNT(*) FROM "user" 
                    WHERE last_login > %s AND active = true
                ''', (datetime.now() - timedelta(days=30),))
                usuarios_ativos = cursor.fetchone()[0]
            except:
                usuarios_ativos = total_usuarios
            
            database_stats = {
                'total_usuarios': total_usuarios,
                'usuarios_ativos': usuarios_ativos,
                'total_agentes': total_agentes,
                'total_templates': total_templates,
                'total_analises': total_analises,
                'total_transcricoes': total_transcricoes,
                'total_fluxos': total_fluxos,
                'agentes_por_area': agentes_por_area,
                'ultima_atualizacao': datetime.now().isoformat()
            }
            
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
                        'erro': str(e),
                        'modelos_disponiveis': 0
                    }
            else:
                api_status['openai'] = {'configurado': False, 'ativo': False}
            
            # Anthropic
            anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
            api_status['anthropic'] = {
                'configurado': bool(anthropic_key),
                'ativo': bool(anthropic_key)  # Não há endpoint público para verificar
            }
            
            # Gemini
            gemini_key = os.environ.get('GEMINI_API_KEY')
            api_status['gemini'] = {
                'configurado': bool(gemini_key),
                'ativo': bool(gemini_key)
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
            
            # AssemblyAI
            assembly_key = os.environ.get('ASSEMBLYAI_API_KEY')
            api_status['assemblyai'] = {
                'configurado': bool(assembly_key),
                'ativo': bool(assembly_key)
            }
            
            self.collected_data['api_status'] = api_status
            logger.info("✅ Status das APIs coletado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao coletar status das APIs: {e}")
            return False
    
    def collect_recent_activity(self):
        """Coleta atividades recentes do sistema"""
        try:
            if not self.db_conn:
                return False
                
            cursor = self.db_conn.cursor()
            recent_activity = []
            
            # Análises recentes (últimas 24h)
            try:
                cursor.execute('''
                    SELECT 'analise' as tipo, created_at, usuario_id, documento_nome
                    FROM analise_juridica 
                    WHERE created_at > %s 
                    ORDER BY created_at DESC LIMIT 10
                ''', (datetime.now() - timedelta(hours=24),))
                
                for row in cursor.fetchall():
                    recent_activity.append({
                        'tipo': 'Análise Jurídica',
                        'data': row[1].isoformat() if row[1] else None,
                        'usuario_id': row[2],
                        'documento': row[3]
                    })
            except:
                pass
            
            # Transcrições recentes
            try:
                cursor.execute('''
                    SELECT 'transcricao' as tipo, created_at, nome_arquivo
                    FROM transcricao_audio 
                    WHERE created_at > %s 
                    ORDER BY created_at DESC LIMIT 10
                ''', (datetime.now() - timedelta(hours=24),))
                
                for row in cursor.fetchall():
                    recent_activity.append({
                        'tipo': 'Transcrição',
                        'data': row[1].isoformat() if row[1] else None,
                        'arquivo': row[2]
                    })
            except:
                pass
            
            # Ordenar por data
            recent_activity.sort(key=lambda x: x.get('data', ''), reverse=True)
            
            self.collected_data['recent_activity'] = recent_activity[:15]
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
            network_connections = len(psutil.net_connections())
            
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
        """Salva dados coletados em cache para as páginas administrativas"""
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
        logger.info("🚀 Iniciando coleta completa de dados administrativos")
        
        success_count = 0
        total_operations = 6
        
        operations = [
            ('Conectar banco', self.connect_database),
            ('Sistema', self.collect_system_info),
            ('Banco de dados', self.collect_database_stats),
            ('APIs', self.collect_api_status),
            ('Atividades', self.collect_recent_activity),
            ('Performance', self.collect_performance_metrics)
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
        
        # Salvar cache
        if self.save_data_cache():
            success_count += 1
            total_operations += 1
        
        # Relatório final
        success_rate = (success_count / total_operations) * 100
        logger.info(f"📊 Coleta concluída: {success_count}/{total_operations} ({success_rate:.1f}%)")
        
        if self.db_conn:
            self.db_conn.close()
        
        return success_rate > 80

def update_admin_dashboard_data():
    """Função principal para atualizar dados do dashboard"""
    collector = AdminDataCollector()
    return collector.collect_all_data()

if __name__ == "__main__":
    success = update_admin_dashboard_data()
    if success:
        print("✅ Dados administrativos atualizados com sucesso")
        sys.exit(0)
    else:
        print("❌ Falha na atualização dos dados administrativos")
        sys.exit(1)