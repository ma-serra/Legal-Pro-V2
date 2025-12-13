"""
Módulo de Auditoria
Logging de ações e eventos do sistema para compliance
"""
from datetime import datetime
from typing import Dict, Any, Optional
import json


def log_audit(action: str, entity_type: str, entity_id: int, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Registra uma ação de auditoria no sistema
    
    Args:
        action: Tipo de ação (CREATE, READ, UPDATE, DELETE)
        entity_type: Tipo de entidade afetada
        entity_id: ID da entidade
        details: Detalhes adicionais da ação
        
    Returns:
        Registro de auditoria
    """
    audit_record = {
        'timestamp': datetime.now().isoformat(),
        'action': action,
        'entity_type': entity_type,
        'entity_id': entity_id,
        'details': details or {},
        'audit_id': None  # Seria preenchido pelo banco de dados
    }
    
    return audit_record
