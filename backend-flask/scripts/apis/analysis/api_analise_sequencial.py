"""
API de análise sequencial com fila de processamento
Evita erros de API processando um agente por vez
"""
import time
import logging
import queue
import threading
from flask import Blueprint, request, jsonify
import os
from openai import OpenAI
import anthropic
from google import genai
from google.genai import types

# Configurar logging
logger = logging.getLogger(__name__)

# Blueprint
api_sequencial = Blueprint('api_sequencial', __name__)

class FilaAnaliseJuridica:
    """Gerenciador de fila para análises jurídicas sequenciais"""
    
    def __init__(self):
        self.fila_processamento = queue.Queue()
        self.resultados_cache = {}
        self.processando = False
        
        # Configurar clientes das APIs
        self.setup_clients()
    
    def setup_clients(self):
        """Configura clientes das APIs de IA"""
        try:
            openai_key = os.environ.get("OPENAI_API_KEY")
            if openai_key:
                self.openai_client = OpenAI(api_key=openai_key)
                logger.info("✅ Cliente OpenAI configurado")
            else:
                logger.warning("⚠️ OPENAI_API_KEY não encontrada")
                self.openai_client = None
        except Exception as e:
            logger.error(f"❌ Erro OpenAI: {e}")
            self.openai_client = None
            
        try:
            anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
            if anthropic_key:
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
                logger.info("✅ Cliente Anthropic configurado")
            else:
                logger.warning("⚠️ ANTHROPIC_API_KEY não encontrada")
                self.anthropic_client = None
        except Exception as e:
            logger.error(f"❌ Erro Anthropic: {e}")
            self.anthropic_client = None
            
        try:
            # Priorizar GOOGLE_API_KEY que já existe no sistema
            gemini_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
            if gemini_key:
                import google.generativeai as genai_config
                genai_config.configure(api_key=gemini_key)
                self.gemini_client = genai_config.GenerativeModel('gemini-pro')
                logger.info("✅ Cliente Gemini configurado com GOOGLE_API_KEY")
            else:
                logger.warning("⚠️ GOOGLE_API_KEY/GEMINI_API_KEY não encontrada")
                self.gemini_client = None
        except Exception as e:
            logger.error(f"❌ Erro Gemini: {e}")
            self.gemini_client = None
    
    def verificar_apis_funcionais(self):
        """Verifica quais APIs estão funcionais"""
        apis_ativas = []
        
        if self.openai_client:
            apis_ativas.append("OpenAI")
        if self.anthropic_client:
            apis_ativas.append("Anthropic") 
        if self.gemini_client:
            apis_ativas.append("Gemini")
            
        return apis_ativas
    
    def processar_com_openai(self, prompt, agente_info):
        """Processa análise com OpenAI GPT-4o"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Você é um especialista jurídico altamente qualificado."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,   # Ampliado para análises mais detalhadas
                temperature=0.3,   # Melhor equilíbrio
                timeout=150        # TIMEOUT ULTRA-AMPLIADO: 150 segundos
            )
            
            resultado = {
                'agente_id': agente_info['agente_id'],
                'agente_nome': agente_info['agente_nome'],
                'especialidade': agente_info['especialidade'],
                'categoria': agente_info['categoria'],
                'modelo_usado': 'OpenAI GPT-4o',
                'resultado': response.choices[0].message.content,
                'status': 'sucesso'
            }
            
            logger.info(f"✅ Análise OpenAI concluída para {agente_info['agente_nome']}")
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Erro OpenAI: {str(e)}")
            return None
    
    def processar_com_anthropic(self, prompt, agente_info):
        """Processa análise com Anthropic Claude"""
        try:
            message = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,   # Ampliado para análises mais detalhadas  
                temperature=0.3,   # Melhor equilíbrio
                messages=[{"role": "user", "content": prompt}]
            )
            
            resultado = {
                'agente_id': agente_info['agente_id'],
                'agente_nome': agente_info['agente_nome'],
                'especialidade': agente_info['especialidade'],
                'categoria': agente_info['categoria'],
                'modelo_usado': 'Anthropic Claude-4.0',
                'resultado': message.content[0].text,
                'status': 'sucesso'
            }
            
            logger.info(f"✅ Análise Anthropic concluída para {agente_info['agente_nome']}")
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Erro Anthropic: {str(e)}")
            return None
    
    def processar_com_gemini(self, prompt, agente_info):
        """Processa análise com Google Gemini"""
        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            resultado = {
                'agente_id': agente_info['agente_id'],
                'agente_nome': agente_info['agente_nome'],
                'especialidade': agente_info['especialidade'],
                'categoria': agente_info['categoria'],
                'modelo_usado': 'Google Gemini 2.5',
                'resultado': response.text if response.text else "Resposta vazia",
                'status': 'sucesso'
            }
            
            logger.info(f"✅ Análise Gemini concluída para {agente_info['agente_nome']}")
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Erro Gemini: {str(e)}")
            return None
    
    def processar_agente_sequencial(self, prompt, agente_info, api_preferida=None):
        """Processa um agente usando a API especificada ou fallback"""
        
        # Definir ordem de tentativa das APIs
        if api_preferida == "OpenAI" and self.openai_client:
            resultado = self.processar_com_openai(prompt, agente_info)
            if resultado:
                return resultado
        
        if api_preferida == "Anthropic" and self.anthropic_client:
            resultado = self.processar_com_anthropic(prompt, agente_info)
            if resultado:
                return resultado
                
        if api_preferida == "Gemini" and self.gemini_client:
            resultado = self.processar_com_gemini(prompt, agente_info)
            if resultado:
                return resultado
        
        # Fallback: tentar todas as APIs disponíveis
        if self.openai_client:
            resultado = self.processar_com_openai(prompt, agente_info)
            if resultado:
                return resultado
                
        if self.anthropic_client:
            resultado = self.processar_com_anthropic(prompt, agente_info)
            if resultado:
                return resultado
                
        if self.gemini_client:
            resultado = self.processar_com_gemini(prompt, agente_info)
            if resultado:
                return resultado
        
        # Se todas falharam, retornar erro
        return {
            'agente_id': agente_info['agente_id'],
            'agente_nome': agente_info['agente_nome'],
            'especialidade': agente_info['especialidade'],
            'categoria': agente_info['categoria'],
            'modelo_usado': 'Erro',
            'resultado': 'Erro: Todas as APIs falharam. Verifique conectividade.',
            'status': 'erro'
        }

# Instância global da fila
fila_global = FilaAnaliseJuridica()

@api_sequencial.route('/api/analise-sequencial', methods=['POST'])
def processar_analise_sequencial():
    """Endpoint para análise sequencial multi-agente"""
    
    try:
        logger.info("🚀 ANÁLISE SEQUENCIAL: Iniciando processamento")
        # Extrair dados da requisição
        texto_documento = str(request.form.get('texto_documento', '')).strip()
        agentes_selecionados = request.form.getlist('agentes_selecionados')
        
        # Fallback para string única
        if not agentes_selecionados and request.form.get('agentes_selecionados'):
            agentes_selecionados = [request.form.get('agentes_selecionados')]
        
        logger.info(f"📊 Documento: {len(texto_documento)} chars, Agentes: {len(agentes_selecionados)}")
        
        # Validações
        if len(texto_documento) < 10:
            return jsonify({
                'success': False,
                'error': 'Documento muito curto',
                'apis_funcionais': fila_global.verificar_apis_funcionais()
            }), 400
        
        if not agentes_selecionados:
            return jsonify({
                'success': False,
                'error': 'Nenhum agente selecionado',
                'apis_funcionais': fila_global.verificar_apis_funcionais()
            }), 400
        
        # Verificar APIs funcionais
        apis_ativas = fila_global.verificar_apis_funcionais()
        if not apis_ativas:
            return jsonify({
                'success': False,
                'error': 'Nenhuma API de IA disponível',
                'apis_funcionais': []
            }), 503
        
        # Processar análises sequencialmente
        resultados = processar_analises_em_fila(texto_documento, agentes_selecionados, apis_ativas)
        
        # Gerar resposta final
        resposta = {
            'success': True,
            'message': f'Análise sequencial concluída com {len(resultados)} agentes',
            'numero_registro': f"SEQ-{int(time.time() * 1000)}",
            'total_agentes': len(resultados),
            'resultados': resultados,
            'apis_funcionais': apis_ativas,
            'processamento_sequencial': True,
            'fallback_mode': False
        }
        
        logger.info(f"✅ ANÁLISE SEQUENCIAL: Concluída com sucesso - {len(resultados)} resultados")
        return jsonify(resposta), 200
        
    except Exception as e:
        logger.error(f"❌ ANÁLISE SEQUENCIAL: Erro crítico - {str(e)}")
        import traceback
        logger.error(f"❌ STACK TRACE: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}',
            'stack_trace': traceback.format_exc() if logger.level <= 10 else None,
            'apis_funcionais': []
        }), 500
    


def processar_analises_em_fila(texto_documento, agentes_ids, apis_ativas):
    """Processa análises uma por vez para evitar sobrecarga"""
    
    # Limitar texto para performance
    texto_limitado = texto_documento[:6000]
    
    # Configurações dos agentes especializados
    especialistas = [
        {
            'agente_id': '21',
            'agente_nome': 'Consultor em Propriedade Intelectual',
            'especialidade': 'Propriedade Intelectual',
            'categoria': 'Direito Empresarial',
            'api_preferida': 'OpenAI'
        },
        {
            'agente_id': '19', 
            'agente_nome': 'Especialista em Antitruste',
            'especialidade': 'Direito Concorrencial',
            'categoria': 'Direito Empresarial',
            'api_preferida': 'Anthropic'
        },
        {
            'agente_id': '38',
            'agente_nome': 'Especialista em Capital de Risco',
            'especialidade': 'Análise Financeira',
            'categoria': 'Direito Empresarial',
            'api_preferida': 'Gemini'
        },
        {
            'agente_id': '464',
            'agente_nome': 'Analista Jurídico Geral',
            'especialidade': 'Análise Geral',
            'categoria': 'Suporte Jurídico',
            'api_preferida': 'OpenAI'
        }
    ]
    
    resultados = []
    num_agentes = min(len(agentes_ids), 3)  # Limitar para performance
    
    for i in range(num_agentes):
        # Selecionar especialista
        especialista = especialistas[i % len(especialistas)]
        
        # Criar prompt específico
        prompt = f"""
Analise este documento jurídico de forma objetiva e específica:

DOCUMENTO:
{texto_limitado}

ESPECIALIDADE: {especialista['especialidade']}

Forneça análise estruturada com:
1. Principais pontos identificados
2. Riscos jurídicos específicos da sua área
3. Recomendações práticas
4. Conclusão fundamentada

Seja específico ao documento fornecido, máximo 1000 palavras.
"""
        
        logger.info(f"🔄 Processando agente {i+1}/{num_agentes}: {especialista['agente_nome']}")
        
        # Processar sequencialmente (um por vez)
        resultado = fila_global.processar_agente_sequencial(
            prompt, 
            especialista, 
            especialista['api_preferida']
        )
        
        if resultado:
            resultados.append(resultado)
            
        # Pausa entre processamentos para evitar rate limiting
        if i < num_agentes - 1:  # Não pausar depois do último
            time.sleep(2)  # 2 segundos entre análises
    
    return resultados

def registrar_api_sequencial(app):
    """Registra a API sequencial na aplicação"""
    app.register_blueprint(api_sequencial)
    logger.info("✅ API de análise sequencial registrada")
    return True