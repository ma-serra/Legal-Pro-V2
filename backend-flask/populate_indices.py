
import logging
from datetime import date, timedelta
from app import app, db
from modules.atualizacao_monetaria.importador import ImportadorIndices

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def populate():
    with app.app_context():
        print("Iniciando importação de dados históricos (5 anos)...")
        # Forçar importação de 5 anos para todos os índices
        data_inicio = date.today() - timedelta(days=1825)
        resultados = ImportadorIndices.importar_todos_indices(data_inicio=data_inicio)
        
        print("\nResultados:")
        for indice, qtd in resultados.items():
            print(f"- {indice}: {qtd} registros importados")
            
        print("\nConcluído.")

if __name__ == "__main__":
    populate()
