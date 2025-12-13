"""
Rotas para integração com a API do Zoom usando OAuth 2.0
"""

import os
import requests
import json
import hmac
import hashlib
from datetime import datetime, timedelta
from urllib.parse import urlencode, urlparse, parse_qs
from functools import lru_cache
import logging

from flask import Blueprint, redirect, request, session, url_for, jsonify, current_app, render_template
from flask_login import current_user, login_required

logger = logging.getLogger(__name__)

# Importe o blueprint do módulo principal
from zoom_api import zoom_api_bp

# Configurações do Zoom OAuth - Credenciais carregadas apenas de variáveis de ambiente
# SEGURANÇA: Não usar valores padrão para evitar exposição de credenciais
ZOOM_CLIENT_ID = os.environ.get('ZOOM_CLIENT_ID')
ZOOM_CLIENT_SECRET = os.environ.get('ZOOM_CLIENT_SECRET')
ZOOM_ACCOUNT_ID = os.environ.get('ZOOM_ACCOUNT_ID')
ZOOM_REDIRECT_URI = os.environ.get('ZOOM_REDIRECT_URI', f'https://{os.environ.get("REPLIT_DOMAINS", "localhost:5000")}/zoom_api/callback')
ZOOM_AUTH_URL = 'https://zoom.us/oauth/authorize'
ZOOM_TOKEN_URL = 'https://zoom.us/oauth/token'
ZOOM_API_BASE_URL = 'https://api.zoom.us/v2'

# Definir escopos necessários
ZOOM_SCOPES = [
    'user:read',
    'user:read:admin',
    'meeting:read',
    'meeting:write',
    'webinar:read',
    'webinar:write',
    'recording:read',
    'recording:write',
    'chat_message:read',
    'chat_message:write'
]

# Cache para token do Zoom (válido por 1 hora)
_zoom_token_cache = {'token': None, 'expires_at': None}

