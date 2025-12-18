
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
        
        logger.info("Applying migration 003 (Tributario fix)...")
        
        sqls = [
            "ALTER TABLE processo_tributario ADD COLUMN IF NOT EXISTS processo_id INTEGER;",
            "ALTER TABLE processo_tributario ADD COLUMN IF NOT EXISTS valor_principal NUMERIC(18,2);",
            "ALTER TABLE processo_tributario ADD COLUMN IF NOT EXISTS numero_cda VARCHAR(100);",
            "ALTER TABLE processo_tributario ADD COLUMN IF NOT EXISTS numero_aiim VARCHAR(100);",
            # Optional FK check (might fail if data exists, so skip strict FK constraint creation for now or make it lazy)
            # "DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_proc_trib_proc') THEN ALTER TABLE processo_tributario ADD CONSTRAINT fk_proc_trib_proc FOREIGN KEY (processo_id) REFERENCES processos(id_processo); END IF; END $$;"
        ]
        
        for sql in sqls:
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
