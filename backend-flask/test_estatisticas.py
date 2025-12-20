
import requests

try:
    response = requests.get(
        "https://legal-pro-saas.up.railway.app/api/processos/estatisticas",
        timeout=30
    )
    print(f"Status: {response.status_code}")
    import json
    data = response.json()
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error: {e}")
