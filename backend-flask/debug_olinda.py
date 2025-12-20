
import requests
import json

def check_olinda():
    base = "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata"
    
    # 1. Tentar listar metadados ou endpoints se possível (difícil em OData básico)
    # Mas vamos testar endpoints conhecidos
    endpoints = [
        "ExpectativasMercadoAnuais",
        "ExpectativasMercadoMensais",
        "ExpectativasMercadoTop5Anuais"
    ]
    
    for ep in endpoints:
        print(f"\n--- Checking {ep} ---")
        url = f"{base}/{ep}"
        
        # Testar sem filtro primeiro, top 1
        params = {"$top": 1, "$format": "json"}
        try:
            r = requests.get(url, params=params, timeout=10)
            print(f"Status: {r.status_code}")
            if r.status_code == 200:
                print("Exemplo de dado:")
                print(r.json())
            else:
                print(r.text[:200])
                
            # Testar com filtro Selic
            print(f"Testing filter Indicador='Selic' on {ep}...")
            params_filter = {
                "$filter": "Indicador eq 'Selic'",
                "$top": 1,
                "$orderby": "Data desc",
                "$format": "json"
            }
            r2 = requests.get(url, params=params_filter, timeout=10)
            if r2.status_code == 200:
                print(f"Found Selic! Count: {len(r2.json()['value'])}")
            else:
                print(f"Filter failed: {r2.status_code}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_olinda()