def get_server_to_server_token():
    """
    Obter token de acesso usando OAuth Server-to-Server com cache
    Não requer interação do usuário, ideal para uso em serviços backend
    Cache: 55 minutos (token válido por 60 minutos)
    """
    # Verificar cache primeiro
    now = datetime.now()
    if _zoom_token_cache['token'] and _zoom_token_cache['expires_at']:
        if now < _zoom_token_cache['expires_at']:
            logger.debug("✅ Token Zoom retornado do cache")
            return _zoom_token_cache['token']
    
    # Verificar se todas as credenciais necessárias estão configuradas
    if not ZOOM_CLIENT_ID or not ZOOM_CLIENT_SECRET or not ZOOM_ACCOUNT_ID:
        missing = []
        if not ZOOM_CLIENT_ID:
            missing.append("ZOOM_CLIENT_ID")
        if not ZOOM_CLIENT_SECRET:
            missing.append("ZOOM_CLIENT_SECRET")
        if not ZOOM_ACCOUNT_ID:
            missing.append("ZOOM_ACCOUNT_ID")
            
        error_msg = f"Credenciais do Zoom não configuradas: {', '.join(missing)}"
        logger.error(error_msg)
        return None
    
    token_url = "https://zoom.us/oauth/token"
    
    params = {
        'grant_type': 'account_credentials',
        'account_id': ZOOM_ACCOUNT_ID
    }
    
    try:
        logger.debug(f"🔄 Solicitando novo token OAuth para Zoom (Account ID: {ZOOM_ACCOUNT_ID[:4]}...)")
        
        response = requests.post(
            token_url,
            auth=(ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET),
            params=params,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if response.status_code != 200:
            error_msg = f"Erro ao obter token do Zoom: {response.status_code} - {response.text}"
            logger.error(error_msg)
            
            # Verificar o tipo de erro para fornecer mensagens mais úteis
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    if error_data.get('error') == 'invalid_client':
                        logger.error("Credenciais do Zoom (client_id/client_secret) inválidas")
                except:
                    pass
            return None
        
        token_data = response.json()
        token = token_data.get('access_token')
        
        # Cachear token por 55 minutos (token válido por 60)
        _zoom_token_cache['token'] = token
        _zoom_token_cache['expires_at'] = now + timedelta(minutes=55)
        
        logger.info("✅ Token OAuth do Zoom obtido e cacheado com sucesso")
        return token
    except Exception as e:
        error_msg = f"Exceção ao obter token do Zoom: {str(e)}"
        logger.exception(error_msg)
        return None

def get_headers():
    """Obter headers para requisições à API do Zoom"""
    token = get_server_to_server_token()
    if not token:
        return None
    
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

@lru_cache(maxsize=1)
def check_zoom_credentials():
    """
    Verifica se as credenciais do Zoom estão configuradas (com cache).
    Retorna uma tupla (bool, dict) onde:
    - bool: True se credenciais estão ok, False caso contrário
    - dict: Resposta de erro JSON se credenciais faltando, None caso contrário
    """
    if not ZOOM_CLIENT_ID or not ZOOM_CLIENT_SECRET or not ZOOM_ACCOUNT_ID:
        missing = []
        if not ZOOM_CLIENT_ID:
            missing.append("ZOOM_CLIENT_ID")
        if not ZOOM_CLIENT_SECRET:
            missing.append("ZOOM_CLIENT_SECRET")
        if not ZOOM_ACCOUNT_ID:
            missing.append("ZOOM_ACCOUNT_ID")
        
        return False, jsonify({
            'error': 'Serviço Zoom não configurado',
            'message': f'Credenciais do Zoom não foram configuradas: {", ".join(missing)}. Por favor, configure as variáveis de ambiente necessárias.',
            'missing_credentials': missing
        }), 503
    
    return True, None

@zoom_api_bp.route('/auth')
def auth():
    """Iniciar o fluxo de autenticação OAuth com o Zoom"""
    params = {
        'response_type': 'code',
        'client_id': ZOOM_CLIENT_ID,
        'redirect_uri': ZOOM_REDIRECT_URI,
        'scope': ' '.join(ZOOM_SCOPES)
    }
    
    auth_url = f"{ZOOM_AUTH_URL}?{urlencode(params)}"
    return redirect(auth_url)

@zoom_api_bp.route('/callback')
def callback():
    """Processar o callback de autenticação do Zoom"""
    code = request.args.get('code')
    
    if not code:
        return jsonify({'error': 'Código de autorização não encontrado'}), 400
    
    # Obter token de acesso
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': ZOOM_REDIRECT_URI
    }
    
    response = requests.post(
        ZOOM_TOKEN_URL,
        auth=(ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET),
        data=token_data
    )
    
    if response.status_code != 200:
        return jsonify({'error': 'Erro ao obter token', 'details': response.text}), 400
    
    # Guardar token na sessão
    session['zoom_token'] = response.json()
    
    return redirect(url_for('zoom_api.dashboard'))

