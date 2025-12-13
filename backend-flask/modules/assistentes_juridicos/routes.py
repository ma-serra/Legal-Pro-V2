"""
Rotas dos Assistentes Jurídicos - Versão Corrigida
"""

from flask import Blueprint, request, jsonify
from .gerenciador_central import gerenciador_assistentes
import logging

logger = logging.getLogger(__name__)

assistentes_bp = Blueprint('assistentes_juridicos', __name__, url_prefix='/api/assistentes')

@assistentes_bp.route('/areas', methods=['GET'])
def listar_areas():
    """Lista todas as áreas jurídicas disponíveis"""
    try:
        areas = gerenciador_assistentes.listar_areas_disponiveis()
        return jsonify(areas)
    except Exception as e:
        logger.error(f"Erro ao listar áreas: {e}")
        return jsonify({"erro": str(e)}), 500

@assistentes_bp.route('/consultar', methods=['POST'])
def processar_consulta():
    """Processa consulta jurídica"""
    try:
        data = request.get_json()
        
        if not data or 'area' not in data or 'pergunta' not in data:
            return jsonify({"erro": "Dados inválidos"}), 400
        
        resultado = gerenciador_assistentes.processar_consulta(
            area=data['area'],
            pergunta=data['pergunta'],
            contexto=data.get('contexto', ''),
            modelo=data.get('modelo', 'gpt-4o')  # Captura modelo específico do frontend
        )
        
        return jsonify(resultado)
        
    except Exception as e:
        logger.error(f"Erro no processamento: {e}")
        return jsonify({"erro": str(e)}), 500

@assistentes_bp.route('/status', methods=['GET'])
def status_sistema():
    """Status do sistema de assistentes"""
    try:
        stats = gerenciador_assistentes.obter_estatisticas_sistema()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        return jsonify({"erro": str(e)}), 500

@assistentes_bp.route('/preferencias', methods=['GET'])
def obter_preferencias():
    """Obtém preferências de IA do usuário"""
    try:
        from flask_login import current_user
        from models import UserAIPreferences
        from main import db
        
        if not current_user.is_authenticated:
            # Retornar padrão para usuários não autenticados
            return jsonify({
                "provider": "openai",
                "modelo": "gpt-5",
                "personalidade": "advogado",
                "tom": "sistematico",
                "estilo": "juridico_tecnico"
            })
        
        area = request.args.get('area')  # None para preferência global
        
        # Buscar preferência específica da área ou global
        pref = UserAIPreferences.query.filter_by(
            user_id=current_user.id,
            area_juridica=area
        ).first()
        
        if not pref:
            # Buscar preferência global se não encontrou específica da área
            pref = UserAIPreferences.query.filter_by(
                user_id=current_user.id,
                area_juridica=None
            ).first()
        
        if pref:
            return jsonify({
                "provider": pref.provider,
                "modelo": pref.modelo,
                "personalidade": pref.personalidade or "advogado",
                "tom": pref.tom or "sistematico",
                "estilo": pref.estilo or "juridico_tecnico"
            })
        else:
            # Padrão GPT-5
            return jsonify({
                "provider": "openai",
                "modelo": "gpt-5",
                "personalidade": "advogado",
                "tom": "sistematico",
                "estilo": "juridico_tecnico"
            })
            
    except Exception as e:
        logger.error(f"Erro ao obter preferências: {e}")
        return jsonify({"erro": str(e)}), 500

@assistentes_bp.route('/preferencias', methods=['POST'])
def salvar_preferencias():
    """Salva preferências de IA do usuário"""
    try:
        from flask_login import current_user
        from models import UserAIPreferences
        from main import db
        
        if not current_user.is_authenticated:
            return jsonify({"erro": "Usuário não autenticado"}), 401
        
        data = request.get_json()
        area = data.get('area')  # None para preferência global
        
        # Buscar ou criar preferência
        pref = UserAIPreferences.query.filter_by(
            user_id=current_user.id,
            area_juridica=area
        ).first()
        
        if not pref:
            pref = UserAIPreferences(
                user_id=current_user.id,
                area_juridica=area
            )
            db.session.add(pref)
        
        # Atualizar valores
        if 'provider' in data:
            pref.provider = data['provider']
        if 'modelo' in data:
            pref.modelo = data['modelo']
        if 'personalidade' in data:
            pref.personalidade = data['personalidade']
        if 'tom' in data:
            pref.tom = data['tom']
        if 'estilo' in data:
            pref.estilo = data['estilo']
        
        db.session.commit()
        
        logger.info(f"✅ Preferências salvas: {current_user.username} - {pref.modelo}")
        
        return jsonify({
            "sucesso": True,
            "mensagem": "Preferências salvas com sucesso",
            "preferencias": {
                "provider": pref.provider,
                "modelo": pref.modelo,
                "personalidade": pref.personalidade,
                "tom": pref.tom,
                "estilo": pref.estilo
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao salvar preferências: {e}")
        db.session.rollback()
        return jsonify({"erro": str(e)}), 500

def registrar_rotas_assistentes(app):
    """Registra as rotas dos assistentes na aplicação"""
    try:
        app.register_blueprint(assistentes_bp)
        
        # Inicializar gerenciador com contexto da app
        gerenciador_assistentes.init_app(app)
        
        logger.info("✅ Rotas dos assistentes registradas")
        return True
    except Exception as e:
        logger.error(f"Erro ao registrar rotas: {e}")
        return False
