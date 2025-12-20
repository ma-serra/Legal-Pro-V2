
import os
import psycopg2
import logging

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"
DB_URL = os.environ.get('DATABASE_URL', DEFAULT_DB_URL)

def check():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        rows = cur.fetchall()
        
        tables = [r[0] for r in rows]
        print("Existing tables:", tables)
        
        required = ['processos', 'processo_tributario', 'processo_civel', 'processo_trabalhista', 'client', 'tenancy']
        for r in required:
            if r in tables:
                print(f"✅ {r} exists")
            else:
                print(f"❌ {r} MISSING")
                
    except Exception as e:
        print(e)
    finally:
        if 'conn' in locals(): conn.close()
        
if __name__ == "__main__":
    check()
