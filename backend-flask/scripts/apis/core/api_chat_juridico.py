"""
API completa para chat jurídico com upload de arquivos e múltiplos provedores de IA
Utiliza o assistente jurídico universal para processamento robusto
"""

import os
import json
import logging
from flask import Blueprint, request, jsonify
from modules.assistente_juridico_universal import assistente_universal
from modules.multi_api_handler import multi_api
from config.api_providers import api_manager

logger = logging.getLogger(__name__)

# Blueprint para a API
api_chat = Blueprint('api_chat', __name__, url_prefix='/api/chat')

# Configurações
UPLOAD_FOLDER = 'uploads/chat_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@api_chat.route('/juridico', methods=['POST'])
def chat_juridico():
    """Endpoint principal do chat jurídico com múltiplos provedores de IA"""
    try:
        # Extrair dados da requisição
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados não fornecidos'
            }), 400
        
        # Extrair parâmetros
        query = data.get('query', '')
        provider = data.get('provider')  # openai, anthropic, deepseek, gemini
        area_juridica = data.get('area_juridica', 'geral')
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Consulta não fornecida'
            }), 400
        
        # Contexto jurídico específico
        context = f"""Você é um assistente jurídico especializado em {area_juridica}.
        Forneça respostas precisas, fundamentadas e práticas.
        Cite artigos de lei relevantes quando apropriado.
        Mantenha um tom profissional e acessível."""
        
        # Processar com multi-API
        resultado = multi_api.generate_response(
            prompt=query,
            provider=provider,
            context=context,
            temperature=0.7,
            max_tokens=1500
        )
        
        if resultado['success']:
            return jsonify({
                'success': True,
                'response': resultado['response'],
                'provider': resultado['provider'],
                'model': resultado['model'],
                'tokens_used': resultado.get('tokens_used', 0),
                'response_time': resultado.get('response_time', 0),
                'timestamp': resultado['timestamp']
            })
        else:
            return jsonify({
                'success': False,
                'error': resultado['error'],
                'provider': resultado.get('provider')
            }), 500
            
    except Exception as e:
        logger.error(f"Erro no endpoint do chat jurídico: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'response': 'Erro interno do servidor'
        }), 500