@zoom_api_bp.route('/webhook', methods=['POST'])
def webhook():
    """
    Webhook para receber eventos do Zoom
    Este endpoint recebe notificações sobre eventos como término de reuniões,
    disponibilidade de gravações, etc.
    
    Cada notificação inclui um cabeçalho 'x-zm-signature' que permite verificar
    se ela foi realmente enviada pelo Zoom usando o token secreto do webhook.
    """
    # Obter o token secreto das variáveis de ambiente
    webhook_secret = os.environ.get('ZOOM_WEBHOOK_SECRET')
    
    try:
        # Validação de segurança do webhook usando o token secreto
        zoom_signature = request.headers.get('x-zm-signature')
        request_timestamp = request.headers.get('x-zm-request-timestamp')
        request_body = request.data.decode('utf-8')
        
        if webhook_secret and zoom_signature:
            print(f"[DEBUG] Verificando assinatura do webhook: {zoom_signature}")
            
            # Verificar assinatura (formato: v0=MAC)
            if not zoom_signature.startswith('v0='):
                print(f"[WARNING] Formato de assinatura inválido: {zoom_signature}")
                return jsonify({'status': 'error', 'message': 'Invalid signature format'}), 401
                
            # Extrair o MAC (Message Authentication Code)
            received_mac = zoom_signature[3:]  # Remover 'v0='
            
            # Gerar uma assinatura para comparação usando o token secreto
            message = f"v0:{request_timestamp}:{request_body}"
            hmac_obj = hmac.new(
                webhook_secret.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            )
            expected_signature = hmac_obj.hexdigest()
            
            # Comparar assinaturas
            if not hmac.compare_digest(received_mac, expected_signature):
                print(f"[WARNING] Assinatura webhook inválida. Possível tentativa de falsificação.")
                return jsonify({'status': 'error', 'message': 'Invalid webhook signature'}), 401
                
            print(f"[DEBUG] Assinatura do webhook verificada com sucesso")
        else:
            print(f"[WARNING] Verificação de assinatura ignorada: Token secreto ausente ou assinatura não fornecida")
        
        # Validação básica do webhook
        data = request.json
        if not data:
            return jsonify({'status': 'error', 'message': 'Invalid payload'}), 400
            
        # Obter o tipo de evento
        event = data.get('event')
        if not event:
            return jsonify({'status': 'error', 'message': 'Missing event type'}), 400
            
        # Processar diferentes tipos de eventos
        if event == 'recording.completed':
            # Quando uma gravação estiver disponível
            _processar_gravacao_disponivel(data)
            
        elif event == 'meeting.ended':
            # Quando uma reunião terminar
            _processar_reuniao_encerrada(data)
            
        # Outros tipos de eventos podem ser adicionados no futuro
            
        # Resposta de sucesso para o Zoom
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        # Log do erro
        current_app.logger.error(f"Erro no webhook do Zoom: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def _processar_gravacao_disponivel(data):
    """
    Processa o evento de gravação disponível
    Extrai informações da gravação e inicia o processo de transcrição automática
    
    Args:
        data (dict): Dados do evento Zoom
    """
    try:
        # Extrair informações da gravação
        payload = data.get('payload', {})
        object_data = payload.get('object', {})
        
        meeting_id = object_data.get('id')
        recordings = object_data.get('recording_files', [])
        
        if not meeting_id or not recordings:
            current_app.logger.warning("Dados de gravação incompletos no webhook")
            return
            
        # Procurar pela gravação de áudio ou vídeo
        recording_url = None
        for recording in recordings:
            if recording.get('file_type') in ['MP4', 'M4A']:
                recording_url = recording.get('download_url')
                if recording_url:
                    break
                    
        if not recording_url:
            current_app.logger.warning(f"Nenhuma URL de gravação encontrada para reunião {meeting_id}")
            return
            
        # Aqui você pode implementar o processamento de gravações conforme sua necessidade
        # Por exemplo, salvar a URL da gravação em um banco de dados ou
        # iniciar um processo de transcrição
        
        current_app.logger.info(f"Gravação disponível para reunião {meeting_id}: {recording_url}")
            
    except Exception as e:
        current_app.logger.error(f"Erro ao processar gravação disponível: {str(e)}")

def _processar_reuniao_encerrada(data):
    """
    Processa o evento de reunião encerrada
    Atualiza o status da sessão no banco de dados
    
    Args:
        data (dict): Dados do evento Zoom
    """
    try:
        # Extrair informações da reunião
        payload = data.get('payload', {})
        object_data = payload.get('object', {})
        
        meeting_id = object_data.get('id')
        if not meeting_id:
            current_app.logger.warning("ID da reunião não encontrado no webhook")
            return
        
        # Aqui você pode implementar a atualização do status da reunião
        # conforme necessário para sua aplicação
        current_app.logger.info(f"Reunião {meeting_id} encerrada")
            
    except Exception as e:
        current_app.logger.error(f"Erro ao processar reunião encerrada: {str(e)}")

@zoom_api_bp.route('/')
@login_required
def dashboard():
    """Dashboard central da integração com Zoom"""
    # Verificar se temos um token válido (Server-to-Server não requer isso)
    token = get_server_to_server_token()
    
    if not token:
        # Renderizar template com erro
        return render_template('zoom/dashboard.html', 
                              error='Não foi possível obter token de acesso do Zoom. Verifique as credenciais.',
                              now=datetime.now())
    
    # Verificar se estamos em uma solicitação API (Accept: application/json)
    if request.headers.get('Accept') == 'application/json':
        return jsonify({
            'status': 'success',
            'message': 'Conectado à API do Zoom',
            'features': [
                {'name': 'Criar reunião', 'url': url_for('zoom_api.create_meeting')},
                {'name': 'Ver webinars', 'url': url_for('zoom_api.list_webinars')},
                {'name': 'Ver gravações', 'url': url_for('zoom_api.list_recordings')},
                {'name': 'Enviar mensagem', 'url': url_for('zoom_api.send_message')}
            ]
        })
    
    # Renderizar template com sucesso
    return render_template('zoom/dashboard.html', token=token, now=datetime.now())

@zoom_api_bp.route('/create_meeting', methods=['GET', 'POST'])
@login_required
def create_meeting():
    """Criar uma reunião no Zoom"""
    # Bloquear APENAS usuários master da criação de reuniões
    if current_user.role == 'master':
        return jsonify({
            'error': 'Acesso negado. Apenas administradores podem criar reuniões.',
            'code': 'PERMISSION_DENIED'
        }), 403
    
    headers = get_headers()
    if not headers:
        # Verificar quais credenciais estão faltando
        missing = []
        if not ZOOM_CLIENT_ID:
            missing.append("ZOOM_CLIENT_ID")
        if not ZOOM_CLIENT_SECRET:
            missing.append("ZOOM_CLIENT_SECRET")
        if not ZOOM_ACCOUNT_ID:
            missing.append("ZOOM_ACCOUNT_ID")
            
        if missing:
            error_msg = f"Não foi possível autenticar com o Zoom. Credenciais ausentes: {', '.join(missing)}"
        else:
            error_msg = "Não autorizado. Token do Zoom expirado ou inválido. Verifique as credenciais do Zoom."
            
        return jsonify({'error': error_msg}), 401
    
    if request.method == 'POST':
        # Dados da reunião
        data = request.json or {}
        
        # Define o título da reunião
        topic = data.get('topic', 'Nova Reunião')
        
        # Processar configurações do Zoom
        settings = {
            'host_video': data.get('settings', {}).get('host_video', True),
            'participant_video': data.get('settings', {}).get('participant_video', True),
            'join_before_host': False,
            'mute_upon_entry': True,
            'waiting_room': data.get('settings', {}).get('waiting_room', True),
            'auto_recording': data.get('settings', {}).get('auto_recording', 'none')
        }
        
        meeting_data = {
            'topic': topic,
            'type': data.get('type', 2),  # 2 = Reunião agendada
            'start_time': data.get('start_time'),
            'duration': data.get('duration', 60),
            'timezone': data.get('timezone', 'America/Sao_Paulo'),
            'agenda': data.get('agenda', 'Reunião agendada via API'),
            'settings': settings
        }
        
        # API para criar reunião
        response = requests.post(
            f"{ZOOM_API_BASE_URL}/users/me/meetings",
            headers=headers,
            json=meeting_data
        )
        
        if response.status_code not in (200, 201):
            return jsonify({
                'error': 'Erro ao criar reunião',
                'details': response.text
            }), response.status_code
        
        meeting_response = response.json()
        
        # Retornar os dados da reunião criada
        return jsonify({
            'success': True,
            'meeting': meeting_response
        })
    
    # Se for uma requisição GET, renderizar o formulário
    return render_template('zoom/create_meeting.html')

@zoom_api_bp.route('/meetings', methods=['GET'])
@login_required
def list_meetings():
    """Listar TODAS as reuniões agendadas com paginação completa"""
    # Verificar permissões - apenas admins podem acessar lista de reuniões
    if current_user.role == 'master':
        return jsonify({
            'error': 'Acesso negado. Apenas administradores podem visualizar reuniões.',
            'code': 'PERMISSION_DENIED'
        }), 403
    
    headers = get_headers()
    if not headers:
        return jsonify({'error': 'Não autorizado. Token do Zoom expirado ou inválido.'}), 401
    
    # Coletar TODAS as reuniões usando paginação
    all_meetings = []
    page_number = 1
    page_size = 100  # Máximo permitido pela API do Zoom
    
    # Parâmetros para obter histórico completo (últimos 6 meses)
    from_date = request.args.get('from', (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d'))
    to_date = request.args.get('to', datetime.now().strftime('%Y-%m-%d'))
    
    while True:
        params = {
            'page_size': page_size,
            'page_number': page_number,
            'type': 'scheduled',  # Reuniões agendadas
            'from': from_date,
            'to': to_date
        }
        
        # API para listar reuniões
        response = requests.get(
            f"{ZOOM_API_BASE_URL}/users/me/meetings",
            headers=headers,
            params=params
        )
        
        if response.status_code != 200:
            if page_number == 1:  # Erro na primeira página
                return jsonify({
                    'error': 'Erro ao listar reuniões',
                    'details': response.text
                }), response.status_code
            else:
                break  # Parar se houver erro em páginas subsequentes
        
        meetings_data = response.json()
        current_meetings = meetings_data.get('meetings', [])
        
        # Adicionar reuniões atuais à lista completa
        all_meetings.extend(current_meetings)
        
        # Verificar se há mais páginas
        total_records = meetings_data.get('total_records', 0)
        if len(all_meetings) >= total_records or len(current_meetings) < page_size:
            break
            
        page_number += 1
    
    # Buscar também reuniões passadas
    params_past = {
        'page_size': 100,
        'type': 'previous_meetings'
    }
    
    response_past = requests.get(
        f"{ZOOM_API_BASE_URL}/users/me/meetings",
        headers=headers,
        params=params_past
    )
    
    if response_past.status_code == 200:
        past_meetings_data = response_past.json()
        past_meetings = past_meetings_data.get('meetings', [])
        all_meetings.extend(past_meetings)
    
    # Buscar reuniões ao vivo/ativas
    params_live = {
        'page_size': 100,
        'type': 'live'
    }
    
    response_live = requests.get(
        f"{ZOOM_API_BASE_URL}/users/me/meetings",
        headers=headers,
        params=params_live
    )
    
    if response_live.status_code == 200:
        live_meetings_data = response_live.json()
        live_meetings = live_meetings_data.get('meetings', [])
        all_meetings.extend(live_meetings)
    
    # Remover duplicatas baseado no ID da reunião
    unique_meetings = []
    seen_ids = set()
    for meeting in all_meetings:
        meeting_id = meeting.get('id')
        if meeting_id and meeting_id not in seen_ids:
            seen_ids.add(meeting_id)
            unique_meetings.append(meeting)
    
    # Ordenar por data de criação (mais recente primeiro)
    unique_meetings.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    meetings_response = {
        'meetings': unique_meetings,
        'total_records': len(unique_meetings),
        'page_count': 1,
        'page_size': len(unique_meetings),
        'page_number': 1
    }
    
    # Verificar se estamos em uma solicitação API
    if request.headers.get('Accept') == 'application/json':
        return jsonify(meetings_response)
    
    # Renderizar template com TODAS as reuniões
    return render_template('zoom/meetings.html', meetings=meetings_response)

@zoom_api_bp.route('/calendar', methods=['GET'])
@login_required
def calendar():
    """Visualizar reuniões em formato de calendário"""
    headers = get_headers()
    if not headers:
        return render_template('zoom/calendar.html', error='Token do Zoom expirado ou inválido.')
    
    # Buscar reuniões agendadas
    params = {
        'type': 'scheduled',
        'page_size': 100
    }
    
    response = requests.get(
        f"{ZOOM_API_BASE_URL}/users/me/meetings",
        headers=headers,
        params=params
    )
    
    meetings = []
    if response.status_code == 200:
        meetings = response.json().get('meetings', [])
    
    # Renderizar template de calendário
    return render_template('zoom/calendar.html', meetings=meetings, now=datetime.now())

@zoom_api_bp.route('/recordings', methods=['GET'])
@login_required
def list_recordings():
    """Listar gravações disponíveis"""
    headers = get_headers()
    if not headers:
        return jsonify({'error': 'Não autorizado. Token do Zoom expirado ou inválido.'}), 401
    
    # Parâmetros opcionais
    from_date = request.args.get('from', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    to_date = request.args.get('to', datetime.now().strftime('%Y-%m-%d'))
    
    params = {
        'page_size': request.args.get('page_size', 30),
        'from': from_date,
        'to': to_date
    }
    
    # API para listar gravações
    response = requests.get(
        f"{ZOOM_API_BASE_URL}/users/me/recordings",
        headers=headers,
        params=params
    )
    
    if response.status_code != 200:
        return jsonify({
            'error': 'Erro ao listar gravações',
            'details': response.text
        }), response.status_code
    
    recordings = response.json()
    
    # Verificar se estamos em uma solicitação API
    if request.headers.get('Accept') == 'application/json':
        return jsonify(recordings)
    
    # Renderizar template com as gravações
    return render_template('zoom/recordings.html', 
                         recordings=recordings, 
                         from_date=from_date, 
                         to_date=to_date,
                         now=datetime.now())

@zoom_api_bp.route('/join/<meeting_id>', methods=['GET'])
def join_meeting(meeting_id):
    """Gerar URL para participar de uma reunião"""
    # Parâmetros para participar da reunião
    name = request.args.get('name', 'Participante')
    email = request.args.get('email', '')
    
    join_url = f"https://zoom.us/j/{meeting_id}"
    
    # Adicionar parâmetros se fornecidos
    params = {}
    if name:
        params['uname'] = name
    if email:
        params['email'] = email
    
    if params:
        join_url = f"{join_url}?{urlencode(params)}"
    
    # Verificar se estamos em uma solicitação API
    if request.headers.get('Accept') == 'application/json':
        return jsonify({
            'join_url': join_url
        })
    
    # Redirecionar para a URL de participação
    return redirect(join_url)

@zoom_api_bp.route('/webinars', methods=['GET'])
@login_required
def list_webinars():
    """Listar webinars agendados"""
    headers = get_headers()
    if not headers:
        return jsonify({'error': 'Não autorizado. Token do Zoom expirado ou inválido.'}), 401
    
    # Parâmetros opcionais
    params = {
        'page_size': request.args.get('page_size', 30)
    }
    
    # API para listar webinars
    response = requests.get(
        f"{ZOOM_API_BASE_URL}/users/me/webinars",
        headers=headers,
        params=params
    )
    
    # Tratar caso o usuário não tenha plano de webinar
    if response.status_code != 200:
        error_data = response.json() if response.headers.get('Content-Type', '').startswith('application/json') else {}
        error_message = error_data.get('message', 'Erro ao listar webinars')
        
        # Se for erro de plano de webinar, mostrar mensagem apropriada
        if 'Webinar plan is missing' in error_message or response.status_code == 400:
            return render_template('zoom/webinars.html', 
                                 webinars={'webinars': []},
                                 error='Plano de Webinar não disponível',
                                 details='Sua conta Zoom não possui o plano de Webinar ativado. Para usar webinars, é necessário fazer upgrade do plano.')
        
        return jsonify({
            'error': 'Erro ao listar webinars',
            'details': response.text
        }), response.status_code
    
    webinars = response.json()
    
    # Verificar se estamos em uma solicitação API
    if request.headers.get('Accept') == 'application/json':
        return jsonify(webinars)
    
    # Renderizar template com os webinars
    return render_template('zoom/webinars.html', webinars=webinars)

@zoom_api_bp.route('/webinar/<webinar_id>', methods=['GET', 'PATCH', 'DELETE'])
@login_required
def manage_webinar(webinar_id):
    """Gerenciar um webinar específico"""
    headers = get_headers()
    if not headers:
        return jsonify({'error': 'Não autorizado. Token do Zoom expirado ou inválido.'}), 401
    
    if request.method == 'GET':
        # Obter detalhes do webinar
        response = requests.get(
            f"{ZOOM_API_BASE_URL}/webinars/{webinar_id}",
            headers=headers
        )
        
        if response.status_code != 200:
            return jsonify({
                'error': 'Erro ao obter detalhes do webinar',
                'details': response.text
            }), response.status_code
        
        webinar = response.json()
        
        # Verificar se estamos em uma solicitação API
        if request.headers.get('Accept') == 'application/json':
            return jsonify(webinar)
        
        # Renderizar template com os detalhes do webinar
        return render_template('zoom/webinar_details.html', webinar=webinar)
        
    elif request.method == 'PATCH':
        # Atualizar configurações do webinar
        data = request.json
        
        response = requests.patch(
            f"{ZOOM_API_BASE_URL}/webinars/{webinar_id}",
            headers=headers,
            json=data
        )
        
        if response.status_code != 204:
            return jsonify({
                'error': 'Erro ao atualizar webinar',
                'details': response.text
            }), response.status_code
        
        return jsonify({'success': True})
        
    elif request.method == 'DELETE':
        # Excluir webinar
        response = requests.delete(
            f"{ZOOM_API_BASE_URL}/webinars/{webinar_id}",
            headers=headers
        )
        
        if response.status_code != 204:
            return jsonify({
                'error': 'Erro ao excluir webinar',
                'details': response.text
            }), response.status_code
        
        return jsonify({'success': True})

@zoom_api_bp.route('/send_message', methods=['POST'])
@login_required
def send_message():
    """Enviar mensagem via Zoom Chat"""
    headers = get_headers()
    if not headers:
        return jsonify({'error': 'Não autorizado. Token do Zoom expirado ou inválido.'}), 401
    
    data = request.json
    if not data or not data.get('message') or not data.get('to_contact'):
        return jsonify({'error': 'Parâmetros inválidos. É necessário fornecer "message" e "to_contact"'}), 400
    
    message_data = {
        'message': data.get('message'),
        'to_contact': data.get('to_contact')
    }
    
    # API para enviar mensagem
    response = requests.post(
        f"{ZOOM_API_BASE_URL}/chat/users/me/messages",
        headers=headers,
        json=message_data
    )
    
    if response.status_code not in (200, 201):
        return jsonify({
            'error': 'Erro ao enviar mensagem',
            'details': response.text
        }), response.status_code
    
    return jsonify({
        'success': True,
        'message': 'Mensagem enviada com sucesso'
    })

@zoom_api_bp.route('/user', methods=['GET'])
@login_required
def get_user():
    """Obter informações do usuário atual"""
    headers = get_headers()
    if not headers:
        return jsonify({'error': 'Não autorizado. Token do Zoom expirado ou inválido.'}), 401
    
    # API para obter informações do usuário
    response = requests.get(
        f"{ZOOM_API_BASE_URL}/users/me",
        headers=headers
    )
    
    if response.status_code != 200:
        return jsonify({
            'error': 'Erro ao obter informações do usuário',
            'details': response.text
        }), response.status_code
    
    user_info = response.json()
    
    # Verificar se estamos em uma solicitação API
    if request.headers.get('Accept') == 'application/json':
        return jsonify(user_info)
    
    # Renderizar template com informações do usuário
    return render_template('zoom/user_info.html', user=user_info)

@zoom_api_bp.route('/meeting/<meeting_id>', methods=['GET', 'PATCH', 'DELETE'])
@login_required
def manage_meeting(meeting_id):
    """Gerenciar uma reunião específica"""
    headers = get_headers()
    if not headers:
        return jsonify({'error': 'Não autorizado. Token do Zoom expirado ou inválido.'}), 401
    
    if request.method == 'GET':
        # Obter detalhes da reunião
        response = requests.get(
            f"{ZOOM_API_BASE_URL}/meetings/{meeting_id}",
            headers=headers
        )
        
        if response.status_code != 200:
            return jsonify({
                'error': 'Erro ao obter detalhes da reunião',
                'details': response.text
            }), response.status_code
        
        meeting = response.json()
        
        # Verificar se estamos em uma solicitação API
        if request.headers.get('Accept') == 'application/json':
            return jsonify(meeting)
        
        # Renderizar template com os detalhes da reunião
        return render_template('zoom/meeting_details.html', meeting=meeting)
        
    elif request.method == 'PATCH':
        # Atualizar configurações da reunião
        data = request.json
        
        response = requests.patch(
            f"{ZOOM_API_BASE_URL}/meetings/{meeting_id}",
            headers=headers,
            json=data
        )
        
        if response.status_code != 204:
            return jsonify({
                'error': 'Erro ao atualizar reunião',
                'details': response.text
            }), response.status_code
        
        return jsonify({'success': True})
        
    elif request.method == 'DELETE':
        # Excluir reunião
        response = requests.delete(
            f"{ZOOM_API_BASE_URL}/meetings/{meeting_id}",
            headers=headers
        )
        
        if response.status_code != 204:
            return jsonify({
                'error': 'Erro ao excluir reunião',
                'details': response.text
            }), response.status_code
        
        return jsonify({'success': True})

@zoom_api_bp.route('/meeting/<meeting_id>/status', methods=['PUT'])
@login_required
def update_meeting_status(meeting_id):
    """Atualizar status de uma reunião (iniciar, encerrar, etc.)"""
    headers = get_headers()
    if not headers:
        return jsonify({'error': 'Não autorizado. Token do Zoom expirado ou inválido.'}), 401
    
    data = request.json
    if not data or not data.get('action'):
        return jsonify({'error': 'Parâmetro "action" não fornecido'}), 400
    
    action = data.get('action')
    
    # Validar ação
    valid_actions = ['end', 'recover']
    if action not in valid_actions:
        return jsonify({'error': f'Ação inválida. Use uma das seguintes: {", ".join(valid_actions)}'}), 400
    
    status_data = {
        'action': action
    }
    
    # API para atualizar status da reunião
    response = requests.put(
        f"{ZOOM_API_BASE_URL}/meetings/{meeting_id}/status",
        headers=headers,
        json=status_data
    )
    
    if response.status_code != 204:
        return jsonify({
            'error': f'Erro ao {action} reunião',
            'details': response.text
        }), response.status_code
    
    return jsonify({
        'success': True,
        'message': f'Reunião {action} com sucesso'
    })

@zoom_api_bp.route('/meeting/<meeting_id>/registrants', methods=['GET', 'POST'])
@login_required
def manage_registrants(meeting_id):
    """Gerenciar participantes registrados para uma reunião"""
    headers = get_headers()
    if not headers:
        return jsonify({'error': 'Não autorizado. Token do Zoom expirado ou inválido.'}), 401
    
    if request.method == 'GET':
        # Listar participantes registrados
        params = {
            'status': request.args.get('status', 'approved'),
            'page_size': request.args.get('page_size', 30)
        }
        
        response = requests.get(
            f"{ZOOM_API_BASE_URL}/meetings/{meeting_id}/registrants",
            headers=headers,
            params=params
        )
        
        if response.status_code != 200:
            return jsonify({
                'error': 'Erro ao obter participantes registrados',
                'details': response.text
            }), response.status_code
        
        registrants = response.json()
        
        # Verificar se estamos em uma solicitação API
        if request.headers.get('Accept') == 'application/json':
            return jsonify(registrants)
        
        # Renderizar template com os participantes
        return render_template('zoom/registrants.html', meeting_id=meeting_id, registrants=registrants)
        
    elif request.method == 'POST':
        # Adicionar novo participante
        data = request.json
        
        if not data or not data.get('email') or not data.get('first_name'):
            return jsonify({'error': 'Parâmetros incompletos. É necessário fornecer pelo menos "email" e "first_name"'}), 400
        
        response = requests.post(
            f"{ZOOM_API_BASE_URL}/meetings/{meeting_id}/registrants",
            headers=headers,
            json=data
        )
        
        if response.status_code not in (200, 201):
            return jsonify({
                'error': 'Erro ao registrar participante',
                'details': response.text
            }), response.status_code
        
        registrant = response.json()
        
        return jsonify({
            'success': True,
            'registrant': registrant
        })