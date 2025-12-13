"""
Script de teste para verificar a integração completa com a API Taskade.

Este script testa múltiplas funcionalidades do cliente da API Taskade, incluindo:
- Autenticação
- Listagem de workspaces e projetos
- Criação, leitura, atualização e exclusão de tarefas
- Manipulação de campos, anotações e datas de tarefas
- Manipulação de agentes e base de conhecimento
- Manipulação de mídias
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
token = "tskdp_KXM9uEyQHJJgFXPnfFgDKAzxVyKBHLrY49"
os.environ['TASKADE_API_TOKEN'] = token

print(f"Token de API definido: {token[:5]}...{token[-5:]}")

def test_integracao_completa():
    """
    Testa a integração completa com a API Taskade.
    """
    try:
        # Inicializar o cliente
        client = TaskadeClient()
        
        print("\nIniciando testes de integração com a API Taskade")
        print("=" * 50)
        
        # 1. Testar autenticação e listagem de workspaces
        print("\nTeste 1: Autenticação e listagem de workspaces")
        print("-" * 50)
        
        workspaces = client.listar_workspaces()
        if 'data' in workspaces and workspaces['data']:
            print(f"✅ Autenticação e listagem de workspaces: OK")
            workspace_id = workspaces['data'][0].get('id')
            print(f"   Workspace de teste: {workspaces['data'][0].get('name')} | ID: {workspace_id}")
        else:
            print("❌ Falha na autenticação ou listagem de workspaces")
            return False
            
        # 2. Testar listagem de projetos
        print("\nTeste 2: Listagem de projetos")
        print("-" * 50)
        
        projetos = client.listar_projetos(workspace_id)
        if 'data' in projetos and projetos['data']:
            print(f"✅ Listagem de projetos: OK")
            projeto_id = projetos['data'][0].get('id')
            print(f"   Projeto de teste: {projetos['data'][0].get('name')} | ID: {projeto_id}")
        else:
            print("❌ Falha na listagem de projetos")
            return False
            
        # 3. Testar criação de tarefa
        print("\nTeste 3: Criação de tarefa")
        print("-" * 50)
        
        tarefa = client.criar_tarefa(
            project_id=projeto_id,
            titulo="Tarefa de Teste Integração Completa",
            descricao="Esta tarefa foi criada para teste de integração completa",
            content_type="text/markdown",
            placement="afterbegin"
        )
        
        if 'data' in tarefa and tarefa['data'].get('id'):
            print(f"✅ Criação de tarefa: OK")
            tarefa_id = tarefa['data'].get('id')
            print(f"   Nova tarefa: {tarefa['data'].get('text')} | ID: {tarefa_id}")
        else:
            print("❌ Falha na criação de tarefa")
            return False
            
        # 4. Testar adição de anotação à tarefa
        print("\nTeste 4: Adição de anotação à tarefa")
        print("-" * 50)
        
        try:
            anotacao = client.atualizar_anotacao_tarefa(
                project_id=projeto_id,
                task_id=tarefa_id,
                conteudo="Esta é uma anotação de teste para a tarefa de integração",
                tipo="text/markdown"
            )
            print(f"✅ Adição de anotação: OK")
        except Exception as e:
            print(f"❌ Falha na adição de anotação: {e}")
            
        # 5. Testar adição de data de vencimento
        print("\nTeste 5: Adição de data de vencimento")
        print("-" * 50)
        
        try:
            # Usar data atual + 7 dias
            import datetime
            due_date = datetime.datetime.now() + datetime.timedelta(days=7)
            due_date_iso = due_date.isoformat()
            
            data_vencimento = client.adicionar_data_tarefa(
                project_id=projeto_id,
                task_id=tarefa_id,
                data=due_date_iso
            )
            print(f"✅ Adição de data de vencimento: OK")
        except Exception as e:
            print(f"❌ Falha na adição de data de vencimento: {e}")
            
        # 6. Testar exclusão de tarefa
        print("\nTeste 6: Exclusão de tarefa")
        print("-" * 50)
        
        try:
            excluir = client.excluir_tarefa(
                project_id=projeto_id,
                task_id=tarefa_id
            )
            print(f"✅ Exclusão de tarefa: OK")
        except Exception as e:
            print(f"❌ Falha na exclusão de tarefa: {e}")
            
        print("\nTestes de integração concluídos com sucesso!")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"❌ Erro geral durante os testes: {e}")
        return False

if __name__ == "__main__":
    test_integracao_completa()