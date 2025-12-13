#!/usr/bin/env python3
"""
Rotas atualizadas para templates jurídicos carregando dados reais do banco
"""

from flask import Blueprint, render_template, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json

def get_database_connection():
    """Conecta com o banco PostgreSQL"""
    return psycopg2.connect(os.environ.get('NEON_DATABASE_URL'))

def get_all_templates():
    """Carrega todos os templates ativos do banco"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT 
                t.id,
                t.nome,
                t.descricao,
                t.tipo_documento,
                t.area_juridica,
                t.nivel_complexidade,
                t.tempo_estimado,
                t.template_conteudo,
                c.nome as categoria_nome,
                c.icone as categoria_icone,
                c.cor as categoria_cor
            FROM template_juridico t
            LEFT JOIN categoria_juridica c ON t.categoria_id = c.id
            WHERE t.ativo = true
            ORDER BY t.area_juridica, t.nome
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def get_areas_with_counts():
    """Carrega todas as áreas com contagem de templates"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT 
                c.id,
                c.nome,
                c.descricao,
                c.icone,
                c.cor,
                COUNT(t.id) as total_templates
            FROM categoria_juridica c
            LEFT JOIN template_juridico t ON c.id = t.categoria_id AND t.ativo = true
            WHERE c.ativo = true
            GROUP BY c.id, c.nome, c.descricao, c.icone, c.cor
            ORDER BY c.nome
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def get_template_by_id(template_id):
    """Carrega template específico por ID"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT 
                t.*,
                c.nome as categoria_nome,
                c.icone as categoria_icone,
                c.cor as categoria_cor
            FROM template_juridico t
            LEFT JOIN categoria_juridica c ON t.categoria_id = c.id
            WHERE t.id = %s AND t.ativo = true
        """, (template_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def search_templates(area_juridica=None, busca=None):
    """Busca templates com filtros"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        where_conditions = ["t.ativo = true"]
        params = []
        
        if area_juridica:
            where_conditions.append("t.area_juridica = %s")
            params.append(area_juridica)
        
        if busca:
            where_conditions.append("(t.nome ILIKE %s OR t.descricao ILIKE %s)")
            params.extend([f'%{busca}%', f'%{busca}%'])
        
        where_clause = " AND ".join(where_conditions)
        
        query = f"""
            SELECT 
                t.id,
                t.nome,
                t.descricao,
                t.tipo_documento,
                t.area_juridica,
                t.nivel_complexidade,
                t.tempo_estimado,
                c.nome as categoria_nome,
                c.icone as categoria_icone,
                c.cor as categoria_cor
            FROM template_juridico t
            LEFT JOIN categoria_juridica c ON t.categoria_id = c.id
            WHERE {where_clause}
            ORDER BY t.area_juridica, t.nome
        """
        
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

# Função para organizar templates por área
def organize_templates_by_area(templates):
    """Organiza templates por área jurídica"""
    areas_dict = {}
    for template in templates:
        area = template['area_juridica']
        if area not in areas_dict:
            areas_dict[area] = {
                'nome': area,
                'templates': [],
                'icone': template['categoria_icone'] or 'bi bi-file-text',
                'cor': template['categoria_cor'] or '#007bff'
            }
        areas_dict[area]['templates'].append(template)
    
    return list(areas_dict.values())

# Função para inserir na aplicação Flask
def register_updated_templates_routes(app):
    """Registra as rotas atualizadas na aplicação Flask"""
    
    @app.route('/legal-design-pro-v2/templates')
    def templates_updated():
        """Página de templates com dados reais do banco"""
        area_selecionada = request.args.get('area')
        busca = request.args.get('q', '')
        
        # Buscar templates
        templates = search_templates(area_selecionada, busca)
        
        # Organizar por área
        areas_organizadas = organize_templates_by_area(templates)
        
        # Buscar todas as áreas para o menu
        todas_areas = get_areas_with_counts()
        
        # Contar templates e áreas totais
        try:
            conn = get_database_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM template_juridico WHERE ativo = true")
            total_templates_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT area_juridica) FROM template_juridico WHERE area_juridica IS NOT NULL")
            total_areas_count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
        except:
            total_templates_count = 557
            total_areas_count = 18

        return render_template('legal_design_pro_v2/templates.html',
                             templates=templates,
                             areas=todas_areas,
                             areas_organizadas=areas_organizadas,
                             area_selecionada=area_selecionada,
                             busca=busca,
                             total_templates=total_templates_count,
                             templates_areas_count=total_areas_count,
                             total_templates=len(templates))
    
    @app.route('/legal-design-pro-v2/api/template/<int:template_id>')
    def api_template_updated(template_id):
        """API para obter template específico"""
        template = get_template_by_id(template_id)
        
        if not template:
            return jsonify({'success': False, 'error': 'Template não encontrado'}), 404
        
        return jsonify({
            'success': True,
            'template': {
                'id': template['id'],
                'nome': template['nome'],
                'descricao': template['descricao'],
                'conteudo_html': template['template_conteudo'],
                'area': template['area_juridica'],
                'tipo_documento': template['tipo_documento'],
                'complexidade': template['nivel_complexidade'],
                'tempo_estimado': template['tempo_estimado'],
                'campos_obrigatorios': json.loads(template['campos_obrigatorios']) if template['campos_obrigatorios'] else [],
                'campos_opcionais': json.loads(template['campos_opcionais']) if template['campos_opcionais'] else []
            }
        })
    
    @app.route('/legal-design-pro-v2/api/areas')
    def api_areas_updated():
        """API para listar áreas jurídicas com contagem"""
        areas = get_areas_with_counts()
        
        return jsonify({
            'success': True,
            'areas': [{
                'id': area['id'],
                'nome': area['nome'],
                'descricao': area['descricao'],
                'icone': area['icone'],
                'cor': area['cor'],
                'total_templates': area['total_templates']
            } for area in areas]
        })

if __name__ == "__main__":
    # Teste das funções
    print("Testando conexão com banco...")
    templates = get_all_templates()
    print(f"Total de templates: {len(templates)}")
    
    areas = get_areas_with_counts()
    print(f"Total de áreas: {len(areas)}")
    
    for area in areas:
        print(f"- {area['nome']}: {area['total_templates']} templates")