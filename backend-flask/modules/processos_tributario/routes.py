"""
Rotas API para Módulo Tributário
Fase 3 - Teses, Prognóstico e Atualização Monetária
"""
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from functools import wraps
from datetime import date
from decimal import Decimal

from .services import (
    TeseTributariaService,
    PrognosticoTributarioService,
    AtualizacaoMonetariaService
)

# Criar Blueprint
tributario_bp = Blueprint('processos_tributario', __name__, url_prefix='/api/tributario')


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
# TESES TRIBUTÁRIAS
# ============================================================================

@tributario_bp.route('/teses', methods=['POST'])
@handle_errors
def criar_tese():
    """
    Cria nova tese tributária
    
    POST /api/tributario/teses
    Body: {codigo, titulo, tributo_id, probabilidade_sucesso, ...}
    """
    data = request.json
    
    tese = TeseTributariaService.criar_tese(data)
    
    return jsonify(tese.to_dict()), 201


@tributario_bp.route('/teses', methods=['GET'])
@handle_errors
def listar_teses():
    """
    Lista teses tributárias
    
    GET /api/tributario/teses?tributo_id=1&situacao=Favorável
    """
    filtros = {
        'tributo_id': request.args.get('tributo_id', type=int),
        'situacao': request.args.get('situacao'),
        'busca': request.args.get('q')
    }
    
    # Remover None
    filtros = {k: v for k, v in filtros.items() if v is not None}
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    resultado = TeseTributariaService.listar_teses(filtros, page, per_page)
    
    return jsonify(resultado), 200


@tributario_bp.route('/teses/<int:tese_id>', methods=['GET'])
@handle_errors
def obter_tese(tese_id):
    """
    Obtém uma tese por ID
    
    GET /api/tributario/teses/123
    """
    tese = TeseTributariaService.obter_tese(tese_id)
    
    if not tese:
        return jsonify({'error': 'Tese não encontrada'}), 404
    
    return jsonify(tese.to_dict()), 200


@tributario_bp.route('/teses/<int:tese_id>', methods=['PUT'])
@handle_errors
def atualizar_tese(tese_id):
    """
    Atualiza uma tese
    
    PUT /api/tributar io/teses/123
    """
    data = request.json
    
    tese = TeseTributariaService.atualizar_tese(tese_id, data)
    
    if not tese:
        return jsonify({'error': 'Tese não encontrada'}), 404
    
    return jsonify(tese.to_dict()), 200


@tributario_bp.route('/teses/<int:tese_id>', methods=['DELETE'])
@handle_errors
def deletar_tese(tese_id):
    """
    Deleta uma tese (soft delete)
    
    DELETE /api/tributario/teses/123
    """
    sucesso = TeseTributariaService.deletar_tese(tese_id)
    
    if not sucesso:
        return jsonify({'error': 'Tese não encontrada'}), 404
    
    return jsonify({'message': 'Tese deletada com sucesso'}), 200


# ============================================================================
# VINCULAÇÃO TESE-PROCESSO
# ============================================================================

@tributario_bp.route('/processos/<int:processo_id>/teses', methods=['POST'])
@handle_errors
def vincular_tese(processo_id):
    """
    Vincula uma tese a um processo
    
    POST /api/tributario/processos/1/teses
    Body: {tese_id, ordem}
    """
    data = request.json
    
    vinculo = TeseTributariaService.vincular_tese_processo(
        processo_id=processo_id,
        tese_id=data['tese_id'],
        ordem=data.get('ordem', 1)
    )
    
    return jsonify({
        'processo_id': vinculo.processo_id,
        'tese_id': vinculo.tese_id,
        'ordem': vinculo.ordem,
        'status': vinculo.status
    }), 201


@tributario_bp.route('/processos/<int:processo_id>/teses/<int:tese_id>', methods=['DELETE'])
@handle_errors
def desvincular_tese(processo_id, tese_id):
    """
    Desvincula tese de processo
    
    DELETE /api/tributario/processos/1/teses/2
    """
    sucesso = TeseTributariaService.desvincular_tese_processo(processo_id, tese_id)
    
    if not sucesso:
        return jsonify({'error': 'Vínculo não encontrado'}), 404
    
    return jsonify({'message': 'Tese desvinculada com sucesso'}), 200


@tributario_bp.route('/processos/<int:processo_id>/teses/<int:tese_id>/status', methods=['PUT'])
@handle_errors
def atualizar_status_tese(processo_id, tese_id):
    """
    Atualiza status de tese no processo
    
    PUT /api/tributario/processos/1/teses/2/status
    Body: {status: 'Aceita'}
    """
    data = request.json
    
    vinculo = TeseTributariaService.atualizar_status_tese_processo(
        processo_id, tese_id, data['status']
    )
    
    if not vinculo:
        return jsonify({'error': 'Vínculo não encontrado'}), 404
    
    return jsonify({
        'processo_id': vinculo.processo_id,
        'tese_id': vinculo.tese_id,
        'status': vinculo.status
    }), 200


