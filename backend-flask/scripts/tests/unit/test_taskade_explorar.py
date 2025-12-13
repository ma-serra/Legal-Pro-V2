"""
Script para explorar a API Taskade com mais detalhes.
"""
import os
import logging
import json
from dotenv import load_dotenv
from multiagent.integrations.taskade.client import TaskadeClient
import requests

# Configuração de logging
logging.basicConfig(level=logging.DEBUG, 
                  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Carregar variáveis de ambiente
load_dotenv()

# Usar o token diretamente (como sabemos que funciona)
token = "tskdp_VBAA9yNVGf5L4RThC28x5dm7iVgE63srH6"
os.environ['TASKADE_API_TOKEN'] = token

print(f"Token de API definido: {token[:5]}...{token[-5:]}")

# ID do workspace e projeto hardcoded para o teste
WORKSPACE_ID = "HKbzTo8oHXGMw1va"

def explore_api():
    """
    Explora diferentes endpoints da API para entender a estrutura do Taskade.
    """
    client = TaskadeClient()
    
    # Obter workspaces
    print("\n1. Listando workspaces:")
    print("-" * 50)
    workspaces = client.listar_workspaces()
    print(f"Resposta: {json.dumps(workspaces, indent=2)}")
    
    # Obter detalhes do workspace
    print("\n2. Obtendo detalhes do workspace:")
    print("-" * 50)
    try:
        workspace_details = client._request("GET", f"/workspaces/{WORKSPACE_ID}")
        print(f"Detalhes do workspace: {json.dumps(workspace_details, indent=2)}")
    except Exception as e:
        print(f"Erro ao obter detalhes do workspace: {e}")
    
    # Listar pastas (folders)
    print("\n3. Listando pastas (folders) do workspace:")
    print("-" * 50)
    try:
        folders = client._request("GET", f"/workspaces/{WORKSPACE_ID}/folders")
        print(f"Pastas: {json.dumps(folders, indent=2)}")
    except Exception as e:
        print(f"Erro ao listar pastas: {e}")
    
    # Tentar listar tarefas para compreender estrutura
    print("\n4. Tentando listar tarefas para entender a estrutura:")
    print("-" * 50)
    try:
        tasks = client._request("GET", f"/projects/{WORKSPACE_ID}/tasks")
        print(f"Tarefas: {json.dumps(tasks, indent=2)}")
    except Exception as e:
        print(f"Erro ao listar tarefas: {e}")
    
    print("\n5. Explorando documentação da API:")
    print("-" * 50)
    try:
        # Alguns serviços têm endpoint para documentação
        api_info = requests.get("https://www.taskade.com/api")
        if api_info.status_code == 200:
            print(f"Informações da API: {api_info.text[:500]}...")
        else:
            print(f"Não foi possível obter documentação: {api_info.status_code}")
    except Exception as e:
        print(f"Erro ao obter documentação: {e}")
        
    # Ver se a API suporta criar um bloco (item/task) em um projeto
    print("\n6. Testando endpoint alternativo para criar uma tarefa:")
    print("-" * 50)
    try:
        # Tentar outro formato de requisição com base na estrutura da resposta
        data = {
            "name": "Teste Item via API",
            "completed": False
        }
        response = client._request("POST", f"/workspaces/{WORKSPACE_ID}/blocks", data=data)
        print(f"Resposta da criação de bloco: {json.dumps(response, indent=2)}")
    except Exception as e:
        print(f"Erro ao criar bloco: {e}")
    
    print("\nExploração concluída")

if __name__ == "__main__":
    explore_api()