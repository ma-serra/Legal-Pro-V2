"""
API REST para Legal Design Pro - Gestão de Fluxos de Trabalho Jurídicos
"""
from flask import Blueprint, jsonify, request
from main import db
from models import FluxoModel, ExecucaoFluxo, User
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

legal_design_api = Blueprint('legal_design_api', __name__, url_prefix='/api/legal-design')

@legal_design_api.route('/fluxos', methods=['GET'])
def listar_fluxos():
    """
    Lista todos os fluxos de trabalho
    Query params: ativo (true/false)
    """
    try:
        ativo = request.args.get('ativo', 'true').lower() == 'true'
        
        query = FluxoModel.query
        if ativo is not None:
            query = query.filter_by(ativo=ativo)
        
        fluxos = query.order_by(FluxoModel.data_criacao.desc()).all()
        
        result = []
        for fluxo in fluxos:
            result.append({
                'id': fluxo.id,
                'nome': fluxo.nome,
                'descricao': fluxo.descricao,
                'ativo': fluxo.ativo,
                'data_criacao': fluxo.data_criacao.isoformat() if fluxo.data_criacao else None,
                'ultima_execucao': fluxo.ultima_execucao.isoformat() if fluxo.ultima_execucao else None,
                'total_execucoes': len(fluxo.execucoes) if hasattr(fluxo, 'execucoes') else 0
            })
        
        return jsonify({'fluxos': result}), 200
        
    except Exception as e:
        logger.error(f"Erro ao listar fluxos: {e}")
        return jsonify({'error': 'Erro ao listar fluxos'}), 500

