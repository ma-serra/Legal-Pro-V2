
import os
import sys

# Add path to find main.py
sys.path.append(os.getcwd())

from main import create_app, db
from models import Processo, ProcessoTributario


def check_count():
    # Set env var before creating app
    os.environ['DATABASE_URL'] = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"
    
    app = create_app()
    
    with app.app_context():
        try:
            total = Processo.query.count()
            tributarios = ProcessoTributario.query.count()
            print(f"VERIFICATION_RESULT: Total Processos: {total}")
            print(f"VERIFICATION_RESULT: Total Tributarios: {tributarios}")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    check_count()
