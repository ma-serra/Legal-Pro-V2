#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API Multi-Agente usando requests direto - SOLUÇÃO PARA PROBLEMA DE PROXY
"""

import os
import time
import json
import logging
import requests
from flask import jsonify, request

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('api_analise_manual')

def fazer_chamada_openai_manual(prompt, api_key):
    """Faz chamada OpenAI usando requests direto"""
    
    url = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "Você é um especialista jurídico altamente qualificado. Forneça análises detalhadas, específicas e estruturadas."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 2000,
        "temperature": 0.7
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    return {
        'content': data['choices'][0]['message']['content'],
        'tokens': data['usage']['total_tokens']
    }

def fazer_chamada_gemini_manual(prompt, api_key):
    """Faz chamada Gemini usando requests direto"""
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "maxOutputTokens": 2000,
            "temperature": 0.7
        }
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    content = data['candidates'][0]['content']['parts'][0]['text']
    tokens = len(content.split()) * 1.3  # Estimativa
    
    return {
        'content': content,
        'tokens': int(tokens)
    }

def fazer_chamada_anthropic_manual(prompt, api_key):
    """Faz chamada Anthropic usando requests direto"""
    
    url = "https://api.anthropic.com/v1/messages"
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 2000,
        "temperature": 0.7,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    content = data['content'][0]['text']
    tokens = data['usage']['input_tokens'] + data['usage']['output_tokens']
    
    return {
        'content': content,
        'tokens': tokens
    }

def criar_prompt_juridico(documento_texto):
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

def registrar_api_manual(app):
    """Registra a API Multi-Agente usando requests manual"""
    
    @app.route('/api/analise-3-agentes-manual', methods=['POST'])
    def analise_3_agentes_manual():
        """API Multi-Agente usando requests direto - SEM PROBLEMAS DE PROXY"""
        try:
            logger.info("🚀 Iniciando análise multi-agente MANUAL (sem SDK problemático)")
            
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
            
            # Verificar chaves de API
            openai_key = os.environ.get('OPENAI_API_KEY')
            gemini_key = os.environ.get('GOOGLE_API_KEY')
            anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
            
            if not openai_key:
                return jsonify({
                    'status': 'erro',
                    'mensagem': 'OPENAI_API_KEY não configurada'
                }), 500
            
            # Criar prompt
            prompt = criar_prompt_juridico(texto_documento)
            
            # Estrutura para resultados
            resultados = {}
            total_tokens = 0
            tempo_inicio = time.time()
            
            # 1. ANÁLISE COM OPENAI (requests direto)
            try:
                logger.info("🤖 OpenAI iniciando análise (requests direto)...")
                resultado_openai = fazer_chamada_openai_manual(prompt, openai_key)
                resultados['analise_openai'] = resultado_openai['content']
                total_tokens += resultado_openai['tokens']
                logger.info(f"✅ OpenAI concluída: {resultado_openai['tokens']} tokens")
                time.sleep(1)
            except Exception as e:
                logger.error(f"❌ OpenAI falhou: {e}")
                resultados['analise_openai'] = f"ERRO OpenAI: {str(e)}"
            
            # 2. ANÁLISE COM GEMINI (se disponível)
            if gemini_key:
                try:
                    logger.info("🤖 Gemini iniciando análise (requests direto)...")
                    resultado_gemini = fazer_chamada_gemini_manual(prompt, gemini_key)
                    resultados['analise_gemini'] = resultado_gemini['content']
                    total_tokens += resultado_gemini['tokens']
                    logger.info(f"✅ Gemini concluída: {resultado_gemini['tokens']} tokens")
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"❌ Gemini falhou: {e}")
                    resultados['analise_gemini'] = f"ERRO Gemini: {str(e)}"
            else:
                resultados['analise_gemini'] = "Gemini não configurado"
            
            # 3. ANÁLISE COM ANTHROPIC (se disponível)
            if anthropic_key:
                try:
                    logger.info("🤖 Anthropic iniciando análise (requests direto)...")
                    resultado_anthropic = fazer_chamada_anthropic_manual(prompt, anthropic_key)
                    resultados['analise_anthropic'] = resultado_anthropic['content']
                    total_tokens += resultado_anthropic['tokens']
                    logger.info(f"✅ Anthropic concluída: {resultado_anthropic['tokens']} tokens")
                except Exception as e:
                    logger.error(f"❌ Anthropic falhou: {e}")
                    resultados['analise_anthropic'] = f"ERRO Anthropic: {str(e)}"
            else:
                resultados['analise_anthropic'] = "Anthropic não configurado"
            
            # Calcular estatísticas
            tempo_total = time.time() - tempo_inicio
            apis_funcionais = sum(1 for resultado in resultados.values() 
                                if not resultado.startswith("ERRO") and not resultado.endswith("não configurado"))
            
            # Salvar resultado na base com identificador único
            try:
                from models import ResultadoAnaliseMultiAgente
                from main import db
                import uuid
                from flask import session
                
                # Obter usuário da sessão ou usar usuário padrão
                # Como esta é uma API chamada diretamente, vamos usar um ID padrão válido
                usuario_id = 1  # Usar usuário admin padrão
                logger.info(f"🔧 DEBUG: usuario_id definido como: {usuario_id} (tipo: {type(usuario_id)})")
                
                # Criar registro na base de dados
                resultado_id = str(uuid.uuid4())
                logger.info(f"🔧 DEBUG: Criando registro com usuario_id={usuario_id}")
                resultado_bd = ResultadoAnaliseMultiAgente(
                    id=resultado_id,
                    usuario_id=1,  # Forçar valor diretamente 
                    documento_original=texto_documento[:5000],  # Limite para performance
                    documento_nome="Análise via API Manual",
                    tipo_analise="multi_agente_manual",
                    resultado_principal={
                        "analise_principal": resultados.get('analise_openai') or resultados.get('analise_gemini') or resultados.get('analise_anthropic'),
                        "total_tokens": total_tokens,
                        "tempo_processamento": round(tempo_total, 1),
                        "apis_funcionais": apis_funcionais,
                        "sistema_id": str(int(time.time()))
                    },
                    resultados_agentes={
                        "openai": {"analise": resultados.get('analise_openai'), "status": "sucesso" if resultados.get('analise_openai') and not resultados.get('analise_openai').startswith("ERRO") else "falha"},
                        "gemini": {"analise": resultados.get('analise_gemini'), "status": "sucesso" if resultados.get('analise_gemini') and not resultados.get('analise_gemini').startswith("ERRO") else "falha"},
                        "anthropic": {"analise": resultados.get('analise_anthropic'), "status": "sucesso" if resultados.get('analise_anthropic') and not resultados.get('analise_anthropic').startswith("ERRO") else "falha"}
                    },
                    agentes_utilizados=["OpenAI GPT-4o", "Google Gemini", "Anthropic Claude"],
                    tempo_processamento=int(tempo_total),
                    status="concluida",
                    provider_principal="openai" if resultados.get('analise_openai') and not resultados.get('analise_openai').startswith("ERRO") else "gemini" if resultados.get('analise_gemini') and not resultados.get('analise_gemini').startswith("ERRO") else "anthropic"
                )
                
                db.session.add(resultado_bd)
                db.session.commit()
                
                logger.info(f"✅ Resultado salvo na base com ID: {resultado_id}")
                
            except Exception as e:
                logger.error(f"❌ Erro ao salvar na base: {e}")
                db.session.rollback()
                resultado_id = None

            # Resposta final
            resposta = {
                'status': 'sucesso',
                'results': {
                    'analise_openai': resultados.get('analise_openai', 'Não disponível'),
                    'analise_gemini': resultados.get('analise_gemini', 'Não disponível'),
                    'analise_anthropic': resultados.get('analise_anthropic', 'Não disponível'),
                    'comparacao': {
                        'consenso': f'Análise realizada com {apis_funcionais}/3 APIs funcionais',
                        'divergencias': 'Análises independentes usando requests direto',
                        'recomendacao_final': 'Análise multi-agente sem problemas de proxy',
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
                    'resultado_id': resultado_id,
                    'configuracao': {
                        'sequencia': 'OpenAI -> Gemini -> Anthropic (requests direto)',
                        'modelo_analise': 'analise_estruturada_manual',
                        'metodo': 'requests_direto_sem_proxy'
                    }
                }
            }
            
            logger.info(f"🎉 Análise concluída: {apis_funcionais}/3 APIs, {total_tokens} tokens, {round(tempo_total, 1)}s")
            return jsonify(resposta)
            
        except Exception as e:
            logger.error(f"❌ Erro geral na API manual: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({
                'status': 'erro',
                'mensagem': f'Erro interno: {str(e)}'
            }), 500
    
    logger.info("✅ API de Análise Multi-Agente MANUAL registrada com sucesso")
    return True