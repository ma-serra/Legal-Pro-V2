
import os
import sys
import logging

# Configuração
DEFAULT_DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"
os.environ['DATABASE_URL'] = DEFAULT_DB_URL

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import create_app, db
from models_saas import Tenancy, Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check():
    try:
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = DEFAULT_DB_URL
    except Exception as e:
        logger.error(f"App Create Error: {e}")
        return

    with app.app_context():
        try:
            print("Checking Tenancy...")
            t = Tenancy.query.filter_by(slug='legal-pro-hub').first()
            if t:
                print(f"✅ Tenancy found: {t.id} - {t.name}")
                
                print("Checking Clients...")
                clients = Client.query.filter_by(tenancy_id=t.id).limit(5).all()
                for c in clients:
                    print(f"  - Client: {c.id} - {c.name}")
            else:
                print("❌ Tenancy NOT found. Attempting create...")
                t = Tenancy(name="Legal Pro Hub Debug", slug="legal-pro-hub", domain="debug.local")
                db.session.add(t)
                db.session.commit()
                print(f"✅ Tenancy created: {t.id}")

        except Exception as e:
            print(f"❌ Database Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    check()
