#!/usr/bin/env python3
"""
API para extração de texto de documentos
Suporta PDF, DOC, DOCX, TXT
"""

from flask import Blueprint, request, jsonify
import tempfile
import os
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Criar blueprint
api_extrair_texto = Blueprint('api_extrair_texto', __name__)

def extrair_texto_arquivo_api(arquivo):
    """
    Extrai texto de arquivo de qualquer tipo suportado
    Implementação robusta para diferentes formatos
    """
    try:
        import tempfile
        import os
        
        # Salvar arquivo temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(arquivo.filename)[1]) as temp_file:
            arquivo.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Determinar tipo de arquivo e extrair texto
            filename_lower = arquivo.filename.lower()
            
            if filename_lower.endswith('.txt') or filename_lower.endswith('.md'):
                with open(temp_path, 'r', encoding='utf-8') as f:
                    texto = f.read()
            
            elif filename_lower.endswith('.docx'):
                from docx import Document
                doc = Document(temp_path)
                texto = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            
            elif filename_lower.endswith('.pdf'):
                import fitz  # PyMuPDF
                try:
                    doc = fitz.open(temp_path)
                    texto = ""
                    for page_num in range(len(doc)):
                        page = doc.load_page(page_num)
                        texto += page.get_text()
                    doc.close()
                except Exception as pdf_error:
                    logger.error(f"Erro ao processar PDF: {pdf_error}")
                    raise ValueError(f"Erro ao processar arquivo PDF: {str(pdf_error)}")
            
            else:
                raise ValueError(f"Formato de arquivo não suportado: {arquivo.filename}")
            
            return texto
            
        finally:
            # Limpar arquivo temporário
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        logger.error(f"Erro na extração de texto: {str(e)}")
        import traceback
        logger.error(f"Stack trace: {traceback.format_exc()}")
        raise e

@api_extrair_texto.route('/api/extrair-texto', methods=['POST'])
def api_extrair_texto_endpoint():
    """
    Endpoint para extração de texto de documentos via AJAX
    """
    try:
        logger.info(f"🔍 API extrair-texto chamada - Method: {request.method}")
        logger.info(f"📋 Files no request: {list(request.files.keys())}")
        logger.info(f"📋 Form data: {list(request.form.keys())}")
        
        # Verificar se arquivo foi enviado
        if 'arquivo' not in request.files:
            logger.error("❌ Nenhum arquivo encontrado no request")
            return jsonify({
                'success': False,
                'error': 'Nenhum arquivo foi enviado'
            }), 400
        
        arquivo = request.files['arquivo']
        logger.info(f"📁 Arquivo recebido: {arquivo.filename}")
        logger.info(f"📏 Tamanho do arquivo: {len(arquivo.read())} bytes")
        arquivo.seek(0)  # Reset file pointer
        
        if arquivo.filename == '':
            logger.error("❌ Nome do arquivo está vazio")
            return jsonify({
                'success': False,
                'error': 'Arquivo vazio'
            }), 400
        
        # Verificar tipo de arquivo
        extensoes_permitidas = ['.pdf', '.doc', '.docx', '.txt', '.md']
        nome_arquivo = arquivo.filename.lower() if arquivo.filename else ''
        logger.info(f"🔍 Verificando extensão do arquivo: {nome_arquivo}")
        
        if not any(nome_arquivo.endswith(ext) for ext in extensoes_permitidas):
            logger.error(f"❌ Extensão não permitida: {nome_arquivo}")
            return jsonify({
                'success': False,
                'error': 'Tipo de arquivo não suportado. Use PDF, DOC, DOCX, TXT ou MD.'
            }), 400
        
        # Extrair texto usando a função existente
        logger.info(f"🔄 Iniciando extração de texto do arquivo: {arquivo.filename}")
        texto_extraido = extrair_texto_arquivo_api(arquivo)
        logger.info(f"📝 Texto extraído com tamanho: {len(texto_extraido) if texto_extraido else 0} caracteres")
        
        if texto_extraido and texto_extraido.strip():
            logger.info(f"✅ Extração bem-sucedida para: {arquivo.filename}")
            return jsonify({
                'success': True,
                'texto': texto_extraido,
                'arquivo': arquivo.filename,
                'tamanho': len(texto_extraido)
            })
        else:
            logger.error(f"❌ Falha na extração de texto para: {arquivo.filename}")
            return jsonify({
                'success': False,
                'error': 'Não foi possível extrair texto do arquivo'
            }), 400
            
    except Exception as e:
        logger.error(f"Erro na API de extração: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

def registrar_api_extrair_texto(app):
    """
    Registra a API de extração de texto na aplicação
    """
    try:
        app.register_blueprint(api_extrair_texto)
        logger.info("✅ API de extração de texto registrada com sucesso")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao registrar API de extração: {str(e)}")
        return False