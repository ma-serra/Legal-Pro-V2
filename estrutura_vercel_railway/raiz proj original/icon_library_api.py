"""
API para biblioteca de ícones legais
Gerencia os ícones extraídos dos 5 packs e fornece endpoints para o editor
"""

import os
import json
from flask import Blueprint, jsonify, request, url_for
from pathlib import Path

icon_library_bp = Blueprint('icon_library', __name__)

# Mapeamento de categorias para cada pack
ICON_CATEGORIES = {
    'pack1': 'Direito Criminal',
    'pack2': 'Direito Empresarial', 
    'pack3': 'Direito Bancário',
    'pack4': 'Direito Trabalhista',
    'pack5': 'Direito do Consumidor'
}

def get_icon_info(pack_name, icon_filename):
    """Obtém informações detalhadas sobre um ícone"""
    icon_number = icon_filename.replace('icon_', '').replace('.png', '')
    
    return {
        'id': f"{pack_name}_{icon_number}",
        'name': f"Ícone {icon_number} - {ICON_CATEGORIES.get(pack_name, 'Legal')}",
        'filename': icon_filename,
        'pack': pack_name,
        'category': ICON_CATEGORIES.get(pack_name, 'Legal'),
        'url': url_for('static', filename=f'icons/legal/{pack_name}/{icon_filename}'),
        'tags': [ICON_CATEGORIES.get(pack_name, 'Legal').lower(), 'juridico', 'icon']
    }

@icon_library_bp.route('/api/icons/library')
def get_icon_library():
    """Retorna toda a biblioteca de ícones organizados por pack"""
    try:
        icons_dir = Path('static/icons/legal')
        library = {
            'total_icons': 0,
            'packs': {},
            'categories': list(ICON_CATEGORIES.values())
        }
        
        for pack_name in ['pack1', 'pack2', 'pack3', 'pack4', 'pack5']:
            pack_dir = icons_dir / pack_name
            if pack_dir.exists():
                icons = []
                for icon_file in sorted(pack_dir.glob('*.png')):
                    icon_info = get_icon_info(pack_name, icon_file.name)
                    icons.append(icon_info)
                
                library['packs'][pack_name] = {
                    'name': ICON_CATEGORIES.get(pack_name, 'Legal'),
                    'total': len(icons),
                    'icons': icons
                }
                library['total_icons'] += len(icons)
        
        return jsonify(library)
    
    except Exception as e:
        return jsonify({'error': f'Erro ao carregar biblioteca: {str(e)}'}), 500

@icon_library_bp.route('/api/icons/search')
def search_icons():
    """Busca ícones por categoria ou termo"""
    try:
        query = request.args.get('q', '').lower()
        category = request.args.get('category', '')
        
        icons_dir = Path('static/icons/legal')
        results = []
        
        for pack_name in ['pack1', 'pack2', 'pack3', 'pack4', 'pack5']:
            pack_dir = icons_dir / pack_name
            if pack_dir.exists():
                # Filtrar por categoria se especificada
                if category and ICON_CATEGORIES.get(pack_name, '').lower() != category.lower():
                    continue
                
                for icon_file in sorted(pack_dir.glob('*.png')):
                    icon_info = get_icon_info(pack_name, icon_file.name)
                    
                    # Filtrar por query se especificada
                    if query:
                        searchable_text = f"{icon_info['name']} {icon_info['category']} {' '.join(icon_info['tags'])}".lower()
                        if query not in searchable_text:
                            continue
                    
                    results.append(icon_info)
        
        return jsonify({
            'query': query,
            'category': category,
            'total': len(results),
            'icons': results
        })
    
    except Exception as e:
        return jsonify({'error': f'Erro na busca: {str(e)}'}), 500

@icon_library_bp.route('/api/icons/pack/<pack_name>')
def get_pack_icons(pack_name):
    """Retorna todos os ícones de um pack específico"""
    try:
        if pack_name not in ['pack1', 'pack2', 'pack3', 'pack4', 'pack5']:
            return jsonify({'error': 'Pack não encontrado'}), 404
        
        icons_dir = Path('static/icons/legal') / pack_name
        if not icons_dir.exists():
            return jsonify({'error': 'Diretório do pack não encontrado'}), 404
        
        icons = []
        for icon_file in sorted(icons_dir.glob('*.png')):
            icon_info = get_icon_info(pack_name, icon_file.name)
            icons.append(icon_info)
        
        return jsonify({
            'pack': pack_name,
            'name': ICON_CATEGORIES.get(pack_name, 'Legal'),
            'total': len(icons),
            'icons': icons
        })
    
    except Exception as e:
        return jsonify({'error': f'Erro ao carregar pack: {str(e)}'}), 500

@icon_library_bp.route('/api/icons/stats')
def get_icon_stats():
    """Retorna estatísticas da biblioteca de ícones"""
    try:
        icons_dir = Path('static/icons/legal')
        stats = {
            'total_icons': 0,
            'total_packs': 0,
            'packs_breakdown': {},
            'categories': {}
        }
        
        for pack_name in ['pack1', 'pack2', 'pack3', 'pack4', 'pack5']:
            pack_dir = icons_dir / pack_name
            if pack_dir.exists():
                icon_count = len(list(pack_dir.glob('*.png')))
                category = ICON_CATEGORIES.get(pack_name, 'Legal')
                
                stats['total_icons'] += icon_count
                stats['total_packs'] += 1
                stats['packs_breakdown'][pack_name] = {
                    'name': category,
                    'count': icon_count
                }
                stats['categories'][category] = stats['categories'].get(category, 0) + icon_count
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({'error': f'Erro ao calcular estatísticas: {str(e)}'}), 500

def register_icon_library_api(app):
    """Registra a API de biblioteca de ícones na aplicação"""
    app.register_blueprint(icon_library_bp)
    print("✅ API de biblioteca de ícones registrada")