
import os
import sys
from flask import Flask
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar diretório atual ao path
sys.path.append(os.getcwd())

from models import db, Processo, ProcessoJuridico, Advogado, Fase, Comarca

app = Flask(__name__)
# Tentar pegar DATABASE_URL, fallback para sqlite se não existir (apenas para teste, mas esperamos postgres)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def check_counts():
    if not app.config['SQLALCHEMY_DATABASE_URI']:
        print("ERROR: DATABASE_URL not found in environment variables.")
        return

    with app.app_context():
        try:
            print(f"Connecting to: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[1] if '@' in app.config['SQLALCHEMY_DATABASE_URI'] else 'LOCAL SQLITE'}")
            
            count_processos = Processo.query.count()
            count_juridicos = ProcessoJuridico.query.count()
            count_advogados = Advogado.query.count()
            count_fases = Fase.query.count()
            count_comarcas = Comarca.query.count()
            
            print(f"SUCCESS: Database Connection OK")
            print(f"Total 'Processo' records: {count_processos}")
            print(f"Total 'ProcessoJuridico' records: {count_juridicos}")
            print(f"Total 'Advogado' records: {count_advogados}")
            print(f"Total 'Fase' records: {count_fases}")
            print(f"Total 'Comarca' records: {count_comarcas}")
            
        except Exception as e:
            print(f"ERROR: Database check failed: {e}")

if __name__ == "__main__":
    check_counts()
