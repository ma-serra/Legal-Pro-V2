# Integração com Taskade API

## Visão Geral

Este módulo implementa a integração com a API da Taskade, uma plataforma de produtividade e gerenciamento de tarefas. A integração permite listar workspaces e projetos do Taskade, para futuras integrações com o sistema multi-agente.

## Funcionalidades Implementadas

- ✅ Autenticação com token de API
- ✅ Listagem de workspaces
- ✅ Listagem de pastas (folders) dentro de um workspace
- ❌ Criação de tarefas (não suportado pela API atual)
- ❌ Atualização de tarefas (não suportado pela API atual)
- ❌ Exclusão de tarefas (não suportado pela API atual)

## Limitações Conhecidas

A API do Taskade está em desenvolvimento e muitos endpoints apresentam erros 404 (não encontrado) ou 500 (erro interno). As seguintes funcionalidades foram testadas mas não estão funcionando na versão atual:

- Obtenção de detalhes de um workspace específico
- Criação de tarefas em um projeto
- Criação de blocos em um workspace

## Credenciais Necessárias

Para utilizar esta integração, é necessário:

1. Um token de API do Taskade (formato: `tskdp_XXXXXXXXXXXXXXXXXXXXXXXXX`)
2. Opcionalmente, Client ID e Client Secret para OAuth2 (em desenvolvimento)

## Como Configurar

1. Acesse a página de administração do sistema
2. Navegue até "Integrações" > "Taskade"
3. Insira seu token de API Taskade
4. Clique em "Testar Conexão" para verificar se a API está acessível
5. Salve as configurações

## Exemplos de Uso

### Listar Workspaces

```python
from multiagent.integrations.taskade.client import TaskadeClient

client = TaskadeClient()
workspaces = client.listar_workspaces()
print(workspaces)
```

### Listar Pastas (Folders) de um Workspace

```python
from multiagent.integrations.taskade.client import TaskadeClient

client = TaskadeClient()
workspace_id = "seu_workspace_id"
folders = client.listar_projetos(workspace_id)
print(folders)
```

## Notas de Implementação

1. A autenticação OAuth2 foi implementada, mas apresenta erro 500 do servidor Taskade
2. Múltiplos métodos de autenticação e formatos de cabeçalho são tentados automaticamente
3. O cliente implementa fallbacks automáticos para diferentes formatos de autenticação

## Recursos Futuros

Quando a API do Taskade for expandida, as seguintes funcionalidades serão implementadas:

- Criação de tarefas
- Atualização de status de tarefas
- Exclusão de tarefas
- Integração bidirecional com agentes do sistema