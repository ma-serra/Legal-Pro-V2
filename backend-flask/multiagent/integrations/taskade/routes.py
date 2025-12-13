"""
Rotas e controladores para a integração com o Taskade.

Este módulo contém as definições de rotas e funções controladoras para
integração com a API do Taskade. Inclui funcionalidades para gerenciar
workspaces, projetos, tarefas, agentes e outras entidades do Taskade.

Suporte a dois métodos de autenticação:
1. Token de API pessoal (simples)
2. OAuth 2.0 (mais seguro e com escopo limitado)
"""
import os
import logging
import secrets
from flask import Blueprint, render_template, redirect, request, url_for, flash, session, jsonify, current_app
from flask_login import login_required, current_user
from urllib.parse import urlencode

from multiagent.integrations.taskade.client import TaskadeClient
from multiagent.integrations.taskade.oauth import TaskadeOAuth

# Configurar logger
logger = logging.getLogger(__name__)

# Criar blueprint para as rotas do Taskade
taskade_bp = Blueprint('taskade', __name__, url_prefix='/taskade')

# Cliente global para facilitar acesso
client = TaskadeClient()

# Cliente OAuth global
oauth_client = None

def get_taskade_client():
    """
    Retorna uma instância do cliente Taskade inicializada com o token da sessão atual.
    
    Ordem de prioridade para o token:
    1. Token OAuth da sessão (se disponível e não expirado)
    2. Token de API pessoal da sessão
    3. Token do cliente global (último configurado)
    
    Returns:
        TaskadeClient: Cliente inicializado com o token válido
    """
    from flask import session
    
    # Verificar se há um token OAuth na sessão
    oauth_token = session.get('taskade_oauth_access_token')
    oauth_expired = False
    
    # Se temos OAuth configurado, verificar se o token expirou
    global oauth_client
    if oauth_token and oauth_client:
        oauth_expired = oauth_client.is_token_expired()
        if oauth_expired:
            # Tentar atualizar o token
            try:
                if oauth_client.refresh_token_if_needed():
                    # Token foi atualizado, usar o novo token
                    oauth_token = session.get('taskade_oauth_access_token')
                    oauth_expired = False
                    logger.debug("Token OAuth atualizado com sucesso")
                else:
                    logger.warning("Falha ao atualizar token OAuth expirado")
            except Exception as e:
                logger.error(f"Erro ao atualizar token OAuth: {e}")
                oauth_token = None
                
    # Se temos um token OAuth válido, usar esse token
    if oauth_token and not oauth_expired:
        if client.api_token != oauth_token:
            client.set_api_key(oauth_token)
            logger.debug("Cliente Taskade atualizado com token OAuth")
        return client
    
    # Caso contrário, usar token de API pessoal
    api_token = session.get('taskade_api_token')
    
    # Se o token na sessão diferir do token no cliente, atualizar o cliente
    if api_token and client.api_token != api_token:
        client.set_api_key(api_token)
        logger.debug("Cliente Taskade atualizado com token de API pessoal")
    
    return client

def initialize_oauth_client():
    """
    Inicializa o cliente OAuth com as configurações do ambiente.
    
    Returns:
        TaskadeOAuth: Cliente OAuth inicializado
    """
    global oauth_client
    
    if oauth_client:
        return oauth_client
    
    client_id = os.environ.get("TASKADE_CLIENT_ID")
    client_secret = os.environ.get("TASKADE_CLIENT_SECRET")
    
    # URL base da aplicação para construir a redirect_uri
    base_url = os.environ.get("BASE_URL")
    if not base_url:
        # Tentar construir a URL base a partir da configuração do Flask
        if current_app and current_app.config.get("SERVER_NAME"):
            scheme = current_app.config.get("PREFERRED_URL_SCHEME", "http")
            base_url = f"{scheme}://{current_app.config.get('SERVER_NAME')}"
        else:
            # Fallback para localhost
            base_url = "http://localhost:5000"
    
    redirect_uri = f"{base_url}/taskade/oauth/callback"
    
    oauth_client = TaskadeOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri
    )
    
    logger.debug(f"Cliente OAuth inicializado. Base URL: {base_url}, Redirect URI: {redirect_uri}")
    return oauth_client

