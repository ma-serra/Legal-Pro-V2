"""
API REST para Processos Jurídicos - CRUD Completo
"""
from flask import Blueprint, jsonify, request
from sqlalchemy import desc, func, or_
from main import db
from models import ProcessoJuridico, User
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

processos_api = Blueprint('processos_api', __name__, url_prefix='/api/processos')

# Lista de áreas jurídicas disponíveis
AREAS_JURIDICAS = [
    'Direito Civil',
    'Direito Trabalhista',
    'Direito Empresarial',
    'Direito Tributário',
    'Direito Penal',
    'Direito Administrativo',
    'Direito Previdenciário',
    'Direito do Consumidor',
    'Direito Ambiental',
    'Direito Digital'
]

@processos_api.route('', methods=['GET'])
def listar_processos():
    """
    Lista todos os processos com paginação e filtros
    Query params: page, limit, area_juridica, nivel_risco, status, search
    """
    try:
        # Parâmetros de paginação
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # Filtros
        area_juridica = request.args.get('area_juridica', '')
        nivel_risco = request.args.get('nivel_risco', '')
        status = request.args.get('status', '')
        search = request.args.get('search', '')
        
        # Query base
        query = ProcessoJuridico.query
        
        # Aplicar filtros
        if area_juridica:
            query = query.filter(ProcessoJuridico.area_juridica == area_juridica)
        if nivel_risco:
            query = query.filter(ProcessoJuridico.nivel_risco == nivel_risco)
        if status:
            query = query.filter(ProcessoJuridico.status == status)
        if search:
            query = query.filter(
                or_(
                    ProcessoJuridico.numero_cnj.ilike(f'%{search}%'),
                    ProcessoJuridico.cliente.ilike(f'%{search}%')
                )
            )
        
        # Ordenar por data de cadastro (mais recentes primeiro)
        query = query.order_by(desc(ProcessoJuridico.data_cadastro))
        
        # Paginação
        pagination = query.paginate(page=page, per_page=limit, error_out=False)
        
        # Serializar processos
        processos = [{
            'id': p.id,
            'numero_cnj': p.numero_cnj,
            'cliente': p.cliente,
            'area_juridica': p.area_juridica,
            'valor_causa': float(p.valor_causa) if p.valor_causa else 0,
            'nivel_risco': p.nivel_risco,
            'status': p.status,
            'data_cadastro': p.data_cadastro.isoformat() if p.data_cadastro else None,
            'comarca': p.comarca if hasattr(p, 'comarca') else None,
            'vara': p.vara if hasattr(p, 'vara') else None
        } for p in pagination.items]
        
        return jsonify({
            'processos': processos,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': limit
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao listar processos: {e}")
        return jsonify({'error': 'Erro ao listar processos'}), 500

@processos_api.route('/<int:processo_id>', methods=['GET'])
def obter_processo(processo_id):
    """
    Retorna detalhes de um processo específico
    """
    try:
        processo = ProcessoJuridico.query.get_or_404(processo_id)
        
        return jsonify({
            'id': processo.id,
            'numero_cnj': processo.numero_cnj,
            'cliente': processo.cliente,
            'area_juridica': processo.area_juridica,
            'valor_causa': float(processo.valor_causa) if processo.valor_causa else 0,
            'nivel_risco': processo.nivel_risco,
            'status': processo.status,
            'data_cadastro': processo.data_cadastro.isoformat() if processo.data_cadastro else None,
            'comarca': processo.comarca if hasattr(processo, 'comarca') else None,
            'vara': processo.vara if hasattr(processo, 'vara') else None,
            'observacoes': processo.observacoes if hasattr(processo, 'observacoes') else None
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter processo {processo_id}: {e}")
        return jsonify({'error': 'Processo não encontrado'}), 404

@processos_api.route('', methods=['POST'])
def criar_processo():
    """
    Cria um novo processo
    Body: { numero_cnj, cliente, area_juridica, valor_causa, nivel_risco, status }
    """
    try:
        data = request.get_json()
        
        # Validações
        if not data.get('numero_cnj'):
            return jsonify({'error': 'Número CNJ é obrigatório'}), 400
        if not data.get('cliente'):
            return jsonify({'error': 'Cliente é obrigatório'}), 400
        if not data.get('area_juridica'):
            return jsonify({'error': 'Área jurídica é obrigatória'}), 400
        
        # Criar processo
        processo = ProcessoJuridico(
            numero_cnj=data['numero_cnj'],
            cliente=data['cliente'],
            area_juridica=data['area_juridica'],
            valor_causa=data.get('valor_causa', 0),
            nivel_risco=data.get('nivel_risco', 'Médio'),
            status=data.get('status', 'Ativo'),
            data_cadastro=datetime.now()
        )
        
        # Campos opcionais
        if hasattr(ProcessoJuridico, 'comarca') and data.get('comarca'):
            processo.comarca = data['comarca']
        if hasattr(ProcessoJuridico, 'vara') and data.get('vara'):
            processo.vara = data['vara']
        if hasattr(ProcessoJuridico, 'observacoes') and data.get('observacoes'):
            processo.observacoes = data['observacoes']
        
        db.session.add(processo)
        db.session.commit()
        
        return jsonify({
            'id': processo.id,
            'numero_cnj': processo.numero_cnj,
            'message': 'Processo criado com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao criar processo: {e}")
        return jsonify({'error': 'Erro ao criar processo'}), 500

@processos_api.route('/<int:processo_id>', methods=['PUT'])
def atualizar_processo(processo_id):
    """
    Atualiza um processo existente
    """
    try:
        processo = ProcessoJuridico.query.get_or_404(processo_id)
        data = request.get_json()
        
        # Atualizar campos
        if 'numero_cnj' in data:
            processo.numero_cnj = data['numero_cnj']
        if 'cliente' in data:
            processo.cliente = data['cliente']
        if 'area_juridica' in data:
            processo.area_juridica = data['area_juridica']
        if 'valor_causa' in data:
            processo.valor_causa = data['valor_causa']
        if 'nivel_risco' in data:
            processo.nivel_risco = data['nivel_risco']
        if 'status' in data:
            processo.status = data['status']
        
        # Campos opcionais
        if hasattr(ProcessoJuridico, 'comarca') and 'comarca' in data:
            processo.comarca = data['comarca']
        if hasattr(ProcessoJuridico, 'vara') and 'vara' in data:
            processo.vara = data['vara']
        if hasattr(ProcessoJuridico, 'observacoes') and 'observacoes' in data:
            processo.observacoes = data['observacoes']
        
        db.session.commit()
        
        return jsonify({
            'id': processo.id,
            'message': 'Processo atualizado com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao atualizar processo {processo_id}: {e}")
        return jsonify({'error': 'Erro ao atualizar processo'}), 500

@processos_api.route('/<int:processo_id>', methods=['DELETE'])
def deletar_processo(processo_id):
    """
    Deleta um processo
    """
    try:
        processo = ProcessoJuridico.query.get_or_404(processo_id)
        
        db.session.delete(processo)
        db.session.commit()
        
        return jsonify({'message': 'Processo deletado com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao deletar processo {processo_id}: {e}")
        return jsonify({'error': 'Erro ao deletar processo'}), 500

@processos_api.route('/areas', methods=['GET'])
def listar_areas():
    """
    Lista todas as áreas jurídicas disponíveis
    """
    return jsonify({'areas': AREAS_JURIDICAS}), 200

@processos_api.route('/stats', methods=['GET'])
def estatisticas_processos():
    """
    Retorna estatísticas sobre os processos
    """
    try:
        total = ProcessoJuridico.query.count()
        ativos = ProcessoJuridico.query.filter_by(status='Ativo').count()
        alto_risco = ProcessoJuridico.query.filter_by(nivel_risco='Alto').count()
        
        # Valor total das causas
        valor_total = db.session.query(func.sum(ProcessoJuridico.valor_causa)).scalar() or 0
        
        return jsonify({
            'total': total,
            'ativos': ativos,
            'alto_risco': alto_risco,
            'valor_total': float(valor_total)
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de processos: {e}")
        return jsonify({'error': 'Erro ao obter estatísticas'}), 500

def register_processos_api(app):
    """Registra o blueprint de processos no app"""
    app.register_blueprint(processos_api)
    print("✅ API REST de Processos registrada")
    logger.info("✅ API REST de Processos registrada com sucesso")
