
"""Test BCB Focus API directly"""
import requests

# Testar endpoint de expectativas Focus
EXPECTATIVAS_BASE = "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata"

def test_focus():
    indicadores = ['Selic', 'IPCA', 'PIB Total', 'Taxa de câmbio']
    
    for indicador in indicadores:
        print(f"\nTestando: {indicador}")
        
        # ExpectativasMercadoAnuais
        url = f"{EXPECTATIVAS_BASE}/ExpectativasMercadoAnuais"
        params = {
            '$filter': f"Indicador eq '{indicador}'",
            '$top': 5,
            '$format': 'json'
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('value', [])
                print(f"  Registros: {len(items)}")
                if items:
                    print(f"  Primeiro: {items[0]}")
            else:
                print(f"  Erro: {response.text[:200]}")
                
        except Exception as e:
            print(f"  Exceção: {e}")

if __name__ == "__main__":
    test_focus()
