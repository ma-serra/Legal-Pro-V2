"""
Legal Design Pro - Rotas Complementares (sem /legal-design-pro)
Mantém apenas funcionalidades auxiliares e páginas independentes
"""

import os
import json
import uuid
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_login import current_user
from werkzeug.utils import secure_filename
from sqlalchemy import text
from models import db
from models_legal_design import LegalAreaJuridica, LegalTipoDocumento, LegalTemplateJuridico, LegalHistoricoUsoTemplate
import openai
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
import io
import base64
import tempfile

# Configuração do Blueprint
legal_design_pro_bp = Blueprint('legal_design_pro', __name__)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração OpenAI
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Configurações do módulo
UPLOAD_FOLDER = 'uploads/legal_design'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'svg', 'pdf', 'docx', 'doc'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Criação do diretório de upload
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Verifica se o arquivo é permitido"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_ai_providers():
    """Retorna provedores de IA disponíveis"""
    providers = []
    
    if os.environ.get('OPENAI_API_KEY'):
        providers.append({
            'id': 'openai',
            'name': 'OpenAI',
            'models': ['gpt-4o', 'gpt-4', 'gpt-3.5-turbo'],
            'status': 'active'
        })
    
    return providers

def generate_legal_piece_with_ai(provider, model, case_data, template_type):
    """Gera peça jurídica usando IA"""
    try:
        if provider == 'openai' and openai.api_key:
            prompt = f"""
            Você é um advogado especialista em {case_data.get('area', 'direito')}. 
            Crie uma {template_type} profissional considerando:
            
            Dados do caso: {json.dumps(case_data, ensure_ascii=False, indent=2)}
            
            Formate a resposta em HTML usando elementos legais apropriados.
            """
            
            response = openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        else:
            raise Exception("Provedor de IA não configurado")
            
    except Exception as e:
        logger.error(f"Erro na geração de IA: {str(e)}")
        raise e

# ===== ROTAS AUXILIARES (SEM /legal-design-pro) =====

@legal_design_pro_bp.route('/legal-design-pro/biblioteca')
def biblioteca():
    """Biblioteca de recursos e documentos"""
    return render_template('legal_design_pro/biblioteca_dark.html',
                         documents_count=150,
                         categories=["Contratos", "Petições", "Pareceres", "Recursos"])

@legal_design_pro_bp.route('/legal-design-pro/ai-assistant')
def ai_assistant():
    """Assistente de IA integrado"""
    return render_template('legal_design_pro/ai_assistant_dark.html',
                         available_models=["gpt-4o", "claude-3-5-sonnet"],
                         features=["Geração de texto", "Análise de documentos", "Sugestões de melhoria"])

@legal_design_pro_bp.route('/legal-design-pro/configuracoes')
def configuracoes():
    """Configurações do Legal Design Pro"""
    return render_template('legal_design_pro/configuracoes_dark.html',
                         user_preferences={},
                         system_settings={})

# ===== APIS AUXILIARES =====

