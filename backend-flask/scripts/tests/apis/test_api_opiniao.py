"""
Script para testar a API de segunda opinião.
"""
import json
import requests

# URL da API
API_URL = "http://localhost:5000/api/juridico/segunda-opiniao"

# Dados de teste
payload = {
    "analise_original": "Este é um contrato de trabalho com cláusulas de não concorrência e confidencialidade.",
    "area_juridica": "trabalhista",
    "contexto": "Teste de API direta"
}

# Headers
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Credenciais (se necessário)
# Para solicitar uma segunda opinião, você precisa estar logado no sistema

# Função para tentar fazer a requisição
def test_api_segunda_opiniao():
    """Faz uma requisição de teste para a API."""
    print("Enviando requisição para a API de segunda opinião...")
    
    try:
        with open('cookie.txt', 'r') as f:
            cookie = f.read().strip()
            headers['Cookie'] = cookie
    except:
        print("Arquivo cookie.txt não encontrado. Execute este script após fazer login.")
        return
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        print(f"Status code: {response.status_code}")
        print(f"Headers da resposta: {dict(response.headers)}")
        
        try:
            json_response = response.json()
            print("\nResposta JSON:")
            print(json.dumps(json_response, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"\nErro ao converter resposta para JSON: {e}")
            print("\nConteúdo da resposta:")
            print(response.text[:300] + "..." if len(response.text) > 300 else response.text)
    
    except Exception as e:
        print(f"Erro ao fazer requisição: {e}")

if __name__ == "__main__":
    test_api_segunda_opiniao()