#!/usr/bin/env python3
"""
SCRIPT DE VERIFICAÇÃO DA INSTALAÇÃO
"""
import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("🔍 VERIFICANDO INSTALAÇÃO DO MÓDULO")
    
    success = True
    
    # Verificar arquivos
    required_files = [
        "modules/comparacao_documentos/__init__.py",
        "modules/comparacao_documentos/routes/views.py",
        "modules/comparacao_documentos/services/comparador.py",
        "templates/comparacao_documentos/form.html",
        "templates/comparacao_documentos/visualizar.html"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            logger.info(f"   ✓ {file_path}")
        else:
            logger.error(f"   ❌ {file_path} - FALTANDO")
            success = False
    
    # Verificar dependências
    try:
        import flask
        import flask_sqlalchemy
        import openai
        import docx
        logger.info("   ✓ Dependências principais OK")
    except ImportError as e:
        logger.error(f"   ❌ Dependência faltando: {e}")
        success = False
    
    # Verificar integração
    try:
        from app import app
        with app.app_context():
            from models_comparacao import ComparacaoDocumento
        logger.info("   ✓ Integração com app OK")
    except Exception as e:
        logger.error(f"   ❌ Erro na integração: {e}")
        success = False
    
    if success:
        logger.info("✅ VERIFICAÇÃO CONCLUÍDA - TUDO OK!")
        logger.info("🚀 Execute o servidor com: python app.py")
    else:
        logger.error("❌ VERIFICAÇÃO FALHOU - Corrigir erros")
        sys.exit(1)

if __name__ == "__main__":
    main()
