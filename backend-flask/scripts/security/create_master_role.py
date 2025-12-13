"""
Script para criar o papel Master no sistema
O Master pode acessar tudo exceto páginas de administração
"""

import os
import sys
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def conectar_database():
    """Conecta ao banco PostgreSQL"""
    import psycopg2
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise Exception("DATABASE_URL não configurada")
    return psycopg2.connect(database_url)

def criar_papel_master():
    """Cria o papel Master no sistema"""
    conn = conectar_database()
    cursor = conn.cursor()
    
    try:
        # Verificar se o papel Master já existe
        cursor.execute("SELECT id FROM role WHERE name = 'Master'")
        master_role = cursor.fetchone()
        
        if not master_role:
            # Criar papel Master
            cursor.execute("""
                INSERT INTO role (name, description, created_at, updated_at)
                VALUES ('Master', 'Acesso completo ao sistema exceto páginas de administração', %s, %s)
                RETURNING id
            """, (datetime.now(), datetime.now()))
            
            master_role_id = cursor.fetchone()[0]
            logger.info(f"✅ Papel Master criado com ID: {master_role_id}")
        else:
            master_role_id = master_role[0]
            logger.info(f"✅ Papel Master já existe com ID: {master_role_id}")
        
        # Buscar todas as permissões exceto admin
        cursor.execute("""
            SELECT id, code FROM permission 
            WHERE code NOT IN ('admin_access', 'admin_dashboard', 'system_admin')
        """)
        permissoes_master = cursor.fetchall()
        
        # Criar permissões Master se não existirem
        permissoes_especiais = [
            ('master_access', 'Acesso Master', 'Acesso completo exceto administração'),
            ('view_all_areas', 'Ver Todas Áreas', 'Visualizar todas as áreas jurídicas'),
            ('use_all_agents', 'Usar Todos Agentes', 'Utilizar todos os agentes jurídicos'),
            ('create_workflows', 'Criar Fluxos', 'Criar e gerenciar fluxos de trabalho'),
            ('export_data', 'Exportar Dados', 'Exportar dados do sistema'),
            ('advanced_search', 'Busca Avançada', 'Usar recursos avançados de busca')
        ]
        
        for code, name, description in permissoes_especiais:
            cursor.execute("SELECT id FROM permission WHERE code = %s", (code,))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO permission (name, code, description, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (name, code, description, datetime.now(), datetime.now()))
                logger.info(f"✅ Permissão criada: {name}")
        
        # Buscar novamente todas as permissões não-admin
        cursor.execute("""
            SELECT id FROM permission 
            WHERE code NOT IN ('admin_access', 'admin_dashboard', 'system_admin')
        """)
        todas_permissoes = cursor.fetchall()
        
        # Associar todas as permissões não-admin ao papel Master
        for perm_id, in todas_permissoes:
            cursor.execute("""
                INSERT INTO role_permissions (role_id, permission_id)
                SELECT %s, %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM role_permissions 
                    WHERE role_id = %s AND permission_id = %s
                )
            """, (master_role_id, perm_id, master_role_id, perm_id))
        
        conn.commit()
        logger.info(f"✅ Papel Master configurado com {len(todas_permissoes)} permissões")
        
        return master_role_id
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Erro ao criar papel Master: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def atualizar_filtros_permissao():
    """Atualiza o sistema de filtros para reconhecer o papel Master"""
    
    # Atualizar permission_filter.py
    permission_filter_content = '''"""
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
        user_roles = [role.name for role in current_user.roles]
        return 'Master' in user_roles
        
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
        user_roles = [role.name for role in current_user.roles]
        return 'Administrador' in user_roles or 'Admin' in user_roles
        
    except Exception as e:
        logger.error(f"Erro ao verificar papel admin: {e}")
        return False

def obter_areas_permitidas_usuario():
    """
    Obtém as áreas jurídicas permitidas para o usuário atual.
    
    Returns:
        list: Lista de nomes das áreas permitidas
    """
    if not current_user.is_authenticated:
        return []
    
    # Master tem acesso a todas as áreas
    if is_master_user():
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
    
    # Master tem acesso a todas as categorias
    if is_master_user():
        try:
            categorias = CategoriaJuridica.query.all()
            return [cat.id for cat in categorias]
        except Exception as e:
            logger.error(f"Erro ao obter todas as categorias para Master: {e}")
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
    
    # Master tem acesso a todos os agentes
    if is_master_user():
        return query
    
    categorias_permitidas = obter_categorias_permitidas()
    
    if not categorias_permitidas:
        return query.filter(False)  # Não retorna nenhum resultado
    
    return query.filter(AgenteJuridico.categoria_id.in_(categorias_permitidas))

def debug_permissoes_usuario():
    """Debug das permissões do usuário atual"""
    if not current_user.is_authenticated:
        logger.info("Usuário não autenticado")
        return
    
    areas = obter_areas_permitidas_usuario()
    categorias = obter_categorias_permitidas()
    is_master = is_master_user()
    is_admin = is_admin_user()
    
    logger.info(f"Debug Permissões para {current_user.username}:")
    logger.info(f"  - É Master: {is_master}")
    logger.info(f"  - É Admin: {is_admin}")
    logger.info(f"  - Áreas permitidas: {areas}")
    logger.info(f"  - IDs categorias permitidas: {categorias}")
'''
    
    # Escrever o arquivo atualizado
    with open('utils/permission_filter.py', 'w', encoding='utf-8') as f:
        f.write(permission_filter_content)
    
    logger.info("✅ Filtros de permissão atualizados com suporte ao papel Master")

