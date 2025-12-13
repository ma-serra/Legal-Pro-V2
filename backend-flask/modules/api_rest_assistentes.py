"""
API REST para Assistentes Jurídicos - Chat com agentes especializados
"""
from flask import Blueprint, jsonify, request
from sqlalchemy import desc
from main import db
from models import AgenteJuridico, CategoriaJuridica, AvaliacaoAgente, User
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

assistentes_api = Blueprint('assistentes_api', __name__, url_prefix='/api/assistentes')

@assistentes_api.route('', methods=['GET'])
def listar_assistentes():
    """
    Lista todos os assistentes jurídicos ativos
    Query params: categoria_id, nivel_especializacao
    """
    try:
        # Filtros opcionais
        categoria_id = request.args.get('categoria_id', type=int)
        nivel_especializacao = request.args.get('nivel_especializacao', type=int)
        
        # Query base
        query = AgenteJuridico.query.filter_by(ativo=True)
        
        # Aplicar filtros
        if categoria_id:
            query = query.filter_by(categoria_id=categoria_id)
        if nivel_especializacao:
            query = query.filter_by(nivel_especializacao=nivel_especializacao)
        
        # Ordenar por nome
        query = query.order_by(AgenteJuridico.nome)
        
        # Buscar assistentes
        assistentes = query.all()
        
        # Serializar
        result = []
        for ass in assistentes:
            categoria_nome = ass.categoria.nome if ass.categoria else 'Geral'
            result.append({
                'id': ass.id,
                'nome': ass.nome,
                'descricao': ass.descricao,
                'categoria': categoria_nome,
                'categoria_id': ass.categoria_id,
                'nivel_especializacao': ass.nivel_especializacao,
                'icone': ass.icone,
                'cor_destaque': ass.cor_destaque,
                'rating_medio': ass.rating_medio,
                'total_avaliacoes': ass.total_avaliacoes,
                'capacidades': ass.capacidades or []
            })
        
        return jsonify({'assistentes': result}), 200
        
    except Exception as e:
        logger.error(f"Erro ao listar assistentes: {e}")
        return jsonify({'error': 'Erro ao listar assistentes'}), 500

