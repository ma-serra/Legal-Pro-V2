
import os
import psycopg2
import logging

DEFAULT_DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"
DB_URL = os.environ.get('DATABASE_URL', DEFAULT_DB_URL)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_mig():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        logger.info("Applying migration 004 (Add filters tables)...")
        
        # Read file
        with open(r'd:\Legal Pro Hub\backend-flask\migrations\004_add_filters_tables.sql', 'r', encoding='utf-8') as f:
            sql = f.read()
            
        cur.execute(sql)
        conn.commit()
        logger.info("Migration successful.")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Migration failed: {e}")
    finally:
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    run_mig()
