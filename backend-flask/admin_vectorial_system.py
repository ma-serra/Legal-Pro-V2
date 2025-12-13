"""
Sistema Administrativo Vetorial Completo
Gerencia upload, monitoramento e status de bases vetoriais e relacionais
"""

import os
import json
import logging
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import text, func
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException
import psycopg2
from psycopg2 import sql
import threading
import time
import schedule

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint para rotas administrativas
admin_vectorial_bp = Blueprint('admin_vectorial', __name__)

class VectorialSystemManager:
    """Gerenciador principal do sistema vetorial"""
    
    def __init__(self, app=None, db=None):
        self.app = app
        self.db = db
        self.qdrant_client = None
        self.cache_dir = 'cache'
        self.cache_file = os.path.join(self.cache_dir, 'vectorial_status.json')
        self.auto_update_running = False
        
        # Garantir que diretório cache existe
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self._init_qdrant_client()
        self._start_auto_update()
    
    def _init_qdrant_client(self):
        """Inicializa cliente Qdrant"""
        try:
            qdrant_url = os.environ.get('QDRANT_URL')
            qdrant_key = os.environ.get('QDRANT_API_KEY')
            
            if qdrant_url and qdrant_key:
                self.qdrant_client = QdrantClient(
                    url=qdrant_url,
                    api_key=qdrant_key,
                    timeout=30
                )
                logger.info("✅ Cliente Qdrant inicializado com sucesso")
            else:
                logger.warning("⚠️ Credenciais Qdrant não encontradas")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Qdrant: {e}")
    
    def get_postgresql_stats(self):
        """Coleta estatísticas do PostgreSQL"""
        try:
            with self.app.app_context():
                stats = {
                    'total_documents': 0,
                    'vectorial_documents': 0,
                    'relational_documents': 0,
                    'areas_distribution': {},
                    'recent_uploads': 0,
                    'storage_size': 0,
                    'embedding_tables': []
                }
                
                # Contar documentos na base universal
                try:
                    universal_count = self.db.session.execute(
                        text("SELECT COUNT(*) FROM documentos_juridicos")
                    ).scalar() or 0
                    stats['total_documents'] = universal_count
                except:
                    pass
                
                # Verificar tabelas de embeddings
                embedding_tables_query = text("""
                    SELECT table_name, 
                           pg_total_relation_size(quote_ident(table_name)) as size_bytes
                    FROM information_schema.tables 
                    WHERE table_name LIKE 'embeddings_%'
                    AND table_schema = 'public'
                """)
                
                embedding_results = self.db.session.execute(embedding_tables_query)
                
                for table_name, size_bytes in embedding_results:
                    try:
                        # Contar registros na tabela de embedding
                        count = self.db.session.execute(
                            text(f"SELECT COUNT(*) FROM {table_name}")
                        ).scalar() or 0
                        
                        area_name = table_name.replace('embeddings_', '').replace('_', ' ').title()
                        
                        stats['embedding_tables'].append({
                            'table': table_name,
                            'area': area_name,
                            'count': count,
                            'size_mb': round(size_bytes / 1024 / 1024, 2)
                        })
                        
                        stats['vectorial_documents'] += count
                        stats['areas_distribution'][area_name] = count
                        stats['storage_size'] += size_bytes
                        
                    except Exception as e:
                        logger.warning(f"Erro ao processar tabela {table_name}: {e}")
                
                # Contar uploads recentes (últimas 24h)
                try:
                    recent_time = datetime.now() - timedelta(hours=24)
                    recent_count = self.db.session.execute(text("""
                        SELECT COUNT(*) FROM documentos_juridicos 
                        WHERE created_at >= :recent_time
                    """), {'recent_time': recent_time}).scalar() or 0
                    stats['recent_uploads'] = recent_count
                except:
                    pass
                
                # Converter storage size para MB
                stats['storage_size'] = round(stats['storage_size'] / 1024 / 1024, 2)
                
                return stats
                
        except Exception as e:
            logger.error(f"Erro ao coletar estatísticas PostgreSQL: {e}")
            return {}
    
    def get_qdrant_stats(self):
        """Coleta estatísticas do Qdrant"""
        try:
            if not self.qdrant_client:
                return {'status': 'não_configurado', 'collections': [], 'total_vectors': 0}
            
            collections_info = self.qdrant_client.get_collections()
            
            stats = {
                'status': 'ativo',
                'collections': [],
                'total_vectors': 0,
                'memory_usage': 0
            }
            
            for collection in collections_info.collections:
                try:
                    collection_info = self.qdrant_client.get_collection(collection.name)
                    
                    collection_stats = {
                        'name': collection.name,
                        'vectors_count': collection_info.vectors_count or 0,
                        'points_count': collection_info.points_count or 0,
                        'status': 'ativo'
                    }
                    
                    stats['collections'].append(collection_stats)
                    stats['total_vectors'] += collection_info.vectors_count or 0
                    
                except Exception as e:
                    logger.warning(f"Erro ao processar coleção {collection.name}: {e}")
            
            return stats
            
        except ResponseHandlingException as e:
            logger.error(f"Erro de conexão Qdrant: {e}")
            return {'status': 'erro_conexao', 'error': str(e)}
        except Exception as e:
            logger.error(f"Erro ao coletar estatísticas Qdrant: {e}")
            return {'status': 'erro', 'error': str(e)}
    
    def calculate_system_health(self, pg_stats, qdrant_stats):
        """Calcula saúde geral do sistema"""
        health_score = 0
        
        # PostgreSQL (50% do score)
        if pg_stats.get('total_documents', 0) > 0:
            health_score += 25
        if pg_stats.get('vectorial_documents', 0) > 0:
            health_score += 25
        
        # Qdrant (50% do score)
        if qdrant_stats.get('status') == 'ativo':
            health_score += 25
        if qdrant_stats.get('total_vectors', 0) > 0:
            health_score += 25
        
        # Determinar status
        if health_score >= 75:
            status = 'excelente'
        elif health_score >= 50:
            status = 'bom'
        elif health_score >= 25:
            status = 'regular'
        else:
            status = 'crítico'
        
        return {
            'score': health_score,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }
    
    def update_system_status(self):
        """Atualiza status completo do sistema"""
        try:
            logger.info("🔄 Atualizando status do sistema vetorial...")
            
            # Coletar estatísticas
            pg_stats = self.get_postgresql_stats()
            qdrant_stats = self.get_qdrant_stats()
            health = self.calculate_system_health(pg_stats, qdrant_stats)
            
            # Dados consolidados
            system_status = {
                'timestamp': datetime.now().isoformat(),
                'postgresql': pg_stats,
                'qdrant': qdrant_stats,
                'health': health,
                'sync_status': self._check_sync_status(pg_stats, qdrant_stats)
            }
            
            # Salvar no cache
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(system_status, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Status atualizado - Saúde: {health['status']} ({health['score']}%)")
            
            return system_status
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar status: {e}")
            return None
    
    def _check_sync_status(self, pg_stats, qdrant_stats):
        """Verifica sincronização entre PostgreSQL e Qdrant"""
        try:
            pg_vectors = pg_stats.get('vectorial_documents', 0)
            qdrant_vectors = qdrant_stats.get('total_vectors', 0)
            
            if pg_vectors == 0 and qdrant_vectors == 0:
                return {'status': 'sincronizado', 'percentage': 100}
            
            if pg_vectors == 0:
                return {'status': 'desincronizado', 'percentage': 0}
            
            sync_percentage = min(100, (qdrant_vectors / pg_vectors) * 100)
            status = 'sincronizado' if sync_percentage >= 95 else 'desincronizado'
            
            return {
                'status': status,
                'percentage': round(sync_percentage, 1),
                'pg_vectors': pg_vectors,
                'qdrant_vectors': qdrant_vectors
            }
            
        except Exception as e:
            logger.error(f"Erro ao verificar sincronização: {e}")
            return {'status': 'erro', 'percentage': 0}
    
    def get_cached_status(self):
        """Obtém status do cache"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao ler cache: {e}")
        
        # Se não há cache, atualizar
        return self.update_system_status()
    
    def _start_auto_update(self):
        """Inicia atualização automática a cada 30 minutos"""
        if not self.auto_update_running:
            self.auto_update_running = True
            
            def update_job():
                if self.app:
                    with self.app.app_context():
                        self.update_system_status()
            
            # Configurar agendamento
            schedule.every(30).minutes.do(update_job)
            
            def run_scheduler():
                while self.auto_update_running:
                    schedule.run_pending()
                    time.sleep(60)  # Verificar a cada minuto
            
            # Executar em thread separada
            scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
            scheduler_thread.start()
            
            logger.info("⏰ Sistema de atualização automática iniciado (30 minutos)")

# Instância global do gerenciador
vectorial_manager = None

def init_vectorial_system(app, db):
    """Inicializa sistema vetorial administrativo"""
    global vectorial_manager
    vectorial_manager = VectorialSystemManager(app, db)
    return vectorial_manager

# Rotas administrativas
@admin_vectorial_bp.route('/admin/upload-manager')
@login_required
def admin_upload_manager_vectorial():
    """Página de gerenciamento de uploads"""
    try:
        if not vectorial_manager:
            flash('Sistema vetorial não inicializado', 'error')
            return redirect(url_for('admin_dashboard'))
        
        # Obter status atual
        status = vectorial_manager.get_cached_status()
        
        # Preparar dados para o template
        stats = {
            'total_uploads': status.get('postgresql', {}).get('total_documents', 0),
            'vectorial_uploads': status.get('postgresql', {}).get('vectorial_documents', 0),
            'relational_uploads': status.get('postgresql', {}).get('total_documents', 0) - status.get('postgresql', {}).get('vectorial_documents', 0),
            'recent_uploads': status.get('postgresql', {}).get('recent_uploads', 0),
            'storage_usage': status.get('postgresql', {}).get('storage_size', 0),
            'system_health': status.get('health', {}).get('score', 0),
            'qdrant_status': status.get('qdrant', {}).get('status', 'não_configurado'),
            'last_update': status.get('timestamp', ''),
            'areas_distribution': status.get('postgresql', {}).get('areas_distribution', {})
        }
        
        return render_template('admin/upload_manager_enhanced.html', stats=stats, status=status)
        
    except Exception as e:
        logger.error(f"Erro no upload manager: {e}")
        flash('Erro ao carregar gerenciador de uploads', 'error')
        return redirect(url_for('admin_dashboard'))

@admin_vectorial_bp.route('/admin/monitoring/vectorial')
@login_required
def admin_monitoring_vectorial():
    """Página de monitoramento vetorial"""
    try:
        if not vectorial_manager:
            flash('Sistema vetorial não inicializado', 'error')
            return redirect(url_for('admin_dashboard'))
        
        # Obter status detalhado
        status = vectorial_manager.get_cached_status()
        
        return render_template('admin/monitoring_vectorial_enhanced.html', 
                             status=status, 
                             timestamp=datetime.now())
        
    except Exception as e:
        logger.error(f"Erro no monitoramento vetorial: {e}")
        flash('Erro ao carregar monitoramento vetorial', 'error')
        return redirect(url_for('admin_dashboard'))

@admin_vectorial_bp.route('/api/admin/vectorial/status')
@login_required
def api_vectorial_status():
    """API para status vetorial em tempo real"""
    try:
        if not vectorial_manager:
            return jsonify({'error': 'Sistema não inicializado'}), 500
        
        # Forçar atualização se solicitado
        force_update = request.args.get('update', 'false').lower() == 'true'
        
        if force_update:
            status = vectorial_manager.update_system_status()
        else:
            status = vectorial_manager.get_cached_status()
        
        if not status:
            return jsonify({'error': 'Erro ao obter status'}), 500
        
        return jsonify({
            'success': True,
            'data': status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro na API de status: {e}")
        return jsonify({'error': str(e)}), 500

@admin_vectorial_bp.route('/api/admin/vectorial/update', methods=['POST'])
@login_required
def api_vectorial_update():
    """API para forçar atualização do sistema"""
    try:
        if not vectorial_manager:
            return jsonify({'error': 'Sistema não inicializado'}), 500
        
        status = vectorial_manager.update_system_status()
        
        if status:
            return jsonify({
                'success': True,
                'message': 'Sistema atualizado com sucesso',
                'data': status
            })
        else:
            return jsonify({'error': 'Erro ao atualizar sistema'}), 500
        
    except Exception as e:
        logger.error(f"Erro na atualização forçada: {e}")
        return jsonify({'error': str(e)}), 500

def register_vectorial_admin(app, db):
    """Registra sistema administrativo vetorial"""
    try:
        # Inicializar gerenciador
        manager = init_vectorial_system(app, db)
        
        # Registrar blueprint
        app.register_blueprint(admin_vectorial_bp)
        
        logger.info("✅ Sistema Administrativo Vetorial registrado com sucesso")
        return manager
        
    except Exception as e:
        logger.error(f"❌ Erro ao registrar sistema vetorial: {e}")
        return None