"""
Script de teste para verificar a criação de tarefas na API Taskade.
"""
import os
import logging
from dotenv import load_dotenv
from multiagent.integrations.taskade.client import TaskadeClient

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
# Obtido do teste anterior
WORKSPACE_ID = "HKbzTo8oHXGMw1va"
PROJECT_ID = "HKbzTo8oHXGMw1va"  # Mesmo ID que o workspace (Home folder)

def test_criar_tarefa():
    """
    Testa especificamente a criação de uma tarefa no Taskade.
    """
    try:
        # Inicializar o cliente
        client = TaskadeClient()
        
        print(f"\nTestando criação de tarefa no projeto ID: {PROJECT_ID}")
        print("-" * 50)
        
        nova_tarefa = client.criar_tarefa(
            project_id=PROJECT_ID,
            titulo="Tarefa de Teste via API",
            descricao="Esta tarefa foi criada automaticamente pelo sistema multi-agente para testar a integração com a API Taskade.",
            content_type="text/markdown",
            placement="afterbegin"
        )
        
        print(f"Resposta da criação de tarefa: {nova_tarefa}")
        
        if nova_tarefa.get('data') and nova_tarefa['data'].get('id'):
            print(f"✅ Tarefa criada com sucesso! ID: {nova_tarefa['data']['id']}")
            return True
        else:
            print("❌ Falha ao criar a tarefa. Resposta em formato inesperado.")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao criar tarefa: {e}")
        return False

if __name__ == "__main__":
    test_criar_tarefa()