# ==============================================================================
# Rotas para Configurações e Autenticação
# ==============================================================================

@taskade_bp.route('/')
@login_required
def index():
    """Página principal da integração com Taskade."""
    try:
        # Verificar se temos um token válido
        token_valido = False
        workspaces_count = 0
        oauth_ativo = False
        
        # Verificar se temos OAuth configurado
        oauth_client = initialize_oauth_client()
        oauth_ativo = bool(oauth_client and oauth_client.client_id and oauth_client.client_secret)
        
        # Verificar se temos um token OAuth na sessão
        oauth_token = session.get('taskade_oauth_access_token')
        if oauth_token and oauth_client:
            oauth_valido = not oauth_client.is_token_expired()
        else:
            oauth_valido = False
        
        # Usar a função auxiliar para obter cliente atualizado
        cliente_atual = get_taskade_client()
        
        if cliente_atual.api_token:
            token_valido = cliente_atual.verificar_autenticacao()
            
            # Se o token for válido, tenta obter número de workspaces para mostrar estatísticas
            if token_valido:
                try:
                    workspaces = cliente_atual.listar_workspaces()
                    workspaces_count = len(workspaces.get('data', []))
                except Exception as e:
                    logger.warning(f"Falha ao obter estatísticas do Taskade: {str(e)}")
                    # Não vamos travar a página por causa disso
                    pass
        
        return render_template(
            'integracoes/taskade/index.html',
            token_valido=token_valido,
            workspaces_count=workspaces_count,
            oauth_ativo=oauth_ativo,
            oauth_valido=oauth_valido if oauth_ativo else False,
            api_token_masked=cliente_atual.api_token[:4] + "****" + cliente_atual.api_token[-4:] if cliente_atual.api_token and len(cliente_atual.api_token) > 8 else None
        )
    except Exception as e:
        logger.error(f"Erro ao carregar página principal do Taskade: {str(e)}")
        flash(f'Erro ao carregar informações do Taskade: {str(e)}', 'error')
        return render_template('integracoes/taskade/index.html', token_valido=False)

@taskade_bp.route('/config', methods=['GET', 'POST'])
@login_required
def config():
    """Configurações da integração com Taskade."""
    # Verificar se temos OAuth configurado
    oauth_client = initialize_oauth_client()
    oauth_ativo = bool(oauth_client and oauth_client.client_id and oauth_client.client_secret)
    
    if request.method == 'POST':
        api_token = request.form.get('api_token')
        if api_token:
            try:
                # Salvar o token na sessão e no cliente
                session['taskade_api_token'] = api_token
                client.set_api_key(api_token)
                
                # Se for uma solicitação AJAX, retornar resposta JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'status': 'success',
                        'message': 'Token configurado temporariamente para teste'
                    })
                
                # Caso contrário, redirecionar com flash message para navegação normal
                flash('Token da API Taskade configurado com sucesso!', 'success')
                return redirect(url_for('taskade.index'))
            except Exception as e:
                error_msg = f'Erro ao configurar token da API: {str(e)}'
                
                # Se for AJAX, retornar erro como JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'status': 'error',
                        'message': error_msg
                    }), 400
                
                # Caso contrário, flash message
                flash(error_msg, 'error')
        else:
            msg = 'Por favor, forneça um token de API válido.'
            
            # Se for AJAX, retornar como JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'status': 'error',
                    'message': msg
                }), 400
            
            # Caso contrário, flash message
            flash(msg, 'warning')
    
    return render_template(
        'integracoes/taskade/config.html',
        oauth_ativo=oauth_ativo
    )

# ==============================================================================
# Rotas para OAuth 2.0
# ==============================================================================

