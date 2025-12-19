
import os
import sys
import pandas as pd
from datetime import datetime
import uuid as uuid_lib

# Set env var FIRST
os.environ['DATABASE_URL'] = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"

# Setup path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup file logging to avoid encoding issues
LOG_FILE = "etl_output.log"
def log(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()}: {msg}\n")
    # Also try print but catch errors
    try:
        print(msg)
    except:
        pass

from main import create_app, db
from models import Processo

def run():
    # Clear log file
    open(LOG_FILE, "w", encoding="utf-8").close()
    
    log("Initializing Simple ETL V3...")
    app = create_app()
    
    excel_path = r"D:\Legal Pro Hub\Tabela_Processos_ETL.xlsx"
    if not os.path.exists(excel_path):
        log(f"File not found: {excel_path}")
        return

    log("Reading Excel...")
    df = pd.read_excel(excel_path)
    log(f"Rows: {len(df)}")
    log(f"Columns: {list(df.columns)}")

    with app.app_context():
        log("Entering App Context...")
        
        count = 0
        errors = 0
        skipped = 0
        
        log("Starting Loop...")
        for index, row in df.iterrows():
            try:
                # Get CNJ
                cnj = row.get('numero_cnj')
                if pd.isna(cnj) or str(cnj).strip() == '' or str(cnj) == 'nan':
                    skipped += 1
                    continue
                    
                cnj = str(cnj).strip()

                # Check existing
                exists = Processo.query.filter_by(numero_cnj=cnj).first()
                if exists:
                    skipped += 1
                    continue
                    
                p = Processo()
                p.numero_cnj = cnj
                p.pasta = f"PROC-{index}"
                p.tenant_id = 1
                p.status_id = 1
                p.natureza_id = 5
                p.data_criacao = datetime.utcnow()
                p.uuid = uuid_lib.uuid4()
                p.titulo = f"Processo {cnj}"
                
                db.session.add(p)
                db.session.commit()  # Commit each one
                
                count += 1
                if count <= 5 or count % 200 == 0:
                    log(f"Imported {count}: {cnj}")
                    
            except Exception as e:
                db.session.rollback()
                errors += 1
                log(f"Row {index} error: {str(e)[:200]}")
                if errors > 20:
                    log("Too many errors, stopping.")
                    break
        
        log(f"Finished. Imported {count}, Skipped {skipped}, Errors {errors}")

if __name__ == "__main__":
    run()
