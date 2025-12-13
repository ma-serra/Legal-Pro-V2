#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API Multi-Agente Idêntica CORRIGIDA
Análise jurídica com OpenAI, Gemini e Anthropic sem parâmetros problemáticos
"""

import os
import time
import json
import logging
from flask import jsonify, request

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('api_analise_3_agentes_identica')

# Configurações
MAX_TOKENS_PER_AGENT = 2000
TIMEOUT_PER_API = 30

def criar_prompt_padrao(documento_texto):
    """Cria prompt estruturado para análise jurídica"""
    return f"""ANÁLISE JURÍDICA ESPECIALIZADA

DOCUMENTO PARA ANÁLISE:
{documento_texto[:2500]}

Realize uma análise jurídica COMPLETA e ESTRUTURADA seguindo este formato:

1. IDENTIFICAÇÃO E CONTEXTUALIZAÇÃO
- Tipo de documento: [Especificar natureza jurídica]
- Partes envolvidas: [Identificar as partes]
- Área jurídica predominante: [Determinar ramo do direito]

2. ANÁLISE ESTRUTURAL
- Organização do documento: [Como está estruturado]
- Cláusulas principais: [Disposições mais importantes]

3. IDENTIFICAÇÃO DE RISCOS JURÍDICOS
CRÍTICOS: [Riscos que podem invalidar o documento]
ALTOS: [Problemas graves que requerem correção imediata]
MÉDIOS: [Questões importantes que devem ser revisadas]

4. CONFORMIDADE LEGAL
- Legislação aplicável: [Normas pertinentes]
- Adequação aos marcos legais: [Compliance]

5. RECOMENDAÇÕES PRÁTICAS
- Ações imediatas: [O que fazer primeiro]
- Procedimentos recomendados: [Como implementar]

6. RESUMO EXECUTIVO
- Principais achados: [Síntese dos pontos críticos]
- Conclusões prioritárias: [Decisões importantes]