@taskade_bp.route('/oauth/authorize')
@login_required
def oauth_authorize():
    """
    Inicia o fluxo de autorização OAuth 2.0.
    
    Redireciona o usuário para a página de autorização do Taskade.
    """
    # Inicializar cliente OAuth
    oauth_client = initialize_oauth_client()
    
    if not oauth_client or not oauth_client.client_id or not oauth_client.client_secret:
        flash('Configuração OAuth incompleta. Configure TASKADE_CLIENT_ID e TASKADE_CLIENT_SECRET.', 'error')
        return redirect(url_for('taskade.config'))
    
    try:
        # Gerar estado aleatório para segurança CSRF
        state = secrets.token_urlsafe(32)
        # Armazenar na sessão para validação
        session['taskade_oauth_state'] = state
        
        # Obter URL de autorização
        auth_url = oauth_client.get_authorization_url(state=state)
        
        # Redirecionar para a página de autorização
        return redirect(auth_url)
    except Exception as e:
        logger.error(f"Erro ao iniciar autorização OAuth: {e}")
        flash(f'Erro ao iniciar autorização: {str(e)}', 'error')
        return redirect(url_for('taskade.config'))

@taskade_bp.route('/oauth/callback')
@login_required
def oauth_callback():
    """
    Callback para receber o código de autorização do Taskade.
    
    Este é o ponto de redirecionamento após o usuário autorizar o aplicativo.
    """
    # Verificar se temos um erro
    error = request.args.get('error')
    if error:
        error_description = request.args.get('error_description', 'Sem descrição')
        logger.error(f"Erro na autorização OAuth: {error} - {error_description}")
        flash(f'Erro na autorização: {error} - {error_description}', 'error')
        return redirect(url_for('taskade.config'))
    
    # Verificar se temos um código de autorização
    code = request.args.get('code')
    if not code:
        logger.error("Nenhum código de autorização recebido do Taskade")
        flash('Nenhum código de autorização recebido. Tente novamente.', 'error')
        return redirect(url_for('taskade.config'))
    
    # Verificar o estado para segurança CSRF
    state = request.args.get('state')
    stored_state = session.get('taskade_oauth_state')
    if not state or not stored_state or state != stored_state:
        logger.error(f"Validação de estado falhou. Recebido: {state}, Esperado: {stored_state}")
        flash('Validação de segurança falhou. Tente novamente.', 'error')
        return redirect(url_for('taskade.config'))
    
    # Inicializar cliente OAuth
    oauth_client = initialize_oauth_client()
    
    # Trocar o código por um token de acesso
    try:
        token_data = oauth_client.get_token(code)
        
        # Armazenar o token na sessão
        oauth_client.store_token_in_session(token_data)
        
        # Definir o token no cliente Taskade para uso imediato
        client.set_api_key(token_data.get('access_token'))
        
        flash('Autorização OAuth concluída com sucesso!', 'success')
        return redirect(url_for('taskade.index'))
    except Exception as e:
        logger.error(f"Erro ao obter token de acesso: {e}")
        flash(f'Erro ao obter token de acesso: {str(e)}', 'error')
        return redirect(url_for('taskade.config'))

@taskade_bp.route('/oauth/logout')
@login_required
def oauth_logout():
    """
    Encerra a sessão OAuth.
    
    Remove os tokens da sessão.
    """
    # Inicializar cliente OAuth
    oauth_client = initialize_oauth_client()
    
    # Limpar tokens da sessão
    oauth_client.clear_token_from_session()
    
    flash('Sessão OAuth encerrada com sucesso.', 'success')
    return redirect(url_for('taskade.index'))

# ==============================================================================
# Rotas de API
# ==============================================================================

