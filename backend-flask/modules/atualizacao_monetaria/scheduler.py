"""
Scheduler para Atualização Automática de Índices
Executa tarefas periódicas de importação
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

from .importador import ImportadorIndices

logger = logging.getLogger(__name__)


class AtualizacaoScheduler:
    """
    Gerencia jobs agendados de atualização monetária
    """
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.jobs = {}
    
    def iniciar(self):
        """Inicia o scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("✅ Scheduler de atualização monetária iniciado")
    
    def parar(self):
        """Para o scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler de atualização monetária parado")
    
    def agendar_atualizacao_diaria(self, hora: int = 8, minuto: int = 0):
        """
        Agenda atualização diária de índices
        
        Args:
            hora: Hora do dia (0-23)
            minuto: Minuto (0-59)
        """
        job_id = 'atualizacao_diaria_indices'
        
        # Remover job existente
        if job_id in self.jobs:
            self.scheduler.remove_job(job_id)
        
        # Criar trigger
        trigger = CronTrigger(hour=hora, minute=minuto)
        
        # Adicionar job
        job = self.scheduler.add_job(
            func=self._executar_atualizacao_diaria,
            trigger=trigger,
            id=job_id,
            name='Atualização Diária de Índices',
            replace_existing=True
        )
        
        self.jobs[job_id] = job
        logger.info(f"Job agendado: atualização diária às {hora:02d}:{minuto:02d}")
        
        return job
    
    def agendar_atualizacao_semanal(self, dia_semana: int = 0, hora: int = 8):
        """
        Agenda atualização semanal completa
        
        Args:
            dia_semana: 0=Segunda, 6=Domingo
            hora: Hora do dia
        """
        job_id = 'atualizacao_semanal_indices'
        
        if job_id in self.jobs:
            self.scheduler.remove_job(job_id)
        
        trigger = CronTrigger(day_of_week=dia_semana, hour=hora)
        
        job = self.scheduler.add_job(
            func=self._executar_atualizacao_completa,
            trigger=trigger,
            id=job_id,
            name='Atualização Semanal Completa',
            replace_existing=True
        )
        
        self.jobs[job_id] = job
        logger.info(f"Job agendado: atualização semanal dia {dia_semana} às {hora:02d}:00")
        
        return job
    
    def executar_agora(self, tipo: str = 'recente'):
        """
        Executa atualização imediatamente
        
        Args:
            tipo: 'recente' (30 dias) ou 'completa' (1 ano)
        """
        if tipo == 'completa':
            return self._executar_atualizacao_completa()
        else:
            return self._executar_atualizacao_diaria()
    
    def _executar_atualizacao_diaria(self):
        """Atualiza índices dos últimos 30 dias"""
        try:
            logger.info("Iniciando atualização diária de índices...")
            resultado = ImportadorIndices.atualizar_indices_recentes(dias=30)
            
            total = sum(resultado.values())
            logger.info(f"Atualização diária concluída: {total} registros importados")
            logger.info(f"Detalhes: {resultado}")
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro na atualização diária: {e}")
            raise
    
    def _executar_atualizacao_completa(self):
        """Atualiza índices do último ano"""
        try:
            logger.info("Iniciando atualização completa de índices (1 ano)...")
            resultado = ImportadorIndices.importar_todos_indices()
            
            total = sum(resultado.values())
            logger.info(f"Atualização completa concluída: {total} registros importados")
            logger.info(f"Detalhes: {resultado}")
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro na atualização completa: {e}")
            raise
    
    def listar_jobs(self):
        """Lista todos os jobs agendados"""
        jobs = []
        
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'nome': job.name,
                'proxima_execucao': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        
        return jobs
    
    def remover_job(self, job_id: str) -> bool:
        """Remove um job agendado"""
        try:
            self.scheduler.remove_job(job_id)
            if job_id in self.jobs:
                del self.jobs[job_id]
            logger.info(f"Job {job_id} removido")
            return True
        except:
            return False


# Instância global do scheduler
scheduler_global = AtualizacaoScheduler()


def iniciar_scheduler_automatico(app):
    """
    Inicializa scheduler com configurações padrão
    
    Chamado no startup do Flask
    """
    try:
        scheduler_global.iniciar()
        
        # Agendar atualizações
        scheduler_global.agendar_atualizacao_diaria(hora=8, minuto=0)  # 08:00
        scheduler_global.agendar_atualizacao_semanal(dia_semana=0, hora=6)  # Segunda 06:00
        
        logger.info("✅ Scheduler automático configurado")
        
        # Executar uma atualização inicial
        # scheduler_global.executar_agora('recente')  # Comentado para não travar startup
        
    except Exception as e:
        logger.error(f"Erro ao iniciar scheduler: {e}")
