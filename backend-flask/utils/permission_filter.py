"""
Sistema de Filtros de Permissão para Áreas Jurídicas
Aplica filtros baseados nas permissões do usuário em todas as rotas relevantes.
Inclui suporte ao papel Master com acesso completo exceto admin.
"""

import logging
from flask_login import current_user
from models import db, AgenteJuridico, CategoriaJuridica

logger = logging.getLogger(__name__)

def is_master_user():
    """
    Verifica se o usuário atual tem papel Master.
    
    Returns:
        bool: True se o usuário é Master
    """
    if not current_user.is_authenticated:
        return False
    
    try:
        from models import Role
        
        # Verificar se o usuário tem papel Master
        if hasattr(current_user, 'roles'):
            user_roles = [role.name for role in current_user.roles]
            return 'Master' in user_roles
        elif hasattr(current_user, 'role') and current_user.role:
            return current_user.role.name == 'Master'
        else:
            return False
        
    except Exception as e:
        logger.error(f"Erro ao verificar papel Master: {e}")
        return False

def is_admin_user():
    """
    Verifica se o usuário atual é administrador.
    
    Returns:
        bool: True se o usuário é admin
    """
    if not current_user.is_authenticated:
        return False
    
    try:
        from models import Role
        
        # Verificar se o usuário tem papel de administrador
        if hasattr(current_user, 'roles'):
            user_roles = [role.name for role in current_user.roles]
            return 'Administrador' in user_roles or 'Admin' in user_roles
        elif hasattr(current_user, 'role') and current_user.role:
            return current_user.role.name in ['Administrador', 'Admin']
        else:
            return False
        
    except Exception as e:
        logger.error(f"Erro ao verificar papel admin: {e}")
        return False

def is_advogado_user():
    """
    Verifica se o usuário atual tem papel Advogado.
    
    Returns:
        bool: True se o usuário é Advogado
    """
    if not current_user.is_authenticated:
        return False
    
    try:
        from models import Role
        
        # Verificar se o usuário tem papel Advogado
        if hasattr(current_user, 'roles'):
            user_roles = [role.name for role in current_user.roles]
            return 'Advogado' in user_roles
        elif hasattr(current_user, 'role') and current_user.role:
            return current_user.role.name == 'Advogado'
        else:
            return False
        
    except Exception as e:
        logger.error(f"Erro ao verificar papel Advogado: {e}")
        return False

def obter_areas_permitidas_usuario():
    """
    Obtém as áreas jurídicas permitidas para o usuário atual.
    
    Returns:
        list: Lista de nomes das áreas permitidas
    """
    if not current_user.is_authenticated:
        return []
    
    # Master e Advogado têm acesso a todas as áreas
    if is_master_user() or is_advogado_user():
        return ["Todas as Áreas"]
    
    try:
        from models import PermissaoAreaJuridica
        
        # Buscar permissões do usuário
        permissoes = PermissaoAreaJuridica.query.filter_by(user_id=current_user.id).all()
        
        if not permissoes:
            # Se não há permissões específicas, retorna todas as áreas (comportamento padrão)
            return ["Todas as Áreas"]
        
        # Verificar se tem permissão para "Todas as Áreas"
        for p in permissoes:
            if p.area_juridica == "Todas as Áreas" and p.pode_visualizar:
                return ["Todas as Áreas"]
        
        # Retornar áreas específicas permitidas
        return [p.area_juridica for p in permissoes if p.pode_visualizar]
        
    except Exception as e:
        logger.error(f"Erro ao obter áreas permitidas: {e}")
        return []

def obter_categorias_permitidas():
    """
    Obtém os IDs das categorias jurídicas permitidas para o usuário atual.
    
    Returns:
        list: Lista de IDs das categorias permitidas
    """
    if not current_user.is_authenticated:
        return []
    
    # Master e Advogado têm acesso a todas as categorias
    if is_master_user() or is_advogado_user():
        try:
            categorias = CategoriaJuridica.query.all()
            return [cat.id for cat in categorias]
        except Exception as e:
            logger.error(f"Erro ao obter todas as categorias para Master/Advogado: {e}")
            return []
    
    areas_permitidas = obter_areas_permitidas_usuario()
    
    if "Todas as Áreas" in areas_permitidas:
        try:
            categorias = CategoriaJuridica.query.all()
            return [cat.id for cat in categorias]
        except Exception as e:
            logger.error(f"Erro ao obter todas as categorias: {e}")
            return []
    
    try:
        categorias = CategoriaJuridica.query.filter(
            CategoriaJuridica.nome.in_(areas_permitidas)
        ).all()
        return [cat.id for cat in categorias]
    except Exception as e:
        logger.error(f"Erro ao obter categorias permitidas: {e}")
        return []

