
"""Testar nomes específicos de indicadores"""
import requests

EXPECTATIVAS_BASE = "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata"

def test_indicador(indicador):
    url = f"{EXPECTATIVAS_BASE}/ExpectativasMercadoAnuais"
    params = {
        '$filter': f"Indicador eq '{indicador}'",
        '$top': 3,
        '$format': 'json'
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            items = data.get('value', [])
            return len(items), items[0] if items else None
        return 0, f"HTTP {response.status_code}"
    except Exception as e:
        return 0, str(e)

# Testar vários nomes possíveis
indicadores_teste = [
    'Selic',
    'Taxa Selic',
    'Meta para taxa Selic',
    'Meta para a taxa Selic',
    'IPCA',
    'PIB Total',
    'PIB',
    'Câmbio',
    'Taxa de câmbio'
]

print("Testando indicadores da API Focus:\n")
for ind in indicadores_teste:
    count, resultado = test_indicador(ind)
    status = "✅" if count > 0 else "❌"
    print(f"{status} '{ind}': {count} registros")
    if count > 0 and isinstance(resultado, dict):
        print(f"   Exemplo: media={resultado.get('Media')}, data={resultado.get('Data')}")