@assistentes_api.route('/<int:assistente_id>', methods=['GET'])
def obter_assistente(assistente_id):
    """
    Retorna detalhes de um assistente específico
    """
    try:
        assistente = AgenteJuridico.query.filter_by(id=assistente_id, ativo=True).first_or_404()
        
        categoria_nome = assistente.categoria.nome if assistente.categoria else 'Geral'
        detalhes_tecnicos = assistente.get_detalhes_tecnicos()
        
        return jsonify({
            'id': assistente.id,
            'nome': assistente.nome,
            'classe': assistente.classe,
            'descricao': assistente.descricao,
            'categoria': categoria_nome,
            'categoria_id': assistente.categoria_id,
            'nivel_especializacao': assistente.nivel_especializacao,
            'icone': assistente.icone,
            'cor_destaque': assistente.cor_destaque,
            'modelo_ai': assistente.modelo_ai,
            'temperatura': assistente.temperatura,
            'max_tokens': assistente.max_tokens,
            'capacidades': assistente.capacidades or [],
            'rating_medio': assistente.rating_medio,
            'total_avaliacoes': assistente.total_avaliacoes,
            'base_vetorial_ativa': assistente.base_vetorial_ativa,
            'template_prompt': assistente.template_prompt,
            'detalhes_tecnicos': detalhes_tecnicos
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter assistente {assistente_id}: {e}")
        return jsonify({'error': 'Assistente não encontrado'}), 404

@assistentes_api.route('/<int:assistente_id>/chat', methods=['POST'])
def chat_assistente(assistente_id):
    """
    Envia uma mensagem para o assistente e recebe resposta
    Body: { "mensagem": "texto", "contexto": "opcional" }
    """
    try:
        assistente = AgenteJuridico.query.filter_by(id=assistente_id, ativo=True).first_or_404()
        data = request.get_json()
        
        if not data or not data.get('mensagem'):
            return jsonify({'error': 'Mensagem é obrigatória'}), 400
        
        mensagem = data['mensagem']
        contexto = data.get('contexto', '')
        
        # Integrar com IA REAL usando multi_api_handler
        try:
            from modules.multi_api_handler import multi_api
            
            # Buscar configurações do assistente
            detalhes = assistente.get_detalhes_tecnicos()
            provider = detalhes.get('provider', 'openai')
            modelo = assistente.modelo_ai or detalhes.get('default_model', 'gpt-4o')
            temperatura = assistente.temperatura or 0.7
            max_tokens = assistente.max_tokens or 2000
            
            # Construir contexto do sistema
            context_system = f"""Você é {assistente.nome}, um assistente jurídico especializado em {assistente.categoria.nome if assistente.categoria else 'Direito'}.

Descrição: {assistente.descricao or 'Assistente jurídico especializado'}

Suas capacidades: {', '.join(assistente.capacidades[:3]) if assistente.capacidades else 'análise jurídica completa'}

Responda de forma profissional, técnica e precisa. Use referências legais quando apropriado."""

            if contexto:
                context_system += f"\n\nContexto adicional: {contexto}"
            
            # Chamar IA
            resultado = multi_api.generate_response(
                prompt=mensagem,
                provider=provider,
                model=modelo,
                max_tokens=max_tokens,
                temperature=temperatura,
                context=context_system
            )
            
            if resultado['success']:
                resposta_final = {
                    'assistente_id': assistente.id,
                    'assistente_nome': assistente.nome,
                    'mensagem_usuario': mensagem,
                    'resposta': resultado['response'],
                    'timestamp': resultado['timestamp'],
                    'modelo_utilizado': f"{resultado['provider']} - {resultado['model']}",
                    'tokens_usados': resultado['tokens_used'],
                    'tempo_resposta': resultado['response_time'],
                    'provider': resultado['provider']
                }
            else:
                # Fallback para mock se IA falhar
                resposta_final = {
                    'assistente_id': assistente.id,
                    'assistente_nome': assistente.nome,
                    'mensagem_usuario': mensagem,
                    'resposta': f"Desculpe, estou com dificuldades técnicas no momento. Erro: {resultado.get('error', 'Desconhecido')}",
                    'timestamp': datetime.now().isoformat(),
                    'modelo_utilizado': 'fallback',
                    'tokens_usados': 0,
                    'erro': resultado.get('error')
                }
        
        except Exception as e:
            logger.error(f"Erro ao processar com IA: {e}")
            # Fallback completo
            resposta_final = {
                'assistente_id': assistente.id,
                'assistente_nome': assistente.nome,
                'mensagem_usuario': mensagem,
                'resposta': f"Sou o assistente {assistente.nome}. No momento estou em modo de manutenção. Por favor, tente novamente em alguns instantes.",
                'timestamp': datetime.now().isoformat(),
                'modelo_utilizado': 'fallback',
                'tokens_usados': 0,
                'erro_tecnico': str(e)
            }
        
        return jsonify(resposta_final), 200
        
    except Exception as e:
        logger.error(f"Erro ao processar chat com assistente {assistente_id}: {e}")
        return jsonify({'error': 'Erro ao processar mensagem'}), 500

@assistentes_api.route('/<int:assistente_id>/avaliar', methods=['POST'])
def avaliar_assistente(assistente_id):
    """
    Avalia um assistente
    Body: { "rating": 1-5, "comentario": "opcional" }
    """
    try:
        assistente = AgenteJuridico.query.filter_by(id=assistente_id, ativo=True).first_or_404()
        data = request.get_json()
        
        if not data or 'rating' not in data:
            return jsonify({'error': 'Rating é obrigatório'}), 400
        
        rating = data['rating']
        if rating < 1 or rating > 5:
            return jsonify({'error': 'Rating deve ser entre 1 e 5'}), 400
        
        # TODO: Associar com usuário autenticado
        # Por enquanto, criar avaliação sem usuário
        avaliacao = AvaliacaoAgente(
            agente_id=assistente_id,
            usuario_id=1,  # TODO: Usar usuário autenticado
            rating=rating,
            comentario=data.get('comentario', ''),
            data_avaliacao=datetime.now()
        )
        
        db.session.add(avaliacao)
        db.session.commit()
        
        return jsonify({
            'message': 'Avaliação registrada com sucesso',
            'rating': rating,
            'rating_medio_atual': assistente.rating_medio
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao avaliar assistente {assistente_id}: {e}")
        return jsonify({'error': 'Erro ao registrar avaliação'}), 500

@assistentes_api.route('/categorias', methods=['GET'])
def listar_categorias():
    """
    Lista todas as categorias jurídicas disponíveis
    """
    try:
        categorias = CategoriaJuridica.query.filter_by(ativa=True).order_by(CategoriaJuridica.nome).all()
        
        result = [{
            'id': cat.id,
            'nome': cat.nome,
            'descricao': cat.descricao,
            'icone': cat.icone,
            'cor': cat.cor
        } for cat in categorias]
        
        return jsonify({'categorias': result}), 200
        
    except Exception as e:
        logger.error(f"Erro ao listar categorias: {e}")
        return jsonify({'error': 'Erro ao listar categorias'}), 500

def register_assistentes_api(app):
    """Registra o blueprint de assistentes no app"""
    app.register_blueprint(assistentes_api)
    print("✅ API REST de Assistentes registrada")
    logger.info("✅ API REST de Assistentes registrada com sucesso")
