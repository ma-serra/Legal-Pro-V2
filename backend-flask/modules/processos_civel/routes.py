"""
Rotas API para Módulo Cível
Fase 3 - Acordos e Prognóstico
"""
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from functools import wraps
from datetime import date
from decimal import Decimal

from .services import CivelService, PrognosticoCivelService

# Criar Blueprint
civel_bp = Blueprint('civel', __name__, url_prefix='/api/civel')


def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            return jsonify({'error': 'Dados inválidos', 'details': e.messages}), 400
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Erro interno', 'details': str(e)}), 500
    return decorated_function


# ============================================================================
# DADOS CÍVEIS
# ============================================================================

@civel_bp.route('/processos/<int:processo_id>', methods=['POST', 'PUT'])
@handle_errors
def criar_atualizar_dados(processo_id):
    """
    Cria ou atualiza dados cíveis de um processo
    
    POST/PUT /api/civel/processos/1
    Body: {tolerancia_acordo, acordo_realizado, data_acordo, observacoes_acordo}
    """
    data = request.json
    
    proc_civel = CivelService.criar_ou_atualizar_dados(processo_id, data)
    
    return jsonify({
        'processo_id': proc_civel.processo_id,
        'tolerancia_acordo': float(proc_civel.tolerancia_acordo) if proc_civel.tolerancia_acordo else None,
        'acordo_realizado': float(proc_civel.acordo_realizado) if proc_civel.acordo_realizado else None
    }), 200


@civel_bp.route('/processos/<int:processo_id>', methods=['GET'])
@handle_errors
def obter_dados(processo_id):
    """
    Obtém dados cíveis de um processo
    
    GET /api/civel/processos/1
    """
    dados = CivelService.obter_dados(processo_id)
    
    if not dados:
        return jsonify({'error': 'Dados não encontrados'}), 404
    
    return jsonify(dados), 200


# ============================================================================
# ACORDO
# ============================================================================

@civel_bp.route('/processos/<int:processo_id>/acordo', methods=['POST'])
@handle_errors
def registrar_acordo(processo_id):
    """
    Registra acordo realizado
    
    POST /api/civel/processos/1/acordo
    Body: {valor_acordo, data_acordo, observacoes}
    """
    data = request.json
    
    proc_civel = CivelService.registrar_acordo(
        processo_id=processo_id,
        valor_acordo=Decimal(str(data['valor_acordo'])),
        data_acordo=date.fromisoformat(data['data_acordo']),
        observacoes=data.get('observacoes')
    )
    
    return jsonify({
        'processo_id': proc_civel.processo_id,
        'acordo_realizado': float(proc_civel.acordo_realizado),
        'data_acordo': proc_civel.data_acordo.isoformat()
    }), 201


@civel_bp.route('/processos/<int:processo_id>/acordo/viabilidade', methods=['POST'])
@handle_errors
def verificar_viabilidade_acordo(processo_id):
    """
    Verifica viabilidade de proposta de acordo
    
    POST /api/civel/processos/1/acordo/viabilidade
    Body: {valor_proposta}
    """
    data = request.json
    
    resultado = CivelService.verificar_viabilidade_acordo(
        processo_id=processo_id,
        valor_proposta=Decimal(str(data['valor_proposta']))
    )
    
    return jsonify(resultado), 200


# ============================================================================
# PROGNÓSTICO
# ============================================================================

@civel_bp.route('/processos/<int:processo_id>/prognostico', methods=['POST'])
@handle_errors
def criar_prognostico(processo_id):
    """
    Cria ou atualiza prognóstico
    
    POST /api/civel/processos/1/prognostico
    Body: {tese_provavel, valor_provavel, tese_possivel, ...}
    """
    data = request.json
    
    prognostico = PrognosticoCivelService.criar_ou_atualizar_prognostico(
        processo_id, data
    )
    
    return jsonify({
        'id_prognostico': prognostico.id_prognostico,
        'processo_id': prognostico.processo_id,
        'data_avaliacao': prognostico.data_avaliacao.isoformat() if prognostico.data_avaliacao else None
    }), 201


@civel_bp.route('/processos/<int:processo_id>/prognostico', methods=['GET'])
@handle_errors
def obter_prognostico(processo_id):
    """
    Obtém prognóstico de um processo
    
    GET /api/civel/processos/1/prognostico
    """
    prognostico = PrognosticoCivelService.obter_prognostico(processo_id)
    
    if not prognostico:
        return jsonify({'error': 'Prognóstico não encontrado'}), 404
    
    return jsonify(prognostico), 200


@civel_bp.route('/processos/<int:processo_id>/valor-esperado', methods=['GET'])
@handle_errors
def calcular_valor_esperado(processo_id):
    """
    Calcula valor esperado do processo
    
    GET /api/civel/processos/1/valor-esperado
    """
    valor = PrognosticoCivelService.calcular_valor_esperado(processo_id)
    
    if valor is None:
        return jsonify({'error': 'Prognóstico não encontrado'}), 404
    
    return jsonify({
        'processo_id': processo_id,
        'valor_esperado': float(valor)
    }), 200


# ============================================================================
# REGISTRO DO BLUEPRINT
# ============================================================================

def registrar_rotas(app):
    """Registra o blueprint no app Flask"""
    app.register_blueprint(civel_bp)
