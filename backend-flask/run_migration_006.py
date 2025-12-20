
import os
import psycopg2
import logging

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL do Banco de Dados
DEFAULT_DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"
DB_URL = os.environ.get('DATABASE_URL', DEFAULT_DB_URL)

def run_mig():
    """
    Executa a migração 006 para criar a tabela simulacoes_tributarias
    """
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        logger.info("Applying migration 006 (Create simulacoes_tributarias)...")
        
        # Lê o arquivo SQL
        migration_file = os.path.join(os.path.dirname(__file__), 'migrations', '006_create_simulacoes_tributarias.sql')
        
        if not os.path.exists(migration_file):
            logger.error(f"Migration file not found: {migration_file}")
            return
            
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
            
        # Executa o script SQL
        cur.execute(sql_content)
        
        conn.commit()
        logger.info("Migration 006 applied successfully.")
        
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        logger.error(f"Migration failed: {e}")
    finally:
        if 'conn' in locals():
            cur.close()
            conn.close()

if __name__ == "__main__":
    run_mig()