def filtrar_agentes_por_permissao(query):
    """
    Aplica filtros de permissão a uma query de agentes jurídicos.
    
    Args:
        query: Query SQLAlchemy para AgenteJuridico
        
    Returns:
        Query filtrada baseada nas permissões do usuário
    """
    if not current_user.is_authenticated:
        return query.filter(False)  # Não retorna nenhum resultado
    
    # Master e Advogado têm acesso a todos os agentes
    if is_master_user() or is_advogado_user():
        return query
    
    categorias_permitidas = obter_categorias_permitidas()
    
    if not categorias_permitidas:
        return query.filter(False)  # Não retorna nenhum resultado
    
    return query.filter(AgenteJuridico.categoria_id.in_(categorias_permitidas))

def aplicar_filtros_dashboard():
    """
    Aplica filtros de permissão para dados do dashboard.
    
    Returns:
        dict: Dados filtrados baseados nas permissões do usuário
    """
    if not current_user.is_authenticated:
        return {
            'areas_permitidas': [],
            'categorias_permitidas': [],
            'agentes_permitidos': [],
            'tem_acesso_completo': False,
            'is_master': False,
            'is_admin': False
        }
    
    areas = obter_areas_permitidas_usuario()
    categorias = obter_categorias_permitidas()
    is_master = is_master_user()
    is_admin = is_admin_user()
    is_advogado = is_advogado_user()
    
    # Obter agentes permitidos
    try:
        agentes_query = AgenteJuridico.query
        agentes_filtrados = filtrar_agentes_por_permissao(agentes_query)
        agentes_permitidos = agentes_filtrados.all()
    except Exception as e:
        logger.error(f"Erro ao obter agentes permitidos: {e}")
        agentes_permitidos = []
    
    # Obter templates jurídicos permitidos
    try:
        from models import TemplateJuridico
        templates_query = TemplateJuridico.query
        templates_permitidos = templates_query.all()
    except Exception as e:
        logger.error(f"Erro ao obter templates permitidos: {e}")
        templates_permitidos = []
    
    return {
        'areas_permitidas': areas,
        'categorias_permitidas': categorias,
        'agentes_permitidos': agentes_permitidos,
        'agentes': agentes_permitidos,  # Alias para compatibilidade
        'templates': templates_permitidos,  # Adicionar templates
        'categorias': categorias,  # Alias para categorias
        'total_agentes': len(agentes_permitidos),
        'total_templates': len(templates_permitidos),
        'total_categorias': len(categorias),
        'tem_acesso_completo': "Todas as Áreas" in areas or is_master or is_admin or is_advogado,
        'is_master': is_master,
        'is_admin': is_admin,
        'is_advogado': is_advogado,
        'total_agentes_disponiveis': len(agentes_permitidos),
        'total_areas_disponiveis': len(areas) if areas != ["Todas as Áreas"] else 18
    }

def debug_permissoes_usuario():
    """Debug das permissões do usuário atual"""
    if not current_user.is_authenticated:
        logger.info("Usuário não autenticado")
        return
    
    areas = obter_areas_permitidas_usuario()
    categorias = obter_categorias_permitidas()
    is_master = is_master_user()
    is_admin = is_admin_user()
    is_advogado = is_advogado_user()
    
    logger.info(f"Debug Permissões para {current_user.username}:")
    logger.info(f"  - É Master: {is_master}")
    logger.info(f"  - É Admin: {is_admin}")
    logger.info(f"  - É Advogado: {is_advogado}")
    logger.info(f"  - Áreas permitidas: {areas}")
    logger.info(f"  - IDs categorias permitidas: {categorias}")
