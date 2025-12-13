#!/usr/bin/env python3
"""
Script de inicialização para produção no Replit
Executa automaticamente a sincronização do banco antes de iniciar a aplicação
"""

import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def is_production_environment():
    """Detecta se está em ambiente de produção"""
    database_url = os.environ.get('DATABASE_URL', '')
    replit_deployment = os.environ.get('REPL_ID') is not None
    
    return any([
        'neon' in database_url.lower(),
        'aws' in database_url.lower(),
        replit_deployment,
        os.environ.get('FLASK_ENV') == 'production'
    ])

def run_database_sync():
    """Executa sincronização do banco de dados"""
    logger.info("🔄 Iniciando sincronização do banco de dados...")
    
    try:
        result = subprocess.run([
            sys.executable, 'sync_production_db.py'
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            logger.info("✅ Sincronização do banco concluída com sucesso")
            logger.info(result.stdout)
            return True
        else:
            logger.error(f"❌ Falha na sincronização: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Timeout na sincronização do banco (120s)")
        return False
    except Exception as e:
        logger.error(f"❌ Erro inesperado na sincronização: {str(e)}")
        return False

def start_application():
    """Inicia a aplicação com Gunicorn"""
    logger.info("🚀 Iniciando aplicação Legal Pro...")
    
    try:
        # Usar configuração otimizada do gunicorn
        cmd = [
            'gunicorn',
            '--config', 'gunicorn.conf.py',
            'main:app'
        ]
        
        logger.info(f"Executando: {' '.join(cmd)}")
        subprocess.run(cmd)
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar aplicação: {str(e)}")
        sys.exit(1)

def main():
    """Função principal do script de produção"""
    logger.info("🚀 Legal Pro - Production Startup")
    
    # Verificar se é ambiente de produção
    if is_production_environment():
        logger.info("📍 Ambiente: PRODUÇÃO")
        
        # Executar sincronização do banco
        if not run_database_sync():
            logger.error("❌ Falha crítica: Não foi possível sincronizar o banco")
            logger.info("🔄 Tentando continuar sem sincronização...")
        
    else:
        logger.info("📍 Ambiente: DESENVOLVIMENTO")
    
    # Iniciar aplicação
    start_application()

if __name__ == '__main__':
    main()