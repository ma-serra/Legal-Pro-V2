"""
Utilitários para armazenamento de conversas e arquivos dos módulos jurídicos.
"""
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from main import db
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

def salvar_conversa_modulo(user_id: int, modulo_id: str, session_id: str, 
                          pergunta: str, resposta: str, personalidade: str = 'advogado',
                          tom: str = 'sistematico', contexto_adicional: str = '',
                          template_usado: str = '', api_utilizada: str = '',
                          tempo_resposta: float = 0.0) -> bool:
    """
    Salva uma conversa de módulo jurídico no banco de dados.
    
    Args:
        user_id: ID do usuário
        modulo_id: ID do módulo jurídico
        session_id: ID da sessão
        pergunta: Pergunta feita pelo usuário
        resposta: Resposta gerada pelo sistema
        personalidade: Personalidade utilizada
        tom: Tom de voz utilizado
        contexto_adicional: Contexto adicional fornecido
        template_usado: Template utilizado (se houver)
        api_utilizada: API de IA utilizada
        tempo_resposta: Tempo de resposta em segundos
    
    Returns:
        bool: True se salvou com sucesso, False caso contrário
    """
    try:
        query = text("""
            INSERT INTO conversas_modulos_juridicos 
            (user_id, modulo_id, session_id, pergunta, resposta, personalidade, 
             tom, contexto_adicional, template_usado, api_utilizada, tempo_resposta)
            VALUES (:user_id, :modulo_id, :session_id, :pergunta, :resposta, 
                   :personalidade, :tom, :contexto_adicional, :template_usado, 
                   :api_utilizada, :tempo_resposta)
        """)
        
        db.session.execute(query, {
            'user_id': user_id,
            'modulo_id': modulo_id,
            'session_id': session_id,
            'pergunta': pergunta,
            'resposta': resposta,
            'personalidade': personalidade,
            'tom': tom,
            'contexto_adicional': contexto_adicional,
            'template_usado': template_usado,
            'api_utilizada': api_utilizada,
            'tempo_resposta': tempo_resposta
        })
        
        db.session.commit()
        logger.info(f"Conversa salva para usuário {user_id} no módulo {modulo_id}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao salvar conversa: {e}")
        db.session.rollback()
        return False

def obter_historico_conversas(user_id: int, modulo_id: str = None, 
                             limit: int = 50) -> List[Dict]:
    """
    Obtém o histórico de conversas de um usuário.
    
    Args:
        user_id: ID do usuário
        modulo_id: ID do módulo específico (opcional)
        limit: Limite de conversas a retornar
    
    Returns:
        List[Dict]: Lista de conversas
    """
    try:
        if modulo_id:
            query = text("""
                SELECT * FROM conversas_modulos_juridicos 
                WHERE user_id = :user_id AND modulo_id = :modulo_id
                ORDER BY created_at DESC 
                LIMIT :limit
            """)
            result = db.session.execute(query, {
                'user_id': user_id,
                'modulo_id': modulo_id,
                'limit': limit
            })
        else:
            query = text("""
                SELECT * FROM conversas_modulos_juridicos 
                WHERE user_id = :user_id
                ORDER BY created_at DESC 
                LIMIT :limit
            """)
            result = db.session.execute(query, {
                'user_id': user_id,
                'limit': limit
            })
        
        conversas = []
        for row in result:
            conversas.append({
                'id': row.id,
                'modulo_id': row.modulo_id,
                'session_id': row.session_id,
                'pergunta': row.pergunta,
                'resposta': row.resposta,
                'personalidade': row.personalidade,
                'tom': row.tom,
                'contexto_adicional': row.contexto_adicional,
                'template_usado': row.template_usado,
                'api_utilizada': row.api_utilizada,
                'tempo_resposta': row.tempo_resposta,
                'created_at': row.created_at
            })
        
        return conversas
        
    except Exception as e:
        logger.error(f"Erro ao obter histórico: {e}")
        return []