@legal_design_pro_bp.route('/legal-design-pro/api/upload-image', methods=['POST'])
def upload_image():
    """Upload de imagem para uso no editor"""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'Nenhum arquivo enviado'})
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nenhum arquivo selecionado'})
        
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = str(int(datetime.now().timestamp()))
            filename = f"{timestamp}_{filename}"
            
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'url': f'/uploads/legal_design/{filename}'
            })
        else:
            return jsonify({'success': False, 'error': 'Tipo de arquivo não permitido'})
            
    except Exception as e:
        logger.error(f"Erro no upload: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@legal_design_pro_bp.route('/legal-design-pro/api/export-docx', methods=['POST'])
def export_docx():
    """Exporta documento para DOCX"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        title = data.get('title', 'Documento Legal')
        
        # Criar documento Word
        doc = Document()
        
        # Adicionar título
        title_paragraph = doc.add_heading(title, 0)
        title_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Adicionar conteúdo (simplificado - remove HTML)
        import re
        clean_content = re.sub('<[^<]+?>', '', content)
        doc.add_paragraph(clean_content)
        
        # Salvar em buffer
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        # Preparar resposta
        filename = f"{title.replace(' ', '_')}.docx"
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        logger.error(f"Erro na exportação DOCX: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@legal_design_pro_bp.route('/legal-design-pro-v2/upload-docx', methods=['POST'])
def upload_docx():
    """Endpoint para upload e processamento de arquivos DOCX"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Nenhum arquivo enviado'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nenhum arquivo selecionado'})
        
        # Verificar extensão do arquivo
        if not file.filename or not file.filename.lower().endswith(('.docx', '.doc')):
            return jsonify({'success': False, 'error': 'Formato de arquivo não suportado'})
        
        # Verificar tamanho do arquivo (máximo 10MB)
        file.seek(0, 2)  # Ir para o final do arquivo
        file_size = file.tell()
        file.seek(0)  # Voltar ao início
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            return jsonify({'success': False, 'error': 'Arquivo muito grande (máximo 10MB)'})
        
        # Processar arquivo DOCX
        try:
            # Ler o arquivo DOCX usando BytesIO
            from io import BytesIO
            file_bytes = BytesIO(file.read())
            doc = Document(file_bytes)
            
            # Extrair conteúdo do documento
            content_html = convert_docx_to_html(doc)
            
            # Extrair título (primeiro parágrafo ou nome do arquivo)
            title = extract_document_title(doc, file.filename)
            
            return jsonify({
                'success': True,
                'content': content_html,
                'title': title,
                'filename': file.filename,
                'size': file_size
            })
            
        except Exception as e:
            logger.error(f"Erro ao processar DOCX: {str(e)}")
            return jsonify({
                'success': False, 
                'error': f'Erro ao processar arquivo DOCX: {str(e)}'
            })
        
    except Exception as e:
        logger.error(f"Erro no upload DOCX: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

def convert_docx_to_html(doc):
    """Converte documento DOCX para HTML formatado"""
    html_parts = []
    
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            # Detectar estilos de cabeçalho
            style = paragraph.style.name.lower()
            text = paragraph.text.strip()
            
            if 'heading 1' in style or 'título 1' in style:
                html_parts.append(f'<h1>{text}</h1>')
            elif 'heading 2' in style or 'título 2' in style:
                html_parts.append(f'<h2>{text}</h2>')
            elif 'heading 3' in style or 'título 3' in style:
                html_parts.append(f'<h3>{text}</h3>')
            else:
                # Verificar formatação de texto
                formatted_text = format_paragraph_text(paragraph)
                html_parts.append(f'<p>{formatted_text}</p>')
    
    # Processar tabelas
    for table in doc.tables:
        table_html = convert_table_to_html(table)
        html_parts.append(table_html)
    
    return '\n'.join(html_parts)

def format_paragraph_text(paragraph):
    """Formata texto do parágrafo preservando formatação completa"""
    formatted_text = ""
    
    for run in paragraph.runs:
        text = run.text
        if not text:
            continue
            
        # Construir estilos CSS inline
        styles = []
        
        # Aplicar formatação básica
        if run.bold:
            styles.append('font-weight: bold')
        if run.italic:
            styles.append('font-style: italic')
        if run.underline:
            styles.append('text-decoration: underline')
            
        # Preservar cor do texto
        if hasattr(run.font, 'color') and run.font.color.rgb:
            color_hex = f"#{run.font.color.rgb}"
            styles.append(f'color: {color_hex}')
            
        # Preservar tamanho da fonte
        if hasattr(run.font, 'size') and run.font.size:
            font_size = run.font.size.pt
            styles.append(f'font-size: {font_size}pt')
            
        # Preservar família da fonte
        if hasattr(run.font, 'name') and run.font.name:
            styles.append(f'font-family: "{run.font.name}"')
        
        # Aplicar estilos se existirem
        if styles:
            style_attr = '; '.join(styles)
            text = f'<span style="{style_attr}">{text}</span>'
        
        formatted_text += text
    
    return formatted_text if formatted_text else paragraph.text

def convert_table_to_html(table):
    """Converte tabela do DOCX para HTML preservando formatação completa"""
    html_parts = ['<div class="table-container" style="margin: 20px 0; overflow-x: auto;">']
    html_parts.append('<table style="border-collapse: collapse; width: 100%; font-family: inherit;">')
    
    for i, row in enumerate(table.rows):
        html_parts.append('<tr>')
        
        for j, cell in enumerate(row.cells):
            # Determinar se é cabeçalho (primeira linha)
            tag = 'th' if i == 0 else 'td'
            
            # Extrair estilos da célula
            cell_styles = []
            
            # Bordas padrão
            cell_styles.append('border: 1px solid #dee2e6')
            cell_styles.append('padding: 8px')
            cell_styles.append('text-align: left')
            
            # Cor de fundo para cabeçalhos
            if i == 0:
                cell_styles.append('background-color: #f8f9fa')
                cell_styles.append('font-weight: bold')
            
            # Processar texto da célula com formatação
            cell_text = ""
            for paragraph in cell.paragraphs:
                if paragraph.text.strip():
                    formatted_text = format_paragraph_text(paragraph)
                    cell_text += formatted_text
            
            # Montar célula com estilos
            style_attr = '; '.join(cell_styles)
            html_parts.append(f'<{tag} style="{style_attr}">{cell_text}</{tag}>')
        
        html_parts.append('</tr>')
    
    html_parts.append('</table>')
    html_parts.append('</div>')
    
    return '\n'.join(html_parts)

def extract_document_title(doc, filename):
    """Extrai título do documento"""
    # Tentar extrair o primeiro parágrafo como título
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text = paragraph.text.strip()
            if len(text) < 100:  # Títulos geralmente são curtos
                return text
            break
    
    # Se não encontrar título adequado, usar nome do arquivo
    return filename.rsplit('.', 1)[0]

@legal_design_pro_bp.route('/legal-design-pro/api/providers')
def api_providers():
    """Retorna provedores de IA disponíveis"""
    try:
        providers = get_ai_providers()
        return jsonify({
            'success': True,
            'providers': providers
        })
    except Exception as e:
        logger.error(f"Erro na API de provedores: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

# ===== INICIALIZAÇÃO =====

def init_legal_design_pro():
    """Inicializa o módulo Legal Design Pro"""
    try:
        logger.info("✅ Legal Design Pro inicializado com sucesso")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar Legal Design Pro: {str(e)}")
        return False

# Inicializar quando o módulo for importado
init_legal_design_pro()