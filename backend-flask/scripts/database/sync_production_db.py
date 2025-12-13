#!/usr/bin/env python3
"""
Script para sincronizar estrutura do banco de dados para produção
Garante que as tabelas e dados estejam alinhados entre desenvolvimento e produção
"""

import os
import sys
import logging
from main import app, db
from werkzeug.security import generate_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sync_database_structure():
    """Sincroniza estrutura do banco de dados"""
    
    with app.app_context():
        try:
            # Importar todos os modelos para garantir que sejam criados
            from models import User, Role, AgenteJuridico, CategoriaJuridica
            
            logger.info("🔄 Criando/atualizando tabelas...")
            db.create_all()
            
            # Verificar e criar roles necessários
            logger.info("🔄 Verificando roles...")
            
            # Role Administrador
            admin_role = Role.query.filter_by(name='Administrador').first()
            if not admin_role:
                admin_role = Role(
                    name='Administrador',
                    description='Papel com acesso total ao sistema'
                )
                db.session.add(admin_role)
                logger.info("✅ Role Administrador criado")
            
            # Role Advogado
            advogado_role = Role.query.filter_by(name='Advogado').first()
            if not advogado_role:
                advogado_role = Role(
                    name='Advogado',
                    description='Papel com acesso completo exceto rotas administrativas'
                )
                db.session.add(advogado_role)
                logger.info("✅ Role Advogado criado")
            
            db.session.commit()
            
            # Verificar e criar usuários necessários
            logger.info("🔄 Verificando usuários...")
            
            users_to_create = [
                {'username': 'admin', 'email': 'admin@legalpro.com', 'password': 'Advogado@2025', 'role': 'Administrador'},
                {'username': 'dmay', 'email': 'dmay@legalpro.com', 'password': 'C4rn31r0$425#', 'role': 'Administrador'},
                {'username': 'teste_eduardo', 'email': 'teste_eduardo@legalpro.com', 'password': 'Advogado@2025', 'role': 'Advogado'},
                {'username': 'eduardo', 'email': 'eduardo@legalpro.com', 'password': 'Advogado@2025', 'role': 'Advogado'},
                {'username': 'advogado', 'email': 'advogado@legalpro.com', 'password': 'Advogado@2025', 'role': 'Advogado'},
            ]
            
            for user_data in users_to_create:
                user = User.query.filter_by(username=user_data['username']).first()
                role = Role.query.filter_by(name=user_data['role']).first()
                
                if not user:
                    user = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        password_hash=generate_password_hash(user_data['password']),
                        role_id=role.id if role else None
                    )
                    db.session.add(user)
                    logger.info(f"✅ Usuário {user_data['username']} criado")
                else:
                    # Atualizar role se necessário
                    if role and user.role_id != role.id:
                        user.role_id = role.id
                        logger.info(f"✅ Role do usuário {user_data['username']} atualizado para {user_data['role']}")
            
            db.session.commit()
            
            # Relatório final
            total_users = User.query.count()
            total_roles = Role.query.count()
            
            logger.info(f"✅ Sincronização concluída:")
            logger.info(f"   - Total usuários: {total_users}")
            logger.info(f"   - Total roles: {total_roles}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na sincronização: {str(e)}")
            db.session.rollback()
            return False

def check_production_environment():
    """Verifica se estamos em ambiente de produção"""
    database_url = os.environ.get('DATABASE_URL', '')
    flask_env = os.environ.get('FLASK_ENV', 'development')
    
    is_production = (
        'neon' in database_url.lower() or 
        'aws' in database_url.lower() or
        flask_env == 'production'
    )
    
    logger.info(f"Ambiente detectado: {'PRODUÇÃO' if is_production else 'DESENVOLVIMENTO'}")
    logger.info(f"FLASK_ENV: {flask_env}")
    logger.info(f"DATABASE_URL: {database_url[:50]}...")
    
    return is_production

if __name__ == '__main__':
    logger.info("🚀 Iniciando sincronização do banco de dados...")
    
    # Verificar ambiente
    is_production = check_production_environment()
    
    if is_production:
        logger.info("⚠️  ATENÇÃO: Executando em ambiente de PRODUÇÃO")
        
        # Em produção, sempre sincronizar
        if sync_database_structure():
            logger.info("✅ Sincronização de produção concluída com sucesso")
            sys.exit(0)
        else:
            logger.error("❌ Falha na sincronização de produção")
            sys.exit(1)
    else:
        logger.info("ℹ️  Executando em ambiente de desenvolvimento")
        
        if sync_database_structure():
            logger.info("✅ Sincronização de desenvolvimento concluída")
            sys.exit(0)
        else:
            logger.error("❌ Falha na sincronização de desenvolvimento")
            sys.exit(1)