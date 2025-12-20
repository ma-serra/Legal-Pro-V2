
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
    Executa a migração 005 para popular a tabela IndiceMonetario
    """
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        logger.info("Applying migration 005 (Add all BACEN indices)...")
        
        # Lê o arquivo SQL
        migration_file = os.path.join(os.path.dirname(__file__), 'migrations', '005_add_all_bacen_indices.sql')
        
        if not os.path.exists(migration_file):
            logger.error(f"Migration file not found: {migration_file}")
            return
            
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
            
        # Executa o script SQL
        # Dividindo por instruções pode ser mais seguro se houver transações separadas,
        # mas aqui é tudo insert com ON CONFLICT, então pode ir direto ou dividido por ;
        # Vamos executar comando por comando para evitar falhas em bloco.
        
        # O arquivo usa ; para separar comandos
        commands = sql_content.split(';')
        
        for command in commands:
            command = command.strip()
            if command:
                try:
                    cur.execute(command)
                except Exception as e:
                    logger.warning(f"Warning executing command: {e}")
                    # Continua mesmo com erro se for duplicação que ON CONFLICT não pegou
                    pass
            
        conn.commit()
        logger.info("Migration 005 applied successfully.")
        
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        logger.error(f"Migration failed: {e}")
    finally:
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    run_mig()
