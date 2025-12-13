"""
Sistema de Filtros de Permissão para Agentes Jurídicos
"""
import logging
from typing import List, Optional
from flask_login import current_user

logger = logging.getLogger(__name__)

def filtrar_agentes_por_permissoes(user_id: int, agentes: List) -> List:
    """
    Filtra lista de agentes baseado nas permissões do usuário.
    """
    try:
        from models import PermissaoAreaJuridica
        
        # Busca permissões do usuário
        permissoes = PermissaoAreaJuridica.query.filter_by(user_id=user_id).all()
        
        if not permissoes:
            logger.warning(f"Usuário {user_id} sem permissões configuradas")
            return []
        
        # Verifica se tem acesso a todas as áreas
        areas_permitidas = [p.area_juridica for p in permissoes]
        
        if "Todas as Áreas" in areas_permitidas:
            logger.info(f"Usuário {user_id} tem acesso a todas as áreas")
            return agentes
        
        # Filtra por áreas específicas
        agentes_filtrados = []
        for agente in agentes:
            if agente.categoria and agente.categoria.nome in areas_permitidas:
                agentes_filtrados.append(agente)
        
        logger.info(f"Filtrados {len(agentes_filtrados)} agentes para usuário {user_id}")
        return agentes_filtrados
        
    except Exception as e:
        logger.error(f"Erro ao filtrar agentes: {e}")
        return []

def verificar_permissao_agente(user_id: int, agente) -> bool:
    """
    Verifica se usuário tem permissão para acessar agente específico.
    """
    try:
        from models import PermissaoAreaJuridica
        
        permissoes = PermissaoAreaJuridica.query.filter_by(user_id=user_id).all()
        areas_permitidas = [p.area_juridica for p in permissoes]
        
        if "Todas as Áreas" in areas_permitidas:
            return True
            
        if agente.categoria and agente.categoria.nome in areas_permitidas:
            return True
            
        return False
        
    except Exception as e:
        logger.error(f"Erro ao verificar permissão: {e}")
        return False

def filtrar_categorias_por_permissao():
    """
    Filtra categorias baseado nas permissões do usuário atual.
    """
    try:
        from models import CategoriaJuridica, PermissaoAreaJuridica
        
        if not current_user.is_authenticated:
            return []
        
        permissoes = PermissaoAreaJuridica.query.filter_by(user_id=current_user.id).all()
        
        if not permissoes:
            return []
        
        areas_permitidas = [p.area_juridica for p in permissoes]
        
        if "Todas as Áreas" in areas_permitidas:
            return CategoriaJuridica.query.filter_by(ativa=True).all()
        
        # Filtra por áreas específicas
        return CategoriaJuridica.query.filter(
            CategoriaJuridica.nome.in_(areas_permitidas),
            CategoriaJuridica.ativa == True
        ).all()
        
    except Exception as e:
        logger.error(f"Erro ao filtrar categorias: {e}")
        return []

def debug_permissoes_usuario():
    """
    Função de debug para verificar permissões do usuário atual.
    """
    try:
        from models import PermissaoAreaJuridica
        
        if not current_user.is_authenticated:
            logger.debug("Usuário não autenticado")
            return
        
        permissoes = PermissaoAreaJuridica.query.filter_by(user_id=current_user.id).all()
        logger.debug(f"Usuário {current_user.id} possui {len(permissoes)} permissões")
        
        for perm in permissoes:
            logger.debug(f"Permissão: {perm.area_juridica}")
            
    except Exception as e:
        logger.error(f"Erro no debug de permissões: {e}")