def criar_decorador_master():
    """Cria decorador para verificar acesso Master"""
    
    decorator_content = '''"""
Decoradores de permissão para o sistema jurídico
Inclui verificações para papéis Master e Admin
"""

from functools import wraps
from flask import redirect, url_for, flash, abort
from flask_login import current_user
import logging

logger = logging.getLogger(__name__)

def master_required(f):
    """
    Decorador que exige papel Master ou superior para acessar a rota.
    
    Args:
        f: Função da rota a ser protegida
        
    Returns:
        Função decorada com verificação de permissão Master
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        
        from utils.permission_filter import is_master_user, is_admin_user
        
        # Admin tem acesso automático
        if is_admin_user():
            return f(*args, **kwargs)
        
        # Verificar se é Master
        if not is_master_user():
            flash('Acesso negado. Necessário papel Master ou superior.', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """
    Decorador que exige papel de Administrador para acessar a rota.
    
    Args:
        f: Função da rota a ser protegida
        
    Returns:
        Função decorada com verificação de permissão Admin
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        
        from utils.permission_filter import is_admin_user
        
        # Verificar se é Admin
        if not is_admin_user():
            flash('Acesso negado. Necessário papel de Administrador.', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    
    return decorated_function

def no_master_access(f):
    """
    Decorador que BLOQUEIA acesso para usuários Master (apenas Admin).
    Usado para páginas de administração.
    
    Args:
        f: Função da rota a ser protegida
        
    Returns:
        Função decorada que bloqueia Masters
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        
        from utils.permission_filter import is_admin_user, is_master_user
        
        # Apenas Admin pode acessar
        if not is_admin_user():
            if is_master_user():
                flash('Acesso negado. Esta área é restrita aos Administradores.', 'error')
            else:
                flash('Acesso negado. Necessário papel de Administrador.', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    
    return decorated_function
'''
    
    # Criar arquivo de decoradores
    with open('utils/permission_decorators.py', 'w', encoding='utf-8') as f:
        f.write(decorator_content)
    
    logger.info("✅ Decoradores de permissão criados")

def main():
    """Função principal"""
    try:
        logger.info("🚀 Iniciando criação do papel Master...")
        
        # Criar papel Master
        master_id = criar_papel_master()
        
        # Atualizar filtros de permissão
        atualizar_filtros_permissao()
        
        # Criar decoradores
        criar_decorador_master()
        
        logger.info("✅ Papel Master criado com sucesso!")
        logger.info(f"   - ID do papel: {master_id}")
        logger.info("   - Acesso: Tudo exceto páginas de admin")
        logger.info("   - Filtros de permissão atualizados")
        logger.info("   - Decoradores criados")
        
        print("\n" + "="*50)
        print("✅ PAPEL MASTER CRIADO COM SUCESSO!")
        print("="*50)
        print("📋 Resumo das alterações:")
        print("   • Papel 'Master' adicionado ao banco de dados")
        print("   • Permissões configuradas (tudo exceto admin)")
        print("   • Filtros de permissão atualizados")
        print("   • Decoradores @master_required e @no_master_access criados")
        print("   • Sistema pronto para usar")
        print("="*50)
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar papel Master: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()