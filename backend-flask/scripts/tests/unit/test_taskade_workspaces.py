"""
Teste de integração com a API Taskade.
Este script testa a listagem de workspaces e projetos do usuário.
"""
import os
import sys
import json
import logging
from dotenv import load_dotenv

# Configure o logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Adicionar diretório raiz ao path para importar o cliente
sys.path.append('.')

# Importar o cliente Taskade
from multiagent.integrations.taskade.client import TaskadeClient

# Carregar variáveis de ambiente
load_dotenv()

def test_client():
    """Testa a criação do cliente e a autenticação."""
    # Usar diretamente o token que sabemos que funciona
    api_token = "tskdp_eyJvuW18Wd6gfeSkSr2eCvuisUUZZHwsDR"
    # O token do ambiente não está funcionando
    # api_token = os.environ.get("TASKADE_API_TOKEN")
    if not api_token:
        logger.error("Token da API Taskade não configurado no ambiente.")
        return False
    
    logger.info(f"Iniciando teste com token: {api_token[:5]}...{api_token[-5:]}")
    
    # Criar cliente
    client = TaskadeClient(api_token=api_token)
    
    # Testar autenticação
    autenticado = client.verificar_autenticacao()
    logger.info(f"Cliente autenticado: {autenticado}")
    
    if not autenticado:
        logger.error("Falha na autenticação com o token fornecido.")
        return False
    
    return True

def test_listar_workspaces():
    """Testa a listagem de workspaces."""
    api_token = "tskdp_eyJvuW18Wd6gfeSkSr2eCvuisUUZZHwsDR"
    client = TaskadeClient(api_token=api_token)
    
    try:
        # Listar workspaces
        workspaces = client.listar_workspaces()
        
        # Verificar se a resposta contém os dados esperados
        if "data" not in workspaces:
            logger.error("Resposta não contém o campo 'data'.")
            logger.info(f"Resposta completa: {json.dumps(workspaces, indent=2)}")
            return False
        
        # Exibir workspaces
        logger.info(f"Encontrados {len(workspaces['data'])} workspaces:")
        for ws in workspaces['data']:
            logger.info(f"- {ws.get('name', 'Sem nome')} (ID: {ws.get('id', 'Sem ID')})")
        
        return True
    except Exception as e:
        logger.error(f"Erro ao listar workspaces: {e}")
        return False

def test_listar_projetos():
    """Testa a listagem de projetos do usuário."""
    api_token = "tskdp_eyJvuW18Wd6gfeSkSr2eCvuisUUZZHwsDR"
    client = TaskadeClient(api_token=api_token)
    
    try:
        # Listar projetos
        projetos = client.listar_meus_projetos()
        
        # Verificar se a resposta contém os dados esperados
        if "data" not in projetos:
            logger.error("Resposta não contém o campo 'data'.")
            logger.info(f"Resposta completa: {json.dumps(projetos, indent=2)}")
            return False
        
        # Exibir projetos
        logger.info(f"Encontrados {len(projetos['data'])} projetos:")
        for projeto in projetos['data']:
            logger.info(f"- {projeto.get('name', 'Sem nome')} (ID: {projeto.get('id', 'Sem ID')})")
        
        return True
    except Exception as e:
        logger.error(f"Erro ao listar projetos: {e}")
        return False

