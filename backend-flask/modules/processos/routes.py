"""Rotas API para módulo de Processos"""
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from functools import wraps

from .services import ProcessoService
from .etl_service import ProcessoETLService
from .schemas import (
    ProcessoSchema,
    ProcessoCreateSchema,
    ProcessoUpdateSchema,
    FiltroPesquisaSchema,
    TributoSchema,
    TeseTributariaSchema,
    IndiceMonetarioSchema
)
from models import Tributo, TeseTributaria, IndiceMonetario

# Criar Blueprint
processos_bp = Blueprint('processos', __name__, url_prefix='/api/processos')


# Decorador para tratamento de erros
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
            return jsonify({'error': 'Erro interno do servidor', 'details': str(e)}), 500
    return decorated_function


# ============================================================================
# CRUD PROCESSOS
# ============================================================================

@processos_bp.route('', methods=['POST'])
@handle_errors
def criar_processo():
    """
    Cria um novo processo
    
    POST /api/processos
    Body: JSON com dados do processo
    """
    schema = ProcessoCreateSchema()
    data = schema.load(request.json)
    
    processo = ProcessoService.criar_processo(data)
    
    result_schema = ProcessoSchema()
    return jsonify(result_schema.dump(processo)), 201


@processos_bp.route('', methods=['GET'])
@handle_errors
def listar_processos():
    """
    Lista processos com filtros e paginação
    
    GET /api/processos?numero_cnj=xxx&page=1&per_page=20
    """
    schema = FiltroPesquisaSchema()
    filtros = schema.load(request.args)
    
    resultado = ProcessoService.listar_processos(
        filtros=filtros,
        page=filtros.get('page', 1),
        per_page=filtros.get('per_page', 20),
        ordenacao=filtros.get('ordenacao', 'data_criacao'),
        ordem=filtros.get('ordem', 'desc')
    )
    
    return jsonify(resultado), 200


@processos_bp.route('/<int:processo_id>', methods=['GET'])
@handle_errors
def obter_processo(processo_id):
    """
    Obtém um processo por ID
    
    GET /api/processos/123
    """
    processo = ProcessoService.obter_processo(processo_id)
    
    if not processo:
        return jsonify({'error': 'Processo não encontrado'}), 404
    
    schema = ProcessoSchema()
    return jsonify(schema.dump(processo)), 200


@processos_bp.route('/<int:processo_id>', methods=['PUT'])
@handle_errors
def atualizar_processo(processo_id):
    """
    Atualiza um processo
    
    PUT /api/processos/123
    Body: JSON com dados a atualizar
    """
    schema = ProcessoUpdateSchema()
    data = schema.load(request.json)
    
    processo = ProcessoService.atualizar_processo(processo_id, data)
    
    if not processo:
        return jsonify({'error': 'Processo não encontrado'}), 404
    
    result_schema = ProcessoSchema()
    return jsonify(result_schema.dump(processo)), 200


@processos_bp.route('/<int:processo_id>', methods=['DELETE'])
@handle_errors
def deletar_processo(processo_id):
    """
    Deleta um processo (soft delete)
    
    DELETE /api/processos/123
    """
    soft_delete = request.args.get('soft', 'true').lower() == 'true'
    
    sucesso = ProcessoService.deletar_processo(processo_id, soft_delete=soft_delete)
    
    if not sucesso:
        return jsonify({'error': 'Processo não encontrado'}), 404
    
    return jsonify({'message': 'Processo deletado com sucesso'}), 200


# ============================================================================
# BUSCA
# ============================================================================

@processos_bp.route('/buscar', methods=['GET'])
@handle_errors
def buscar_processos():
    """
    Busca processos por termo
    
    GET /api/processos/buscar?q=0001234&limite=10
    """
    termo = request.args.get('q', '')
    limite = int(request.args.get('limite', 10))
    
    if not termo:
        return jsonify({'error': 'Termo de busca não fornecido'}), 400
    
    processos = ProcessoService.buscar_processos(termo, limite)
    
    schema = ProcessoSchema(many=True)
    return jsonify(schema.dump(processos)), 200


# ============================================================================
# DADOS AUXILIARES
# ============================================================================

@processos_bp.route('/tributos', methods=['GET'])
@handle_errors
def listar_tributos():
    """
    Lista tributos disponíveis
    
    GET /api/processos/tributos
    """
    tributos = Tributo.query.filter_by(ativo=True).all()
    
    schema = TributoSchema(many=True)
    return jsonify(schema.dump(tributos)), 200


@processos_bp.route('/tributos/<int:tributo_id>/teses', methods=['GET'])
@handle_errors
def listar_teses_por_tributo(tributo_id):
    """
    Lista teses de um tributo
    
    GET /api/processos/tributos/1/teses
    """
    teses = TeseTributaria.query.filter_by(
        tributo_id=tributo_id,
        ativo=True
    ).all()
    
    schema = TeseTributariaSchema(many=True)
    return jsonify(schema.dump(teses)), 200


@processos_bp.route('/indices-monetarios', methods=['GET'])
@handle_errors
def listar_indices_monetarios():
    """
    Lista índices monetários
    
    GET /api/processos/indices-monetarios
    """
    indices = IndiceMonetario.query.filter_by(ativo=True).all()
    
    schema = IndiceMonetarioSchema(many=True)
    return jsonify(schema.dump(indices)), 200


