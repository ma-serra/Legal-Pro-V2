"""
Utilitários de Segurança - Sistema Jurídico Multi-Agente
Implementação de funções de segurança centralizadas
"""

import os
import re
import hashlib
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from werkzeug.utils import secure_filename as werkzeug_secure_filename
from flask import request, session
import mimetypes

# Configuração de logging para eventos de segurança
security_logger = logging.getLogger('security')

# Criar diretório de logs se não existir
logs_dir = 'logs'
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir, exist_ok=True)

security_handler = logging.FileHandler('logs/security_events.log')
security_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
))
security_logger.addHandler(security_handler)
security_logger.setLevel(logging.INFO)

# Configurações de segurança
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'txt', 'md', 'odt', 'rtf',
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp',
    'mp3', 'wav', 'ogg', 'mp4', 'avi', 'mov', 'webm'
}

DANGEROUS_EXTENSIONS = {
    'exe', 'bat', 'cmd', 'com', 'pif', 'scr', 'vbs', 'js', 'jar',
    'php', 'asp', 'aspx', 'jsp', 'py', 'rb', 'pl', 'sh'
}

def validate_file_upload(file) -> Dict[str, Any]:
    """
    Valida upload de arquivo com verificações de segurança
    
    Returns:
        Dict com status da validação e mensagens de erro
    """
    try:
        if not file:
            return {
                'valid': False,
                'error': 'Nenhum arquivo foi selecionado',
                'code': 'NO_FILE'
            }
        
        if not file.filename:
            return {
                'valid': False,
                'error': 'Nome do arquivo é obrigatório',
                'code': 'NO_FILENAME'
            }
        
        # Verificar tamanho do arquivo
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset para o início
        
        if file_size > MAX_FILE_SIZE:
            return {
                'valid': False,
                'error': f'Arquivo muito grande. Máximo: {MAX_FILE_SIZE // (1024*1024)}MB',
                'code': 'FILE_TOO_LARGE'
            }
        
        # Verificar extensão do arquivo
        filename = file.filename.lower()
        extension = filename.rsplit('.', 1)[-1] if '.' in filename else ''
        
        if extension in DANGEROUS_EXTENSIONS:
            log_security_event('dangerous_file_upload', {
                'filename': file.filename,
                'extension': extension,
                'ip': request.remote_addr
            })
            return {
                'valid': False,
                'error': 'Tipo de arquivo não permitido por motivos de segurança',
                'code': 'DANGEROUS_FILE'
            }
        
        if extension not in ALLOWED_EXTENSIONS:
            return {
                'valid': False,
                'error': f'Extensão .{extension} não permitida',
                'code': 'INVALID_EXTENSION'
            }
        
        # Verificar MIME type
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type and not is_safe_mime_type(mime_type):
            return {
                'valid': False,
                'error': 'Tipo MIME do arquivo não permitido',
                'code': 'INVALID_MIME'
            }
        
        # Verificar conteúdo do arquivo (primeiros bytes)
        file_content = file.read(1024)
        file.seek(0)  # Reset
        
        if has_suspicious_content(file_content):
            log_security_event('suspicious_file_content', {
                'filename': file.filename,
                'ip': request.remote_addr
            })
            return {
                'valid': False,
                'error': 'Conteúdo do arquivo rejeitado por verificações de segurança',
                'code': 'SUSPICIOUS_CONTENT'
            }
        
        return {
            'valid': True,
            'filename': secure_filename_enhanced(file.filename),
            'size': file_size,
            'extension': extension,
            'mime_type': mime_type
        }
        
    except Exception as e:
        log_security_event('file_validation_error', {
            'error': str(e),
            'filename': getattr(file, 'filename', 'unknown'),
            'ip': request.remote_addr
        })
        return {
            'valid': False,
            'error': 'Erro interno na validação do arquivo',
            'code': 'VALIDATION_ERROR'
        }

def secure_filename_enhanced(filename: str) -> str:
    """
    Versão aprimorada do secure_filename com validações adicionais
    """
    # Usar secure_filename do Werkzeug como base
    secure_name = werkzeug_secure_filename(filename)
    
    # Remover caracteres potencialmente perigosos
    secure_name = re.sub(r'[^\w\-_\.]', '_', secure_name)
    
    # Limitar tamanho do nome
    name_part = secure_name.rsplit('.', 1)[0] if '.' in secure_name else secure_name
    extension = secure_name.rsplit('.', 1)[-1] if '.' in secure_name else ''
    
    if len(name_part) > 100:
        name_part = name_part[:100]
    
    # Evitar nomes reservados
    reserved_names = {'con', 'prn', 'aux', 'nul', 'com1', 'com2', 'lpt1', 'lpt2'}
    if name_part.lower() in reserved_names:
        name_part = f"file_{name_part}"
    
    # Garantir que não comece com ponto
    if name_part.startswith('.'):
        name_part = 'file' + name_part
    
    return f"{name_part}.{extension}" if extension else name_part

