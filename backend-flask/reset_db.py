
import sqlalchemy
from sqlalchemy import create_engine, text

# Hardcoded for reliability
DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"

def reset_database():
    try:
        engine = create_engine(DB_URL)
        with engine.connect() as conn:
            print("Cleaning up database tables...")
            
            # Truncate tables with cascade to handle foreign keys
            # We target the main process tables
            tables_to_truncate = [
                "processo_tributario",
                "processo_trabalhista", 
                "processo_civel",
                "processos" # The main table
            ]
            
            # Disable triggers/constraints temporarily if needed, but CASCADE should handle FKs.
            # Using RESTART IDENTITY to reset auto-increment counters.
            
            # Note: We need to commit explicitely with SQLAlchemy text execution
            conn.execution_options(isolation_level="AUTOCOMMIT")
            
            for table in tables_to_truncate:
                # Check existance
                check = text(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}');")
                if conn.execute(check).scalar():
                    print(f"Truncating {table}...")
                    conn.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;"))
                else:
                    print(f"Table {table} not found, skipping.")
                    
            print("Database cleanup completed successfully.")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    reset_database()
