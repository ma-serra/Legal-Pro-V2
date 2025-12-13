"""
Script de teste para verificar a integração com a API Taskade.
"""
import os
import sys
import logging
from dotenv import load_dotenv
from multiagent.integrations.taskade.client import TaskadeClient

# Configuração de logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Carregar variáveis de ambiente
load_dotenv()

# Usar o novo token e credenciais diretamente
token = "tskdp_KXM9uEyQHJJgFXPnfFgDKAzxVyKBHLrY49"
client_id = "m6LEQMb6eW21nsko"
client_secret = "CP7Zbh7UhHZ7fXqP"

# Configurar variáveis de ambiente
# A autenticação OAuth2 apresentou erro 500, usando token de API
os.environ['TASKADE_API_TOKEN'] = token
os.environ['TASKADE_CLIENT_ID'] = client_id
os.environ['TASKADE_CLIENT_SECRET'] = client_secret

print(f"Token de API definido: {token[:5]}...{token[-5:]}")
print(f"Comprimento do token: {len(token)}")
print("Mantendo Client ID/Secret para uso futuro (OAuth2 falhou com erro 500)")
print(f"Client ID definido: {client_id}")
print(f"Client Secret definido: {client_secret[:5]}...")

def test_taskade_api():
    """
    Testa a conexão com a API da Taskade, lista os workspaces disponíveis e, em seguida,
    tenta criar uma nova tarefa em um workspace específico.
    """
    try:
        # Inicializar o cliente
        client = TaskadeClient()
        
        print("\nTestando acesso à API da Taskade:")
        print("-" * 50)
        
        # Abordagem 1: Testa com os formatos de cabeçalho padrão (o cliente já tentará os dois formatos)
        try:
            print("Método 1: Usando cabeçalhos de autenticação...")
            workspaces = client.listar_workspaces()
            print("Sucesso! Usando cabeçalhos de autenticação.")
        except Exception as e:
            print(f"Falha no método 1: {e}")
            
            # Abordagem 2: Tenta fazer uma requisição direta usando token como parâmetro
            print("\nMétodo 2: Usando token como parâmetro de URL...")
            import requests
            
            token = os.getenv('TASKADE_API_TOKEN')
            url = f"https://api.taskade.com/v1/workspaces?token={token}"
            
            try:
                headers = {"Content-Type": "application/json"}
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                workspaces = response.json()
                print("Sucesso! Usando token como parâmetro de URL.")
            except Exception as e2:
                print(f"Falha no método 2: {e2}")
                print("\nTodas as tentativas de autenticação falharam.")
                print("Verifique se o token da API está correto e tem as permissões necessárias.")
                return False
                
        # Se chegou aqui, conseguiu listar workspaces
        print("\nConexão com a API Taskade estabelecida com sucesso!")
        print("\nWorkspaces disponíveis:")
        print("-" * 50)
        
        # Verificar se há workspaces retornados
        if 'data' in workspaces and workspaces['data']:
            for ws in workspaces.get("data", []):
                print(f"Workspace: {ws.get('name')} | ID: {ws.get('id')}")
                
                # Para o primeiro workspace, listar projetos como exemplo
                if ws == workspaces["data"][0]:
                    try:
                        print(f"\nTentando listar projetos do workspace: {ws.get('name')}")
                        projetos = client.listar_projetos(ws.get('id'))
                        print(f"Resposta: {projetos}")
                        
                        if 'data' in projetos:
                            print("\nProjetos no workspace:", ws.get('name'))
                            for projeto in projetos.get("data", []):
                                print(f"  - {projeto.get('name')} | ID: {projeto.get('id')}")
                        else:
                            print("Formato de resposta diferente do esperado:")
                            print(projetos)
                    except Exception as e:
                        print(f"Erro ao listar projetos: {e}")
        else:
            print("Nenhum workspace encontrado na resposta:")
            print(workspaces)
        
        print("-" * 50)

        # Testar a criação de uma nova tarefa
        try:
            print("\nTestando a criação de uma nova tarefa...")
            
            # Procurar um projeto válido para criar a tarefa
            projeto_id = None
            workspace_id = None
            
            if 'data' in workspaces and workspaces['data']:
                workspace_id = workspaces['data'][0].get('id')
                
                if workspace_id:
                    projetos = client.listar_projetos(workspace_id)
                    if 'data' in projetos and projetos['data']:
                        projeto_id = projetos['data'][0].get('id')
            
            # Caso alternativo se a resposta estiver no formato diferente
            if not projeto_id and 'ok' in workspaces and workspaces.get('ok') and 'items' in workspaces:
                for workspace in workspaces['items']:
                    workspace_id = workspace.get('id')
                    if workspace_id:
                        projetos = client.listar_projetos(workspace_id)
                        if 'data' in projetos and projetos['data']:
                            for projeto in projetos['data']:
                                if projeto.get('id'):
                                    projeto_id = projeto.get('id')
                                    break
                    if projeto_id:
                        break
            
            if projeto_id:
                print(f"Projeto selecionado: {projeto_id}")
                
                nova_tarefa = client.criar_tarefa(
                    project_id=projeto_id,
                    titulo="Tarefa de Teste via API",
                    descricao="Esta tarefa foi criada automaticamente pelo sistema multi-agente para testar a integração com a API Taskade.",
                    content_type="text/markdown",
                    placement="afterbegin"
                )
                
                print(f"Resposta da criação de tarefa: {nova_tarefa}")
                
                if nova_tarefa.get('data') and nova_tarefa['data'].get('id'):
                    print(f"✅ Tarefa criada com sucesso! ID: {nova_tarefa['data']['id']}")
                else:
                    print("❌ Falha ao criar a tarefa. Resposta em formato inesperado.")
            else:
                print("❌ Não foi possível criar tarefa pois nenhum projeto foi encontrado.")
        except Exception as e:
            print(f"❌ Erro ao criar tarefa: {e}")
        
        return True
        
    except Exception as e:
        print(f"Erro geral ao conectar com a API Taskade: {e}")
        return False

if __name__ == "__main__":
    test_taskade_api()