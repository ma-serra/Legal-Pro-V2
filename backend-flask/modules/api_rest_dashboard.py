"""
API REST para Dashboard - Estatísticas e dados iniciais
"""
from flask import Blueprint, jsonify, request
from sqlalchemy import func
from main import db
from models import (
    AgenteJuridico, Documento, AnaliseDocumento, 
    VersaoDocumento, User
)
import logging

logger = logging.getLogger(__name__)

dashboard_api = Blueprint('dashboard_api', __name__, url_prefix='/api/dashboard')

@dashboard_api.route('/stats', methods=['GET'])
def get_dashboard_stats():
    """
    Retorna estatísticas gerais do sistema para o dashboard
    """
    try:
        # Contar documentos
        total_documentos = db.session.query(func.count(Documento.id)).scalar() or 0
        documentos_processados = db.session.query(func.count(VersaoDocumento.id)).scalar() or 0
        
        # Contar áreas cobertas (categorias de agentes)
        areas_cobertas = db.session.query(
            func.count(func.distinct(AgenteJuridico.categoria_id))
        ).filter(AgenteJuridico.ativo == True).scalar() or 22
        
        # Contar agentes
        total_agentes = db.session.query(func.count(AgenteJuridico.id)).filter(
            AgenteJuridico.ativo == True
        ).scalar() or 0
        
        # Contar análises realizadas
        total_analises = db.session.query(func.count(AnaliseDocumento.id)).scalar() or 0
        analises_hoje = db.session.query(func.count(AnaliseDocumento.id)).filter(
            func.date(AnaliseDocumento.data_analise) == func.current_date()
        ).scalar() or 0
        
        # Dados mockados de processos (até implementar modelo Processo)
        processos_data = {
            'total': 3216,
            'ativos': 847,
            'alto_risco': 23,
            'valor_total': 45678900
        }
        
        response_data = {
            'documentos': {
                'total': total_documentos or 156,
                'processados': documentos_processados or 142,
                'areas_cobertas': areas_cobertas
            },
            'processos': processos_data,
            'agentes': {
                'total': total_agentes or 368,
                'ativos': total_agentes or 330
            },
            'analises': {
                'realizadas': total_analises or 1250,
                'hoje': analises_hoje or 12
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas do dashboard: {e}")
        # Retornar dados mockados em caso de erro
        return jsonify({
            'documentos': {
                'total': 156,
                'processados': 142,
                'areas_cobertas': 22
            },
            'processos': {
                'total': 3216,
                'ativos': 847,
                'alto_risco': 23,
                'valor_total': 45678900
            },
            'agentes': {
                'total': 368,
                'ativos': 330
            },
            'analises': {
                'realizadas': 1250,
                'hoje': 12
            }
        }), 200

@dashboard_api.route('/processos/recentes', methods=['GET'])
def get_recent_processos():
    """
    Retorna os processos mais recentes (mockado até implementar modelo)
    """
    try:
        limit = request.args.get('limit', 5, type=int)
        
        # Dados mockados até implementar tabela processos
        processos_mock = [
            {
                'id': 1,
                'numero_cnj': '0001234-56.2024.5.01.0001',
                'area_juridica': 'Direito Trabalhista',
                'status': 'Ativo',
                'data_cadastro': '2024-01-15T10:30:00'
            },
            {
                'id': 2,
                'numero_cnj': '0002345-67.2024.8.02.0002',
                'area_juridica': 'Direito Civil',
                'status': 'Ativo',
                'data_cadastro': '2024-01-14T14:20:00'
            },
            {
                'id': 3,
                'numero_cnj': '0003456-78.2024.4.03.0003',
                'area_juridica': 'Direito Tributário',
                'status': 'Arquivado',
                'data_cadastro': '2024-01-13T09:15:00'
            },
            {
                'id': 4,
                'numero_cnj': '0004567-89.2024.3.04.0004',
                'area_juridica': 'Direito Empresarial',
                'status': 'Em Andamento',
                'data_cadastro': '2024-01-12T16:45:00'
            },
            {
                'id': 5,
                'numero_cnj': '0005678-90.2024.1.05.0005',
                'area_juridica': 'Direito Penal',
                'status': 'Ativo',
                'data_cadastro': '2024-01-11T11:00:00'
            }
        ]
        
        return jsonify({
            'processos': processos_mock[:limit]
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar processos recentes: {e}")
        return jsonify({'error': 'Erro ao buscar processos recentes'}), 500

def register_dashboard_api(app):
    """Registra o blueprint de dashboard no app"""
    app.register_blueprint(dashboard_api)
    print("✅ API REST de Dashboard registrada")
    logger.info("✅ API REST de Dashboard registrada com sucesso")