# ============================================================================
# SCHEMA DINÂMICO
# ============================================================================

@processos_bp.route('/schema/<int:natureza_id>', methods=['GET'])
@handle_errors
def obter_schema_formulario(natureza_id):
    """
    Obtém schema dinâmico de formulário por natureza
    
    GET /api/processos/schema/1
    """
    from .dynamic_forms import FormularioDinamicoService
    
    schema = FormularioDinamicoService.obter_schema_por_natureza(natureza_id)
    
    if not schema:
        return jsonify({'error': 'Schema não encontrado para esta natureza'}), 404
    
    return jsonify(schema), 200


# ============================================================================
# ESTATÍSTICAS
# ============================================================================

@processos_bp.route('/estatisticas', methods=['GET'])
@handle_errors
def obter_estatisticas():
    """
    Obtém estatísticas gerais dos processos
    
    GET /api/processos/estatisticas
    """
    from models import Processo
    from sqlalchemy import func, case
    
    # Total de processos ativos
    total = Processo.query.filter_by(ativo=True).count()
    
    # Estatísticas por natureza
    por_natureza = db.session.query(
        Processo.natureza_id,
        func.count(Processo.id_processo).label('count')
    ).filter_by(ativo=True)\
     .group_by(Processo.natureza_id)\
     .all()
    
    # Estatísticas por status
    por_status = db.session.query(
        Processo.status_id,
        func.count(Processo.id_processo).label('count')
    ).filter_by(ativo=True)\
     .group_by(Processo.status_id)\
     .all()
    
    # Estatísticas por risco
    por_risco = db.session.query(
        Processo.risco_id,
        func.count(Processo.id_processo).label('count')
    ).filter_by(ativo=True)\
     .group_by(Processo.risco_id)\
     .all()
    
    # Valores financeiros
    valores = db.session.query(
        func.sum(Processo.valor_causa).label('total_valor_causa'),
        func.sum(Processo.valor_envolvido).label('total_valor_envolvido'),
        func.sum(Processo.contingencia).label('total_contingencia'),
        func.avg(Processo.valor_causa).label('media_valor_causa')
    ).filter_by(ativo=True).first()
    
    # Processos por ano (data distribuição)
    por_ano = db.session.query(
        func.extract('year', Processo.data_distribuicao).label('ano'),
        func.count(Processo.id_processo).label('count')
    ).filter(Processo.ativo == True, Processo.data_distribuicao != None)\
     .group_by('ano')\
     .order_by('ano')\
     .all()
    
    return jsonify({
        'total_processos': total,
        'por_natureza': {
            int(nat_id) if nat_id else 0: count 
            for nat_id, count in por_natureza
        },
        'por_status': {
            int(status_id) if status_id else 0: count 
            for status_id, count in por_status
        },
        'por_risco': {
            int(risco_id) if risco_id else 0: count 
            for risco_id, count in por_risco
        },
        'valores_financeiros': {
            'total_valor_causa': float(valores.total_valor_causa or 0),
            'total_valor_envolvido': float(valores.total_valor_envolvido or 0),
            'total_contingencia': float(valores.total_contingencia or 0),
            'media_valor_causa': float(valores.media_valor_causa or 0)
        },
        'por_ano': {
            int(ano): count 
            for ano, count in por_ano
        }
    }), 200


# ============================================================================
# IMPORTERS
# ============================================================================

@processos_bp.route('/importar-lote', methods=['POST'])
@handle_errors
def importar_lote():
    """
    Importa processos via JSON em lote (Frontend ETL)
    
    POST /api/processos/importar-lote
    Body: { "processos": [...] }
    """
    data = request.json
    lista = data.get('processos', [])
    
    if not lista:
        return jsonify({'error': 'Lista de processos vazia'}), 400
        
    resultado = ProcessoService.criar_processo_lote(lista)
    
    return jsonify(resultado), 200

# ============================================================================
# IMPORTAÇÃO ETL
# ============================================================================

@processos_bp.route('/importar', methods=['POST'])
@handle_errors
def importar_planilha():
    """
    Importa planilha Excel/CSV com ETL automático
    
    POST /api/processos/importar
   Content-Type: multipart/form-data
    File: arquivo
    """
    if 'arquivo' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    arquivo = request.files['arquivo']
    
    if arquivo.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio'}), 400
    
    # Validar extensão
    extensoes_permitidas = {'xlsx', 'xls', 'csv'}
    ext = arquivo.filename.rsplit('.', 1)[1].lower() if '.' in arquivo.filename else ''
    
    if ext not in extensoes_permitidas:
        return jsonify({'error': f'Formato não suportado. Use: {", ".join(extensoes_permitidas)}'}), 400
    
    # Ler bytes do arquivo
    arquivo_bytes = arquivo.read()
    
    # Executar ETL
    etl_service = ProcessoETLService()
    resultado = etl_service.importar_planilha(arquivo_bytes, arquivo.filename)
    
    status_code = 200 if resultado.get('sucesso') else 400
    return jsonify(resultado), status_code


#============================================================================
# REGISTRO DO BLUEPRINT
# ============================================================================

def registrar_rotas(app):
    """Registra o blueprint no app Flask"""
    app.register_blueprint(processos_bp)
