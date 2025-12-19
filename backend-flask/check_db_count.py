
import os
import sys
from flask import Flask
from models import db, Processo, ProcessoJuridico

# Adicionar diretório atual ao path
sys.path.append(os.getcwd())

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def check_counts():
    with app.app_context():
        try:
            count_processos = Processo.query.count()
            count_juridicos = ProcessoJuridico.query.count()
            print(f"SUCCESS: Database Connection OK")
            print(f"Total 'Processo' records: {count_processos}")
            print(f"Total 'ProcessoJuridico' records: {count_juridicos}")
        except Exception as e:
            print(f"ERROR: Database check failed: {e}")

if __name__ == "__main__":
    check_counts()
