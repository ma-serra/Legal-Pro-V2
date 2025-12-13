"""
Módulo de notificações para manter o painel administrativo e outras interfaces atualizadas.
"""
import time
import json
import threading
import queue
from datetime import datetime
from flask import current_app

# Fila global para eventos do sistema
sistema_eventos = queue.Queue()

def notificar_alteracao_sistema(tipo="atualizacao_sistema", dados=None):
    """
    Adiciona um evento à fila de eventos do sistema.
    
    Args:
        tipo: Tipo de evento (ex: "atualizacao_sistema", "nova_analise", etc)
        dados: Dados adicionais do evento (opcional)
    """
    if dados is None:
        dados = {}
    
    evento = {
        "tipo": tipo,
        "timestamp": datetime.now().isoformat(),
        "dados": dados
    }
    
    sistema_eventos.put(evento)
    if current_app:
        current_app.logger.debug(f"Notificação enviada: {tipo}")

# Decorador para notificar mudanças após operações
def notificar_mudanca(tipo_evento="atualizacao_sistema"):
    """
    Decorador que notifica o sistema sobre mudanças após a execução de uma função.
    
    Args:
        tipo_evento: Tipo de evento a ser enviado (ex: "usuario_criado", "agente_atualizado")
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Executa a função original
            resultado = func(*args, **kwargs)
            
            # Após a execução, notifica o sistema
            dados = {}
            # Se a função retorna um dicionário, usamos como dados adicionais
            if isinstance(resultado, dict) and 'id' in resultado:
                dados = resultado
            
            notificar_alteracao_sistema(tipo=tipo_evento, dados=dados)
            
            return resultado
        return wrapper
    return decorator

# Funções específicas para diferentes tipos de notificações
def notificar_novo_usuario(usuario_id, username):
    """
    Notifica a criação de um novo usuário.
    
    Args:
        usuario_id: ID do usuário criado
        username: Nome de usuário
    """
    notificar_alteracao_sistema(
        tipo="usuario_criado",
        dados={"id": usuario_id, "username": username}
    )

def notificar_edicao_usuario(usuario_id, username):
    """
    Notifica a edição de um usuário.
    
    Args:
        usuario_id: ID do usuário editado
        username: Nome de usuário
    """
    notificar_alteracao_sistema(
        tipo="usuario_atualizado",
        dados={"id": usuario_id, "username": username}
    )

def notificar_exclusao_usuario(usuario_id, username):
    """
    Notifica a exclusão de um usuário.
    
    Args:
        usuario_id: ID do usuário excluído
        username: Nome de usuário
    """
    notificar_alteracao_sistema(
        tipo="usuario_excluido",
        dados={"id": usuario_id, "username": username}
    )

def notificar_nova_analise(analise_id, titulo):
    """
    Notifica a criação de uma nova análise.
    
    Args:
        analise_id: ID da análise criada
        titulo: Título da análise
    """
    notificar_alteracao_sistema(
        tipo="analise_criada",
        dados={"id": analise_id, "titulo": titulo}
    )

def notificar_atualizacao_config(secao, chave=None):
    """
    Notifica a atualização de configuração no sistema.
    
    Args:
        secao: Seção de configuração atualizada
        chave: Chave específica (opcional)
    """
    dados = {"secao": secao}
    if chave:
        dados["chave"] = chave
        
    notificar_alteracao_sistema(
        tipo="config_atualizada",
        dados=dados
    )

def notificar_erro_sistema(erro, modulo=None):
    """
    Notifica um erro no sistema.
    
    Args:
        erro: Mensagem de erro
        modulo: Módulo onde ocorreu o erro (opcional)
    """
    dados = {"mensagem": str(erro)}
    if modulo:
        dados["modulo"] = modulo
        
    notificar_alteracao_sistema(
        tipo="erro_sistema",
        dados=dados
    )

def notificar_api_status_alterado(api_nome, disponivel):
    """
    Notifica alteração no status de uma API.
    
    Args:
        api_nome: Nome da API
        disponivel: Status de disponibilidade (True/False)
    """
    notificar_alteracao_sistema(
        tipo="api_status_alterado",
        dados={"api": api_nome, "disponivel": disponivel}
    )