
import os
import sqlalchemy
from sqlalchemy import create_engine, text

# Hardcoded for verification reliability
DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"

def verify_count():
    try:
        engine = create_engine(DB_URL)
        with engine.connect() as conn:
            # Check table existence first (in case it wasn't created)
            # This query works on Postgres to check if table exists
            check_table = text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'processos');")
            exists = conn.execute(check_table).scalar()
            
            if not exists:
                print("TABLE_STATUS: Processos table does NOT exist.")
                return

            result = conn.execute(text("SELECT COUNT(*) FROM processos"))
            count = result.scalar()
            print(f"REAL_COUNT_PROCESSO: {count}")
            
            # Check ProcessoTributario
            result_trib = conn.execute(text("SELECT COUNT(*) FROM processo_tributario"))
            count_trib = result_trib.scalar()
            print(f"REAL_COUNT_TRIBUTARIO: {count_trib}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    verify_count()