@legal_design_api.route('/fluxos/<int:fluxo_id>', methods=['GET'])
def obter_fluxo(fluxo_id):
    """
    Retorna detalhes completos de um fluxo
    """
    try:
        fluxo = FluxoModel.query.get_or_404(fluxo_id)
        
        # Parse JSON fields
        agentes = json.loads(fluxo.agentes) if fluxo.agentes else []
        conexoes = json.loads(fluxo.conexoes) if fluxo.conexoes else []
        configuracao = json.loads(fluxo.configuracao) if fluxo.configuracao else {}
        
        return jsonify({
            'id': fluxo.id,
            'nome': fluxo.nome,
            'descricao': fluxo.descricao,
            'agentes': agentes,
            'conexoes': conexoes,
            'configuracao': configuracao,
            'ativo': fluxo.ativo,
            'data_criacao': fluxo.data_criacao.isoformat() if fluxo.data_criacao else None,
            'data_atualizacao': fluxo.data_atualizacao.isoformat() if fluxo.data_atualizacao else None,
            'ultima_execucao': fluxo.ultima_execucao.isoformat() if fluxo.ultima_execucao else None
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter fluxo {fluxo_id}: {e}")
        return jsonify({'error': 'Fluxo não encontrado'}), 404

@legal_design_api.route('/fluxos', methods=['POST'])
def criar_fluxo():
    """
    Cria um novo fluxo de trabalho
    Body: { "nome": "...", "descricao": "...", "agentes": [], "conexoes": [], "configuracao": {} }
    """
    try:
        data = request.get_json()
        
        if not data.get('nome'):
            return jsonify({'error': 'Nome é obrigatório'}), 400
        
        fluxo = FluxoModel(
            nome=data['nome'],
            descricao=data.get('descricao', ''),
            agentes=json.dumps(data.get('agentes', [])),
            conexoes=json.dumps(data.get('conexoes', [])),
            configuracao=json.dumps(data.get('configuracao', {})),
            ativo=data.get('ativo', True),
            criado_por_id=1  # TODO: Usar usuário autenticado
        )
        
        db.session.add(fluxo)
        db.session.commit()
        
        return jsonify({
            'id': fluxo.id,
            'nome': fluxo.nome,
            'message': 'Fluxo criado com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao criar fluxo: {e}")
        return jsonify({'error': 'Erro ao criar fluxo'}), 500

@legal_design_api.route('/fluxos/<int:fluxo_id>', methods=['PUT'])
def atualizar_fluxo(fluxo_id):
    """
    Atualiza um fluxo existente
    """
    try:
        fluxo = FluxoModel.query.get_or_404(fluxo_id)
        data = request.get_json()
        
        if 'nome' in data:
            fluxo.nome = data['nome']
        if 'descricao' in data:
            fluxo.descricao = data['descricao']
        if 'agentes' in data:
            fluxo.agentes = json.dumps(data['agentes'])
        if 'conexoes' in data:
            fluxo.conexoes = json.dumps(data['conexoes'])
        if 'configuracao' in data:
            fluxo.configuracao = json.dumps(data['configuracao'])
        if 'ativo' in data:
            fluxo.ativo = data['ativo']
        
        fluxo.data_atualizacao = datetime.now()
        db.session.commit()
        
        return jsonify({
            'id': fluxo.id,
            'message': 'Fluxo atualizado com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao atualizar fluxo {fluxo_id}: {e}")
        return jsonify({'error': 'Erro ao atualizar fluxo'}), 500

@legal_design_api.route('/executar', methods=['POST'])
def executar_fluxo():
    """
    Executa um fluxo de trabalho
    Body: { "fluxo_id": 1, "dados_entrada": {...} }
    """
    try:
        data = request.get_json()
        fluxo_id = data.get('fluxo_id')
        
        if not fluxo_id:
            return jsonify({'error': 'fluxo_id é obrigatório'}), 400
        
        fluxo = FluxoModel.query.get_or_404(fluxo_id)
        
        # Criar execução
        execucao = ExecucaoFluxo(
            fluxo_id=fluxo_id,
            usuario_id=1,  # TODO: Usar usuário autenticado
            dados_entrada=json.dumps(data.get('dados_entrada', {})),
            status='em_execucao',
            data_inicio=datetime.now()
        )
        db.session.add(execucao)
        db.session.flush()
        
        # Mock: simular execução
        # TODO: Integrar com executor real de fluxos
        resultado_mock = {
            'execucao_id': execucao.id,
            'fluxo_nome': fluxo.nome,
            'status': 'concluido',
            'resultado': 'Fluxo executado com sucesso (mockado)',
            'etapas_executadas': 5,
            'tempo_execucao_segundos': 12.5
        }
        
        # Atualizar execução
        execucao.resultado = json.dumps(resultado_mock)
        execucao.status = 'concluida'
        execucao.data_conclusao = datetime.now()
        execucao.duracao_segundos = 12.5
        
        # Atualizar última execução do fluxo
        fluxo.ultima_execucao = datetime.now()
        
        db.session.commit()
        
        return jsonify(resultado_mock), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao executar fluxo: {e}")
        return jsonify({'error': 'Erro ao executar fluxo'}), 500

@legal_design_api.route('/execucoes/<int:execucao_id>', methods=['GET'])
def obter_execucao(execucao_id):
    """
    Retorna detalhes de uma execução
    """
    try:
        execucao = ExecucaoFluxo.query.get_or_404(execucao_id)
        
        resultado = json.loads(execucao.resultado) if execucao.resultado else {}
        
        return jsonify({
            'id': execucao.id,
            'fluxo_id': execucao.fluxo_id,
            'fluxo_nome': execucao.fluxo.nome if execucao.fluxo else 'Desconhecido',
            'status': execucao.status,
            'data_inicio': execucao.data_inicio.isoformat() if execucao.data_inicio else None,
            'data_conclusao': execucao.data_conclusao.isoformat() if execucao.data_conclusao else None,
            'duracao_segundos': execucao.duracao_segundos,
            'resultado': resultado
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter execução {execucao_id}: {e}")
        return jsonify({'error': 'Execução não encontrada'}), 404

def register_legal_design_api(app):
    """Registra o blueprint de legal design no app"""
    app.register_blueprint(legal_design_api)
    print("✅ API REST de Legal Design Pro registrada")
    logger.info("✅ API REST de Legal Design Pro registrada com sucesso")
