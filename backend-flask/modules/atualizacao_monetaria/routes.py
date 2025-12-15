"""
Rotas API para Atualização Monetária
Fase 4 - Gestão de Índices e Importação
"""
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from functools import wraps
from datetime import date, timedelta

from .importador import ImportadorIndices
from .scheduler import scheduler_global
from models import IndiceMonetario, HistoricoIndice

# Criar Blueprint
atualizacao_bp = Blueprint('atualizacao_monetaria', __name__, url_prefix='/api/atualizacao-monetaria')


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
# IMPORTAÇÃO DE ÍNDICES
# ============================================================================

@atualizacao_bp.route('/importar/<string:indice_nome>', methods=['POST'])
@handle_errors
def importar_indice(indice_nome):
    """
    Importa histórico de um índice específico
    
    POST /api/atualizacao-monetaria/importar/SELIC
    Body: {data_inicio, data_fim, sobrescrever} (opcional)
    """
    data = request.json or {}
    
    # Parse datas
    data_inicio = None
    data_fim = None
    
    if 'data_inicio' in data:
        data_inicio = date.fromisoformat(data['data_inicio'])
    if 'data_fim' in data:
        data_fim = date.fromisoformat(data['data_fim'])
    
    sobrescrever = data.get('sobrescrever', False)
    
    # Importar
    registros = ImportadorIndices.importar_historico(
        indice_nome=indice_nome.upper(),
        data_inicio=data_inicio,
        data_fim=data_fim,
        sobrescrever=sobrescrever
    )
    
    return jsonify({
        'indice': indice_nome,
        'registros_importados': registros,
        'data_inicio': data_inicio.isoformat() if data_inicio else None,
        'data_fim': data_fim.isoformat() if data_fim else None
    }), 201


@atualizacao_bp.route('/importar/todos', methods=['POST'])
@handle_errors
def importar_todos():
    """
    Importa histórico de todos os índices
    
    POST /api/atualizacao-monetaria/importar/todos
    Body: {data_inicio, data_fim} (opcional)
    """
    data = request.json or {}
    
    data_inicio = None
    data_fim = None
    
    if 'data_inicio' in data:
        data_inicio = date.fromisoformat(data['data_inicio'])
    if 'data_fim' in data:
        data_fim = date.fromisoformat(data['data_fim'])
    
    resultado = ImportadorIndices.importar_todos_indices(data_inicio, data_fim)
    
    return jsonify({
        'resultados': resultado,
        'total_registros': sum(resultado.values())
    }), 201


@atualizacao_bp.route('/atualizar/recentes', methods=['POST'])
@handle_errors
def atualizar_recentes():
    """
    Atualiza índices dos últimos 30 dias
    
    POST /api/atualizacao-monetaria/atualizar/recentes
    Body: {dias} (opcional, padrão: 30)
    """
    data = request.json or {}
    dias = data.get('dias', 30)
    
    data_inicio = date.today() - timedelta(days=dias)
    resultado = ImportadorIndices.importar_todos_indices(data_inicio, date.today())
    
    return jsonify({
        'dias': dias,
        'resultados': resultado,
        'total_registros': sum(resultado.values())
    }), 200


# ============================================================================
# CONSULTAS DE ÍNDICES
# ============================================================================

@atualizacao_bp.route('/indices', methods=['GET'])
@handle_errors
def listar_indices():
    """
    Lista todos os índices disponíveis
    
    GET /api/atualizacao-monetaria/indices
    """
    indices = IndiceMonetario.query.filter_by(ativo=True).all()
    
    resultado = []
    for indice in indices:
        # Contar registros
        total_registros = HistoricoIndice.query.filter_by(indice_id=indice.id_indice).count()
        
        # Último registro
        ultimo = HistoricoIndice.query.filter_by(
            indice_id=indice.id_indice
        ).order_by(HistoricoIndice.data_referencia.desc()).first()
        
        resultado.append({
            'id': indice.id_indice,
            'nome': indice.nome,
            'descricao': indice.descricao,
            'fonte_oficial': indice.fonte_oficial,
            'total_registros': total_registros,
            'ultima_atualizacao': ultimo.data_referencia.isoformat() if ultimo else None,
            'ultimo_valor': float(ultimo.valor) if ultimo else None
        })
    
    return jsonify(resultado), 200


@atualizacao_bp.route('/indices/<int:indice_id>/historico', methods=['GET'])
@handle_errors
def obter_historico_indice(indice_id):
    """
    Obtém histórico de um índice
    
    GET /api/atualizacao-monetaria/indices/1/historico?data_inicio=2024-01-01&limite=100
    """
    # Parâmetros
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    limite = request.args.get('limite', 100, type=int)
    
    # Query
    query = HistoricoIndice.query.filter_by(indice_id=indice_id)
    
    if data_inicio_str:
        data_inicio = date.fromisoformat(data_inicio_str)
        query = query.filter(HistoricoIndice.data_referencia >= data_inicio)
    
    if data_fim_str:
        data_fim = date.fromisoformat(data_fim_str)
        query = query.filter(HistoricoIndice.data_referencia <= data_fim)
    
    historico = query.order_by(HistoricoIndice.data_referencia.desc()).limit(limite).all()
    
    resultado = [{
        'data_referencia': h.data_referencia.isoformat(),
        'valor': float(h.valor)
    } for h in historico]
    
    return jsonify(resultado), 200


# ============================================================================
# SCHEDULER
# ============================================================================

@atualizacao_bp.route('/scheduler/jobs', methods=['GET'])
@handle_errors
def listar_jobs():
    """
    Lista jobs agendados
    
    GET /api/atualizacao-monetaria/scheduler/jobs
    """
    jobs = scheduler_global.listar_jobs()
    
    return jsonify(jobs), 200


@atualizacao_bp.route('/scheduler/executar', methods=['POST'])
@handle_errors
def executar_job_agora():
    """
    Executa atualização imediatamente
    
    POST /api/atualizacao-monetaria/scheduler/executar
    Body: {tipo: 'recente' ou 'completa'}
    """
    data = request.json or {}
    tipo = data.get('tipo', 'recente')
    
    resultado = scheduler_global.executar_agora(tipo)
    
    return jsonify({
        'tipo': tipo,
        'resultados': resultado,
        'total_registros': sum(resultado.values())
    }), 200


@atualizacao_bp.route('/scheduler/agendar/diaria', methods=['POST'])
@handle_errors
def agendar_diaria():
    """
    Agenda atualização diária
    
    POST /api/atualizacao-monetaria/scheduler/agendar/diaria
    Body: {hora, minuto}
    """
    data = request.json or {}
    hora = data.get('hora', 8)
    minuto = data.get('minuto', 0)
    
    job = scheduler_global.agendar_atualizacao_diaria(hora, minuto)
    
    return jsonify({
        'job_id': job.id,
        'agendado_para': f"{hora:02d}:{minuto:02d}",
        'proximo': job.next_run_time.isoformat() if job.next_run_time else None
    }), 201


# ============================================================================
# REGISTRO DO BLUEPRINT
# ============================================================================

def registrar_rotas(app):
    """Registra o blueprint no app Flask"""
    app.register_blueprint(atualizacao_bp)
