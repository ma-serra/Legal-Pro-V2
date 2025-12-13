"""
Teste simples e direto da API Taskade, sem usar o cliente completo.
Usado para isolar problemas de autenticação ou acesso à API.
"""
import os
import json
import requests
import logging
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Usar o token mais recente (verificar qual funciona)
tokens = [
    "tskdp_eyJvuW18Wd6gfeSkSr2eCvuisUUZZHwsDR",  # Token 1
    "tskdp_KXM9uEyQHJJgFXPnfFgDKAzxVyKBHLrY49",  # Token 2
    "tskdp_vw49t6cH3DGmEHTp7VEz4JeGwV6vbQHd5z"   # Token 3 (atual no ambiente)
]

# Definir URLs base
base_urls = [
    "https://www.taskade.com/api/v1",
    "https://api.taskade.com/v1"
]

# Métodos de autenticação
auth_methods = [
    {"type": "Bearer", "header": lambda token: {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}},
    {"type": "X-Auth", "header": lambda token: {"X-Auth-Token": token, "Content-Type": "application/json"}},
    {"type": "URL Param", "header": lambda token: {"Content-Type": "application/json"}, "param": lambda token: {"api_key": token}}
]

# Endpoints para teste
endpoints = [
    "/projects",
    "/workspaces",
    "/user/me",
    "/me/projects",
    "/me"
]

def test_combinacoes():
    """Testa todas as combinações possíveis de token, URL e método de autenticação."""
    resultados_sucesso = []
    
    for token in tokens:
        for base_url in base_urls:
            for auth_method in auth_methods:
                for endpoint in endpoints:
                    method_type = auth_method["type"]
                    headers = auth_method["header"](token)
                    
                    params = None
                    if "param" in auth_method:
                        params = auth_method["param"](token)
                    
                    url = f"{base_url}{endpoint}"
                    
                    try:
                        print(f"\nTestando: {url}")
                        print(f"Token: {token[:5]}...{token[-5:]}")
                        print(f"Método de autenticação: {method_type}")
                        
                        response = requests.get(
                            url=url,
                            headers=headers,
                            params=params
                        )
                        
                        status = response.status_code
                        print(f"Status: {status}")
                        
                        if status < 400:  # Sucesso
                            print("SUCESSO!")
                            try:
                                data = response.json()
                                print(f"Resposta: {json.dumps(data, indent=2)[:500]}...")
                                resultados_sucesso.append({
                                    "token": token,
                                    "base_url": base_url,
                                    "auth_method": method_type,
                                    "endpoint": endpoint,
                                    "status": status,
                                    "response": data
                                })
                            except Exception:
                                print(f"Resposta (não JSON): {response.text[:200]}...")
                        else:
                            print(f"Erro: {status}")
                            print(f"Resposta: {response.text[:200]}...")
                    
                    except Exception as e:
                        print(f"Erro ao fazer requisição: {e}")
    
    # Resumo dos resultados bem-sucedidos
    print("\n==== RESUMO DOS RESULTADOS BEM-SUCEDIDOS ====")
    if resultados_sucesso:
        for idx, resultado in enumerate(resultados_sucesso, 1):
            print(f"\n{idx}. Combinação bem-sucedida:")
            print(f"   Token: {resultado['token'][:5]}...{resultado['token'][-5:]}")
            print(f"   URL Base: {resultado['base_url']}")
            print(f"   Método de Autenticação: {resultado['auth_method']}")
            print(f"   Endpoint: {resultado['endpoint']}")
            print(f"   Status: {resultado['status']}")
    else:
        print("Nenhuma combinação bem-sucedida encontrada.")

def test_oauth_workflow():
    """Testa o fluxo OAuth 2.0"""
    client_id = os.environ.get("TASKADE_CLIENT_ID")
    client_secret = os.environ.get("TASKADE_CLIENT_SECRET")
    redirect_uri = os.environ.get("BASE_URL") + "/taskade/oauth/callback" if os.environ.get("BASE_URL") else "http://localhost:5000/taskade/oauth/callback"
    
    if not client_id or not client_secret:
        print("Credenciais OAuth não encontradas nas variáveis de ambiente.")
        print("TASKADE_CLIENT_ID e TASKADE_CLIENT_SECRET são necessários.")
        return
    
    print(f"\n==== TESTE DO FLUXO OAUTH ====")
    print(f"Client ID: {client_id}")
    print(f"Client Secret: {client_secret[:3]}...{client_secret[-3:]}")
    print(f"Redirect URI: {redirect_uri}")
    
    # Etapa 1: Gerar URL de autorização
    auth_url = "https://www.taskade.com/oauth/authorize"
    auth_params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "user.read projects.read projects.write tasks.read tasks.write"
    }
    
    auth_request_url = auth_url + "?" + "&".join([f"{k}={v}" for k, v in auth_params.items()])
    print(f"\nURL de Autorização:")
    print(auth_request_url)
    
    # Etapa 2: Trocar código por token (simulação)
    print("\nPara concluir o fluxo OAuth, o usuário precisa acessar a URL acima,")
    print("autorizar o aplicativo, e você receberá o código no redirect_uri.")
    print("Depois, você pode trocar o código por um token de acesso usando:")
    
    token_url = "https://www.taskade.com/oauth/token"
    token_payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "authorization_code",
        "code": "<CODE>",  # Placeholder
        "redirect_uri": redirect_uri
    }
    
    print(f"\nPOST {token_url}")
    print(f"Payload: {json.dumps(token_payload, indent=2)}")

if __name__ == "__main__":
    print("=== Teste Direto da API Taskade ===")
    
    test_combinacoes()
    print("\n")
    test_oauth_workflow()
    
    print("\nTestes concluídos!")