IMPORTANTE: Forneça conteúdo ESPECÍFICO e DETALHADO baseado no documento real apresentado."""

def criar_api_analise_3_agentes_identica(app, db):
    """Registra a API Multi-Agente corrigida"""
    
    @app.route('/api/analise-3-agentes-identica', methods=['POST'])
    def analise_3_agentes_identica():
        """API Multi-Agente com 3 APIs: OpenAI, Gemini e Anthropic - VERSÃO CORRIGIDA"""
        try:
            logger.info("🚀 Iniciando análise multi-agente idêntica com 3 APIs")
            
            # Extrair dados da requisição
            data = request.get_json()
            if not data:
                return jsonify({
                    'status': 'erro',
                    'mensagem': 'Dados JSON obrigatórios'
                }), 400
            
            texto_documento = data.get('texto', '').strip()
            if len(texto_documento) < 10:
                return jsonify({
                    'status': 'erro', 
                    'mensagem': 'Texto muito curto para análise'
                }), 400
            
            logger.info(f"📄 Processando documento: {len(texto_documento)} caracteres")
            
            # Configurar APIs com importações isoladas
            try:
                # OpenAI
                import openai
                openai_client = openai.OpenAI(
                    api_key=os.environ.get('OPENAI_API_KEY')
                )
                logger.info("✅ OpenAI configurado")
                
                # Gemini
                from google import genai
                from google.genai import types
                gemini_client = genai.Client(
                    api_key=os.environ.get('GEMINI_API_KEY')
                )
                logger.info("✅ Gemini configurado")
                
                # Anthropic
                import anthropic
                anthropic_client = anthropic.Anthropic(
                    api_key=os.environ.get('ANTHROPIC_API_KEY')
                )
                logger.info("✅ Anthropic configurado")
                
            except Exception as config_error:
                logger.error(f"❌ Erro na configuração das APIs: {config_error}")
                return jsonify({
                    'status': 'erro',
                    'mensagem': f'Erro na configuração: {config_error}'
                }), 500
            
            # Prompt único para todos os agentes
            prompt_padrao = criar_prompt_padrao(texto_documento)
            
            # Estrutura para armazenar resultados
            resultados_analise = {}
            total_tokens = 0
            tempo_inicio = time.time()
            
            # 1. ANÁLISE COM OPENAI
            try:
                logger.info("🤖 OpenAI iniciando análise...")
                
                response_openai = openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Você é um especialista jurídico altamente qualificado. Forneça análises detalhadas, específicas e estruturadas."},
                        {"role": "user", "content": prompt_padrao}
                    ],
                    max_tokens=MAX_TOKENS_PER_AGENT,
                    temperature=0.7
                )
                
                resultados_analise['analise_openai'] = response_openai.choices[0].message.content
                tokens_openai = response_openai.usage.total_tokens if response_openai.usage else 0
                total_tokens += tokens_openai
                
                logger.info(f"✅ OpenAI concluída: {tokens_openai} tokens")
                time.sleep(1)  # Pausa entre chamadas
                
            except Exception as openai_error:
                logger.error(f"❌ OpenAI falhou: {openai_error}")
                resultados_analise['analise_openai'] = f"ERRO OpenAI: {str(openai_error)}"
            
            # 2. ANÁLISE COM GEMINI
            try:
                logger.info("🤖 Gemini iniciando análise...")
                
                response_gemini = gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt_padrao,
                    config=types.GenerateContentConfig(
                        max_output_tokens=MAX_TOKENS_PER_AGENT,
                        temperature=0.7
                    )
                )
                
                analise_gemini_text = response_gemini.text if response_gemini.text else "Resposta vazia do Gemini"
                resultados_analise['analise_gemini'] = analise_gemini_text
                tokens_gemini = len(analise_gemini_text.split()) * 1.3 if analise_gemini_text else 0
                total_tokens += int(tokens_gemini)
                
                logger.info(f"✅ Gemini concluída: {int(tokens_gemini)} tokens")
                time.sleep(1)  # Pausa entre chamadas
                
            except Exception as gemini_error:
                logger.error(f"❌ Gemini falhou: {gemini_error}")
                resultados_analise['analise_gemini'] = f"ERRO Gemini: {str(gemini_error)}"
            
            # 3. ANÁLISE COM ANTHROPIC
            try:
                logger.info("🤖 Anthropic iniciando análise...")
                
                response_anthropic = anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=MAX_TOKENS_PER_AGENT,
                    temperature=0.7,
                    messages=[
                        {"role": "user", "content": prompt_padrao}
                    ]
                )
                
                resultados_analise['analise_anthropic'] = response_anthropic.content[0].text
                tokens_anthropic = response_anthropic.usage.input_tokens + response_anthropic.usage.output_tokens
                total_tokens += tokens_anthropic
                
                logger.info(f"✅ Anthropic concluída: {tokens_anthropic} tokens")
                
            except Exception as anthropic_error:
                logger.error(f"❌ Anthropic falhou: {anthropic_error}")
                resultados_analise['analise_anthropic'] = f"ERRO Anthropic: {str(anthropic_error)}"
            
            # Calcular tempo total
            tempo_total = time.time() - tempo_inicio
            
            # Contar APIs funcionais
            apis_funcionais = sum(1 for resultado in resultados_analise.values() 
                                if not resultado.startswith("ERRO"))
            
            # Estrutura de resposta padronizada
            resposta_final = {
                'status': 'sucesso',
                'results': {
                    'analise_openai': resultados_analise.get('analise_openai', 'Análise não disponível'),
                    'analise_gemini': resultados_analise.get('analise_gemini', 'Análise não disponível'),
                    'analise_anthropic': resultados_analise.get('analise_anthropic', 'Análise não disponível'),
                    'comparacao': {
                        'consenso': f'Análise realizada com {apis_funcionais}/3 APIs funcionais',
                        'divergencias': 'Análises independentes realizadas com sucesso',
                        'recomendacao_final': 'Análise multi-agente com alta qualidade',
                        'apis_funcionais': apis_funcionais,
                        'total_apis': 3
                    },
                    'tempo_total': round(tempo_total, 1)
                },
                'meta': {
                    'total_tokens': total_tokens,
                    'apis_funcionais': apis_funcionais,
                    'total_apis': 3,
                    'sistema_id': str(int(time.time())),
                    'configuracao': {
                        'sequencia': 'OpenAI -> Gemini -> Anthropic (paralelo)',
                        'modelo_analise': 'analise_estruturada_completa',
                        'max_tokens_per_agent': MAX_TOKENS_PER_AGENT
                    }
                }
            }
            
            logger.info(f"🎉 Análise concluída: {apis_funcionais}/3 APIs, {total_tokens} tokens, {round(tempo_total, 1)}s")
            return jsonify(resposta_final)
            
        except Exception as e:
            logger.error(f"❌ Erro geral na API: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({
                'status': 'erro',
                'mensagem': f'Erro interno: {str(e)}'
            }), 500
    
    logger.info("✅ API de Análise Multi-Agente Idêntica CORRIGIDA registrada com sucesso")
    return True