#!/usr/bin/env python3
"""
Monitor Automático de Sessão - Sistema de Produção
Executa limpeza automática e monitora saúde das sessões
"""

import time
import logging
import threading
from datetime import datetime, timedelta
from session_manager import SessionManager
from flask import Flask

class SessionMonitor:
    """
    Monitor automático de sessão que roda em background
    """
    
    def __init__(self, app=None, interval=300):  # 5 minutos por padrão
        self.app = app
        self.interval = interval
        self.running = False
        self.thread = None
        self.stats = {
            'cleanups_performed': 0,
            'sessions_cleaned': 0,
            'last_cleanup': None,
            'warnings_issued': 0,
            'critical_alerts': 0
        }
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def start_monitoring(self):
        """Inicia o monitoramento em background"""
        if self.running:
            self.logger.warning("Monitor já está rodando")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        self.logger.info("SessionMonitor: Monitoramento iniciado")
    
    def stop_monitoring(self):
        """Para o monitoramento"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        self.logger.info("SessionMonitor: Monitoramento parado")
    
    def _monitor_loop(self):
        """Loop principal de monitoramento"""
        while self.running:
            try:
                self._perform_cleanup()
                time.sleep(self.interval)
            except Exception as e:
                self.logger.error(f"SessionMonitor: Erro no loop de monitoramento: {e}")
                time.sleep(60)  # Espera 1 minuto em caso de erro
    
    def _perform_cleanup(self):
        """Executa limpeza automática"""
        if not self.app:
            return
        
        with self.app.app_context():
            try:
                # Executar limpeza de sessões antigas
                SessionManager.clean_old_sessions()
                
                # Monitorar saúde da sessão
                health = SessionManager.monitor_session_health()
                
                # Atualizar estatísticas
                self.stats['cleanups_performed'] += 1
                self.stats['last_cleanup'] = datetime.now().isoformat()
                
                # Alertas baseados na saúde
                if health['status'] == 'warning':
                    self.stats['warnings_issued'] += 1
                    self.logger.warning(
                        f"SessionMonitor: Uso de sessão alto ({health['percentage_used']:.1f}%)"
                    )
                elif health['status'] == 'critical':
                    self.stats['critical_alerts'] += 1
                    self.logger.error(
                        f"SessionMonitor: Uso de sessão crítico ({health['percentage_used']:.1f}%)"
                    )
                    # Limpeza forçada em situação crítica
                    self._emergency_cleanup()
                
                self.logger.debug(f"SessionMonitor: Limpeza concluída - {health}")
                
            except Exception as e:
                self.logger.error(f"SessionMonitor: Erro na limpeza: {e}")
    
    def _emergency_cleanup(self):
        """Limpeza de emergência para situações críticas"""
        try:
            # Limpar dados mais agressivamente
            SessionManager.clear_analysis_data()
            self.stats['sessions_cleaned'] += 1
            self.logger.info("SessionMonitor: Limpeza de emergência executada")
        except Exception as e:
            self.logger.error(f"SessionMonitor: Erro na limpeza de emergência: {e}")
    
    def get_stats(self):
        """Retorna estatísticas do monitor"""
        stats = self.stats.copy()
        stats['is_running'] = self.running
        stats['interval_seconds'] = self.interval
        return stats
    
    def force_cleanup(self):
        """Força uma limpeza imediata"""
        if self.app:
            with self.app.app_context():
                self._perform_cleanup()
                return True
        return False

# Instância global do monitor
session_monitor = SessionMonitor()

def init_session_monitoring(app, interval=300):
    """
    Inicializa o monitoramento de sessão na aplicação Flask
    
    Args:
        app: Instância da aplicação Flask
        interval: Intervalo em segundos entre limpezas (padrão: 5 minutos)
    """
    global session_monitor
    session_monitor.app = app
    session_monitor.interval = interval
    
    # Iniciar monitoramento automaticamente
    session_monitor.start_monitoring()
    
    # Registrar rota de status (opcional)
    @app.route('/admin/session-monitor-status')
    def session_monitor_status():
        from flask import jsonify
        from flask_login import login_required
        
        @login_required
        def _status():
            stats = session_monitor.get_stats()
            return jsonify(stats)
        
        return _status()
    
    # Registrar rota de limpeza forçada (opcional)
    @app.route('/admin/force-session-cleanup', methods=['POST'])
    def force_session_cleanup():
        from flask import jsonify, flash, redirect, url_for
        from flask_login import login_required
        from auth import admin_required
        
        @login_required
        @admin_required
        def _force_cleanup():
            success = session_monitor.force_cleanup()
            if success:
                flash('Limpeza de sessão executada com sucesso', 'success')
            else:
                flash('Erro ao executar limpeza de sessão', 'error')
            
            return redirect(url_for('admin_config'))
        
        return _force_cleanup()
    
    # Cleanup gracioso na finalização da aplicação
    import atexit
    atexit.register(session_monitor.stop_monitoring)
    
    app.logger.info("SessionMonitor: Sistema de monitoramento inicializado")
    return session_monitor

if __name__ == "__main__":
    # Teste standalone
    from flask import Flask
    
    app = Flask(__name__)
    app.secret_key = "test_key"
    
    # Inicializar monitoramento
    monitor = init_session_monitoring(app, interval=10)  # 10 segundos para teste
    
    try:
        print("Monitor iniciado. Pressione Ctrl+C para parar...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nParando monitor...")
        monitor.stop_monitoring()