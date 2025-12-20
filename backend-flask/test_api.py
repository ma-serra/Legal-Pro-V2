
import requests

try:
    response = requests.get(
        "https://legal-pro-saas.up.railway.app/api/processos",
        params={"page": 1, "per_page": 5},
        timeout=30
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:2000]}")
except Exception as e:
    print(f"Error: {e}")
