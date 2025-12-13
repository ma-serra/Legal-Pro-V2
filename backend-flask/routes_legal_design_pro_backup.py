"""
Legal Design Pro - Sistema Completo de Criação de Peças Jurídicas com Legal Design
Desenvolvido conforme especificações do prompt oficial
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
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'svg', 'pdf'}
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
            'models': ['gpt-4o', 'gpt-4o-mini', 'o1-preview', 'o1-mini', 'gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo']
        })
    
    if os.environ.get('ANTHROPIC_API_KEY'):
        providers.append({
            'id': 'anthropic', 
            'name': 'Anthropic',
            'models': ['claude-sonnet-4-20250514', 'claude-3-7-sonnet-20250219', 'claude-3-5-sonnet-20241022', 'claude-3-5-haiku-20241022', 'claude-3-opus-20240229', 'claude-3-sonnet-20240229']
        })
    
    if os.environ.get('GEMINI_API_KEY'):
        providers.append({
            'id': 'google',
            'name': 'Google Gemini',
            'models': ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro', 'gemini-2.0-flash-preview-image-generation']
        })
    
    if os.environ.get('DEEPSEEK_API_KEY'):
        providers.append({
            'id': 'deepseek',
            'name': 'DeepSeek', 
            'models': ['deepseek-chat', 'deepseek-coder', 'deepseek-reasoner']
        })
    
    return providers

def generate_legal_piece_with_ai(provider, model, case_data, template_type):
    """
    Gera peça jurídica usando IA
    """
    try:
        if provider == 'openai' and os.environ.get('OPENAI_API_KEY'):
            # Usar OpenAI
            prompt = f"""
            Crie uma {template_type} profissional com as seguintes informações:
            {json.dumps(case_data, ensure_ascii=False, indent=2)}
            
            Formate o documento de forma clara e profissional, incluindo:
            - Cabeçalho apropriado
            - Estrutura bem organizada
            - Fundamentação jurídica adequada
            - Conclusão consistente
            """
            
            response = openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        else:
            return "Provedor de IA não configurado ou indisponível."
            
    except Exception as e:
        logger.error(f"Erro na geração com IA: {str(e)}")
        return f"Erro na geração: {str(e)}"

# ===== ROTAS PRINCIPAIS =====

# Rota principal desativada - páginas funcionam independentemente
# @legal_design_pro_bp.route('/legal-design-pro')
# @legal_design_pro_bp.route('/legal-design-pro/dashboard')
# def dashboard():
#     """Dashboard principal do Legal Design Pro"""
#     return render_template('legal_design_pro/dashboard_dark.html')

# Rota /legal-design-pro/api/stats removida - funcionalidade migrada para /legal-design-pro-v2/

# Rotas de editor /legal-design-pro removidas - funcionalidade migrada para /legal-design-pro-v2/

# Rota /legal-design-pro/templates removida - funcionalidade migrada para /legal-design-pro-v2/

@legal_design_pro_bp.route('/legal-design-pro/api/templates-list')
def api_templates_list():
    """API para listar templates com filtro dinâmico por área"""
    try:
        area_filter = request.args.get('area', 'all')
        
        # Query incluindo template_conteudo
        query_text = """
            SELECT 
                id,
                nome,
                COALESCE(descricao, 'Template profissional') as descricao,
                COALESCE(area_juridica, 'Geral') as area_juridica,
                COALESCE(tipo_documento, 'Documento') as tipo_documento,
                COALESCE(total_utilizacoes, 0) as uso_contador,
                COALESCE(template_conteudo, '') as template_conteudo
            FROM template_juridico 
            WHERE ativo = true
        """
        
        params = {}
        
        # Aplicar filtro por área se especificado
        if area_filter and area_filter != 'all':
            area_map = {
                'Direito Penal': 'Direito Penal',
                'Direito Civil': 'Direito Civil', 
                'Direito Trabalhista': 'Direito Trabalhista',
                'Direito Empresarial': 'Direito Empresarial',
                'Direito Bancário': 'Direito Bancário',
                'Direito do Consumidor': 'Direito do Consumidor',
                'Direito Agrário': 'Direito Agrário',
                'Recuperação de Crédito': 'Recuperação de Crédito',
                'Direito Securitário': 'Direito Securitário',
                'Direito Tributário': 'Direito Tributário'
            }
            
            if area_filter in area_map:
                query_text += " AND area_juridica = :area_filter"
                params['area_filter'] = area_map[area_filter]
        
        query_text += " ORDER BY total_utilizacoes DESC NULLS LAST, id ASC LIMIT 100"
        
        query = text(query_text)
        
        result = db.session.execute(query, params)
        templates = result.fetchall()
        
        # Converter para lista de dicionários
        templates_data = []
        for template in templates:
            templates_data.append({
                'id': template.id,
                'nome': template.nome,
                'descricao': template.descricao or 'Template jurídico',
                'area_juridica': template.area_juridica or 'geral',
                'tipo_documento': template.tipo_documento or 'Documento',
                'uso_contador': getattr(template, 'uso_contador', 0),
                'template_conteudo': getattr(template, 'template_conteudo', ''),
                'total_utilizacoes': getattr(template, 'total_utilizacoes', 0)
            })
        
        return jsonify({
            'success': True,
            'templates': templates_data,
            'total': len(templates_data)
        })
        
    except Exception as e:
        logger.error(f"Erro na API de templates: {str(e)}")
        return jsonify({'success': False, 'error': str(e), 'templates': []})

@legal_design_pro_bp.route('/legal-design-pro/api/template/<int:template_id>')
def api_get_template(template_id):
    """API para obter conteúdo completo de um template específico"""
    try:
        query = text("""
            SELECT 
                id,
                nome,
                descricao,
                conteudo_html,
                CASE 
                    WHEN area_juridica_id = 1 THEN 'Direito Civil'
                    WHEN area_juridica_id = 2 THEN 'Direito Penal'
                    WHEN area_juridica_id = 3 THEN 'Direito Trabalhista'
                    WHEN area_juridica_id = 4 THEN 'Direito Empresarial'
                    WHEN area_juridica_id = 5 THEN 'Direito Bancário'
                    WHEN area_juridica_id = 6 THEN 'Direito do Consumidor'
                    WHEN area_juridica_id = 7 THEN 'Direito Agrário'
                    ELSE 'Geral'
                END as area_juridica,
                CASE 
                    WHEN tipo_documento_id = 1 THEN 'Petição Inicial'
                    WHEN tipo_documento_id = 2 THEN 'Contestação'
                    WHEN tipo_documento_id = 3 THEN 'Recurso'
                    WHEN tipo_documento_id = 4 THEN 'Contrato'
                    WHEN tipo_documento_id = 5 THEN 'Parecer'
                    WHEN tipo_documento_id = 9 THEN 'Peça Processual'
                    ELSE 'Documento'
                END as tipo_documento,
                COALESCE(uso_contador, 0) as uso_contador
            FROM legal_templates_juridicos 
            WHERE id = :template_id
        """)
        
        result = db.session.execute(query, {'template_id': template_id})
        template = result.fetchone()
        
        if not template:
            return jsonify({'success': False, 'error': 'Template não encontrado'})
        
        # Incrementar contador de uso
        update_query = text("""
            UPDATE legal_templates_juridicos 
            SET uso_contador = COALESCE(uso_contador, 0) + 1,
                modificado_em = :modified_at
            WHERE id = :template_id
        """)
        
        db.session.execute(update_query, {
            'template_id': template_id,
            'modified_at': datetime.now()
        })
        db.session.commit()
        
        template_data = {
            'id': template.id,
            'nome': template.nome,
            'descricao': template.descricao,
            'area_juridica': template.area_juridica,
            'tipo_documento': template.tipo_documento,
            'conteudo_html': template.conteudo_html or '',
            'uso_contador': (template.uso_contador or 0) + 1
        }
        
        return jsonify({
            'success': True,
            'template': template_data
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter template {template_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@legal_design_pro_bp.route('/legal-design-pro/api/templates')
def api_templates_simple():
    """API para listar templates por área jurídica"""
    try:
        area_filter = request.args.get('area', 'all')
        search_query = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 12))
        
        # Query usando tabela principal template_juridico
        query_text = """
            SELECT 
                t.id,
                t.nome,
                t.descricao,
                t.area_juridica,
                t.tipo_documento,
                t.nivel_complexidade as complexidade,
                t.tempo_estimado,
                t.total_utilizacoes as uso_contador,
                t.versao,
                t.criado_em,
                t.modificado_em,
                c.nome as categoria_nome
            FROM template_juridico t
            LEFT JOIN categoria_juridica c ON t.categoria_id = c.id
            WHERE t.ativo = true
        """
        
        # Adicionar filtros à query
        params = {}
        
        # Filtro por área
        if area_filter != 'all':
            area_map = {
                'civil': 'Direito Civil',
                'trabalhista': 'Direito Trabalhista', 
                'empresarial': 'Direito Empresarial',
                'penal': 'Direito Penal',
                'agrario': 'Direito Agrário',
                'securitario': 'Direito Securitário',
                'tributario': 'Direito Tributário'
            }
            if area_filter in area_map:
                query_text += " AND t.area_juridica = :area_filter"
                params['area_filter'] = area_map[area_filter]
        
        # Filtro de busca
        if search_query:
            query_text += " AND (t.nome ILIKE :search OR t.descricao ILIKE :search)"
            params['search'] = f"%{search_query}%"
        
        # Ordenação
        query_text += " ORDER BY t.total_utilizacoes DESC NULLS LAST, t.id ASC"
        
        # Executar query
        result = db.session.execute(text(query_text), params)
        templates = result.fetchall()
        
        # Paginação manual
        total = len(templates)
        start = (page - 1) * per_page
        end = start + per_page
        templates_page = templates[start:end]
        
        # Criar objeto similar ao paginate
        class SimplePagination:
            def __init__(self, items, total, page, per_page):
                self.items = items
                self.total = total
                self.page = page
                self.per_page = per_page
                self.pages = (total + per_page - 1) // per_page
                self.has_prev = page > 1
                self.has_next = page < self.pages
                
        templates_paginated = SimplePagination(templates_page, total, page, per_page)
        
        # Serializar resultados
        templates_data = []
        for template in templates_paginated.items:
            templates_data.append({
                'id': template.id,
                'nome': template.nome,
                'descricao': template.descricao or '',
                'area_juridica': {
                    'nome': template.area_juridica or 'Geral',
                    'icone': 'fas fa-balance-scale',
                    'cor_tema': '#007bff'
                },
                'tipo_documento': {
                    'nome': template.tipo_documento or 'Documento',
                    'categoria': template.categoria_nome or 'Geral',
                    'icone': 'fas fa-file-alt'
                },
                'complexidade': template.complexidade or 'Médio',
                'tempo_estimado': template.tempo_estimado or 30,
                'uso_contador': template.uso_contador or 0,
                'versao': template.versao or '1.0',
                'criado_em': template.criado_em.isoformat() if template.criado_em else datetime.now().isoformat(),
                'modificado_em': template.modificado_em.isoformat() if template.modificado_em else datetime.now().isoformat()
            })
        
        return jsonify({
            'success': True,
            'templates': templates_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': templates_paginated.total,
                'pages': templates_paginated.pages,
                'has_prev': templates_paginated.has_prev,
                'has_next': templates_paginated.has_next
            }
        })
        
    except Exception as e:
        logger.error(f"Erro na API de templates: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@legal_design_pro_bp.route('/legal-design-pro/api/template/<int:template_id>')
def api_template_content(template_id):
    """API para obter conteúdo completo de um template com dados expandidos"""
    try:
        # Buscar template na tabela legal_templates_juridicos com conteúdo expandido
        query = text("""
            SELECT id, nome, descricao, conteudo_html,
                   CASE 
                       WHEN area_juridica_id = 1 THEN 'Direito Civil'
                       WHEN area_juridica_id = 2 THEN 'Direito Penal'
                       WHEN area_juridica_id = 3 THEN 'Direito Trabalhista'
                       WHEN area_juridica_id = 4 THEN 'Direito Empresarial'
                       WHEN area_juridica_id = 5 THEN 'Direito Bancário'
                       WHEN area_juridica_id = 6 THEN 'Direito do Consumidor'
                       WHEN area_juridica_id = 7 THEN 'Direito Agrário'
                       ELSE 'Geral'
                   END as area_juridica,
                   CASE 
                       WHEN tipo_documento_id = 1 THEN 'Petição Inicial'
                       WHEN tipo_documento_id = 2 THEN 'Contestação'
                       WHEN tipo_documento_id = 3 THEN 'Recurso'
                       WHEN tipo_documento_id = 4 THEN 'Contrato'
                       WHEN tipo_documento_id = 5 THEN 'Parecer'
                       WHEN tipo_documento_id = 9 THEN 'Peça Processual'
                       ELSE 'Documento'
                   END as tipo_documento,
                   COALESCE(uso_contador, 0) as uso_contador
            FROM legal_templates_juridicos 
            WHERE id = :template_id
        """)
        
        result = db.session.execute(query, {'template_id': template_id})
        template = result.fetchone()
        
        if not template:
            return jsonify({'success': False, 'error': 'Template não encontrado'})
        
        # Incrementar contador de uso na tabela correta
        update_query = text("""
            UPDATE legal_templates_juridicos 
            SET uso_contador = COALESCE(uso_contador, 0) + 1
            WHERE id = :template_id
        """)
        db.session.execute(update_query, {'template_id': template_id})
        db.session.commit()
        
        return jsonify({
            'success': True,
            'id': template.id,
            'nome': template.nome,
            'descricao': template.descricao or 'Template jurídico profissional',
            'conteudo_html': template.conteudo_html,
            'area_juridica': template.area_juridica or 'Geral',
            'tipo_documento': template.tipo_documento or 'Documento',
            'uso_contador': template.uso_contador + 1
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter template {template_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@legal_design_pro_bp.route('/legal-design-pro/api/areas-juridicas')
def api_areas_juridicas():
    """API para listar áreas jurídicas disponíveis"""
    try:
        areas = db.session.query(LegalAreaJuridica).filter_by(ativo=True).order_by(LegalAreaJuridica.ordem_exibicao).all()
        
        areas_data = []
        for area in areas:
            template_count = db.session.query(LegalTemplateJuridico).filter_by(
                area_juridica_id=area.id, 
                ativo=True
            ).count()
            
            areas_data.append({
                'id': area.id,
                'nome': area.nome,
                'icone': area.icone,
                'descricao': area.descricao,
                'cor_tema': area.cor_tema,
                'total_templates': template_count
            })
        
        return jsonify({
            'success': True,
            'areas': areas_data
        })
        
    except Exception as e:
        logger.error(f"Erro na API de áreas jurídicas: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@legal_design_pro_bp.route('/legal-design-pro/generate', methods=['POST'])
def generate_with_ai():
    """Gera peça jurídica usando IA"""
    try:
        data = request.get_json()
        
        provider = data.get('provider', 'openai')
        model = data.get('model', 'gpt-4o')
        case_data = data.get('case_data', {})
        template_type = data.get('template_type', 'petição')
        
        content = generate_legal_piece_with_ai(provider, model, case_data, template_type)
        
        # Salvar no banco (simulado)
        piece_id = str(uuid.uuid4())
        
        return jsonify({
            'success': True,
            'piece_id': piece_id,
            'content': content,
            'provider': provider,
            'model': model
        })
        
    except Exception as e:
        logger.error(f"Erro na geração: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@legal_design_pro_bp.route('/legal-design-pro/salvar-documento', methods=['POST'])
def save_document():
    """Salva documento jurídico no banco de dados"""
    try:
        data = request.get_json()
        
        title = data.get('title', 'Documento Sem Título')
        content = data.get('content', '')
        area = data.get('area', 'Geral')
        word_count = data.get('word_count', 0)
        user_id = current_user.id if current_user.is_authenticated else 1
        
        # Salvar no banco usando SQL direto
        document_id = str(uuid.uuid4())
        
        sql_query = text("""
            INSERT INTO legal_documents (id, title, content, area, word_count, user_id, created_at, updated_at)
            VALUES (:id, :title, :content, :area, :word_count, :user_id, :created_at, :updated_at)
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                content = EXCLUDED.content,
                area = EXCLUDED.area,
                word_count = EXCLUDED.word_count,
                updated_at = EXCLUDED.updated_at
        """)
        
        db.session.execute(sql_query, {
            'id': document_id,
            'title': title,
            'content': content,
            'area': area,
            'word_count': word_count,
            'user_id': user_id,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        })
        db.session.commit()
        
        logger.info(f"Documento salvo: {document_id} - {title}")
        
        return jsonify({
            'success': True,
            'document_id': document_id,
            'message': 'Documento salvo com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Erro ao salvar documento: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@legal_design_pro_bp.route('/legal-design-pro/pesquisa-juridica', methods=['POST'])
def legal_research():
    """Realiza pesquisa jurídica inteligente"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        area = data.get('area', 'Geral')
        provider = data.get('provider', 'openai')
        
        if not query:
            return jsonify({'success': False, 'error': 'Query de pesquisa é obrigatória'})
        
        # Realizar pesquisa usando IA
        if provider == 'openai' and os.environ.get('OPENAI_API_KEY'):
            prompt = f"""
            Realize uma pesquisa jurídica sobre: {query}
            Área do direito: {area}
            
            Forneça:
            1. Fundamentação legal relevante
            2. Jurisprudência aplicável
            3. Doutrina relacionada
            4. Precedentes importantes
            5. Análise prática
            
            Seja preciso e cite fontes quando possível.
            """
            
            response = openai.chat.completions.create(
                model='gpt-4o',
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500
            )
            
            research_result = response.choices[0].message.content
            
            return jsonify({
                'success': True,
                'query': query,
                'area': area,
                'result': research_result,
                'provider': provider,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False, 
                'error': 'Provedor de IA não configurado. Configure OPENAI_API_KEY para usar esta funcionalidade.'
            })
            
    except Exception as e:
        logger.error(f"Erro na pesquisa jurídica: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@legal_design_pro_bp.route('/legal-design-pro/exportar-documento', methods=['POST'])
def export_document():
    """Exporta documento em formato PDF usando ReportLab"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.units import cm
        from reportlab.lib.colors import black
        from bs4 import BeautifulSoup
        import re
        
        data = request.get_json()
        title = data.get('title', 'Documento Jurídico')
        content = data.get('content', '')
        area = data.get('area', 'Geral')
        
        # Criar PDF em memória
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            alignment=1,  # Centro
            textColor=black
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            alignment=0,  # Justificado
            textColor=black
        )
        
        # Processar conteúdo HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # Limpar HTML e converter para texto
        clean_content = soup.get_text()
        clean_content = re.sub(r'\n\s*\n', '\n\n', clean_content)
        
        # Construir documento
        story = []
        
        # Título
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Área jurídica
        story.append(Paragraph(f"Área: {area}", normal_style))
        story.append(Spacer(1, 0.3*cm))
        
        # Conteúdo
        paragraphs = clean_content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), normal_style))
                story.append(Spacer(1, 0.2*cm))
        
        # Gerar PDF
        doc.build(story)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"{title.replace(' ', '_')}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Erro na exportação: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro ao exportar: {str(e)}'})

def export_to_docx(piece, conteudo, visual_elements):
    """Exporta peça para formato DOCX"""
    doc = Document()
    
    # Adicionar título
    title = doc.add_heading(piece.get('title', 'Documento'), 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Adicionar conteúdo
    doc.add_paragraph(conteudo)
    
    # Salvar em buffer
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    
    filename = f"{piece.get('title', 'documento')}.docx"
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )

def export_to_pdf(piece, conteudo, visual_elements):
    """Exporta peça para formato PDF usando WeasyPrint"""
    try:
        from weasyprint import HTML
        
        html_content = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <title>{piece.get('title', 'Documento')}</title>
        </head>
        <body>
            <h1>{piece.get('title', 'Documento')}</h1>
            <p>{conteudo}</p>
        </body>
        </html>
        """
        
        buffer = io.BytesIO()
        HTML(string=html_content).write_pdf(buffer)
        buffer.seek(0)
        
        filename = f"{piece.get('title', 'documento')}.pdf"
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except ImportError:
        return jsonify({'error': 'WeasyPrint não está instalado'}), 500

def export_to_html(piece, conteudo, visual_elements):
    """Exporta peça para formato HTML"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{piece.get('title', 'Documento')}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #2c3e50; text-align: center; }}
            p {{ line-height: 1.6; }}
        </style>
    </head>
    <body>
        <h1>{piece.get('title', 'Documento')}</h1>
        <p>{conteudo}</p>
    </body>
    </html>
    """
    
    buffer = io.BytesIO()
    buffer.write(html_content.encode('utf-8'))
    buffer.seek(0)
    
    filename = f"{piece.get('title', 'documento')}.html"
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='text/html'
    )

