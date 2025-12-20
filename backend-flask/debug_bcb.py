
import requests
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_tr_sgs():
    print("\n--- Testando TR (SGS) ---")
    # Código TR = 226
    url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.226/dados?formato=json"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data and len(data) > 0:
            print(f"✅ TR (226) retornou {len(data)} registros.")
            print(f"Último: {data[-1]}")
        else:
            print("❌ TR (226) retornou lista vazia ou inválida.")
    except Exception as e:
        print(f"❌ Erro ao buscar TR: {e}")

def test_focus_olinda():
    print("\n--- Testando Focus (Olinda) ---")
    base_url = "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata"
    
    indicadores = ['Selic', 'IPCA', 'PIB Total', 'Câmbio']
    
    for ind in indicadores:
        print(f"\nTestando Indicador: {ind}")
        # Tentar buscar últimos registros ordenados por Data
        url = f"{base_url}/ExpectativasMercadoAnuais"
        params = {
            '$filter': f"Indicador eq '{ind}'",
            '$top': 5,
            '$orderby': 'Data desc',
            '$format': 'json'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            values = data.get('value', [])
            
            if values:
                print(f"✅ {ind}: Encontrados {len(values)} registros.")
                print(f"Exemplo: {values[0]}")
            else:
                print(f"❌ {ind}: Nenhum registro encontrado com filtro exato.")
                
                # Tentar listar indicadores disponíveis (se falhar)
                if ind == 'Selic': # Só faz uma vez
                    print("Tentando descobrir indicadores disponíveis...")
                    # Não há endpoint direto de 'lista de indicadores' fácil no OData sem varrer, 
                    # mas vamos tentar sem filtro
                    params_all = {'$top': 1, '$format': 'json'}
                    resp_all = requests.get(url, params=params_all)
                    print(f"Amostra geral: {resp_all.json()}")

        except Exception as e:
            print(f"❌ Erro na requisição Olinda: {e}")

if __name__ == "__main__":
    test_tr_sgs()
    test_focus_olinda()
