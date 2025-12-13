"""
Endpoints de teste para verificar conectividade das APIs
"""
import os
import logging
from flask import Blueprint, request, jsonify
import requests

# Blueprint para testes de API
test_api_bp = Blueprint('test_api', __name__, url_prefix='/api/test')

@test_api_bp.route('/openai', methods=['POST'])
def test_openai():
    """Teste de conectividade da API OpenAI"""
    try:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            return jsonify({
                'status': 'error',
                'message': 'OPENAI_API_KEY não configurada',
                'provider': 'OpenAI'
            }), 500
        
        # Teste simples de conectividade
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        # Teste com o modelo mais recente
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=5
        )
        
        return jsonify({
            'status': 'success',
            'message': 'OpenAI API funcional',
            'provider': 'OpenAI',
            'model': 'gpt-4o',
            'test_response': response.choices[0].message.content
        })
        
    except Exception as e:
        logging.error(f"Erro ao testar OpenAI: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erro na API OpenAI: {str(e)}',
            'provider': 'OpenAI'
        }), 500

@test_api_bp.route('/anthropic', methods=['POST'])
def test_anthropic():
    """Teste de conectividade da API Anthropic"""
    try:
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            return jsonify({
                'status': 'error',
                'message': 'ANTHROPIC_API_KEY não configurada',
                'provider': 'Anthropic'
            }), 500
        
        # Teste com Claude
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=5,
            messages=[{"role": "user", "content": "Test"}]
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Anthropic API funcional',
            'provider': 'Anthropic',
            'model': 'claude-3-5-sonnet-20241022',
            'test_response': message.content[0].text
        })
        
    except Exception as e:
        logging.error(f"Erro ao testar Anthropic: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erro na API Anthropic: {str(e)}',
            'provider': 'Anthropic'
        }), 500

@test_api_bp.route('/google', methods=['POST'])
def test_google():
    """Teste de conectividade da API Google Gemini"""
    try:
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return jsonify({
                'status': 'error',
                'message': 'GEMINI_API_KEY não configurada',
                'provider': 'Google'
            }), 500
        
        # Teste com Gemini
        try:
            from google import genai
            from google.genai import types
        except ImportError:
            # Fallback para google-generativeai se google-genai não estiver disponível
            import google.generativeai as genai
        
        try:
            # Novo SDK google-genai
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents="Test"
            )
            response_text = response.text
        except:
            # Fallback para google-generativeai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Test")
            response_text = response.text
        
        return jsonify({
            'status': 'success',
            'message': 'Google Gemini API funcional',
            'provider': 'Google',
            'model': 'gemini-1.5-flash',
            'test_response': response_text
        })
        
    except Exception as e:
        logging.error(f"Erro ao testar Google: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erro na API Google: {str(e)}',
            'provider': 'Google'
        }), 500

@test_api_bp.route('/deepseek', methods=['POST'])
def test_deepseek():
    """Teste de conectividade da API DeepSeek"""
    try:
        api_key = os.environ.get('DEEPSEEK_API_KEY')
        if not api_key:
            return jsonify({
                'status': 'error',
                'message': 'DEEPSEEK_API_KEY não configurada',
                'provider': 'DeepSeek'
            }), 500
        
        # Teste com DeepSeek
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'deepseek-chat',
            'messages': [{'role': 'user', 'content': 'Test'}],
            'max_tokens': 5
        }
        
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'status': 'success',
                'message': 'DeepSeek API funcional',
                'provider': 'DeepSeek',
                'model': 'deepseek-chat',
                'test_response': result.get('choices', [{}])[0].get('message', {}).get('content', 'Test OK')
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'DeepSeek API retornou status {response.status_code}',
                'provider': 'DeepSeek'
            }), 500
        
    except Exception as e:
        logging.error(f"Erro ao testar DeepSeek: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erro na API DeepSeek: {str(e)}',
            'provider': 'DeepSeek'
        }), 500

@test_api_bp.route('/all', methods=['GET'])
def test_all_apis():
    """Teste de todas as APIs disponíveis"""
    results = {}
    
    # Lista de APIs para testar
    apis = ['openai', 'anthropic', 'google', 'deepseek']
    
    for api in apis:
        try:
            # Testar cada API individualmente
            if api == 'openai':
                response_data, status_code = test_openai()
            elif api == 'anthropic':
                response_data, status_code = test_anthropic()
            elif api == 'google':
                response_data, status_code = test_google()
            elif api == 'deepseek':
                response_data, status_code = test_deepseek()
            else:
                response_data, status_code = ({'status': 'error', 'message': 'API desconhecida'}, 400)
            
            # Extrair dados da resposta
            if hasattr(response_data, 'get_json'):
                results[api] = response_data.get_json()
            elif isinstance(response_data, dict):
                results[api] = response_data
            else:
                results[api] = {'status': 'error', 'message': 'Formato de resposta inválido'}
                
        except Exception as e:
            results[api] = {
                'status': 'error',
                'message': f'Erro ao testar {api}: {str(e)}',
                'provider': api.title()
            }
    
    # Contar APIs funcionais
    functional_apis = sum(1 for result in results.values() if result.get('status') == 'success')
    total_apis = len(apis)
    
    return jsonify({
        'summary': {
            'total_apis': total_apis,
            'functional_apis': functional_apis,
            'success_rate': f"{(functional_apis/total_apis)*100:.1f}%"
        },
        'results': results
    })

def register_test_endpoints(app):
    """Registra os endpoints de teste na aplicação"""
    app.register_blueprint(test_api_bp)
    logging.info("✅ Endpoints de teste de API registrados")