@taskade_bp.route('/api/test-connection')
@login_required
def api_test_connection_route():
    """API para testar a conexão com o Taskade."""
    try:
        # Usar a função auxiliar para obter cliente atualizado
        cliente_atual = get_taskade_client()
        
        # Verificar se o token é válido
        if not cliente_atual.api_token:
            return jsonify({
                'status': 'error',
                'message': 'Nenhum token de API configurado.'
            }), 400
            
        # Testar conexão
        conexao_valida = cliente_atual.verificar_autenticacao()
        
        if not conexao_valida:
            return jsonify({
                'status': 'error',
                'message': 'Token inválido ou expirado. Verifique suas configurações.'
            }), 400
            
        # Se a conexão for válida, tentar obter alguns dados básicos
        try:
            # Tentar listar workspaces para verificar funcionalidade
            workspaces = cliente_atual.listar_workspaces()
            workspaces_count = len(workspaces.get('data', [])) if workspaces and 'data' in workspaces else 0
            
            # Determinar método de autenticação
            oauth_token = session.get('taskade_oauth_access_token')
            metodo_auth = "OAuth 2.0" if oauth_token and oauth_token == cliente_atual.api_token else "Token de API Pessoal"
            
            return jsonify({
                'status': 'success',
                'message': f'Conexão estabelecida com sucesso via {metodo_auth}.',
                'data': {
                    'auth_method': metodo_auth,
                    'workspaces_count': workspaces_count
                }
            })
        except Exception as e:
            # Conexão válida, mas encontrou erro ao tentar operações
            logger.warning(f"Erro ao acessar dados do Taskade durante teste: {str(e)}")
            return jsonify({
                'status': 'warning',
                'message': f'Autenticação bem-sucedida, mas erro ao acessar dados: {str(e)}'
            })
            
    except Exception as e:
        logger.error(f"Erro ao testar conexão com Taskade: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erro ao testar conexão: {str(e)}'
        }), 500

# ==============================================================================
# Rotas para Workspaces
# ==============================================================================

@taskade_bp.route('/workspaces')
@login_required
def workspaces():
    """Lista todos os workspaces disponíveis."""
    try:
        workspaces_data = client.listar_workspaces()
        return render_template(
            'integracoes/taskade/workspaces.html',
            workspaces=workspaces_data.get('data', [])
        )
    except Exception as e:
        flash(f'Erro ao listar workspaces: {str(e)}', 'error')
        return redirect(url_for('taskade.index'))

@taskade_bp.route('/workspace/<workspace_id>')
@login_required
def workspace_detail(workspace_id):
    """Detalhes de um workspace específico."""
    try:
        # Buscar projetos do workspace
        projetos = client.listar_projetos(workspace_id)
        
        return render_template(
            'integracoes/taskade/workspace_detail.html',
            workspace_id=workspace_id,
            projetos=projetos.get('data', [])
        )
    except Exception as e:
        flash(f'Erro ao carregar detalhes do workspace: {str(e)}', 'error')
        return redirect(url_for('taskade.workspaces'))

# ==============================================================================
# Rotas para Projetos
# ==============================================================================

@taskade_bp.route('/projeto/<projeto_id>')
@login_required
def projeto_detail(projeto_id):
    """Detalhes de um projeto específico."""
    try:
        # Buscar tarefas do projeto
        tarefas = client.listar_tarefas(projeto_id)
        
        return render_template(
            'integracoes/taskade/projeto_detail.html',
            projeto_id=projeto_id,
            tarefas=tarefas.get('data', [])
        )
    except Exception as e:
        flash(f'Erro ao carregar detalhes do projeto: {str(e)}', 'error')
        return redirect(url_for('taskade.workspaces'))

# ==============================================================================
# Rotas para Tarefas
# ==============================================================================

@taskade_bp.route('/projeto/<projeto_id>/criar-tarefa', methods=['GET', 'POST'])
@login_required
def criar_tarefa(projeto_id):
    """Criar uma nova tarefa em um projeto."""
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descricao = request.form.get('descricao')
        
        if not titulo:
            flash('Por favor, forneça um título para a tarefa.', 'warning')
            return render_template('integracoes/taskade/criar_tarefa.html', projeto_id=projeto_id)
        
        try:
            resultado = client.criar_tarefa(
                project_id=projeto_id,
                titulo=titulo,
                descricao=descricao or '',
                content_type="text/markdown"
            )
            
            if resultado.get('status') == 'error':
                flash(f'Erro ao criar tarefa: {resultado.get("message")}', 'error')
            else:
                flash('Tarefa criada com sucesso!', 'success')
                return redirect(url_for('taskade.projeto_detail', projeto_id=projeto_id))
                
        except Exception as e:
            flash(f'Erro ao criar tarefa: {str(e)}', 'error')
    
    return render_template('integracoes/taskade/criar_tarefa.html', projeto_id=projeto_id)

