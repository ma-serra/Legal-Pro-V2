"""
Rotas API para Módulo Trabalhista
Fase 3 - Acordos e Prognóstico
"""
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from functools import wraps
from datetime import date
from decimal import Decimal

from .services import TrabalhistaService, PrognosticoTrabalhistaService

# Criar Blueprint
trabalhista_bp = Blueprint('trabalhista', __name__, url_prefix='/api/trabalhista')


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
# DADOS TRABALHISTAS
# ============================================================================

@trabalhista_bp.route('/processos/<int:processo_id>', methods=['POST', 'PUT'])
@handle_errors
def criar_atualizar_dados(processo_id):
    """
    Cria ou atualiza dados trabalhistas de um processo
    
    POST/PUT /api/trabalhista/processos/1
    Body: {tolerancia_acordo, acordo_realizado, data_acordo, observacoes_acordo}
    """
    data = request.json
    
    proc_trab = TrabalhistaService.criar_ou_atualizar_dados(processo_id, data)
    
    return jsonify({
        'processo_id': proc_trab.processo_id,
        'tolerancia_acordo': float(proc_trab.tolerancia_acordo) if proc_trab.tolerancia_acordo else None,
        'acordo_realizado': float(proc_trab.acordo_realizado) if proc_trab.acordo_realizado else None
    }), 200


@trabalhista_bp.route('/processos/<int:processo_id>', methods=['GET'])
@handle_errors
def obter_dados(processo_id):
    """
    Obtém dados trabalhistas de um processo
    
    GET /api/trabalhista/processos/1
    """
    dados = TrabalhistaService.obter_dados(processo_id)
    
    if not dados:
        return jsonify({'error': 'Dados não encontrados'}), 404
    
    return jsonify(dados), 200


# ============================================================================
# ACORDO
# ============================================================================

@trabalhista_bp.route('/processos/<int:processo_id>/acordo', methods=['POST'])
@handle_errors
def registrar_acordo(processo_id):
    """
    Registra acordo realizado
    
    POST /api/trabalhista/processos/1/acordo
    Body: {valor_acordo, data_acordo, observacoes}
    """
    data = request.json
    
    proc_trab = TrabalhistaService.registrar_acordo(
        processo_id=processo_id,
        valor_acordo=Decimal(str(data['valor_acordo'])),
        data_acordo=date.fromisoformat(data['data_acordo']),
        observacoes=data.get('observacoes')
    )
    
    return jsonify({
        'processo_id': proc_trab.processo_id,
        'acordo_realizado': float(proc_trab.acordo_realizado),
        'data_acordo': proc_trab.data_acordo.isoformat()
    }), 201


@trabalhista_bp.route('/processos/<int:processo_id>/acordo/viabilidade', methods=['POST'])
@handle_errors
def verificar_viabilidade_acordo(processo_id):
    """
    Verifica viabilidade de proposta de acordo
    
    POST /api/trabalhista/processos/1/acordo/viabilidade
    Body: {valor_proposta}
    """
    data = request.json
    
    resultado = TrabalhistaService.verificar_viabilidade_acordo(
        processo_id=processo_id,
        valor_proposta=Decimal(str(data['valor_proposta']))
    )
    
    return jsonify(resultado), 200


# ============================================================================
# PROGNÓSTICO
# ============================================================================

@trabalhista_bp.route('/processos/<int:processo_id>/prognostico', methods=['POST'])
@handle_errors
def criar_prognostico(processo_id):
    """
    Cria ou atualiza prognóstico
    
    POST /api/trabalhista/processos/1/prognostico
    Body: {tese_provavel, valor_provavel, tese_possivel, ...}
    """
    data = request.json
    
    prognostico = PrognosticoTrabalhistaService.criar_ou_atualizar_prognostico(
        processo_id, data
    )
    
    return jsonify({
        'id_prognostico': prognostico.id_prognostico,
        'processo_id': prognostico.processo_id,
        'data_avaliacao': prognostico.data_avaliacao.isoformat() if prognostico.data_avaliacao else None
    }), 201


@trabalhista_bp.route('/processos/<int:processo_id>/prognostico', methods=['GET'])
@handle_errors
def obter_prognostico(processo_id):
    """
    Obtém prognóstico de um processo
    
    GET /api/trabalhista/processos/1/prognostico
    """
    prognostico = PrognosticoTrabalhistaService.obter_prognostico(processo_id)
    
    if not prognostico:
        return jsonify({'error': 'Prognóstico não encontrado'}), 404
    
    return jsonify(prognostico), 200


@trabalhista_bp.route('/processos/<int:processo_id>/valor-esperado', methods=['GET'])
@handle_errors
def calcular_valor_esperado(processo_id):
    """
    Calcula valor esperado do processo
    
    GET /api/trabalhista/processos/1/valor-esperado
    """
    valor = PrognosticoTrabalhistaService.calcular_valor_esperado(processo_id)
    
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
    app.register_blueprint(trabalhista_bp)
