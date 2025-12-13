"""
API para carregar conteúdo real de templates do banco de dados
"""

from flask import Blueprint, jsonify, request
from main import db
from sqlalchemy import text
import os

template_content_bp = Blueprint('template_content', __name__)

@template_content_bp.route('/api/template-content/<template_name>')
def get_template_content(template_name):
    """Carrega conteúdo real de template do banco de dados"""
    try:
        area = request.args.get('area', '')
        
        # Mapear nomes de template para busca no banco
        template_mapping = {
            'denuncia-criminal': 'Denúncia Criminal',
            'defesa-previa': 'Defesa Prévia',
            'habeas-corpus': 'Habeas Corpus',
            'alegacoes-finais': 'Alegações Finais',
            'reclamacao-trabalhista': 'Reclamação Trabalhista',
            'defesa-trabalhista': 'Defesa Trabalhista',
            'acordo-trabalhista': 'Acordo Trabalhista',
            'rescisao-trabalhista': 'Rescisão Trabalhista',
            'contrato-social': 'Contrato Social',
            'acordo-acionistas': 'Acordo de Acionistas',
            'due-diligence': 'Due Diligence',
            'fusao-aquisicao': 'Fusão e Aquisição',
            'revisao-bancaria': 'Revisão Bancária',
            'defesa-bancaria': 'Defesa Bancária',
            'financiamento': 'Financiamento',
            'cartao-credito': 'Cartão de Crédito'
        }
        
        template_real_name = template_mapping.get(template_name, template_name.replace('-', ' ').title())
        
        # Buscar template na tabela legal_templates_juridicos
        query = text("""
            SELECT id, nome, conteudo_html,
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
                   END as tipo_documento
            FROM legal_templates_juridicos 
            WHERE nome ILIKE :template_name
            LIMIT 1
        """)
        
        result = db.session.execute(query, {'template_name': f'%{template_real_name}%'})
        template = result.fetchone()
        
        if not template:
            # Buscar por nome exato
            query = text("""
                SELECT id, nome, conteudo_html,
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
                       END as tipo_documento
                FROM legal_templates_juridicos 
                WHERE conteudo_html IS NOT NULL AND LENGTH(conteudo_html) > 500
                LIMIT 1
            """)
            result = db.session.execute(query)
            template = result.fetchone()
        
        if template and template.conteudo_html:
            return jsonify({
                'success': True,
                'template': {
                    'id': template.id,
                    'nome': template.nome,
                    'conteudo_html': template.conteudo_html,
                    'area_juridica': template.area_juridica,
                    'tipo_documento': template.tipo_documento
                }
            })
        
        return jsonify({
            'success': False,
            'message': f'Template {template_name} não encontrado no banco de dados'
        }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao carregar template: {str(e)}'
        }), 500

@template_content_bp.route('/api/template/<int:template_id>')
def get_template_by_id(template_id):
    """Carrega template específico por ID para o editor"""
    try:
        # Buscar na tabela legal_templates_juridicos com o conteúdo expandido
        query = text("""
            SELECT id, nome, conteudo_html, 
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
                   COALESCE(uso_contador, 0) as total_utilizacoes
            FROM legal_templates_juridicos 
            WHERE id = :template_id
        """)
        
        result = db.session.execute(query, {'template_id': template_id})
        template = result.fetchone()
        
        if not template:
            return jsonify({
                'success': False,
                'message': f'Template com ID {template_id} não encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'id': template.id,
            'nome': template.nome,
            'conteudo_html': template.conteudo_html,
            'area_juridica': template.area_juridica,
            'tipo_documento': template.tipo_documento,
            'total_utilizacoes': template.total_utilizacoes or 0
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao carregar template: {str(e)}'
        }), 500

@template_content_bp.route('/api/templates-list')
def list_all_templates():
    """Lista todos os templates disponíveis no banco"""
    try:
        query = text("""
            SELECT id, nome, conteudo_html,
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
                   END as tipo_documento
            FROM legal_templates_juridicos 
            WHERE conteudo_html IS NOT NULL AND LENGTH(conteudo_html) > 100
            ORDER BY nome ASC
        """)
        
        result = db.session.execute(query)
        templates = result.fetchall()
        
        template_list = []
        for template in templates:
            template_list.append({
                'id': template.id,
                'nome': template.nome,
                'area_juridica': template.area_juridica,
                'tipo_documento': template.tipo_documento,
                'has_content': bool(template.conteudo_html)
            })
        
        return jsonify({
            'success': True,
            'templates': template_list,
            'total': len(template_list)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar templates: {str(e)}'
        }), 500

def register_template_content_api(app):
    """Registra a API de conteúdo de templates"""
    app.register_blueprint(template_content_bp, url_prefix='/api/templates')
    print("✅ API de conteúdo de templates registrada")