@taskade_bp.route('/projeto/<projeto_id>/tarefa/<tarefa_id>')
@login_required
def tarefa_detail(projeto_id, tarefa_id):
    """Detalhes de uma tarefa específica."""
    try:
        # Buscar detalhes da tarefa
        tarefa = client.obter_tarefa(projeto_id, tarefa_id)
        
        # Buscar anotação da tarefa
        try:
            anotacao = client.obter_anotacao_tarefa(projeto_id, tarefa_id)
        except:
            anotacao = None
        
        return render_template(
            'integracoes/taskade/tarefa_detail.html',
            projeto_id=projeto_id,
            tarefa=tarefa.get('data', {}),
            anotacao=anotacao.get('data', {}) if anotacao else None
        )
    except Exception as e:
        flash(f'Erro ao carregar detalhes da tarefa: {str(e)}', 'error')
        return redirect(url_for('taskade.projeto_detail', projeto_id=projeto_id))

# ==============================================================================
# Rotas para Agentes
# ==============================================================================

@taskade_bp.route('/agentes')
@login_required
def agentes():
    """Lista todos os agentes disponíveis."""
    try:
        agentes_data = client.listar_agentes()
        return render_template(
            'integracoes/taskade/agentes.html',
            agentes=agentes_data.get('data', [])
        )
    except Exception as e:
        flash(f'Erro ao listar agentes: {str(e)}', 'error')
        return redirect(url_for('taskade.index'))

@taskade_bp.route('/agente/<agente_id>')
@login_required
def agente_detail(agente_id):
    """Detalhes de um agente específico."""
    try:
        # Buscar detalhes do agente
        agente = client.obter_agente(agente_id)
        
        return render_template(
            'integracoes/taskade/agente_detail.html',
            agente=agente.get('data', {})
        )
    except Exception as e:
        flash(f'Erro ao carregar detalhes do agente: {str(e)}', 'error')
        return redirect(url_for('taskade.agentes'))

# ==============================================================================
# API JSON (para chamadas AJAX)
# ==============================================================================

@taskade_bp.route('/api/test-connection', methods=['GET'])
@login_required
def api_test_connection():
    """API para testar a conexão com o Taskade."""
    try:
        # Verificar autenticação
        if hasattr(client, 'verificar_autenticacao') and client.verificar_autenticacao():
            # Obter workspaces como teste adicional
            workspaces_data = client.listar_workspaces()
            workspace_count = len(workspaces_data.get('data', []))
            
            return jsonify({
                'status': 'success',
                'message': 'Conexão com API Taskade estabelecida com sucesso',
                'data': {
                    'workspaces_count': workspace_count
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Falha na autenticação com API Taskade. Verifique seu token.'
            }), 401
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao conectar com API Taskade: {str(e)}'
        }), 500

@taskade_bp.route('/api/workspaces', methods=['GET'])
@login_required
def api_workspaces():
    """API para listar workspaces em formato JSON."""
    try:
        workspaces_data = client.listar_workspaces()
        return jsonify(workspaces_data)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@taskade_bp.route('/api/projetos/<workspace_id>', methods=['GET'])
@login_required
def api_projetos(workspace_id):
    """API para listar projetos de um workspace em formato JSON."""
    try:
        projetos = client.listar_projetos(workspace_id)
        return jsonify(projetos)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@taskade_bp.route('/api/tarefas/<projeto_id>', methods=['GET'])
@login_required
def api_tarefas(projeto_id):
    """API para listar tarefas de um projeto em formato JSON."""
    try:
        tarefas = client.listar_tarefas(projeto_id)
        return jsonify(tarefas)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500