"""
Monitoramento de sistema para o Sistema Multi-Agente.
"""
import os
import datetime
import psutil
import platform
import logging
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

class SystemMonitor:
    """
    Classe responsável pelo monitoramento do sistema e operações administrativas.
    """
    
    def __init__(self):
        self.start_time = datetime.datetime.now()
    
    def get_system_metrics(self):
        """
        Obtém métricas do sistema como uso de CPU, memória, etc.
        
        Returns:
            dict: Dicionário com métricas do sistema
        """
        try:
            # Informações de CPU
            cpu_percent = psutil.cpu_percent(interval=0.5)
            cpu_count = psutil.cpu_count()
            
            # Informações de memória
            memory = psutil.virtual_memory()
            memory_total = memory.total
            memory_available = memory.available
            memory_used = memory.used
            memory_percent = memory.percent
            
            # Informações de disco
            disk = psutil.disk_usage('/')
            disk_total = disk.total
            disk_free = disk.free
            disk_used = disk.used
            disk_percent = disk.percent
            
            # Informações de rede
            net_io = psutil.net_io_counters()
            net_bytes_sent = net_io.bytes_sent
            net_bytes_recv = net_io.bytes_recv
            
            # Tempo de execução
            uptime = datetime.datetime.now() - self.start_time
            uptime_seconds = uptime.total_seconds()
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count
                },
                "memory": {
                    "total": memory_total,
                    "available": memory_available,
                    "used": memory_used,
                    "percent": memory_percent
                },
                "disk": {
                    "total": disk_total,
                    "free": disk_free,
                    "used": disk_used,
                    "percent": disk_percent
                },
                "network": {
                    "bytes_sent": net_bytes_sent,
                    "bytes_recv": net_bytes_recv
                },
                "uptime": {
                    "seconds": uptime_seconds,
                    "formatted": str(uptime).split('.')[0]  # Remove microssegundos
                },
                "system": {
                    "platform": platform.system(),
                    "release": platform.release(),
                    "version": platform.version(),
                    "processor": platform.processor()
                }
            }
        except Exception as e:
            logger.error(f"Erro ao obter métricas do sistema: {str(e)}")
            return {
                "error": str(e)
            }
    
    def initialize_admin_user(self, db):
        """
        Inicializa o usuário administrador se não existir.
        
        Args:
            db: Instância do SQLAlchemy
        
        Returns:
            bool: True se o usuário foi criado, False caso contrário
        """
        from models import User, Role, Permission
        
        try:
            # Verifica se já existe algum usuário
            user_count = User.query.count()
            if user_count > 0:
                logger.info("Sistema já possui usuários cadastrados. Pulando inicialização de admin.")
                return False
            
            # Cria permissões básicas se não existirem
            permissions = {
                "user_manage": "Gerenciar Usuários",
                "role_manage": "Gerenciar Papéis",
                "permission_manage": "Gerenciar Permissões",
                "system_config": "Configurar Sistema",
                "agent_manage": "Gerenciar Agentes",
                "workflow_manage": "Gerenciar Fluxos",
                "logs_view": "Visualizar Logs",
                "reports_view": "Visualizar Relatórios"
            }
            
            created_permissions = []
            for code, name in permissions.items():
                perm = Permission.query.filter_by(code=code).first()
                if not perm:
                    perm = Permission()
                    perm.code = code
                    perm.name = name
                    perm.description = f"Permissão para {name.lower()}"
                    db.session.add(perm)
                    created_permissions.append(perm)
            
            # Salva para obter IDs
            db.session.commit()
            
            # Cria papel de administrador se não existir
            admin_role = Role.query.filter_by(name="Administrador").first()
            if not admin_role:
                admin_role = Role()
                admin_role.name = "Administrador"
                admin_role.description = "Papel com acesso total ao sistema"
                db.session.add(admin_role)
                db.session.commit()
                
                # Associa todas as permissões ao papel de administrador
                all_permissions = Permission.query.all()
                admin_role.permissions = all_permissions
                db.session.commit()
            
            # Cria o usuário administrador
            admin_user = User()
            admin_user.username = "admin"
            admin_user.email = "admin@sistema.com"
            admin_user.first_name = "Administrador"
            admin_user.last_name = "Sistema"
            admin_user.active = True
            admin_user.is_admin = True
            admin_user.role_id = admin_role.id
            admin_user.set_password("admin123")
            
            db.session.add(admin_user)
            db.session.commit()
            
            logger.info("Usuário administrador criado com sucesso.")
            logger.info("Username: admin")
            logger.info("Senha: admin123")
            logger.info("ATENÇÃO: Por favor, altere a senha após o primeiro login.")
            
            return True
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erro SQL ao criar usuário administrador: {str(e)}")
            return False
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao criar usuário administrador: {str(e)}")
            return False


# Singleton para o monitor do sistema
_system_monitor = None

def get_system_monitor():
    """
    Obtém uma instância do monitor do sistema.
    
    Returns:
        SystemMonitor: Instância do monitor do sistema
    """
    global _system_monitor
    if _system_monitor is None:
        _system_monitor = SystemMonitor()
    return _system_monitor