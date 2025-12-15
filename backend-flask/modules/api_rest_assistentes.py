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
                'tipo': ass.tipo or 'juridico',  # NOVO
                'descricao': ass.descricao,
                'area_juridica': categoria_nome,  # Renomeado para consistência
                'categoria': categoria_nome,
                'categoria_id': ass.categoria_id,
                'nivel_especializacao': ass.nivel_especializacao,
                'icone': ass.icone,
                'cor_destaque': ass.cor_destaque,
                'rating_medio': ass.rating_medio,
                'total_avaliacoes': ass.total_avaliacoes,
                'total_conversas': ass.total_conversas or 0,  # NOVO
                'customizado': ass.customizado or False,  # NOVO
                'capacidades': ass.capacidades or [],
                'status': 'ativo' if ass.ativo else 'inativo',
                'created_at': ass.data_criacao.isoformat() if ass.data_criacao else None  # NOVO
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
        
        # Construir configuracoes_llm se nao existir
        configuracoes_llm = assistente.configuracoes_llm if assistente.configuracoes_llm else {
            'llm_provider': detalhes_tecnicos.get('provider', 'openai'),
            'llm_model': assistente.modelo_ai or 'gpt-4o',
            'temperatura': assistente.temperatura or 0.3,
            'parametros': {},
            'modo_debug': False,
            'sempre_executar': True,
            'timeout': 120,
            'max_tokens': assistente.max_tokens or 8000
        }
        
        return jsonify({
            'id': assistente.id,
            'nome': assistente.nome,
            'tipo': assistente.tipo or 'juridico',  # NOVO
            'classe': assistente.classe,
            'descricao': assistente.descricao,
            'area_juridica': categoria_nome,  # NOVO
            'categoria': categoria_nome,
            'categoria_id': assistente.categoria_id,
            'nivel_especializacao': assistente.nivel_especializacao,
            'icone': assistente.icone,
            'cor_destaque': assistente.cor_destaque,
            'prompt_template': assistente.prompt_template or assistente.template_prompt,  # NOVO - usar novo campo
            'configuracoes': configuracoes_llm,  # NOVO - exposicao completa
            'customizado': assistente.customizado or False,  # NOVO
            'total_conversas': assistente.total_conversas or 0,  # NOVO
            'capacidades': assistente.capacidades or [],
            'rating_medio': assistente.rating_medio,
            'total_avaliacoes': assistente.total_avaliacoes,
            'base_vetorial_ativa': assistente.base_vetorial_ativa,
            'created_at': assistente.data_criacao.isoformat() if assistente.data_criacao else None,  # NOVO
            'updated_at': assistente.data_atualizacao.isoformat() if assistente.data_atualizacao else None,  # NOVO
            # Campos legacy para compatibilidade
            'modelo_ai': assistente.modelo_ai,
            'temperatura': assistente.temperatura,
            'max_tokens': assistente.max_tokens,
            'template_prompt': assistente.template_prompt,  # Deprecated
            'detalhes_tecnicos': detalhes_tecnicos  # Deprecated
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
            
            # Buscar configurações LLM do assistente (NOVO - usar configuracoes_llm)
            config_llm = assistente.configuracoes_llm if assistente.configuracoes_llm else {}
            
            # Extrair provider e model das configuracoes_llm
            provider = config_llm.get('llm_provider', 'openai')
            modelo = config_llm.get('llm_model', 'gpt-4o')
            temperatura = config_llm.get('temperatura', 0.3)
            max_tokens = config_llm.get('max_tokens', 8000)
            
            # Usar prompt_template se disponível
            prompt_template = assistente.prompt_template or assistente.template_prompt
            
            # Construir contexto do sistema
            if prompt_template:
                # Se tem template, substituir placeholders básicos
                context_system = prompt_template.replace('{input}', mensagem)
                # Substituir outros placeholders comuns
                context_system = context_system.replace('{parametros.profundidade}', 'completa')
                context_system = context_system.replace('{parametros.perspectiva}', 'neutra')
                context_system = context_system.replace('{parametros.jurisdicao}', 'Brasil')
            else:
                # Fallback para contexto padrão
                context_system = f"""Você é {assistente.nome}, um assistente jurídico especializado em {assistente.categoria.nome if assistente.categoria else 'Direito'}.

Descrição: {assistente.descricao or 'Assistente jurídico especializado'}

Suas capacidades: {', '.join(assistente.capacidades[:3]) if assistente.capacidades else 'análise jurídica completa'}

Responda de forma profissional, técnica e precisa. Use referências legais quando apropriado."""

            if contexto:
                context_system += f"\n\nContexto adicional: {contexto}"
            
            logger.info(f"Chamando {provider}/{modelo} para assistente {assistente.nome}")
            
            # Chamar IA com configurações reais do assistente
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
                logger.error(f"Erro na API de IA: {resultado.get('error')}")
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
            logger.error(f"Erro ao processar com IA: {e}", exc_info=True)
            # Fallback completo
            resposta_final = {
                'assistente_id': assistente.id,
                'assistente_nome': assistente.nome,
                'mensagem_usuario': mensagem,
                'resposta': f"Sou o assistente {assistente.nome}. No momento estou em modo de manutenção. Erro técnico: {str(e)}",
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

@assistentes_api.route('', methods=['POST'])
def criar_assistente():
    """
    Cria um novo assistente customizado
    Body: { "nome": str, "tipo": str, "descricao": str, "prompt_template": str, "configuracoes": {} }
    """
    try:
        from flask_login import current_user, login_required
        
        # Verificar autenticacao (simplificado - ideal usar decorator)
        # if not current_user.is_authenticated:
        #     return jsonify({'error': 'Autenticacao requerida'}), 401
        
        data = request.get_json()
        
        # Validacoes
        if not data or not data.get('nome') or not data.get('tipo'):
            return jsonify({'error': 'Nome e tipo sao obrigatorios'}), 400
        
        # Buscar ou criar categoria padrao
        categoria_geral = CategoriaJuridica.query.filter_by(nome='Geral').first()
        if not categoria_geral:
            categoria_geral = CategoriaJuridica(nome='Geral', ativa=True)
            db.session.add(categoria_geral)
            db.session.flush()
        
        # Criar assistente
        assistente = AgenteJuridico(
            nome=data['nome'],
            classe=f"Assistente{data['tipo'].capitalize()}",
            tipo=data['tipo'],
            descricao=data.get('descricao', ''),
            prompt_template=data.get('prompt_template', ''),
            categoria_id=categoria_geral.id,
            configuracoes_llm=data.get('configuracoes', {}),
            customizado=True,
            ativo=True,
            icone=data.get('icone', 'fas fa-robot'),
            cor_destaque=data.get('cor_destaque', '#3B82F6'),
            # created_by=current_user.id if current_user.is_authenticated else None
        )
        
        db.session.add(assistente)
        db.session.commit()
        
        logger.info(f"Assistente customizado criado: {assistente.nome} (ID: {assistente.id})")
        
        return jsonify({
            'id': assistente.id,
            'nome': assistente.nome,
            'tipo': assistente.tipo,
            'mensagem': 'Assistente criado com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao criar assistente: {e}")
        return jsonify({'error': 'Erro ao criar assistente'}), 500

@assistentes_api.route('/<int:assistente_id>', methods=['PUT'])
def atualizar_assistente(assistente_id):
    """
    Atualiza um assistente customizado
    Body: { "nome": str, "descricao": str, "prompt_template": str, "configuracoes": {} }
    """
    try:
        assistente = AgenteJuridico.query.get_or_404(assistente_id)
        
        # Verificar se e customizado
        if not assistente.customizado:
            return jsonify({'error': 'Apenas assistentes customizados podem ser editados'}), 403
        
        data = request.get_json()
        
        # Atualizar campos permitidos
        if 'nome' in data:
            assistente.nome = data['nome']
        if 'descricao' in data:
            assistente.descricao = data['descricao']
        if 'prompt_template' in data:
            assistente.prompt_template = data['prompt_template']
        if 'configuracoes' in data:
            assistente.configuracoes_llm = data['configuracoes']
        if 'icone' in data:
            assistente.icone = data['icone']
        if 'cor_destaque' in data:
            assistente.cor_destaque = data['cor_destaque']
        
        db.session.commit()
        
        logger.info(f"Assistente atualizado: {assistente.nome} (ID: {assistente.id})")
        
        return jsonify({'mensagem': 'Assistente atualizado com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao atualizar assistente {assistente_id}: {e}")
        return jsonify({'error': 'Erro ao atualizar assistente'}), 500

@assistentes_api.route('/<int:assistente_id>/conversas', methods=['GET'])
def listar_conversas(assistente_id):
    """
    Lista conversas/historico de um assistente
    Por enquanto retorna vazio - implementar modelo Conversa depois
    """
    try:
        # Verificar se assistente existe
        assistente = AgenteJuridico.query.get_or_404(assistente_id)
        
        # TODO: Implementar modelo Conversa e query real
        # Por enquanto retornar array vazio
        conversas = []
        
        return jsonify({'conversas': conversas, 'total': len(conversas)}), 200
        
    except Exception as e:
        logger.error(f"Erro ao listar conversas do assistente {assistente_id}: {e}")
        return jsonify({'error': 'Erro ao listar conversas'}), 500

@assistentes_api.route('/<int:assistente_id>/conversas', methods=['POST'])
def criar_conversa(assistente_id):
    """
    Cria uma nova conversa
    """
    try:
        from models import Conversa
        assistente = AgenteJuridico.query.get_or_404(assistente_id)
        data = request.get_json()
        
        conversa = Conversa(
            assistente_id=assistente_id,
            titulo=data.get('titulo', f'Conversa com {assistente.nome}'),
            mensagens=[],
            provider_usado=data.get('provider'),
            modelo_usado=data.get('modelo'),
            arquivos_anexados=[]
        )
        db.session.add(conversa)
        db.session.commit()
        
        return jsonify({
            'id': conversa.id,
            'titulo': conversa.titulo,
            'mensagens': [],
            'provider_usado': conversa.provider_usado,
            'modelo_usado': conversa.modelo_usado
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao criar conversa: {e}")
        return jsonify({'error': 'Erro ao criar conversa'}), 500

@assistentes_api.route('/<int:assistente_id>/conversas/<int:conversa_id>', methods=['GET'])
def obter_conversa(assistente_id, conversa_id):
    """
    Obtém detalhes de uma conversa
    """
    try:
        from models import Conversa
        conversa = Conversa.query.filter_by(id=conversa_id, assistente_id=assistente_id, ativa=True).first_or_404()
        return jsonify({
            'id': conversa.id,
            'titulo': conversa.titulo,
            'mensagens': conversa.mensagens or [],
            'provider_usado': conversa.provider_usado,
            'modelo_usado': conversa.modelo_usado,
            'arquivos_anexados': conversa.arquivos_anexados or []
        }), 200
    except Exception as e:
        logger.error(f"Erro ao obter conversa: {e}")
        return jsonify({'error': 'Conversa não encontrada'}), 404

@assistentes_api.route('/<int:assistente_id>/conversas/<int:conversa_id>', methods=['PUT'])
def atualizar_conversa_endpoint(assistente_id, conversa_id):
    """
    Atualiza uma conversa
    """
    try:
        from models import Conversa
        from datetime import datetime
        
        conversa = Conversa.query.filter_by(id=conversa_id, assistente_id=assistente_id, ativa=True).first_or_404()
        data = request.get_json()
        
        if 'titulo' in data:
            conversa.titulo = data['titulo']
        if 'mensagens' in data:
            conversa.mensagens = data['mensagens']
        if 'provider' in data:
            conversa.provider_usado = data['provider']
        if 'modelo' in data:
            conversa.modelo_usado = data['modelo']
        
        conversa.data_atualizacao = datetime.now()
        db.session.commit()
        
        return jsonify({'mensagem': 'Conversa atualizada'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao atualizar conversa: {e}")
        return jsonify({'error': 'Erro ao atualizar'}), 500

@assistentes_api.route('/<int:assistente_id>/conversas/<int:conversa_id>', methods=['DELETE'])
def deletar_conversa(assistente_id, conversa_id):
    """
    Deleta uma conversa (soft delete)
    """
    try:
        from models import Conversa
        from datetime import datetime
        
        conversa = Conversa.query.filter_by(id=conversa_id, assistente_id=assistente_id, ativa=True).first_or_404()
        conversa.ativa = False
        conversa.data_atualizacao = datetime.now()
        db.session.commit()
        
        return jsonify({'mensagem': 'Conversa deletada'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao deletar conversa: {e}")
        return jsonify({'error': 'Erro ao deletar'}), 500

def register_assistentes_api(app):
    """Registra o blueprint de assistentes no app"""
    app.register_blueprint(assistentes_api)
    print("✅ API REST de Assistentes registrada")
    logger.info("✅ API REST de Assistentes registrada com sucesso")
