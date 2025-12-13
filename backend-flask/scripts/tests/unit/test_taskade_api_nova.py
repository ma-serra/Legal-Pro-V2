"""
Script de teste para verificar a nova implementação de integração com a API Taskade.
"""
import os
import json
import logging
from dotenv import load_dotenv
from multiagent.integrations.taskade.client import TaskadeClient

# Configuração de logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Carregar variáveis de ambiente
load_dotenv()

# Usar o token mais recente
token = "tskdp_eyJvuW18Wd6gfeSkSr2eCvuisUUZZHwsDR"
os.environ['TASKADE_API_TOKEN'] = token

print(f"Token de API definido: {token[:5]}...{token[-5:]}")

# ID do workspace confirmado no teste anterior
WORKSPACE_ID = "HKbzTo8oHXGMw1va"
# ID de um projeto válido (Getting Started)
PROJECT_ID = "YiZzvBYEyThMdNRj"

def test_listar_workspaces():
    """Testa a listagem de workspaces."""
    try:
        client = TaskadeClient(api_token=token)
        workspaces = client.listar_workspaces()
        print("\nWorkspaces disponíveis:")
        print("-" * 50)
        if "data" in workspaces:
            for ws in workspaces["data"]:
                print(f"ID: {ws['id']} - Nome: {ws['name']}")
            return True
        else:
            print(f"Erro ou formato inesperado: {workspaces}")
            return False
    except Exception as e:
        print(f"Erro ao listar workspaces: {e}")
        return False

def test_criar_tarefa_workspace():
    """
    Testa a criação de uma tarefa em um projeto existente.
    """
    try:
        client = TaskadeClient(api_token=token)
        
        print(f"\nTestando criação de tarefa no projeto ID: {PROJECT_ID}")
        print("-" * 50)
        
        nova_tarefa = client.criar_tarefa(
            project_id=PROJECT_ID,  # Usando ID do projeto válido
            titulo="Tarefa de Teste com Nova Implementação",
            descricao="Esta tarefa foi criada para testar a nova implementação.",
            content_type="text/markdown",
            placement="afterbegin"
        )
        
        print(f"Resposta da criação de tarefa: {json.dumps(nova_tarefa, indent=2)}")
        
        if nova_tarefa.get('data'):
            print("✅ Tarefa criada com sucesso!")
            # Tentar adicionar uma data de vencimento se temos uma tarefa e um projeto
            if isinstance(nova_tarefa['data'], list) and len(nova_tarefa['data']) > 0:
                task_id = nova_tarefa['data'][0].get('id')
                if task_id:
                    # Tentativa de adicionar data de vencimento
                    try:
                        data_resp = client.adicionar_data_tarefa(
                            project_id=PROJECT_ID,
                            task_id=task_id,
                            data_string="2025-06-01T10:00:00"
                        )
                        print(f"✅ Data adicionada: {data_resp}")
                    except Exception as date_err:
                        print(f"❌ Erro ao adicionar data: {date_err}")
            return True
        else:
            print("❌ Falha ao criar a tarefa. Resposta em formato inesperado.")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao criar tarefa: {e}")
        return False

if __name__ == "__main__":
    print("=== Teste de Integração com Taskade API ===")
    
    print("\n1. Testando listagem de workspaces...")
    if test_listar_workspaces():
        print("✅ Teste de listagem de workspaces bem-sucedido!")
    else:
        print("❌ Teste de listagem de workspaces falhou.")
    
    print("\n2. Testando criação de tarefa em workspace...")
    if test_criar_tarefa_workspace():
        print("✅ Teste de criação de tarefa com nova implementação bem-sucedido!")
    else:
        print("❌ Teste de criação de tarefa com nova implementação falhou.")
    
    print("\nTestes concluídos!")