
from main import create_app, db
from models import Processo, ProcessoTributario
from sqlalchemy import func

import os
os.environ['DATABASE_URL'] = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"
app = create_app()
# app.config['SQLALCHEMY_DATABASE_URI'] set by create_app from env
print(f"DEBUG URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
with app.app_context():
    try:
        print("Querying Processo...")
        count_proc = Processo.query.count()
        print(f"Total Processos: {count_proc}")
    except Exception as e:
        print(f"Error querying Processo: {e}")

    try:
        print("Querying ProcessoTributario...")
        count_trib = ProcessoTributario.query.count()
        print(f"Total Tributarios: {count_trib}")
    except Exception as e:
        print(f"Error querying ProcessoTributario: {e}")
