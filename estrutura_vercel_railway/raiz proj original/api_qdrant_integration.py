
"""
API de Integração Qdrant para Sistema Jurídico
Endpoints para busca avançada com Qdrant
"""

from flask import Blueprint, request, jsonify
from busca_qdrant_juridica import buscar_juridico_qdrant, buscar_similaridade_qdrant
import logging

logger = logging.getLogger(__name__)

qdrant_api_bp = Blueprint('qdrant_api', __name__, url_prefix='/api/qdrant')

@qdrant_api_bp.route('/buscar', methods=['POST'])
def buscar_documentos():
    """Busca documentos usando Qdrant"""
    try:
        data = request.get_json()
        
        if not data or 'area' not in data or 'consulta' not in data:
            return jsonify({"erro": "Parâmetros 'area' e 'consulta' são obrigatórios"}), 400
        
        area = data['area']
        consulta = data['consulta']
        limite = data.get('limite', 10)
        
        # Filtros opcionais
        filtros = {}
        if 'tipo_documento' in data:
            filtros['tipo_documento'] = data['tipo_documento']
        if 'artigo_numero' in data:
            filtros['artigo_numero'] = data['artigo_numero']
        
        resultado = buscar_juridico_qdrant(area, consulta, limite, **filtros)
        
        return jsonify(resultado)
        
    except Exception as e:
        logger.error(f"Erro na busca Qdrant: {e}")
        return jsonify({"erro": str(e)}), 500

@qdrant_api_bp.route('/similaridade', methods=['POST'])
def buscar_similaridade():
    """Busca documentos similares"""
    try:
        data = request.get_json()
        
        if not data or 'area' not in data or 'texto_referencia' not in data:
            return jsonify({"erro": "Parâmetros 'area' e 'texto_referencia' são obrigatórios"}), 400
        
        area = data['area']
        texto_referencia = data['texto_referencia']
        limite = data.get('limite', 5)
        
        resultado = buscar_similaridade_qdrant(area, texto_referencia, limite)
        
        return jsonify({
            "status": "sucesso",
            "area": area,
            "total_resultados": len(resultado),
            "documentos_similares": resultado
        })
        
    except Exception as e:
        logger.error(f"Erro na busca por similaridade: {e}")
        return jsonify({"erro": str(e)}), 500

@qdrant_api_bp.route('/areas', methods=['GET'])
def listar_areas():
    """Lista áreas jurídicas disponíveis"""
    areas = [
        'direito_penal_integrado', 'direito_civil', 'direito_agrario',
        'direito_ambiental', 'direito_tributario', 'direito_constitucional',
        'direito_administrativo', 'direito_familia', 'direito_sucessorio',
        'direito_empresarial', 'direito_trabalhista', 'direito_previdenciario',
        'direito_consumidor', 'direito_imobiliario', 'direito_digital',
        'seguros', 'conflitos_mediacao', 'analise_riscos'
    ]
    
    return jsonify({
        "areas_disponiveis": areas,
        "total": len(areas),
        "tecnologia": "qdrant_vector_search"
    })

@qdrant_api_bp.route('/status', methods=['GET'])
def status_qdrant():
    """Status do sistema Qdrant"""
    try:
        from busca_qdrant_juridica import busca_qdrant
        
        # Testar uma busca simples
        resultado_teste = busca_qdrant.buscar_documentos_juridicos(
            'direito_civil', 'teste', limite=1
        )
        
        return jsonify({
            "status": "operacional",
            "qdrant_disponivel": True,
            "areas_configuradas": len(busca_qdrant.areas_juridicas),
            "teste_busca": "sucesso" if resultado_teste.get("status") == "sucesso" else "erro"
        })
        
    except Exception as e:
        return jsonify({
            "status": "erro",
            "qdrant_disponivel": False,
            "erro": str(e)
        }), 500

def registrar_api_qdrant(app):
    """Registra a API Qdrant na aplicação"""
    try:
        app.register_blueprint(qdrant_api_bp)
        logger.info("✅ API Qdrant registrada com sucesso")
        return True
    except Exception as e:
        logger.error(f"Erro ao registrar API Qdrant: {e}")
        return False
