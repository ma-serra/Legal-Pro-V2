
"""Test BCB Focus API with different filter approaches"""
import requests

EXPECTATIVAS_BASE = "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata"

def test_focus():
    print("Testando diferentes filtros para Focus API...\n")
    
    # Teste 1: Sem filtro (apenas top)
    print("1. Sem filtro:")
    url = f"{EXPECTATIVAS_BASE}/ExpectativasMercadoAnuais"
    params = {
        '$top': 5,
        '$format': 'json'
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            items = data.get('value', [])
            print(f"   Registros: {len(items)}")
            if items:
                print(f"   Indicadores disponíveis: {set(item.get('Indicador') for item in items)}")
                print(f"   Primeiro: {items[0]}")
        else:
            print(f"   Erro: {response.text[:200]}")
    except Exception as e:
        print(f"   Exceção: {e}")
    
    # Teste 2: Listar indicadores únicos
    print("\n2. Listando indicadores disponíveis:")
    params = {
        '$top': 100,
        '$format': 'json'
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            items = data.get('value', [])
            indicadores = set(item.get('Indicador') for item in items)
            print(f"   Indicadores encontrados: {indicadores}")
    except Exception as e:
        print(f"   Exceção: {e}")

if __name__ == "__main__":
    test_focus()
