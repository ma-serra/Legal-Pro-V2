"""
Routes API para ML Tributário
Endpoints REST para predições e gerenciamento de modelos
"""
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError, Schema, fields
from functools import wraps
from typing import List
import logging

from .predictor import TributarioPredictor, quick_predict
from .trainer import TributarioTrainer
from models_processos import MLModeloTributario, MLPredicaoTributario

logger = logging.getLogger(__name__)

# Criar Blueprint
ml_tributario_bp = Blueprint('ml_tributario', __name__, url_prefix='/api/ml/tributario')


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
        except FileNotFoundError as e:
            return jsonify({'error': 'Modelo não encontrado', 'details': str(e)}), 404
        except Exception as e:
            logger.error(f"Erro interno: {e}", exc_info=True)
            return jsonify({'error': 'Erro interno do servidor', 'details': str(e)}), 500
    return decorated_function


# Schemas de validação
class PredictRequestSchema(Schema):
    """Schema para request de predição"""
    processo_id = fields.Integer(required=True)
    versao_modelo = fields.String(required=False)
    save_to_db = fields.Boolean(required=False, load_default=True)


class BatchPredictRequestSchema(Schema):
    """Schema para request de predição em lote"""
    processo_ids = fields.List(fields.Integer(), required=True)
    versao_modelo = fields.String(required=False)
    save_to_db = fields.Boolean(required=False, load_default=True)


class RetrainRequestSchema(Schema):
    """Schema para request de re-treinamento"""
    model_type = fields.String(required=False, load_default='ridge')
    version = fields.String(required=False)
    hyperparameter_tuning = fields.Boolean(required=False, load_default=False)


# ============================================================================
# ENDPOINTS DE PREDIÇÃO
# ============================================================================

@ml_tributario_bp.route('/predict', methods=['POST'])
@handle_errors
def predict_single():
    """
    Prediz valor contingência para um processo
    
    POST /api/ml/tributario/predict
    
    Body:
    {
        "processo_id": 123,
        "versao_modelo": "v1.0.0",  // opcional
        "save_to_db": true  // opcional, default true
    }
    
    Returns:
    {
        "processo_id": 123,
        "valor_contingencia_predito": 50000.00,
        "confianca": 0.87,
        "modelo_versao": "v1.0.0",
        "modelo_algoritmo": "xgboost_regressor"
    }
    """
    # Validar request
    schema = PredictRequestSchema()
    data = schema.load(request.json)
    
    # Criar predictor
    predictor = TributarioPredictor(versao_modelo=data.get('versao_modelo'))
    
    # Predizer
    resultado = predictor.predict_processo(
        processo_id=data['processo_id'],
        save_to_db=data.get('save_to_db', True)
    )
    
    return jsonify(resultado), 200


@ml_tributario_bp.route('/batch-predict', methods=['POST'])
@handle_errors
def predict_batch():
    """
    Prediz valores para múltiplos processos
    
    POST /api/ml/tributario/batch-predict
    
    Body:
    {
        "processo_ids": [123, 124, 125],
        "versao_modelo": "v1.0.0",  // opcional
        "save_to_db": true  // opcional
    }
    
    Returns:
    {
        "total": 3,
        "successful": 3,
        "failed": 0,
        "results": [...]
    }
    """
    # Validar request
    schema = BatchPredictRequestSchema()
    data = schema.load(request.json)
    
    # Criar predictor
    predictor = TributarioPredictor(versao_modelo=data.get('versao_modelo'))
    
    # Predizer em lote
    resultados = predictor.predict_batch(
        processo_ids=data['processo_ids'],
        save_to_db=data.get('save_to_db', True)
    )
    
    # Contar sucessos e falhas
    successful = sum(1 for r in resultados if 'error' not in r)
    failed = len(resultados) - successful
    
    return jsonify({
        'total': len(resultados),
        'successful': successful,
        'failed': failed,
        'results': resultados
    }), 200


@ml_tributario_bp.route('/simular', methods=['POST'])
@handle_errors
def simular_cenario():
    """
    Simula predição com dados "What-If" (sem persistir)
    
    POST /api/ml/tributario/simular
    Body:
    {
        "valor_causa": 100000,
        "comarca_id": 5,
        "tributo_id": 2
    }
    """
    data = request.json
    
    predictor = TributarioPredictor()
    resultado = predictor.predict_simulation(data)
    
    return jsonify(resultado), 200


@ml_tributario_bp.route('/quick-predict/<int:processo_id>', methods=['GET'])
@handle_errors
def quick_predict_endpoint(processo_id: int):
    """
    Predição rápida (GET simples)
    
    GET /api/ml/tributario/quick-predict/123
    """
    resultado = quick_predict(processo_id)
    return jsonify(resultado), 200


# ============================================================================
# ENDPOINTS DE INFORMAÇÕES DO MODELO
# ============================================================================