@tributario_bp.route('/processos/<int:processo_id>/teses', methods=['GET'])
@handle_errors
def listar_teses_processo(processo_id):
    """
    Lista teses vinculadas a um processo
    
    GET /api/tributario/processos/1/teses
    """
    teses = TeseTributariaService.listar_teses_processo(processo_id)
    
    return jsonify(teses), 200


# ============================================================================
# PROGNÓSTICO TRIBUTÁRIO
# ============================================================================

@tributario_bp.route('/processos/<int:processo_id>/prognostico', methods=['POST'])
@handle_errors
def criar_prognostico(processo_id):
    """
    Cria ou atualiza prognóstico
    
    POST /api/tributario/processos/1/prognostico
    Body: {tese_provavel_id, valor_provavel, tese_possivel_id, ...}
    """
    data = request.json
    
    prognostico = PrognosticoTributarioService.criar_ou_atualizar_prognostico(
        processo_id, data
    )
    
    return jsonify({
        'id_prognostico': prognostico.id_prognostico,
        'processo_id': prognostico.processo_id,
        'data_avaliacao': prognostico.data_avaliacao.isoformat() if prognostico.data_avaliacao else None
    }), 201


@tributario_bp.route('/processos/<int:processo_id>/prognostico', methods=['GET'])
@handle_errors
def obter_prognostico(processo_id):
    """
    Obtém prognóstico de um processo
    
    GET /api/tributario/processos/1/prognostico
    """
    prognostico = PrognosticoTributarioService.obter_prognostico(processo_id)
    
    if not prognostico:
        return jsonify({'error': 'Prognóstico não encontrado'}), 404
    
    return jsonify(prognostico), 200


@tributario_bp.route('/processos/<int:processo_id>/valor-esperado', methods=['GET'])
@handle_errors
def calcular_valor_esperado(processo_id):
    """
    Calcula valor esperado do processo
    
    GET /api/tributario/processos/1/valor-esperado
    """
    valor = PrognosticoTributarioService.calcular_valor_esperado(processo_id)
    
    if valor is None:
        return jsonify({'error': 'Prognóstico não encontrado'}), 404
    
    return jsonify({
        'processo_id': processo_id,
        'valor_esperado': float(valor)
    }), 200


# ============================================================================
# ATUALIZAÇÃO MONETÁRIA
# ============================================================================

@tributario_bp.route('/atualizacao-monetaria/calcular', methods=['POST'])
@handle_errors
def calcular_atualizacao():
    """
    Calcula atualização monetária
    
    POST /api/tributario/atualizacao-monetaria/calcular
    Body: {valor_base, data_base, data_atualizacao, indice_id}
    """
    data = request.json
    
    resultado = AtualizacaoMonetariaService.calcular_atualizacao(
        valor_base=Decimal(str(data['valor_base'])),
        data_base=date.fromisoformat(data['data_base']),
        data_atualizacao=date.fromisoformat(data['data_atualizacao']),
        indice_id=data['indice_id']
    )
    
    return jsonify(resultado), 200


@tributario_bp.route('/processos/<int:processo_id>/atualizacao-monetaria', methods=['POST'])
@handle_errors
def registrar_atualizacao(processo_id):
    """
    Registra atualização monetária para processo
    
    POST /api/tributario/processos/1/atualizacao-monetaria
    Body: {indice_id, data_base, valor_base}
    """
    data = request.json
    
    atualizacao = AtualizacaoMonetariaService.registrar_atualizacao(
        processo_id=processo_id,
        indice_id=data['indice_id'],
        data_base=date.fromisoformat(data['data_base']),
        valor_base=Decimal(str(data['valor_base']))
    )
    
    return jsonify({
        'id_atualizacao': atualizacao.id_atualizacao,
        'processo_id': atualizacao.processo_id,
        'valor_atualizado': float(atualizacao.valor_atualizado) if atualizacao.valor_atualizado else None,
        'percentual_correcao': float(atualizacao.percentual_correcao) if atualizacao.percentual_correcao else None
    }), 201


@tributario_bp.route('/processos/<int:processo_id>/atualizacao-monetaria', methods=['GET'])
@handle_errors
def listar_atualizacoes(processo_id):
    """
    Lista atualizações de um processo
    
    GET /api/tributario/processos/1/atualizacao-monetaria
    """
    atualizacoes = AtualizacaoMonetariaService.listar_atualizacoes_processo(processo_id)
    
    return jsonify(atualizacoes), 200


# ============================================================================
# REGISTRO DO BLUEPRINT
# ============================================================================

def registrar_rotas(app):
    """Registra o blueprint no app Flask"""
    app.register_blueprint(tributario_bp)
