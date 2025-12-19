
import sys
import os

# Set environment variables
os.environ['DATABASE_URL'] = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from main import create_app, db
    app = create_app()
    with app.app_context():
        from models import (
            Processo, 
            ProcessoTributario, 
            ProcessoTrabalhista, 
            ProcessoCivel
        )
        # Models SaaS
        from models_saas import Client, Tenancy
        
        # Imports de models_processos SOMENTE para tabelas que NÃO estão em models.py
        # Tributo e TeseTributaria devem vir de models_processos
        try:
            from models_processos import Tributo, TeseTributaria
        except ImportError:
            # Fallback ou definição dummy se falhar, mas deve existir
            print("WARNING: Could not import Tributo/TeseTributaria from models_processos")

        print("Imported ALL models successfully")
except Exception as e:
    import traceback
    traceback.print_exc()