@legal_design_pro_bp.route('/legal-design-pro/templates')
def templates():
    """Biblioteca de templates jurídicos"""
    try:
        # Contar templates ativos do banco principal
        template_count_query = text("SELECT COUNT(*) as total FROM template_juridico WHERE ativo = true")
        result = db.session.execute(template_count_query)
        templates_count = result.scalar() or 0
        
        # Contar áreas jurídicas distintas
        areas_query = text("SELECT COUNT(DISTINCT area_juridica) as total FROM template_juridico WHERE ativo = true AND area_juridica IS NOT NULL")
        areas_result = db.session.execute(areas_query)
        areas_count = areas_result.scalar() or 0
        
        # Obter templates em destaque (mais utilizados)
        featured_query = text("""
            SELECT id, nome, descricao, area_juridica, total_utilizacoes 
            FROM template_juridico 
            WHERE ativo = true 
            ORDER BY total_utilizacoes DESC NULLS LAST, id ASC 
            LIMIT 6
        """)
        featured_result = db.session.execute(featured_query)
        featured_templates = []
        
        for row in featured_result:
            featured_templates.append({
                'id': row.id,
                'nome': row.nome,
                'descricao': row.descricao or '',
                'area_juridica': row.area_juridica or 'Geral',
                'total_utilizacoes': row.total_utilizacoes or 0
            })
        
        logger.info(f"Legal Design Pro Templates: {templates_count} templates encontrados")
        
        return render_template('legal_design_pro/templates_dark.html',
                             templates_count=templates_count,
                             areas_count=areas_count,
                             featured_templates=featured_templates)
                             
    except Exception as e:
        logger.error(f"Erro ao carregar templates Legal Design Pro: {str(e)}")
        # Fallback para dados básicos em caso de erro
        return render_template('legal_design_pro/templates_dark.html',
                             templates_count=0,
                             areas_count=0,
                             featured_templates=[])

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

