"""
API de Chat Jurídico - Sistema integrado com múltiplos provedores
Endpoints para chat jurídico especializado com suporte a Anthropic, OpenAI e Google
"""
import os
import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
import requests

# Configurar logging
logger = logging.getLogger(__name__)

# Blueprint
chat_juridico = Blueprint('chat_juridico', __name__, url_prefix='/api/chat-juridico')

# Configurações de APIs
API_CONFIGS = {
    "anthropic": {
        "api_key": os.environ.get("ANTHROPIC_API_KEY"),
        "base_url": "https://api.anthropic.com",
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 4000
    },
    "openai": {
        "api_key": os.environ.get("OPENAI_API_KEY"),
        "base_url": "https://api.openai.com",
        "model": "gpt-4",
        "max_tokens": 4000
    },
    "google": {
        "api_key": os.environ.get("GOOGLE_API_KEY"),
        "base_url": "https://generativelanguage.googleapis.com",
        "model": "gemini-pro",
        "max_tokens": 4000
    }
}

class ChatJuridicoService:
    """Serviço principal para chat jurídico"""
    
    def __init__(self, provider="anthropic"):
        self.provider = provider
        self.config = API_CONFIGS.get(provider, API_CONFIGS["anthropic"])
        self.api_key = self.config["api_key"]
        
    def get_legal_context_prompt(self):
        """Obter prompt de contexto jurídico brasileiro"""
        return """Você é um assistente jurídico especializado em Direito Brasileiro.
        
INSTRUÇÕES:
- Forneça respostas precisas e fundamentadas na legislação brasileira
- Cite artigos de lei relevantes quando aplicável
- Use linguagem técnica mas acessível
- Sempre indique quando uma resposta requer análise mais detalhada
- Mantenha-se atualizado com jurisprudência dos tribunais superiores

ÁREAS DE ESPECIALIZAÇÃO:
- Direito Civil e Processual Civil
- Direito Penal e Processual Penal
- Direito Trabalhista
- Direito Constitucional
- Direito Administrativo
- Direito Tributário
- Direito do Consumidor
- Direito Empresarial

Responda de forma profissional e educativa."""
    
    def chat_with_anthropic(self, messages, context=""):
        """Chat usando Anthropic Claude"""
        try:
            if not self.config["api_key"]:
                raise Exception("API Key da Anthropic não configurada")
            
            # Preparar mensagens para Anthropic
            formatted_messages = []
            system_message = self.get_legal_context_prompt()
            if context:
                system_message += f"\n\nCONTEXTO ADICIONAL:\n{context}"
            
            for msg in messages:
                role = "user" if msg.get("role") == "user" else "assistant"
                formatted_messages.append({
                    "role": role,
                    "content": msg.get("content", "")
                })
            
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.config["api_key"],
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": self.config["model"],
                "max_tokens": self.config["max_tokens"],
                "system": system_message,
                "messages": formatted_messages
            }
            
            response = requests.post(
                f"{self.config['base_url']}/v1/messages",
                headers=headers,
                json=data,
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "response": result.get("content", [{}])[0].get("text", ""),
                "provider": "anthropic",
                "model": self.config["model"],
                "usage": result.get("usage", {})
            }
            
        except Exception as e:
            logger.error(f"Erro no chat Anthropic: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def chat_with_openai(self, messages, context=""):
        """Chat usando OpenAI GPT"""
        try:
            if not self.config["api_key"]:
                raise Exception("API Key da OpenAI não configurada")
            
            # Preparar mensagens para OpenAI
            formatted_messages = [
                {"role": "system", "content": self.get_legal_context_prompt() + (f"\n\n{context}" if context else "")}
            ]
            
            for msg in messages:
                formatted_messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config['api_key']}"
            }
            
            data = {
                "model": self.config["model"],
                "messages": formatted_messages,
                "max_tokens": self.config["max_tokens"],
                "temperature": 0.1
            }
            
            response = requests.post(
                f"{self.config['base_url']}/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "response": result.get("choices", [{}])[0].get("message", {}).get("content", ""),
                "provider": "openai",
                "model": self.config["model"],
                "usage": result.get("usage", {})
            }
            
        except Exception as e:
            logger.error(f"Erro no chat OpenAI: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def chat_with_google(self, messages, context=""):
        """Chat usando Google Gemini"""
        try:
            if not self.config["api_key"]:
                raise Exception("API Key do Google não configurada")
            
            # Preparar prompt para Google
            prompt = self.get_legal_context_prompt()
            if context:
                prompt += f"\n\nCONTEXTO: {context}"
            
            # Adicionar mensagens ao prompt
            for msg in messages:
                role = "Usuário" if msg.get("role") == "user" else "Assistente"
                prompt += f"\n\n{role}: {msg.get('content', '')}"
            
            prompt += "\n\nAssistente:"
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "maxOutputTokens": self.config["max_tokens"],
                    "temperature": 0.1
                }
            }
            
            response = requests.post(
                f"{self.config['base_url']}/v1beta/models/{self.config['model']}:generateContent?key={self.config['api_key']}",
                json=data,
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            candidates = result.get("candidates", [])
            if candidates:
                response_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            else:
                response_text = "Não foi possível gerar resposta"
            
            return {
                "success": True,
                "response": response_text,
                "provider": "google",
                "model": self.config["model"],
                "usage": result.get("usageMetadata", {})
            }
            
        except Exception as e:
            logger.error(f"Erro no chat Google: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def send_message(self, messages, context=""):
        """Enviar mensagem usando o provedor configurado"""
        if self.provider == "anthropic":
            return self.chat_with_anthropic(messages, context)
        elif self.provider == "openai":
            return self.chat_with_openai(messages, context)
        elif self.provider == "google":
            return self.chat_with_google(messages, context)
        else:
            return {"success": False, "error": "Provedor não suportado"}

def get_chat_history(user_id, limit=50):
    """Obter histórico de chat do usuário"""
    try:
        from main import db
        from sqlalchemy import text
        
        query = text("""
            SELECT message, response, created_at, provider, model
            FROM chat_juridico_history 
            WHERE user_id = :user_id 
            ORDER BY created_at DESC 
            LIMIT :limit
        """)
        
        result = db.session.execute(query, {'user_id': user_id, 'limit': limit})
        
        history = []
        for row in result:
            history.append({
                'message': row[0],
                'response': row[1],
                'timestamp': row[2].isoformat() if row[2] else None,
                'provider': row[3],
                'model': row[4]
            })
        
        return history
        
    except Exception as e:
        logger.error(f"Erro ao obter histórico: {str(e)}")
        return []

def save_chat_message(user_id, message, response, provider, model):
    """Salvar mensagem do chat no histórico"""
    try:
        from main import db
        from sqlalchemy import text
        
        # Criar tabela se não existir
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS chat_juridico_history (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                message TEXT,
                response TEXT,
                provider VARCHAR(50),
                model VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Inserir mensagem
        insert_query = text("""
            INSERT INTO chat_juridico_history 
            (user_id, message, response, provider, model)
            VALUES (:user_id, :message, :response, :provider, :model)
        """)
        
        db.session.execute(insert_query, {
            'user_id': user_id,
            'message': message,
            'response': response,
            'provider': provider,
            'model': model
        })
        
        db.session.commit()
        logger.info("✅ Mensagem salva no histórico")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao salvar histórico: {str(e)}")
        return False

# ROTAS DA API

@chat_juridico.route('/send', methods=['POST'])
@login_required
def send_chat_message():
    """Enviar mensagem para o chat jurídico"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Dados não fornecidos'}), 400
        
        message = data.get('message', '').strip()
        provider = data.get('provider', 'anthropic')
        context = data.get('context', '')
        
        if not message:
            return jsonify({'success': False, 'error': 'Mensagem não pode estar vazia'}), 400
        
        # Obter histórico recente para contexto
        history = get_chat_history(current_user.id, limit=5)
        
        # Preparar mensagens incluindo histórico
        messages = []
        for item in reversed(history[-3:]):  # Últimas 3 mensagens para contexto
            messages.extend([
                {"role": "user", "content": item['message']},
                {"role": "assistant", "content": item['response']}
            ])
        
        # Adicionar mensagem atual
        messages.append({"role": "user", "content": message})
        
        # Enviar para o provedor de IA
        chat_service = ChatJuridicoService(provider)
        result = chat_service.send_message(messages, context)
        
        if result['success']:
            # Salvar no histórico
            save_chat_message(
                current_user.id,
                message,
                result['response'],
                provider,
                result.get('model', '')
            )
            
            return jsonify({
                'success': True,
                'response': result['response'],
                'provider': provider,
                'model': result.get('model', ''),
                'usage': result.get('usage', {})
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Erro desconhecido')
            }), 500
        
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@chat_juridico.route('/history')
@login_required
def get_user_history():
    """Obter histórico de chat do usuário"""
    try:
        limit = int(request.args.get('limit', 50))
        history = get_chat_history(current_user.id, limit)
        
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history)
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter histórico: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@chat_juridico.route('/clear-history', methods=['POST'])
@login_required
def clear_user_history():
    """Limpar histórico de chat do usuário"""
    try:
        from main import db
        from sqlalchemy import text
        
        delete_query = text("""
            DELETE FROM chat_juridico_history 
            WHERE user_id = :user_id
        """)
        
        result = db.session.execute(delete_query, {'user_id': current_user.id})
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{result.rowcount} mensagens removidas do histórico'
        })
        
    except Exception as e:
        logger.error(f"Erro ao limpar histórico: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@chat_juridico.route('/providers')
def get_available_providers():
    """Obter provedores de IA disponíveis"""
    try:
        providers = []
        for provider, config in API_CONFIGS.items():
            providers.append({
                'name': provider,
                'model': config['model'],
                'available': bool(config['api_key']),
                'max_tokens': config['max_tokens']
            })
        
        return jsonify({
            'success': True,
            'providers': providers
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter provedores: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Função para registrar o blueprint
def register_chat_juridico_routes(app):
    """Registrar rotas do chat jurídico"""
    try:
        app.register_blueprint(chat_juridico)
        logger.info("✅ API do Chat Jurídico registrada com sucesso")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao registrar Chat Jurídico: {str(e)}")
        return False