@ml_tributario_bp.route('/model-info', methods=['GET'])
@handle_errors
def get_model_info():
    """
    Obtém informações do modelo ativo
    
    GET /api/ml/tributario/model-info?versao=v1.0.0
    
    Returns:
    {
        "id_modelo": 1,
        "versao": "v1.0.0",
        "algoritmo": "xgboost_regressor",
        "data_treinamento": "2024-01-15T10:30:00",
        "metricas": {
            "r2_score": 0.87,
            "mae": 4500.00,
            "rmse": 7500.00
        },
        "amostras_treino": 150,
        "amostras_teste": 30,
        "features": [...]
    }
    """
    versao = request.args.get('versao')
    
    # Buscar modelo
    if versao:
        modelo = MLModeloTributario.query.filter_by(versao=versao, ativo=True).first()
    else:
        modelo = MLModeloTributario.query.filter_by(
            tipo='regressao',
            ativo=True
        ).order_by(MLModeloTributario.id_modelo.desc()).first()
    
    if not modelo:
        return jsonify({'error': 'Modelo não encontrado'}), 404
    
    return jsonify({
        'id_modelo': modelo.id_modelo,
        'versao': modelo.versao,
        'algoritmo': modelo.algoritmo,
        'tipo': modelo.tipo,
        'data_treinamento': modelo.data_treinamento.isoformat(),
        'metricas': {
            'r2_score': float(modelo.r2_score or 0),
            'mae': float(modelo.mae or 0),
            'rmse': float(modelo.rmse or 0)
        },
        'amostras_treino': modelo.total_amostras_treino,
        'amostras_teste': modelo.total_amostras_teste,
        'features': modelo.features_utilizadas,
        # Adaptador para frontend que espera features_importantes
        'features_importantes': [
            {'nome': f, 'importancia': 1.0/len(modelo.features_utilizadas) if modelo.features_utilizadas else 0}
            for f in (modelo.features_utilizadas or [])
        ],
        'hiperparametros': modelo.hiperparametros,
        'ativo': modelo.ativo
    }), 200


@ml_tributario_bp.route('/models', methods=['GET'])
@handle_errors
def list_models():
    """
    Lista todos os modelos treinados
    
    GET /api/ml/tributario/models?tipo=regressao
    
    Returns:
    {
        "total": 3,
        "models": [...]
    }
    """
    tipo = request.args.get('tipo')
    
    query = MLModeloTributario.query
    
    if tipo:
        query = query.filter_by(tipo=tipo)
    
    modelos = query.order_by(MLModeloTributario.id_modelo.desc()).all()
    
    return jsonify({
        'total': len(modelos),
        'models': [{
            'id_modelo': m.id_modelo,
            'versao': m.versao,
            'algoritmo': m.algoritmo,
            'tipo': m.tipo,
            'r2_score': float(m.r2_score or 0),
            'mae': float(m.mae or 0),
            'data_treinamento': m.data_treinamento.isoformat(),
            'ativo': m.ativo
        } for m in modelos]
    }), 200


# ============================================================================
# ENDPOINTS DE HISTÓRICO
# ============================================================================

@ml_tributario_bp.route('/historico/<int:processo_id>', methods=['GET'])
@handle_errors
def get_historico_predicoes(processo_id: int):
    """
    Obtém histórico de predições de um processo
    
    GET /api/ml/tributario/historico/123
    
    Returns:
    {
        "processo_id": 123,
        "total_predicoes": 5,
        "predicoes": [...]
    }
    """
    predicoes = MLPredicaoTributario.query.filter_by(
        processo_id=processo_id
    ).order_by(MLPredicaoTributario.data_predicao.desc()).all()
    
    return jsonify({
        'processo_id': processo_id,
        'total_predicoes': len(predicoes),
        'predicoes': [{
            'id_predicao': p.id_predicao,
            'valor_predito': float(p.valor_contingencia_predito or 0),
            'confianca': float(p.valor_confianca or 0),
            'modelo_versao': p.modelo.versao,
            'data_predicao': p.data_predicao.isoformat()
        } for p in predicoes]
    }), 200


# ============================================================================
# ENDPOINTS DE TREINAMENTO
# ============================================================================

@ml_tributario_bp.route('/retrain', methods=['POST'])
@handle_errors
def retrain_model():
    """
    Re-treina modelo com dados atualizados
    
    POST /api/ml/tributario/retrain
    
    Body:
    {
        "model_type": "ridge",  // ou "xgboost"
        "version": "v1.1.0",  // opcional
        "hyperparameter_tuning": false  // opcional
    }
    
    Returns:
    {
        "success": true,
        "model_type": "ridge",
        "version": "v1.1.0",
        "metrics": {...},
        "model_path": "..."
    }
    """
    # Validar request
    schema = RetrainRequestSchema()
    data = schema.load(request.json or {})
    
    # Criar trainer
    trainer = TributarioTrainer()
    
    # Verificar dados disponíveis
    readiness = trainer.check_data_readiness()
    if not readiness['ready']:
        return jsonify({
            'error': 'Dados insuficientes para treinar',
            'details': readiness
        }), 400
    
    # Treinar e salvar
    result = trainer.train_and_save(
        model_type=data['model_type'],
        version=data.get('version'),
        hyperparameter_tuning=data.get('hyperparameter_tuning', False)
    )
    
    return jsonify({
        'success': True,
        'model_type': result['model_type'],
        'metrics': {
            'r2_score': result['r2_score'],
            'mae': result['mae'],
            'rmse': result['rmse']
        },
        'model_path': result['model_path']
    }), 201


@ml_tributario_bp.route('/data-status', methods=['GET'])
@handle_errors
def get_data_status():
    """
    Verifica status de dados disponíveis para treinamento
    
    GET /api/ml/tributario/data-status
    
    Returns:
    {
        "ready": true,
        "total_processos_tributarios": 150,
        "com_dados_tributarios": 150,
        "com_contingencia_definida": 120
    }
    """
    from .dataset_builder import check_data_availability
    
    availability = check_data_availability()
    ready = availability['com_contingencia_definida'] >= 50
    
    return jsonify({
        'ready': ready,
        'min_samples_required': 50,
        **availability
    }), 200


# ============================================================================
# REGISTRO DO BLUEPRINT
# ============================================================================

def registrar_rotas(app):
    """Registra o blueprint no app Flask"""
    app.register_blueprint(ml_tributario_bp)
