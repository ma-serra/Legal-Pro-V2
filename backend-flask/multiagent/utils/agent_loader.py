"""
Utilitários para carregar e gerenciar agentes do sistema.
"""
import logging
from models import db
from sqlalchemy import text

logger = logging.getLogger(__name__)

def obter_todos_agentes():
    """
    Obtém todos os agentes disponíveis no sistema.
    
    Retorna agentes da tabela 'agente' (agentes padrão do sistema) e
    'agentes_personalizados' (agentes criados pelos usuários).
    
    Returns:
        list: Lista de agentes formatados com seus atributos
    """
    try:
        # Consulta SQL para união dos agentes do sistema e agentes personalizados
        query = text("""
            SELECT 
                id, 
                nome, 
                descricao, 
                tipo,
                'sistema' as origem,
                ativo,
                data_criacao as criado_em,
                icon
            FROM agente
            UNION ALL
            SELECT 
                id, 
                nome, 
                descricao, 
                tipo,
                'personalizado' as origem,
                ativo,
                criado_em,
                NULL as icon
            FROM agentes_personalizados
            ORDER BY nome
        """)
        
        result = db.session.execute(query)
        
        agentes = []
        for row in result:
            agentes.append({
                'id': row.id,
                'nome': row.nome,
                'descricao': row.descricao,
                'tipo': row.tipo,
                'origem': row.origem,
                'ativo': row.ativo,
                'criado_em': row.criado_em,
                'icon': row.icon
            })
        
        return agentes
        
    except Exception as e:
        logger.error(f"Erro ao obter agentes: {str(e)}")
        return []