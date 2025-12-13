"""
API para gerenciamento de elementos gráficos do Legal Design Pro
Integra com o banco de dados e fornece endpoints para o editor
"""

from flask import Blueprint, jsonify, request, render_template_string
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import json

# Configuração do Blueprint
elementos_bp = Blueprint('elementos_graficos', __name__, url_prefix='/api/elementos')

# Configuração do banco
DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

@elementos_bp.route('/listar')
def listar_elementos():
    """Lista todos os elementos gráficos disponíveis"""
    session = Session()
    try:
        result = session.execute(text("""
            SELECT id, nome, categoria, tipo, descricao, cor_primaria, cor_secundaria,
                   tags, area_juridica, popularidade
            FROM elementos_graficos 
            WHERE ativo = true 
            ORDER BY categoria, popularidade DESC, nome
        """))
        
        elementos = []
        for row in result:
            elemento = {
                'id': row[0],
                'nome': row[1],
                'categoria': row[2],
                'tipo': row[3],
                'descricao': row[4],
                'cor_primaria': row[5],
                'cor_secundaria': row[6],
                'tags': json.loads(row[7]) if row[7] else [],
                'area_juridica': row[8],
                'popularidade': row[9]
            }
            elementos.append(elemento)
        
        # Agrupar por categoria
        categorias = {}
        for elemento in elementos:
            cat = elemento['categoria']
            if cat not in categorias:
                categorias[cat] = []
            categorias[cat].append(elemento)
        
        return jsonify({
            'success': True,
            'elementos': elementos,
            'por_categoria': categorias,
            'total': len(elementos)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()

@elementos_bp.route('/obter/<int:elemento_id>')
def obter_elemento(elemento_id):
    """Obtém um elemento específico com todo o código necessário"""
    session = Session()
    try:
        result = session.execute(text("""
            SELECT nome, categoria, tipo, descricao, codigo_svg, codigo_html, codigo_css,
                   cor_primaria, cor_secundaria, largura, altura, tags, area_juridica
            FROM elementos_graficos 
            WHERE id = :id AND ativo = true
        """), {'id': elemento_id})
        
        row = result.fetchone()
        if not row:
            return jsonify({'success': False, 'error': 'Elemento não encontrado'}), 404
        
        elemento = {
            'nome': row[0],
            'categoria': row[1],
            'tipo': row[2],
            'descricao': row[3],
            'codigo_svg': row[4],
            'codigo_html': row[5],
            'codigo_css': row[6],
            'cor_primaria': row[7],
            'cor_secundaria': row[8],
            'largura': row[9],
            'altura': row[10],
            'tags': json.loads(row[11]) if row[11] else [],
            'area_juridica': row[12]
        }
        
        # Incrementar popularidade
        session.execute(text("""
            UPDATE elementos_graficos 
            SET popularidade = popularidade + 1 
            WHERE id = :id
        """), {'id': elemento_id})
        session.commit()
        
        return jsonify({
            'success': True,
            'elemento': elemento
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()

@elementos_bp.route('/buscar')
def buscar_elementos():
    """Busca elementos por categoria, tags ou área jurídica"""
    categoria = request.args.get('categoria')
    area = request.args.get('area')
    busca = request.args.get('q', '').strip()
    
    session = Session()
    try:
        query = """
            SELECT id, nome, categoria, tipo, descricao, cor_primaria, 
                   tags, area_juridica, popularidade
            FROM elementos_graficos 
            WHERE ativo = true
        """
        params = {}
        
        if categoria:
            query += " AND categoria = :categoria"
            params['categoria'] = categoria
            
        if area:
            query += " AND area_juridica = :area"
            params['area'] = area
            
        if busca:
            query += " AND (nome ILIKE :busca OR descricao ILIKE :busca OR tags ILIKE :busca)"
            params['busca'] = f'%{busca}%'
        
        query += " ORDER BY popularidade DESC, nome"
        
        result = session.execute(text(query), params)
        
        elementos = []
        for row in result:
            elemento = {
                'id': row[0],
                'nome': row[1],
                'categoria': row[2],
                'tipo': row[3],
                'descricao': row[4],
                'cor_primaria': row[5],
                'tags': json.loads(row[6]) if row[6] else [],
                'area_juridica': row[7],
                'popularidade': row[8]
            }
            elementos.append(elemento)
        
        return jsonify({
            'success': True,
            'elementos': elementos,
            'total': len(elementos),
            'filtros': {
                'categoria': categoria,
                'area': area,
                'busca': busca
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()

@elementos_bp.route('/renderizar/<int:elemento_id>')
def renderizar_elemento(elemento_id):
    """Renderiza um elemento gráfico com HTML/CSS completo"""
    session = Session()
    try:
        result = session.execute(text("""
            SELECT nome, tipo, codigo_svg, codigo_html, codigo_css, cor_primaria, cor_secundaria
            FROM elementos_graficos 
            WHERE id = :id AND ativo = true
        """), {'id': elemento_id})
        
        row = result.fetchone()
        if not row:
            return jsonify({'success': False, 'error': 'Elemento não encontrado'}), 404
        
        nome, tipo, svg, html, css, cor1, cor2 = row
        
        # Preparar HTML renderizado
        if tipo == 'icon' and svg:
            html_final = f'''
            <div class="elemento-grafico icon-{elemento_id}" style="color: {cor1};">
                {svg}
            </div>
            '''
        elif tipo == 'template' and html:
            html_final = f'''
            <div class="elemento-grafico template-{elemento_id}">
                {html}
            </div>
            '''
        else:
            html_final = f'<div class="elemento-grafico">Elemento: {nome}</div>'
        
        css_final = css or ''
        
        return jsonify({
            'success': True,
            'html': html_final,
            'css': css_final,
            'nome': nome,
            'tipo': tipo
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()

@elementos_bp.route('/categorias')
def listar_categorias():
    """Lista todas as categorias disponíveis"""
    session = Session()
    try:
        result = session.execute(text("""
            SELECT categoria, COUNT(*) as total
            FROM elementos_graficos 
            WHERE ativo = true 
            GROUP BY categoria 
            ORDER BY categoria
        """))
        
        categorias = []
        for row in result:
            categorias.append({
                'nome': row[0],
                'total': row[1]
            })
        
        return jsonify({
            'success': True,
            'categorias': categorias
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()

@elementos_bp.route('/areas-juridicas')
@elementos_bp.route('/areas')
def listar_areas():
    """Lista todas as áreas jurídicas disponíveis"""
    session = Session()
    try:
        result = session.execute(text("""
            SELECT area_juridica, COUNT(*) as total
            FROM elementos_graficos 
            WHERE ativo = true 
            GROUP BY area_juridica 
            ORDER BY area_juridica
        """))
        
        areas = []
        for row in result:
            areas.append({
                'nome': row[0],
                'total': row[1]
            })
        
        return jsonify({
            'success': True,
            'areas': areas
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()

@elementos_bp.route('/estatisticas')
def estatisticas():
    """Fornece estatísticas dos elementos gráficos"""
    session = Session()
    try:
        # Total de elementos
        total_result = session.execute(text("SELECT COUNT(*) FROM elementos_graficos WHERE ativo = true"))
        total = total_result.scalar()
        
        # Por categoria
        cat_result = session.execute(text("""
            SELECT categoria, COUNT(*) 
            FROM elementos_graficos 
            WHERE ativo = true 
            GROUP BY categoria
        """))
        por_categoria = {row[0]: row[1] for row in cat_result}
        
        # Mais populares
        pop_result = session.execute(text("""
            SELECT nome, popularidade 
            FROM elementos_graficos 
            WHERE ativo = true 
            ORDER BY popularidade DESC 
            LIMIT 5
        """))
        mais_populares = [{'nome': row[0], 'uso': row[1]} for row in pop_result]
        
        return jsonify({
            'success': True,
            'estatisticas': {
                'total_elementos': total,
                'por_categoria': por_categoria,
                'mais_populares': mais_populares
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()

# Função para registrar o blueprint
def registrar_api_elementos(app):
    """Registra a API de elementos gráficos na aplicação"""
    app.register_blueprint(elementos_bp)
    print("✅ API de elementos gráficos registrada")