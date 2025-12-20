
import requests

try:
    response = requests.get(
        "https://legal-pro-saas.up.railway.app/api/processos",
        params={"page": 1, "per_page": 5},
        timeout=30
    )
    with open("error_response.txt", "w", encoding="utf-8") as f:
        f.write(f"Status: {response.status_code}\n\n")
        f.write(response.text)
    print("Response saved to error_response.txt")
except Exception as e:
    print(f"Error: {e}")
