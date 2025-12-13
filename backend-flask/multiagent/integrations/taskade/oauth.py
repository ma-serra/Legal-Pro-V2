"""
Módulo para OAuth 2.0 com a API Taskade.

Este módulo contém as classes e funções para autenticação OAuth 2.0
com a API do Taskade, seguindo a documentação oficial atualizada em maio de 2025.

Documentação de referência:
- https://www.taskade.com/api/documentation/
- https://taskade.com/settings/password (seção OAuth 2.0 Apps)
"""
import os
import json
import logging
import time
import urllib.parse
import requests
from flask import session, redirect, url_for, request, flash

logger = logging.getLogger(__name__)

class TaskadeOAuth:
    """
    Classe para autenticação OAuth 2.0 com o Taskade.
    
    Esta classe fornece métodos para autenticação OAuth 2.0 com o Taskade,
    incluindo geração de URLs de autorização, obtenção e atualização de tokens,
    seguindo a documentação oficial atualizada.
    """
    
    def __init__(self, client_id=None, client_secret=None, redirect_uri=None):
        """
        Inicializa o cliente OAuth do Taskade.
        
        Args:
            client_id: ID do cliente OAuth (opcional, padrão: obtido de variável de ambiente)
            client_secret: Segredo do cliente OAuth (opcional, padrão: obtido de variável de ambiente)
            redirect_uri: URI de redirecionamento OAuth (opcional)
        """
        self.client_id = client_id or os.environ.get("TASKADE_CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("TASKADE_CLIENT_SECRET")
        self.redirect_uri = redirect_uri
        
        # URLs atualizadas conforme documentação mais recente
        self.auth_base_url = "https://www.taskade.com/oauth2/authorize"
        self.token_url = "https://www.taskade.com/oauth2/token"
        self.refresh_token_url = "https://www.taskade.com/oauth2/token"
        
        if not self.client_id or not self.client_secret:
            logger.warning("ID do cliente ou segredo OAuth do Taskade não configurados")
            
    def get_authorization_url(self, state=None, scope=None):
        """
        Gera a URL de autorização OAuth 2.0.
        
        Args:
            state: Estado para segurança CSRF (opcional, mas recomendado)
            scope: Escopos de autorização (opcional)
            
        Returns:
            str: URL de autorização completa
        """
        if not self.client_id or not self.redirect_uri:
            raise ValueError("ID do cliente e URI de redirecionamento são obrigatórios")
            
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
        }
        
        if state:
            params["state"] = state
        else:
            # Gerar um state aleatório para segurança se não for fornecido
            import uuid
            params["state"] = str(uuid.uuid4())
            # Armazenar na sessão para validação posterior
            session["taskade_oauth_state"] = params["state"]
            
        if scope:
            params["scope"] = " ".join(scope) if isinstance(scope, list) else scope
            
        query_string = urllib.parse.urlencode(params)
        auth_url = f"{self.auth_base_url}?{query_string}"
        
        logger.debug(f"URL de autorização gerada: {auth_url}")
        return auth_url
        
    def get_token(self, code):
        """
        Obtém um token de acesso usando o código de autorização.
        
        Args:
            code: Código de autorização obtido após redirecionamento
            
        Returns:
            dict: Resposta contendo token de acesso, token de atualização e outros dados
            
        Raises:
            Exception: Se ocorrer um erro na solicitação do token
        """
        if not self.client_id or not self.client_secret or not self.redirect_uri:
            raise ValueError("ID do cliente, segredo e URI de redirecionamento são obrigatórios")
            
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code"
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        logger.debug(f"Solicitando token de acesso para código: {code}")
        
        response = requests.post(self.token_url, data=data, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Erro ao obter token: {response.status_code} - {response.text}")
            raise Exception(f"Erro ao obter token: {response.status_code} - {response.text}")
            
        token_data = response.json()
        logger.debug(f"Token de acesso obtido com sucesso. Expira em: {token_data.get('expires_in', 'desconhecido')}s")
        
        # Adicionar timestamp de expiração para facilitar verificação posterior
        if 'expires_in' in token_data:
            token_data['expires_at'] = int(time.time()) + int(token_data['expires_in'])
            
        return token_data
        
    def refresh_token(self, refresh_token):
        """
        Atualiza um token de acesso usando o token de atualização.
        
        Args:
            refresh_token: Token de atualização
            
        Returns:
            dict: Resposta contendo novo token de acesso e outros dados
            
        Raises:
            Exception: Se ocorrer um erro na solicitação de atualização
        """
        if not self.client_id or not self.client_secret:
            raise ValueError("ID do cliente e segredo são obrigatórios")
            
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        logger.debug(f"Atualizando token de acesso...")
        
        response = requests.post(self.refresh_token_url, data=data, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Erro ao atualizar token: {response.status_code} - {response.text}")
            raise Exception(f"Erro ao atualizar token: {response.status_code} - {response.text}")
            
        token_data = response.json()
        logger.debug(f"Token de acesso atualizado com sucesso. Expira em: {token_data.get('expires_in', 'desconhecido')}s")
        
        # Adicionar timestamp de expiração para facilitar verificação posterior
        if 'expires_in' in token_data:
            token_data['expires_at'] = int(time.time()) + int(token_data['expires_in'])
            
        return token_data
        
    def store_token_in_session(self, token_data):
        """
        Armazena os dados do token na sessão.
        
        Args:
            token_data: Dados do token obtidos de get_token ou refresh_token
        """
        session["taskade_oauth_access_token"] = token_data.get("access_token")
        session["taskade_oauth_refresh_token"] = token_data.get("refresh_token")
        session["taskade_oauth_expires_at"] = token_data.get("expires_at") or (
            int(time.time()) + int(token_data.get("expires_in", 3600))
        )
        
        # Armazenar também como token de API para compatibilidade com o cliente existente
        session["taskade_api_token"] = token_data.get("access_token")
        
        logger.debug("Dados do token armazenados na sessão")
        
    def get_token_from_session(self):
        """
        Obtém o token armazenado na sessão.
        
        Returns:
            str: Token de acesso ou None se não existir
        """
        return session.get("taskade_oauth_access_token")
        
    def is_token_expired(self):
        """
        Verifica se o token armazenado na sessão está expirado.
        
        Returns:
            bool: True se o token estiver expirado ou não existir, False caso contrário
        """
        expires_at = session.get("taskade_oauth_expires_at")
        if not expires_at:
            return True
            
        # Adicionar um buffer de 60 segundos para evitar problemas de timing
        return int(time.time()) + 60 >= int(expires_at)
        
    def refresh_token_if_needed(self):
        """
        Atualiza o token se estiver expirado.
        
        Returns:
            bool: True se o token foi atualizado com sucesso ou não precisou ser atualizado,
                  False se a atualização falhou
        """
        if not self.is_token_expired():
            return True
            
        refresh_token = session.get("taskade_oauth_refresh_token")
        if not refresh_token:
            logger.warning("Token expirado, mas não há token de atualização disponível")
            return False
            
        try:
            token_data = self.refresh_token(refresh_token)
            self.store_token_in_session(token_data)
            return True
        except Exception as e:
            logger.error(f"Falha ao atualizar token: {e}")
            return False
        
    def clear_token_from_session(self):
        """
        Remove os dados do token da sessão.
        """
        session.pop("taskade_oauth_access_token", None)
        session.pop("taskade_oauth_refresh_token", None) 
        session.pop("taskade_oauth_expires_at", None)
        session.pop("taskade_api_token", None)
        session.pop("taskade_oauth_state", None)
        
        logger.debug("Dados do token removidos da sessão")
    
    def validate_state(self, state):
        """
        Valida o parâmetro state para prevenir ataques CSRF.
        
        Args:
            state: Valor do parâmetro state recebido na callback
            
        Returns:
            bool: True se o state for válido, False caso contrário
        """
        stored_state = session.get("taskade_oauth_state")
        if not stored_state or not state:
            logger.warning("Parâmetro state ausente na validação")
            return False
            
        is_valid = stored_state == state
        if not is_valid:
            logger.warning(f"Validação de state falhou. Recebido: {state}, Esperado: {stored_state}")
            
        return is_valid