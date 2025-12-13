"""
API REST para Comparação de Documentos
"""
from flask import Blueprint, jsonify, request
from main import db
from models import AnaliseComparativa, AnaliseDocumento, Documento, User
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

comparacao_api = Blueprint('comparacao_api', __name__, url_prefix='/api/documentos')

@comparacao_api.route('/upload', methods=['POST'])
def upload_documento():
    """
    Upload de documento para análise
    Aceita: text/plain, application/pdf, application/msword
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Arquivo não fornecido'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nome de arquivo vazio'}), 400
        
        # Ler conteúdo
        if file.content_type == 'text/plain':
            conteudo = file.read().decode('utf-8')
        else:
            # TODO: Implementar extração de PDF/DOCX
            return jsonify({'error': 'Tipo de arquivo não suportado ainda. Use .txt'}), 400
        
        # Criar documento
        # TODO: Associar com usuário autenticado
        documento = Documento(
            titulo=file.filename,
            tipo='upload',
            usuario_id=1,  # Mock
            data_criacao=datetime.now()
        )
        db.session.add(documento)
        db.session.flush()
        
        # Criar primeira versão
        from models import VersaoDocumento
        versao = VersaoDocumento(
            documento_id=documento.id,
            numero_versao=1,
            conteudo=conteudo,
            usuario_id=1,  # Mock
            data_criacao=datetime.now()
        )
        db.session.add(versao)
        db.session.commit()
        
        return jsonify({
            'documento_id': documento.id,
            'versao_id': versao.id,
            'titulo': documento.titulo,
            'tamanho': len(conteudo),
            'message': 'Documento enviado com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao fazer upload: {e}")
        return jsonify({'error': 'Erro ao processar arquivo'}), 500

@comparacao_api.route('/comparar', methods=['POST'])
def comparar_documentos():
    """
    Compara 2 ou mais documentos
    Body: { "documentos_ids": [1, 2, 3] } ou { "textos": ["texto1", "texto2"] }
    """
    try:
        data = request.get_json()
        
        # Opção 1: IDs de documentos existentes
        if 'documentos_ids' in data:
            doc_ids = data['documentos_ids']
            if len(doc_ids) < 2:
                return jsonify({'error': 'Mínimo 2 documentos para comparar'}), 400
            
            # Buscar documentos
            documentos = Documento.query.filter(Documento.id.in_(doc_ids)).all()
            if len(documentos) != len(doc_ids):
                return jsonify({'error': 'Um ou mais documentos não encontrados'}), 404
            
            textos = []
            for doc in documentos:
                versao = doc.versao_atual()
                if versao:
                    textos.append(versao.conteudo)
        
        # Opção 2: Textos diretos
        elif 'textos' in data:
            textos = data['textos']
            if len(textos) < 2:
                return jsonify({'error': 'Mínimo 2 textos para comparar'}), 400
        else:
            return jsonify({'error': 'Forneça documentos_ids ou textos'}), 400
        
        # Realizar comparação (mockado)
        # TODO: Integrar com módulo real de comparação
        resultado_mock = {
            'total_documentos': len(textos),
            'analise': {
                'similaridade_global': 0.75,
                'diferencas_encontradas': 42,
                'pontos_comuns': 156,
                'recomendacoes': [
                    'Revisar cláusulas divergentes',
                    'Verificar termos específicos',
                    'Considerar padronização'
                ]
            },
            'detalhes': [
                {
                    'documento_index': i,
                    'caracteristicas': {
                        'palavras': len(texto.split()),
                        'caracteres': len(texto),
                        'paragrafos': texto.count('\n\n') + 1
                    }
                } for i, texto in enumerate(textos)
            ],
            'comparacao_pareada': [
                {
                    'doc_a': 0,
                    'doc_b': 1,
                    'similaridade': 0.82,
                    'diferencas_principais': [
                        'Cláusula 3.1: valores diferentes',
                        'Seção 4: ausente no doc B'
                    ]
                }
            ],
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(resultado_mock), 200
        
    except Exception as e:
        logger.error(f"Erro ao comparar documentos: {e}")
        return jsonify({'error': 'Erro ao comparar documentos'}), 500

@comparacao_api.route('/comparacoes', methods=['GET'])
def listar_comparacoes():
    """
    Lista histórico de comparações
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        
        comparacoes = AnaliseComparativa.query.order_by(
            AnaliseComparativa.data_comparacao.desc()
        ).limit(limit).all()
        
        result = []
        for comp in comparacoes:
            result.append({
                'id': comp.id,
                'data_comparacao': comp.data_comparacao.isoformat() if comp.data_comparacao else None,
                'nivel_concordancia': comp.nivel_concordancia,
                'preview': comp.resultado_comparacao[:200] + '...' if len(comp.resultado_comparacao) > 200 else comp.resultado_comparacao
            })
        
        return jsonify({'comparacoes': result}), 200
        
    except Exception as e:
        logger.error(f"Erro ao listar comparações: {e}")
        return jsonify({'error': 'Erro ao listar comparações'}), 500

def register_comparacao_api(app):
    """Registra o blueprint de comparação no app"""
    app.register_blueprint(comparacao_api)
    print("✅ API REST de Comparação de Documentos registrada")
    logger.info("✅ API REST de Comparação registrada com sucesso")
