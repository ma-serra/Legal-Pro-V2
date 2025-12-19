
import sys
import os
import traceback

sys.path.append(os.getcwd())

def test_imports():
    os.environ['DATABASE_URL'] = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"
    try:
        print("Attempting to create app...")
        from main import create_app
        app = create_app()
        print("App created. Checking models...")
        with app.app_context():
            from models import AgenteJuridico, AnaliseDocumento, SegundaOpiniao, AnaliseComparativa
            from models import Processo, ProcessoTributario, ProcessoTrabalhista, ProcessoCivel
            try:
                import models_processos
                print("Imported models_processos.")
                from models_saas import Client, Tenancy
                print("Imported models_saas.")
            except Exception as e:
                print(f"Failed extra imports: {e}")
            print("Models imported successfully. Attempting create_all...")
            from main import db
            db.create_all()
            print("Create_all success.")
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    test_imports()
