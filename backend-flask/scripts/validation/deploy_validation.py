#!/usr/bin/env python3
"""
Script de Validação para Deploy - Legal Pro
Valida todos os componentes críticos antes do deploy
"""

import os
import sys
import importlib.util
import traceback
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeployValidator:
    """Validador completo do sistema para deploy"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_checks = 0
    
    def validate_imports(self):
        """Valida todas as importações críticas"""
        logger.info("🔍 Validando importações críticas...")
        self.total_checks += 1
        
        try:
            # Imports essenciais
            import flask
            import psycopg2
            import sqlalchemy
            import werkzeug
            import openai
            import anthropic
            import google.generativeai
            import qdrant_client
            import requests
            import python_docx
            import reportlab
            import plotly
            import pandas
            import numpy
            
            logger.info("✅ Todas as importações críticas estão funcionando")
            self.success_count += 1
            return True
            
        except ImportError as e:
            error_msg = f"Erro de importação: {e}"
            self.errors.append(error_msg)
            logger.error(f"❌ {error_msg}")
            return False
    
    def validate_environment_variables(self):
        """Valida variáveis de ambiente essenciais"""
        logger.info("🔍 Validando variáveis de ambiente...")
        self.total_checks += 1
        
        required_vars = [
            'DATABASE_URL',
            'OPENAI_API_KEY',
            'QDRANT_URL',
            'QDRANT_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            error_msg = f"Variáveis de ambiente faltantes: {', '.join(missing_vars)}"
            self.warnings.append(error_msg)
            logger.warning(f"⚠️ {error_msg}")
        else:
            logger.info("✅ Todas as variáveis de ambiente essenciais estão presentes")
            self.success_count += 1
            return True
        
        return len(missing_vars) == 0
    
    def validate_database_connection(self):
        """Valida conexão com base de dados"""
        logger.info("🔍 Validando conexão com base de dados...")
        self.total_checks += 1
        
        try:
            import psycopg2
            database_url = os.environ.get('DATABASE_URL')
            
            if not database_url:
                error_msg = "DATABASE_URL não configurada"
                self.errors.append(error_msg)
                logger.error(f"❌ {error_msg}")
                return False
            
            # Testar conexão
            conn = psycopg2.connect(database_url)
            with conn.cursor() as cursor:
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                logger.info(f"✅ Conexão com PostgreSQL estabelecida: {version[:50]}...")
            conn.close()
            
            self.success_count += 1
            return True
            
        except Exception as e:
            error_msg = f"Erro de conexão com base de dados: {e}"
            self.errors.append(error_msg)
            logger.error(f"❌ {error_msg}")
            return False
    
    def validate_flask_app(self):
        """Valida se a aplicação Flask carrega corretamente"""
        logger.info("🔍 Validando aplicação Flask...")
        self.total_checks += 1
        
        try:
            # Tentar importar app principal
            sys.path.insert(0, '.')
            
            # Verificar se main.py existe e é válido
            if not os.path.exists('main.py'):
                error_msg = "main.py não encontrado"
                self.errors.append(error_msg)
                logger.error(f"❌ {error_msg}")
                return False
            
            # Verificar se app.py existe
            if not os.path.exists('app.py'):
                error_msg = "app.py não encontrado"
                self.errors.append(error_msg)
                logger.error(f"❌ {error_msg}")
                return False
            
            # Validar sintaxe básica dos arquivos Python críticos
            critical_files = ['main.py', 'app.py', 'models.py']
            
            for file_path in critical_files:
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            compile(content, file_path, 'exec')
                        logger.info(f"✅ {file_path} - sintaxe válida")
                    except SyntaxError as e:
                        error_msg = f"Erro de sintaxe em {file_path}: {e}"
                        self.errors.append(error_msg)
                        logger.error(f"❌ {error_msg}")
                        return False
            
            self.success_count += 1
            return True
            
        except Exception as e:
            error_msg = f"Erro ao validar aplicação Flask: {e}"
            self.errors.append(error_msg)
            logger.error(f"❌ {error_msg}")
            return False
    
    def validate_templates(self):
        """Valida templates principais"""
        logger.info("🔍 Validando templates...")
        self.total_checks += 1
        
        try:
            critical_templates = [
                'templates/base.html',
                'templates/auth/login.html',
                'templates/home.html',
                'templates/admin/sync_database.html'
            ]
            
            missing_templates = []
            for template in critical_templates:
                if not os.path.exists(template):
                    missing_templates.append(template)
            
            if missing_templates:
                warning_msg = f"Templates faltantes: {', '.join(missing_templates)}"
                self.warnings.append(warning_msg)
                logger.warning(f"⚠️ {warning_msg}")
            else:
                logger.info("✅ Todos os templates críticos estão presentes")
                self.success_count += 1
                return True
                
            return len(missing_templates) == 0
            
        except Exception as e:
            error_msg = f"Erro ao validar templates: {e}"
            self.warnings.append(error_msg)
            logger.warning(f"⚠️ {error_msg}")
            return False
    
    def validate_static_files(self):
        """Valida arquivos estáticos essenciais"""
        logger.info("🔍 Validando arquivos estáticos...")
        self.total_checks += 1
        
        try:
            critical_static = [
                'static/css',
                'static/js',
                'static/images'
            ]
            
            missing_dirs = []
            for static_dir in critical_static:
                if not os.path.exists(static_dir):
                    missing_dirs.append(static_dir)
            
            if missing_dirs:
                warning_msg = f"Diretórios estáticos faltantes: {', '.join(missing_dirs)}"
                self.warnings.append(warning_msg)
                logger.warning(f"⚠️ {warning_msg}")
            else:
                logger.info("✅ Diretórios estáticos essenciais presentes")
                self.success_count += 1
                return True
                
            return len(missing_dirs) == 0
            
        except Exception as e:
            warning_msg = f"Erro ao validar arquivos estáticos: {e}"
            self.warnings.append(warning_msg)
            logger.warning(f"⚠️ {warning_msg}")
            return False
    
    def validate_sync_system(self):
        """Valida sistema de sincronização"""
        logger.info("🔍 Validando sistema de sincronização...")
        self.total_checks += 1
        
        try:
            # Verificar se os scripts de sincronização existem
            sync_files = [
                'sync_database.py',
                'quick_sync.py',
                'safe_sync_system.py'
            ]
            
            for sync_file in sync_files:
                if not os.path.exists(sync_file):
                    warning_msg = f"Script de sincronização faltante: {sync_file}"
                    self.warnings.append(warning_msg)
                    logger.warning(f"⚠️ {warning_msg}")
                else:
                    # Verificar sintaxe
                    try:
                        with open(sync_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            compile(content, sync_file, 'exec')
                        logger.info(f"✅ {sync_file} - sintaxe válida")
                    except SyntaxError as e:
                        error_msg = f"Erro de sintaxe em {sync_file}: {e}"
                        self.errors.append(error_msg)
                        logger.error(f"❌ {error_msg}")
            
            self.success_count += 1
            return True
            
        except Exception as e:
            warning_msg = f"Erro ao validar sistema de sincronização: {e}"
            self.warnings.append(warning_msg)
            logger.warning(f"⚠️ {warning_msg}")
            return False
    
    def validate_port_configuration(self):
        """Valida configuração de porta"""
        logger.info("🔍 Validando configuração de porta...")
        self.total_checks += 1
        
        try:
            # Verificar se o gunicorn está configurado corretamente
            if os.path.exists('gunicorn.conf.py'):
                with open('gunicorn.conf.py', 'r') as f:
                    content = f.read()
                    if '0.0.0.0:5000' in content or 'bind = "0.0.0.0:5000"' in content:
                        logger.info("✅ Configuração de porta do Gunicorn correta")
                        self.success_count += 1
                        return True
                    else:
                        warning_msg = "Configuração de porta pode estar incorreta"
                        self.warnings.append(warning_msg)
                        logger.warning(f"⚠️ {warning_msg}")
            
            # Verificar configuração no main.py ou app.py
            main_files = ['main.py', 'app.py']
            for main_file in main_files:
                if os.path.exists(main_file):
                    with open(main_file, 'r') as f:
                        content = f.read()
                        if 'port=5000' in content or '0.0.0.0:5000' in content:
                            logger.info(f"✅ Configuração de porta encontrada em {main_file}")
                            self.success_count += 1
                            return True
            
            warning_msg = "Configuração de porta não encontrada"
            self.warnings.append(warning_msg)
            logger.warning(f"⚠️ {warning_msg}")
            return False
            
        except Exception as e:
            warning_msg = f"Erro ao validar configuração de porta: {e}"
            self.warnings.append(warning_msg)
            logger.warning(f"⚠️ {warning_msg}")
            return False
    
    def validate_memory_usage(self):
        """Valida uso de memória estimado"""
        logger.info("🔍 Validando uso de memória...")
        self.total_checks += 1
        
        try:
            import psutil
            
            # Obter uso atual de memória
            memory = psutil.virtual_memory()
            available_mb = memory.available / (1024 * 1024)
            
            if available_mb < 512:  # Menos de 512MB disponível
                warning_msg = f"Pouca memória disponível: {available_mb:.0f}MB"
                self.warnings.append(warning_msg)
                logger.warning(f"⚠️ {warning_msg}")
            else:
                logger.info(f"✅ Memória disponível suficiente: {available_mb:.0f}MB")
                self.success_count += 1
                return True
            
            return available_mb >= 256  # Mínimo necessário
            
        except ImportError:
            warning_msg = "psutil não disponível para verificar memória"
            self.warnings.append(warning_msg)
            logger.warning(f"⚠️ {warning_msg}")
            return True  # Não bloquear o deploy por isso
        except Exception as e:
            warning_msg = f"Erro ao validar memória: {e}"
            self.warnings.append(warning_msg)
            logger.warning(f"⚠️ {warning_msg}")
            return True
    
    def run_validation(self):
        """Executa todas as validações"""
        logger.info("🚀 INICIANDO VALIDAÇÃO PARA DEPLOY - LEGAL PRO")
        logger.info("=" * 60)
        
        # Lista de validações
        validations = [
            self.validate_imports,
            self.validate_environment_variables,
            self.validate_database_connection,
            self.validate_flask_app,
            self.validate_templates,
            self.validate_static_files,
            self.validate_sync_system,
            self.validate_port_configuration,
            self.validate_memory_usage
        ]
        
        # Executar validações
        for validation in validations:
            try:
                validation()
            except Exception as e:
                error_msg = f"Erro inesperado em {validation.__name__}: {e}"
                self.errors.append(error_msg)
                logger.error(f"❌ {error_msg}")
        
        # Relatório final
        self.generate_report()
        
        return len(self.errors) == 0
    
    def generate_report(self):
        """Gera relatório final da validação"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 RELATÓRIO FINAL DE VALIDAÇÃO")
        logger.info("=" * 60)
        
        success_rate = (self.success_count / self.total_checks) * 100 if self.total_checks > 0 else 0
        
        logger.info(f"✅ Sucessos: {self.success_count}/{self.total_checks} ({success_rate:.1f}%)")
        logger.info(f"❌ Erros: {len(self.errors)}")
        logger.info(f"⚠️ Avisos: {len(self.warnings)}")
        
        if self.errors:
            logger.error("\n🚨 ERROS CRÍTICOS (DEVEM SER CORRIGIDOS):")
            for i, error in enumerate(self.errors, 1):
                logger.error(f"  {i}. {error}")
        
        if self.warnings:
            logger.warning("\n⚠️ AVISOS (RECOMENDADO CORRIGIR):")
            for i, warning in enumerate(self.warnings, 1):
                logger.warning(f"  {i}. {warning}")
        
        # Veredicto final
        if len(self.errors) == 0:
            if len(self.warnings) == 0:
                logger.info("\n🎉 SISTEMA PRONTO PARA DEPLOY!")
                logger.info("✅ Todas as validações passaram com sucesso")
            else:
                logger.info("\n✅ SISTEMA APROVADO PARA DEPLOY")
                logger.warning("⚠️ Alguns avisos foram encontrados, mas não impedem o deploy")
        else:
            logger.error("\n❌ SISTEMA NÃO ESTÁ PRONTO PARA DEPLOY")
            logger.error("🔧 Corrija os erros críticos antes de prosseguir")
        
        return len(self.errors) == 0

def main():
    """Função principal"""
    validator = DeployValidator()
    success = validator.run_validation()
    
    # Código de saída
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()