#!/usr/bin/env python3
"""
Rotas para a funcionalidade de personalização de Temas
do sistema jurídico multi-agente.
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, TemaPagina
import json
import logging

# Configurar blueprint
temas_bp = Blueprint('temas', __name__, url_prefix='/temas')

@temas_bp.route('/')
@login_required
def personalizar():
    """Página principal de personalização de temas."""
    try:
        # Buscar todos os temas configurados
        temas = TemaPagina.query.filter_by(ativo=True).order_by(TemaPagina.rota).all()
        
        return render_template('temas/personalizar.html', temas=temas)
        
    except Exception as e:
        logging.error(f"Erro ao carregar página de temas: {e}")
        flash('Erro ao carregar configurações de temas', 'error')
        return redirect(url_for('juridico_especialistas'))

@temas_bp.route('/api/temas/<int:tema_id>', methods=['PUT'])
@login_required
def salvar_tema(tema_id):
    """Salvar configurações de um tema específico."""
    try:
        # Buscar o tema
        tema = TemaPagina.query.get_or_404(tema_id)
        
        # Obter dados do request
        dados = request.get_json()
        cores = dados.get('cores', {})
        
        # Validar cores (formato hexadecimal)
        for nome_cor, valor_cor in cores.items():
            if not valor_cor.startswith('#') or len(valor_cor) != 7:
                return jsonify({'erro': f'Cor inválida: {nome_cor}'}), 400
        
        # Atualizar tema
        tema.set_cores(cores)
        tema.modificado_por = current_user.id
        
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Tema atualizado com sucesso',
            'tema': tema.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Erro ao salvar tema {tema_id}: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@temas_bp.route('/api/temas/<int:tema_id>/reset', methods=['POST'])
@login_required
def resetar_tema(tema_id):
    """Resetar um tema para as configurações padrão."""
    try:
        tema = TemaPagina.query.get_or_404(tema_id)
        
        # Cores padrão baseadas na rota
        cores_padrao = obter_cores_padrao(tema.rota)
        
        # Resetar tema
        tema.set_cores(cores_padrao)
        tema.modificado_por = current_user.id
        
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Tema resetado com sucesso',
            'tema': tema.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Erro ao resetar tema {tema_id}: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@temas_bp.route('/api/temas/aplicar-escuro', methods=['POST'])
@login_required
def aplicar_tema_escuro():
    """Aplicar tema escuro em todos os módulos."""
    try:
        # Cores do tema escuro
        cores_escuro = {
            "header_bg": "#000000",
            "primary_color": "#0d6efd",
            "secondary_color": "#6c757d",
            "success_color": "#1f5981",
            "warning_color": "#ffc107",
            "danger_color": "#dc3545",
            "info_color": "#0dcaf0",
            "text_color": "#ffffff",
            "bg_color": "#1a1a1a",
            "accent_color": "#495057"
        }
        
        # Aplicar em todos os temas
        temas = TemaPagina.query.filter_by(ativo=True).all()
        
        for tema in temas:
            tema.set_cores(cores_escuro)
            tema.modificado_por = current_user.id
        
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': f'Tema escuro aplicado em {len(temas)} módulos',
            'total_temas': len(temas)
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Erro ao aplicar tema escuro: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@temas_bp.route('/api/temas/aplicar-claro', methods=['POST'])
@login_required
def aplicar_tema_claro():
    """Aplicar tema claro em todos os módulos."""
    try:
        # Cores do tema claro
        cores_claro = {
            "header_bg": "#f8f9fa",
            "primary_color": "#0d6efd",
            "secondary_color": "#6c757d",
            "success_color": "#1f5981",
            "warning_color": "#ffc107",
            "danger_color": "#dc3545",
            "info_color": "#0dcaf0",
            "text_color": "#212529",
            "bg_color": "#ffffff",
            "accent_color": "#e9ecef"
        }
        
        # Aplicar em todos os temas
        temas = TemaPagina.query.filter_by(ativo=True).all()
        
        for tema in temas:
            tema.set_cores(cores_claro)
            tema.modificado_por = current_user.id
        
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': f'Tema claro aplicado em {len(temas)} módulos',
            'total_temas': len(temas)
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Erro ao aplicar tema claro: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@temas_bp.route('/api/temas/reset-todos', methods=['POST'])
@login_required
def resetar_todos_temas():
    """Resetar todos os temas para as configurações padrão."""
    try:
        temas = TemaPagina.query.filter_by(ativo=True).all()
        
        for tema in temas:
            cores_padrao = obter_cores_padrao(tema.rota)
            tema.set_cores(cores_padrao)
            tema.modificado_por = current_user.id
        
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': f'Todos os {len(temas)} temas foram resetados',
            'total_temas': len(temas)
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Erro ao resetar todos os temas: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@temas_bp.route('/api/temas', methods=['GET'])
@login_required
def listar_temas():
    """Listar todos os temas configurados."""
    try:
        temas = TemaPagina.query.filter_by(ativo=True).order_by(TemaPagina.rota).all()
        
        return jsonify({
            'temas': [tema.to_dict() for tema in temas],
            'total': len(temas)
        })
        
    except Exception as e:
        logging.error(f"Erro ao listar temas: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

def obter_cores_padrao(rota):
    """Obter cores padrão para uma rota específica."""
    cores_por_modulo = {
        '/juridico/especialistas': {
            "header_bg": "#1a1a1a",
            "primary_color": "#007bff",
            "secondary_color": "#6c757d",
            "success_color": "#1f5981",
            "warning_color": "#ffc107",
            "danger_color": "#dc3545",
            "info_color": "#17a2b8",
            "text_color": "#ffffff",
            "bg_color": "#2c2c2c"
        },
        '/juridico/criminal': {
            "primary_color": "#dc3545",
            "header_bg": "#1a1a1a",
            "accent_color": "#ff6b6b",
            "text_color": "#ffffff",
            "bg_color": "#2c2c2c"
        },
        '/juridico/empresarial': {
            "primary_color": "#007bff",
            "header_bg": "#1a1a1a",
            "accent_color": "#4dabf7",
            "text_color": "#ffffff",
            "bg_color": "#2c2c2c"
        },
        '/juridico/bancario': {
            "primary_color": "#1f5981",
            "header_bg": "#1a1a1a",
            "accent_color": "#51cf66",
            "text_color": "#ffffff",
            "bg_color": "#2c2c2c"
        },
        '/juridico/recuperacao': {
            "primary_color": "#ffc107",
            "header_bg": "#1a1a1a",
            "accent_color": "#ffd43b",
            "text_color": "#ffffff",
            "bg_color": "#2c2c2c"
        },
        '/juridico/trabalhista': {
            "primary_color": "#6f42c1",
            "header_bg": "#1a1a1a",
            "accent_color": "#9775fa",
            "text_color": "#ffffff",
            "bg_color": "#2c2c2c"
        },
        '/juridico/agrario': {
            "primary_color": "#20c997",
            "header_bg": "#1a1a1a",
            "accent_color": "#63e6be",
            "text_color": "#ffffff",
            "bg_color": "#2c2c2c"
        },
        '/juridico/consumidor': {
            "primary_color": "#fd7e14",
            "header_bg": "#1a1a1a",
            "accent_color": "#ffb366",
            "text_color": "#ffffff",
            "bg_color": "#2c2c2c"
        }
    }
    
    return cores_por_modulo.get(rota, {
        "header_bg": "#1a1a1a",
        "primary_color": "#007bff",
        "text_color": "#ffffff",
        "bg_color": "#2c2c2c"
    })

# Função para aplicar tema a uma página específica
def aplicar_tema_pagina(rota):
    """Aplicar tema de uma página específica no template."""
    try:
        tema = TemaPagina.query.filter_by(rota=rota, ativo=True).first()
        if tema:
            return tema.get_cores()
        return {}
    except Exception as e:
        logging.error(f"Erro ao aplicar tema da página {rota}: {e}")
        return {}

# Filtro Jinja2 para usar nos templates
def filtro_tema(rota):
    """Filtro Jinja2 para obter cores do tema."""
    return aplicar_tema_pagina(rota)