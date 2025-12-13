"""
API para Validação Multi-Agente Expandida
Sistema de salvamento e recuperação de análises com identificadores únicos
"""

import os
import json
import hashlib
import uuid
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_login import current_user, login_required
from sqlalchemy import text
# Imports movidos para dentro das funções para evitar circular import

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint para API de validação multi-agente
validacao_multi_agente_api = Blueprint('validacao_multi_agente_api', __name__)

@validacao_multi_agente_api.route('/api/validacao-multi-agente/salvar', methods=['POST'])
@login_required
def salvar_analise():
    """
    Salva uma análise de validação multi-agente com identificadores únicos
    """
    try:
        # Imports locais para evitar circular import
        from models import db, User, ValidacaoMultiAgenteAnalise
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados não fornecidos'
            }), 400
        
        # Validação de campos obrigatórios
        campos_obrigatorios = [
            'documento_original',
            'total_agentes_utilizados', 
            'areas_juridicas_envolvidas',
            'resultados_agentes'
        ]
        
        for campo in campos_obrigatorios:
            if campo not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório ausente: {campo}'
                }), 400
        
        # Criar nova análise
        analise = ValidacaoMultiAgenteAnalise()
        
        # Dados básicos
        analise.titulo_analise = data.get('titulo_analise', 'Análise Multi-Agente')
        analise.descricao = data.get('descricao', '')
        analise.user_id = current_user.id
        
        # Dados do documento
        analise.documento_original = data['documento_original']
        analise.documento_nome = data.get('documento_nome', 'documento.txt')
        analise.documento_tipo = data.get('documento_tipo', 'text/plain')
        analise.documento_tamanho = len(data['documento_original'])
        
        # Configurações da análise
        analise.total_agentes_utilizados = data['total_agentes_utilizados']
        analise.areas_juridicas_envolvidas = data['areas_juridicas_envolvidas']
        analise.configuracao_analise = data.get('configuracao_analise', {})
        
        # Resultados
        analise.resultados_agentes = data['resultados_agentes']
        analise.opiniao_consolidada = data.get('opiniao_consolidada', '')
        analise.pontos_criticos = data.get('pontos_criticos', [])
        analise.recomendacoes_prioritarias = data.get('recomendacoes_prioritarias', [])
        analise.recomendacoes_importantes = data.get('recomendacoes_importantes', [])
        analise.recomendacoes_sugeridas = data.get('recomendacoes_sugeridas', [])
        
        # Metadados de execução
        analise.tempo_processamento_segundos = data.get('tempo_processamento_segundos', 0.0)
        analise.modelos_ia_utilizados = data.get('modelos_ia_utilizados', [])
        analise.tokens_consumidos = data.get('tokens_consumidos', 0)
        analise.custo_estimado = data.get('custo_estimado', 0.0)
        
        # Status
        analise.status = data.get('status', 'concluida')
        analise.status_mensagem = data.get('status_mensagem', '')
        analise.fallback_mode = data.get('fallback_mode', False)
        analise.debug_mode = data.get('debug_mode', False)
        
        # Gerar identificadores únicos
        analise.gerar_identificadores_unicos(data['documento_original'])
        
        # Verificar se já existe uma análise com o mesmo hash
        analise_existente = ValidacaoMultiAgenteAnalise.obter_por_hash(analise.hash_sha256)
        if analise_existente:
            logger.info(f"Análise com hash duplicado encontrada: {analise_existente.numero_registro}")
            
            # Verificar se pertence ao mesmo usuário
            if analise_existente.user_id == current_user.id:
                return jsonify({
                    'success': True,
                    'message': 'Esta análise já foi salva anteriormente',
                    'data': {
                        'id': analise_existente.id,
                        'uuid_analise': analise_existente.uuid_analise,
                        'hash_sha256': analise_existente.hash_sha256,
                        'numero_registro': analise_existente.numero_registro,
                        'data_criacao': analise_existente.data_criacao.isoformat(),
                        'ja_existia': True
                    }
                })
            else:
                # Se pertence a outro usuário, gerar novos identificadores com salt adicional
                import random
                salt = str(random.randint(1000, 9999))
                hash_content = f"{data['documento_original']}_{datetime.now().timestamp() * 1000}_{analise.uuid_analise}_{salt}"
                import hashlib
                analise.hash_sha256 = hashlib.sha256(hash_content.encode('utf-8')).hexdigest()
        
        # Timestamps
        analise.data_criacao = datetime.now()
        analise.data_atualizacao = datetime.now()
        if analise.status == 'concluida':
            analise.data_conclusao = datetime.now()
        
        # Salvar no banco
        db.session.add(analise)
        db.session.commit()
        
        logger.info(f"Análise salva com sucesso: {analise.numero_registro}")
        
        return jsonify({
            'success': True,
            'message': 'Análise salva com sucesso',
            'data': {
                'id': analise.id,
                'uuid_analise': analise.uuid_analise,
                'hash_sha256': analise.hash_sha256,
                'numero_registro': analise.numero_registro,
                'data_criacao': analise.data_criacao.isoformat()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao salvar análise: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@validacao_multi_agente_api.route('/api/validacao-multi-agente/buscar/<identificador>', methods=['GET'])
@login_required
def buscar_analise(identificador):
    """
    Busca uma análise por qualquer um dos identificadores únicos
    """
    try:
        # Imports locais para evitar circular import
        from models import ValidacaoMultiAgenteAnalise
        
        analise = None
        
        # Tentar buscar por UUID
        if len(identificador) == 36 and '-' in identificador:
            analise = ValidacaoMultiAgenteAnalise.obter_por_uuid(identificador)
        
        # Tentar buscar por hash SHA-256
        elif len(identificador) == 64:
            analise = ValidacaoMultiAgenteAnalise.obter_por_hash(identificador)
        
        # Tentar buscar por número de registro
        elif identificador.startswith('REG-'):
            analise = ValidacaoMultiAgenteAnalise.obter_por_registro(identificador)
        
        # Tentar buscar por ID numérico
        elif identificador.isdigit():
            analise = ValidacaoMultiAgenteAnalise.query.get(int(identificador))
        
        if not analise:
            return jsonify({
                'success': False,
                'error': 'Análise não encontrada'
            }), 404
        
        # Verificar se o usuário tem acesso
        if analise.user_id != current_user.id and not current_user.is_admin:
            return jsonify({
                'success': False,
                'error': 'Acesso negado'
            }), 403
        
        return jsonify({
            'success': True,
            'data': analise.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar análise: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@validacao_multi_agente_api.route('/api/validacao-multi-agente/listar', methods=['GET'])
@login_required
def listar_analises():
    """
    Lista análises do usuário atual
    """
    try:
        # Imports locais para evitar circular import
        from models import ValidacaoMultiAgenteAnalise
        
        limite = request.args.get('limite', 20, type=int)
        user_id = current_user.id if not current_user.is_admin else request.args.get('user_id', current_user.id, type=int)
        
        analises = ValidacaoMultiAgenteAnalise.listar_por_usuario(user_id, limite)
        
        return jsonify({
            'success': True,
            'data': [analise.to_dict() for analise in analises],
            'total': len(analises)
        })
        
    except Exception as e:
        logger.error(f"Erro ao listar análises: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@validacao_multi_agente_api.route('/api/validacao-multi-agente/marcar-exportacao', methods=['POST'])
@login_required
def marcar_exportacao():
    """
    Marca que uma análise foi exportada em determinado formato
    """
    try:
        # Imports locais para evitar circular import
        from models import ValidacaoMultiAgenteAnalise
        
        data = request.get_json()
        
        if not data or 'identificador' not in data or 'formato' not in data:
            return jsonify({
                'success': False,
                'error': 'Identificador e formato são obrigatórios'
            }), 400
        
        identificador = data['identificador']
        formato = data['formato']
        
        # Buscar análise
        analise = None
        if len(identificador) == 36 and '-' in identificador:
            analise = ValidacaoMultiAgenteAnalise.obter_por_uuid(identificador)
        elif identificador.startswith('REG-'):
            analise = ValidacaoMultiAgenteAnalise.obter_por_registro(identificador)
        elif identificador.isdigit():
            analise = ValidacaoMultiAgenteAnalise.query.get(int(identificador))
        
        if not analise:
            return jsonify({
                'success': False,
                'error': 'Análise não encontrada'
            }), 404
        
        # Verificar acesso
        if analise.user_id != current_user.id and not current_user.is_admin:
            return jsonify({
                'success': False,
                'error': 'Acesso negado'
            }), 403
        
        # Marcar exportação
        analise.marcar_exportacao(formato)
        
        return jsonify({
            'success': True,
            'message': f'Exportação em {formato} marcada com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Erro ao marcar exportação: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@validacao_multi_agente_api.route('/api/validacao-multi-agente/estatisticas', methods=['GET'])
@login_required
def obter_estatisticas():
    """
    Obtém estatísticas das análises do usuário
    """
    try:
        # Imports locais para evitar circular import
        from models import db
        
        user_id = current_user.id
        
        # Contar análises por status
        stats_query = text("""
            SELECT 
                status,
                COUNT(*) as total,
                AVG(tempo_processamento_segundos) as tempo_medio,
                SUM(tokens_consumidos) as tokens_total,
                SUM(custo_estimado) as custo_total
            FROM validacao_multi_agente_analise 
            WHERE user_id = :user_id 
            GROUP BY status
        """)
        
        resultado = db.session.execute(stats_query, {'user_id': user_id})
        estatisticas = {}
        
        for row in resultado:
            estatisticas[row.status] = {
                'total': row.total,
                'tempo_medio': float(row.tempo_medio) if row.tempo_medio else 0.0,
                'tokens_total': row.tokens_total or 0,
                'custo_total': float(row.custo_total) if row.custo_total else 0.0
            }
        
        # Total geral
        total_geral = sum([stats['total'] for stats in estatisticas.values()])
        
        return jsonify({
            'success': True,
            'data': {
                'estatisticas_por_status': estatisticas,
                'total_geral': total_geral,
                'user_id': user_id
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@validacao_multi_agente_api.route('/api/validacao-multi-agente/health', methods=['GET'])
def health_check():
    """
    Verifica se a API está funcionando
    """
    try:
        # Imports locais para evitar circular import
        from models import db
        
        # Testar conexão com banco
        db.session.execute(text('SELECT 1'))
        
        return jsonify({
            'success': True,
            'message': 'API de Validação Multi-Agente operacional',
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy'
        })
        
    except Exception as e:
        logger.error(f"Health check falhou: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro na conexão: {str(e)}',
            'status': 'unhealthy'
        }), 500

# Função para integrar com a aplicação principal
def registrar_api_validacao_multi_agente(app):
    """
    Registra a API de validação multi-agente na aplicação Flask
    """
    app.register_blueprint(validacao_multi_agente_api)
    logger.info("API de Validação Multi-Agente registrada com sucesso")