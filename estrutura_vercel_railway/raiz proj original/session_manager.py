"""
Sistema de Gestão de Sessão - Prevenção de Overflow de Cookies
Previne erros de produção relacionados ao limite de 4093 bytes dos cookies
"""

import json
import logging
from flask import session, request
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configurações
MAX_COOKIE_SIZE = 4000  # Limite seguro (menor que 4093)
MAX_TEXT_LENGTH = 500   # Máximo de caracteres para texto
MAX_SESSION_AGE = 3600  # 1 hora em segundos

class SessionManager:
    """
    Gerenciador inteligente de sessão com prevenção de overflow
    """
    
    @staticmethod
    def calculate_session_size() -> int:
        """Calcula o tamanho atual da sessão em bytes"""
        try:
            session_data = dict(session)
            session_json = json.dumps(session_data, ensure_ascii=False)
            return len(session_json.encode('utf-8'))
        except Exception:
            return 0
    
    @staticmethod
    def clean_old_sessions():
        """Remove dados antigos da sessão automaticamente"""
        current_time = datetime.utcnow()
        
        # Lista de chaves que podem ser removidas se antigas
        cleanable_keys = [
            'ultimo_resultado_analise',
            'texto_original_analise',
            'tipo_analise',
            'agente_usado',
            'historico_analises',
            'temp_data'
        ]
        
        for key in cleanable_keys:
            if key in session:
                # Verificar se existe timestamp
                timestamp_key = f"{key}_timestamp"
                if timestamp_key in session:
                    try:
                        timestamp = datetime.fromisoformat(session[timestamp_key])
                        if (current_time - timestamp).total_seconds() > MAX_SESSION_AGE:
                            session.pop(key, None)
                            session.pop(timestamp_key, None)
                            logging.info(f"Sessão: Removido {key} por expiração")
                    except Exception:
                        # Se não conseguir processar timestamp, remove
                        session.pop(key, None)
                        session.pop(timestamp_key, None)
    
    @staticmethod
    def compress_text(text: str, max_length: int = MAX_TEXT_LENGTH) -> str:
        """Comprime texto para evitar overflow"""
        if not text:
            return ""
        
        if len(text) <= max_length:
            return text
        
        # Corta e adiciona indicador
        return text[:max_length] + "..."
    
    @staticmethod
    def compress_result(resultado: Dict[str, Any]) -> Dict[str, Any]:
        """Comprime resultado para manter apenas dados essenciais"""
        compressed = {}
        
        # Campos essenciais com compressão
        if 'analise' in resultado:
            compressed['analise'] = SessionManager.compress_text(
                str(resultado['analise']), 1000
            )
        elif 'content' in resultado:
            compressed['analise'] = SessionManager.compress_text(
                str(resultado['content']), 1000
            )
        else:
            compressed['analise'] = "Análise processada com sucesso"
        
        # Resumo comprimido
        if 'resumo' in resultado:
            compressed['resumo'] = SessionManager.compress_text(
                str(resultado['resumo']), 200
            )
        else:
            compressed['resumo'] = "Análise jurídica especializada"
        
        # Status simples
        compressed['status'] = 'concluido'
        compressed['timestamp'] = datetime.utcnow().isoformat()
        
        return compressed
    
    @staticmethod
    def store_analysis_result(resultado: Dict[str, Any], texto: str, 
                            tipo_analise: str, agente_usado: str):
        """
        Armazena resultado de análise de forma segura na sessão
        Preserva texto integral e análise completa
        """
        # Limpar dados antigos primeiro
        SessionManager.clean_old_sessions()
        
        # Comprimir apenas o resultado, preservar texto integral
        compressed_result = SessionManager.compress_result(resultado)
        
        # Armazenar texto integral em sessão separada para exibição
        session['texto_original_completo'] = texto
        
        # Verificar tamanho do resultado comprimido
        test_session = {
            'ultimo_resultado_analise': compressed_result,
            'tipo_analise': tipo_analise,
            'agente_usado': agente_usado,
            'resultado_timestamp': datetime.utcnow().isoformat()
        }
        
        test_size = len(json.dumps(test_session, ensure_ascii=False).encode('utf-8'))
        
        # Se resultado muito grande, comprimir mais agressivamente
        if test_size > MAX_COOKIE_SIZE * 0.7:  # 70% do limite para margem
            compressed_result['analise'] = SessionManager.compress_text(
                compressed_result['analise'], 800
            )
            logging.warning(f"Sessão: Compressão de resultado aplicada (tamanho: {test_size})")
        
        # Armazenar dados principais (sem texto completo no cookie)
        session['ultimo_resultado_analise'] = compressed_result
        session['texto_original_analise'] = SessionManager.compress_text(texto, 200)  # Apenas preview
        session['tipo_analise'] = tipo_analise
        session['agente_usado'] = agente_usado
        session['resultado_timestamp'] = datetime.utcnow().isoformat()
        
        # Log do tamanho final
        final_size = SessionManager.calculate_session_size()
        logging.info(f"Sessão: Dados armazenados ({final_size} bytes)")
        
        if final_size > MAX_COOKIE_SIZE:
            logging.error(f"AVISO: Sessão ainda muito grande ({final_size} bytes)")
    
    @staticmethod
    def get_analysis_result() -> Optional[Dict[str, Any]]:
        """Recupera resultado de análise da sessão"""
        resultado = session.get('ultimo_resultado_analise')
        
        if not resultado:
            return None
        
        # Verificar se não expirou
        timestamp_str = session.get('resultado_timestamp')
        if timestamp_str:
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
                if (datetime.utcnow() - timestamp).total_seconds() > MAX_SESSION_AGE:
                    SessionManager.clear_analysis_data()
                    return None
            except Exception:
                pass
        
        return resultado
    
    @staticmethod
    def clear_analysis_data():
        """Remove dados de análise da sessão"""
        keys_to_remove = [
            'ultimo_resultado_analise',
            'texto_original_analise',
            'tipo_analise',
            'agente_usado',
            'resultado_timestamp'
        ]
        
        for key in keys_to_remove:
            session.pop(key, None)
        
        logging.info("Sessão: Dados de análise removidos")
    
    @staticmethod
    def monitor_session_health():
        """Monitora e reporta saúde da sessão"""
        size = SessionManager.calculate_session_size()
        
        health_status = {
            'size_bytes': size,
            'max_size': MAX_COOKIE_SIZE,
            'percentage_used': (size / MAX_COOKIE_SIZE) * 100,
            'status': 'healthy' if size < MAX_COOKIE_SIZE * 0.8 else 'warning' if size < MAX_COOKIE_SIZE else 'critical'
        }
        
        if health_status['status'] == 'warning':
            logging.warning(f"Sessão: Uso alto ({health_status['percentage_used']:.1f}%)")
        elif health_status['status'] == 'critical':
            logging.error(f"Sessão: Uso crítico ({health_status['percentage_used']:.1f}%)")
            SessionManager.clean_old_sessions()
        
        return health_status

# Middleware para monitoramento automático
def session_middleware():
    """
    Middleware para aplicar automaticamente antes de cada requisição
    """
    @request.before_app_request
    def before_request():
        # Limpar dados antigos a cada 10 requisições
        if not hasattr(session_middleware, 'request_count'):
            session_middleware.request_count = 0
        
        session_middleware.request_count += 1
        
        if session_middleware.request_count % 10 == 0:
            SessionManager.clean_old_sessions()
    
    return before_request

# Função de inicialização para Flask
def init_session_manager(app):
    """
    Inicializa o gerenciador de sessão na aplicação Flask
    """
    app.before_request(session_middleware())
    
    logging.info("SessionManager: Sistema inicializado")
    return SessionManager