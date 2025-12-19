
import os
import sys

# Set env var BEFORE importing main to ensure create_app picks it up
os.environ['DATABASE_URL'] = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"
os.environ['SESSION_SECRET'] = "debug_secret"

# Add current dir to sys.path
sys.path.append(os.getcwd())

try:
    from main import app, db
    from models import Processo, Advogado, Fase, Comarca
    from sqlalchemy import text
except Exception as e:
    print(f"Error importing main: {e}")
    sys.exit(1)

def debug():
    print("--- Starting Debug V3 ---")
    with app.app_context():
        try:
            # 1. Check DB Connection
            print("Checking DB connection...")
            result = db.session.execute(text('SELECT 1')).scalar()
            print(f"DB Connection OK: {result}")
            
            # 2. Check Tables
            print("Checking tables...")
            # Check if columns exist
            insp = db.inspect(db.engine)
            cols = [c['name'] for c in insp.get_columns('processos')]
            print(f"Columns in 'processos': {cols}")
            
            if 'advogado_id' not in cols:
                print("CRITICAL: Column 'advogado_id' MISSING in DB!")
            
            # 3. Check Data
            count = Processo.query.count()
            print(f"Total processos: {count}")
            
            if count > 0:
                p = Processo.query.first()
                print(f"Sample Processo: {p.id_processo}")
                print(f"Advogado ID: {p.advogado_id}")
                print(f"Fase ID: {p.fase_id}")
                
                # 4. Serialize
                print("Testing serialization...")
                d = p.to_dict()
                print("Serialization successful")
                print(d)
                
        except Exception as e:
            print(f"Debug Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug()
