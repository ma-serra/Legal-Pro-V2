"""
Script para configurar o token Taskade que funciona.
Este script atualiza as variáveis de ambiente para usar o token
e URL que confirmamos funcionar nos testes.
"""
import os
from dotenv import load_dotenv, set_key

# Carregar as variáveis de ambiente atuais
load_dotenv()

def update_env_token():
    """Atualiza o token Taskade nas variáveis de ambiente."""
    # Token que confirmamos funcionar
    working_token = "tskdp_eyJvuW18Wd6gfeSkSr2eCvuisUUZZHwsDR"
    
    # Caminho para o arquivo .env
    env_path = os.path.join(os.getcwd(), '.env')
    
    # Atualizar ou adicionar o token ao arquivo .env
    set_key(env_path, "TASKADE_API_TOKEN", working_token)
    print(f"Token Taskade atualizado em {env_path}")
    
    # Definir também para o ambiente atual
    os.environ["TASKADE_API_TOKEN"] = working_token
    print("Token definido para a sessão atual")
    
    return working_token

if __name__ == "__main__":
    token = update_env_token()
    print(f"Token configurado: {token[:5]}...{token[-5:]}")