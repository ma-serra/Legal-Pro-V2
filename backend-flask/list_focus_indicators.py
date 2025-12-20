
"""Descobrir nomes exatos dos indicadores disponíveis na API Focus BCB"""
import requests

EXPECTATIVAS_BASE = "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata"

def listar_indicadores():
    print("Listando todos os indicadores da API Focus...\n")
    
    endpoints = [
        'ExpectativasMercadoAnuais',
        'ExpectativasMercadoTop5Anuais',
        'ExpectativasMercadoMensais',
        'ExpectativasMercadoTrimestrais'
    ]
    
    todos_indicadores = set()
    
    for endpoint in endpoints:
        url = f"{EXPECTATIVAS_BASE}/{endpoint}"
        params = {
            '$top': 100,
            '$format': 'json'
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                items = data.get('value', [])
                indicadores = set(item.get('Indicador') for item in items if item.get('Indicador'))
                todos_indicadores.update(indicadores)
                print(f"{endpoint}: {len(indicadores)} indicadores")
                for ind in sorted(indicadores):
                    print(f"   - {ind}")
                print()
        except Exception as e:
            print(f"{endpoint}: Erro - {e}")
    
    print(f"\n=== TODOS OS INDICADORES ÚNICOS ({len(todos_indicadores)}) ===")
    for ind in sorted(todos_indicadores):
        print(f"  {ind}")

if __name__ == "__main__":
    listar_indicadores()
