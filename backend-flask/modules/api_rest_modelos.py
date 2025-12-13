"""
API REST para Modelos Jurídicos - Templates de Documentos
"""
from flask import Blueprint, jsonify, request
from main import db
from models import CategoriaTemplate, Documento, VersaoDocumento
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

modelos_api = Blueprint('modelos_api', __name__, url_prefix='/api/modelos')

# Templates mockados (em produção, viriam do banco)
TEMPLATES_MOCK = [
    {
        'id': 1,
        'nome': 'Contrato de Prestação de Serviços',
        'categoria': 'Contratos',
        'descricao': 'Modelo padrão de contrato de prestação de serviços',
        'campos_personalizaveis': ['contratante', 'contratado', 'valor', 'prazo', 'servicos']
    },
    {
        'id': 2,
        'nome': 'Procuração Ad Judicia',
        'categoria': 'Procurações',
        'descricao': 'Procuração para representação judicial',
        'campos_personalizaveis': ['outorgante', 'outorgado_oab', 'poderes', 'prazo']
    },
    {
        'id': 3,
        'nome': 'Petição Inicial',
        'categoria': 'Petições',
        'descricao': 'Modelo de petição inicial genérica',
        'campos_personalizaveis': ['autor', 'reu', 'pedidos', 'fundamentos', 'valor_causa']
    },
    {
        'id': 4,
        'nome': 'Contestação',
        'categoria': 'Petições',
        'descricao': 'Modelo de contestação',
        'campos_personalizaveis': ['reu', 'autor', 'defesa', 'preliminares']
    },
    {
        'id': 5,
        'nome': 'Acordo Extrajudicial',
        'categoria': 'Acordos',
        'descricao': 'Modelo de acordo entre partes',
        'campos_personalizaveis': ['parte1', 'parte2', 'objeto', 'condicoes', 'valor']
    }
]

@modelos_api.route('', methods=['GET'])
def listar_modelos():
    """
    Lista todos os modelos de documentos disponíveis
    Query params: categoria
    """
    try:
        categoria = request.args.get('categoria', '')
        
        modelos = TEMPLATES_MOCK.copy()
        
        if categoria:
            modelos = [m for m in modelos if m['categoria'] == categoria]
        
        return jsonify({'modelos': modelos}), 200
        
    except Exception as e:
        logger.error(f"Erro ao listar modelos: {e}")
        return jsonify({'error': 'Erro ao listar modelos'}), 500

@modelos_api.route('/<int:modelo_id>', methods=['GET'])
def obter_modelo(modelo_id):
    """
    Retorna detalhes de um modelo específico
    """
    try:
        modelo = next((m for m in TEMPLATES_MOCK if m['id'] == modelo_id), None)
        
        if not modelo:
            return jsonify({'error': 'Modelo não encontrado'}), 404
        
        # Adicionar template de exemplo
        modelo_completo = modelo.copy()
        modelo_completo['template'] = f"""
[CABEÇALHO]

{modelo['nome'].upper()}

[CORPO DO DOCUMENTO]

Este é um template de {modelo['nome']} que pode ser personalizado com os seguintes campos:
{', '.join(modelo['campos_personalizaveis'])}

[ASSINATURAS]

__________________________
Parte 1

__________________________
Parte 2
"""
        
        return jsonify(modelo_completo), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter modelo {modelo_id}: {e}")
        return jsonify({'error': 'Modelo não encontrado'}), 404

@modelos_api.route('/<int:modelo_id>/gerar', methods=['POST'])
def gerar_documento(modelo_id):
    """
    Gera um documento a partir de um modelo
    Body: { "dados": { "campo1": "valor1", ... } }
    """
    try:
        modelo = next((m for m in TEMPLATES_MOCK if m['id'] == modelo_id), None)
        if not modelo:
            return jsonify({'error': 'Modelo não encontrado'}), 404
        
        data = request.get_json()
        dados = data.get('dados', {})
        
        # Validar campos obrigatórios
        campos_faltantes = [c for c in modelo['campos_personalizaveis'] if c not in dados]
        if campos_faltantes:
            return jsonify({
                'error': 'Campos obrigatórios faltando',
                'campos': campos_faltantes
            }), 400
        
        # Gerar documento (mock)
        documento_gerado = f"""
{modelo['nome'].upper()}

---

Gerado automaticamente em {datetime.now().strftime('%d/%m/%Y')}

"""
        for campo, valor in dados.items():
            documento_gerado += f"\n{campo.upper()}: {valor}"
        
        documento_gerado += f"""

---

Este documento foi gerado a partir do modelo "{modelo['nome']}" do sistema Legal Pro.

[Espaço para assinaturas]
"""
        
        # Criar documento no banco
        documento = Documento(
            titulo=f"{modelo['nome']} - {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            tipo='gerado',
            usuario_id=1,  # TODO: Usuário autenticado
            data_criacao=datetime.now()
        )
        db.session.add(documento)
        db.session.flush()
        
        # Criar versão
        versao = VersaoDocumento(
            documento_id=documento.id,
            numero_versao=1,
            conteudo=documento_gerado,
            usuario_id=1,
            comentario=f'Gerado a partir do modelo {modelo_id}',
            data_criacao=datetime.now()
        )
        db.session.add(versao)
        db.session.commit()
        
        return jsonify({
            'documento_id': documento.id,
            'versao_id': versao.id,
            'modelo_id': modelo_id,
            'titulo': documento.titulo,
            'conteudo': documento_gerado,
            'message': 'Documento gerado com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao gerar documento: {e}")
        return jsonify({'error': 'Erro ao gerar documento'}), 500

@modelos_api.route('/<int:modelo_id>/personalizar', methods=['POST'])
def personalizar_modelo(modelo_id):
    """
    Personaliza um modelo com dados do usuário
    Body: { "dados": {...}, "customizacoes": {...} }
    """
    try:
        modelo = next((m for m in TEMPLATES_MOCK if m['id'] == modelo_id), None)
        if not modelo:
            return jsonify({'error': 'Modelo não encontrado'}), 404
        
        data = request.get_json()
        dados = data.get('dados', {})
        customizacoes = data.get('customizacoes', {})
        
        # Preview do documento personalizado
        preview = {
            'modelo': modelo['nome'],
            'categoria': modelo['categoria'],
            'dados_preenchidos': dados,
            'customizacoes_aplicadas': customizacoes,
            'preview_texto': f"Preview de {modelo['nome']} com personalizações aplicadas...",
            'pronto_para_gerar': len(dados) >= len(modelo['campos_personalizaveis'])
        }
        
        return jsonify(preview), 200
        
    except Exception as e:
        logger.error(f"Erro ao personalizar modelo {modelo_id}: {e}")
        return jsonify({'error': 'Erro ao personalizar modelo'}), 500

@modelos_api.route('/categorias', methods=['GET'])
def listar_categorias():
    """
    Lista todas as categorias de modelos
    """
    categorias = list(set([m['categoria'] for m in TEMPLATES_MOCK]))
    categorias.sort()
    
    categorias_detalhadas = [
        {
            'nome': cat,
            'total_modelos': len([m for m in TEMPLATES_MOCK if m['categoria'] == cat])
        }
        for cat in categorias
    ]
    
    return jsonify({'categorias': categorias_detalhadas}), 200

def register_modelos_api(app):
    """Registra o blueprint de modelos no app"""
    app.register_blueprint(modelos_api)
    print("✅ API REST de Modelos Jurídicos registrada")
    logger.info("✅ API REST de Modelos Jurídicos registrada com sucesso")