@legal_design_pro_bp.route('/legal-design-pro/analytics')
def analytics():
    """Analytics e métricas do Legal Design Pro"""
    return render_template('legal_design_pro/analytics.html')

def init_legal_design_pro():
    """Inicializa o módulo Legal Design Pro"""
    try:
        # Criar tabela de peças se não existir
        create_table_query = text("""
            CREATE TABLE IF NOT EXISTS legal_design_pieces (
                id VARCHAR(36) PRIMARY KEY,
                user_id INTEGER REFERENCES "user"(id),
                titulo VARCHAR(255) NOT NULL,
                area_juridica VARCHAR(100),
                tipo_documento VARCHAR(100),
                conteudo_json TEXT,
                visual_elements TEXT,
                template_id INTEGER,
                ai_generated BOOLEAN DEFAULT FALSE,
                ai_provider VARCHAR(50),
                ai_model VARCHAR(50),
                status VARCHAR(20) DEFAULT 'rascunho',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_legal_design_pieces_user_id ON legal_design_pieces(user_id);
            CREATE INDEX IF NOT EXISTS idx_legal_design_pieces_area ON legal_design_pieces(area_juridica);
            CREATE INDEX IF NOT EXISTS idx_legal_design_pieces_status ON legal_design_pieces(status);
        """)
        
        db.session.execute(create_table_query)
        db.session.commit()
        
        logger.info("✅ Legal Design Pro inicializado com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar Legal Design Pro: {str(e)}")
        db.session.rollback()
        return False