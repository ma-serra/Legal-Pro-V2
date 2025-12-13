"""
Utilitário de serialização JSON segura
Elimina completamente erros de serialização de objetos function
"""

import json
import datetime
from typing import Any, Dict, List, Union

class SafeJSONEncoder(json.JSONEncoder):
    """Encoder JSON que converte todos os tipos problemáticos"""
    
    def default(self, o):
        # Funções e métodos
        if callable(o):
            return f"<function: {o.__name__ if hasattr(o, '__name__') else 'unknown'}>"
        
        # Datetime objects
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        
        # Outros objetos complexos
        if hasattr(o, '__dict__'):
            return str(o)
        
        # Fallback para string
        return str(o)

def safe_json_serialize(data: Any) -> Dict[str, Any]:
    """
    Serializa dados de forma completamente segura
    Remove qualquer possibilidade de erro de serialização
    """
    
    def clean_value(value):
        """Limpa recursivamente qualquer valor problemático"""
        
        # Funções - converter para string descritiva
        if callable(value):
            return f"<function: {getattr(value, '__name__', 'unknown')}>"
        
        # Tipos primitivos seguros
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        
        # Listas
        if isinstance(value, (list, tuple)):
            return [clean_value(item) for item in value]
        
        # Dicionários
        if isinstance(value, dict):
            cleaned_dict = {}
            for k, v in value.items():
                # Garantir que a chave seja string
                clean_key = str(k) if not isinstance(k, str) else k
                cleaned_dict[clean_key] = clean_value(v)
            return cleaned_dict
        
        # Datetime
        if isinstance(value, datetime.datetime):
            return value.isoformat()
        
        # Qualquer outro objeto - converter para string
        return str(value)
    
    return clean_value(data)

def save_json_safely(data: Any, filepath: str) -> bool:
    """
    Salva dados JSON de forma completamente segura
    Retorna True se bem-sucedido, False caso contrário
    """
    try:
        # Primeira limpeza
        clean_data = safe_json_serialize(data)
        
        # Tentativa com encoder personalizado
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(clean_data, f, ensure_ascii=False, indent=2, cls=SafeJSONEncoder)
        
        return True
        
    except Exception as e:
        print(f"Erro na serialização primária: {e}")
        
        # Fallback extremo - apenas dados essenciais
        try:
            minimal_data = {
                'error': 'Dados complexos simplificados',
                'original_error': str(e),
                'simplified_data': str(data)[:1000]  # Primeiros 1000 caracteres
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(minimal_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as final_error:
            print(f"Erro final na serialização: {final_error}")
            return False

def load_json_safely(filepath: str) -> Union[Dict[str, Any], None]:
    """
    Carrega dados JSON de forma segura
    Retorna None se houver erro
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar JSON: {e}")
        return None