@api_chat.route('/providers', methods=['GET'])
def get_providers():
    """Retorna lista de provedores disponíveis incluindo AssemblyAI"""
    try:
        # Incluir todos os provedores do sistema, incluindo AssemblyAI
        all_providers = {}
        
        # Provedores de chat/análise
        if hasattr(multi_api, 'get_available_providers'):
            available_providers = multi_api.get_available_providers()
            for provider in available_providers:
                config = api_manager.get_provider_config(provider)
                if config:
                    all_providers[provider] = {
                        'name': config['name'],
                        'models': config['models'],
                        'available': True,
                        'type': config.get('type', 'chat')
                    }
        
        # Adicionar AssemblyAI manualmente se configurada
        assemblyai_config = api_manager.get_provider_config('assemblyai')
        if assemblyai_config and assemblyai_config['enabled']:
            all_providers['assemblyai'] = {
                'name': 'AssemblyAI',
                'models': ['speech-to-text', 'speaker-diarization', 'sentiment-analysis'],
                'available': True,
                'type': 'transcription'
            }
        
        return jsonify({
            'success': True,
            'providers': all_providers,
            'total_providers': len(all_providers)
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter provedores: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_chat.route('/analyze', methods=['POST'])
def analyze_text():
    """Análise de texto com múltiplos provedores"""
    try:
        data = request.get_json()
        if not data or not data.get('text'):
            return jsonify({
                'success': False,
                'error': 'Texto não fornecido'
            }), 400
        
        text = data.get('text')
        provider = data.get('provider')
        analysis_type = data.get('type', 'sentiment')
        
        if analysis_type == 'sentiment':
            result = multi_api.analyze_sentiment(text, provider)
        elif analysis_type == 'legal':
            result = multi_api.generate_response(
                prompt=f"Faça uma análise jurídica detalhada do seguinte texto: {text}",
                provider=provider,
                context="Você é um advogado especialista. Analise o texto sob perspectiva jurídica.",
                temperature=0.3
            )
        elif analysis_type == 'summary':
            result = multi_api.generate_response(
                prompt=f"Faça um resumo executivo do seguinte texto: {text}",
                provider=provider,
                context="Você é um especialista em resumos. Seja conciso e objetivo.",
                temperature=0.5
            )
        else:
            return jsonify({
                'success': False,
                'error': 'Tipo de análise não suportado'
            }), 400
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro na análise de texto: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_chat.route('/status', methods=['GET'])
def api_status():
    """Status detalhado de todas as APIs incluindo AssemblyAI"""
    try:
        from datetime import datetime
        
        # Status dos provedores de chat/análise
        status = multi_api.get_status()
        summary = api_manager.get_provider_summary()
        
        # Adicionar AssemblyAI ao status
        assemblyai_config = api_manager.get_provider_config('assemblyai')
        if assemblyai_config:
            status['providers']['assemblyai'] = {
                'name': assemblyai_config['name'],
                'enabled': assemblyai_config['enabled'],
                'available': assemblyai_config['enabled'],
                'default_model': assemblyai_config['default_model'],
                'type': assemblyai_config.get('type', 'transcription')
            }
            
            if assemblyai_config['enabled']:
                status['total_providers'] += 1
                status['available_providers'] += 1
        
        return jsonify({
            'success': True,
            'status': status,
            'summary': summary,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_chat.route('/tokens/usage', methods=['GET'])
def get_token_usage():
    """Retorna uso de tokens por API e componente"""
    try:
        from modules.token_tracker import token_tracker
        
        period = request.args.get('period', 'today')
        usage_summary = token_tracker.get_usage_summary(period)
        component_breakdown = token_tracker.get_component_breakdown()
        realtime_stats = token_tracker.get_realtime_stats()
        
        return jsonify({
            'success': True,
            'usage_summary': usage_summary,
            'component_breakdown': component_breakdown,
            'realtime_stats': realtime_stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Erro ao obter uso de tokens: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_chat.route('/tokens/track', methods=['POST'])
def track_token_usage():
    """Registra uso de tokens"""
    try:
        from modules.token_tracker import token_tracker
        
        data = request.get_json()
        required_fields = ['provider', 'component', 'tokens']
        
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'error': 'Campos obrigatórios: provider, component, tokens'
            }), 400
        
        token_tracker.track_usage(
            provider=data['provider'],
            component=data['component'],
            tokens=data['tokens'],
            cost=data.get('cost', 0.0),
            session_id=data.get('session_id'),
            user_id=data.get('user_id'),
            request_type=data.get('request_type'),
            model_used=data.get('model_used')
        )
        
        return jsonify({
            'success': True,
            'message': 'Uso de tokens registrado com sucesso'
        })
    except Exception as e:
        logger.error(f"Erro ao registrar tokens: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_chat.route('/pricing/calculate', methods=['POST'])
def calculate_pricing():
    """Calcula custos baseado nos preços oficiais dos provedores"""
    try:
        from modules.pricing_calculator import pricing_calculator
        
        data = request.get_json()
        service_type = data.get('type', 'text')
        
        if service_type == 'text':
            required_fields = ['provider', 'model', 'input_tokens']
            if not all(field in data for field in required_fields):
                return jsonify({
                    'success': False,
                    'error': 'Campos obrigatórios para texto: provider, model, input_tokens'
                }), 400
            
            result = pricing_calculator.calculate_text_cost(
                provider=data['provider'],
                model=data['model'],
                input_tokens=data['input_tokens'],
                output_tokens=data.get('output_tokens', 0)
            )
            
        elif service_type == 'audio':
            required_fields = ['provider', 'duration_minutes']
            if not all(field in data for field in required_fields):
                return jsonify({
                    'success': False,
                    'error': 'Campos obrigatórios para áudio: provider, duration_minutes'
                }), 400
            
            result = pricing_calculator.calculate_audio_cost(
                provider=data['provider'],
                duration_minutes=data['duration_minutes'],
                features=data.get('features', [])
            )
            
        else:
            return jsonify({
                'success': False,
                'error': 'Tipo de serviço não suportado. Use: text, audio'
            }), 400
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
        return jsonify({
            'success': True,
            'pricing': result
        })
        
    except Exception as e:
        logger.error(f"Erro ao calcular preços: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_chat.route('/pricing/compare', methods=['POST'])
def compare_pricing():
    """Compara custos entre todos os provedores"""
    try:
        from modules.pricing_calculator import pricing_calculator
        
        data = request.get_json()
        required_fields = ['input_tokens']
        
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'error': 'Campo obrigatório: input_tokens'
            }), 400
        
        result = pricing_calculator.compare_providers(
            input_tokens=data['input_tokens'],
            output_tokens=data.get('output_tokens', 0),
            service_type=data.get('service_type', 'text')
        )
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
        return jsonify({
            'success': True,
            'comparison': result
        })
        
    except Exception as e:
        logger.error(f"Erro na comparação de preços: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_chat.route('/pricing/components', methods=['GET'])
def estimate_component_costs():
    """Estima custos por componente do sistema"""
    try:
        from modules.pricing_calculator import pricing_calculator
        
        component = request.args.get('component')
        if not component:
            # Retornar estimativas para todos os componentes
            components = [
                'assistentes_juridicos',
                'agentes_multiagent', 
                'transcricao_audio',
                'transcricao_video',
                'analise_sentimento',
                'chat_juridico'
            ]
            
            estimates = {}
            for comp in components:
                result = pricing_calculator.estimate_component_cost(comp, {})
                if 'error' not in result:
                    estimates[comp] = result
            
            return jsonify({
                'success': True,
                'component_estimates': estimates
            })
        
        else:
            result = pricing_calculator.estimate_component_cost(component, {})
            
            if 'error' in result:
                return jsonify({
                    'success': False,
                    'error': result['error']
                }), 400
            
            return jsonify({
                'success': True,
                'estimate': result
            })
        
    except Exception as e:
        logger.error(f"Erro ao estimar custos de componentes: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_chat.route('/pricing/exchange-rate', methods=['GET'])
def get_exchange_rate():
    """Retorna taxa de câmbio USD/BRL atual"""
    try:
        from modules.pricing_calculator import pricing_calculator
        
        return jsonify({
            'success': True,
            'exchange_rate': {
                'usd_to_brl': pricing_calculator.usd_to_brl_rate,
                'updated_at': pricing_calculator.exchange_rate_updated.isoformat() if pricing_calculator.exchange_rate_updated else None,
                'source': 'exchangerate-api.com'
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter taxa de câmbio: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_chat.route('/health', methods=['GET'])
def health_check():
    """Health check da API"""
    return jsonify({
        'status': 'healthy',
        'service': 'Chat Jurídico API',
        'version': '2.0.0',
        'providers_active': len(multi_api.get_available_providers())
    })