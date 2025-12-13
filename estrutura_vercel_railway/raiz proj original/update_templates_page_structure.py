#!/usr/bin/env python3
"""
Script para atualizar a estrutura da página de templates para carregar dados reais
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

def update_complete_legal_design_pro_v2():
    """Atualiza o arquivo complete_legal_design_pro_v2.py para carregar dados reais"""
    
    # Conteúdo atualizado para carregar dados do banco
    new_content = '''#!/usr/bin/env python3
"""
Legal Design Pro V2 - Sistema completo com dados reais do banco
"""

from flask import Blueprint, render_template, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json

legal_design_pro_v2_bp = Blueprint('legal_design_pro_v2', __name__, url_prefix='/legal-design-pro-v2')

def get_database_connection():
    """Conecta com o banco PostgreSQL"""
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

def get_all_templates_from_db():
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
                t.nivel_complexidade as complexidade,
                t.tempo_estimado,
                t.template_conteudo,
                c.nome as area_nome,
                c.icone as area_icone,
                c.cor as area_cor,
                c.id as area_id
            FROM template_juridico t
            LEFT JOIN categoria_juridica c ON t.categoria_id = c.id
            WHERE t.ativo = true
            ORDER BY t.area_juridica, t.nome
        """)
        templates = cursor.fetchall()
        
        # Converter para estrutura esperada pelo template
        formatted_templates = []
        for t in templates:
            formatted_templates.append({
                'id': t['id'],
                'nome': t['nome'],
                'descricao': t['descricao'],
                'tipo_documento': t['tipo_documento'],
                'complexidade': t['complexidade'],
                'tempo_estimado': t['tempo_estimado'],
                'template_conteudo': t['template_conteudo'],
                'area_id': t['area_id'],
                'area': {
                    'id': t['area_id'],
                    'nome': t['area_juridica'],
                    'icone': t['area_icone'] or 'bi bi-file-text',
                    'cor': t['area_cor'] or '#007bff'
                }
            })
        
        return formatted_templates
    finally:
        cursor.close()
        conn.close()

def get_areas_from_db():
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

def search_templates_in_db(area_id=None, busca=None):
    """Busca templates com filtros no banco"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        where_conditions = ["t.ativo = true"]
        params = []
        
        if area_id:
            where_conditions.append("c.id = %s")
            params.append(area_id)
        
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
                t.nivel_complexidade as complexidade,
                t.tempo_estimado,
                t.template_conteudo,
                c.nome as area_nome,
                c.icone as area_icone,
                c.cor as area_cor,
                c.id as area_id
            FROM template_juridico t
            LEFT JOIN categoria_juridica c ON t.categoria_id = c.id
            WHERE {where_clause}
            ORDER BY t.area_juridica, t.nome
        """
        
        cursor.execute(query, params)
        templates = cursor.fetchall()
        
        # Converter para estrutura esperada
        formatted_templates = []
        for t in templates:
            formatted_templates.append({
                'id': t['id'],
                'nome': t['nome'],
                'descricao': t['descricao'],
                'tipo_documento': t['tipo_documento'],
                'complexidade': t['complexidade'],
                'tempo_estimado': t['tempo_estimado'],
                'template_conteudo': t['template_conteudo'],
                'area_id': t['area_id'],
                'area': {
                    'id': t['area_id'],
                    'nome': t['area_juridica'],
                    'icone': t['area_icone'] or 'bi bi-file-text',
                    'cor': t['area_cor'] or '#007bff'
                }
            })
        
        return formatted_templates
    finally:
        cursor.close()
        conn.close()

# Rotas principais
@legal_design_pro_v2_bp.route('/')
def dashboard():
    """Dashboard com estatísticas reais"""
    areas = get_areas_from_db()
    total_templates = sum(area['total_templates'] for area in areas)
    
    estatisticas = {
        'total_templates': total_templates,
        'total_areas': len(areas),
        'templates_mais_usados': []  # Pode ser implementado se necessário
    }
    
    return render_template('legal_design_pro_v2/dashboard.html', 
                         areas=areas, 
                         estatisticas=estatisticas)

@legal_design_pro_v2_bp.route('/templates')
def templates():
    """Página de templates com dados reais do banco"""
    area_id = request.args.get('area', type=int)
    busca = request.args.get('q', '')
    
    # Buscar templates
    if area_id or busca:
        templates = search_templates_in_db(area_id, busca)
    else:
        templates = get_all_templates_from_db()
    
    # Buscar todas as áreas para o menu
    areas = get_areas_from_db()
    
    return render_template('legal_design_pro_v2/templates.html',
                         templates=templates,
                         areas=areas,
                         area_selecionada=area_id,
                         busca=busca)

@legal_design_pro_v2_bp.route('/editor')
def editor():
    """Editor de documentos"""
    template_id = request.args.get('template', type=int)
    return render_template('legal_design_pro_v2/editor.html', template_id=template_id)

@legal_design_pro_v2_bp.route('/api/template/<int:template_id>')
def api_template(template_id):
    """API para obter template específico"""
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
        
        template = cursor.fetchone()
        
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
    finally:
        cursor.close()
        conn.close()

def register_legal_design_pro_v2(app):
    """Registra o blueprint na aplicação"""
    app.register_blueprint(legal_design_pro_v2_bp)
    print("✅ Legal Design Pro V2 com dados reais registrado com sucesso")
'''
    
    # Escrever o arquivo atualizado
    with open('complete_legal_design_pro_v2.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Arquivo complete_legal_design_pro_v2.py atualizado com dados reais")

def test_database_connection():
    """Testa a conexão e mostra estatísticas"""
    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Contar templates por área
        cursor.execute("""
            SELECT 
                t.area_juridica,
                COUNT(*) as total
            FROM template_juridico t
            WHERE t.ativo = true
            GROUP BY t.area_juridica
            ORDER BY t.area_juridica
        """)
        
        areas_stats = cursor.fetchall()
        
        print("\\n📊 ESTATÍSTICAS ATUAIS DO BANCO:")
        print("-" * 50)
        total_templates = 0
        for area in areas_stats:
            print(f"{area['area_juridica']}: {area['total']} templates")
            total_templates += area['total']
        
        print(f"\\nTotal: {total_templates} templates ativos")
        print(f"Áreas cobertas: {len(areas_stats)}")
        
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar com banco: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Atualizando sistema Legal Design Pro V2...")
    
    # Testar conexão
    if test_database_connection():
        # Atualizar arquivo
        update_complete_legal_design_pro_v2()
        print("\\n🎉 Sistema atualizado com sucesso!")
        print("📝 A página de templates agora carrega dados reais do banco PostgreSQL")
    else:
        print("❌ Falha na conexão com banco de dados")