def salvar_arquivo_modulo(user_id: int, modulo_id: str, nome_arquivo: str,
                         tipo_arquivo: str, caminho_arquivo: str,
                         template_origem: str = '', conteudo_original: str = '',
                         mime_type: str = '') -> bool:
    """
    Salva informações de um arquivo gerado por módulo jurídico.
    
    Args:
        user_id: ID do usuário
        modulo_id: ID do módulo jurídico
        nome_arquivo: Nome do arquivo
        tipo_arquivo: Tipo do arquivo (docx, pdf, etc.)
        caminho_arquivo: Caminho completo do arquivo
        template_origem: Template usado para gerar o arquivo
        conteudo_original: Conteúdo original antes da geração
        mime_type: Tipo MIME do arquivo
    
    Returns:
        bool: True se salvou com sucesso, False caso contrário
    """
    try:
        # Calcular hash do arquivo se existir
        hash_arquivo = ''
        tamanho_arquivo = 0
        
        if os.path.exists(caminho_arquivo):
            tamanho_arquivo = os.path.getsize(caminho_arquivo)
            with open(caminho_arquivo, 'rb') as f:
                hash_arquivo = hashlib.md5(f.read()).hexdigest()
        
        query = text("""
            INSERT INTO arquivos_modulos_juridicos 
            (user_id, modulo_id, nome_arquivo, tipo_arquivo, caminho_arquivo,
             template_origem, conteudo_original, tamanho_arquivo, mime_type, hash_arquivo)
            VALUES (:user_id, :modulo_id, :nome_arquivo, :tipo_arquivo, :caminho_arquivo,
                   :template_origem, :conteudo_original, :tamanho_arquivo, :mime_type, :hash_arquivo)
        """)
        
        db.session.execute(query, {
            'user_id': user_id,
            'modulo_id': modulo_id,
            'nome_arquivo': nome_arquivo,
            'tipo_arquivo': tipo_arquivo,
            'caminho_arquivo': caminho_arquivo,
            'template_origem': template_origem,
            'conteudo_original': conteudo_original,
            'tamanho_arquivo': tamanho_arquivo,
            'mime_type': mime_type,
            'hash_arquivo': hash_arquivo
        })
        
        db.session.commit()
        logger.info(f"Arquivo {nome_arquivo} salvo para usuário {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao salvar arquivo: {e}")
        db.session.rollback()
        return False

def salvar_template_gerado(user_id: int, modulo_id: str, template_id: str,
                          nome_template: str, conteudo_gerado: str,
                          parametros_usados: Dict = None, formato_saida: str = 'html',
                          session_id: str = '') -> bool:
    """
    Salva um template gerado por módulo jurídico.
    
    Args:
        user_id: ID do usuário
        modulo_id: ID do módulo jurídico
        template_id: ID do template
        nome_template: Nome do template
        conteudo_gerado: Conteúdo gerado
        parametros_usados: Parâmetros utilizados na geração
        formato_saida: Formato de saída (html, docx, pdf)
        session_id: ID da sessão
    
    Returns:
        bool: True se salvou com sucesso, False caso contrário
    """
    try:
        import json
        
        query = text("""
            INSERT INTO templates_gerados_modulos 
            (user_id, modulo_id, template_id, nome_template, conteudo_gerado,
             parametros_usados, formato_saida, session_id)
            VALUES (:user_id, :modulo_id, :template_id, :nome_template, :conteudo_gerado,
                   :parametros_usados, :formato_saida, :session_id)
        """)
        
        db.session.execute(query, {
            'user_id': user_id,
            'modulo_id': modulo_id,
            'template_id': template_id,
            'nome_template': nome_template,
            'conteudo_gerado': conteudo_gerado,
            'parametros_usados': json.dumps(parametros_usados or {}),
            'formato_saida': formato_saida,
            'session_id': session_id
        })
        
        db.session.commit()
        logger.info(f"Template {nome_template} salvo para usuário {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao salvar template gerado: {e}")
        db.session.rollback()
        return False

def obter_arquivos_usuario(user_id: int, modulo_id: str = None) -> List[Dict]:
    """
    Obtém lista de arquivos de um usuário.
    
    Args:
        user_id: ID do usuário
        modulo_id: ID do módulo específico (opcional)
    
    Returns:
        List[Dict]: Lista de arquivos
    """
    try:
        if modulo_id:
            query = text("""
                SELECT * FROM arquivos_modulos_juridicos 
                WHERE user_id = :user_id AND modulo_id = :modulo_id
                ORDER BY created_at DESC
            """)
            result = db.session.execute(query, {
                'user_id': user_id,
                'modulo_id': modulo_id
            })
        else:
            query = text("""
                SELECT * FROM arquivos_modulos_juridicos 
                WHERE user_id = :user_id
                ORDER BY created_at DESC
            """)
            result = db.session.execute(query, {
                'user_id': user_id
            })
        
        arquivos = []
        for row in result:
            arquivos.append({
                'id': row.id,
                'modulo_id': row.modulo_id,
                'nome_arquivo': row.nome_arquivo,
                'tipo_arquivo': row.tipo_arquivo,
                'caminho_arquivo': row.caminho_arquivo,
                'template_origem': row.template_origem,
                'tamanho_arquivo': row.tamanho_arquivo,
                'mime_type': row.mime_type,
                'created_at': row.created_at
            })
        
        return arquivos
        
    except Exception as e:
        logger.error(f"Erro ao obter arquivos: {e}")
        return []