def test_criar_tarefa():
    """Testa a criação de uma tarefa em um projeto."""
    api_token = "tskdp_eyJvuW18Wd6gfeSkSr2eCvuisUUZZHwsDR"
    client = TaskadeClient(api_token=api_token)
    
    try:
        # Primeiro, listar projetos para obter um ID
        projetos = client.listar_meus_projetos()
        
        if "data" not in projetos or not projetos["data"]:
            logger.error("Não foi possível obter a lista de projetos ou lista vazia.")
            return False
        
        # Usar o primeiro projeto como exemplo
        projeto = projetos["data"][0]
        projeto_id = projeto["id"]
        projeto_nome = projeto.get("name", "Sem nome")
        
        logger.info(f"Criando tarefa de teste no projeto: {projeto_nome} (ID: {projeto_id})")
        
        # Criar tarefa
        nome_tarefa = "Tarefa de teste via API - Sistema Multiagente"
        descricao = "Esta é uma tarefa criada automaticamente para testar a API."
        
        # Verificar se o método existe no cliente
        if not hasattr(client, "criar_tarefa"):
            logger.error("O método 'criar_tarefa' não existe no cliente.")
            logger.info("Este teste será implementado quando o método estiver disponível.")
            return None
        
        # O método existe, tentar criar a tarefa
        try:
            tarefa = client.criar_tarefa(
                project_id=projeto_id,
                titulo=nome_tarefa,
                descricao=descricao
            )
            
            # Verificar se a resposta contém os dados esperados
            if "data" not in tarefa:
                logger.error("Resposta não contém o campo 'data'.")
                logger.info(f"Resposta completa: {json.dumps(tarefa, indent=2)}")
                return False
            
            # Verificar o formato da resposta
            if isinstance(tarefa["data"], list):
                # Se for uma lista, pegar o primeiro item
                if len(tarefa["data"]) > 0:
                    tarefa_id = tarefa["data"][0].get("id", "desconhecido")
                    logger.info(f"Tarefa criada com sucesso! ID: {tarefa_id}")
                else:
                    logger.error("Lista de tarefas vazia na resposta")
                    return False
            else:
                # Se for um objeto, pegar o ID diretamente
                tarefa_id = tarefa["data"].get("id", "desconhecido")
                logger.info(f"Tarefa criada com sucesso! ID: {tarefa_id}")
            
            return True
        except Exception as e:
            logger.error(f"Erro ao criar tarefa: {e}")
            return False
    except Exception as e:
        logger.error(f"Erro ao preparar teste de criação de tarefa: {e}")
        return False

if __name__ == "__main__":
    print("=== Teste de Integração com Taskade ===")
    
    # Teste 1: Cliente e autenticação
    print("\n1. Testando cliente e autenticação...")
    cliente_ok = test_client()
    print(f"Resultado: {'SUCESSO ✓' if cliente_ok else 'FALHA ✗'}")
    
    if not cliente_ok:
        print("Não é possível continuar sem um cliente autenticado.")
        sys.exit(1)
    
    # Teste 2: Listar workspaces
    print("\n2. Testando listagem de workspaces...")
    workspaces_ok = test_listar_workspaces()
    print(f"Resultado: {'SUCESSO ✓' if workspaces_ok else 'FALHA ✗'}")
    
    # Teste 3: Listar projetos
    print("\n3. Testando listagem de projetos...")
    projetos_ok = test_listar_projetos()
    print(f"Resultado: {'SUCESSO ✓' if projetos_ok else 'FALHA ✗'}")
    
    # Teste 4: Criar tarefa
    print("\n4. Testando criação de tarefa...")
    tarefa_result = test_criar_tarefa()
    if tarefa_result is None:
        print("Resultado: PENDENTE ? (Método ainda não implementado)")
    else:
        print(f"Resultado: {'SUCESSO ✓' if tarefa_result else 'FALHA ✗'}")
    
    # Resumo
    print("\n=== Resumo dos Testes ===")
    print(f"Cliente e autenticação: {'SUCESSO ✓' if cliente_ok else 'FALHA ✗'}")
    print(f"Listar workspaces: {'SUCESSO ✓' if workspaces_ok else 'FALHA ✗'}")
    print(f"Listar projetos: {'SUCESSO ✓' if projetos_ok else 'FALHA ✗'}")
    if tarefa_result is None:
        print("Criar tarefa: PENDENTE ? (Método ainda não implementado)")
    else:
        print(f"Criar tarefa: {'SUCESSO ✓' if tarefa_result else 'FALHA ✗'}")