def is_safe_mime_type(mime_type: str) -> bool:
    """
    Verifica se o MIME type é seguro
    """
    safe_types = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
        'text/markdown',
        'application/vnd.oasis.opendocument.text',
        'application/rtf',
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/bmp',
        'image/webp',
        'audio/mpeg',
        'audio/wav',
        'audio/ogg',
        'video/mp4',
        'video/avi',
        'video/quicktime',
        'video/webm'
    ]
    
    return mime_type in safe_types

def has_suspicious_content(content: bytes) -> bool:
    """
    Verifica se o conteúdo do arquivo contém padrões suspeitos
    """
    suspicious_patterns = [
        b'<script',
        b'javascript:',
        b'<?php',
        b'<%',
        b'#!/bin/',
        b'#!/usr/bin/',
        b'MZ',  # Executáveis Windows
        b'\x7fELF'  # Executáveis Linux
    ]
    
    content_lower = content.lower()
    
    for pattern in suspicious_patterns:
        if pattern in content_lower:
            return True
    
    return False

def log_security_event(event_type: str, details: Dict[str, Any]):
    """
    Registra eventos de segurança
    """
    try:
        event_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details,
            'session_id': session.get('user_id', 'anonymous'),
            'user_agent': request.headers.get('User-Agent', 'unknown')
        }
        
        security_logger.warning(f"SECURITY_EVENT: {event_type} - {details}")
        
        # Aqui poderia ser implementado envio para SIEM ou sistema de monitoramento
        
    except Exception as e:
        # Evitar que erro de logging quebre a aplicação
        security_logger.error(f"Erro ao registrar evento de segurança: {e}")

def validate_sql_table_name(table_name: str) -> bool:
    """
    Valida nome de tabela para prevenir SQL injection
    """
    # Apenas caracteres alfanuméricos e underscore
    return bool(re.match(r'^[a-zA-Z0-9_]+$', table_name))

def sanitize_user_input(input_text: str, max_length: int = 1000) -> str:
    """
    Sanitiza entrada do usuário
    """
    if not input_text:
        return ""
    
    # Limitar tamanho
    sanitized = input_text[:max_length]
    
    # Remover caracteres de controle perigosos
    sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)
    
    # Escapar caracteres HTML básicos
    html_escapes = {
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '&': '&amp;'
    }
    
    for char, escape in html_escapes.items():
        sanitized = sanitized.replace(char, escape)
    
    return sanitized.strip()

def check_rate_limit(user_id: str, action: str, limit: int = 100, window: int = 3600) -> bool:
    """
    Verificação básica de rate limiting
    """
    # Esta é uma implementação básica
    # Em produção, usar Redis ou sistema dedicado
    try:
        from collections import defaultdict
        import time
        
        if not hasattr(check_rate_limit, '_counters'):
            check_rate_limit._counters = defaultdict(list)
        
        key = f"{user_id}:{action}"
        now = time.time()
        
        # Limpar entradas antigas
        check_rate_limit._counters[key] = [
            timestamp for timestamp in check_rate_limit._counters[key]
            if now - timestamp < window
        ]
        
        # Verificar limite
        if len(check_rate_limit._counters[key]) >= limit:
            log_security_event('rate_limit_exceeded', {
                'user_id': user_id,
                'action': action,
                'count': len(check_rate_limit._counters[key])
            })
            return False
        
        # Adicionar nova entrada
        check_rate_limit._counters[key].append(now)
        return True
        
    except Exception as e:
        security_logger.error(f"Erro na verificação de rate limit: {e}")
        return True  # Em caso de erro, permitir (fail open)

def generate_secure_token(length: int = 32) -> str:
    """
    Gera token seguro para sessões/CSRF
    """
    import secrets
    return secrets.token_urlsafe(length)

def hash_password_secure(password: str) -> str:
    """
    Hash de senha com salt seguro
    """
    import bcrypt
    
    # Gerar salt aleatório
    salt = bcrypt.gensalt(rounds=12)
    
    # Hash da senha
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    return hashed.decode('utf-8')

def verify_password_secure(password: str, hashed: str) -> bool:
    """
    Verifica senha com hash seguro
    """
    import bcrypt
    
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False

def validate_json_input(json_data: Any, required_fields: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Valida entrada JSON
    """
    if not isinstance(json_data, dict):
        return {
            'valid': False,
            'error': 'Dados JSON inválidos',
            'code': 'INVALID_JSON'
        }
    
    if required_fields:
        missing_fields = [field for field in required_fields if field not in json_data]
        if missing_fields:
            return {
                'valid': False,
                'error': f'Campos obrigatórios ausentes: {", ".join(missing_fields)}',
                'code': 'MISSING_FIELDS'
            }
    
    return {'valid': True, 'data': json_data}

# Configuração de headers de segurança
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://code.jquery.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; img-src 'self' data: https:; font-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com https://fonts.gstatic.com; connect-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
    'Referrer-Policy': 'strict-origin-when-cross-origin'
}

def apply_security_headers(response):
    """
    Aplica headers de segurança à resposta
    """
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response